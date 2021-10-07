import numpy as np
import csv
import itertools

def main():
    basketsFile = "../bakery-datasets/1000/1000-out1.csv"
    goodsFile = "../bakery-datasets/goods.csv"
    goods = parseGoods(goodsFile)
    baskets = parseBaskets(basketsFile)
    minSup = 40
    skyline = apriori(baskets, goods, minSup)

def apriori(basketsDict, goodsDict, minSup):
    zeros = np.zeros(50, dtype=int)
    frequentItemsets = []
    supportDict = {}
    for reciept in basketsDict.values():
        for item in reciept:
            zeros[int(item)]+=1
    for i in range(50):
        if(zeros[i] > minSup):
            if(len(frequentItemsets) == 0):
                frequentItemsets.append([i])
            else:
                frequentItemsets = np.vstack([frequentItemsets, [i]])
    k = 2
    while True:
        candidates = candidateGen(frequentItemsets, k-1)
        zeros = np.zeros(len(candidates), dtype=int)
        for reciept in basketsDict.values():
            for i in range(len(candidates)):
                exists = True
                for freqGood in candidates[i]:
                    if freqGood not in reciept:
                        exists = False
                if exists:
                    zeros[i] += 1
        for i in range(len(zeros)):
            if zeros[i] >= minSup:
                if(type(frequentItemsets) != list):
                    frequentItemsets = frequentItemsets.tolist()
                frequentItemsets.append(candidates[i])

        k = k+1
        if(len(frequentItemsets[len(frequentItemsets) - 1]) < k-1):
            break
    return 0

def candidateGen(frequentItemsets, k):
    candidates = set()
    candidatesArr = []
    if(k == 1):
        for x in frequentItemsets:
            for y in frequentItemsets:
                double = frozenset([frozenset(x), frozenset(y)])
                if(len(double) >1):
                    candidates.add(double)
        for cand in candidates:
            toAdd = np.array([], dtype=int)
            for e in cand:
                toAdd = np.append(toAdd, list(e)[0])
            if(len(candidatesArr) == 0):
                candidatesArr.append([candidatesArr, toAdd])
            else:
                candidatesArr = np.vstack([candidatesArr, toAdd])
        return candidatesArr
    else:
        prevFreqItemsets = []
        for item in frequentItemsets:
            if(len(item) == k):
                prevFreqItemsets.append(item)
        for i in range(len(prevFreqItemsets)):
            for j in range(len(prevFreqItemsets)):
                if(i+1 != len(prevFreqItemsets)):
                    if(i != j):
                        nextLevel = list(itertools.combinations(np.append(prevFreqItemsets[i], prevFreqItemsets[j]), k+1))
                        # print(nextLevel)
                        valid = prune(prevFreqItemsets, nextLevel, k)
                        if len(valid) > 0:
                            candidatesArr.append(valid)
        return filterDuplicates(candidatesArr)

""" 
MAJOR PROBLEM WITH PRUNE MESSES UP GOOD COMBO """
def prune(prevFreqs, potentialCombs, k):
    # print(prevFreqs)
    # print(potentialCombs)
    finalList = []
    for combo in potentialCombs:
        # print(combo) <- this is a good combo
        matches = 0
        for subset in list(itertools.combinations(list(combo), k)):
            print(subset)
            for prev in prevFreqs:
                if set(prev) == set(subset):
                    matches += 1
        if matches == k:
            # print(combo) <- but this combo is messed up
            finalList.append(list(combo)) 
    # print("well")
    # print(finalList)
    return finalList

def filterDuplicates(candidates):
    updatedCandidates = []
    for cand in candidates:
        for item in cand:
            # print(frozenset(item))
            updatedCandidates.append(frozenset(item))
    
    # print(updatedCandidates)
    return []

def parseGoods(file):
    goodsDict = {}
    with open(file, 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter = ',')
        for line in lines:
            if(line[0] != "Id"):
                key = int(line[0])
                goodsDict[key] = np.array([line[1], line[2], line[3], line[4]])
        csvfile.close()
    return goodsDict

def parseBaskets(file):
    basketsDict = {}
    with open(file, 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter = ',')
        for line in lines:
            basket = np.array([])
            for i in range(len(line)-1):
                basket = np.append(basket, int(line[i+1]))
            basketsDict[int(line[0])] = np.array(basket)
        csvfile.close()
    return basketsDict

if __name__ == "__main__":
    main()