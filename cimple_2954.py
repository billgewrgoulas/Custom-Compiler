#Vasileios Gewrgoulas
#AM 2954
#UN cse52954

import sys

########################################categories######################################
key_words = {
                'program': 'program_tk', 'declare': 'declare_tk', 'if': 'if_tk',
                'else':'else_tk', 'while':'while_tk', 'switchcase' : 'switchcase_tk',
                'forcase': 'forcase_tk', 'incase': 'incase_tk', 'case': 'case_tk',
                'default':'default_tk', 'not':'not_tk', 'and':'and_tk', 'in':'in_tk' ,
                'or': 'or_tk', 'function': 'function_tk', 'procedure': 'procedure_tk',
                'call': 'call_tk', 'return': 'return_tk', 'input': 'input_tk',
                'print' : 'print_tk' , 'inout' : 'inout_tk'
            }

addOperator = {'+': 'plus_tk', '-': 'minus_tk'}

mulOperator = {'*': 'mul_tk', '/': 'div_tk'}

relOper = {
            '<': 'lt_tk', '>': 'gt_tk', '=': 'eq_tk',
            '<=': 'leq_tk', '>=': 'geq_tk', '<>': 'neq_tk'
          }
            
assign = {':=': 'assign_tk'}

delim = {';': 'semcol_tk', ',': 'comma_tk'}

groupSymbol = {
                '[': 'lbracket_tk', ']': 'rbracket_tk',
                '{': 'lbrace_tk', '}': 'rbrace_tk',
                '(': 'lpar_tk', ')': 'rpar_tk'
              }

end = {'.': 'end_tk'}

comments = {'#': 'comment_tk'}

##########################################global vars#########################################

line = 1
char = ''
token = ''
file = ''
temp = 0
quadNo = -1
programName = ''
varList = []   #vars in use
quadList = []  #each element will be in the form of [ quadNo , op , x , y , z ]

class Token:
    def __init__(self, tokenType, tokenString, lineNo):
        self.tokenType = tokenType       #category , can be identifier,number , keyword , addOperator...
        self.tokenString = tokenString   #actual symbol
        self.lineNo = lineNo             #current line
        
    def get_tokenString(self):
        return self.tokenString

    def get_tokenType(self):
        return self.tokenType


###################################intermediate code helpers####################################

def nextQuad():
    global quadNo
    return (quadNo + 1)
    
def genQuad(op, x, y, z):
    global quadList, quadNo
    quadNo += 1
    quadList.append([quadNo, str(op), str(x), str(y), str(z)])
    
def newTemp():
    global tempvarList, temp
    tempvar = 'T_' + str(temp)
    temp += 1
    varList.append(tempvar)
    return tempvar

def emptyList():
    return []

def makeList(x):
    return [str(x)]
    
def merge(list1, list2):
    return list1 + list2

def backpatch(quadLabels, z):
    global quadList
    
    for label in quadLabels:
        quadList[int(label)][4] = str(z)

##################################generate .c/.int files################################

def genInt():
    global quadList

    outFile = ''
    try:
        outFile = open('out.int', 'w')
    except:
        print('file could not be created')
        exit(1)
    
    for quad in quadList:
        outFile.write('%s: %s , %s , %s , %s \n' % (quad[0], quad[1], quad[2], quad[3], quad[4]))
    outFile.close()

def genC():
    global quadList , varList

    outFile = ''
    try:
        outFile = open('out.c', 'w')
    except:
        print('file could not be created')
        exit(1)
    outFile.write('int main()\n{')

    text = '  int '
    for var in varList:
        text += str(var) + ','
    outFile.write(text[:-1] + ';\n')

    for quad in quadList:
        instruction = '   L_' + str(quad[0]) + ': '
        if quad[1] == ':=':
            instruction += str(quad[4]) + ' = ' + str(quad[2]) + ';\n'
        elif quad[1] == 'jump':
            instruction += 'goto ' + 'L_' + str(quad[4]) + ';\n'
        elif quad[1] in addOperator.keys() or quad[1] in mulOperator.keys():
            instruction += str(quad[4]) + ' = ' + str(quad[2]) + str(quad[1]) + str(quad[3]) + ';\n'
        elif quad[1] in relOper.keys():
            op = quad[1]
            if op == '<>': op = '!='
            if op == '=' : op = '=='
            instruction += 'if (' + str(quad[2]) + op + str(quad[3]) + ') goto ' + 'L_' + str(quad[4]) + ';\n'
        elif quad[1] == 'retv':
            instruction += 'return(' + str(quad[2]) + ')' + ';\n'
        elif quad[1] == 'call':
            instruction += '{};\n'
        elif quad[1] == 'inp':
            instruction += 'scanf(' + str(quad[2]) + ')' + ';\n'
        elif quad[1] == 'out':
            instruction += 'printf(' + str(quad[2]) + ')' + ';\n'
        else:
            instruction += '{};\n'   
        outFile.write(instruction)
    outFile.write('}')
    outFile.close()

