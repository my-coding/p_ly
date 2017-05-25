# coding=utf-8
"""
This module defines abstract syntax tree.
"""



def to_list(obj):
    try:
        return [obj.__class__.__name__] + [to_list(item) for item in obj.children]
    except AttributeError:
        if type(obj) is list:
            return [to_list(item) for item in obj]
        else:
            return obj


def fold_decList(obj):
    try:
        for item in obj.children:
            fold_decList(item)
        obj.fold_decList()
    except AttributeError:
        if type(obj) is list:
            for item in obj:
                fold_decList(item)


class Program:
    def __init__(self, expr, pos):
        self.pos = pos
        self.children = [expr]


class Binop:
    def __init__(self, left, op, right, pos):
        self.pos = pos
        self.children = [left, op, right]


class IntLit:
    def __init__(self, value, pos):
        self.pos = pos
        self.children = [value]


class StringLit:
    def __init__(self, value, pos):
        self.pos = pos
        self.children = [value]


class NilLit:
    def __init__(self, pos):
        self.pos = pos
        self.children = []


class Break:
    def __init__(self, pos):
        self.pos = pos
        self.children = []


class SimpleVar:
    def __init__(self, var_id, pos):
        self.pos = pos
        self.children = [var_id]


class Assign:
    def __init__(self, lvalue, expr, pos):
        self.pos = pos
        self.children = [lvalue, expr]


class FieldExp:
    def __init__(self, lvalue, field_id, pos):
        self.pos = pos
        self.field_id = field_id
        self.children = [lvalue, field_id]


class Subscript:
    def __init__(self, lvalue, expr, pos):
        self.pos = pos
        self.children = [lvalue, expr]


class SeqExp:
    def __init__(self, exprList, pos):
        self.pos = pos
        self.children = [exprList]


class Call:
    def __init__(self, func_id, exprList, pos):
        self.pos = pos
        self.children = [func_id, exprList]


class ArrCreate:
    def __init__(self, type_id, length, ini, pos):
        self.pos = pos
        self.children = [type_id, length, ini]


class RecCreate:
    def __init__(self, type_id, fieldCreateList, pos):
        self.pos = pos
        self.children = [type_id, fieldCreateList]


class FieldCreate:
    def __init__(self, field_id, expr, pos):
        self.pos = pos
        self.children = [field_id, expr]


class IfThen:
    def __init__(self, cond, body, pos):
        self.pos = pos
        self.children = [cond, body]


class IfThenElse:
    def __init__(self, cond, thenBody, elseBody, pos):
        self.pos = pos
        self.children = [cond, thenBody, elseBody]


class WhileExp:
    def __init__(self, cond, body, pos):
        self.pos = pos
        self.children = [cond, body]


class ForExp:
    def __init__(self, var_id, low, hight, body, pos):
        self.pos = pos
        self.children = [var_id, low, hight, body]


class LetExp:
    def __init__(self, decList, exprList, pos):
        self.pos = pos
        self.children = [decList, exprList]

    def fold_decList(self):
        def add_item(lstt, itemm):
            try:
                if lstt[-1][-1].__class__.__name__ == itemm.__class__.__name__:
                    lstt[-1].append(itemm)
                else:
                    lstt.append([itemm])
            except IndexError:
                lstt.append([itemm])

        lst = []
        for item in self.children[0]:
            add_item(lst, item)
        self.children[0] = lst


class TyID:
    def __init__(self, type_id, pos):
        self.pos = pos
        self.children = [type_id]


class ArrTy:
    def __init__(self, type_id, pos):
        self.pos = pos
        self.children = [type_id]


class RecTy:
    def __init__(self, fieldDecList, pos):
        self.pos = pos
        self.children = [fieldDecList]


class FieldDec:
    def __init__(self, field_id, type_id, pos):
        self.pos = pos
        self.children = [field_id, type_id]


class TyDec:
    def __init__(self, type_id, ty, pos):
        self.pos = pos
        self.children = [type_id, ty]


class VarDec:
    def __init__(self, var_id, type_id, expr, pos):
        self.pos = pos
        self.children = [var_id, type_id, expr]


class FunDec:
    def __init__(self, func_id, params, type_id, expr, pos):
        self.pos = pos
        self.children = [func_id, params, type_id, expr]
