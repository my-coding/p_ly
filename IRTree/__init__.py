import IRTree.tree as tree
import IRTree.env as env
import IRTree.frame as frame
import pprint as pp

_outermost = 0
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
    type = env.look(_tenv, obj.children[0])
    if (obj.children[1] == None):
        type = 'unknown'            # 换成表达式对应的type
    elif(not type):
        error(obj.pos, "variable type error, no shch type :", obj.children[1])
        return []
    r = tree.Move(tree.Mem(obj.children[0]), build_IR_tree_exp(obj.children[2]))
    env.enter(_venv, '_var_'+obj.children[0], type)
    return r

# FunDec
# name fieldDec type [exp]
def fun_dec(obj):
    if(env.look(_tenv, '_func_'+obj.children[0])):
        error(obj.pos, "function redefined :", obj.children[0])
        return []

    fun_label = env.new_label()
    formals = para_list(obj.children[1])
    if obj.children[2] is None:
        result_type = 'TY_VOID'
    else:
        result_type = obj.children[2]
    env.enter(_venv, '_func_'+obj.children[0], [fun_label, formals, result_type])
    fieldList = []
    for item in obj.children[1]:
        if (item != []):
            fieldList+=build_IR_tree_dec(item)
    return ['function', label(fun_label), [fieldList], build_IR_tree_exp(obj.children[3])]


def para_list(obj):
    r = []
    for item in obj:
        r.append([item.children[0], item.children[1]])
    return r


def field_dec(obj):
    return [obj.children[0], obj.children[1]]


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
    r = []
    for dec in obj.children[0]:
        for item in dec:
            dec_r = build_IR_tree_dec(item)
            if(dec_r != []):
                r.append(dec_r)
    for exp in obj.children[1]:
        r.append(build_IR_tree_exp(exp))
    return ir_seq_list(r)


def const_exp(obj):
    return tree.Const(obj.children[0], 'ex')


def binop_exp(obj):
    o = obj.children[1]
    e1 = build_IR_tree_exp(obj.children[0])
    e2 = build_IR_tree_exp(obj.children[2])
    return tree.Binop(o, e1, e2, 'ex')


def string_exp(obj):
    return name(obj.children[0])


def move_exp(obj):
    dst = build_IR_tree_exp(obj.children[0])
    src = build_IR_tree_exp(obj.children[1])
    return tree.Move(dst, src)


def mem_exp(obj):
    return tree.Mem(obj.children[0], 'ex')


def nil_exp(obj):
    return tree.Const(0, 'ex')


def call_exp(obj):
    f = name(obj.children[0])
    l = []
    for item in obj.children[1]:
        l.append(build_IR_tree_exp(item))
    return tree.Call(f, l, 'ex')


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
    var = ['fr', obj.children[1]]        # 在栈帧里

    r = []
    r.append(tree.Move(tree.Mem(var), build_IR_tree_exp(obj.children[2])))
    r.append(label(start))
    r.append(tree.Cjump(['<='], var, build_IR_tree_exp(obj.children[2]), name(loop), name(done)))
    r.append(label(loop))
    r.append(build_IR_tree_exp(obj.children[3]))
    r.append(tree.Move(var, tree.Binop('+', var, tree.Const(1))))
    r.append(tree.Jump(name(start), [start]))
    r.append(label(done))
    return ir_seq_list(r)


expression = {
    'Program': program,
    'LetExp': let_exp,

    'IntLit': const_exp,
    'StringLit': string_exp,
    'NilLit': nil_exp,
    'SimpleVar': mem_exp,     # 要改为栈帧
    'Binop': binop_exp,
    'Assign': move_exp,
    'Call': call_exp,
    'SeqExp': seq_exp,
    'IfThen': if_then_exp,
    'IfThenElse': if_then_else_exp,
    'WhileExp': while_exp,
    'ForExp': for_exp,
}


def build_IR_tree_exp(obj):
    return expression.get(obj.__class__.__name__, 'Error')(obj)


def level(parent, name, formals):
    return 0


def init_env():
    env.enter(_venv, env.symbol('print'),
              [frame.get_outermost(), ['TY_STRING'], 'TY_INT'])


def build_IR_tree(obj):
    init_env()
    r = build_IR_tree_exp(obj)
    print("-------tenv-------")
    env.print_table(_tenv)
    print("-------venv-------")
    env.print_table(_venv)
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
