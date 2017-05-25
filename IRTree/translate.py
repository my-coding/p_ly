import IRTree.tree as tree
import IRTree.env as env

def un_ex(obj):
    if obj.kind == 'ex':
        return obj
    elif obj.kind == 'un':
        return tree.Eseq(
            obj, tree.Const(0)
        )
    elif obj.kind == 'cx':
        temp = env.new_temp()
        t = env.new_temp()
        f = env.new_temp()
        return tree.Eseq(
            obj, tree.Const(1)  # 先这样
        )
    else:
        print("error kind of IRtree")
