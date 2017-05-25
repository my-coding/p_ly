import IRTree.tree as tree
import IRTree.frame as frame
import IRTree.env as env
import pprint

_level = 0
_tenv = env.base_tenv()
_venv = env.base_venv()


def array_type(obj):
    t = env.look(_tenv, obj.children[0])
    if t == None:
        error(obj.pos, "type error, not exist arrayType : %s" % (obj.children[0]))
    else:
        env.pop(_tenv)
        return ['TY_ARRAY', t]


def record_type(obj):
    t = []
    for item in obj.children[0]:
        tt = env.look(_tenv, item.children[1])
        if tt == None:
            error(obj.pos, "type error, record : %s" % (item.children[1]))
        elif tt == 'Null' :
            t.append([item.children[0], 'TY_RECORD'])
        else:
            t.append([item.children[0], tt])
    env.pop(_tenv)
    return ['TY_RECORD', t]


def name_type(obj):
    t = env.look(_tenv, obj.children[0])
    if (t == None):
        error(obj.pos, "type error : %s" % (obj.children[0]))
    else:
        env.pop(_tenv)
        return ['TY_NAME', t]


ty = {
    'ArrTy': array_type,
    'RecTy': record_type,
    'TyID': name_type
}


def build_IR_tree_type(obj):
    return ty.get(obj.__class__.__name__, 'Error')(obj)


# TyDec
# name [[FieldDec, name, type],[],[],……]
# 还需要考虑无限递归
def type_dec(obj):
    if (env.look(_tenv, obj.children[0])):
        error(obj.pos, "type error, redefined : %s" % (obj.children[0]))
    env.enter(_tenv, obj.children[0], 'Null')
    env.enter(_tenv, obj.children[0], build_IR_tree_type(obj.children[1]))
    return []


# VarDec name type [exp]
def var_dec(obj):
    global _venv
    access = [_level, frame.alloc_local(frame.get_frame(_level), [True])]

    t = env.look(_tenv, obj.children[1])
    value = build_IR_tree_exp(obj.children[2])
    if obj.children[1] is None:
        t = value.ty
    elif t is None:
        error(obj.pos, "variable type error, no shch type : %s" % (obj.children[1]))
        return []
    elif t != value.ty:
        error(obj.pos, "type error, the exprression is %s type not %s type" % (value.ty, t))
        return []

    if env.look(_venv, '_var_' + obj.children[0]):
        error(obj.pos, "variable redefined : %s" % (obj.children[0]))
# 保存数组大小
    if (t[0] == 'TY_ARRAY') and (len(t) == 2):
        # t += [obj.children[2].children[1].children[0]]
        t += [build_IR_tree_exp(obj.children[2].children[1])]
    env.enter(_venv, '_var_' + obj.children[0], [access, t])
    return tree.Move(simple_var(obj), value)


# FunDec
# name fieldDec type [exp]
def fun_dec(obj):
    global _level
    _level += 1
    if env.look(_venv, '_func_'+obj.children[0]):
        error(obj.pos, "function redefined : %s" % (obj.children[0]))

    fun_label = env.new_label()
    formals = para_list(obj.children[1])
    if obj.children[2] is None:
        result_type = 'TY_VOID'
    else:
        result_type = env.look(_tenv, obj.children[2])
    frame.new_level_item(_level, fun_label, form_escape_list(obj.children[1]))
    env.enter(_venv, '_func_'+obj.children[0],
              [_level, fun_label, formals, result_type])

    env.begin_scope(_venv)
    # fieldList = []
    # for item in obj.children[1]:
        # build_IR_tree_dec(item)
    i = 0
    while i<len(obj.children[1]):
        access = [_level, frame.get_frame(_level)['formals'][i]]
        env.enter(_venv, '_var_' + obj.children[1][i].children[0], [access, env.look(_tenv, obj.children[1][i].children[1])])
        i += 1
    body = build_IR_tree_exp(obj.children[3])
    env.end_scope(_venv)

    frame.add_function(obj.children[0], _level-1, frame.get_frame(_level), body)
    _level -= 1
    return []


