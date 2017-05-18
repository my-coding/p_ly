# coding=utf-8
"""
This package works as lexer and parser.

This module takes the source code as input
and gives the abstract tree as output.
"""

import pprint
import ATree

tokens = (
    'ID', 'INT', 'STRING',
    'NEQ', 'LE', 'GE', 'ASSIGN',

    'ARRAY',
    'IF',
    'THEN',
    'ELSE',
    'WHILE',
    'FOR',
    'TO',
    'DO',
    'LET',
    'IN',
    'END',
    'OF',
    'BREAK',
    'NIL',
    'FUNCTION',
    'VAR',
    'TYPE',
)

literals = (
    '+', '-', '*', '/',
    '=', '<', '>',
    '&', '|',
    ',', ':', ';', '.',
    '(', ')', '[', ']', '{', '}',
)

reserved = {
    'array': 'ARRAY',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'to': 'TO',
    'do': 'DO',
    'let': 'LET',
    'in': 'IN',
    'end': 'END',
    'of': 'OF',
    'break': 'BREAK',
    'nil': 'NIL',
    'function': 'FUNCTION',
    'var': 'VAR',
    'type': 'TYPE',
}

t_NEQ = r'<>'
t_LE = r'<='
t_GE = r'>='
t_ASSIGN = r':='

# t_STRING = r'".+?"'

t_ignore = ' \t'

t_stringcond_ignore = ' \t'

states = (
    ('stringcond', 'exclusive'),
)


def t_STRINGBEG(t):
    r'"'
    gdict["string_mem"] = ""
    t.lexer.begin('stringcond')
    pass


def t_stringcond_STRING(t):
    r'"'
    t.lexer.begin('INITIAL')
    t.value = gdict["string_mem"]
    return t


def t_stringcond_general(t):
    r'[^\n\"\\]+'
    gdict["string_mem"] += t.value
    pass


def t_stringcond_blankescape(t):
    r'\\[ \t\n]*\\'
    t.lexer.lineno += t.value.count("\n")
    pass


def t_stringcond_codeescape(t):
    r'\\[0-9]{1,3}'
    gdict["string_mem"] += chr(t.value[1:])
    pass


def t_stringcond_tabescape(t):
    r'\\t'
    gdict["string_mem"] += '\t'
    pass


def t_stringcond_newlineescape(t):
    r'\\n'
    gdict["string_mem"] += '\n'
    pass


def t_stringcond_backslashescape(t):
    r'\\\\'
    gdict["string_mem"] += '\\'
    pass


def t_stringcond_dqescape(t):
    r'\\"'
    gdict["string_mem"] += '\"'
    pass


def t_INT(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t


def t_ID(t):
    r'[a-zA-Z_][0-9a-zA-Z_]*'
    t.type = reserved.get(t.value, 'ID')
    return t


def t_COMMENT(t):
    r'/[*](.|\n)*?[*]/'
    t.lexer.lineno += t.value.count("\n")
    pass


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '{0}'".format(t.value[0]))
    t.lexer.lineno += t.value.count("\n")
    t.lexer.skip(1)


def t_stringcond_error(t):
    print("Illegal character '{0}'".format(t.value[0]))
    t.lexer.lineno += t.value.count("\n")
    t.lexer.skip(1)


# Build the lexer
import ply.lex as lex

lexer = lex.lex()

# if __name__ == '__main__':
#     def test_lex():
#         data = '''
#         let
#             var x := 12 \* A local varible. *\
#         in
#             x + 1 \* result *\
#         end
#         '''
#         lexer.input(data)
#
#         # Tokenize
#         while True:
#             tok = lexer.token()
#             if not tok:
#                 break  # No more input
#             print(tok)
#
#     test_lex()

precedence = (
    ('left', 'THEN', 'DO', 'OF'),
    ('left', 'ELSE'),
    ('left', 'ASSIGN'),
    ('left', '|'),
    ('left', '&'),
    ('left', '=', '<', '>', 'NEQ', 'LE', 'GE'),
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),
)


