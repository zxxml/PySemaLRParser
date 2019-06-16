#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from pslrp import CLRTable, Grammar, LRParser, LRToken


def meet_s_mabb(sym, args, stack):
    # expression: S -> M A b B
    if args[3].value == 0:
        sym.value = True
    else:
        sym.value = False


def meet_a_aa(sym, args, stack):
    # expression: A -> A a
    sym.value = args[0].value - 1


def meet_a(sym, args, stack):
    # expression: A -> <empty>
    sym.value = stack[-1].value


def meet_b_ba(sym, args, stack):
    # expression: B -> B a
    sym.value = args[0].value - 1


def meet_b_bb(sym, args, stack):
    # expression: B -> B b
    sym.value = args[0].value


def meet_b(sym, args, stack):
    # expression: B -> <empty>
    sym.value = stack[-2].value


def meet_m(sym, args, stack):
    # expression: M -> <empty>
    sym.value = 3


if __name__ == '__main__':
    g = Grammar(['a', 'b'])
    g.add_prod('S', ['M', 'A', 'b', 'B'], meet_s_mabb)
    g.add_prod('A', ['A', 'a'], meet_a_aa)
    g.add_prod('A', [], meet_a)
    g.add_prod('B', ['B', 'a'], meet_b_ba)
    g.add_prod('B', ['B', 'b'], meet_b_bb)
    g.add_prod('B', [], meet_b)
    g.add_prod('M', [], meet_m)
    g.set_start()
    print(str(g))
    t = CLRTable(g)
    # t = SLRTable(g)
    p = LRParser(t)
    # count the number of 'a'
    # return if the num is 3
    s = ['a', 'b', 'a', 'b', '$end']
    s = [LRToken(each) for each in s]
    print(p.parse(s))
    s = ['a', 'b', 'a', 'a', '$end']
    s = [LRToken(each) for each in s]
    print(p.parse(s))
