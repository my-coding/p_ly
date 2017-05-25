import IRTree.tree as tree
import IRTree.env as env
import IRTree.frame as frame
import pprint

_level = 0
_tenv = env.base_tenv()
_venv = env.base_venv()


def array_type(obj):
    t = env.look(_tenv, obj.children[0])
    if t == None:
        # print('arr type error')
        error(obj.pos, "type error, not exist arrayType :", obj.children[0])
    else:
        env.pop(_tenv)
        return ['TY_ARRAY', t]


def record_type(obj):
    t = []
    for item in obj.children[0]:
        tt = env.look(_tenv, item.children[1])
        if tt == None:
            error(obj.pos, "type error, record :", item.children[1])
        elif tt == 'Null' :
            t.append([item.children[0], 'TY_RECORD'])
        else:
            t.append([item.children[0], tt])
    env.pop(_tenv)
    return ['TY_RECORD', t]


def name_type(obj):
    t = env.look(_tenv, obj.children[0])
    if (t == None):
        # print('arr type error')
        error(obj.pos, "type error, name :", obj.children[0])
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
        error(obj.pos, "type error, redefined :", obj.children[0])
    env.enter(_tenv, obj.children[0], 'Null')
    env.enter(_tenv, obj.children[0], build_IR_tree_type(obj.children[1]))
    return []


# VarDec name type [exp]
def var_dec(obj):
    global _venv
    access = [_level, frame.alloc_local(frame.get_frame(_level), [True])]

    t = env.look(_tenv, obj.children[1])
    if obj.children[1] == None:
        t = 'unknown'            # 换成表达式对应的type
    elif not t:
        error(obj.pos, "variable type error, no shch type :", obj.children[1])
        return []

    env.enter(_venv, '_var_' + obj.children[0], [access, t])
    return tree.Move(simple_var(obj), build_IR_tree_exp(obj.children[2]))


# FunDec
# name fieldDec type [exp]
def fun_dec(obj):
    global _level
    _level += 1
    if(env.look(_venv, '_func_'+obj.children[0])):
        error(obj.pos, "function redefined :", obj.children[0])
        return []

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
    fieldList = []
    for item in obj.children[1]:
        build_IR_tree_dec(item)
    body = build_IR_tree_exp(obj.children[3])
    env.end_scope(_venv)

    _level -= 1
    # 把数存到fragment里
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


def field_dec(obj):
    access = [_level, frame.alloc_local(frame.get_frame(_level), [True])]
    env.enter(_venv, '_var_' + obj.children[0], [access, env.look(_tenv, obj.children[1])])