##################################lexical analysis######################################

#read char by char
def getNext():
    global line , char , file

    char = file.read(1)
    if not char:
        print('program was not terminated properly')
        exit(1)
    if char == '\n':
        line+=1    
      
def potentialNumber():
    global char , line

    text = ''
    while 1:
        if not char.isdigit():
            break
        text += char
        getNext()
    if char.isalpha():
        text += char
        print("invalid number: %s at line: %s" % (text , line))
        exit(1)
    if int(text) > pow(2,32) - 1 or int(text) < -pow(2,32) + 1:
        print(int(text))
        print('error at line: %s , number out of bounds' % (line))
        exit(1)
    return Token('int_tk' , text , line)
        #not sure if its complete here

#ignore
def comments():
    global char, line
    
    while 1:
        getNext()
        if char == '#':
            break
        if not len(char):
            print('Error: close comment tag was not detected.')
            exit(1)
    getNext()
    return Token('comment_tk' , '#' , line)

def identOrKey():
    global char , line
    text = ''

    while 1:
        if char.isalnum():
            text += char
            getNext()
        else:
            break

    if text in key_words.keys():
        return Token( key_words[text] , text, line)

    if text.isalnum():
        return Token('id_tk', text, line)
    
    if len(text) > 30:
        print('error: character: %s , at line: %s ' % (text, line))
        print('a word can not be more than 30 characters')
        exit(1)
    #not sure if its complete here
        
def addOp():
    global char , line
    temp = char
    getNext()
    return Token( addOperator[temp] , temp , line)

def mulOp():
    global char , line
    temp = char
    getNext()
    return Token( mulOperator[temp] , temp, line)

def groupSym():
    global char , line
    temp = char
    getNext()
    return Token( groupSymbol[temp] , temp, line)
    
def delimSym():
    global char , line
    temp = char
    getNext()
    return Token( delim[temp] , temp, line)
    
def assignOp():
    global char , line

    getNext()
    if char != '=':
        print('error , expected = but got %s , at line %s' % (char ,line))
        exit(1)
    getNext()
    return Token('assign_tk', ':=', line)
    
def relOp():
    global char , line
 
    if char == '=':
        getNext()
        return Token('eq_tk', '=', line)
    
    temp = char
    #sneak peek
    getNext()
    if char.isalnum() or char.isspace() or char in addOperator.keys():
        return Token( relOper[temp] , temp, line)
    if temp == '<' and char == '=':
        getNext()
        return Token('leq_tk', '<=', line)
    if temp == '<' and char == '>':
        getNext()
        return Token('neq_tk', '<>', line)
    if temp == '>' and char == '=':
        getNext()
        return Token('geq_tk', '>=', line)
    if not char.isalnum():
        print('error invalid character: %s , at line: %s ' % (temp+char,line))
        exit(1)
        
def endOfProgram():
    global line
    return Token('end_tk','.',line)

#driver function of lexical analysis that determines the token type. 
#Depending on the incoming symbol we follow the corresponding transition.
def tokenResolver():
    global char , line

    while char.isspace():
        getNext()
    
    while 1:
        #states
        if char == '#':
            return comments()
        
        if char.isdigit():
            return potentialNumber()

        if char.isalnum():
            return identOrKey()

        if char in addOperator.keys():
            return addOp()

        if char in mulOperator.keys():
            return mulOp()

        if char in groupSymbol.keys():
            return groupSym()

        if char in delim.keys():
            return delimSym()

        if char == ':':
            return assignOp()

        if char in relOper.keys():
            return relOp()
    
        if char == '.':
            return endOfProgram()
        print('illegal character detected at line: %s' % line)
        exit(1)

