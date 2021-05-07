#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 19:23:37 2017

@author: lilianab
"""

import time
from coevolutionary_tools import simulation
from multiprocessing import Pool
import csv


def initialize_file(file_name):
    # we write the results to the file coevolutionary_experiment.csv
    csvFile = open(file_name, "w", newline="")
    csvWriter = csv.writer(csvFile, delimiter=",", lineterminator="\n")
    csvWriter.writerow(
        ["experiment", "percentage_coop", "heterogeneity", "k_max", "cumm_deg_dist"]
    )
    return csvFile, csvWriter


"""
This function runs the simulations in parallel using the available cores
"""


def run_experiment_parallel(number_of_simulations, S, T, W, N, z, f, file_name):
    csvFile, csvWriter = initialize_file(file_name)
    # the variable arguments contains the arguments for the simulation function times the
    # total number of different simulations we're running the experiment for
    arguments = [(S, T, W, N, z, f)] * number_of_simulations
    p = Pool()
    result = p.starmap(simulation, arguments)
    p.close()
    p.join()
    count = 1
    for simul in result:
        csvWriter.writerow([count] + [elem for elem in simul])
        count += 1

    csvFile.close()


def run_experiment(number_of_simulations, S, T, W, N, z, f, file_name):

    csvFile, csvWriter = initialize_file(file_name)
    count = 1
    for _ in range(number_of_simulations):
        result = simulation(S, T, W, N, z, f)
        csvWriter.writerow([count] + [elem for elem in result])
        count += 1
    csvFile.close()


if __name__ == "__main__":
    start_time = time.time()

    # Save the results to the file
    file_name = "coevolutionary_experiment.csv"
    number_of_simulations = 2

    # This function runs the fimulations in parallel
    run_experiment_parallel(number_of_simulations, 1, 0, 0, 1000, 10, 0.5, file_name)

    # this function does not run the simulations in parallel (slower to use)
    # run_experiment(number_of_simulations,1,0,0,1000,10,0.5,file_name)

    timing = time.time() - start_time
    print("-----Total time -----", timing)
