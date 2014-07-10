# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division	

"""
Created on Fri Jun 27 15:47:47 2014

@author: enrico.giampieri2
"""

import unittest
import sympy

from utils import Counter
from utils import variazione
from utils import shift
from utils import WRGnumpy

class test_Counter(unittest.TestCase):
    def test_creation_1(self):
        a = Counter()
        self.assertTrue(a is not None)
        self.assertEqual(a['a'], 0)
        
    def test_creation_2(self):
        a = Counter({'a':3})
        self.assertEqual(a['a'], 3)
        
    def test_creation_3(self):
        a = Counter({'a':3})
        b = Counter(a)
        self.assertEqual(b['a'], 3)
        self.assertIs(a.keymap, b.keymap)
        
    def test_creation_4(self):
        a = Counter(5)
        self.assertEqual(a['a'], 5)
        
    def test_calculate_total_1(self):
        a = Counter({'a':3, 'b':5, 'c':2})
        self.assertEqual(a.total(), 10)
        
    def test_normalize_1(self):
        a = Counter({'a':3, 'b':5, 'c':2})
        b = a.normalize()
        self.assertAlmostEqual(b.total(), 1.0)
        self.assertAlmostEqual(b['a'], 0.3)
        self.assertAlmostEqual(b['b'], 0.5)
        self.assertAlmostEqual(b['c'], 0.2)
        self.assertIs(a.keymap, b.keymap)
        
    def test_add_other_counter(self):
        a = Counter({'b':5, 'c':2})
        b = Counter({'a':3, 'b':5})
        c = a + b
        self.assertAlmostEqual(c['a'], 3)
        self.assertAlmostEqual(c['b'], 10)
        self.assertAlmostEqual(c['c'], 2)
        
    def test_add_dict(self):
        a = Counter({'b':5, 'c':2})
        b = {'a':3, 'b':5}
        c = a + b
        self.assertAlmostEqual(c['a'], 3)
        self.assertAlmostEqual(c['b'], 10)
        self.assertAlmostEqual(c['c'], 2)
        
    def test_add_dict_reverse(self):
        a = Counter({'b':5, 'c':2})
        b = {'a':3, 'b':5}
        c = b + a
        self.assertAlmostEqual(c['a'], 3)
        self.assertAlmostEqual(c['b'], 10)
        self.assertAlmostEqual(c['c'], 2)
        
    def test_add_number(self):
        a = Counter({'b':5, 'c':2})
        with self.assertRaises(NotImplementedError):
            a + 1
        with self.assertRaises(NotImplementedError):
            1 + a
            
    def test_multiply_number(self):
        a = Counter({'b':5, 'c':2})
        b = a * 2
        self.assertAlmostEqual(b['b'], 10)
        self.assertAlmostEqual(b['c'], 4)
        self.assertIs(a.keymap, b.keymap)
        
    def test_multiply_other_counter(self):
        a = Counter({'b':5, 'c':2})
        b = Counter({'a':3, 'b':5})
        c = a * b
        self.assertAlmostEqual(c['a'], 0)
        self.assertAlmostEqual(c['b'], 25)
        self.assertAlmostEqual(c['c'], 0)
        
    def test_itermap_1(self):
        a = Counter({'b':5, 'c':2}, keymap=lambda s: s*2)
        b = dict(a.itermap())
        self.assertEqual(b, {'bb': 5, 'cc': 2})
        
    def test_itermap_2(self):
        a = Counter({'b':5, 'c':2})
        b = dict(a.itermap(lambda s: s*2))
        self.assertEqual(b, {'bb': 5, 'cc': 2})
        
    def test_itermap_3(self):
        a = Counter({'b':5, 'c':2}, keymap=lambda s: s*3)
        b = dict(a.itermap(lambda s: s*2))
        self.assertEqual(b, {'bb': 5, 'cc': 2})
        
    def test_map_1(self):
        a = Counter({'b':5, 'c':2}, keymap=lambda s: s*2)
        b = a.map()
        self.assertEqual(b, {'bb': 5, 'cc': 2})
        
    def test_map_2(self):
        a = Counter({(1, 2): 0.5}, keymap=['a', 'b'])
        b = a.map()
        self.assertEqual(b, {(('a', 1), ('b', 2)): 0.5})
        
    def test_positive(self):
        a = Counter({'a':1})
        self.assertTrue(a.positive())
        
        a = Counter({'a':-1})
        self.assertFalse(a.positive())
        
        a = Counter({'a':1, 'b':-1})
        self.assertFalse(a.positive())
        
    

class test_variazione(unittest.TestCase):
    def test_base(self):
        A = sympy.Symbol('A')
        B = sympy.Symbol('B')
        r = variazione(A)
        self.assertEqual(r, {A:1})
        
        r = variazione(A+B)
        self.assertEqual(r, {A:1, B:1})
        
        r = variazione(2*A)
        self.assertEqual(r, {A:2})
        
        r = variazione(A+A)
        self.assertEqual(r, {A:2})


class test_shift(unittest.TestCase):
    def test_base(self):
        A = sympy.Symbol('A')
        B = sympy.Symbol('B')

        state_0 = Counter({A:2})
        substrate = Counter({A:1})
        products = Counter({B:2})
        kinetic = A*(A-1)
        new_state, kinetic_val = shift(state_0, substrate, products, kinetic)
        self.assertEqual(new_state, {A:1, B:2})
        self.assertEqual(kinetic_val, 2)
        
    def test_base_impossible_1(self):
        A = sympy.Symbol('A')
        B = sympy.Symbol('B')

        state_0 = Counter({A:1})
        substrate = Counter({A:1})
        products = Counter({B:2})
        kinetic = A*(A-1)
        new_state, kinetic_val = shift(state_0, substrate, products, kinetic)
        self.assertEqual(new_state, None)
        self.assertEqual(kinetic_val, None)
        
    def test_base_impossible_2(self):
        A = sympy.Symbol('A')
        B = sympy.Symbol('B')

        state_0 = Counter({A:2})
        substrate = Counter({A:3})
        products = Counter({B:2})
        kinetic = A*(A-1)
        new_state, kinetic_val = shift(state_0, substrate, products, kinetic)
        self.assertEqual(new_state, None)
        self.assertEqual(kinetic_val, None)
        

if __name__ == '__main__':
    unittest.main()