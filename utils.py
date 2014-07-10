# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division	

"""
Created on Fri Jun 27 15:46:09 2014

@author: enrico.giampieri2
"""
from collections import defaultdict

import sympy
import numpy as np

class Counter(defaultdict):
    """implementation of thr Counter class more appropriate for the CME"""
    def __init__(self, other=0, keymap = None):
        defaultdict.__init__(self, int)
        try:
            for k, v in other.items():
                self[k] += v
        except AttributeError:
            defaultdict.__init__(self, lambda: other)
            
        if hasattr(other, 'keymap'):
            #copy from the other Counter
            # if explicitly set as parameter, is overwritten
            self.keymap = other.keymap
            
        if callable(keymap):
            # if it is a callable, set it directly
             self.keymap = keymap
        elif keymap is not None:
            # use it as a mapping on the keys explicitly
            self.keymap = lambda k: tuple(zip(keymap, k))
        else:
            # it is None, give up
            self.keymap = keymap
    
    def total(self):
        return sum(self.itervalues(), self.default_factory())
    
    def normalize(self):
        tot = self.total()
        new_counter = self.__class__(self, keymap=self.keymap)
        for k, v in self.iteritems():
            new_counter[k] = v / tot   
        return new_counter
    
    def __add__(self, other):
        try:
            new_counter = self.__class__(self)
            for k, v in other.items():
                new_counter[k] += v
            return new_counter
        except AttributeError:
            raise NotImplementedError
    
    __radd__ = __add__
    
    def __mul__(self, other):
        new_counter = self.__class__()
        try:
            for k, v in other.items():
                new_counter[k] += self[k] * v
            return new_counter
        except AttributeError:
            for k, v in self.items():
                new_counter[k] += other * v
            new_counter.keymap = self.keymap
        return new_counter
    
    __rmul__ = __mul__    

    def itermap(self, keymap=None):
        if keymap is None:
            if self.keymap is not None:
                keymap = self.keymap
            else:
                e = 'either the class or the method should have a set keymap'
                raise ValueError(e)
        for k, v in self.iteritems():
            yield keymap(k), v
            
    def map(self, keymap=None):
        new_counter = self.__class__()
        for k, v in self.itermap(keymap=keymap):
            new_counter[k] = v
        return new_counter

    def positive(self):
        return all(v>=0 for v in self.values())    
    
 #UNTESTED METHODS  
    def __sub__(self, other):
        try:
            new_counter = self.__class__(self)
            for k, v in other.items():
                new_counter[k] -= v
            return new_counter
        except AttributeError:
            raise NotImplementedError
    
    def __rsub__(self, other):
        try:
            new_counter = self.__class__(other)
            for k, v in self.items():
                new_counter[k] -= v
            return new_counter
        except AttributeError:
            raise NotImplementedError
    
    def __str__(self):
        f = "{}={}"
        return "{"+ "\n".join(f.format(k, v) for k, v in self.items()) +"}"
    
    __repr__ = __str__
    

def variazione(expr, diff=sympy.diff):
    """given an expression returns the corresponding variation of the state
    A   --->  {A:1}
    A+B --->  {A:1, B:1}
    2*A --->  {A:2}
    """
    res = Counter()
    if expr is None:
        return res
    for s in expr.free_symbols:
        res[s] = diff(expr, s)
    return res
    
    
def shift(state, substrate, products, kinetic):
    """given a starting state and a variation on the state, 
    it returns the destination state and the transition constant or None
    """
    first_passage = state - substrate
    kin_val = kinetic.subs(state)
    if first_passage.positive() and kin_val > 0:
        return first_passage + products, kin_val
    else:
        return None, None  
        
# untested
def WRGnumpy(ensemble, weights, n):
    """weighted random generator
    
    given an array of possible values and a vector of weights,
    extract n random values
    """
    rand = np.random.rand
    bisect = np.searchsorted
    totals = np.cumsum(weights)
    rnd = rand(n) * totals[-1]
    idx = bisect(totals, rnd)
    return [ensemble[i] for i in idx]
    
