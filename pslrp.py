#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from collections import defaultdict
from contextlib import suppress
from typing import Iterable


class Production:
    def __init__(self, index, name, syms, func=None):
        self.index = index
        self.name = name
        self.syms = syms
        self.func = func
        self.lr_next = None
        self.lr_items = None
        # all symbols in the production
        self.uni_syms = list(set(syms))
        # internal variables
        self._add_count = 0

    def __len__(self):
        return len(self.syms)

    def __str__(self):
        syms = '\40'.join(self.syms)
        return '%s -> %s' % (self.name, syms)

    @property
    def f(self):
        if self.func is not None: return self.func
        return lambda x, y, z: print(x, y, z)


class GramError(Exception):
    def __init__(self, message):
        self.message = message
        self.args = (message,)
        super().__init__(message)


class Grammar:
    def __init__(self, terms):
        self.start = None
        self.prodlist = [None]
        self.proddict = defaultdict(list)
        self.termdict = defaultdict(list)
        self.nontdict = defaultdict(list)
        self.first = defaultdict(list)
        self.follow = defaultdict(list)
        for t in terms: self.termdict[t] = []

    def __len__(self):
        return len(self.prodlist)

    def __getitem__(self, i):
        return self.prodlist[i]

    def add_prod(self, name, syms, func=None):
        if name in self.termdict:
            text = 'Illegal nonterm: %s'
            raise GramError(text % name)
        if name == 'error':
            text = 'Illegal nonterm: %s'
            raise GramError(text % name)
        for i, each in enumerate(syms):
            if not each.isidentifier():
                text = 'Illegal symbol: %s'
                raise GramError(text % each)
        # from now, everything is valid
        # use all info to create a prod
        i = len(self.prodlist)
        for each in syms:
            if each in self.termdict:
                self.termdict[each].append(i)
            else:
                self.nontdict[each].append(i)
        # build a production and update self
        prod = Production(i, name, syms, func)
        self.prodlist.append(prod)
        self.proddict[name].append(prod)

    def set_start(self, start=None):
        if start is None:
            start = self.prodlist[1].name
        if start not in self.nontdict:
            text = 'Illegal start: %s'
            raise GramError(text % start)
        self.prodlist[0] = Production(0, "S'", [start])
        self.nontdict[start].append(0)
        self.start = start

    def get_first(self, syms):
        result = []
        for s in syms:
            can_empty = False
            for f in self.first[s]:
                if f == '<empty>':
                    can_empty = True
                elif f not in result:
                    result.append(f)
            # continue if can empty
            if not can_empty: break
        else:
            # if always can empty
            result.append('<empty>')
        return result

    def first_set(self):
        if not self.first:
            for t in self.termdict:
                self.first[t] = [t]
            been_changed = True
            while been_changed:
                been_changed = False
                for n in self.nontdict:
                    for p in self.proddict[n]:
                        for f in self.get_first(p.syms):
                            if f not in self.first[n]:
                                been_changed = True
                                self.first[n].append(f)
        # after generation
        # return the first
        return self.first

    def follow_set(self, start=None):
        if start is None:
            start = self.start
        if self.follow:
            return self.follow
        if not self.first:
            self.first_set()
        for n in self.nontdict:
            self.follow[n] = []
        # follow(start) contains $end
        self.follow[start] = ['$end']
        been_changed = True
        while been_changed:
            been_changed = False
            for p in self.prodlist[1:]:
                for i, s in enumerate(p.syms):
                    follows_empty = False
                    if s in self.nontdict:
                        # now we have found a vn in a production
                        # get the first set and set the follow set
                        for f in self.get_first(p.syms[i + 1:]):
                            if f == '<empty>':
                                follows_empty = True
                            elif f not in self.follow[s]:
                                been_changed = True
                                self.follow[s].append(f)
                        # if the first set contains empty
                        # or the vn the the last of syms
                        # add follow(p.name) to the follow
                        if follows_empty or i == (len(p.syms) - 1):
                            for f in self.follow[p.name]:
                                if f not in self.follow[s]:
                                    been_changed = True
                                    self.follow[s].append(f)
        # after generation
        # return the follow
        return self.follow

    def build_lr_items(self):
        for p in self.prodlist:
            last, i = p, 0
            p.lr_items = []
            while True:
                if i > len(p):
                    item = None
                else:
                    item = LRItem(p, i)
                    item.lr_after = []
                    item.lr_before = None
                    with suppress(IndexError, KeyError):
                        # lr_after is the list of productions following
                        item.lr_after = self.proddict[item.syms[i + 1]]
                    with suppress(IndexError):
                        # lr_before is the symbol before
                        # if item is the first, the last
                        item.lr_before = item.syms[i - 1]
                last.lr_next = item
                if item is None: break
                p.lr_items.append(item)
                last, i = item, i + 1


