# Generated from /Users/jack/Development/python/CMinx/src/cminx/parser/CMake.g4 by ANTLR 4.13.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,13,59,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,1,0,1,0,1,0,1,0,5,0,19,8,0,10,0,12,0,22,9,0,1,0,1,0,1,1,1,1,3,
        1,28,8,1,1,1,1,1,1,2,1,2,1,3,1,3,1,4,1,4,1,4,1,4,5,4,40,8,4,10,4,
        12,4,43,9,4,1,4,1,4,1,5,1,5,1,6,1,6,1,6,5,6,52,8,6,10,6,12,6,55,
        9,6,1,6,1,6,1,6,0,0,7,0,2,4,6,8,10,12,0,1,2,0,5,6,8,9,60,0,20,1,
        0,0,0,2,27,1,0,0,0,4,31,1,0,0,0,6,33,1,0,0,0,8,35,1,0,0,0,10,46,
        1,0,0,0,12,48,1,0,0,0,14,19,3,2,1,0,15,19,3,8,4,0,16,19,3,4,2,0,
        17,19,3,6,3,0,18,14,1,0,0,0,18,15,1,0,0,0,18,16,1,0,0,0,18,17,1,
        0,0,0,19,22,1,0,0,0,20,18,1,0,0,0,20,21,1,0,0,0,21,23,1,0,0,0,22,
        20,1,0,0,0,23,24,5,0,0,1,24,1,1,0,0,0,25,28,3,4,2,0,26,28,3,6,3,
        0,27,25,1,0,0,0,27,26,1,0,0,0,28,29,1,0,0,0,29,30,3,8,4,0,30,3,1,
        0,0,0,31,32,5,3,0,0,32,5,1,0,0,0,33,34,5,4,0,0,34,7,1,0,0,0,35,36,
        5,5,0,0,36,41,5,1,0,0,37,40,3,10,5,0,38,40,3,12,6,0,39,37,1,0,0,
        0,39,38,1,0,0,0,40,43,1,0,0,0,41,39,1,0,0,0,41,42,1,0,0,0,42,44,
        1,0,0,0,43,41,1,0,0,0,44,45,5,2,0,0,45,9,1,0,0,0,46,47,7,0,0,0,47,
        11,1,0,0,0,48,53,5,1,0,0,49,52,3,10,5,0,50,52,3,12,6,0,51,49,1,0,
        0,0,51,50,1,0,0,0,52,55,1,0,0,0,53,51,1,0,0,0,53,54,1,0,0,0,54,56,
        1,0,0,0,55,53,1,0,0,0,56,57,5,2,0,0,57,13,1,0,0,0,7,18,20,27,39,
        41,51,53
    ]

