import IRTree.table as Table
_label=0
_temps=100
_symbol=[[]]*Table.HT_SIZE


def newTemp():
    global _temps
    _temps += 1
    item = {'num': _temps}
    t = Table.empty()
    Table.enter(t, id(item), item['num'])
    return item


def label():
    global _label
    _label += 1
    buf = [_label]
    return symnol(buf)


def symnol(buf):
    addr = id(buf)
    index = hash(addr)%Table.HT_SIZE
    for n in _symbol[index]:
        if(n == buf):
            return n
    if(_symbol[index] == []):
        _symbol[index] = buf
    else:
        _symbol.append(buf)
    return buf


def empty():
    return [Table.empty()]


def layerList(over, under):
    return over+under


def enter(l, t, s):
    Table.enter(l[0], t, s)


def look(l, t):
    for tab in l:
        s = Table.look(tab, t)
        if(s != None):
            return s
    return None


if __name__ == '__main__':
    tmp = empty()
    tmp2 = [empty(),empty()]
    enter(tmp, 'a', 10)
    print(len(tmp))
    print(look(tmp, 'a'))
    print(look(tmp, 'b'))