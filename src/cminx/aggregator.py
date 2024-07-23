# Copyright 2022 CMakePP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module interfaces with the generated CMake parser.
The primary entrypoint is :class:`~DocumentationAggregator`,
which subclasses :class:`cminx.parser.CMakeListener`. This
class listens to all relevent parser rules, generates
:class:`cminx.documentation_types.DocumentationType`
objects that represent the parsed CMake, and
aggregates them in a single list.

:Author: Branden Butler
:License: Apache 2.0
"""

import logging
import re
from dataclasses import dataclass
from typing import List, Union

from antlr4 import ParserRuleContext

from .documentation_types import AttributeDocumentation, FunctionDocumentation, MacroDocumentation, \
    VariableDocumentation, GenericCommandDocumentation, ClassDocumentation, TestDocumentation, SectionDocumentation, \
    MethodDocumentation, VarType, CTestDocumentation, AbstractCommandDefinitionDocumentation, OptionDocumentation, \
    DocumentationType, DanglingDoccomment

from .documentation_command_types import AbstractDocumentationCommand, ModuleDocumentationCommand, \
    NoDocDocumentationCommand, DocumentationHelpers

from .exceptions import CMakeSyntaxException, DocumentationCommandSyntaxException
from .parser.CMakeListener import CMakeListener
# Annoyingly, the Antl4 Python libraries use camelcase since it was originally Java, so we have convention
# inconsistencies here
from .parser.CMakeParser import CMakeParser
from cminx import Settings


def get_cmake_command_name(ctx: CMakeParser.Command_invocationContext) -> str:
    return ctx.Identifier().getText().lower()


def clean_comment_lines(comment_ctx: CMakeParser.Bracket_doccommentContext | CMakeParser.Command_doccommentContext
                        ) -> List[str]:
    """
    Prepares comment for placement into generated RST.
    Strips start and end identifiers along with leading whitespace (before #), first
    # character (with following whitespace if found) from each line.

    A fast path is used to determine a 'global' whitespace offset for indented comments.
    Determines leading whitespace by counting the number of whitespace characters before
    a # (beginning of comment lines) character is found. If the number of whitespace
    characters is equal for the first and last lines, then the offset is used for every line.
    Otherwise, each lines characters are iterated over until the first non-whitespace
    character is found.

    :param comment_ctx: Raw comment string as found in CMake source files.
    """
    raw_lines = comment_ctx.getText().split("\n")

    global_whitespace_offset = 0  # number of chars before '#' in last line
    for char in raw_lines[-1]:
        if char == "#":
            break
        global_whitespace_offset += 1

    if len(raw_lines) > 1:
        last_line_whitespace_offset = 0  # number of chars before '#' in first line
        for char in raw_lines[0]:
            if char == "#":
                break
            last_line_whitespace_offset += 1
        if last_line_whitespace_offset == global_whitespace_offset:
            global_whitespace_offset = global_whitespace_offset
        else:
            global_whitespace_offset = 0  # beginning and end lines have different indentation

    cleaned_lines: List[str] = []
    for raw_line in raw_lines:
        start_offset = global_whitespace_offset  # number of chars to strip from start of raw line
        end_offset = 0  # number of chars to strip from end of raw line
        end_index = len(raw_line)
        for char_index in range(global_whitespace_offset,
                                end_index):  # start searching for '#' from the global offset
            first_char = raw_line[char_index]
            if first_char != "#":
                if first_char == " " or first_char == "\t":
                    start_offset += 1  # strip leading whitespace char
                    continue  # skip to next char
                break  # inside comment
            start_offset += 1  # strip '#' char
            if start_offset >= end_index:
                break  # blank line
            second_char = raw_line[start_offset]
            if second_char == " " or second_char == "\t":
                start_offset += 1  # strip whitespace char following '#'
            elif end_index >= (start_offset + 1) and (second_char == "]" and raw_line[start_offset + 1] == "]"):
                start_offset += 2  # strip end identifier char sequence
            elif end_index >= (start_offset + 2) and (second_char == "[" and raw_line[start_offset + 1] == "[" and
                                                      raw_line[start_offset + 2] == "["):
                start_offset += 3  # strip start identifier char sequence
                if end_index >= (start_offset + 1) and raw_line[start_offset + 1] == " ":
                    start_offset += 1  # strip whitespace char following start identifier
                if end_index >= (start_offset + 2) and (raw_line[end_index - 2] == "#" and
                                                        raw_line[end_index - 1] == "]" and raw_line[
                                                            end_index] == "]"):
                    end_offset -= 3  # strip single line closing identifier
                    if raw_line[-4] == " ":
                        end_offset -= 1  # strip single line closing identifier leading space
            break  # found start of line contents
        if start_offset >= end_index:
            cleaned_lines.append("")  # line processed
        else:
            new_start_index = max(start_offset, 0)
            new_end_index = max(end_index - end_offset, new_start_index)
            cleaned_lines.append(raw_line[new_start_index:new_end_index])  # line processed

    # Pop empty lines from beginning of list. Most comments will always have an
    # empty first line due to the opening identifier being stripped.
    while len(cleaned_lines) > 0:
        if len(cleaned_lines[0].strip(" \t\n")) != 0:
            break
        cleaned_lines.pop(0)

    return cleaned_lines


def clean_escaped_command_lines(lines: List[str]):
    for line_index in range(0, max(len(lines), 1)):
        line_end_index = max(len(lines[line_index]), 1)
        if line_end_index < 2:
            continue  # ignore lines with less than 2 chars
        for char_index in range(0, line_end_index):
            if lines[line_index][char_index] == " " or lines[line_index][char_index] == "\t":
                continue
            elif lines[line_index][char_index] == "\\" and line_index >= char_index + 1:
                if lines[line_index][char_index + 1] == "@":
                    if char_index == 0:
                        lines[line_index] = lines[line_index][1:]
                    else:
                        lines[line_index] = lines[line_index][0:char_index - 1] + lines[line_index][char_index + 1:]
            break  # fall through means line cannot match escape sequence

@dataclass
class DefinitionCommand:
    """
    A container for documentation of definition commands, used to update
    the parameter list when a :code:`cmake_parse_arguments()` command
    is encountered.

    A definition command is a command that defines another command,
    so the function() and macro() commands are definition commands.
    Instances of this dataclass are placed on the top of a stack
    when definition commands are encountered.
    """
    documentation: Union[AbstractCommandDefinitionDocumentation, None]
    """
    The documentation for the definition command. If None,
    this DefinitionCommand will be ignored when popped.
    """

    should_document: bool = True
    """
    Whether the contained documentation object should be updated
    if a :code:`cmake_parse_arguments()` command is found.
    When false, this object is ignored.
    """


class DocumentationAggregator(CMakeListener):
    """
    Processes all docstrings and their associated commands, aggregating
    them in a list. Uses the given :class:`~cminx.config.Settings` object
    to determine aggregation settings, and will document commands without
    doccomments if the associated settings are set.

    The method used to generate the documentation object for
    a given command is chosen by searching for a method with the name
    :code:`"process_<command name>"` with two arguments: :code:`ctx` that is
    of type :class:`cminx.parser.CMakeParser.Command_invocationContext`,
    and :code:`docstring` that is of type string.
    """

    def __init__(self, settings: Settings = Settings()) -> None:
        self.settings: Settings = settings
        """Application settings used to determine what commands to document"""

        self.documented: List[DocumentationType] = []
        """All current documented commands"""

        self.documented_classes_stack: List[Union[ClassDocumentation, None]] = []
        """A stack containing the documented classes and inner classes as they are processed"""

        self.documented_awaiting_function_def: Union[DocumentationType, None] = None
        """
        A variable containing a documented command such as cpp_member() that is awaiting its function/macro
        definition
        """

        self.documentation_command_stack: List[AbstractDocumentationCommand] = []
        """
        A stack containing the currently active documentation commands. A documentation
        command may affect multiple CMake command invocations or require follow lines
        providing more context, in these cases the dataclass will be appended to the stack.
        """

        self.definition_command_stack: List[DefinitionCommand] = []
        """
        A stack containing the current definition command that we are inside.
        A definition command is any command that defines a construct with both a
        beginning command and an ending command, with all commands within being considered
        part of the definition. Examples of definition commands include
        function(), macro(), and cpp_class().
        """

        self.consumed: List[ParserRuleContext] = []
        """
        A list containing all of the contexts that have already been processed
        """

        self.logger: logging.Logger = logging.getLogger(__name__)

    def process_function(self, ctx: CMakeParser.Command_invocationContext, doc_lines: List[str]) -> None:
        """
        Extracts function name and declared parameters.

        :param ctx: Documented command context. Constructed by the Antlr4 parser.

        :param doc_lines: Cleaned doc-comment lines.
        """

        def_params = [param for param in ctx.single_argument()]  # Extract declared function parameters

        if len(def_params) < 1:
            pretty_text = "\n".join(doc_lines) + f"\n{ctx.getText()}"
            raise CMakeSyntaxException(
                f"function() called with incorrect parameters: {ctx.single_argument()}\n\n{pretty_text}",
                ctx.start.line
            )

        params = [
            re.sub(self.settings.input.function_parameter_name_strip_regex, "", p.getText()) for p in def_params[1:]
        ]
        function_name = def_params[0].getText()

        has_kwargs = False
        for line in doc_lines:
            if self.settings.input.kwargs_doc_trigger_string in line:
                has_kwargs = True
                break

        # Extracts function name and adds the completed function documentation to the 'documented' list
        doc = FunctionDocumentation(function_name, doc_lines, params, has_kwargs)
        self.documented.append(doc)
        self.definition_command_stack.append(DefinitionCommand(doc))

    def process_macro(self, ctx: CMakeParser.Command_invocationContext, doc_lines: List[str]) -> None:
        """
        Extracts macro name and declared parameters.

        :param ctx: Documented command context. Constructed by the Antlr4 parser.

        :param doc_lines: Cleaned doc-comment lines.
        """

        def_params = [param for param in ctx.single_argument()]  # Extract declared macro parameters

        if len(def_params) < 1:
            pretty_text = "\n".join(doc_lines) + f"\n{ctx.getText()}"
            raise CMakeSyntaxException(
                f"macro() called with incorrect parameters: {ctx.single_argument()}\n\n{pretty_text}",
                ctx.start.line
            )

        params = [
            re.sub(self.settings.input.macro_parameter_name_strip_regex, "", p.getText()) for p in def_params[1:]
        ]
        macro_name = def_params[0].getText()

        has_kwargs = False
        for line in doc_lines:
            if self.settings.input.kwargs_doc_trigger_string in line:
                has_kwargs = True
                break

        # Extracts macro name and adds the completed macro documentation to the 'documented' list
        doc = MacroDocumentation(macro_name, doc_lines, params, has_kwargs)
        self.documented.append(doc)
        self.definition_command_stack.append(DefinitionCommand(doc))

    def process_cmake_parse_arguments(self, ctx: CMakeParser.Command_invocationContext, doc_lines: List[str]) -> None:
        """
        Determines whether a documented function or macro uses *args or *kwargs.
        Accesses the last element in the :code:`definition_command_stack` to
        update the documentation's :code:`has_kwargs` field.

        :param ctx: Documented command context. Constructed by the Antlr4 parser.

        :param doc_lines: Cleaned doc-comment lines.
        """
        if len(self.definition_command_stack) > 0:
            last_element = self.definition_command_stack[-1]
            if last_element.should_document and isinstance(last_element.documentation,
                                                           AbstractCommandDefinitionDocumentation):
                last_element.documentation.has_kwargs = True

    def process_ct_add_test(self, ctx: CMakeParser.Command_invocationContext, doc_lines: List[str]) -> None:
        """
        Extracts test name and declared parameters.

        :param ctx: Documented command context. Constructed by the Antlr4 parser.

        :param doc_lines: Cleaned doc-comment lines.
        """
        params = [param.getText() for param in ctx.single_argument()]  # Extract parameters

        if len(params) < 2:
            pretty_text = "\n".join(doc_lines) + f"\n{ctx.getText()}"
            self.logger.error(
                f"ct_add_test() called with incorrect parameters: {params}\n\n{pretty_text}")
            return

        name = ""
        expect_fail = False
        for i in range(0, len(params)):
            param = params[i]
            if param.upper() == "NAME":
                try:
                    name = params[i + 1]
                except IndexError:
                    pretty_text = "\n".join(doc_lines) + f"\n{ctx.getText()}"
                    self.logger.error(
                        f"ct_add_test() called with incorrect parameters: {params}\n\n{pretty_text}")
                    return

            if param.upper() == "EXPECTFAIL":
                expect_fail = True

        test_doc = TestDocumentation(name, doc_lines, expect_fail)
        self.documented.append(test_doc)
        self.documented_awaiting_function_def = test_doc

    def process_ct_add_section(self, ctx: CMakeParser.Command_invocationContext, doc_lines: List[str]) -> None:
        """
        Extracts section name and declared parameters.

        :param ctx: Documented command context. Constructed by the Antlr4 parser.

        :param doc_lines: Cleaned doc-comment lines.
        """
        params = [param.getText() for param in ctx.single_argument()]  # Extract parameters

        if len(params) < 2:
            pretty_text = "\n".join(doc_lines) + f"\n{ctx.getText()}"
            self.logger.error(
                f"ct_add_section() called with incorrect parameters: {params}\n\n{pretty_text}")
            return

        name = ""
        expect_fail = False
        for i in range(0, len(params)):
            param = params[i]
            if param.upper() == "NAME":
                try:
                    name = params[i + 1]
                except IndexError:
                    pretty_text = "\n".join(doc_lines) + f"\n{ctx.getText()}"
                    self.logger.error(f"ct_add_section() called with incorrect parameters: {params}\n\n{pretty_text}")
                    return

            if param.upper() == "EXPECTFAIL":
                expect_fail = True

        section_doc = SectionDocumentation(name, doc_lines, expect_fail)
        self.documented.append(section_doc)
        self.documented_awaiting_function_def = section_doc

    def process_set(self, ctx: CMakeParser.Command_invocationContext, doc_lines: List[str]) -> None:
        """
        Extracts variable name and values from the documented set command.
        Also determines the type of set command/variable: String, List, or Unset.

        :param ctx: Documented command context. Constructed by the Antlr4 parser.

        :param doc_lines: Cleaned doc-comment lines.
        """

        if len(ctx.single_argument()) < 1:
            pretty_text = "\n".join(doc_lines) + f"\n{ctx.getText()}"
            self.logger.error(
                f"set() called with incorrect parameters: {ctx.single_argument()}\n\n{pretty_text}")
            return

        varname = ctx.single_argument()[
            0].getText()
        # First argument is name of variable so ignore that
        arg_len = len(ctx.single_argument()) - 1

        if arg_len > 1:  # List
            values = [val.getText()
                      for val in ctx.single_argument()[1:]]
            self.documented.append(VariableDocumentation(
                varname, doc_lines, VarType.LIST, " ".join(values)))
        elif arg_len == 1:  # String
            value = ctx.single_argument()[1].getText()

            # If the value includes the quote marks,
            # need to remove them to get just the raw string
            if value[0] == '"':
                value = value[1:]
            if value[-1] == '"':
                value = value[:-1]
            self.documented.append(VariableDocumentation(
                varname, doc_lines, VarType.STRING, value))
        else:  # Unset
            self.documented.append(VariableDocumentation(
                varname, doc_lines, VarType.UNSET, None))

    def process_cpp_class(self, ctx: CMakeParser.Command_invocationContext, doc_lines: List[str]) -> None:
        """
        Extracts the name and the declared superclasses from the documented
        cpp_class command.

        :param ctx: Documented command context. Constructed by the Antlr4 parser.

        :param doc_lines: Cleaned doc-comment lines.
        """

        if len(ctx.single_argument()) < 1:
            pretty_text = "\n".join(doc_lines) + f"\n{ctx.getText()}"
            self.logger.error(f"cpp_class() called with incorrect parameters: {ctx.single_argument()}\n\n{pretty_text}")
            return

        params = [param.getText()
                  for param in ctx.single_argument()]

        name = params[0]
        superclasses = params[1:]
        clazz = ClassDocumentation(name, doc_lines, superclasses, [], [], [], [])
        self.documented.append(clazz)

        # If we are currently processing another class, then this one
        # is an inner class and we need to add it
        if len(self.documented_classes_stack) > 0 and self.documented_classes_stack[-1] is not None:
            self.documented_classes_stack[-1].inner_classes.append(clazz)

        # Continue processing within the class's context
        # until we reach cpp_end_class()
        self.documented_classes_stack.append(clazz)

    def process_cpp_member(self, ctx: CMakeParser.Command_invocationContext, doc_lines: List[str],
                           is_constructor: bool = False) -> None:
        """
        Extracts the method name and declared parameter types from the documented cpp_member
        command.

        :param ctx: Documented command context. Constructed by the Antlr4 parser.

        :param doc_lines: Cleaned doc-comment lines.

        :param is_constructor: Whether the member is a constructor, this parameter is reflected in the generated
        MethodDocumentation.
        """
        if len(ctx.single_argument()) < 2:
            pretty_text = "\n".join(doc_lines) + f"\n{ctx.getText()}"
            self.logger.error(
                f"cpp_class() called with incorrect parameters: {ctx.single_argument()}\n\n{pretty_text}")
            return

        params = [param.getText()
                  for param in ctx.single_argument()]
        if len(self.documented_classes_stack) <= 0:
            pretty_text = "\n".join(doc_lines) + f"\n{ctx.getText()}"
            called_type = "cpp_constructor()" if is_constructor else "cpp_member()"

            self.logger.error(
                f"{called_type} called outside of cpp_class() definition: {params}\n\n{pretty_text}")
            return

        clazz = self.documented_classes_stack[-1]
        # Shouldn't document because class isn't supposed to be documented
        if clazz is None:
            return

        parent_class = params[1]
        name = params[0]
        param_types = params[2:] if len(params) > 2 else []
        method_doc = MethodDocumentation(
            name, doc_lines, parent_class, param_types, [], is_constructor)
        if is_constructor:
            clazz.constructors.append(method_doc)
        else:
            clazz.members.append(method_doc)
        self.documented_awaiting_function_def = method_doc

    def process_cpp_constructor(self, ctx: CMakeParser.Command_invocationContext, doc_lines: List[str]) -> None:
        """
        Alias for calling process_cpp_member() with is_constructor=True.
        """
        self.process_cpp_member(ctx, doc_lines, is_constructor=True)

    def process_cpp_attr(self, ctx: CMakeParser.Command_invocationContext, doc_lines: List[str]) -> None:
        """
        Extracts the name and any default values from the documented cpp_attr
        command.

        :param ctx: Documented command context. Constructed by the Antlr4 parser.

        :param doc_lines: Cleaned doc-comment lines.
        """
        if len(ctx.single_argument()) < 2:
            pretty_text = "\n".join(doc_lines) + f"\n{ctx.getText()}"
            self.logger.error(
                f"cpp_attr() called with incorrect parameters: {ctx.single_argument()}\n\n{pretty_text}")
            return

        params = [param.getText()
                  for param in ctx.single_argument()]
        if len(self.documented_classes_stack) <= 0:
            pretty_text = "\n".join(doc_lines) + f"\n{ctx.getText()}"
            self.logger.error(
                f"cpp_attr() called outside of cpp_class() definition: {params}\n\n{pretty_text}")
            return

        clazz = self.documented_classes_stack[-1]
        # Shouldn't document because class isn't supposed to be documented
        if clazz is None:
            return
        parent_class = params[0]
        name = params[1]
        default_values = params[2] if len(params) > 2 else None
        clazz.attributes.append(AttributeDocumentation(
            name, doc_lines, parent_class, default_values))

    def process_add_test(self, ctx: CMakeParser.Command_invocationContext, doc_lines: List[str]) -> None:
        """
        Extracts information from a CTest add_test() command.
        Note: this is not the processor for the CMakeTest ct_add_test() command,
        but the processor for the vanilla CMake add_test() command.

        :param ctx: Documented command context. Constructed by the Antlr4 parser.

        :param doc_lines: Cleaned doc-comment lines.
        """
        params = [param.getText() for param in ctx.single_argument()]  # Extract parameters

        if len(params) < 2:
            pretty_text = "\n".join(doc_lines) + f"\n{ctx.getText()}"
            self.logger.error(
                f"ct_add_section() called with incorrect parameters: {params}\n\n{pretty_text}")
            return

        name = ""
        for i in range(0, len(params)):
            param = params[i]
            if param.upper() == "NAME":
                try:
                    name = params[i + 1]
                except IndexError:
                    pretty_text = "\n".join(doc_lines) + f"\n{ctx.getText()}"
                    self.logger.error(f"add_test() called with incorrect parameters: {params}\n\n{pretty_text}")
                    return

        test_doc = CTestDocumentation(name, doc_lines, [p for p in params if p != name and p != "NAME"])
        self.documented.append(test_doc)

    def process_option(self, ctx: CMakeParser.Command_invocationContext, doc_lines: List[str]) -> None:
        """
        Extracts information from an :code:`option()` command and creates
        an OptionDocumentation from it. It extracts the option name,
        the help text, and the default value if any.

        :param ctx: Documented command context. Constructed by the Antlr4 parser.
        :param doc_lines: Cleaned doc-comment lines.
        """
        params = [param.getText() for param in ctx.single_argument()]  # Extract parameters
        if len(params) < 2 or len(params) > 3:
            pretty_text = "\n".join(doc_lines) + f"\n{ctx.getText()}"
            self.logger.error(
                f"ct_add_section() called with incorrect parameters: {params}\n\n{pretty_text}")
            return
        option_doc = OptionDocumentation(
            params[0],
            doc_lines,
            "bool",
            params[2] if len(params) == 3 else None,
            params[1]
        )
        self.documented.append(option_doc)

    def process_generic_command(self, command_name: str, ctx: CMakeParser.Command_invocationContext,
                                doc_lines: List[str]) -> None:
        """
        Extracts command invocation and arguments for a documented command that does not
        have a dedicated processor function.

        :param command_name: The documented command's name, such as add_library.

        :param ctx: Documented command context. Constructed by the Antlr4 parser.

        :param doc_lines: Cleaned docstring.
        """

        args = ctx.single_argument() + ctx.compound_argument()
        args = [val.getText() for val in args]
        self.documented.append(GenericCommandDocumentation(
            command_name, doc_lines, args))

    def process_command_doccomment(self, ctx: CMakeParser.Command_doccommentContext,
                                   cleaned_lines: List[str],
                                   invocation_ctx: CMakeParser.Command_invocationContext | None = None) -> bool:
        """
        TODO: Documentation description
        :param ctx: Documented command context. Constructed by the Antlr4 parser.
        :param invocation_ctx: CMake command invocation context. Constructed by the Antlr4 parser.
                               If value is `None` the comment is considered dangling/free.
        :param cleaned_lines: Cleaned doc-comment lines. Will be extracted from the comment context if value is `None`.

        :return: Returns `True` if the commands were processed without consuming the invocation context.
                 Returns `False` if the commands consumed the invocation context while being processed.
        """
        cleaned_lines = cleaned_lines if cleaned_lines is not None else clean_comment_lines(ctx)
        found_commands = DocumentationHelpers.extract_documentation_commands(
            cleaned_lines,
            get_cmake_command_name(invocation_ctx) if not (invocation_ctx is None) else ""
        )
        num_commands_processed = 0
        num_command_types: dict[str, int] = {}  # tracks the number of commands from each type
        unrelated_to_invocation = invocation_ctx is None
        for command in found_commands:
            abs_line_num = ctx.start.line + command.start_line_offset
            if command.must_be_only_command() and num_commands_processed > 0:
                self.logger.error(f"Found `@{command.name}` command in doc-comment with other commands on line "
                                  f"#{abs_line_num}. `@{command.name}` commands must be the only command found in "
                                  "a doc-comment for processing to work as expected. Therefore, this command will "
                                  "not be processed.")
                continue

            if command.name not in num_command_types.keys():
                num_command_types[command.name] = 0
            if command.must_be_unique_per_comment() and num_command_types[command.name] > 0:
                self.logger.error(f"Found multiple `@{command.name}` commands in doc-comment on line "
                                  f"#{abs_line_num}. `@{command.name}` commands must appear at most once per "
                                  "doc-comment for processing to work as expected. Therefore, this command will "
                                  "not be processed.")
                continue
            if command.preprocess(ctx, self.documentation_command_stack, self.documented, self.consumed,
                                  invocation_ctx):
                unrelated_to_invocation = True
            num_commands_processed += 1
            num_command_types[command.name] += 1

        return unrelated_to_invocation

    def process_bracket_doccomment(self, ctx: CMakeParser.Bracket_doccommentContext,
                                   invocation_ctx: CMakeParser.Command_invocationContext | None = None,
                                   cleaned_lines: List[str] | None = None) -> bool:
        """
        :param ctx: Bracket doc-comment context. Constructed by the Antlr4 parser.
        :param invocation_ctx: Command invocation context. Constructed by the Antlr4 parser.
        :param cleaned_lines: List of commands found in the doc-comment.

        :return: Returns `True` if the comment was processed without consuming the invocation context.
                 Returns `False` if the comment consumed the invocation context while being processed.
        """
        if invocation_ctx is None:
            self.consumed.append(ctx)
            self.logger.warning(
                "Ignoring dangling doc-comment (no CMake command invocation to document.) "
                "Generated RST may change depending on CMinx version."
            )
            return True
        return False

    def process_cmake_invocation(self, ctx: CMakeParser.Command_invocationContext,
                                 cleaned_lines: List[str] | None = None) -> bool:
        """
        :param ctx: Command invocation context. Constructed by the Antlr4 parser.
        :param cleaned_lines: Optional parameter used to forward the cleaned lines when invoked by a documented command.
        """
        if ctx in self.consumed:
            return False  # was already handled

        self.consumed.append(ctx)  # consume CMake command invocation node
        cmake_command = get_cmake_command_name(ctx)

        if len(self.documentation_command_stack) > 0:
            no_doc_stack = DocumentationHelpers.commands_of_type(NoDocDocumentationCommand,
                                                                 self.documentation_command_stack)
            if len(no_doc_stack) > 0:
                # if DocumentationHelpers.starts_invocation_block(cmake_command):
                #     # append a new no-doc command to the stack when the previous has child invocation blocks
                #     new_no_doc = copy(no_doc_stack[-1])
                #     new_no_doc.cmake_command = cmake_command
                #     self.documentation_command_stack.append(new_no_doc)
                return True  # handled by no-doc command

        cleaned_lines = [] if cleaned_lines is None else cleaned_lines

        try:
            if f"process_{cmake_command}" in dir(self):
                getattr(self, f"process_{cmake_command}")(ctx, cleaned_lines)
            else:
                self.process_generic_command(cmake_command, ctx, cleaned_lines)
        except Exception as e:
            line_num = ctx.start.line
            self.logger.error(f"Caught exception while processing command beginning at line number {line_num}")
            raise e

        return True  # notify caller the

    def enterDocumented_command(self, ctx: CMakeParser.Documented_commandContext) -> None:
        """
        Main entrypoint into the documentation processor and aggregator. Called by ParseTreeWalker whenever
        encountering a documented command. Cleans the docstring and dispatches ctx to other functions for additional
        processing (process_{command}(), i.e. process_function())

        :param ctx: Documented command context, constructed by the Antlr4 parser.

        :raise NotImplementedError: If no processor can be found for the command that was documented.
        """
        self.consumed.append(ctx)  # consume parent node of doc-comment + command invocation

        is_command: bool = (
            ctx.command_doccomment() is not None and
            not ctx.command_doccomment().isEmpty()
        )  # check is needed due to grammar ambiguity
        comment_ctx: CMakeParser.Command_doccommentContext | CMakeParser.Bracket_doccommentContext = (
            ctx.command_doccomment() if is_command else ctx.bracket_doccomment()
        )
        self.consumed.append(comment_ctx)  # consume doc-comment/bracket-comment node
        cleaned_lines = clean_comment_lines(comment_ctx)

        invocation_ctx: CMakeParser.Command_invocationContext = ctx.command_invocation()
        try:
            if is_command:
                documented_size_before = len(self.documented)
                if self.process_command_doccomment(comment_ctx, cleaned_lines, invocation_ctx):
                    return  # the command processing handles the invocation node processing
                if len(self.documented) > documented_size_before:
                    last_documented = self.documented[-1]
                    if isinstance(last_documented, AbstractDocumentationCommand):
                        # use the modified comment from the doc-comment command for generated output
                        cleaned_lines = self.documented[-1].doc
                        # and remove the temporary command object from the documented stack
                        self.documented.pop()

            clean_escaped_command_lines(cleaned_lines)
            if not self.process_cmake_invocation(invocation_ctx, cleaned_lines) and ctx not in self.consumed:
                self.consumed.append(invocation_ctx)
        except Exception as e:
            line_num = ctx.command_invocation().start.line
            type_name: str = " command " if is_command else " "
            self.logger.error(
                f"Caught exception while processing{type_name}doc-comment beginning at line number {line_num}"
            )
            raise e

    def enterCommand_doccomment(self, ctx: CMakeParser.Command_doccommentContext) -> None:
        """
        Handles doc-comment commands without a CMake command invocation. This path is expected
        for top-level `@module` and `@no-doc` commands. Any other command is ignored, this may
        change in future CMinx versions.

        :param ctx: Documentation command comment context. Constructed by the Antlr4 parser.
        """
        if ctx in self.consumed:
            return  # doc-comment is attached to a CMake command invocation

        self.consumed.append(ctx)
        cleaned_lines = clean_comment_lines(ctx)
        clean_escaped_command_lines(cleaned_lines)

        # process the doc-comment command as free/dangling
        documented_size_before = len(self.documented)
        try:
            self.process_command_doccomment(ctx, cleaned_lines, None)
        except Exception as e:
            self.logger.error(f"Caught exception while processing command doc-comment beginning on line {ctx.start.line}.")
            raise e

        if len(self.documented) == documented_size_before:
            # the doc-comment command should not appear here
            self.logger.warning(f"Detected dangling command doc-comment beginning on line {ctx.start.line}, ignoring. "
                                "RST may change depending on CMinx version.")
            # self.documented.append(DanglingDoccomment("", cleaned_lines))

    def enterBracket_doccomment(self, ctx: CMakeParser.Bracket_doccommentContext):
        """
        Handles doc-comments with no CMake command invocation (dangling.)
        Current behaviour ignores comment contents, this may change in future CMinx versions.

        :param ctx: Documentation command comment context. Constructed by the Antlr4 parser.
        """
        if ctx in self.consumed:
            return  # doc-comment is attached to a CMake command invocation

        self.consumed.append(ctx)
        self.logger.warning(f"Detected dangling doc-comment on line {ctx.start.line}, ignoring. "
                            "RST may change depending on CMinx version.")
        # self.documented.append(DanglingDoccomment("", clean_comment_lines(ctx)))

    def enterCommand_invocation(self, ctx: CMakeParser.Command_invocationContext) -> None:
        """
        Visitor for all other commands, used for locating position-dependent elements
        of documented commands.

        * `endfunction()`/`endmacro()` that pops the stack element created by
          the matching `function()`/`macro()` to 'attach' preceding invocations.

        * `cpp_end_class()` that pops the stack element created by `cpp_class()` which
          is used to 'attach' preceding invocations to the class definition.

        :param ctx: Command invocation context. Constructed by the Antlr4 parser.
        """
        cmake_command = get_cmake_command_name(ctx)
        try:
            # This switch/match is a hot path so check most common cases first
            if ((cmake_command == "endfunction" or cmake_command == "endmacro") and
                    len(self.definition_command_stack) > 0):
                self.definition_command_stack.pop()
            elif ((cmake_command == "function" or cmake_command == "macro") and
                    self.documented_awaiting_function_def is not None):
                # We've found the function/macro def that the previous documented cmake_command needed
                params = [param.getText()
                          for param in ctx.single_argument()]
                if isinstance(self.documented_awaiting_function_def, MethodDocumentation):
                    params = [
                        re.sub(self.settings.input.member_parameter_name_strip_regex, "", p.getText()) for p in
                        ctx.single_argument()
                    ]

                self.documented_awaiting_function_def.is_macro = cmake_command == "macro"

                # Ignore function name and self param
                if len(params) > 2:
                    param_names = params[2:]
                    self.documented_awaiting_function_def.params.extend(param_names)

                # Clear the var since we've processed the function/macro def we need
                self.documented_awaiting_function_def = None

                # Allows scanning for cmake_parse_arguments() inside other types of definitions
                self.definition_command_stack.append(DefinitionCommand(None, False))
            elif cmake_command == "cmake_parse_arguments":
                self.process_cmake_parse_arguments(ctx, [])
            elif cmake_command == "cpp_end_class":
                # Stop associating invocations with the class
                self.documented_classes_stack.pop()
            elif cmake_command == "cpp_class" and not self.settings.input.include_undocumented_cpp_class:
                # Class definitions rarely lack documentation so this check last. Ensures the stack
                # doesn't fall into an inconsistent state when no doc-comment is found.
                self.documented_classes_stack.append(None)
            elif cmake_command != "set" and f"process_{cmake_command}" in dir(self):
                # Fall-through case: handles any invocation without a doc-comment.
                # Any cases handled before this will never be included in generated
                # documentation, regardless of `include_undocumented` configuration.
                if ctx not in self.consumed:
                    if self.settings.input.__dict__[f"include_undocumented_{cmake_command}"]:
                        if not self.process_cmake_invocation(ctx) and ctx not in self.consumed:
                            self.consumed.append(ctx)  # consume command invocation node
                    elif cmake_command == "function" or cmake_command == "macro":
                        self.definition_command_stack.append(DefinitionCommand(None, False))
                        self.consumed.append(ctx)  # consume command invocation node
        except Exception as e:
            self.logger.error(f"Caught exception while processing command beginning at line number {ctx.start.line}")
            raise e

    def exitCommand_invocation(self, ctx: CMakeParser.Command_invocationContext):
        if len(self.documentation_command_stack) <= 0:
            return
        no_doc_stack = DocumentationHelpers.commands_of_type(NoDocDocumentationCommand,
                                                             self.documentation_command_stack)
        if len(no_doc_stack) > 0:
            active_command = no_doc_stack[-1]
            if (active_command.cmake_command == get_cmake_command_name(ctx) or active_command.cmake_command ==
                    DocumentationHelpers.start_invocation_block_command_for(get_cmake_command_name(ctx))):
                self.documentation_command_stack.pop()
