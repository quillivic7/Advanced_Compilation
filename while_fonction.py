#!/usr/bin/env python

import tatsu
from tatsu import parse
from tatsu.ast import AST



### GRAMMAR


GRAMMAR = '''
    @@grammar::While
    
    start = program $ ;
    
    program = 
    | function program
    | var '=' nombre ';' program
    | 'main' '(' var_list ')' '{' command '}'
    ;

    function = var '(' var_list ')' '{' command '}' ;

    command =  
    | command command
    | var '=' expr ';'
    | 'if' '(' expr ')' '{' command '}'
    | 'while' '(' expr ')' '{' command '}'
    | function
    | 'return' '(' expr ')' ';'
    ;
    
    expr =
    | expr op expr
    | var '(' var_list ')'
    | var
    | nombre
    ;
    
    var = /[a-zA-Z][a-zA-Z0-9]*/ ;   
    nombre = /[0-9]+/ ;
    op = '+' | '-' | '*' | '>' ;

    var_list = ','<{ var }+ ;
'''



### USEFULL functions


op2asm = {'+' : 'add', '-' : 'sub', '*' : 'imul', '>' : 'test'} 



### SEMANTICS class


class Semantics:
    """
    Définit la Semantics pour le compilateur
    avec la GRAMMAR définie ci-dessus
    """
    def program(self, ast):
        if ast[0] == 'main':
            return {'type' : 'main_function', 'input' : ast[2], 'body' : ast[5]}
        elif ast[1] == '=':
            return {'type' : 'global_var', 'name' : ast[0], 'value' : ast[2], 'program' : ast[4]}
        else:
            return {'type' : 'function', 'function' : ast[0], 'program' : ast[1]}

    def function(self, ast):
        return {'type' : 'function', 'name' : ast[0], 'input' : ast[2], 'body' : ast[5]}

    def command(self, ast):
        if ast[0] == 'if':
            return {'type' : 'if', 'expr' : ast[2], 'body' : ast[5]}
        elif ast[0] == 'while':
            return {'type' : 'while', 'expr' : ast[2], 'body' : ast[5]}
        elif ast[0] == 'return':
            return {'type' : 'return', 'expr' : ast[2]}
        elif ast[1] == '=':
            return {'type' : 'affect', 'lhs' : ast[0], 'rhs' : ast[2]}                
        elif len(ast) > 6 and ast[1] == '(' and ast[3] == ')' and ast[4] == '{' and ast[6] == '}':
            return{'type' : 'local_function', 'function' : ast}
        else:
            return {'type' : 'seq', 'first' : ast[0], 'second' : ast[1]}

    def expr(self, ast) :
        if isinstance(ast, list):
            if ast[1] in op2asm:
                return {'type' : 'opbin', 'op' : ast[1], 'gauche' : ast[0], 'droit' : ast[2]}
            elif ast[1] == '(':
                return {'type' : 'call_function', 'function' : ast[0], 'input' : ast[2]}
        else: 
            return ast

    def var(self, ast):
        return {'type' : 'variable', 'id' : ast}

    def nombre(self, ast):
        return {'type' : 'constant', 'val' : int(ast)}
 
    def var_list(self, ast):
        def decompose(ast):
            if isinstance(ast, tuple):
                return decompose(ast[1]) + [ast[2]]
            else:
                return [ast]
        return {'type' : 'var_list', 'list' : decompose(ast)}





### PRETTIER PRINT functions


def pprint_expr(expr_ast, tab = 0):
    if expr_ast['type'] == 'opbin':
        return  "%s %s %s" % (pprint_expr(expr_ast['gauche']), 
        expr_ast['op'], pprint_expr(expr_ast['droit']))
    elif expr_ast['type'] == 'constant':
        return str(expr_ast['val'])
    else:
        return expr_ast['id']

def pprint_com(com_ast, tab = 0):
    if com_ast['type'] == 'affect':
        return "%s%s = %s;" % (tab*'\t', com_ast['lhs']['id'], 
        pprint_expr(com_ast['rhs']))
    elif com_ast['type'] == 'while':
        return "%swhile(%s) {\n%s\n%s}" % (tab*'\t', pprint_expr(com_ast['expr']), 
        pprint_com(com_ast['body'], tab+1), tab*'\t')
    elif com_ast['type'] == 'if':
        return "%sif(%s) {\n%s\n%s}" % (tab*'\t', pprint_expr(com_ast['expr']), 
        pprint_com(com_ast['body'], tab+1), tab*'\t')
    else:
        return "%s\n%s" % (pprint_com(com_ast['first'], tab), 
        pprint_com(com_ast['second'], tab))

def pprint_prg(prg_ast, tab = 0):
    variables = ", ".join([x['id'] for x in prg_ast['input']['list']])
    body = pprint_com(prg_ast['body'], tab+1)
    ret = pprint_expr(prg_ast['return_expr'], 0) 
    return ("%smain(%s) {\n%s\n%sreturn (%s);\n%s}" % (tab*'\t', variables, body, (tab+1)*'\t', ret, tab*'\t'))



