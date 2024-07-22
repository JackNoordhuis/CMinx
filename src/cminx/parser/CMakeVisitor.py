# Generated from /Users/jack/Development/python/CMinx/src/cminx/parser/CMake.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .CMakeParser import CMakeParser
else:
    from CMakeParser import CMakeParser

# This class defines a complete generic visitor for a parse tree produced by CMakeParser.

class CMakeVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by CMakeParser#cmake_file.
    def visitCmake_file(self, ctx:CMakeParser.Cmake_fileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CMakeParser#documented_command.
    def visitDocumented_command(self, ctx:CMakeParser.Documented_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CMakeParser#command_doccomment.
    def visitCommand_doccomment(self, ctx:CMakeParser.Command_doccommentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CMakeParser#bracket_doccomment.
    def visitBracket_doccomment(self, ctx:CMakeParser.Bracket_doccommentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CMakeParser#command_invocation.
    def visitCommand_invocation(self, ctx:CMakeParser.Command_invocationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CMakeParser#single_argument.
    def visitSingle_argument(self, ctx:CMakeParser.Single_argumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CMakeParser#compound_argument.
    def visitCompound_argument(self, ctx:CMakeParser.Compound_argumentContext):
        return self.visitChildren(ctx)



del CMakeParser