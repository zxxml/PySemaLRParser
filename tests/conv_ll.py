#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from psllp import LLParser
from pslrp import Grammar, LRToken


def empty_func(new, old):
    return None


def meet_s_n_1(new, old):
    print('meet_s_n_1')
    # S -> dot {<this>} N
    new['N.len'] = 1


def meet_s_n_2(new, old):
    print('meet_s_n_2')
    # S -> dot N {<this>}
    print(new['N.val'])


def meet_n_bn_0(new, old):
    print('meet_n_bn_0')
    # N -> {<this>} B N
    new['B.len'] = old['N.len']


def meet_n_bn_1(new, old):
    print('meet_n_bn_1')
    # N -> B {<this>} N
    new['N.len'] = old['N.len'] + 1


def meet_n_bn_2(new, old):
    print('meet_n_bn_2')
    # N -> B N {<this>}
    old['N.val'] = new['B.val'] + new['N.val']


def meet_n_0(new, old):
    print('meet_n_0')
    # N -> <empty> {<this>}
    old['N.val'] = 0


def meet_b_0_1(new, old):
    print('meet_b_0_1')
    # B -> 0 {<this>}
    old['B.val'] = 0


def meet_b_1_1(new, old):
    print('meet_b_1_1')
    # B -> 1 {<this>}
    old['B.val'] = 2 ** -old['B.len']


if __name__ == '__main__':
    g = Grammar(['dot', '0', '1'])
    g.add_prod('S', ['dot', 'N'], [empty_func, meet_s_n_1, meet_s_n_2])
    g.add_prod('N', ['B', 'N'], [meet_n_bn_0, meet_n_bn_1, meet_n_bn_2])
    g.add_prod('N', [], [meet_n_0])
    g.add_prod('B', ['0'], [empty_func, meet_b_0_1])
    g.add_prod('B', ['1'], [empty_func, meet_b_1_1])
    g.set_start()
    print(str(g))
    p = LLParser(g)
    s = ['dot', '1', '0', '1', '$end']
    s = [LRToken(each) for each in s]
    p.parse(s)