### COMPILE functions

##### VAR_LIST functions

def var_list(prg_ast):
    """
    Enumère les variables
    définies dans le code assembleur 
    dans la section .data
    ex: 
        x: dq 0
        y: dq 0
        argv: dq 0
        argc: dd 0
    """
    vars_set = var_list_prg(prg_ast)
    res = ""
    for v in vars_set:
        if v == "returnExpr":
            res += "%s: db \"%%d\", 10, 0\n" % v
        elif v == "argc":
            res += "%s: dd 0\n" % v
        elif v == "argv":
            res += "%s: dq 0\n" % v
        else:
            res += "%s: dq 0\n" % v
    return res

def var_list_prg(prg_ast):
    """
    Récupère le nom des différentes 
    variables du programme
    en les stockant dans un ensemble
    """
    if prg_ast['type'] == 'global_var':
        return var_list_expr(prg_ast['global_var']) | var_list_prg(prg_ast['program'])
    elif prg_ast['type'] == 'function':
        return var_list_fun(prg_ast['function']) | var_list_prg(prg_ast['program'])
    else:
        return {"returnExpr", "argc", "argv"} | var_list_fun(prg_ast)

def var_list_fun(fun_ast):
    """ 
    Traite les variables
    au sein des fonctions
    """
    vars = [x['id'] for x in fun_ast['input']['list']]
    vars += var_list_com(fun_ast['body'])
    #vars += var_list_expr(prg_ast['return_expr'])
    vars_set = set(vars)
    return vars_set

def var_list_com(com_ast):
    """ 
    Traite les variables
    au sein des commandes
    """
    if com_ast['type'] == 'affect':
        return [com_ast['lhs']['id']] + var_list_expr(com_ast['rhs'])
    elif com_ast['type'] in ['while','if'] :
        return var_list_expr(com_ast['expr']) + var_list_com(com_ast['body'])
    elif com_ast['type'] =='return':
        return var_list_expr(com_ast['expr'])
    elif com_ast['type'] == 'local_function':
        return var_list_fun(com_ast)
    else:
        return var_list_com(com_ast['first']) + var_list_com(com_ast['second'])

def var_list_expr(expr_ast):
    """ 
    Traite les variables
    au sein des expressions
    """
    if expr_ast['type'] == 'opbin':
        return var_list_expr(expr_ast['gauche']) + var_list_expr(expr_ast['droit']) 
    elif expr_ast['type'] == 'constant':
        return []
    elif expr_ast['type'] == 'call_function':
        return []
    else:
        return [expr_ast['id']]

##### FUNCTIONS functions

def functions(prg_ast):
    """
    Enumère les fonctions
    définies dans le code assembleur 
    dans la section .data
    ex: 
        global main
    """
    funcs_set = functions_prg(prg_ast)
    return "\n".join(["global %s" % f for f in funcs_set]) + "\n"

def functions_prg(prg_ast):
    """
    Récupère le nom des différentes
    fonctions du programme
    en les stockant dans un ensemble
    """
    if prg_ast['type'] == 'global_var':
        return functions_prg(prg_ast['program'])
    elif prg_ast['type'] == 'function':
        return {prg_ast['function']['name']['id']} | functions_prg(prg_ast['program'])
    else:
        return {"main"}

##### PROGRAM functions 

def init_var(prg_ast):
    """
    Initialise les variables
    concernées dans ce programme
    et les stocke dans la mémoire
    """
    def decompose(prg_ast):
        """
        Récupère les variables
        concernées dans ce programme
        """
        if prg_ast['type'] == 'function':
            return [x['id'] for x in prg_ast['function']['input']['list']] + decompose(prg_ast['programme'])
        elif prg_ast['type'] == 'global_var':
            return prg_ast['name']['id'] + decompose(prg_ast['program'])
        else:
            return [x['id'] for x in prg_ast['input']['list']]
    vars = decompose(prg_ast)
    ivar = ""
    for i in range(len(vars)):
        ivar += """; main variables init
mov rax, [argv]
mov rdi, [rax+%s]
call atoi
mov [%s], rax
""" % (8*(i+1), vars[i])
    return ivar 

def init_var_fun(fun_ast):
    """
    Initialise les variables
    concernées dans cette fonction
    et les stocke dans la mémoire
    """
    vars = [x['id'] for x in fun_ast['input']['list']]
    ivar = ""
    for i in range(len(vars)):
        ivar += """; initialisation variables fonction
mov rax, [argv]
mov rdi, [rax+%s]
call atoi
mov [%s], rax
""" % (8*(i+1), vars[i]) #TODO
    return ivar  


