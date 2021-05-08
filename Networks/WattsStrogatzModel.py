import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random


def flip(p):
    return np.random.random() < p


def adjacent_edges(nodes, halfk):
    n = len(nodes)
    for i, u in enumerate(nodes):
        for j in range(i + 1, i + halfk + 1):
            v = nodes[j % n]
            yield u, v


def make_ring_lattice(n, k):
    G = nx.Graph()
    nodes = range(n)
    G.add_nodes_from(nodes)
    G.add_edges_from(adjacent_edges(nodes, k // 2))
    return G


def rewire_node(lattice, current_node, neighbour_current_node):
    new_neighbour = np.random.choice(
        [
            x
            for x in lattice.nodes()
            if not (x in lattice.neighbors(current_node) and x != current_node)
        ]
    )
    lattice.remove_edge(current_node, neighbour_current_node)
    lattice.add_edge(current_node, new_neighbour)
    return lattice


def watts_strogatz_model(lattice, start, halfk, p):
    current_node = 0
    n = len(lattice.nodes())
    for i in range(1, halfk + 1):
        for _ in range(0, n):
            neighbour_current_node = (current_node + i) % (n)
            if flip(p):
                lattice = rewire_node(lattice, current_node, neighbour_current_node)
            current_node = (current_node + 1) % (n)
    return lattice


def all_pairs(nodes):
    for i, u in enumerate(nodes):
        for j, v in enumerate(nodes):
            if i > j:
                yield u, v


def path_lengths(lattice):
    length_map = nx.shortest_path_length(lattice)
    lengths = [length_map[u][v] for u, v in all_pairs(lattice.nodes())]
    return lengths


def characteristic_path_length(lattice):
    return np.mean(path_lengths(lattice))


def node_clustering(lattice, u):
    neighbours = lattice.neighbors(u)
    k = len(neighbours)
    if k < 2:
        return 0

    total = (k * (k - 1)) / 2
    exist = 0
    for v, w in all_pairs(neighbours):
        if lattice.has_edge(v, w):
            exist += 1
    return exist / total


def clustering_coefficient(lattice):
    cc = np.mean([node_clustering(lattice, node) for node in lattice])
    return cc


if __name__ == "__main__":

    lattice = make_ring_lattice(1000, 10)
    lattice = watts_strogatz_model(lattice, 0, 2, 0.9)
    print("Characteristic path length: " + str(characteristic_path_length(lattice)))
    print("Clustering coefficient: " + str(clustering_coefficient(lattice)))
