import pprint
HT_SIZE = 773


def empty():
    tab = {
        'top' : [],
        'table' : [[]]*HT_SIZE
    }
    return tab


def enter(tab, key, value):
    index = hash(key) % HT_SIZE
    item = {
        'key': key,
        'value': value,
        'prev': tab['top']
    }
    if(tab['table'][index] == []):
        tab['table'][index] = [ item ]
    else:
        tab['table'][index].append(item)
    tab['top'] = tab['table'][index][-1]
    return index


def look(tab, key):
    index = hash(key) % HT_SIZE
    for item in tab['table'][index][::-1]:
        if(item['key'] == key):
            return item['value']
    return None


def pop(tab):
    if(tab['top'] == []):
        return None
    index = hash(tab['top']['key']) % HT_SIZE
    tab['top'] = tab['top']['prev']
    return tab['table'][index].pop()


if __name__ == '__main__':
    t = empty()
    enter(t, 2, 2)
    enter(t, 'aa', 'aaaaaaaaaaa')
    enter(t, 'my', 'mymymymymymy')
    enter(t, 'mm', 'mmmmmmmmmmmmmmmmm')
    enter(t, 'aa', 'mmmmmmmmmmmmmmmmm')
    print('------------------------')
    # pprint.pprint(t['top'])
    for item in t['table']:
        if (item != []):
            pprint.pprint(item)

    print('------------------------')
    a = look(t, 'aa')
    print(a)

    print('------------------------')
    b = pop(t)
    pprint.pprint(b)
    a = look(t, 'aa')
    print(a)

    print('------------------------')
    b = pop(t)
    pprint.pprint(b)
    a = look(t, 'mm')
    print(a)