declare = {
    'TyDec': type_dec,
    'VarDec': var_dec,
    'FunDec': fun_dec,
    'FieldDec': field_dec,
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
        return tree.Seq(seq_list[0], seq_list[1])
    t = seq_list.pop(0)
    return tree.Seq(t, ir_seq_list(seq_list))


def program(obj):
    return build_IR_tree_exp(obj.children[0])


def let_exp(obj):
    env.begin_scope(_tenv)
    env.begin_scope(_venv)

    r = []
    for dec in obj.children[0]:
        for item in dec:
            dec_r = build_IR_tree_dec(item)
            if dec_r != []:
                r.append(dec_r)
    for exp in obj.children[1]:
        r.append(build_IR_tree_exp(exp))

    env.end_scope(_tenv)
    env.end_scope(_venv)
    return ir_seq_list(r)


def const_exp(obj):
    return tree.Const(obj.children[0], 'ex')


def binop_exp(obj):
    o = obj.children[1]
    e1 = build_IR_tree_exp(obj.children[0])
    e2 = build_IR_tree_exp(obj.children[2])
    return tree.Binop(o, e1, e2, 'ex')


def string_exp(obj):
    # return name(obj.children[0])
    label = env.new_temp()
    return tree.Name(label)


def move_exp(obj):
    dst = build_IR_tree_exp(obj.children[0])
    src = build_IR_tree_exp(obj.children[1])
    return tree.Move(dst, src)


def nil_exp(obj):
    return tree.Const(0, 'ex')


def call_exp(obj):
    fun_entry = env.look(_venv, '_func_'+obj.children[0])
    if not fun_entry:
        error(obj.pos, "call error, no such function:", obj.children[0])
        return []
    i = 0
    field = []
    if len(obj.children[1]) == len(fun_entry[2]):
        while i<len(obj.children[1]):
            item = build_IR_tree_exp(obj.children[1][i])
            #类型检查
            field.append(item)
            i+=1
    elif len(obj.children[1]) <= len(fun_entry[2]):
        error(obj.pos, "call error, function except more arguments :", obj.children[0])
    else:
        error(obj.pos, "call error, function except less arguments :", obj.children[0])

    # return tree.Call([fun_entry[0], fun_entry[1]], field)
    fr = frame.get_frame_by_name(fun_entry[0], fun_entry[1])
    print(fr['formals'])
    return tree.Call(
        tree.Name(fun_entry[1]),
        [fr['formals'], field]
    )


def seq_exp(obj):
    r = []
    for item in obj.children[0]:
        r.append(build_IR_tree_exp(item))
    return ir_seq_list(r)


def label(lab):
    return tree.Label(lab)


def name(lab):
    return tree.Name(lab)


def to_condition(obj, t, f):
    if(obj.__class__.__name__ == 'SimpleVar'):
        return tree.Cjump(['!='], build_IR_tree_exp(obj),
                          tree.Const('0', 'ex'), name(t), name(f), 'ex')
        return []
    elif (obj.__class__.__name__ == 'Binop'):
        return tree.Cjump([obj.children[1]], build_IR_tree_exp(obj.children[0]),
                          build_IR_tree_exp(obj.children[2]), name(t), name(f), 'ex')
    else:
        return tree.Cjump(['!='], build_IR_tree_exp(obj),
                          tree.Const('0', 'ex'), name(t), name(f, ), 'ex')


def if_then_else_exp(obj):
    t = env.new_label()
    f = env.new_label()
    done = env.new_label()
    result = env.new_temp()

    r = []
    r.append(to_condition(obj.children[0], t, f))

    r.append(label(t))
    r.append(tree.Move(tree.Mem(result), build_IR_tree_exp(obj.children[1])))
    r.append(tree.Jump(name(done), [done]))

    r.append(label(f))
    r.append(tree.Move(tree.Mem(result), build_IR_tree_exp(obj.children[2])))
    r.append(label(done))
    s = ir_seq_list(r)
    e = tree.Temp(result, 'ex')
    return tree.Eseq(s, e, 'ex')


def if_then_exp(obj):
    t = env.new_label()
    f = env.new_label()

    r = []
    r.append(to_condition(obj.children[0], t, f))
    r.append(label(t))
    r.append(build_IR_tree_exp(obj.children[1]))
    r.append(label(f))

    return ir_seq_list(r)


def while_exp(obj):
    start = env.new_label()
    loop = env.new_label()
    done = env.new_label()

    r = []
    r.append(label(start))
    r.append(to_condition(obj.children[0], loop, done))
    r.append(label(loop))
    r.append(build_IR_tree_exp(obj.children[1]))
    r.append(tree.Jump(name(start), [start]))
    r.append(label(done))
    return ir_seq_list(r)


def for_exp(obj):
    start = env.new_label()
    loop = env.new_label()
    done = env.new_label()

    env.begin_scope(_venv)
    access = [_level, frame.alloc_local(frame.get_frame(_level), [True])]
    env.enter(_venv, '_var_' + obj.children[0], [access, 'TY_INT'])
    var = frame.expr(access[1], frame.fp())

    r = []
    r.append(tree.Move(var, build_IR_tree_exp(obj.children[1])))
    r.append(label(start))
    r.append(tree.Cjump(['<='], var, build_IR_tree_exp(obj.children[2]), name(loop), name(done)))
    r.append(label(loop))
    r.append(build_IR_tree_exp(obj.children[3]))
    r.append(tree.Move(var, tree.Binop('+', var, tree.Const(1))))
    r.append(tree.Jump(name(start), [start]))
    r.append(label(done))

    env.end_scope(_venv)
    return ir_seq_list(r)


def break_exp(obj):
    return []


def simple_var(obj):
    # return tree.Mem(obj.children[0], 'ex')
    var = env.look(_venv, '_var_'+obj.children[0])
    if not var:
        error(obj.pos, 'variable not declare :', obj.children[0])
        return []
    return frame.expr(var[0][1], frame.fp())


def array_create(obj):
    # print(obj)
    t = env.look(_tenv, obj.children[0])
    if not t:
        error(obj.pos, 'no such type :', obj.children[0])
    if t[0] != 'TY_ARRAY':
        error(obj.pos, 'type is not array :', obj.children[0])
    size = build_IR_tree_exp(obj.children[1])
    init = build_IR_tree_exp(obj.children[2])

    return tree.Call(tree.Name("__arrayCreate__"), [size, init])


def array_var(obj):
    # print(obj)
    var = build_IR_tree_exp(obj.children[0])
    # print(to_list(var))
    sub = build_IR_tree_exp(obj.children[1])
    # 类型检查,var是否为array，init是否为int
    return tree.Mem(tree.Binop('+', var,
                               tree.Binop('*', sub,
                                          tree.Const(frame.WORD_SIZE))))


def record_create(obj):
    # print(obj)
    type = env.look(_tenv, obj.children[0])
    addr = tree.Temp(env.new_temp())

    if not type:
        error(obj.pos, 'no such type :', obj.children[0])
    if type[0] != 'TY_RECORD':
        error(obj.pos, 'type is not record :', obj.children[0])
    size = len(type[1])
    if len(obj.children[1]) != size:
        error(obj.pos, 'need %d items, but give %d in record:' % (len(obj.children[1]), size), obj.children[0])

    i = 0
    record = []
    while i < size:
        index = find_record_index(type[1], obj.children[1][i].children[0])
        value = build_IR_tree_exp(obj.children[1][i])
        location = tree.Binop('+', addr, tree.Const(index*frame.WORD_SIZE))
        record.append(tree.Move(tree.Mem(location), value))
        i += 1

    alloc = tree.Call(tree.Name("__recordCreate__"), [size])
    r = [tree.Move(addr, alloc)] + record
    return tree.Eseq(ir_seq_list(r), addr)


def find_record_index(l, var):
    for item in l:
        if item[0] == var:
            return l.index(item)
    return None


def field_create(obj):
    return build_IR_tree_exp(obj.children[1])


def record_var(obj):
    t = env.look(_venv, '_var_'+obj.children[0].children[0])
    if not t:
        error(obj.pos, 'no such variable :', obj.children[0])
    elif t[1][0] != 'TY_RECORD':
        error(obj.pos, 'variable is not record :', obj.children[0])

    index = find_record_index(t[1][1], obj.children[1])

    return tree.Mem(tree.Binop('+', build_IR_tree_exp(obj.children[0]),
                    tree.Binop('*', tree.Const(index), tree.Const(frame.WORD_SIZE))))


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
    'Subscript': array_var,
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
              [_level+1, l1, ['TY_STRING'], 'TY_INT'])

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
    print("------------------")
    return r


def error(pos, msg, token):
    print("At (%d, %d) %s %s" % (pos[0], pos[1], msg, token))


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
