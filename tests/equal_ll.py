#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from psllp import LLParser
from pslrp import Grammar, LRToken


def empty_func(new, old):
    return None


def meet_s_abb_2(new, old):
    # S -> A b {<this>} B
    new['B.in'] = new['A.num']


def meet_s_abb_3(new, old):
    # S -> A b B {<this>}
    if new['B.num'] == 0:
        print('Accepted!')
    else:
        print('Refused!')


def meet_a_aa_2(new, old):
    # A -> a A {<this>}
    old['A.num'] = new['A.num'] + 1


def meet_a_0(new, old):
    # A -> <empty> {<this>}
    old['A.num'] = 0


def meet_b_ab_1(new, old):
    # B -> a {<this>} B
    new['B.in'] = old['B.in']


def meet_b_ab_2(new, old):
    # B -> a B {<this>}
    old['B.num'] = new['B.num'] - 1


def meet_b_bb_1(new, old):
    # B -> b {<this>} B
    new['B.in'] = old['B.in']


def meet_b_bb_2(new, old):
    # B -> b B {<this>}
    old['B.num'] = new['B.num']


def meet_b_0(new, old):
    # B -> <empty> {<this>}
    old['B.num'] = old['B.in']


if __name__ == '__main__':
    g = Grammar(['a', 'b'])
    g.add_prod('S', ['A', 'b', 'B'], [empty_func, empty_func, meet_s_abb_2, meet_s_abb_3])
    g.add_prod('A', ['a', 'A'], [empty_func, empty_func, meet_a_aa_2])
    g.add_prod('A', [], [meet_a_0])
    g.add_prod('B', ['a', 'B'], [empty_func, meet_b_ab_1, meet_b_ab_2])
    g.add_prod('B', ['b', 'B'], [empty_func, meet_b_bb_1, meet_b_bb_2])
    g.add_prod('B', [], [meet_b_0])
    g.set_start()
    print(str(g))
    p = LLParser(g)
    # count the number of 'a' between
    # the first 'b' in the tokens and
    # accept when equals else refuse
    s = ['a', 'b', 'a', 'b', '$end']
    s = [LRToken(each) for each in s]
    p.parse(s)
    s = ['a', 'b', 'a', 'a', '$end']
    s = [LRToken(each) for each in s]
    p.parse(s)
