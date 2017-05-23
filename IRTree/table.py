import pprint
HT_SIZE = 773


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
                print(i['key'], end=" ")
                print(i['value'], end=" ")
            print(' ')


if __name__ == '__main__':
    t = empty()
#     enter(t, 2, 2)
#     enter(t, 'aa', 'aaaaaaaaaaa')
#     enter(t, 'my', 'mymymymymymy')
#     enter(t, 'mm', 'mmmmmmmmmmmmmmmmm')
#     enter(t, "id([1,2,3])", '123')
#     enter(t, "id"+"([1,2,3])", 'last')
#
# # 打印整张表
#     print('------------------------')
#     print_table(t)
# # 查询
#     print('------------------------')
#     a = look(t, 'aa')
#     print(a)
#     b = look(t, 'aaa')
#     print(b)
# # 删除最后一个插入项
#     print('------------------------')
#     b = pop(t)
#     print(b)
#     print('------------------------')
#     print_table(t)
#
# # 测试所有的pop
#     print('------------------------')
    enter(t, 'a', 'a')
    enter(t, 'b', 'b')
    enter(t, 'c', 'c')
    enter(t, 'a', 'test')
    print_table(t)
    print(pop(t))
    print(pop(t))
    print(pop(t))
    print(pop(t))