class LRItem:
    def __init__(self, prod: Production, lr_index):
        self.prod = prod
        self.lr_index = lr_index
        syms = list(prod.syms)
        syms.insert(lr_index, '.')
        self.syms = tuple(syms)
        self.lr_next = None
        self.lr_after = None
        self.lr_before = None
        # internal variables
        self._add_count = 0

    def __len__(self):
        return len(self.syms)

    def __str__(self):
        syms = '\40'.join(self.syms)
        if not self.syms: syms = '<empty>'
        return '%s -> %s' % (self.name, syms)

    @property
    def index(self):
        return self.prod.index

    @index.setter
    def index(self, index):
        self.prod.index = index

    @property
    def name(self):
        return self.prod.name

    @name.setter
    def name(self, name):
        self.prod.name = name

    @property
    def uni_syms(self):
        return self.prod.uni_syms

    @uni_syms.setter
    def uni_syms(self, uni_syms):
        self.prod.uni_syms = uni_syms

    @property
    def can_reduce(self):
        # whether this item can be reduced
        # or acc if the name is the starter
        return len(self) == self.lr_index + 1


def dumps_items(items: Iterable[LRItem]):
    # it can be also used to dumps
    # goto and closure(just items)
    if items is None: return None
    string = [str(i) for i in items]
    return '\040'.join(string)


def unique_symbols(items: Iterable[LRItem], reverse=False):
    syms = [s for y in items for s in y.uni_syms]
    return tuple(sorted(set(syms), reverse=reverse))


class SLRTable:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.actiondict = {}
        self.gotodict = {}
        # incomplete tables
        self.actioncache = defaultdict(dict)
        self.gotocache = defaultdict(dict)
        self.closcache = defaultdict(int)
        # internal variables
        self._add_count = 0

    @property
    def prodlist(self):
        return self.grammar.prodlist

    @prodlist.setter
    def prodlist(self, v):
        self.grammar.prodlist = v

    def lr0_closure(self, state):
        self._add_count += 1
        # state_i means Ii
        # a set of lr items
        closure = state[:]
        been_changed = True
        while been_changed:
            been_changed = False
            for c in closure:
                for a in c.lr_after:
                    if a._add_count != self._add_count:
                        been_changed = True
                        closure.append(a.lr_next)
                        a._add_count = self._add_count
        return closure

    def lr0_goto(self, state, x):
        # if there is goto cached, just return it
        goto = self.gotocache.get((id(state), x))
        if goto is not None: return goto
        # s is {} if x not in gotocache
        # do remember the default is {}
        s, gs = self.gotocache[x], []
        # we have the state
        # and all the lr_next
        for item in state:
            n = item.lr_next
            if n is not None:
                # x can be vn or vt
                # and we got a goto
                if n.lr_before == x:
                    t = s.get(id(n))
                    if t is None:
                        s[id(n)] = {}
                        t = s[id(n)]
                    s = t
                    gs.append(n)
        goto = s.get('$end')
        if goto is None:
            if gs: goto = self.lr0_closure(gs)
            s['$end'] = goto if gs else []
        self.gotocache[(id(state), x)] = goto
        return goto

    def lr0_items(self):
        closure = [self.lr0_closure([self.grammar.prodlist[0].lr_next])]
        for i, c in enumerate(closure): self.closcache[id(c)] = i
        index = 0  # must use while
        # traverse all unvisited states
        # and generate their goto states
        while index < len(closure):
            c, index = closure[index], index + 1
            # get all the symbols in every prods of c
            syms = unique_symbols(c, reverse=False)
            for s in syms:
                goto = self.lr0_goto(c, s)
                if goto and id(goto) not in self.closcache:
                    self.closcache[id(goto)] = len(closure)
                    closure.append(goto)
        return closure

    def slr_table(self):
        for i, state in enumerate(self.lr0_items()):
            # actiondict[s] = <index>
            # actionprod[s] = <prod>
            # for reduce or accept, <index> is pos
            # for shift, <index> is negetive or zero
            actiondict = {}
            actionprod = {}
            gotodict = {}
            # generate the action table
            # ignore goto in this loop
            for item in state:
                if item.can_reduce:
                    if item.name == "S'":
                        actiondict['$end'] = 0
                        actionprod['$end'] = item
                    else:
                        # the lookaheads of slr is the follow
                        for a in self.grammar.follow[item.name]:
                            if actiondict.get(a) is not None:
                                message = 'Conflict reduce and %s.'
                                raise GramError(message % 'shift')
                            # reverse index(-1, -2, ...)
                            actiondict[a] = -item.index
                            actionprod[a] = item
                else:
                    index = item.lr_index
                    # e.g. S -> a.Sb, s = S
                    s = item.syms[index + 1]
                    if s in self.grammar.termdict:
                        # now we have a shift item
                        goto = self.lr0_goto(state, s)
                        # get the index of goto in all states
                        c = self.closcache.get(id(goto), -1)
                        if c >= 0:
                            actiondict[s] = c
                            actionprod[s] = item
            # already finished the action
            # now generate the goto table
            nontdict = defaultdict()
            for item in state:
                for s in item.uni_syms:
                    if s in self.grammar.nontdict:
                        nontdict[s] = None
            for n in nontdict:
                # do the same thing in shift
                goto = self.lr0_goto(state, n)
                c = self.closcache.get(id(goto), -1)
                if c >= 0:
                    # but no more prod
                    gotodict[n] = c
            self.actiondict[i] = actiondict
            self.gotodict[i] = gotodict


