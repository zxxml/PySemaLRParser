#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from collections import defaultdict

from pslrp import CLRTable, Grammar, LRParser, LRToken

termlist = ['+', '-', 'num']
namedict = defaultdict()


def meet_e_tar(sym, args, stack):
    # expression: E -> T A R
    sym.value = args[2].value


def meet_r_ptbr(sym, args, stack):
    # expression: R -> + T B R
    sym.value = args[3].value


def meet_r_mtcr(sym, args, stack):
    # expression: R -> - T C R
    sym.value = args[3].value


def meet_r(sym, args, stack):
    # expression: R -> <empty>
    sym.value = stack[-1].value


def meet_t_n(sym, args, stack):
    # expression: T -> num
    sym.value = args[0].value


def meet_a(sym, args, stack):
    # expression: A -> <empty>
    sym.value = stack[-1].value


def meet_b(sym, args, stack):
    # expression: B -> <empty>
    sym.value = stack[-3].value + stack[-1].value


def meet_c(sym, args, stack):
    # expression: C -> <empty>
    sym.value = stack[-3].value - stack[-1].value


if __name__ == '__main__':
    g = Grammar(termlist)
    g.add_prod('E', ['T', 'A', 'R'], meet_e_tar)
    g.add_prod('R', ['+', 'T', 'B', 'R'], meet_r_ptbr)
    g.add_prod('R', ['-', 'T', 'C', 'R'], meet_r_mtcr)
    g.add_prod('R', [], meet_r)
    g.add_prod('T', ['num'], meet_t_n)
    g.add_prod('A', [], meet_a)
    g.add_prod('B', [], meet_b)
    g.add_prod('C', [], meet_c)
    g.set_start()
    print(str(g))
    t = CLRTable(g)
    # t = SLRTable(g)
    p = LRParser(t)
    s = [LRToken('num', 3),
         LRToken('+'),
         LRToken('num', 4),
         LRToken('-'),
         LRToken('num', 5),
         LRToken('$end')]
    print(p.parse(s))
