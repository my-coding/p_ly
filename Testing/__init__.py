# coding=utf-8
"""
This package is used for testing.
"""

import LexAndYaccParser
import ATree
import IRTree
import pprint


def run_test():
    with open("merge.tig") as file:
        code = file.read()
    tree = LexAndYaccParser.build_abstract_syntax_tree(code)
    pprint.pprint(ATree.to_list(tree), indent = 2)
    print('------------------------------------------------')
    ir_tree = IRTree.build_IR_tree(tree)
    pprint.pprint(IRTree.to_list(ir_tree), indent = 4)


if __name__ == '__main__':
    run_test()
