import pprint
HT_SIZE = 773
_label = 0                        # 静态存储器地址
_temps = 100                      # 临时变量
_symbol = [[]] * HT_SIZE    # 符号列表
_tempList = []                    # 临时变量环境

_mark_scope = 0


def empty():
    tab = {
        'top': [],
        'table': [[]]*HT_SIZE
    }
    return tab


def enter(tab, key, value):
    index = hash(key) % HT_SIZE
    item = {
        'key': key,
        'value': value,
        'prev': tab['top']
    }
    if not tab['table'][index]:
        tab['table'][index] = [item]
    else:
        tab['table'][index].append(item)
    tab['top'] = tab['table'][index][-1]
    return index


def look(tab, key):
    index = hash(key) % HT_SIZE
    for item in tab['table'][index][::-1]:
        if item['key'] == key:
            return item['value']
    return None


def pop(tab):
    if not tab['top']:
        return None
    index = hash(tab['top']['key']) % HT_SIZE
    tab['top'] = tab['top']['prev']
    return (tab['table'][index].pop())['key']


def print_table(tab):
    for item in tab['table']:
        if item:
            # print(item[-1]['key'], end=" ")
            # print(item[-1]['value'])
            for i in item:
                pprint.pprint(i['key'])
                pprint.pprint(i['value'])
            print(' ')


# 基本的类型环境、值环境
def base_tenv():
    tab = empty()
    enter(tab, 'int', 'TY_INT')
    enter(tab, 'string', 'TY_STRING')
    return tab


def base_venv():
    tab = empty()
    return tab


# scope
def begin_scope(tab):
    global _mark_scope
    if not _mark_scope:
        _mark_scope = "<__mask__>"
    enter(tab, _mark_scope, None)


def end_scope(tab):
    global _mark_scope
    mask = pop(tab)
    while mask != _mark_scope:
        mask = pop(tab)


# label，在_symbol之中加一项
def new_label():
    global _label
    buf = '%d' % _label
    _label += 1
    return 'L' + symbol(buf)


def symbol(buf):
    global _symbol
    index = hash(buf) % HT_SIZE
    for n in _symbol[index]:
        if n == buf:
            return buf
    if not _symbol[index]:
        _symbol[index] = buf
    else:
        _symbol.append(buf)
    return buf


# temp，在_tempList之中加一项
def new_temp():
    global _temps
    global _tempList
    item = '%d' % _temps
    _temps += 1
    if not _tempList:
        _tempList = temp_empty()
    temp_enter(_tempList, item, item)
    return 'T' + item


# 临时变量操作
def temp_empty():
    return [empty()]


def temp_layerList(over, under):
    return over + under


def temp_enter(l, t, s):
    enter(l[-1], t, s)


def temp_look(l, t):
    for tab in l[::-1]:
        s = look(tab, t)
        if s != None:
            return s
    return None


def print_tableList(l):
    for tab in l[::-1]:
        print('temp table:')
        print_table(tab)


if __name__ == '__main__':
# 测试临时变量环境
    tmp = temp_empty()
    temp_enter(tmp, 'a', 13)
    temp_enter(tmp, 'b', 11)
    begin_scope(tmp[0])
    temp_enter(tmp, 'c', 12)
    temp_enter(tmp, 'd', 10)

    print('---------------')
    print(temp_look(tmp, 'a'))

    print('---------------')
    print_tableList(tmp)

    print('---------------')
    print(new_temp())
    print(new_label())
    end_scope(tmp[0])

    print('---------------')
    print_table(tmp[0])

    print('---------------')
    print_table(base_tenv())
    print_table(base_venv())