def p_program_expr(p):
    """program : expr"""
    p[0] = ATree.Program(p[1], (p.lineno(1), p.lexpos(1)))


def p_program_expr_repeat(p):
    """program : program error expr"""
    print("Reason: more than one expression in one program")
    p[0] = ATree.Program(p[3], (p.lineno(3), p.lexpos(3)))


def p_program_expr_error(p):
    """program : error expr"""
    print("Reason: invalid expression")
    p[0] = ATree.Program(p[2], (p.lineno(2), p.lexpos(2)))


def p_expr_binop(p):
    """expr : expr '+' expr
            | expr '-' expr
            | expr '*' expr
            | expr '/' expr
            | expr NEQ expr
            | expr LE expr
            | expr GE expr
            | expr '=' expr
            | expr '<' expr
            | expr '>' expr
            | expr '|' expr
            | expr '&' expr"""
    if p[2] == '|':
        p[0] = ATree.IfThenElse(p[1], ATree.IntLit(1, (-1, -1)), p[3], (p.lineno(1), p.lexpos(1)))
    elif p[2] == '&':
        p[0] = ATree.IfThenElse(p[1], p[3], ATree.IntLit(0, (-1, -1)), (p.lineno(1), p.lexpos(1)))
    else:
        p[0] = ATree.Binop(p[1], p[2], p[3], (p.lineno(1), p.lexpos(1)))


def p_expr_nil(p):
    """expr : NIL"""
    p[0] = ATree.NilLit((p.lineno(1), p.lexpos(1)))


def p_expr_break(p):
    """expr : BREAK"""
    p[0] = ATree.Break((p.lineno(1), p.lexpos(1)))


def p_expr_negation(p):
    """expr : '-' expr %prec UMINUS"""
    p[0] = ATree.Binop(ATree.IntLit(0, (-1, -1)), '-', p[2], (p.lineno(1), p.lexpos(1)))


def p_expr_int(p):
    """expr : INT"""
    p[0] = ATree.IntLit(p[1], (p.lineno(1), p.lexpos(1)))


def p_expr_string(p):
    """expr : STRING"""
    p[0] = ATree.StringLit(p[1], (p.lineno(1), p.lexpos(1)))


def p_expr_lvalue(p):
    """expr : lvalue"""
    p[0] = p[1]


def p_lvalue_simpleVar(p):
    """lvalue : ID"""
    p[0] = ATree.SimpleVar(p[1], (p.lineno(1), p.lexpos(1)))


def p_lvalue_complexLValue(p):
    """lvalue : complexLValue"""
    p[0] = p[1]


def p_complexLValue(p):
    """complexLValue : subscript
                    |  fieldExp"""
    p[0] = p[1]


def p_subscript_complex(p):
    """subscript : complexLValue '[' expr ']'"""
    p[0] = ATree.Subscript(p[1], p[3], (p.lineno(1), p.lexpos(1)))


def p_subscript_simple(p):
    """subscript : ID '[' expr ']'"""
    p[0] = ATree.Subscript(ATree.SimpleVar(p[1], (p.lineno(1), p.lexpos(1))), p[3], (p.lineno(1), p.lexpos(1)))


def p_fieldExp(p):
    """fieldExp : lvalue '.' ID"""
    p[0] = ATree.FieldExp(p[1], p[3], (p.lineno(1), p.lexpos(1)))


def p_expr_assign(p):
    """expr : lvalue ASSIGN expr"""
    p[0] = ATree.Assign(p[1], p[3], (p.lineno(1), p.lexpos(1)))


def p_expr_seqExp(p):
    """expr : '(' exprSemiStar ')'"""
    p[0] = ATree.SeqExp(p[2], (p.lineno(1), p.lexpos(1)))


def p_expr_call(p):
    """expr : ID '(' exprCommaStar ')'"""
    p[0] = ATree.Call(p[1], p[3], (p.lineno(1), p.lexpos(1)))


