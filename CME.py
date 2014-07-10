# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 13:17:23 2014

@author: enrico.giampieri2
"""

from collections import defaultdict

import numpy as np
import sympy
from sympy import sympify, Symbol
from numpy.random import exponential as rand_exp

from sympy.utilities.lambdify import lambdify
from scipy.integrate import odeint

from utils import Counter
from utils import variazione
from utils import shift
from utils import WRGnumpy

class CME(object):
    def __init__(self):
        self.reactions = []
        
    def add_reaction(self, substrate, products, kinetic):
        """add a reaction to the CME, given the consumed substrate, the created product and the reaction kinetic"""
        self.reactions.append( (variazione(sympify(substrate)), variazione(sympify(products)), sympify(kinetic)) )
    
    def     
    
    def escapes(self, start):
        """given a starting state it evaluate which states are reachable and the corresponding transition rate"""
        start = Counter(start)
        end_states = []
        kinetics = []
        for substrate, products, kinetic in self.reactions:
            end_state, kinetic = shift(start, substrate, products, kinetic)
            if kinetic and end_state is not None:
                end_states.append(end_state)
                kinetics.append(float(kinetic))
        kinetics = np.array(kinetics)
        return end_states, kinetics

    def gillespie(self, start, steps=10):
        """make n step of gillespie simulation given the starting state"""
        start = Counter(start)
        time = 0.0
        while time<steps:
        #for i in xrange(steps):
            end_states, kinetics = self.escapes(start)
            cumulative = np.cumsum(kinetics)
            if not len(end_states) or not len(cumulative):
                # ho raggiunto uno stato stazionario
                yield start, np.inf
                break
            lambda_tot = cumulative[-1]
            dt = rand_exp(1./lambda_tot)
            selected = np.searchsorted(cumulative/lambda_tot, np.random.rand())
            new_state = end_states[selected]
            yield start, time, dt
            time +=dt
            start = new_state
            
    def evaluate(self, start, steps, *functions):
        """evaluate the value of several function in time given a starting state and the number of step to be done"""
        time = 0.0
        states, times, dts = zip(*self.gillespie(start, steps))
        time = np.cumsum([0] + list(dts))
        states = [start] + list(states)
        func_values = { str(function):[ float(function.subs(state)) for state in states ] for function in functions}
        return time, func_values
    
    def distribution(self, start, steps=10, burnout=-1, *functions):
        """return the stationary distribution from a gillespie simulation"""
        distrib = defaultdict(float)
        time = 0.0
        for idx, (state, times, dt) in enumerate(self.gillespie(start, steps)):
            time+=dt
            if time>burnout:
                state = tuple(sorted(state.items(), key=str))
                distrib[state]+=dt
        if not distrib:
            return {tuple(sorted(state.items(), key=str)):1.0}
        result = {}
        for function in functions:
            if isinstance(function, (tuple,list)):
                pass
            else:
                A_distrib = { int(function.subs(dict(k))):v for k, v in distrib.items()}
                min_a, max_a = min(A_distrib), max(A_distrib)
                A_distrib = [A_distrib.get(idx, 0.0) for idx in xrange(min_a, max_a+1)]
                result[function] = A_distrib
        return result
    
    def writeCME(self):
        """write the complete CME of the given process"""
        p = Symbol('p')
        pxy = p(*sorted(k for k in set.union(*[set(substrate-products) for substrate, products, kinetic in self.reactions])))
        base = 0
        for substrate, products, kinetic in self.reactions:
            transition = substrate-products
            temp = (pxy*kinetic).subs( {k: k+transition.get(k, 0) for k in transition}) - pxy * kinetic
            base += temp
        return base
    
    def transition_matrix(self, start):
        """create the transition matrix and the state vector from a starting point

        Will stuck in an infinite loop if the CME is not limited
        """
        start = Counter(start)
        states = [start]
        transitions = dict()
        for state in states:
            for destination, kinetic in zip(*self.escapes(state)):
                if destination not in states:
                    states.append(destination)
                transitions[tuple(state.items()), tuple(destination.items())] = kinetic
        return transitions, states

    def deterministic(self):
        Zero = type(sympify(0))
        kinetics = defaultdict(Zero)
        for substrates, products, kinetic in self.reactions:
            #print(substrates, products, kinetic)
            for substrate in substrates:
                kinetics[substrate]-=kinetic
            for product in products:
                kinetics[product]+=kinetic
        return kinetics
    
    def equilibriums(self):
        kinetics = self.deterministic()
        variables = kinetics.keys()
        kinets = kinetics.values()
        sol = sympy.solve(kinets, variables, dict=True)
        return sol
    
    def numerical_equilibrium(self):
        
        res = self.deterministic()
        f = lambdify(res.keys(), res.values())
        g = lambda y, t: f(*y)
        r = odeint(g, y0=np.ones(len(res.keys())), t=[0.0, 1e6])[-1]
        r = odeint(g, y0=r, t=[0.0, 1e6])[-1]
        return dict(zip(res.keys(), r))
    
    def naive_distribution(self, state_0, final_time, burnout_time):
        from collections import Counter
        distribution = Counter()
        conteggi = Counter()
        for state, time, dt in self.gillespie(state_0, final_time):
            if time<burnout_time:
                continue
            idx = tuple(state.values())
            distribution[idx]+=dt
            conteggi[idx]+=1 
        return state_0.keys(), distribution, conteggi





def parsimulate(self, state_0, burnout, warmup, time, njobs=8):
    """
    def g(s):
        return cme.naive_distribution(*s)
    
    parsimulate(g, {B1:1, B2:1}, 10, 10, 10)
    """
    
    globals()['__cme__'] = self
    
    def g(s):
        return __cme__.naive_distribution(*s)
    
    globals()['__f__'] = g
    
    import concurrent.futures as futures
    
    s = (state_0, warmup+burnout, burnout)
    keys, dists2, counts2 = __f__(s)
    a = WRGnumpy(dists2.keys(), dists2.values(), njobs)
    l = [dict(zip(keys, state)) for state in a]
    l = [(d, time, 0) for d in l]

    executioner_class = futures.ThreadPoolExecutor
    executioner_class = futures.ProcessPoolExecutor
    
    with executioner_class(max_workers=njobs) as executor:
        dists = []
        counts = []
        for k, d, c in executor.map(__f__, l):
            dists.append(d)
            counts.append(c)
        #dists = sum(dists, Counter())
        #counts = sum(counts, Counter())
    return keys, dists, counts