def lex():
    global varList

    tempToken = tokenResolver()
    while tempToken.get_tokenType() == 'comment_tk':
        tempToken = tokenResolver()
    if tempToken.get_tokenType() == 'id_tk' and not tempToken.get_tokenString() in varList:
        varList.append(tempToken.get_tokenString())
    return [ str(tempToken.get_tokenType()) , str(tempToken.get_tokenString()) ]
    

###########################syntax analysis############################

def program():
    global token , quadList , programName
    getNext()
    token = lex() #initialize token for the first time
    
    if token[0] ==  'program_tk':
        token = lex()
        if token[0] ==  'id_tk':
            programName = token[1]  
            token = lex()
            block(programName)
            if token[0] == 'end_tk':
                genInt()
                genC()
                print('Program compiled succesfully. ')
            else:
                print('program was not ended properly' )
                exit(1)
        else:
            print('program name was expected')
            exit(1)
    else:
        print('keyword: program was expcted')
        exit(1)

def block(blockName):
    global programName
    declarations()
    genQuad('begin_block', blockName, '_', '_')
    subprograms()
    statements()
    if blockName == programName:
        genQuad('halt' , '_' , '_' , '_')
    genQuad('end_block',blockName,'_','_')

def declarations():
    global token , line

    while token[0] ==  'declare_tk':
        token = lex()
        varlist()
        if token[0] ==  'semcol_tk':
            token = lex()
        else:
            print('error , ; was expected at line %s' % line)
            
def varlist():
    global token , line

    if token[0] ==  'id_tk':
        token = lex()
        while token[0] ==  'comma_tk':
            token = lex()
            if token[0] ==  'id_tk':
                token = lex()
            else:
                print('parameter declaration was expected at line: %s' % line)
                exit(1)

def subprograms():
    global token , line

    while token[0] ==  'function_tk' or token[0] == 'procedure_tk':
        token = lex()
        if token[0] == 'id_tk':
            name = token[1]
            token = lex()
            if token[0] ==  'lpar_tk':
                token = lex()
                formalparlist()
                if token[0] ==  'rpar_tk':
                    token = lex()
                    block(name)
                else:
                    print('error , expected: ) at line: %s' % line)
                    exit(1)
            else:
                print('error , expected: ( at line: %s' % line)
                exit(1)
        else:
            print('error , subprogram name was expected at line: %s' % line)
            exit(1)

def formalparlist():
    global token

    formalparitem()
    while token[0] ==  'comma_tk':
        token = lex()
        formalparitem()

def formalparitem():
    global token , line

    if token[0] ==  'in_tk':
        token = lex()
        if token[0] ==  'id_tk':
            token = lex()
        else:
            print('error , expected: identifier at line: %s' % line)
            exit(1)
    elif token[0] ==  'inout_tk':
        token = lex()
        if token[0] ==  'id_tk':
            token = lex()
        else:
            print('error , expected: identifier at line: %s' % line)
            exit(1)
    elif token[0] != ')':
        print('error , type of param must be specified')
        exit(1)
    #else continue so formalparlist can return e

def statements():
    global token , line

    if token[0] == 'lbrace_tk':
        token = lex()
        statement()
        while token[0] == 'semcol_tk':
            token = lex()
            statement()
        if token[0] == 'rbrace_tk':
            token = lex()
        else:                     #must fixt this
            print('error , expected } or ; at line: %s' % (line -1))
            exit(1)
    else:
        statement()
        if token[0] == 'semcol_tk':
            token = lex()
        else:
            print('error , expected: ; at line: %s' % line)
            exit(1)

def assignStat(name):
    global token , line

    if token[0] == 'assign_tk':
        token = lex()     #result of the expression , will be either an id or a tempValue
        genQuad(':=' , expression() , '_' , name )
    else:
        print('error , expected: := at line: %s' % line)
        exit(1)