def p_expr_arrCreate(p):
    """expr : ID '[' expr ']' OF expr"""
    p[0] = ATree.ArrCreate(p[1], p[3], p[6], (p.lineno(1), p.lexpos(1)))


def p_expr_recCreate(p):
    """expr : ID '{' fieldCreateCommaStar '}'"""
    p[0] = ATree.RecCreate(p[1], p[3], (p.lineno(1), p.lexpos(1)))


def p_fieldCreate(p):
    """fieldCreate : ID '=' expr"""
    p[0] = ATree.FieldExp(p[1], p[3], (p.lineno(1), p.lexpos(1)))


def p_expr_ifThen(p):
    """expr : IF expr THEN expr"""
    p[0] = ATree.IfThen(p[2], p[4], (p.lineno(1), p.lexpos(1)))


def p_expr_ifThenElse(p):
    """expr : IF expr THEN expr ELSE expr"""
    p[0] = ATree.IfThenElse(p[2], p[4], p[6], (p.lineno(1), p.lexpos(1)))


def p_expr_whileExp(p):
    """expr : WHILE expr DO expr"""
    p[0] = ATree.WhileExp(p[2], p[4], (p.lineno(1), p.lexpos(1)))


def p_expr_forExp(p):
    """expr : FOR ID ASSIGN expr TO expr DO expr"""
    p[0] = ATree.ForExp(p[2], p[4], p[6], p[8], (p.lineno(1), p.lexpos(1)))


def p_expr_letExp(p):
    """expr : LET decPlus IN exprSemiStar END"""
    p[0] = ATree.LetExp(p[2], p[4], (p.lineno(1), p.lexpos(1)))


def p_dec_tyDec(p):
    """dec : TYPE ID '=' ty"""
    p[0] = ATree.TyDec(p[2], p[4], (p.lineno(1), p.lexpos(1)))


def p_dec_varDec(p):
    """dec : VAR ID ASSIGN expr"""
    p[0] = ATree.VarDec(p[2], None, p[4], (p.lineno(1), p.lexpos(1)))


def p_dec_varDec_more(p):
    """dec : VAR ID ':' ID ASSIGN expr"""
    p[0] = ATree.VarDec(p[2], p[4], p[6], (p.lineno(1), p.lexpos(1)))


def p_dec_funDec(p):
    """dec : FUNCTION ID '(' fieldDecCommaStar ')' '=' expr"""
    p[0] = ATree.FunDec(p[2], p[4], None, p[7], (p.lineno(1), p.lexpos(1)))


def p_dec_funDec_more(p):
    """dec : FUNCTION ID '(' fieldDecCommaStar ')' ':' ID '=' expr"""
    p[0] = ATree.FunDec(p[2], p[4], p[7], p[9], (p.lineno(1), p.lexpos(1)))


def p_ty_tyID(p):
    """ty : ID"""
    p[0] = ATree.TyID(p[1], (p.lineno(1), p.lexpos(1)))


def p_ty_arrTy(p):
    """ty : ARRAY OF ID"""
    p[0] = ATree.ArrTy(p[3], (p.lineno(1), p.lexpos(1)))


def p_ty_recTy(p):
    """ty : '{' fieldDecCommaStar '}'"""
    p[0] = ATree.RecTy(p[1], (p.lineno(1), p.lexpos(1)))


def p_fieldDec(p):
    """fieldDec : ID ':' ID"""
    p[0] = ATree.FieldDec(p[1], p[3], (p.lineno(1), p.lexpos(1)))


def p_fieldDecCommaStar_empty(p):
    """fieldDecCommaStar : """
    p[0] = []


def p_fieldDecCommaStar(p):
    """fieldDecCommaStar : fieldDecCommaPlus"""
    p[0] = p[1]


def p_fieldDecCommaPlus_single(p):
    """fieldDecCommaPlus : fieldDec"""
    p[0] = [p[1]]


def p_fieldDecCommaPlus_append(p):
    """fieldDecCommaPlus : fieldDecCommaPlus ',' fieldDec"""
    p[0] = p[1] + [p[3]]


