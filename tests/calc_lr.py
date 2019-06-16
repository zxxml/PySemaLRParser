#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from collections import defaultdict

from pslrp import CLRTable, Grammar, LRParser, LRToken

termlist = ['+', '*', '(', ')', 'd']
namedict = defaultdict()


def meet_s_e(sym, args, stack):
    # production: S -> E
    sym.value = args[0].value


def meet_e_ept(sym, args, stack):
    # production: E -> E + T
    sym.value = args[0].value + args[2].value


def meet_e_t(sym, args, stack):
    # production: E -> T
    sym.value = args[0].value


def meet_t_tmf(sym, args, stack):
    # production: T -> T * F
    sym.value = args[0].value * args[2].value


def meet_t_f(sym, args, stack):
    # production: T -> F
    sym.value = args[0].value


def meet_f_beb(sym, args, stack):
    # production: F -> ( E )
    sym.value = args[1].value


def meet_f_d(sym, args, stack):
    # production: F -> d
    sym.value = args[0].value


if __name__ == '__main__':
    g = Grammar(termlist)
    g.add_prod('S', ['E'], meet_s_e)
    g.add_prod('E', ['E', '+', 'T'], meet_e_ept)
    g.add_prod('E', ['T'], meet_e_t)
    g.add_prod('T', ['T', '*', 'F'], meet_t_tmf)
    g.add_prod('T', ['F'], meet_t_f)
    g.add_prod('F', ['(', 'E', ')'], meet_f_beb)
    g.add_prod('F', ['d'], meet_f_d)
    g.set_start()
    print(str(g))
    t = CLRTable(g)
    # t = SLRTable(g)
    p = LRParser(t)
    s = [LRToken('d', 3),
         LRToken('*'),
         LRToken('('),
         LRToken('d', 5),
         LRToken('+'),
         LRToken('d', 4),
         LRToken(')'),
         LRToken('$end')]
    print(p.parse(s))
