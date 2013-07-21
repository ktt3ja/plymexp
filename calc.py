import ply.lex as lex
import ply.yacc as yacc
from decimal import Decimal

tokens = (
    'NAME','NUMBER',
    'PLUS','MINUS','TIMES','DIVIDE','RAISE_TO','EQUALS', 'SET_TO',
    'LPAREN','RPAREN',
    )

# Tokens

t_PLUS     = r'\+'
t_MINUS    = r'-'
t_TIMES    = r'\*'
t_DIVIDE   = r'/'
t_RAISE_TO = r'\^'
t_EQUALS   = r'='
t_SET_TO   = r'->'
t_LPAREN   = r'\('
t_RPAREN   = r'\)'
t_NAME     = r'[a-zA-Z_][a-zA-Z0-9_]*'

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = Decimal(t.value)
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer
lex.lex()

# Parsing rules

precedence = (
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
    ('right','UMINUS'),
    ('right','RAISE_TO'),
    )


names = { }
reserved_names = ['_last']
def p_statement_assign(t):
    'statement : NAME EQUALS expression'
    if t[1] in reserved_names:
        print "Name %s reserved" % t[1]
    else: 
        names[t[1]] = t[3]

def p_set_last_to(t):
    'statement : SET_TO NAME'
    if t[2] in reserved_names:
        print "Name %s reserved" % t[2]
    else:
        names[t[2]] = names['_last'] 

def p_statement_expr(t):
    'statement : expression'
    names['_last'] = t[1]
    print(t[1])

def p_expression_binop(t):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    if t[2] == '+'  : t[0] = t[1] + t[3]
    elif t[2] == '-': t[0] = t[1] - t[3]
    elif t[2] == '*': t[0] = t[1] * t[3]
    elif t[2] == '/': t[0] = t[1] / t[3]

def p_expression_uminus(t):
    'expression : MINUS expression %prec UMINUS'
    t[0] = -t[2]

def p_expression_exponent(t):
    'expression : expression RAISE_TO expression'
    t[0] = t[1] ** t[3]

def p_expression_group(t):
    'expression : LPAREN expression RPAREN'
    t[0] = t[2]

def p_expression_number(t):
    'expression : NUMBER'
    t[0] = t[1]

def p_expression_name(t):
    'expression : NAME'
    try:
        t[0] = names[t[1]]
    except LookupError:
        print("Undefined name '%s'" % t[1])
        t[0] = 0

def p_error(t):
    print("Syntax error at '%s'" % t.value)

yacc.yacc()

while 1:
    try:
        s = raw_input('calc > ')   # Use raw_input on Python 2
    except EOFError:
        break
    yacc.parse(s)