def para_list(obj):
    r = []
    for item in obj:
        r.append(env.look(_tenv, item.children[1]))
        # r.append([item.children[0], item.children[1]])
    return r


def form_escape_list(obj):
    r = []
    for item in obj:
        r.append(True)
    return r


# def field_dec(obj):
#     access = [_level, frame.get_frame(_level)]
#     env.enter(_venv, '_var_'+obj.children[0], [access, env.look(_tenv, obj.children[1])])


declare = {
    'TyDec': type_dec,
    'VarDec': var_dec,
    'FunDec': fun_dec,
    # 'FieldDec': field_dec,
}


def build_IR_tree_dec(obj):
    return declare.get(obj.__class__.__name__, 'Error')(obj)


def ir_seq_list(seq_list):
    l = len(seq_list)
    if (l == 0):
        return []
    if (l == 1):
        return seq_list[0]
    if (l == 2):
        return tree.Seq(seq_list[0], seq_list[1], seq_list[1].ty)
    t = seq_list.pop(0)
    return tree.Seq(t, ir_seq_list(seq_list), seq_list[-1].ty)


def program(obj):
    return build_IR_tree_exp(obj.children[0])


def let_exp(obj):
    env.begin_scope(_tenv)
    env.begin_scope(_venv)

    r = []
    for dec in obj.children[0]:
        for item in dec:
            dec_r = build_IR_tree_dec(item)
            if dec_r:
                r.append(dec_r)
    for exp in obj.children[1]:
        exp_r = build_IR_tree_exp(exp)
        if exp_r:
            r.append(exp_r)

    # print("-------tenv-------")
    # env.print_table(_tenv)
    # print("-------venv-------")
    # env.print_table(_venv)

    env.end_scope(_tenv)
    env.end_scope(_venv)
    return ir_seq_list(r)


def const_exp(obj):
    return tree.Const(obj.children[0], 'TY_INT')


def binop_exp(obj):
    o = obj.children[1]
    e1 = build_IR_tree_exp(obj.children[0])
    e2 = build_IR_tree_exp(obj.children[2])
    if o in ['+', '-', '*', '/']:
        if (e1.ty != 'TY_INT') and (e2.ty != 'TY_INT'):
            error(obj.pos, 'unsupported operand type(s) for %s: \'%s\' and \'%s\'' % (o, e1.ty, e2.ty))
        return tree.Binop(o, e1, e2, 'TY_INT')
    if o in ['<', '<=', '>', '>=', '<>', '=']:
        if ((type(e1.ty) is list) and (e1.ty[0] == 'TY_RECORD') and (e2.ty == 'TY_NIL')) \
                or ((type(e2.ty) is list) and (e2.ty[0] == 'TY_RECORD') and (e1.ty == 'TY_NIL')):
            return tree.Binop(o, e1, e2, 'TY_INT')
        elif e1.ty != e2.ty:
            error(obj.pos, 'unsupported operand type(s) for %s: \'%s\' and \'%s\'' % (o, e1.ty, e2.ty))
        # elif e1.ty not in ['TY_INT', 'TY_STRING']:
        #     error(obj.pos, 'unsupported operand type(s) for %s: \'%s\' and \'%s\', only for int and string' % (o, e1.ty, e2.ty))

        if e1.ty == 'TY_STRING':
            stmt = tree.Call(tree.Name("__strcmp__"), [e1, e2])
            return tree.Binop(o, stmt, tree.Const(0), 'TY_INT')
        else:
            return tree.Binop(o, e1, e2, 'TY_INT')


def string_exp(obj):
    # return name(obj.children[0])
    lab = env.new_temp()
    frame.add_string(lab, obj.children[0])
    return tree.Name(lab, 'TY_STRING')


def move_exp(obj):
    dst = build_IR_tree_exp(obj.children[0])
    src = build_IR_tree_exp(obj.children[1])

    if dst.ty != src.ty:
        error(obj.pos, "can not assign %s to %s" % (src.ty, dst.ty))
    return tree.Move(dst, src)


def nil_exp(obj):
    return tree.Const(0,  'TY_NIL')


