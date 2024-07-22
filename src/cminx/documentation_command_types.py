# Copyright 2024 CMakePP
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
This module contains dataclasses representing each of the different
doc-comment commands CMinx recognizes. Each dataclass implements an
abstract :code:`preprocess()` method responsible for handling the
command after being extracted from the AST.

:Author: Jack Noordhuis
:License: Apache 2.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
#from logging import Logger  # TODO: Pass logger or throw exceptions on invalid commands
from typing import List, TypeVar, Type

from antlr4 import ParserRuleContext

from .documentation_types import DocumentationType
from .exceptions import DocumentationCommandSyntaxException
from .parser.CMakeParser import CMakeParser
from .rstwriter import RSTWriter


@dataclass
class AbstractDocumentationCommand(DocumentationType, ABC):
    """
    This is the base dataclass for all doc-comment commands.

    Classes in this file that inherit from this class will be used to find
    command implementations. The first character and characters following
    '-' (command word separator) will be capitalized to form the class
    name for lookup.
    """

    cmake_command: str
    """The name of the CMake command the doc-comment belongs to"""

    params: List[str]
    """The list of parameters provided to the doc-comment command"""

    start_line_offset: int
    """
    The line number where the doc-comment command starts. Offset is relative
    to the start of the doc-comment.
    """

    stop_line_offset: int
    """
    The line number where the doc-comment command stops. Only differs from
    :ref:`start_line_offset` when the command is split across multiple lines
    due to escaped newline characters.
    """

    __T = TypeVar("__T", bound="AbstractDocumentationCommand")
    """
    Generic `TypeVar` constrained to children of `AbstractDocumentationCommand`.
    """

    @abstractmethod
    def preprocess(self, ctx: CMakeParser.Command_doccommentContext, command_stack: List[__T],
                   documented: List[DocumentationType], consumed: List[ParserRuleContext],
                   invocation_ctx: CMakeParser.Command_invocationContext | None = None) -> bool:
        """
        Preprocess the doc-comment containing the command.

        TODO: Finish preprocess documentation
        """
        pass