def ifStat():
    global token , line

    if token[0] ==  'lpar_tk':
        token = lex()
        (Btrue, Bfalse) = condition()
        if token[0] ==  'rpar_tk':
            token = lex()
            backpatch(Btrue, nextQuad())    #if cond is true continue to the next quad
            statements()
            ifList = makeList(nextQuad())   #save the next quad label and patch it later with the very first stat after else stats
            genQuad('jump', '_', '_', '_')
            backpatch(Bfalse , nextQuad())  #now we know where to go , after the if statements in case of falsy cond , else part
            elsepart()
            backpatch(ifList , nextQuad())  #contains the jump quad label above 
        else:
            print('error , expected: ) at line: %s' % line)
            exit(1)
    else:
        print('error , expected: ( at line: %s' % line)
        exit(1)

def elsepart():
    global token

    if token[0] ==  'else_tk':
        token = lex()
        statements()

def whileStat():        # S -> while B stats
    global token , line

    if token[0] == 'lpar_tk':
        token = lex()
        Bquad = nextQuad()  # similar to if but we need to jump up to check again
        (Btrue , Bfalse) = condition()
        if token[0] == 'rpar_tk':
            token = lex()
            backpatch(Btrue , nextQuad()) #if true continue to stats
            statements()
            genQuad('jump', '_', '_', Bquad)
            backpatch(Bfalse , nextQuad())   #if falsy exit 
        else:
            print('error , expected: ) at line: %s' % line)
            exit(1)
    else:
        print('error , expected: ( at line: %s' % line)
        exit(1)

def switchcaseStat():   
    global token , line

    exit = emptyList()                            #save all exit jump outs inside each case
    while token[0] == 'case_tk':
        token = lex()
        if token[0] == 'lpar_tk':
            token = lex()
            (Btrue , Bfalse) = condition()
            if token[0] == 'rpar_tk':
                token = lex()
                backpatch(Btrue, nextQuad())
                statements()
                exit.append(nextQuad())  
                genQuad('jump', '_', '_', '_')     #truthy , jump out , default gets ignored
                backpatch(Bfalse , nextQuad())     #next case or default
            else:
                print('error , expected: ) at line: %s' % line)
                exit(1)
        else:
            print('error , expected: ( at line: %s' % line)
            exit(1)
    if token[0] == 'default_tk':
        token = lex()
        statements()
        backpatch(exit , nextQuad())  #patch all jump out quads
    else:
        print('error , expected: default case at line: %s' % line)
        exit(1)

def forcaseStat():
    global token , line

    Bquad = nextQuad()
    while token[0] ==  'case_tk':
        token = lex()
        if token[0] ==  'lpar_tk':
            token = lex()
            (Btrue , Bfalse) = condition()
            if token[0] ==  'rpar_tk':
                token = lex()
                backpatch(Btrue , nextQuad())
                statements()
                genQuad('jump' , '_' , '_' , Bquad) #if truthy jump up
                backpatch(Bfalse , nextQuad())
            else:
                print('error , expected: ) at line: %s' % line)
                exit(1)
        else:
            print('error , expected: ( at line: %s' % line)
            exit(1)
    if token[0] ==  'default_tk':
        token = lex()
        statements() #if no condition is met then the Bfalse jumps will lead us here
    else:
        print('error , expected: default case at line: %s' % line)
        exit(1)

def incaseStat():              
    global token , line

    temp = (newTemp(), nextQuad())      #save start of current incase
    genQuad(':=' , '0' , '_' , temp[0]) #always set temp to zero at start
    while token[0] == 'case_tk':
        token = lex()
        if token[0] == 'lpar_tk':
            token = lex()
            (Btrue , Bfalse) = condition()
            if token[0] == 'rpar_tk':
                token = lex()
                backpatch(Btrue , nextQuad()) #patch remaining quads
                statements()
                genQuad(':=' , '1' , '_' , temp[0])  #update temp
                backpatch(Bfalse , nextQuad())
            else:
                print('error , expected: ) at line: %s' % line)
                exit(1)
        else:
            print('error , expected: ( at line: %s' % line)
            exit(1)
    genQuad('=' , '1' , temp[0] , temp[1] )  #if temp[0] == 1 jump up 
    
def returnStat():
    global token , line

    if token[0] ==  'lpar_tk':
        token = lex()
        genQuad('retv' , expression() , '_' , '_') #return the very last result of the expression
        if token[0] ==  'rpar_tk':
            token = lex()  
        else:
            print('error , expected ) at line %s' % line)
            exit(1)
    else:
        print('error , expected ( at line %s' % line)
        exit(1)