def call_exp(obj):
    fun_entry = env.look(_venv, '_func_'+obj.children[0])
    if not fun_entry:
        error(obj.pos, "call error, no such function: %s" % (obj.children[0]))
        return None

    i = 0
    field = []
    if len(obj.children[1]) == len(fun_entry[2]):
        while i<len(obj.children[1]):
            item = build_IR_tree_exp(obj.children[1][i])
            #类型检查
            field.append(item)
            i+=1
    elif len(obj.children[1]) <= len(fun_entry[2]):
        error(obj.pos, "call error, function except more arguments : %s"%(obj.children[0]))
    else:
        error(obj.pos, "call error, function except less arguments : %s"%(obj.children[0]))

    # return tree.Call([fun_entry[0], fun_entry[1]], field)
    fr = frame.get_frame_by_name(fun_entry[0], fun_entry[1])
    # print(fr['formals'])
    return tree.Call(tree.Name(fun_entry[1]),
                     [fr['formals'], field], fun_entry[3])


def seq_exp(obj):
    r = []
    for item in obj.children[0]:
        r.append(build_IR_tree_exp(item))
    return ir_seq_list(r)


def if_then_else_exp(obj):
    t = env.new_label()
    f = env.new_label()
    done = env.new_label()
    result = env.new_temp()

    e1 = build_IR_tree_exp(obj.children[0])
    if e1.ty != 'TY_INT':
        error(obj.pos, "if condition must be int not %s" % (e1.ty))

    e2 = build_IR_tree_exp(obj.children[1])
    e3 = build_IR_tree_exp(obj.children[2])
    if (e2.ty != e3.ty) \
            and not(((type(e2.ty) is list) and (e2.ty[0] == 'TY_RECORD') and (e3.ty == 'TY_NIL')) \
            or ((type(e3.ty) is list) and (e3.ty[0] == 'TY_RECORD') and (e2.ty == 'TY_NIL'))):
        error(obj.pos, "then type : %s doesn't match else type : %s" % (e2.ty, e3.ty))

    return tree.Eseq(ir_seq_list([un_cx(e1, t, f),
                                  tree.Label(t),
                                  tree.Move(tree.Mem(result), e2),
                                  tree.Jump(tree.Name(done), [done]),
                                  tree.Label(f),
                                  tree.Move(tree.Mem(result), e3),
                                  tree.Label(done)]),
                     tree.Temp(result), e2.ty)


def if_then_exp(obj):
    t = env.new_label()
    f = env.new_label()

    e1 = build_IR_tree_exp(obj.children[0])
    if e1.ty != 'TY_INT':
        error(obj.pos, "if condition must be int not %s" % (e1.ty))
    e2 = build_IR_tree_exp(obj.children[1])
    if e2.ty != 'TY_VOID':
        error(obj.pos, "if then's body must be TY_VOID, unsupport %s type" % (e2.ty))

    return ir_seq_list([un_cx(e1, t, f),
                        tree.Label(t),
                        e2,
                        tree.Label(f)])


def while_exp(obj):
    start = env.new_label()
    loop = env.new_label()
    done = env.new_label()

    e1 = build_IR_tree_exp(obj.children[0])
    if e1.ty != 'TY_INT':
        error(obj.pos, "while's condition must be int not %s" % (e1.ty))

    e2 = build_IR_tree_exp(obj.children[1])
    if e2.ty != 'TY_VOID':
        error(obj.pos, "while's body must be TY_VOID, unsupport %s type" % (e2.ty))

    return ir_seq_list([tree.Label(start),
                        un_cx(e1, loop, done),
                        tree.Label(loop), e2,
                        tree.Jump(tree.Name(start), [start]),
                        tree.Label(done)])


