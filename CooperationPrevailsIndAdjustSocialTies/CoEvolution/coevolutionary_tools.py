#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 19:23:38 2017

@author: lilianab
"""


import networkx as nx
import random
import math

"""Yields edges between each node and halfk neighbors.
    
    halfk: number of edges from each node
    This code is from Think Complexity 2nd Edition
"""


def adjacent_edges(nodes, halfk):
    n = len(nodes)
    for i, u in enumerate(nodes):
        for j in range(i + 1, i + halfk + 1):
            v = nodes[j % n]
            yield u, v


"""Makes a ring lattice with n nodes and degree z.
    
    Note: this only works correctly if z is even.
    
    n: number of nodes
    z: degree of each node
    
    This code is from Think Complexity 2nd Edition
"""


def make_ring_lattice(N, z):
    G = nx.Graph()
    nodes = range(N)
    G.add_nodes_from(nodes)
    G.add_edges_from(adjacent_edges(nodes, z // 2))
    return G


"""
This function performs the rewiring mechanism
in order to construct an homogeneous 
random graph. The dimensionless parameter f gives the fraction of edges
to be rewired.

The algorithm can be found in the paper 
Epidemic spreading and cooperation dynamics on homogeneous small-world networks
and works as follows:
    
When f=0 the result is a regular graph, when f=1 the result is a random graph, i.e. all
edges are randomly rewired.

The rewiring mechanism does not change the degree distribution.

Algorithm. Repeat untill f edges are successfuly rewired:

(1) Choose randomly and independently two different edges which have not been used yet in 
step (2).

(2) Swap the end of the edges if no duplicate connections arise.
"""


def rewire(G, f=0.6):
    edges_used = set()
    edges_to_swap = set()
    num_swaps_to_be_made = int(f * G.number_of_edges())
    num_swaps_done_so_far = 0
    while num_swaps_done_so_far < num_swaps_to_be_made:
        for _ in range(2):
            choices = set(G.edges()) - edges_used - edges_to_swap
            edge = random.choice(list(choices))
            edges_to_swap.add(edge)
        u_0, v_0 = edges_to_swap.pop()
        u_1, v_1 = edges_to_swap.pop()
        if not u_0 == v_1 and not u_1 == v_0:
            if not (u_0, v_1) in G.edges() and not (u_1, v_0) in G.edges():
                G.add_edge(u_0, v_1)
                G.add_edge(u_1, v_0)
                G.remove_edge(u_0, v_0)
                G.remove_edge(u_1, v_1)
                edges_used.add((u_0, v_1))
                edges_used.add((u_1, v_0))
                num_swaps_done_so_far += 1
    return G


def initialize_HoSW(N, z, f=0.6):
    return rewire(make_ring_lattice(N, z), f)


def fermi_distribution(fitness_A, fitness_B, beta=0.005):
    return 1 / (1 + (math.exp((-beta) * (fitness_B - fitness_A))))


"""
The fitness of each individual corresponds to the total accumulated payoff resulting
from pairwise interactions with all his/her neighbours. By convention, we set
payoffs R=1 and P=0 and S,T are set according to the social dilemma that's being played
"""


def get_individual_fitness(A, graph, S, T, cooperators, defectors):
    fitness = 0
    R = 1
    P = 0
    for neighbor in graph[A].keys():
        if A in cooperators and neighbor in cooperators:
            fitness += R
        elif A in cooperators and neighbor in defectors:
            fitness += S
        elif A in defectors and neighbor in cooperators:
            fitness += T
        elif A in defectors and neighbor in defectors:
            fitness += P
    return fitness


def flip(p):
    return random.random() < p


"""
This function corresponds to the pairwise comparison rule.
One node A is chosen randomly among A's first neighbors. A and B accumulate
total payoffs and the strategy of B replaces that of A with a probability given
by the fermi distribution.
"""


def strategy_update(graph, A, B, cooperators, defectors, S, T):
    if not (A in cooperators and B in cooperators) and not (
        A in defectors and B in defectors
    ):
        fitness_A = get_individual_fitness(A, graph, S, T, cooperators, defectors)
        fitness_B = get_individual_fitness(B, graph, S, T, cooperators, defectors)
        if flip(fermi_distribution(fitness_A, fitness_B)):
            if B in cooperators and A in defectors:
                defectors.remove(A)
                cooperators.append(A)
            else:
                cooperators.remove(A)
                defectors.append(A)
    return cooperators, defectors


"""
This functions rewires A to a random neighbour of B
"""


def rewire_A_to_random_neigh_B(graph, A, B):
    neighbors_B = list(graph[B].keys())
    neighbors_B.remove(A)
    # If an individual has only one link we should not destroy it (for more info
    # see paper Cooperation prevails when individuals adjust their social ties)
    if len(neighbors_B) > 1:
        C = random.choice(neighbors_B)
        graph.remove_edge(A, B)
        graph.add_edge(A, C)
    return graph


"""
Given an edge with individuals A and B at the extremes, we say that A(B) is satisfied
with the edge if the strategy of B(A) is a cooperator, being dissatisfied otherwise.
If A is satisfied, she will decide to maintain the link. If dissatisfied, then she may
compete with B to rewire the link, rewiring being attempted to a random neighbor of B.
"""


def structural_update(graph, A, B, cooperators, defectors, S, T):
    # If A is a cooperator and B is a cooperator, then both are satisfied and do nothing
    # Else they play the game
    if not (A in cooperators and B in cooperators):
        fitness_A = get_individual_fitness(A, graph, S, T, cooperators, defectors)
        fitness_B = get_individual_fitness(B, graph, S, T, cooperators, defectors)
        if A in defectors and B in defectors:
            if flip(fermi_distribution(fitness_A, fitness_B)):
                graph = rewire_A_to_random_neigh_B(graph, A, B)
            else:
                graph = rewire_A_to_random_neigh_B(graph, B, A)
        elif A in cooperators and B in defectors:
            if flip(fermi_distribution(fitness_A, fitness_B)):
                graph = rewire_A_to_random_neigh_B(graph, A, B)
        elif B in cooperators and A in defectors:
            if flip(fermi_distribution(fitness_A, fitness_B)):
                graph = rewire_A_to_random_neigh_B(graph, B, A)

    return graph


"""
In synchronous updating, after playing all games, all players update their strategy
simultaneously
"""


def synchronous_updating(graph, cooperators, defectors, S, T):
    N = len(graph.nodes())
    # All individuals play the game
    for indiv in range(N):
        neigh_indiv = random.choice(list(graph[indiv].keys()))
        graph = structural_update(
            graph, indiv, neigh_indiv, cooperators, defectors, S, T
        )
    # All individuals update their strategy simultaneously
    for indiv in range(N):
        neigh_indiv = random.choice(list(graph[indiv].keys()))
        cooperators, defectors = strategy_update(
            graph, indiv, neigh_indiv, cooperators, defectors, S, T
        )
    return graph, cooperators, defectors


"""
In the asynchronous updating, a randomly chosen player plays the game immediately followed
by his/her strategy update; following that, another randomly chosen player plays and 
updates
"""


def asynchronous_updating(graph, cooperators, defectors, S, T):
    indiv = random.choice(graph.nodes())
    neigh_indiv = random.choice(list(graph[indiv].keys()))
    graph = structural_update(graph, indiv, neigh_indiv, cooperators, defectors, S, T)
    cooperators, defectors = strategy_update(
        graph, indiv, neigh_indiv, cooperators, defectors, S, T
    )
    return graph, cooperators, defectors


"""
The full explanation of the algorithm for the simulation can be found at the Computer
Simulations section of the paper Cooperation prevails when individuals adjust their
social ties.