def callStat():
    global token , line

    if token[0] == 'id_tk':
        name = token[1]
        token = lex()
        if token[0] ==  'lpar_tk':
            token = lex()
            parlist = actualparlist()
            if token[0] ==  'rpar_tk':
                token = lex()
                new_temp = newTemp()
                for par in parlist:                         #generate quads here instead of inside parlist 
                    genQuad('par', par[0], par[1], '_')
                genQuad('par', new_temp, 'RET', '_')        #new_temp stores return 
                genQuad('call', '_', '_', name)
                return new_temp
            else:
                print('error , expected ) at line %s' % line)
                exit(1)
        else:
            print('error , expected ( at line %s' % line)
            exit(1)
    else:
        print('error , expected id declaration at line %s' % line)
        exit(1)

def printStat():
    global token , line

    if token[0] ==  'lpar_tk':
        token = lex()    #print the very last result of the expression  
        genQuad('out' , expression() , '_' , '_')
        if token[0] ==  'rpar_tk':
            token = lex()
        else:
            print('error , expected ) at line %s' % line)
            exit(1)
    else:
        print('error , expected ( at line %s' % line)
        exit(1)

def inputStat():
    global token , line

    if token[0] ==  'lpar_tk':
        token = lex()
        if token[0] == 'id_tk':
            in_id = token[1]
            token = lex()
            if token[0] ==  'rpar_tk':
                token = lex()
                genQuad('inp' , in_id , '_' , '_')
            else:
                print('error , expected ) at line %s' % line)
                exit(1)
        else:
            print('error , expected id at line %s' % line)
            exit(1)
    else:
        print('error , expected ( at line %s' % line)
        exit(1)

def condition():                         #B -> Q1( or Q2 )* 
    global token

    (Btrue , Bfalse) = boolterm()        
    while token[0] == 'or_tk':
        backpatch(Bfalse , nextQuad())    #we do the opposite of and ,       
        token = lex()                     #if left evaluation false , on to the next
        (Q2true, Q2false) = boolterm()
        Btrue = merge(Btrue, Q2true)
        Bfalse = Q2false
    return (Btrue , Bfalse)               #need to return in case of recursion
        
def boolterm():                           #Q -> R1( and R2 )*
    global token

    (Qtrue , Qfalse) = boolfactor()       #retrieve R1 lists
    while token[0] == 'and_tk':
        backpatch(Qtrue , nextQuad())     #if the left is true we only have to evalute right -> next quad
        token = lex()
        (R2true, R2false) = boolfactor()  #get the R2 lists
        Qfalse = merge(Qfalse, R2false)   #if R2 is false then we can say that Q is also false
        Qtrue = R2true                    #if R1 true then if R2 true then we can say that Q is true
    return (Qtrue , Qfalse)               #send them over to B rule

def boolfactor():
    global token , line

    if token[0] ==  'not_tk':
        token = lex()
        if token[0] ==  'lbracket_tk':
            token = lex()
            (Btrue, Bfalse) = condition() #  R -> not [B] , swap lists
            if token[0] ==  'rbracket_tk':
                token = lex()
                return (Bfalse , Btrue)
            else:
                print('error , expected ] at line %s' % line)
                exit(1)
        else:
            print('error , expected [ at line %s' % line)
            exit(1)
    elif token[0] ==  'lbracket_tk':  
        token = lex()            
        (Btrue , Bfalse ) = condition()     #nothing interesting here :(     
        if token[0] ==  'rbracket_tk':
            token = lex()
            return (Btrue , Bfalse)
        else:
            print('error , expected ] at line %s' % line)
            exit(1)
    else:               
        left = expression()                 #  R -> left relop right  , all conditions will end up here eventually
        if token[0] in relOper.values():
            op = token[1]
            token = lex()
            right = expression()
            Rtrue = makeList(nextQuad())    #truethy evaluation
            genQuad(op, left, right, '_')
            Rfalse = makeList(nextQuad())     #list containing the jump label , falsy evaluation
            genQuad('jump', '_', '_', '_')  #falsy evaluation
            return (Rtrue , Rfalse)
        else:
            print('expected a relational operator at line: %s' % line)

