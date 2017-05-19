#exp
class Const:
    def __init__(self, i):
        self.children = ['CONST', i]


class Name:
    def __init__(self, n):
        self.children = ['NAME', n]


class Temp:
    def __init__(self, t):
        self.children = ['TEMP', t]


class Binop:
    def __init__(self, o, e1, e2):
        self.children =  [o, e1, e2]


class Mem:
    def __init__(self, e):
        self.children = ['MEM', e]


class Call:
    def __init__(self, f, l):
        self.children = ['CALL', f, l]


class Eseq:
    def __init__(self, s, e):
        self.children = ['ESEQ', s, e]

# stmt
class Move:
    def __init__(self, dst, src):
        self.children = ['MOVE', dst, src]


class Exp:
    def __init__(self, e):
        self.children = ['EXP', e]


class Jump:
    def __init__(self, e, labels):
        self.children = ['JUMP', e, labels]


class Cjump:
    def __init__(self, o, e1, e2, t, f):
        self.children = ['CJUMP', o, e1, e2, t, f]


class Seq:
    def __init__(self, s1, s2):
        self.children = ['SEQ', s1, s2]


class Label:
    def __init__(self, n):
        self.children = ['LABEL', n]