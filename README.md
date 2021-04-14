# Compiler for Cimple programming language.

Cimple is a minified version of C programming language . While it doesnt support some of the basic features and tools that C does , 
it provides a wide variety of structures and elements that have very intresting implementation patterns. Cimple supports functions and procedures , 
parameter passing by value or by reference, complex conditional loops , recursion calls and even nesting in function declaration and many more.

Task: Given a source program written in Cimple , generate the final code written in assembly.

The phaces of the implementation are the following:
•Lexical Analysis  
•Syntax Analysis  
•Intermidiate Code Generation  
•Symbol Table / Meaning Analysis  
•Final Code Generation  

Grammar of Cimple (follows the LL(1) principle):  

program : program ID block .  
block : declarations subprograms statements  
declarations : ( declare varlist ; )∗  
varlist : ID ( , ID )∗ | ε  
subprograms : ( subprogram )∗  
subprogram : function ID ( formalparlist ) block | procedure ID ( formalparlist ) block  
formalparlist : formalparitem ( , formalparitem )∗ | ε  
formalparitem : in ID | inout ID  
statements : statement ; | { statement ( ; statement )∗ }  
statement : assignStat | ifStat | whileStat | switchcaseStat | forcaseStat | incaseStat | callStat | returnStat | inputStat | printStat | ε  
assignStat : ID := expression  
ifStat : if ( condition ) statements elsepart  
elsepart : else statements | ε  

whileStat : while ( condition ) statements  
switchcaseStat: switchcase ( case ( condition ) statements )∗ default statements  
forcaseStat : forcase ( case ( condition ) statements )∗ default statements  
incaseStat : incase ( case ( condition ) statements )∗  
returnStat : return( expression )  
callStat : call ID( actualparlist )  
printStat : print( expression )  
inputStat : input( ID )  
actualparlist : actualparitem ( , actualparitem )∗ | ε  
actualparitem : in expression | inout ID  
condition : boolterm ( or boolterm )∗  

boolterm : boolfactor ( and boolfactor )∗  
boolfactor : not [ condition ] | [ condition ] | expression REL_OP expression  
expression : optionalSign term ( ADD_OP term )∗  
term : factor ( MUL_OP factor )∗  
factor : INTEGER | ( expression ) | ID idtail  
idtail : ( actualparlist ) | ε  
optionalSign : ADD_OP | ε  
REL_OP : = | <= | >= | > | < | <> ; ADD_OP : + |   
MUL_OP : * | /  
INTEGER : [0-9]+  
ID : [a-zA-Z][a-zA-Z0-9]*  




