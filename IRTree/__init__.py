class Const:
    def __init__(self, obj):
        self.children = ['CONST', obj.children[0]]


class Name:
    def __init__(self, obj):
        self.children = [s, e]


class Temp:
    def __init__(self, obj):
        self.children = ['TEMP', obj.children[0]]


class Binop:
    def __init__(self, obj):
        op = obj.children[1]
        left = build_stmt(obj.children[0])
        right = build_stmt(obj.children[2])
        self.children =  [op, left, right]


class Mem:
    def __init__(self, obj):
        self.children = []


class Call:
    def __init__(self, obj):
        self.children = []


class Cjump:
    def __init__(self, obj):
        if (obj.children[0].__class__.__name__ == 'Binop'):
            o = [obj.children[0].children[1]]
            e1 = build_stmt(obj.children[0].children[0])
            e2 = build_stmt(obj.children[0].children[2])
        else:
            o = ['<>']
            e1 = build_stmt(obj.children[0])
            e2 = ['CONST', 0]
        t = build_stmt(obj.children[1])
        if (len(obj.children) > 2):
            f = build_stmt(obj.children[2])
        else:
            f = []
        self.children = ['CJUMP', o, e1, e2, t, f]


class Seq:
    def __init__(self, obj):
        if (len(obj) > 2):
            tmp = obj.copy()
            tmp.pop()
            s1 = Seq(tmp)
        else:
            s1 = build_stmt(obj[0])
        s2 = build_stmt(obj[len(obj)-1])
        self.children = ['SEQ', s1, s2]


class Eseq:
    def __init__(self, obj):
        tmp = obj.children[0].copy()
        tmp.pop()
        s = Seq(tmp)
        e = build_stmt(obj.children[0][len(obj.children[0])-1])
        self.children = ['ESEQ', s, e]


class Move:
    def __init__(self, obj):
        t = build_stmt(obj.children[0])
        e = build_stmt(obj.children[1])
        self.children = ['MOVE', t, e]


class Exp:
    def __init__(self, obj):
        self.children = []


class Jump:
    def __init__(self, obj):
        self.children = []


class Label:
    def __init__(self, obj):
        self.children = []


choose = {
    'IntLit' : Const,
    'SimpleVar' : Temp,
    'Binop': Binop,

    'Assign' : Move,
    'SeqExp' : Eseq,
    'IfThen' : Cjump,
    'IfThenElse' : Cjump,
}


def build_stmt(item):
    return choose.get(item.__class__.__name__,'Error')(item)


def build_IR_tree(obj):
    IR_tree_list = []
    for item in obj:
        IR_tree_list.append(build_stmt(item))
    return IR_tree_list


def to_list(obj):
    try:
        return [to_list(item) for item in obj.children]
    except AttributeError:
        if type(obj) is list:
            return [to_list(item) for item in obj]
        else:
            return obj


def traversal(node):
    if (type(node) == list):
        for a in node:
            traversal(a)
    elif(type(node) == str or type(node) == int):
        print(node)
    else:
        # print('--------')
        print(node.__class__.__name__)
        for item in node.children:
            traversal(item)


def test(obj):
    # print(obj.__class__.__name__)
    # print(obj.children[0].__class__.__name__)
    # print(obj.children[0].children[0])
    # for item in obj.children[0].children[1]:
    #     print(item.children[0].children[0])
    # # print(obj.children[0].children[1][0].children[0].children[0])
    print(obj.children[0].children[1][5].__class__.__name__)
    print(obj.children[0].children[1][5].children[0].__class__.__name__)
    print(obj.children[0].children[1][5].children[1].__class__.__name__)
    print(len(obj.children[0].children[1][5].children))
    print(obj.children[0].children[1][6].__class__.__name__)
    print(obj.children[0].children[1][6].children[0].__class__.__name__)
    print(obj.children[0].children[1][6].children[0].children[1])
    print(obj.children[0].children[1][6].children[1].__class__.__name__)
    # print(obj.children[0].children[1][4].children[0][0].__class__.__name__)
    # print(obj.children[0].children[1][4].children[1].children[0])