class DocumentationHelpers:
    """
    Defines static helper methods for aggregating documentation.
    Good candidate methods for this class are small, reusable
    parts of the aggregator which require no state and can be
    classified as CMake or CMinx domain-specific logic.
    """

    __multi_invocation_commands: dict[str, str] = {
        "function": "endfunction",
        "macro": "endmacro",
        "cpp_class": "cpp_class_end"
    }
    """
    Dictionary where each key is the name of a CMake command that may have
    multiple invocations that 'belong' to the command. Values are the CMake
    command name used to mark the point where invocations are no longer
    attached to the start command.
    
    WARNING: Do not duplicate any keys or values in this dictionary or methods
             that implement the matching logic will break (check methods below.)
    """

    @staticmethod
    def starts_invocation_block(cmake_command_name: str) -> bool:
        """
        Check if a CMake command name is the start point of a potential
        invocation grouping.

        :param cmake_command_name: The command name denoting the start of
                                   a potential grouping of invocations
        :return: True if the CMake command is allowed to have multiple
                 invocations, False otherwise.
        """
        return cmake_command_name in DocumentationHelpers.__multi_invocation_commands.keys()

    @staticmethod
    def ends_invocation_block(cmake_command_name: str) -> bool:
        """
        Check if a CMake command name is the start point of a potential
        invocation grouping.

        :param cmake_command_name: The command name denoting the start
                                   of a potential grouping of invocations.
        :return: True if the CMake command is allowed to have multiple
                 invocations, False otherwise.
        """
        return cmake_command_name in DocumentationHelpers.__multi_invocation_commands.values()

    @staticmethod
    def end_invocation_block_command_for(cmake_command_name: str) -> str | None:
        """
        Get the CMake command name that marks the end point of an
        invocation block.

        :param cmake_command_name: The command name denoting the start of
                                   a potential block of invocations.
        :return: The command name denoting the end of the invocation block,
                 none if command is a single invocation
        """
        values = [key for key in DocumentationHelpers.__multi_invocation_commands.keys() if key == cmake_command_name]
        return values[0] if len(values) > 0 else None

    @staticmethod
    def start_invocation_block_command_for(cmake_command_name: str) -> str | None:
        """
        Given a CMake command name that marks the end point of an
        invocation block, get the matching start command name.

        :param cmake_command_name: The command name denoting the end of a
                                   potential invocation block
        :return: The command name denoting the start of the invocation block,
                 none if command is a single invocation
        """
        items = [items[0] for items in DocumentationHelpers.__multi_invocation_commands.items() if
                 items[1] == cmake_command_name]
        return items[0] if len(items) > 0 else None

    @staticmethod
    def extract_documentation_commands(doc_lines: List[str], cmake_command: str) -> List[AbstractDocumentationCommand]:
        """
        Extracts documentation commands (lines beginning with '@') from
        a doc-comment string. If a class named `{command_name}DocumentationCommand`
        (where `command_name` is CamelCase) is found in this scope then an
        instance of that class will be constructed, otherwise :ref:`Unknown_DocumentationCommand`
        is used.

        :param doc_lines: The doc-comment, processed by :ref:`DocumentationCommandHelpers.clean_doc_lines`
        :param cmake_command: The invoked CMake command name attached to the doc-comment
        :return: A list of found doc-comment commands to be processed
        """
        found_commands: List[AbstractDocumentationCommand] = []
        lines_processed = -1  # tracks the line count of processed lines

        current_lines_elapsed = 0  # tracks the number of lines the current command spans across
        current_args: List[str] = []  # doc-comment command line contents split on spaces
        for comment_line in doc_lines:
            lines_processed += 1
            stripped_line = comment_line.lstrip(" \t")
            line_end_index = len(stripped_line) - 1
            if line_end_index >= 0 and current_lines_elapsed == 0 and stripped_line[0] != "@":
                continue  # not a documentation command
            stripped_line = stripped_line[1:]  # remove '@' command identifier
            line_end_index -= 1
            current_arg: str = ""
            next_line_continues_params = False
            next_char_escaped = False
            for char_index in range(0, line_end_index):
                if next_char_escaped:
                    next_char_escaped = False
                    continue

                char = stripped_line[char_index]
                if char == " " or char == "\t":
                    if len(current_arg) == 0:
                        continue
                    else:
                        if stripped_line[char_index + 1] == "\\" and char_index + 2 == line_end_index:
                            next_line_continues_params = True
                            break  # escaped new line joins command parameters
                        current_args.append(current_arg)
                        current_arg = ""
                elif char == "\\":
                    if next_line_continues_params:
                        next_char_escaped = True
                        continue  # skip current and next char
                    break
                current_arg += char

            if next_line_continues_params:
                current_lines_elapsed += 1
                continue

            if len(current_arg) != 0:
                current_args.append(current_arg)

            if len(current_args) == 0:
                continue

            command_name = (
                current_args.pop(0)
                .replace("_", "")
                .replace("-", " ")
            ).lower()

            clazz_name_prefix = "".join(
                name_part[:1].upper() + name_part[1:] for name_part in command_name.split(" ")
            )

            command_name = command_name.replace(" ", "")

            clazz = Unknown_DocumentationCommand
            if f"{clazz_name_prefix}DocumentationCommand" in globals().keys():
                clazz = globals()[f"{clazz_name_prefix}DocumentationCommand"]
                if not issubclass(clazz, AbstractDocumentationCommand):
                    # Programmer error. Class name matches command name convention but doesn't inherit base class.
                    raise Exception("Tried to construct a documentation command implementation from a class not "
                                    "inheriting from `AbstractDocumentationCommand` base class.")
            found_commands.append(clazz(command_name, doc_lines, cmake_command, current_args,
                                  lines_processed, lines_processed + current_lines_elapsed))
            current_lines_elapsed = 0
            current_args = []

        return found_commands

    @staticmethod
    def replace_command_lines(doc_command: AbstractDocumentationCommand, replacement: str | None):
        doc_command.doc = (  # strip the lines containing the doc-comment command
            doc_command.doc[0:doc_command.start_line_offset - 1] + doc_command.doc[doc_command.stop_line_offset + 1:-1]
        )

        if replacement is None or len(replacement) < 1:
            return

        new_index = doc_command.start_line_offset
        for new_line in replacement.split("\n"):
            doc_command.doc.insert(new_index, new_line)
            new_index += 1

    __T = TypeVar("__T", bound=AbstractDocumentationCommand)
    """
    Generic `TypeVar` constrained to children of `AbstractDocumentationCommand`.
    """

    @staticmethod
    def commands_of_type(doc_command_type: Type[AbstractDocumentationCommand],
                         commands: list[DocumentationType]) -> list[__T]:
        return [command for command in commands if isinstance(command, doc_command_type)]


