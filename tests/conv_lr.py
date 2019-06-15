#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from collections import defaultdict

from pslrp import CLRTable, Grammar, LRParser, LRToken

termlist = ['dot', '0', '1']
namedict = defaultdict()


def meet_s_dmn(sym, args, stack):
    # S -> dot M N, here assign it
    # and return, or you can print
    sym.value = args[2].value


def meet_n_bpn(sym, args, stack):
    # N -> B P N, P is used to insert a action(and do it)
    # only do the last action, B and P will do the others
    sym.value = args[0].value + args[2].value


def meet_n(sym, args, stack):
    # N -> <empty>, sym is N
    # just assign 0 to the sym
    sym.value = 0


def meet_b_0(sym, args, stack):
    # B -> 0, assign 0 to B.value
    sym.value = int(args[0].name)


def meet_b_1(sym, args, stack):
    # B -> 1, assign 2^(-len) to B
    sym.value = 2 ** -namedict['B']


def meet_m(sym, args, stack):
    # M -> <empty>, to insert a action
    # assign 1 to B.length(namedict['B'])
    namedict['B'] = 1


def meet_p(sym, args, stack):
    # P -> <empty>, to insert a action
    # increase B.length(namedict['B'])
    namedict['B'] += 1


if __name__ == '__main__':
    g = Grammar(termlist)
    g.add_prod('S', ['dot', 'M', 'N'], meet_s_dmn)
    g.add_prod('N', ['B', 'P', 'N'], meet_n_bpn)
    g.add_prod('N', [], meet_n)
    g.add_prod('B', ['0'], meet_b_0)
    g.add_prod('B', ['1'], meet_b_1)
    g.add_prod('M', [], meet_m)
    g.add_prod('P', [], meet_p)
    g.set_start()
    print(str(g))
    t = CLRTable(g)
    # t = SLRTable(g)
    p = LRParser(t)
    s = ['dot', '1', '0', '1', '$end']
    s = [LRToken(each) for each in s]
    print(p.parse(s))
