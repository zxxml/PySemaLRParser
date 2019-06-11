#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from collections import defaultdict
from contextlib import suppress


class Production:
    def __init__(self, index, name, syms, func=None):
        self.index = index
        self.name = name
        self.syms = syms
        self.func = func
        self.lr_next = None
        self.lr_items = None

    def __len__(self):
        return len(self.syms)

    def __str__(self):
        syms = '\40'.join(self.syms)
        return '%s -> %s' % (self.name, syms)


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
    def __init__(self, prod, lr_index):
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
        return len(self.prod)

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


class SLRTable:
    def __init__(self):
        self.actiondict = None
        self.gotodict = None
        self.prodlist = None
        # incomplete tables
        self.actioncache = {}
        self.gotocache = {}
        # internal variables
        self._add_count = 0

    def lr0_closure(self, state_i):
        self._add_count += 1
        # state_i means Ii
        # a set of lr items
        closure = state_i[:]
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

    def lr0_goto(self, state_i, x):
        goto = self.gotocache.get((id(state_i), x))
        if goto is not None: return goto
        s = self.gotocache.get(x)
        if s is None:
            self.gotocache[x] = {}
            s = self.gotocache[x]
        goto_set = []
        for item in state_i:
            n = item.lr_next
            if n and n.lr_before == x:
                s1 = s.get(id(n))
                if not s1:
                    s[id(n)] = {}
                    s1 = s[id(n)]
                goto_set.append(n)
                s = s1
        g = s.get('$end')
        if g is None:
            if goto_set:
                g = self.lr0_closure(goto_set)
                s['$end'] = g
            else:
                s['$end'] = g
        self.gotocache[(id(state_i), x)] = g
        return g


if __name__ == '__main__':
    g = Grammar(['a', 'b', 'c', 'd'])
    g.add_prod('S', ['a', 'S', 'b'])
    g.add_prod('S', ['b', 'c', 'd'])
    g.add_prod('S', [])
    g.set_start()
    for e in g.prodlist: print(e)
    print(g.proddict)
    print(g.nontdict)
    print(g.termdict)
    print(g.first_set())
    print(g.follow_set())
    print(g.start)
    g.build_lr_items()
    for each in g.prodlist:
        for item in each.lr_items:
            print(item, '#', item.lr_before, '#', item.lr_after, '#', item.lr_next)
