#!/usr/bin/env python
import re

def matcher(searcher):
        if callable(searcher): return searcher
        if searcher == None: return lambda value: True
        if type(searcher) == type(re.compile('')): return lambda value: re.match(searcher, value)
        if str(searcher) == searcher: return lambda value: searcher in value
        else: return lambda value: searcher == value

def search_object(object, name = None, value = None):
    if not name and not value: raise Exception("Must search by name or value")
    name, value = matcher(name), matcher(value)
    return [(i, getattr(object, i)) for i in dir(object) if name(i) and value(getattr(object, i))]

def make_chain(*functions, **kwargs):
    '''Return a function calling all the functions passed in sequence with the given params'''
    merge = kwargs.get('merge') or (lambda l: l)
    call_chain = lambda *args, **kwargs: [f(*args, **kwargs) for f in functions]
    return lambda *args, **kwargs: merge(call_chain(*args, **kwargs))

