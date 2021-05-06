#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 09:51:43 2017

@author: liliana
"""
import re
import csv
import time
import sys
from itertools import product


def binaryToDecimal(s):
    return int(s, 2)


def findFirstEvenPos(s, startPos, c):
    pos = -1
    if not len(s) <= 1 and not startPos == len(s) - 1:
        for i in range(startPos + 1, len(s), 2):
            if s[i] == c:
                pos = i
                break
    return pos


def codeCrossInv(s):
    if len(s) <= 1:
        return ""
    if s[len(s) - 1] == "1" and len(s) % 2 == 0:
        str_to_list = list(s)
        new_str = [str_to_list[i] for i in range(0, len(str_to_list) - 2, 2)]
        new_str.append(str_to_list[len(str_to_list) - 2])
        return "".join(new_str)
    return ""


def codeDiamondInv(s):
    new_str = list(s)
    for i in range(0, len(new_str)):
        if new_str[i] == "0":
            new_str[i] = "1"
        else:
            new_str[i] = "0"
    return codeCrossInv("".join(new_str))[1:]


def correctEncoding(s):
    match = re.search(r"^((1|0)0)*((0|1)1)", s)
    if match:
        return True
    else:
        return False


def isValidTransducer(bins, outs):
    if len(bins) == len(outs) and len(bins) % 2 == 0 and len(bins) > 0:
        return True
    else:
        return False


def missingStatesTransducer(bins):
    state = 1
    for i in range(0, len(bins), 2):
        if bins[i] == "":
            bins[i] = state
        if bins[i + 1] == "":
            bins[i + 1] = state
        state += 1
    return bins


def getTransducer(s):
    bins = []
    outs = []
    posIni = 0
    posFin = 0
    while posIni < len(s):
        if s[posIni] == "0":
            posFin = findFirstEvenPos(s, posIni, "0")
            if posFin > -1:
                bins.append("")
                outs.append(codeDiamondInv(s[posIni : posFin + 1]))
                posIni = posFin + 1
            else:
                break
        elif s[posIni] == "1":
            posFin = findFirstEvenPos(s, posIni, "1")
            if posFin > -1:
                bins.append(binaryToDecimal(codeCrossInv(s[posIni : posFin + 1])))
                posIni = posFin + 1
                posFin = findFirstEvenPos(s, posIni, "0")
                if posFin > -1:
                    outs.append(codeDiamondInv(s[posIni : posFin + 1]))
                    posIni = posFin + 1
                else:
                    break
            else:
                break

        else:
            break
    return bins, outs


def computeTransducer(bins, outs, p):
    bins = missingStatesTransducer(bins)
    # print("bins "+str(bins))
    # print("outs "+str(outs))
    for elem in bins:
        if elem == 0 or elem > (len(bins) / 2):
            return False
    output = []
    k = 0
    t = 0
    for c in p:
        if c == "0":
            t = bins[k]
            output.append(outs[k])
        else:
            t = bins[k + 1]
            output.append(outs[k + 1])
        k = 2 * (t - 1)
    # print("result of the computation: "+str(''.join(output)))
    return "".join(output)


def analyzeStringForTransducer(ro):
    if correctEncoding(ro):
        sigma = codeCrossInv(ro[0 : findFirstEvenPos(ro, 0, "1") + 1])
        p = ro[findFirstEvenPos(ro, 0, "1") + 1 :]
        # print('ro '+ro)
        # print('transducer '+sigma+' input '+p)
        bins, outs = getTransducer(sigma)
        if isValidTransducer(bins, outs):
            # If we want the # of states this trasnducer has, we should append
            # len(bins) to the result
            return [
                1,
                sigma,
                p,
                len(bins) // 2,
                computeTransducer(bins, outs, p),
                len(sigma) + len(p),
            ]
        else:
            return [0, "NaN", "NaN", "NaN", "NaN", "NaN"]
    else:
        return [0, "NaN", "NaN", "NaN", "NaN", "NaN"]


def enumerationStrings(m, n):
    for i in range(m, n + 1):
        for bits in product([0, 1], repeat=i):
            yield "".join(str(bit) for bit in bits)


def runExperiment(n, m):
    # start taking time
    start_time = time.time()
    print("------Experiment started------")
    # we open the file and set it up for writing the results
    csvFile = open("result_experiment_distribution.csv", "w", newline="")
    csvWriter = csv.writer(csvFile, delimiter=",", lineterminator="\n")
    csvWriter.writerow(
        [
            "string",
            "valid_encoding",
            "sigma",
            "string_p",
            "num_states",
            "output",
            "output_complexity",
        ]
    )

    list_strings = enumerationStrings(n, m)
    total_strings = 0
    for ro in list_strings:
        total_strings += 1
        # print("len ",len(ro))
        result = analyzeStringForTransducer(ro)
        if result[0] == 1:
            csvWriter.writerow(
                [ro, result[0], result[1], result[2], result[3], result[4], result[5]]
            )
        # print("Result :",[ro,result[0],result[1],result[2],result[3],result[4],result[5]])

    timing = (time.time() - start_time) / 60
    print("-----Total time -----", timing)
    print("Total of strings analyzed ", total_strings)


if __name__ == "__main__":
    runExperiment(int(sys.argv[1]), int(sys.argv[2]))
