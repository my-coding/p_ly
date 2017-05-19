import IRTree.tree as tree
import IRTree.temp as temp
import pprint as pp


def seq_item(s1,s2):
    return {
        'exp' : tree.Seq(s1, s2),
        'kind' : 'nx'
    }


def ir_seq(seq_list):
    l = len(seq_list)
    if (l==0):
        return []
    if (l==1):
        return seq_list[0]
    if (l==2):
        return seq_item(seq_list[0], seq_list[1])
    t = seq_list.pop()
    return seq_item(ir_seq(seq_list), t)


def program(obj):
    return build_IR_tree(obj.children[0])


def let_exp(obj):
    r = []
    for exp in obj.children[1]:
        r.append(build_IR_tree(exp))
    return ir_seq(r)


def const_exp(obj):
    return {
        'exp' : tree.Const(obj.children[0]),
        'kind' : 'ex'
    }


choose = {
    'Program': program,
    'LetExp' : let_exp,
    'IntLit' : const_exp,
}


def build_IR_tree(obj):
    # return choose.get(obj.__class__.__name__, 'Error')(obj)
    a = choose.get(obj.__class__.__name__, 'Error')(obj)
    # print(a.__class__.__name__)
    return a


def to_list(obj):
    try:
        r = [ obj['exp'].children[0] ]
        i = 1
        while (i < len( obj['exp'].children)):
            r.append(to_list(obj['exp'].children[i]))
            i+=1
        return r
    except TypeError or AttributeError:
        if type(obj) is dict:
            return [to_list(obj['exp'])]
        else:
            return obj


def test(obj):
    print(obj.__class__.__name__)
    print(obj.children[0].__class__.__name__)
    print(obj.children[0].children[1][0].children[0])


if __name__ == '__main__':
    a = ir_seq([1,2,3,4,5,6])
    print(to_list(a))