def compile_expr(expr_ast):
    """
    Génère le code assembleur
    correspondant à l'expression
    """
    if expr_ast['type'] == 'constant':
        return """; constant
mov rax, %s
""" % expr_ast['val']
    elif expr_ast['type'] == 'variable':
        return """; variable
mov rax, [%s]
""" % expr_ast['id']
    elif expr_ast['type'] == 'call_function':
        nb_params = len(expr_ast['input']['list'])
        params = "push " + "\npush ".join([x['id'] for x in expr_ast['input']['list']])
        return """; function call 
call %s
""" % (expr_ast['function']['id']) #TODO
    else:
        e1 = compile_expr(expr_ast['gauche'])
        e2 = compile_expr(expr_ast['droit'])
        return """; binary opcode
%s
push rax
%s
pop rbx
%s rax, rbx
""" % (e2, e1, op2asm[expr_ast['op']])

cpt = 0
def compile_com(com_ast):
    """
    Génère le code assembleur
    correspondant à la commande
    """
    global cpt
    if com_ast['type'] == 'affect':
        return """; affect
%s
mov [%s], rax
""" % (compile_expr(com_ast['rhs']), com_ast['lhs']['id'])
    if com_ast['type'] == 'if':
        cpt += 1
        return """; if
%s
cmp rax, 0
jz fin_%s
%s
fin_%s: nop
""" % (compile_expr(com_ast['expr']), cpt, compile_com(com_ast['body']), cpt)
    elif com_ast['type'] == 'while':
        cpt += 1
        return """; while
debut_%s:
%s
cmp rax, 0
jz fin_%s
%s
jmp debut_%s
fin_%s: nop
""" % (cpt, compile_expr(com_ast['expr']), cpt, compile_com(com_ast['body']), cpt, cpt)
    elif com_ast['type'] == 'return':
        return """; return
%s
mov eax, [%s]
""" % (compile_expr(com_ast['expr']), com_ast['expr']['id'])
    elif com_ast['type'] == 'local_function':
        return None #TODO
    else:
        return compile_com(com_ast['first']) + compile_com(com_ast['second'])

def compile_fun(fun_ast):
    """
    Génère le code assembleur
    correspondant à la fonction
    """
    return """; function
%s:
push rbp
mov rbp, rsp
%s
%s
;nop
pop rbp
ret
""" % (fun_ast['name']['id'], init_var_fun(fun_ast), compile_com(fun_ast['body'])) #TODO
  
    
def compile_prg(prg_ast):
    """
    Génère le code assembleur
    correspondant au programme
    """
    if prg_ast['type'] == 'function':
        return compile_fun(prg_ast['function']) + compile_prg(prg_ast['program'])
    elif prg_ast['type'] == 'global_var':
        return compile_expr(prg_ast) + compile_prg(prg_ast['program'])
    else:
        code_main = """; main function
main:
push rbp
mov rbp, rsp
mov [argc], edi
mov [argv], rsi
_INIT_VAR
_BODY
mov rdi, returnExpr
mov rsi, rax
call printf
pop rbp
ret
"""
        code_main = code_main.replace("_INIT_VAR", init_var(prg_ast))
        code_main = code_main.replace("_BODY", compile_com(prg_ast['body']))
        return code_main #TODO
        

    

def compile(ast):
    """
    Génère le code assembleur général
    """
    code_asm =  """; PROGRAM
extern printf, atoi

section .data
; VAR_LIST
_VAR_LIST
; FUNCTIONS
_FUNCTIONS
section .text
; PROGRAM BODY
_PROGRAM
"""
    code_asm = code_asm.replace("_VAR_LIST", var_list(ast))
    code_asm = code_asm.replace("_FUNCTIONS", functions(ast))
    code_asm = code_asm.replace("_PROGRAM", compile_prg(ast))
    return code_asm


example0 = """
main(X, Y) {
    while(X) {
        X = X - 1;
        Y = Y + 1;
        Z = 1;
    }
    return(Y); 
}
"""

example0bis = """
main(x) {
    i = 10;
    while(i) {
        x = x+1;
        i = i-1;
    }
    return(x);
}
"""

example1 = """
main(x) {
    return(x);
}
"""

example2 = """
add (x, y) {
    a = x + y;
    return(a);
}

main (x, y) {
    z = add(x, y);
    return(z);
}
"""

example3 = """
add(x, y) {
    a = x+y;
    return(a);
}

tripleadd(x, y, z) {
    a = add(x, y);
    b = add(a, z);
    return(b); 
}

main(x, y, z) {
    z = tripleadd(x, y, z);
    return(z);
}
"""

example4 = """
main(x) {
    add1(x) {
        x = x+1;
        return(x);
    }
    z = add1(x);
    return(z);
}
"""

example = example2
#try:
ast = parse(GRAMMAR, example, semantics=Semantics())
print("example = " + example)
print("ast = " + str(ast))
print()
#print(pprint_prg(ast))
code_asm = compile(ast)
print(code_asm)
myfile = open("code.asm", 'w')
myfile.write(code_asm)
#except Exception as e:
#    print(e)


