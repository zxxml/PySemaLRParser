#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from collections import defaultdict

from pslrp import CLRTable, Grammar, LRParser, LRToken

termlist = ['dot', '0', '1']
namedict = defaultdict()


def root(sym, args, stack):
    # S -> dot M N, here assign it
    # and return, or you can print
    sym.value = args[2].value


def meet_nb(sym, args, stack):
    # N -> N P B, P is used to insert a action(and do it)
    # only do the last action, N and P will do the others
    sym.value = args[0].value + args[2].value


def meet_b(sym, args, stack):
    # N -> B, just assign it
    sym.value = args[0].value


def meet_0(sym, args, stack):
    # B -> 0, assign 0 to B.value
    sym.value = int(args[0].name)


def meet_1(sym, args, stack):
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
    g.add_prod('S', ['dot', 'M', 'N'], root)
    g.add_prod('N', ['N', 'P', 'B'], meet_nb)
    g.add_prod('N', ['B'], meet_b)
    g.add_prod('B', ['0'], meet_0)
    g.add_prod('B', ['1'], meet_1)
    g.add_prod('M', [], meet_m)
    g.add_prod('P', [], meet_p)
    for each in g.prodlist:
        print(each)
    g.set_start()
    g.first_set()
    g.follow_set()
    g.build_lr_items()
    t = CLRTable(g)
    # print(t.clr_items())
    t.clr_table()
    # print(t.actiondict)
    # print( t.gotodict)
    # t = SLRTable(g)
    # t.slr_table()
    p = LRParser(t)
    s = ['dot', '1', '0', '1', '$end']
    s = [LRToken(each) for each in s]
    print(p.parse(s))
