import tatsu
from tatsu import parse
from tatsu.ast import AST

GRAMMAR = '''
   @@grammar::While
   
   start = program $
   ;
   
   program = 'main' '(' var_list ')' '{' command 'return' '(' expr ')' ';' '}' ;

   command =  
   | command command
   | 'if' '(' expr ')' '{' command '}'
   | 'while' '(' expr ')' '{' command '}'
   | var '=' expr ';' ;
   
   expr =
   | expr op expr
   | var
   | nombre ;
   
   var = /[a-zA-Z][a-zA-Z0-9]*/ ;   
   nombre = /[0-9]+/ ;
   op = '+' | '-' | '*' | '>' ;

   var_list = ','<{ var }+ ;
'''

op2asm = {'+' : 'add', '-' : 'sub', '*' : 'imul', '>' : 'test'} 

class Semantics:
    def nombre(self, ast):
        return {'type' : 'constant', 'val' : int(ast)}
    def var(self, ast):
        return {'type' : 'variable', 'id' : ast}
    def expr(self, ast) :
        if isinstance(ast, list):
            return {'type' : 'opbin', 'op' : ast[1],
            'gauche' : ast[0], 'droit' : ast[2]}
        else:
            return ast
    def command(self, ast):
        if ast[0] == 'if':
            return {'type' : 'if', 'expr' : ast[2], 'body' : ast[5]}
        elif ast[0] == 'while':
            return {'type' : 'while', 'expr' : ast[2], 'body' : ast[5]}
        elif ast[1] == '=':
            return {'type' : 'aff', 'lhs' : ast[0], 'rhs' : ast[2]}
        else:
            return {'type' : 'seq', 'first' : ast[0], 'second' : ast[1]}
        
    def var_list(self, ast):
        def decompose(ast):
            if isinstance(ast, tuple):
                return decompose(ast[1]) + [ast[2]]
            else:
                return [ast]
        return {'type' : 'var_list', 'list' : decompose(ast)}
        
    def program(self, ast):
        return {'type' : 'program', 'input' : ast[2],
                'body' : ast[5], 'return_expr' : ast[8]}

def pprint_expr(expr_ast, tab = 0):
    if expr_ast['type'] == 'opbin':
        return  "%s %s %s" % (pprint_expr(expr_ast['gauche']), 
        expr_ast['op'], pprint_expr(expr_ast['droit']))
    elif expr_ast['type'] == 'constant':
        return str(expr_ast['val'])
    else:
        return expr_ast['id']
    
def var_list_expr(expr_ast):
    if expr_ast['type'] == 'opbin':
        return var_list_expr(expr_ast['gauche']) + var_list_expr(expr_ast['droit']) 
    elif expr_ast['type'] == 'constant':
        return []
    else:
        return [expr_ast['id']]


def compile_expr(expr_ast):
    if expr_ast['type'] == 'constant':
        return """mov rax, %s
        """ % expr_ast['val']
    elif expr_ast['type'] == 'variable':
        return """mov rax, [%s]
        """ % expr_ast['id']
    else:
        e1 = compile_expr(expr_ast['gauche'])
        e2 = compile_expr(expr_ast['droit'])
        return """%s
        push rax
        %s
        pop rbx
        %s rax, rbx
        """ % (e2, e1, op2asm[expr_ast['op']])
        
    

def pprint_com(com_ast, tab = 0):
    if com_ast['type'] == 'aff':
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
    
    
def var_list_com(com_ast):
    if com_ast['type'] == 'aff':
        return [com_ast['lhs']['id']] + var_list_expr(com_ast['rhs'])
    elif com_ast['type'] in ['while','if'] :
        return var_list_expr(com_ast['expr']) + var_list_com(com_ast['body'])
    else:
        return var_list_com(com_ast['first']) + var_list_com(com_ast['second'])  

cpt = 0
def compile_com(com_ast):
    global cpt
    if com_ast['type'] == 'aff':
        return """%s
        mov[%s], rax
        """ % (compile_expr(com_ast['rhs']), com_ast['lhs']['id'])
    if com_ast['type'] == 'if':
        cpt += 1
        return """%s
        cmp rax, 0
        jz fin_%s
        %s
        fin_%s: nop
        """ % (compile_expr(com_ast['expr']), cpt, compile_com(com_ast['body']), cpt)
    elif com_ast['type'] == 'while':
        cpt += 1
        return """debut_%s:
        %s
        cmp rax, 0
        jz fin_%s
        %s
        jmp debut_%s
        fin_%s: nop
        """ % (cpt, compile_expr(com_ast['expr']), cpt, compile_com(com_ast['body']), cpt, cpt)
    else:
        return compile_com(com_ast['first']) + compile_com(com_ast['second'])
        
def pprint_prg(prg_ast, tab = 0):
    variables = ", ".join([x['id'] for x in prg_ast['input']['list']])
    body = pprint_com(prg_ast['body'], tab+1)
    ret = pprint_expr(prg_ast['return_expr'], 0) 
    return ("%smain(%s) {\n%s\n%sreturn (%s);\n%s}" % (tab*'\t', variables, body, (tab+1)*'\t', ret, tab*'\t'))
   
def var_list(prg_ast):
    """ return the list of vars with X: dd 0, .... """
    vars = [x['id'] for x in prg_ast['input']['list']]
    vars += var_list_com(prg_ast['body'])
    vars += var_list_expr(prg_ast['return_expr'])
    vars_set = set(vars)
    return "\n".join(["%s: dd 0" % v for v in vars_set]) 

def init_var(prg_ast):
    vars = [x['id'] for x in prg_ast['input']['list']]
    ivar = ""
    for i in range(len(vars)):
        ivar += """
        mov rax, [argv]
        mov rdi, [rax+%s] 
        call atoi ; le resultat est un entier, il est stocké dans rax
        mov [%s], rax
        """ % (8*(i+1), vars[i])
    return ivar    
    
def compile_prg(prg_ast):
    code_asm = """extern prinf, atoi 
section .data
returnExpr: "%d", 10, 0 ; moule
argc: dd 0              ; 4 octets
argv: dq 0  
VAR_LIST
global main           ; moule
section .text   
main: 
   push rbp
   ; LE CODE DU COMPILO
   mov [argc], rdi
   mov [argv], rsi
   INIT_VAR
   BODY 
   EVAL_RETURN
   mov rdi, returnExpr
   mov rsi, rax
   call printf
   pop rbp
   ret"""
    code_asm = code_asm.replace("VAR_LIST", var_list(prg_ast))
    code_asm = code_asm.replace("INIT_VAR", init_var(prg_ast))
    code_asm = code_asm.replace("EVAL_RETURN", compile_expr(prg_ast['return_expr']))
    code_asm = code_asm.replace("BODY", compile_com(prg_ast['body']))
    return code_asm

 
#try:
ast = parse(GRAMMAR, """main(X, Y){
    while(X){
    X = X - 1;
    Y = Y + 1;
    }
    return (Y) ; 
    }
    """, semantics=Semantics())
print(pprint_prg(ast))
#print(compile_prg(ast))
#except Exception as e:
#    print(e)