class LRToken:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def __str__(self):
        return self.name


class LRParser:
    def __init__(self, table: SLRTable):
        self.table = table
        self.statestack = None
        self.symbolstack = None

    @property
    def prodlist(self):
        return self.table.prodlist

    @property
    def actiondict(self):
        return self.table.actiondict

    @property
    def gotodict(self):
        return self.table.gotodict

    def restart(self):
        sym = LRToken('$end')
        self.statestack = [0]
        self.symbolstack = [sym]

    def parse(self, tokens):
        self.restart()
        # reassign for convenience
        prodlist = self.prodlist
        actiondict = self.actiondict
        gotodict = self.gotodict
        statestack = self.statestack
        symbolstack = self.symbolstack
        while True:
            next_sym = tokens[0]
            state = statestack[-1]
            symbol = symbolstack[-1]
            action = actiondict[state]
            next = action.get(next_sym.name)
            if next is not None:
                if next > 0:
                    statestack.append(next)
                    next_sym = tokens.pop(0)
                    symbolstack.append(next_sym)
                elif next < 0:
                    p = prodlist[-next]
                    if len(p):
                        args = symbolstack[-len(p):]
                        # doing reduce from now
                        del symbolstack[-len(p):]
                        del statestack[-len(p):]
                        # doing actions while reducing
                        p.f(symbol, args, symbolstack)
                        symbolstack.append(symbol)
                        # after applying the rule
                        # generate the next state
                        r_state = statestack[-1]
                        r_goto = gotodict[r_state]
                        next_state = r_goto[p.name]
                        statestack.append(next_state)
                    else:
                        p.f(symbol, None, symbolstack)
                        symbolstack.append(symbol)
                        # after applying the rule
                        # generate the next state
                        r_state = statestack[-1]
                        r_goto = gotodict[r_state]
                        next_state = r_goto[p.name]
                        statestack.append(next_state)
                # for readability
                elif next == 0:
                    symbol = symbolstack[-1]
                    return symbol.value
            else:
                message = 'Parsing error.'
                raise GramError(message)


def test_main():
    g = Grammar(['a', 'b', 'c', 'd'])
    g.add_prod('S', ['a', 'S', 'b'])
    g.add_prod('S', ['b', 'c', 'd'])
    g.set_start()
    g.first_set()
    g.follow_set()
    g.build_lr_items()
    t = SLRTable(g)
    t.slr_table()
    p = LRParser(t)
    p.parse([LRToken('a'), LRToken('b'), LRToken('c'), LRToken('d'), LRToken('b'), LRToken('$end')])


if __name__ == '__main__':
    test_main()