def p_decPlus_single(p):
    """decPlus : dec"""
    p[0] = [p[1]]


def p_decPlus_single_error(p):
    """decPlus : error"""
    print("Reason: invalid declaration")
    p[0] = []


def p_decPlus_append(p):
    """decPlus : decPlus dec"""
    p[0] = p[1] + [p[2]]


def p_decPlus_append_error(p):
    """decPlus : decPlus error"""
    print("Reason: invalid declaration")
    p[0] = p[1]


def p_fieldCreateCommaStar_empty(p):
    """fieldCreateCommaStar : """
    p[0] = []


def p_fieldCreateCommaStar(p):
    """fieldCreateCommaStar : fieldCreateCommaPlus"""
    p[0] = p[1]


def p_fieldCreateCommaPlus_single(p):
    """fieldCreateCommaPlus : fieldCreate"""
    p[0] = [p[1]]


def p_fieldCreateCommaPlus_append(p):
    """fieldCreateCommaPlus : fieldCreateCommaPlus ',' fieldCreate"""
    p[0] = p[1] + [p[3]]


def p_exprSemiStar_empty(p):
    """exprSemiStar : """
    p[0] = []


def p_exprSemiStar(p):
    """exprSemiStar : exprSemiPlus"""
    p[0] = p[1]


def p_exprSemiPlus_single(p):
    """exprSemiPlus : expr"""
    p[0] = [p[1]]


def p_exprSemiPlus_single_error(p):
    """exprSemiPlus : error"""
    print("Reason: invalid expression")
    p[0] = []


def p_exprSemiPlus_append(p):
    """exprSemiPlus : exprSemiPlus ';' expr"""
    p[0] = p[1] + [p[3]]


def p_exprSemiPlus_append_error(p):
    """exprSemiPlus : exprSemiPlus error"""
    print("Reason: invalid expression")
    p[0] = p[1]


def p_exprCommaStar_empty(p):
    """exprCommaStar : """
    p[0] = []


def p_exprCommaStar(p):
    """exprCommaStar : exprCommaPlus"""
    p[0] = p[1]


def p_exprCommaPlus_single(p):
    """exprCommaPlus : expr"""
    p[0] = [p[1]]


def p_exprCommaPlus_append(p):
    """exprCommaPlus : exprCommaPlus ',' expr"""
    p[0] = p[1] + [p[3]]


def p_error(p):
    if p:
        print(
            "At ({2}, {3}) syntax error: TokenValue {1}".format(p.type, repr(p.value), p.lineno, find_column(p.lexpos)))
    else:
        print("Syntax error at EOF")


import ply.yacc as yacc

parser = yacc.yacc()

gdict = dict()


def find_column(textpos):
    last_cr = gdict["code"].rfind('\n', 0, textpos)
    if last_cr < 0:
        last_cr = 0
    column = textpos - last_cr
    return column


def convert_pos(obj):
    """
    Originally the pos of  ATree Node has the offset from the text beginning.
    This function converts them to the offset from the row begining.
    :param obj: ATree Node
    :return:None
    """
    try:
        for item in obj.children:
            convert_pos(item)
        obj.pos = (obj.pos[0], find_column(obj.pos[1]))
    except AttributeError:
        if type(obj) is list:
            for item in obj:
                convert_pos(item)


def build_abstract_syntax_tree(code):
    gdict["code"] = code
    res = yacc.parse(code, tracking=True)
    ATree.fold_decList(res)
    convert_pos(res)
    return res


if __name__ == '__main__':
    def test_yacc():
        code = """
        let
	        type  strArr = array of string
	        type  intArr = array of int
	        var x: int := 12 + 3
	        var y: string := "story"
	        function foo(): int = 108 + 88
	        function foo2(i: int, j: int) = 108 + i - j
        in
            3 + 7;
            strArr = intArr
        end
        """
        res = build_abstract_syntax_tree(code)
        pprint.pprint(ATree.to_list(res), indent=4)


    test_yacc()
