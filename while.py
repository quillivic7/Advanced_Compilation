import tatsu
from tatsu import parse
from tatsu.ast import AST

GRAMMAR = '''
    @@grammar::While

    start = program $
    ;

    program = 'main' '(' var_list ')' '{' command 'return' '(' expr ')' ';' '}' 
    ;

    command = 
    | command command
    | 'if' '(' expr ')' '{' command '}'
    | 'while' '(' expr ')' '{' command '}'
    | var '=' expr ';'
    ;
    
    expr = 
    | expr op expr
    | var
    | nombre
    ;

    var_list = ','<{var}+ 
    ;

    var = /[a-zA-Z][a-zA-Z0-9]*/ 
    ;

    nombre = /[0-9]+/ 
    ;

    op = '+' | '-' | '*' | '>' 
    ;
'''

class Semantics:

    def nombre(self, ast):
        return {'type' : 'constant', 'val' : int(ast)}

    def var(self, ast):
        return {'type' : 'variable', 'id' : ast}

    def expr(self, ast):
        if isinstance(ast, list):
            return {'type' : 'opbin', 'op' : ast[1], 
                    'gauche' : ast[0], 'droit' : ast[2]}
        else: 
            return ast

    def command(self, ast):
        if isinstance(ast, list):
            if ast[1] == '=':
                return {'type' : 'aff', 'lhs' : ast[0], 'rhs' : ast[2]}
            elif ast[0] == 'if':
                return {'type' : 'if', 'expr' : ast[2], 'body' : ast[5]}
            elif ast[0] == 'while':
                return {'type' : 'while', 'expr' : ast[2], 'body' : ast[5]}
            elif len(ast) == 2:
                return {'type' : 'seq', 'first' : ast[0], 'second' : ast[1]}
            else:
                print("Uncatch error")
                return ast
        else:
            print("Uncatch error")
            return ast

    def var_list(self, ast):
        l = []
        def extract_rec(ast):
            if isinstance(ast, tuple):
                extract_rec(ast[1])
                extract_rec(ast[2])
            else:
                l.append(ast)
        extract_rec(ast)
        return {'type' : 'var_list', 'list' : l}

    def program(self, ast):
        return {'type' : 'program', 'input' : ast[2], 'body' : ast[5], 'return_expr' : ast[8]}





def pretty(ast):
    if ast['type'] == 'constant':
        return str(ast['val'])

    elif ast['type'] == 'variable':
        return ast['id']

    elif ast['type'] == 'opbin':
        return pretty(ast['gauche']) + ' ' + ast['op'] + ' ' + pretty(ast['droit'])

    elif ast['type'] == 'aff':
        return pretty(ast['lhs']) + ' = ' + pretty(ast['rhs']) + ';\n'

    elif ast['type'] == 'if':
        return 'if(' + pretty(ast['expr']) + ') {\n\t' + pretty(ast['body']) + '}\n'

    elif ast['type'] == 'while':
        return 'while(' + pretty(ast['expr']) + ') {\n\t' + pretty(ast['body']) + '}\n'

    elif ast['type'] == 'seq':
        return pretty(ast['first']) + pretty(ast['second'])

    elif ast['type'] == 'var_list':
        return ', '.join((pretty(ast_var) for ast_var in ast['list']))

    elif ast['type'] == 'program':
        return 'main(' + pretty(ast['input']) + ') {\n\t' + \
                    pretty(ast['body']) + \
                    'return (' + pretty(ast['return_expr']) + ');\n}'
                    
    else:
        print("Uncatch error: " + ast['type'])


try:
    ast = parse(GRAMMAR, \
        """main(X, Y, Z) {
            while(X) {
                X = X - 1;
                Y = Y + 1;
            }
            return (Y);
        }"""
        , semantics=Semantics())
    print(ast)
    print(pretty(ast))
except Exception as e:
    print(e)

