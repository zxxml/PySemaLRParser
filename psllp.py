#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from typing import Iterable

from pslrp import GramError, Grammar


class LLToken:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def __str__(self):
        return self.name


def dumps_tokens(tokens: Iterable[LLToken]):
    if tokens is None: return None
    string = [str(t) for t in tokens]
    return '\040'.join(string)


class LLParser:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.funcdict = {}

    @property
    def start(self):
        return self.grammar.start

    @property
    def termdict(self):
        return self.grammar.termdict

    @property
    def nontdict(self):
        return self.grammar.nontdict

    @property
    def prodlist(self):
        return self.grammar.prodlist

    @property
    def proddict(self):
        return self.grammar.proddict

    @property
    def first(self):
        return self.grammar.first

    @property
    def follow(self):
        return self.grammar.follow

    def get_first(self, syms):
        return self.grammar.get_first(syms)

    def term_func(self, sym):
        if sym in self.funcdict:
            return self.funcdict[sym]
        def _func(tokens):
            if not tokens:
                message = 'Parsing error, perhaps %s.'
                more_hint = 'missing the end symbol'
                raise GramError(message % more_hint)
            if tokens[0].name == sym:
                return tokens[1:]
            message = 'Parsing error.'
            raise GramError(message)
        self.funcdict[sym] = _func
        return self.funcdict[sym]

    def nont_func(self, sym):
        if sym in self.funcdict:
            return self.funcdict[sym]
        def _func(tokens):
            if not tokens:
                message = 'Parsing error, perhaps %s.'
                more_hint = 'missing the end symbol'
                raise GramError(message % more_hint)
            for p in self.proddict[sym]:
                first = self.get_first(p.syms)
                if tokens[0].name in first:
                    for s in p.syms:
                        f = self.funcdict[s]
                        tokens = f(tokens)
                    return tokens
            follow = self.follow[sym]
            if tokens[0].name in follow:
                return tokens
            message = 'Parsing error.'
            raise GramError(message)
        self.funcdict[sym] = _func
        return self.funcdict[sym]

    def restart(self):
        for t in self.termdict:
            self.term_func(t)
        for n in self.nontdict:
            self.nont_func(n)
        return self.funcdict

    def parse(self, tokens):
        func = self.funcdict[self.start]
        return func(tokens)


if __name__ == '__main__':
    g = Grammar(['a', 'b', 'c'])
    g.add_prod('S', ['a', 'S'])
    g.add_prod('S', ['b', 'S'])
    g.add_prod('S', ['c', 'S'])
    g.add_prod('S', [])
    g.set_start()
    g.first_set()
    g.follow_set()
    p = LLParser(g)
    s = ['a', 'b', 'c', '$end']
    s = [LLToken(x) for x in s]
    p.restart()
    p.parse(s)