def expression():                #exp -> termLeft | termLeft addOp termRight addOp ....
    global token, line

    sign = optionalSign()
    left = term()
    if sign == '-':
        temp = newTemp()         #if we have a sign then  [sign , 0 , left , temp]
        genQuad('-', 0, left, temp)
        left = temp

    while token[0] in addOperator.values():    
        op = token[1]
        token = lex()
        right = term()          
        temp = newTemp()
        genQuad(op, left, right, temp)
        left = temp
    return left 
                  #END RESULT wich holds the value of the expression 
                  # ex for p := x+y  we need to return T_i where T_i = x+y then p := T_i
def term():
    global token

    left = factor()       #term -> factorLeft | factorLeft mulOp factorRight mulOp ...
    while token[0] in mulOperator.values():
        op = token[1]
        token = lex()
        right = factor()
        temp = newTemp()
        genQuad(op, left, right, temp)
        left = temp
    return left

def factor():
    global token , line

    if token[0] == 'int_tk':
        temp = token[1]
        token = lex()
        return temp               #just an int in our expression , send it as is
    elif token[0] ==  'lpar_tk':
        token = lex()
        nestedTemp = expression() #nested expression , (exp)
        if token[0] ==  'rpar_tk':
            token = lex()
            return nestedTemp     #after evaluation return the very last factor ( T_i or id )
        else:
            print('error , expected ) at line %s' % line)
            exit(1)
    elif token[0] == 'id_tk':     #can be just an id or return value holder#
        temp = token[1]
        token = lex()
        func = idtail(temp)
        if func != 'no_func_call':
            return func   # we have a func call so we need  T_i , which holds the return result
        return temp       #simple identifier
    else:
        print('error at line %s , expected identifier or a number')
        exit(1)

def actualparlist():
    global token
    parlist = []

    param = actualparitem()
    parlist.append(param)
    
    while token[0] == 'comma_tk': #we should not generate the quads here directly
        token = lex()             #this should happen when parlist returns 
        param = actualparitem()
        parlist.append(param)
    return parlist

def actualparitem():
    global token , line

    if token[0] ==  'in_tk':
        token = lex()
        return (expression(), 'CV') #end result of expression , can also have a nested call
    elif token[0] ==  'inout_tk':
        token = lex()
        if token[0] == 'id_tk':
            temp = token[1]
            token = lex()
            return (temp , 'REF')
        else:
            print('error , inout must have a parameter , at line %s' % line)
            exit(1)

def idtail(name):
    global token , line

    if token[0] ==  'lpar_tk':
        token = lex()
        parlist = actualparlist()
        if token[0] ==  'rpar_tk':
            token = lex()
            new_temp = newTemp()
            for par in parlist: #generate quads here instead of inside parlist 
                genQuad('par', par[0], par[1], '_')
            genQuad('par', new_temp, 'RET', '_')
            genQuad('call', '_', '_', name)
            return new_temp
        else:
            print('error , expected ) at line %s' % line)
            exit(1)
    return 'no_func_call'

def optionalSign():
    global token

    sign = ''
    if token[0] in addOperator.values():
        sign = token[1]
        token = lex()
    return sign

def statement():
    global token , line

    if token[0] == 'id_tk':
        name = token[1]
        token = lex()
        assignStat(name)
    elif token[0] == 'if_tk':
        token = lex()
        ifStat()
    elif token[0] == 'while_tk':
        token = lex()
        whileStat()
    elif token[0] == 'switchcase_tk':
        token = lex()
        switchcaseStat()
    elif token[0] == 'forcase_tk':
        token = lex()
        forcaseStat()
    elif token[0] == 'incase_tk':
        token = lex()
        incaseStat()
    elif token[0] == 'call_tk':
        token = lex()
        callStat()
    elif token[0] == 'return_tk':
        token = lex()
        returnStat()
    elif token[0] == 'input_tk':
        token = lex()
        inputStat()
    elif token[0] == 'print_tk':
        token = lex()
        printStat()

##########################main#################################

try:
    #file = open(sys.argv[1], 'r')
    file = open('cimple2.ci' , 'r')
except:
    print('file could not be opened')
    exit(1)
program()
file.close()
