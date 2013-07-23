import ply.lex as lex
import ply.yacc as yacc
from decimal import Decimal
import decimal
from decimal_math import sin, cos, pi, exp

functions = ['sqrt','sin','cos','ln','log']

tokens = [
    'NAME','NUMBER','FUNCTION',
    'PLUS','MINUS','TIMES','DIVIDE','RAISE_TO','EQUALS','SET_TO',
    'LPAREN','RPAREN',
    ]

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

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.value = t.value.lower();
    if t.value in functions or t.value[:4] == 'log_':
        t.type = 'FUNCTION'
    return t

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


names = {'e': exp(Decimal(1)), 'pi': pi(), '_last': Decimal(0)}
reserved_names = ['e','pi','_last']
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

def p_expression_function(t):
    'expression : FUNCTION LPAREN expression RPAREN'
    if t[1] == 'sqrt':
        t[0] = t[3].sqrt()
    elif t[1] == 'sin':
        t[0] = sin(t[3])
    elif t[1] == 'cos':
        t[0] = cos(t[3])
    elif t[1] == 'ln':
        t[0] = t[3].ln()
    elif t[1] == 'log':
        t[0] = t[3].log10()
    elif t[1][:4] == 'log_':
        try:
            b = Decimal(t[1][4:])
            t[0] = t[3].log10() / b.log10()
        except decimal.InvalidOperation:
            print "Cannot evaluate %s%s%s%s. " \
                  "Setting it to 0." % (t[1], t[2], t[3], t[4])
            t[0] = Decimal(0)

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
        t[0] = Decimal(0)

def p_error(t):
    print("Syntax error at '%s'" % t.value)

yacc.yacc()

while 1:
    try:
        s = raw_input('calc > ')   # Use raw_input on Python 2
    except EOFError:
        break
    yacc.parse(s)