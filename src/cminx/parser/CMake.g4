/*
Copyright (c) 2018  zbq.

License for use and distribution: Eclipse Public License

CMake language grammar reference:
https://cmake.org/cmake/help/v3.12/manual/cmake-language.7.html

Modified by Branden Butler on behalf of Ames Laboratory/Department of Energy
October 31st, 2019

*/

grammar CMake;

/*
Changes:
	Renamed from file to cmake_file to avoid conflict with Python
	Added documented_command to list of expected parser rules
	Added bracket_doccomment to parser rules
	Added bracket_doccomment to top-level parse rule, enabling dangling doccomments
	Added Module_DocBlock, NoDoc_DocBlock, Command_DocBlock to lexer rules
	Added nodoc_doccomment as alternative to bracket_comment for documented_command parser rule
*/

/*Begin CMinx*/

/*
    WARNING: This grammar is ambiguous because of the bracket_doccomment alternative.
    Ambiguity is resolved via order of alternatives, ensure order is consistent
    with the desired precedence.
*/
cmake_file
	: (documented_command | command_invocation | command_doccomment | bracket_doccomment)* EOF
	;


/*
    WARNING: This grammar is also ambiguous because of the command_doccomment alternative.
*/
documented_command
	: (command_doccomment | bracket_doccomment) command_invocation
	;

command_doccomment
    : Command_DocBlock
    ;

bracket_doccomment
    : DocBlock
    ;

Command_DocBlock
    : DocBlock_Start .*? Command_DocString .*? DocBlock_End
    ;

fragment
Command_DocString
    : ~[\\] '@' DocBlock_Command_Identifier
    ;

fragment
DocBlock_Command_Identifier
    : [A-Za-z\-][A-Za-z0-9\-]*
    ;

DocBlock
    : DocBlock_Start .*? DocBlock_End
    ;

fragment
DocBlock_Start
    : Space*? '#[[['
    ;

fragment
DocBlock_End
    : Space*? '#]]'
    ;

/*End Cminx*/

command_invocation
	: Identifier '(' (single_argument|compound_argument)* ')'
	;

single_argument
	: Identifier | Unquoted_argument | Bracket_argument | Quoted_argument
	;

compound_argument
	: '(' (single_argument|compound_argument)* ')'
	;

Identifier
	: [A-Za-z_][A-Za-z0-9_]*
	;

Unquoted_argument
	: (~[ \t\r\n()#"\\] | Escape_sequence)+
	;

Escape_sequence
	: Escape_identity | Escape_encoded | Escape_semicolon
	;

fragment
Escape_identity
	: '\\' ~[A-Za-z0-9;]
	;

fragment
Escape_encoded
	: '\\t' | '\\r' | '\\n'
	;

fragment
Escape_semicolon
	: '\\;'
	;

Quoted_argument
	: '"' (~[\\"] | Escape_sequence | Quoted_cont)* '"'
	;

fragment
Quoted_cont
	: '\\' ('\r' '\n'? | '\n')
	;

Bracket_argument
	: '[' Bracket_arg_nested ']'
	;

fragment
Bracket_arg_nested
	: '=' Bracket_arg_nested '='
	| '[' .*? ']'
	;




Bracket_comment
	: '#[' Bracket_arg_nested ']'
	-> skip
	;

Line_comment
	: '#' (  // #
	  	  | '[' '='*   // #[==
		  | '[' '='* ~('=' | '[' | '\r' | '\n') ~('\r' | '\n')*  // #[==xx
		  | ~('[' | '\r' | '\n') ~('\r' | '\n')*  // #xx
		  ) ('\r' '\n'? | '\n' | EOF)
    -> skip
	;

Newline
	: ('\r' '\n'? | '\n')+
	-> skip
	;

Space
	: [ \t]+
	-> skip
	;