Parameteres:
S,T: payoffs according to the social dilemma that's being played.
W: if W>0 then evolution of strategy and structure proceed together under asynchronous updating
N: Size of population, i.e. number of individuals
z: average connectivity
f: Dimensionless parameter for initializing the graph

This function returns:
-percentage of cooperators
-heterogeneity
-maximal connectivity
-cummulative degree distribution
"""


def simulation(S, T, W, N, z, f):
    # We start from an homogeneous random graph, in which all nodes have the same number of
    # edges z
    graph = initialize_HoSW(N, z, f)
    # We start with 50% of cooperators randomly distributed in the population
    cooperators = list(random.sample(range(N), N // 2))
    defectors = list(set(range(N)) - set(cooperators))

    fraction_of_cooperators_per_generation = []

    # We run the simulation until evolution reaches 100% cooperation. If after 10**8
    # generations the population has not converged to an absorving state, we take as the
    # final result average fraction of cooperators over the last 1,000 generations
    generations = 0
    while len(cooperators) < N and generations < (10 ** 8):
        # If W>0, evolution of strategy and structure proceed together
        # under asynchronous updating
        if W > 0:
            #       print("asynchronous")
            graph, cooperators, defectors = asynchronous_updating(
                graph, cooperators, defectors, S, T
            )
        else:
            #      print("synchronous")
            graph, cooperators, defectors = synchronous_updating(
                graph, cooperators, defectors, S, T
            )
        fraction_of_cooperators_per_generation.append(len(cooperators) / N)
        generations += 1

    if len(cooperators) != N and generations > 1000:
        percentage_of_cooperators = (
            sum(fraction_of_cooperators_per_generation[-1000:]) / 1000
        )
    else:
        percentage_of_cooperators = 1.0

    return (
        percentage_of_cooperators,
        heterogeneity(graph, N, z),
        k_max(graph),
        cumulative_degree_dist(graph, N),
    )


"""
The following functions are used for computing the degree of heterogeneity of the graph
and the cummulative degree distribution
"""


def degrees(graph):
    degs = {}
    for node in graph.nodes():
        deg = graph.degree(node)
        if deg not in degs:
            degs[deg] = 0
        degs[deg] += 1
    return degs


def heterogeneity(graph, N, z):
    result = 0
    for key, value in degrees(graph).items():
        result += (key ** 2) * value
    return (result - (z ** 2)) / N


def cumulative_degree_dist(graph, N):
    degs = degrees(graph)
    cum_degs = {}
    k_max = max(degs.keys())
    for key in degs.keys():
        cum_degs[key] = (
            sum([degs.get(i) for i in range(key, k_max + 1) if not degs.get(i) == None])
            / N
        )
    return cum_degs


def k_max(graph):
    return max(degrees(graph).keys())