@dataclass
class Unknown_DocumentationCommand(AbstractDocumentationCommand):
    """
    Represents an unknown documentation command by implementing `AbstractDocumentationCommand`
    to log encountered unknown doc-comment commands.

    This class name will not collide with real command names as the grammar
    (`DocBlock_Command_Identifier`) disallows `_` in doc-comment command names.
    This allows searching the python `globals()` to resolve commands using
    classes defined in this files scope. The naming breaks CMinx project naming
    conventions but is less maintenance than maintaining an extra mapping/registry
    of command names to their class implementations.
    """

    def preprocess(self, ctx: CMakeParser.Command_doccommentContext, command_stack: List[AbstractDocumentationCommand],
                   documented: List[DocumentationType], consumed: List[ParserRuleContext],
                   invocation_ctx: CMakeParser.Command_invocationContext | None = None) -> bool:
        """
        #TODO: document
        """
        # TODO: Log warning on unknown doc-comment command
        return False  # notifies aggregator doc-comment command wasn't handled

    def process(self, writer: RSTWriter) -> None:
        pass  # no-op


@dataclass
class ModuleDocumentationCommand(AbstractDocumentationCommand):
    """
    Represents documentation for an entire CMake module
    """

    @staticmethod
    def default_module(name: str):
        """
        Constructs a default module documentation command. Used when
        a `@module` command is not explicitly declared in a CMake
        source file.

        :param name: The module name
        :return ModuleDocumentationCommand: The constructed module documentation
                                            command instance
        """
        return ModuleDocumentationCommand("module", [], "", [name], 0, 0)

    def module_name(self) -> str | None:
        """
        Returns the declared module name from the list of doc-comment command
        parameters. If no name was declared with the command, None is returned.
        """
        return self.params[0] if len(self.params) > 0 and len(self.params[0]) > 0 else None

    def set_module_name(self, name: str) -> None:
        if len(self.params) < 1:
            self.params.insert(0, name)
        else:
            self.params[0] = name

    def preprocess(self, ctx: CMakeParser.Command_doccommentContext, command_stack: List[AbstractDocumentationCommand],
                   documented: List[DocumentationType], consumed: List[ParserRuleContext],
                   invocation_ctx: CMakeParser.Command_invocationContext | None = None) -> bool:
        is_not_first_declaration = len(documented) > 0
        is_not_first_module_declaration = (len(
            DocumentationHelpers.commands_of_type(ModuleDocumentationCommand, documented)) > 0)

        if is_not_first_declaration or is_not_first_module_declaration:
            message = ("Found `@module` declaration in non-top-level doc-comment" if is_not_first_declaration
                       else "Multiple `@module` declarations found in file")
            abs_line_number = ctx.start.line + self.start_line_offset
            raise DocumentationCommandSyntaxException(
                f"{message}. Module declarations should appear only once per file in the top-level doc-comment.",
                abs_line_number)

        documented.append(self)
        return True  # notifies aggregator the comment is handled and not attached to invocation

    def process(self, writer: RSTWriter) -> None:
        DocumentationHelpers.replace_command_lines(self, None)

        module = writer.directive("module", self.module_name())
        if self.doc is not None and len(self.doc) > 0:
            module.text(self.get_joined_doc())


@dataclass
class NoDocDocumentationCommand(AbstractDocumentationCommand):
    """
    Marks a doc-comment and (if applicable) its invocation(s) as exempt
    from documentation.
    """

    def needs_stop_command(self) -> bool:
        return DocumentationHelpers.starts_invocation_block(self.cmake_command)

    def stop_command(self) -> str | None:
        return DocumentationHelpers.end_invocation_block_command_for(self.cmake_command)

    def preprocess(self, ctx: CMakeParser.Command_doccommentContext, command_stack: List[AbstractDocumentationCommand],
                   documented: List[DocumentationType], consumed: List[ParserRuleContext],
                   invocation_ctx: CMakeParser.Command_invocationContext | None = None) -> bool:
        # abs_line_number = ctx.start.line + self.start_line_offset
        is_first_declaration = len(consumed) <= 0 and len(documented) <= 0
        if is_first_declaration:
            # set to a command name that will be unmatched (top-level `@no-doc` applies to module)
            self.cmake_command = "module"
            # self.logger.debug(
            #     f"Skipping RST generation for CMake module "
            #     f" (found top-level `@no-doc` command on line {abs_line_num})"
            # )
        else:
            pass
            # self.logger.debug(
            #     f"Skipping RST generation for CMake command {command.cmake_command}"
            #     f" (found `@no-doc` command on line {abs_line_num})"
            # )

        command_stack.append(self)
        return True  # notifies aggregator the comment is handled and not attached to invocation

    def process(self, writer: RSTWriter) -> None:
        return  # no-op
