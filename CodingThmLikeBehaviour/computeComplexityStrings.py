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


def computeTransducer(bins, outs, p, x):
    bins = missingStatesTransducer(bins)
    #    print("bins "+str(bins))
    #    print("outs "+str(outs))
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
    if "".join(output) == x:
        return True
    else:
        return False
    return False


def transducerComputesString(ro, x):
    if correctEncoding(ro):
        sigma = codeCrossInv(ro[0 : findFirstEvenPos(ro, 0, "1") + 1])
        p = ro[findFirstEvenPos(ro, 0, "1") + 1 :]
        # print('ro '+ro)
        # print('transducer '+sigma+' input '+p)
        bins, outs = getTransducer(sigma)
        if isValidTransducer(bins, outs):
            # If we want the # of states this trasnducer has, we should append
            # len(bins) to the result
            return [computeTransducer(bins, outs, p, x), sigma, p]
        else:
            return [False]
    else:
        return [False]


def enumerationStrings(m, n):
    for i in range(m, n + 1):
        for bits in product([0, 1], repeat=i):
            yield "".join(str(bit) for bit in bits)


def fsComplexity(x):
    # Get the list of encoded transducers, upper bound is lenght of string+16
    upperBd = len(x) + 16
    # The lower bound is 8 because that's the smallest transducer
    list_transducers = enumerationStrings(8, upperBd)
    for ro in list_transducers:
        result = transducerComputesString(ro, x)
        if result[0]:
            return [len(result[1]) + len(result[2]), result[1], result[2]]
    return [-1, -1, -1]


def runExperiment(n, m):
    # start taking time
    start_time = time.time()
    print("------Experiment started------")
    # we open the file and set it up for writing the results
    csvFile = open("result_complexity.csv", "w", newline="")
    csvWriter = csv.writer(csvFile, delimiter=",", lineterminator="\n")
    csvWriter.writerow(["x", "complexity", "sigma", "string_p"])

    list_strings = enumerationStrings(n, m)
    for x in list_strings:
        # indexUpperBound=2**(len(x)+16)
        complexity_string = fsComplexity(x)
        csvWriter.writerow(
            [x, complexity_string[0], complexity_string[1], complexity_string[2]]
        )
        print(
            "Result :",
            [x, complexity_string[0], complexity_string[1], complexity_string[2]],
        )

    timing = (time.time() - start_time) / 60
    print("-----Total time -----", timing)


if __name__ == "__main__":
    runExperiment(int(sys.argv[1]), int(sys.argv[2]))
