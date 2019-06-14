#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
from typing import Dict, Iterable

from pslrp import GramError, Grammar, Production


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


def get_empty_prod(proddict: Dict[str, Production], name):
    for p in proddict[name]:
        if not p.syms: return p
    return None


class LLParser:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.funcdict = {}
        for t in self.termdict:
            self.term_func(t)
        for n in self.nontdict:
            self.nont_func(n)

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
    def proddict(self):
        return self.grammar.proddict

    def get_first(self, syms):
        return self.grammar.get_first(syms)

    @property
    def follow(self):
        return self.grammar.follow

    def term_func(self, sym):
        if sym in self.funcdict:
            return self.funcdict[sym]
        def _func(tokens, old):
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
        def _func(tokens, old):
            new = old.copy()
            if not tokens:
                message = 'Parsing error, perhaps %s.'
                more_hint = 'missing the end symbol'
                raise GramError(message % more_hint)
            for p in self.proddict[sym]:
                first = self.get_first(p.syms)
                if tokens[0].name in first:
                    for i, s in enumerate(p.syms):
                        p.functions[i](new, old)
                        f = self.funcdict[s]
                        tokens = f(tokens, new)
                    p.functions[-1](new, old)
                    return tokens
            follow = self.follow[sym]
            if tokens[0].name in follow:
                p = get_empty_prod(self.proddict, sym)
                message = 'Conflict error on parsing.'
                if p is None: raise GramError(message)
                p.functions[-1](new, old)
                return tokens
            message = 'Parsing error.'
            raise GramError(message)
        self.funcdict[sym] = _func
        return self.funcdict[sym]

    def parse(self, tokens, result=None):
        if result is None: result = {}
        func = self.funcdict[self.start]
        return func(tokens, result)
