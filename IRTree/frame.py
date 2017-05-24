import IRTree.tree as tree
import IRTree.env as env
import pprint

WORD_SIZE = 4
_level = []
_fp = None
_rv = None


def new_level_item(level, name, boolList):
    global _level
    if len(_level) == level:
        _level.append([])
    fr = frame(name, boolList)
    _level[level].append(fr)
    return _level[level]


def get_level(level):
    new_level_item(level, env.new_label(), [])
    return _level[level]


def get_frame(level):
    return _level[level][-1]


def get_frame_by_name(level, name):
    for item in _level[level]:
        if item['name'] == name:
            return item
    return None


def frame(name, formals):
    i = 0
    form = []
    for item in formals:
        form.append(['InFrame',i*WORD_SIZE])
        i += 1
    return {
        'name' : name,
        'formals' : form,
        'locals' : [],
        'localNum' : 0
    }


def fp():
    global _fp
    if _fp == None:
        _fp = env.new_temp()
    return _fp


def fv():
    global _rv
    if _rv == None:
        _rv = env.new_temp()
    return _rv


def expr(access, fp):
    if access[0] == 'InFrame':
        return tree.Mem(tree.Binop('+', tree.Temp(fp), tree.Const(access[1])))


def alloc_local(frame, escape):
    if escape:
        access = ['InFrame',(-1-frame['localNum'])*WORD_SIZE]
        frame['localNum'] += 1
    else:
        access = ['InReg', env.new_temp()]
    frame['locals'].append(access)
    return access

if __name__ == '__main__':
    new_level_item(0, 'L0', [True,True])
    new_level_item(0, 'L2', [True,True])
    new_level_item(1, 'L1', [True,True])
    pprint.pprint(_level[0])
    print('-----------------------')
    pprint.pprint(get_frame(0))
    print('-----------------------')
    pprint.pprint(get_frame(1))