def for_exp(obj):
    start = env.new_label()
    loop = env.new_label()
    done = env.new_label()

    env.begin_scope(_venv)
    access = [_level, frame.alloc_local(frame.get_frame(_level), [True])]
    if env.look(_venv, '_var_' + obj.children[0]):
        error(obj.pos, "for's variable redefined : %s" % (obj.children[0]))

    env.enter(_venv, '_var_' + obj.children[0], [access, 'TY_INT'])
    var = frame.expr(access[1], frame.fp())

    e1 = build_IR_tree_exp(obj.children[1])
    e2 = build_IR_tree_exp(obj.children[2])
    e3 = build_IR_tree_exp(obj.children[3])
    if e3.ty != 'TY_VOID':
        error(obj.pos, "for's body must be TY_VOID, unsupport %s type" % (e2.ty))

    env.end_scope(_venv)
    return ir_seq_list([tree.Move(var, e1),
                        tree.Label(start),
                        tree.Cjump(['<='], var, e2, tree.Name(loop), tree.Name(done)),
                        tree.Label(loop), e3,
                        tree.Move(var, tree.Binop('+', var, tree.Const(1))),
                        tree.Jump(tree.Name(start), [start]), tree.Label(done)])


def break_exp(obj):
    return None


def simple_var(obj):
    var = env.look(_venv, '_var_'+obj.children[0])
    if not var:
        error(obj.pos, 'variable not declare : %s' % (obj.children[0]))
        return tree.Const(0,  'TY_INT')
    return frame.expr(var[0][1], frame.fp(), var[1])


def array_create(obj):
    t = env.look(_tenv, obj.children[0])
    if not t:
        error(obj.pos, 'no such type : %s' % (obj.children[0]))
        return None
    if t[0] != 'TY_ARRAY':
        error(obj.pos, '%s is not array' % (obj.children[0]))
        return None
    size = build_IR_tree_exp(obj.children[1])
    init = build_IR_tree_exp(obj.children[2])
    if size.ty != 'TY_INT':
        error(obj.pos, 'size of array unsupport %s' % (size.ty))
        return None
    if t[1] != init.ty:
        error(obj.pos, 'need %s not %s' % (t, init.ty))
    return tree.Call(tree.Name("__arrayCreate__"), [size, init], t)


def array_sub(obj):
    var = build_IR_tree_exp(obj.children[0])
    if var.ty[0] != 'TY_ARRAY':
        error(obj.pos, 'need array type not %s' % (var.ty))
        return None

    sub = build_IR_tree_exp(obj.children[1])
    if sub.ty != 'TY_INT':
        error(obj.pos, 'array sub need TY_INT not %s' % (sub.ty))
        return None

    return tree.Mem(tree.Binop('+', var, tree.Binop('*', sub, tree.Const(frame.WORD_SIZE))), var.ty[1])


def record_create(obj):
    t = env.look(_tenv, obj.children[0])
    addr = tree.Temp(env.new_temp())

    if not t:
        error(obj.pos, 'no such type : %s' % (obj.children[0]))
        return None
    if t[0] != 'TY_RECORD':
        error(obj.pos, 'type is not record : %s' % (obj.children[0]))
        return None
    size = len(t[1])
    if len(obj.children[1]) != size:
        error(obj.pos, 'need %d items, but give %d items in record: %s' % (len(obj.children[1]), size, obj.children[0]))

    i = 0
    record = []
    while i < size:
        index = find_record_index(t[1], obj.children[1][i].children[0])
        if index is None:
            error(obj.pos, "record create error, type %s has no such item : \'%s\'" % (obj.children[0], obj.children[1][i].children[0]))
        value = build_IR_tree_exp(obj.children[1][i])
        location = tree.Binop('+', addr, tree.Const(index*frame.WORD_SIZE))
        record.append(tree.Move(tree.Mem(location), value))
        i += 1

    alloc = tree.Call(tree.Name("__recordCreate__"), [size])
    r = [tree.Move(addr, alloc)] + record
    return tree.Eseq(ir_seq_list(r), addr, t)


def find_record_index(l, var):
    for item in l:
        if item[0] == var:
            return l.index(item)
    return None


def field_create(obj):
    return build_IR_tree_exp(obj.children[1])


