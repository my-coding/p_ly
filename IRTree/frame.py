import IRTree.tree as tree
import IRTree.env as env

WORD_SIZE = 4;
_fp = None
_fv = None

def get_outermost():
    fr = frame(env.new_label(), ['str'])
    return {
        'parent': None,
        'frame': fr,
        'formals': ['str'],
        'local': None,
    }

def frame(name, formals):
    i = 0
    form = []
    for item in formals:
        form.append(['InFrame',i*WORD_SIZE])
        i += 1
    return {
        'name' : name,
        'formals' : form,
        'local' : [],
        'localNum' : 0
    }


def fp():
    if (_fp == None):
        _fp = temp.new_temp_item()
    return _fp


def fv():
    if (_fv == None):
        _fv = temp.new_temp_item()
    return _fv


def expr(access, fp):
    if(access[0] == 'InFrame'):
        return tree.Mem(tree.Binop('+', tree.Temp(fp), tree.Const(access[1])))


def alloc_local(frame, escape):
    if(escape):
        access = ['InFrame',(-1-frame['numLocal'])*WORD_SIZE]
        frame['numLocal'] += 1
    else:
        access = ['InReg', temp.new_temp_item()]
    frame[local].append(access)
    return access