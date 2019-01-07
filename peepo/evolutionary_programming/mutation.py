import logging
import math
import random
import uuid

import numpy as np

from peepo.predictive_processing.v3.peepo_network import read_from_file, get_topologies


def add_node(network, epsilon=0.05):
    """
    Random mutation of adding a single node and an edge.

    :param network: PeepoNetwork to mutate
    :param epsilon: Rate of change for mutation parameters: float, default 0.05
    :return: mutated PeepoNetwork
    """
    new_parent_node = str(uuid.uuid4())[:8]
    child_node = random.choice(network.get_nodes())
    logging.info('Adding new node with edge to: %s to %s', new_parent_node, child_node)

    network.add_belief_node(new_parent_node, 2)
    network.add_edge((new_parent_node, child_node))

    incoming_edges = network.get_incoming_edges(child_node)
    cardinality_map = network.get_cardinality_map()
    parents_card = [cardinality_map[x] for x in incoming_edges]

    omega_map = network.get_omega_map()
    omega_map[child_node] += (0.5 - np.random.rand(cardinality_map[child_node])) * epsilon

    network.add_omega(new_parent_node, np.random.rand(2) * (2 * math.pi))

    network.add_cpd(new_parent_node, ga_parent_cpd(omega_map[new_parent_node]))
    network.add_cpd(child_node, ga_child_cpd(parents_card, omega_map[child_node]))


def ga_parent_cpd(omega):
    phase_shift = omega[0]

    pdf = []
    for idx, ang in enumerate(omega):
        pdf.append(math.sin(ang * (idx + 1) + phase_shift) + 1.2)

    return normalize_distribution(np.asarray(pdf))


def ga_child_cpd(card_parents, omega):
    """
    Used in the framework of Genetic Algorithm to initialize a childs cpd and to alter it later (mutation)
    The word 'child" used here is in the context of Bayesian network and is not an offspring of a GA


    :param card_parents: array containing the cardinality of the childs' parents
    :param omega: an array of dim cardinality of the child (card_child) containing the cpd's  generating parameters
    :return: a matrix of shape (card_child, numpy.prod(card_parents) containing the conditional probability distribution

    example :

        my_card_parents = [2, 3, 2]
        max_omega = 2 * math.pi * np.prod(my_card_parents)

        zero generation : (my_card_child = 3)
        my_omega = [2.0,0.1,0.9] -> only for this example. As a rule one will use
            my_omega = np.random.rand(my_card_child) * max_omega to initialize (0th generation)
            a child's cpd and
            my_omega += (0.5 - np.random.rand(my_card_child))*epsilon with espilon small (e.g. 0.05)
            when mutating the childs' cpd

        my_pdf = ga_child_cpd( my_card_parents, my_omega)

        mutation :
        epsilon = 0.05
        my_omega += (0.5 - np.random.rand(len(my_omega))*epsilon
        my_pdf_ = ga_child_cpd( my_card_parents, my_omega)

        --->
            Zero generation cpd
            [[0.07 0.25 0.53 0.18 0.14 0.37 0.18 0.09 0.54 0.46 0.06 0.45]
             [0.56 0.62 0.47 0.67 0.49 0.28 0.35 0.48 0.35 0.54 0.69 0.24]
             [0.37 0.13 0.00 0.15 0.37 0.35 0.47 0.44 0.11 0.00 0.25 0.31]]


            Mutated generation cpd
            [[0.08 0.23 0.54 0.21 0.13 0.37 0.20 0.06 0.55 0.55 0.03 0.47]
             [0.55 0.62 0.46 0.65 0.50 0.27 0.32 0.45 0.32 0.45 0.71 0.21]
             [0.37 0.14 0.00 0.13 0.38 0.36 0.47 0.49 0.13 0.00 0.26 0.33]]


            Delta zero generation - mutated cpd
            [[-0.01 0.01 -0.01 -0.03 0.02 -0.01 -0.03 0.03 -0.01 -0.08 0.04 -0.02]
             [0.01 -0.00 0.01 0.02 -0.01 0.01 0.03 0.03 0.03 0.09 -0.03 0.03]
             [-0.00 -0.01 -0.00 0.01 -0.01 -0.00 -0.00 -0.05 -0.03 -0.00 -0.01 -0.01]]
    """

    phase_shift = omega[0]
    n_comb = np.prod(card_parents)  # type: int
    pdf = []
    for ang in omega:
        pdf_row = []
        for col in range(n_comb):
            pdf_row.append(math.sin(ang * (col + 1) + phase_shift) + 1.2)
        pdf.append(pdf_row)
    return normalize_distribution(np.asarray(pdf))


def normalize_distribution(matrix):
    """
    Normalizes the columns of a matrix (i.e. sum matrix[:,i] = 1

    :param matrix: numpy 2 dimensional array
    :return: numpy 2 dimensional normalized array
    """
    factor = np.sum(matrix, axis=0)
    return matrix / factor


if __name__ == '__main__':
    case = 'color_recognition'

    pp_network = read_from_file(case)
    topologies = get_topologies(pp_network)
    pp_network.set_edges(topologies[20]['edges'])
    add_node(pp_network)
    print(pp_network)