class CMakeParser ( Parser ):

    grammarFileName = "CMake.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'('", "')'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "Command_DocBlock", 
                      "DocBlock", "Identifier", "Unquoted_argument", "Escape_sequence", 
                      "Quoted_argument", "Bracket_argument", "Bracket_comment", 
                      "Line_comment", "Newline", "Space" ]

    RULE_cmake_file = 0
    RULE_documented_command = 1
    RULE_command_doccomment = 2
    RULE_bracket_doccomment = 3
    RULE_command_invocation = 4
    RULE_single_argument = 5
    RULE_compound_argument = 6

    ruleNames =  [ "cmake_file", "documented_command", "command_doccomment", 
                   "bracket_doccomment", "command_invocation", "single_argument", 
                   "compound_argument" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    Command_DocBlock=3
    DocBlock=4
    Identifier=5
    Unquoted_argument=6
    Escape_sequence=7
    Quoted_argument=8
    Bracket_argument=9
    Bracket_comment=10
    Line_comment=11
    Newline=12
    Space=13

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Cmake_fileContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(CMakeParser.EOF, 0)

        def documented_command(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CMakeParser.Documented_commandContext)
            else:
                return self.getTypedRuleContext(CMakeParser.Documented_commandContext,i)


        def command_invocation(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CMakeParser.Command_invocationContext)
            else:
                return self.getTypedRuleContext(CMakeParser.Command_invocationContext,i)


        def command_doccomment(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CMakeParser.Command_doccommentContext)
            else:
                return self.getTypedRuleContext(CMakeParser.Command_doccommentContext,i)


        def bracket_doccomment(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CMakeParser.Bracket_doccommentContext)
            else:
                return self.getTypedRuleContext(CMakeParser.Bracket_doccommentContext,i)


        def getRuleIndex(self):
            return CMakeParser.RULE_cmake_file

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCmake_file" ):
                listener.enterCmake_file(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCmake_file" ):
                listener.exitCmake_file(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCmake_file" ):
                return visitor.visitCmake_file(self)
            else:
                return visitor.visitChildren(self)




    def cmake_file(self):

        localctx = CMakeParser.Cmake_fileContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_cmake_file)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 20
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 56) != 0):
                self.state = 18
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
                if la_ == 1:
                    self.state = 14
                    self.documented_command()
                    pass

                elif la_ == 2:
                    self.state = 15
                    self.command_invocation()
                    pass

                elif la_ == 3:
                    self.state = 16
                    self.command_doccomment()
                    pass

                elif la_ == 4:
                    self.state = 17
                    self.bracket_doccomment()
                    pass


                self.state = 22
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 23
            self.match(CMakeParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Documented_commandContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def command_invocation(self):
            return self.getTypedRuleContext(CMakeParser.Command_invocationContext,0)


        def command_doccomment(self):
            return self.getTypedRuleContext(CMakeParser.Command_doccommentContext,0)


        def bracket_doccomment(self):
            return self.getTypedRuleContext(CMakeParser.Bracket_doccommentContext,0)


        def getRuleIndex(self):
            return CMakeParser.RULE_documented_command

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDocumented_command" ):
                listener.enterDocumented_command(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDocumented_command" ):
                listener.exitDocumented_command(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDocumented_command" ):
                return visitor.visitDocumented_command(self)
            else:
                return visitor.visitChildren(self)




    def documented_command(self):

        localctx = CMakeParser.Documented_commandContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_documented_command)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 27
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [3]:
                self.state = 25
                self.command_doccomment()
                pass
            elif token in [4]:
                self.state = 26
                self.bracket_doccomment()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 29
            self.command_invocation()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Command_doccommentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Command_DocBlock(self):
            return self.getToken(CMakeParser.Command_DocBlock, 0)

        def getRuleIndex(self):
            return CMakeParser.RULE_command_doccomment

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCommand_doccomment" ):
                listener.enterCommand_doccomment(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCommand_doccomment" ):
                listener.exitCommand_doccomment(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCommand_doccomment" ):
                return visitor.visitCommand_doccomment(self)
            else:
                return visitor.visitChildren(self)




    def command_doccomment(self):

        localctx = CMakeParser.Command_doccommentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_command_doccomment)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 31
            self.match(CMakeParser.Command_DocBlock)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Bracket_doccommentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DocBlock(self):
            return self.getToken(CMakeParser.DocBlock, 0)

        def getRuleIndex(self):
            return CMakeParser.RULE_bracket_doccomment

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBracket_doccomment" ):
                listener.enterBracket_doccomment(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBracket_doccomment" ):
                listener.exitBracket_doccomment(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBracket_doccomment" ):
                return visitor.visitBracket_doccomment(self)
            else:
                return visitor.visitChildren(self)




    def bracket_doccomment(self):

        localctx = CMakeParser.Bracket_doccommentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_bracket_doccomment)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 33
            self.match(CMakeParser.DocBlock)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Command_invocationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Identifier(self):
            return self.getToken(CMakeParser.Identifier, 0)

        def single_argument(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CMakeParser.Single_argumentContext)
            else:
                return self.getTypedRuleContext(CMakeParser.Single_argumentContext,i)


        def compound_argument(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CMakeParser.Compound_argumentContext)
            else:
                return self.getTypedRuleContext(CMakeParser.Compound_argumentContext,i)


        def getRuleIndex(self):
            return CMakeParser.RULE_command_invocation

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCommand_invocation" ):
                listener.enterCommand_invocation(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCommand_invocation" ):
                listener.exitCommand_invocation(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCommand_invocation" ):
                return visitor.visitCommand_invocation(self)
            else:
                return visitor.visitChildren(self)




    def command_invocation(self):

        localctx = CMakeParser.Command_invocationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_command_invocation)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 35
            self.match(CMakeParser.Identifier)
            self.state = 36
            self.match(CMakeParser.T__0)
            self.state = 41
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 866) != 0):
                self.state = 39
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [5, 6, 8, 9]:
                    self.state = 37
                    self.single_argument()
                    pass
                elif token in [1]:
                    self.state = 38
                    self.compound_argument()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 43
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 44
            self.match(CMakeParser.T__1)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Single_argumentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Identifier(self):
            return self.getToken(CMakeParser.Identifier, 0)

        def Unquoted_argument(self):
            return self.getToken(CMakeParser.Unquoted_argument, 0)

        def Bracket_argument(self):
            return self.getToken(CMakeParser.Bracket_argument, 0)

        def Quoted_argument(self):
            return self.getToken(CMakeParser.Quoted_argument, 0)

        def getRuleIndex(self):
            return CMakeParser.RULE_single_argument

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSingle_argument" ):
                listener.enterSingle_argument(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSingle_argument" ):
                listener.exitSingle_argument(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSingle_argument" ):
                return visitor.visitSingle_argument(self)
            else:
                return visitor.visitChildren(self)




    def single_argument(self):

        localctx = CMakeParser.Single_argumentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_single_argument)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 46
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 864) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Compound_argumentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def single_argument(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CMakeParser.Single_argumentContext)
            else:
                return self.getTypedRuleContext(CMakeParser.Single_argumentContext,i)


        def compound_argument(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CMakeParser.Compound_argumentContext)
            else:
                return self.getTypedRuleContext(CMakeParser.Compound_argumentContext,i)


        def getRuleIndex(self):
            return CMakeParser.RULE_compound_argument

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCompound_argument" ):
                listener.enterCompound_argument(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCompound_argument" ):
                listener.exitCompound_argument(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCompound_argument" ):
                return visitor.visitCompound_argument(self)
            else:
                return visitor.visitChildren(self)




    def compound_argument(self):

        localctx = CMakeParser.Compound_argumentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_compound_argument)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 48
            self.match(CMakeParser.T__0)
            self.state = 53
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 866) != 0):
                self.state = 51
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [5, 6, 8, 9]:
                    self.state = 49
                    self.single_argument()
                    pass
                elif token in [1]:
                    self.state = 50
                    self.compound_argument()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 55
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 56
            self.match(CMakeParser.T__1)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





