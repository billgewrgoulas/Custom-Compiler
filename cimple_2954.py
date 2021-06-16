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

numOp = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div'}

relOper = {
            '<': 'lt_tk', '>': 'gt_tk', '=': 'eq_tk',
            '<=': 'leq_tk', '>=': 'geq_tk', '<>': 'neq_tk'
          }

branch =  {
            '<': 'blt', '>': 'bgt', '=': 'beq',
            '<=': 'ble', '>=': 'bge', '<>': 'bne'
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

sub = False
line = 1
char = ''
token = ''
file = ''
st = ''
temp = 0
quadNo = -1
varList = []   #vars in use
quadList = []  #each element will be in the form of [ quadNo , op , x , y , z ]
symTable = []
final = []
retCheck = ()
nestingLevel = 0
index = 0
label = 0

class Token:
    def __init__(self, tokenType, tokenString, lineNo):
        self.tokenType = tokenType       #category , can be identifier,number , keyword , addOperator...
        self.tokenString = tokenString   #actual symbol
        self.lineNo = lineNo             #current line

#############################symbol table entities################################

class VarEntity:
    def __init__(self, name, type, offset):
        self.name = name
        self.type = type
        self.offset = offset

class SubpEntity:
    def __init__(self, name, type, sQuad, fLength):
        self.name = name
        self.type = type
        self.args = []
        self.sQuad = sQuad
        self.fLength = fLength

class TempEntity:
    def __init__(self, name, offset):
        self.name = name
        self.offset = offset
        self.type = 'temp'

class ParEntity:
    def __init__(self, name, offset, parMode):
        self.name = name
        self.offset = offset
        self.parMode = parMode
        self.type = 'par'

class Scope:
    def __init__(self, nestingLevel, name):
        self.entities = []
        self.nestingLevel = nestingLevel
        self.name = name
        self.totalOffset = 12

#############################final code generators##########################################

def commentsFin():
    global final, label, quadList, index

    final.append('L' + str(label) + ':       #' + str(quadList[index]) + '#\n')
    label += 1

def gnvlcode(e):
    global final, symTable

    final.append('  lw $t0,-4($sp)\n')
    eLevel = symTable[-1].nestingLevel
    dif = eLevel- e[1] 

    for i in range(0, dif - 1):
        final.append('  lw $t0,-4($t0)\n')
    final.append('  addi $t0,$t0,-' + str(e[0].offset) + '\n')

def loadvr(v, r):
    global final, symTable

    e = search(v, ['temp', 'par', 'var', 'global'])
    if v.isdigit():
        final.append('  li ' + str(r) + ', ' + str(v) + '\n')
    elif e[0].type == 'global':
        final.append('  lw ' + str(r) + ', -' + str(e[0].offset) + '($s0)\n')
    elif e[0].type == 'temp' or e[0].type == 'var' and e[1] == symTable[-1].nestingLevel:
        final.append('  lw ' + str(r) + ', -' + str(e[0].offset) + '($sp)\n')
    elif e[0].type == 'par' and e[1] == symTable[-1].nestingLevel:
        if e[0].parMode == 'cv':
            final.append('  lw ' + str(r) + ', -' + str(e[0].offset) + '($sp)\n')
        else:
            final.append('  lw $t0, -' + str(e[0].offset) + '($sp)\n')
            final.append('  lw ' + str(r) + ', ($t0)\n')
    elif symTable[-1].nestingLevel > e[1]:
        if e[0].type == 'par':
            if e[0].parMode == 'cv':
                gnvlcode(e)
                final.append('  lw ' + str(r) + ', ($t0)\n')
            else:
                gnvlcode(e)
                final.append('  lw $t0, ($t0)\n')
                final.append('  lw ' + str(r) + ', ($t0)\n')
        elif e[0].type == 'var':
            gnvlcode(e)
            final.append('  lw ' + str(r) + ', ($t0)\n')

def storerv(r, v):
    global final, symTable

    e = search(v, ['temp', 'par', 'var', 'global'])
    if e[0].type == 'global':
        final.append('  sw ' + str(r) + ', -' + str(e[0].offset) + '($s0)\n')
    elif e[0].type == 'temp' or e[0].type == 'var' and e[1] == symTable[-1].nestingLevel:
        final.append('  sw ' + str(r) + ', -' + str(e[0].offset) + '($sp)\n')
    elif e[0].type == 'par' and e[1] == symTable[-1].nestingLevel:
        if e[0].parMode == 'cv':
            final.append('  sw ' + str(r) + ', -' + str(e[0].offset) + '($sp)\n')
        else:
            final.append('  lw $t0, -' + str(e[0].offset) + '($sp)\n')
            final.append('  sw ' + str(r) + ', ($t0)\n')
    elif symTable[-1].nestingLevel > e[1]:
        if e[0].type == 'par':
            if e[0].parMode == 'cv':
                gnvlcode(e)
                final.append('  sw ' + str(r) + ', ($t0)\n')
            else:
                gnvlcode(e)
                final.append('  lw $t0, ($t0)\n')
                final.append('  sw ' + str(r) + ', ($t0)\n')
        elif e[0].type == 'var':
            gnvlcode(e)
            final.append('  sw ' + str(r) + ', ($t0)\n')

def jump(l):
    global final

    commentsFin()
    final.append('  b L' + str(l) + '\n')
    
def relop(op, x, y, z):
    global final

    commentsFin()
    loadvr(x, '$t1')
    loadvr(y, '$t2')
    final.append( '  ' +branch[op] + ', $t1, $t2, L' + str(z) + '\n')

def assignV(x, z):
    global final

    commentsFin()
    loadvr(x, '$t1')
    storerv('$t1', z)

def numExp(op, x, y, z):
    global final

    commentsFin()
    loadvr(x, '$t1')
    loadvr(y, '$t2')
    final.append('  ' + numOp[op] + ' $t1, $t1, $t2\n')
    storerv('$t1', z)

def outP(x):
    global final

    commentsFin()
    final.append('  li $v0, 1\n')
    loadvr(x, '$a0')
    final.append('  syscall\n')

def inP(x):
    global final

    commentsFin()
    final.append('  li $v0, 5\n')
    final.append('  syscall\n')
    storerv('  $v0', x)

def retv(x):
    global final

    commentsFin()
    loadvr(x, '$t1')
    final.append('  lw $t0, -8($sp)\n')
    final.append('  sw $t1, ($t0)\n')
    final.append('  lw $ra, ($sp)\n') #ignore everything after return
    final.append('  jr $ra\n')

def subPars():
    global quadList, final, index

    e = symTable[-1]
    ins = len(final)
    q = quadList[index]
    pars = []
    i = 0
    while q[1] == 'par' and not q[3] == 'RET':
        pars.append(q[3])
        commentsFin()
        if q[3] == 'cv':
            loadvr(q[2], '$t0')
            final.append('  sw $t0, -' + str(12 + 4 * i) + '($fp)\n')
        elif q[3] == 'ref':
            entity = search(q[2], ['temp', 'par', 'var', 'global'])
            if entity[1] == e.nestingLevel:
                if entity[0].type == 'par':
                    if entity[0].parMode == 'cv':
                        final.append('  addi $t0, $sp, -' + str(entity[0].offset) + '\n')
                        final.append('  sw $t0, -' + str(12 + 4 * i) + '($fp)\n')
                    elif entity[0].parMode == 'ref':
                        final.append('  lw $t0, -' + str(entity[0].offset) + '($sp\n') #get the reference
                        final.append('  sw $t0, -' + str(12 + 4 * i) + '($fp)\n')
                else:
                    final.append('  addi $t0, $sp, -' + str(entity[0].offset) + '\n')
                    final.append('  sw $t0, -' + str(12 + 4 * i) + '($fp)\n')
            else:
                if entity[0].type == 'par':
                    if entity[0].parMode == 'cv':
                        gnvlcode(entity)
                        final.append('  sw $t0, -' + str(12 + 4 * i) + '($fp)\n')
                    elif entity[0].parMode == 'ref':
                        gnvlcode(entity)
                        final.append('  lw $t0, ($t0)\n')
                        final.append('  sw $t0, -' + str(12 + 4 * i) + '($fp)\n')
                else:
                    gnvlcode(entity)
                    final.append('  sw $t0, -' + str(12 + 4 * i) + '($fp)\n')
        i += 1
        index += 1
        q = quadList[index]
    type = 'procedure'
    if q[3] == 'RET':
        type = 'function'
        entity = search(q[2], ['temp', 'par', 'var', 'global'])
        commentsFin()
        final.append('  addi $t0, $sp, -' + str(entity[0].offset) + '\n')
        final.append('  sw $t0, -8($fp)\n')
        index += 1
        q = quadList[index]

    if q[1] == 'call':
        callSub(pars, q[4], ins, type)
   
def callSub(pars, name, ins, type):
    global final, symTable

    e = search(name, [type])
    checkArgs(e[0], pars)

    final.insert(ins + 1, '  addi $fp, $sp, ' + str(e[0].fLength) + '\n')
    commentsFin()
    lvl = symTable[-1].nestingLevel

    if e[1] + 1 == lvl:
        final.append('  lw $t0, -4($sp)\n')
        final.append('  sw $t0, -4($fp)\n')
    else:
        final.append('  sw $sp, -4($fp)\n')

    final.append('  addi $sp, $sp, ' + str(e[0].fLength) + '\n')
    final.append('  jal L' + str(e[0].sQuad) + '\n')
    final.append('  addi $sp, $sp, -' + str(e[0].fLength) + '\n')

def callSubNoPars(name): #we could use callSub but whatever..
    global final, symTable

    e = search(name, ['procedure'])
    lvl = symTable[-1].nestingLevel

    commentsFin()
    final.append('  addi $fp, $sp, ' + str(e[0].fLength) + '\n')

    if e[1] + 1 == lvl:                 #obviously the level will be + 1 since we get this from its parent
        final.append('  lw $t0, -4($sp)\n')
        final.append('  sw $t0, -4($fp)\n')
    else:
        final.append('  sw $sp, -4($fp)\n')

    final.append('  addi $sp, $sp, ' + str(e[0].fLength) + '\n')
    final.append('  jal L' + str(e[0].sQuad) + '\n')
    final.append('  addi $sp, $sp, -' + str(e[0].fLength) + '\n')

def main():
    global final, symTable

    f = symTable[-1].totalOffset
    final.append('Lmain:     #MAIN# \n')
    final.append('  addi $sp, $sp, ' + str(f) + '\n')
    final.append('  move $s0, $sp\n')

def quadsToFinal():
    global guadlist, index, final

    quad = quadList[index]
    while (quad[1] != 'end_block'):
        if quad[1] in numOp.keys():
            numExp(quad[1], quad[2], quad[3], quad[4])
        elif quad[1] in assign.keys():
            assignV(quad[2], quad[4])
        elif quad[1] in relOper.keys():
            relop(quad[1], quad[2], quad[3], quad[4])
        elif quad[1] == 'retv':
            retv(quad[2])
        elif quad[1] == 'par':
            subPars()
        elif quad[1] == 'jump':
            jump(quad[4])
        elif quad[1] == 'inp':
            inP(quad[2])
        elif quad[1] == 'out':
            outP(quad[2])
        elif quad[1] == 'call':
            callSubNoPars(quad[4])
        index += 1
        quad = quadList[index]
    index += 1

def genInstructions():
    global final, nestingLevel, label, quadList, index

    if nestingLevel - 1 == 0:
        main()
        quadsToFinal()
    else:
        commentsFin()
        final.append('  sw $ra, ($sp)\n')
        quadsToFinal()
        final.append('L' + str(label) + ':      #' + str(quadList[index-1]) + '#\n')
        label += 1
        final.append('  lw $ra, ($sp)\n')
        final.append('  jr $ra\n')

###################################symbol Table helpers#############################

def newArg(par):
    global nestingLevel, symTable

    if par:
        l = symTable[nestingLevel-2].entities[-1].args
        l.append(par[0])

def newScope(name):
    global nestingLevel, symTable

    symTable.append(Scope(nestingLevel, name))
    nestingLevel += 1

def delScope():
    global nestingLevel, symTable

    printScope()
    scope = symTable[-1]
    if nestingLevel > 1:
        for e in symTable[-2].entities[::-1]:
            if e.name == scope.name:
                e.fLength = scope.totalOffset
    genInstructions()
    symTable.pop()
    nestingLevel -= 1

def search(name, spec):
    global symTable

    for scope in symTable[::-1]:
        for entity in scope.entities:
            if entity.name == name and entity.type in spec:
                return (entity, scope.nestingLevel)
    return 'err'

def searchByName(name):
    global symTable

    for scope in symTable[::-1]:
        for entity in scope.entities:
            if entity.name == name:
                return (entity, scope.nestingLevel)
    return 'err'

def checkArgs(e, pars):
    
    if e.args != pars:
        print('error, parameter missmatch when calling subp: %s' % (e.name))
        exit(1)

def isProc(name):
    global line

    e = search(name, ['procedure'])
    if e == 'err':
        print('error, procedure out of scope at line: %s', line)
        exit(1)

def isFunc(name):
    global line

    e = search(name, ['function'])
    if e == 'err':
        print('error, function out of scope at line: ', line)
        exit(1)

def validatePars(lst):
    global line, symTable

    for par in lst:
        if search(par, ['temp', 'par', 'var', 'global']) == 'err' and not par.isdigit():
            print('error, undefined variable %s at line: %s' % (par, line))
            exit(1)

def hasReturn(block):
    global retCheck

    if block[2] == 'function' and not retCheck[0]:
        print('error, function %s must have a return statement at line: %s' % (block[0], retCheck[1]))
        exit(1)
    if retCheck[0] and not block[2] == 'function':
        print('error, only functions can have a return statement , at line: %s' % (retCheck[1]))
        exit(1)

def newEntity(entity):
    global symTable, line

    subp = ['function', 'procedure']
    vars = ['var', 'par', 'temp', 'global']
    for e in symTable[-1].entities:
        if e.name == entity.name:
            if e.type in vars and entity.type in vars:
                print('error, duplicate parameter declaration: %s at line: %s' % (e.name, line))
                exit(1)
            elif e.type in subp and entity.type in subp:
                print('error, two subprograms cant have the same name in the same scope, at line: %s' % (line))
                exit(1)
            else :
                print('error, a subprogram and a variable can not have the same name , at line: %s' % (line))
                exit(1)
    symTable[-1].entities.append(entity)

def patchStart(quadNo):
    global symTable

    if len(symTable) < 2: return
    symTable[-2].entities[-1].sQuad = quadNo

def printScope():  #print current sym table
    global symTable, st

    for e in symTable[-1].entities:
        st.write(str(vars(e)) + '\n')
    st.write('scope name: %s\n' % symTable[-1].name )
    st.write('scope fLength: %s\n' % symTable[-1].totalOffset )
    st.write('scope level: %s\n' % symTable[-1].nestingLevel )
    st.write('=================================================================================\n\n')
    
###################################intermediate code helpers####################################

def nextQuad():
    global quadNo
    return (quadNo + 1)
    
def genQuad(op, x, y, z):
    global quadList, quadNo
    quadNo += 1
    quadList.append([quadNo, str(op), str(x), str(y), str(z)])
    
def newTemp():
    global tempvarList, temp, symTable
    tempvar = 'T_' + str(temp)
    temp += 1
    symTable[-1].entities.append(TempEntity(tempvar, symTable[-1].totalOffset))
    symTable[-1].totalOffset += 4
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

##################################generate .c, .int, .asm files################################

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
    global quadList, varList, sub

    if sub: return

    instructions = []
    instructions.append('int main()\n{')

    text = '  int '
    for var in varList[1:]:
        text += str(var) + ','
    instructions.append(text[:-1] + ';\n')

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
            instruction += 'scanf("%d", &' + str(quad[2]) + ')' + ';\n'
        elif quad[1] == 'out':
            instruction += 'printf("%d", ' + str(quad[2]) + ')' + ';\n'
        else:
            instruction += '{};\n'
        instructions.append(instruction)
    instructions.append('}')

    try:
        outFile = open('out.c', 'w')
        for i in instructions:
            outFile.write(i)
        outFile.close()
    except:
        print('file could not be created')
        exit(1)

def genAsm():
    global final

    try:
        outFile = open('out.asm', 'w')
        for f in final:
            outFile.write(f)
        outFile.close()
    except:
        print('file could not be created')
        exit(1)

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
    global char , line, groupSymbol
 
    if char == '=':
        getNext()
        return Token('eq_tk', '=', line)
    
    temp = char
    #sneak peek
    getNext()
    if char.isalnum() or char.isspace() or char in addOperator.keys() or char in groupSymbol.keys():
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
    while tempToken.tokenType == 'comment_tk':
        tempToken = tokenResolver()
    if tempToken.tokenType == 'id_tk' and not tempToken.tokenString in varList:
        varList.append(tempToken.tokenString)
    return [ str(tempToken.tokenType) , str(tempToken.tokenString) ]
    
###########################syntax analysis############################

def program():
    global token , quadList, symTable, final
    getNext()
    token = lex()  #initialize token for the first time
    
    final.append('Lbegin: \n')
    final.append('  j Lmain\n')
    
    if token[0] ==  'program_tk':
        token = lex()
        if token[0] ==  'id_tk':
            programName = token[1]
            newScope(programName)
            token = lex()
            block((programName , True, 'main' ))
            if token[0] == 'end_tk':
                genInt()
                genC()
                genAsm()
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

def block(block):
    global retCheck, line

    declarations(block[1])
    subprograms()
    patchStart(nextQuad())
    genQuad('begin_block', block[0], '_', '_')
    retCheck = (False, line)
    statements()
    hasReturn(block)
    if block[1]:
        genQuad('halt' , '_' , '_' , '_')
    genQuad('end_block', block[0], '_', '_')
    delScope()

def declarations(b):
    global token , line

    while token[0] == 'declare_tk':
        token = lex()
        varlist(b)
        if token[0] == 'semcol_tk':
            token = lex()
        else:
            print('error , ; was expected at line %s' % line)
            
def varlist(b): #declarations
    global token, line, symTable
    
    type = 'var'
    if b:
        type = 'global'

    if token[0] == 'id_tk':
        newEntity(VarEntity(token[1], type, symTable[-1].totalOffset))
        symTable[-1].totalOffset += 4
        token = lex()
        while token[0] == 'comma_tk':
            token = lex()
            if token[0] == 'id_tk':
                newEntity(VarEntity(token[1], type, symTable[-1].totalOffset))
                symTable[-1].totalOffset += 4
                token = lex()
            else:
                print('parameter declaration was expected at line: %s' % line)
                exit(1)

def subprograms():
    global token, line, symTable, final, sub

    while token[0] == 'function_tk' or token[0] == 'procedure_tk':
        
        sub = True
        type = token[1]
        token = lex()
        if token[0] == 'id_tk':
            name = token[1]
            newEntity(SubpEntity(name, type, '', 12))
            newScope(name)
            token = lex()
            if token[0] == 'lpar_tk':
                token = lex()
                formalparlist()
                if token[0] == 'rpar_tk':
                    token = lex()
                    block((name, False, type))
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
    global token,symTable

    par = formalparitem()
    if par:
        newEntity(ParEntity(par[1], symTable[-1].totalOffset, par[0]))
        symTable[-1].totalOffset += 4
    while token[0] == 'comma_tk':
        token = lex()
        par = formalparitem()
        if par:
            newEntity(ParEntity(par[1], symTable[-1].totalOffset, par[0]))
            symTable[-1].totalOffset += 4

def formalparitem():
    global token , line

    fPar = ()
    if token[0] == 'in_tk':
        token = lex()
        if token[0] == 'id_tk':
            fPar = ('cv', token[1])
            token = lex()
        else:
            print('error , expected: identifier at line: %s' % line)
            exit(1)
    elif token[0] == 'inout_tk':
        token = lex()
        if token[0] == 'id_tk':
            fPar = ('ref', token[1])
            token = lex()
        else:
            print('error , expected: identifier at line: %s' % line)
            exit(1)
    newArg(fPar)
    return fPar

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
        else:                     #must fix this
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
        token = lex()  #result of the expression , will be either an id or a tempValue
        validatePars([name])
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
                genQuad(':=' , '1' , '_' , temp[0])  #update temp in run time
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
        isProc(name)
        token = lex()
        if token[0] ==  'lpar_tk':
            token = lex()
            parlist = actualparlist()
            if token[0] ==  'rpar_tk':
                token = lex()
                for par in parlist:  #generate quads here instead of inside parlist
                    genQuad('par', par[0], par[1], '_')
                genQuad('call', '_', '_', name)
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
                validatePars([in_id])
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
        backpatch(Bfalse, nextQuad())     #we do the opposite of and ,       
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
        (Btrue , Bfalse) = condition()     #nothing interesting here :(     
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
            return func  # we have a func call so we need  T_i , which holds the return result
        validatePars([temp])
        return temp       #simple identifier
    else:
        print('error at line %s , expected identifier or a number' % (line))
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
    
    if parlist[0] is None:
        parlist = []
    validatePars([ p[0] for p in parlist ])
    return parlist

def actualparitem():
    global token , line

    if token[0] ==  'in_tk':
        token = lex()
        return (expression(), 'cv') #end result of expression , can also have a nested call
    elif token[0] ==  'inout_tk':
        token = lex()
        if token[0] == 'id_tk':
            temp = token[1]
            token = lex()
            return (temp , 'ref')
        else:
            print('error , inout must have a parameter , at line %s' % line)
            exit(1)

def idtail(name):
    global token, line

    if token[0] ==  'lpar_tk':
        token = lex()
        parlist = actualparlist()
        if token[0] ==  'rpar_tk':
            token = lex()
            new_temp = newTemp()
            for par in parlist:  #generate quads here instead of inside parlist
                genQuad('par', par[0], par[1], '_')
            genQuad('par', new_temp, 'RET', '_')
            genQuad('call', '_', '_', name)
            isFunc(name)
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
    global token , line, retCheck

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
        retCheck = (True, line)
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
    file = open('cimple3.ci' , 'r')
    st = open('symtable.txt' , 'w')
except:
    print('file could not be opened')
    exit(1)
program()
file.close()
st.close()