def record_var(obj):
    t = env.look(_venv, '_var_'+obj.children[0].children[0])
    if t is None:
        error(obj.pos, 'no such variable %s:' % (obj.children[0]))
    elif t[1][0] != 'TY_RECORD':
        error(obj.pos, 'variable is not record : %s' % (obj.children[0]))

    index = find_record_index(t[1][1], obj.children[1])
    if index is None:
        error(obj.pos, "no such record item : \'%s\'"%(obj.children[1]))
    # print(t[1][1][index][1])
    return tree.Mem(tree.Binop('+', build_IR_tree_exp(obj.children[0]),
                    tree.Binop('*', tree.Const(index), tree.Const(frame.WORD_SIZE))),
                    t[1][1][index][1])


expression = {
    'Program': program,
    'LetExp': let_exp,

    'IntLit': const_exp,
    'StringLit': string_exp,
    'NilLit': nil_exp,
    'Binop': binop_exp,
    'Assign': move_exp,
    'Call': call_exp,
    'SeqExp': seq_exp,
    'IfThen': if_then_exp,
    'IfThenElse': if_then_else_exp,
    'WhileExp': while_exp,
    'ForExp': for_exp,
    'Break': break_exp,

    'SimpleVar': simple_var,
    'ArrCreate': array_create,
    'Subscript': array_sub,
    'RecCreate': record_create,
    'FieldCreate': field_create,
    'FieldExp': record_var,
}


def build_IR_tree_exp(obj):
    return expression.get(obj.__class__.__name__, 'Error')(obj)


def init_venv():
    frame.new_level_item(_level, env.new_label(), [])
    l1 = env.new_label()
    frame.new_level_item(_level+1, l1, [])
    env.enter(_venv, env.symbol('_func_print'),
              [_level+1, l1, ['TY_STRING'], 'TY_VOID'])

    l2 = env.new_label()
    frame.new_level_item(_level+1, l2, [])
    env.enter(_venv, env.symbol('_func_getchar'),
              [_level+1, l2, [], 'TY_STRING'])

    l3 = env.new_label()
    frame.new_level_item(_level+1, l3, [])
    env.enter(_venv, env.symbol('_func_ord'),
              [_level+1, l3, ['TY_STRING'], 'TY_INT'])

    l4 = env.new_label()
    frame.new_level_item(_level + 1, l4, [])
    env.enter(_venv, env.symbol('_func_chr'),
              [_level + 1, l4, ['TY_INT'], 'TY_STRING'])


def build_IR_tree(obj):
    init_venv()
    r = build_IR_tree_exp(obj)
    print("-------tenv-------")
    env.print_table(_tenv)
    print("-------venv-------")
    env.print_table(_venv)
    print("------level--------")
    print(_level)
    pprint.pprint(frame._level)
    print("--------str--------")
    pprint.pprint(frame._string)
    print("------func--------")
    pprint.pprint(frame._function)
    print("------------------")
    return r


def error(pos, msg):
    print("At (%d, %d) %s" % (pos[0], pos[1], msg))


def un_ex(obj):
    if obj.kind == 'ex':
        return obj
    elif obj.kind == 'un':
        return tree.Eseq(obj, tree.Const(0))
    elif obj.kind == 'cx':
        t = env.new_temp()
        t = env.new_temp()
        f = env.new_temp()
        return tree.Eseq( ir_seq_list(
            tree.Move(tree.Temp(r), tree.Const(1)),
            obj, tree.Label(f),
            tree.Move(tree.Temp(r), tree.Const(0)), tree.Label(t)
        ), tree.Temp(t))
    else:
        print("error kind of IRtree")


def un_cx(obj, t, f):
    if obj.kind == 'ex':
        return tree.Cjump(['='], obj, tree.Const(0), tree.Name(t), tree.Name(f))
    elif obj.kind == 'un':
        return None
    elif obj.kind == 'cx':
        return obj
    else:
        print("error kind of IRtree")


def to_list(obj):
    try:
        return [to_list(item) for item in obj.children]
    except AttributeError:
        if type(obj) is list:
            return [to_list(item) for item in obj]
        else:
            return obj


if __name__ == '__main__':
    a = ir_seq_list([1, 2, 3, 4, 5, 6])
    print(to_list(a))
