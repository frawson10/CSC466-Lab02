import numpy as np
import csv
import itertools

def main():
    basketsFile = "../training/out1.csv"
    goodsFile = "../bakery-datasets/goods.csv"
    goods = parseGoods(goodsFile)
    baskets = parseBaskets(basketsFile)
    minSup = 100
    minConf = .8
    (skylineFrequentItemsets, supportDict) = apriori(baskets, goods, minSup)
    confDict = genRules(skylineFrequentItemsets, supportDict, minConf)
    outputToTerminal(skylineFrequentItemsets, supportDict, confDict)

def apriori(basketsDict, goodsDict, minSup):
    zeros = np.zeros(50, dtype=int)
    frequentItemsets = []
    supportDict = {}
    for reciept in basketsDict.values():
        for item in reciept:
            zeros[int(item)]+=1
    for i in range(50):
        supportDict[i] = zeros[i]
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
                supportDict[frozenset(candidates[i])] = zeros[i]
                if(type(frequentItemsets) != list):
                    frequentItemsets = frequentItemsets.tolist()
                frequentItemsets.append(candidates[i])
        if(len(frequentItemsets[len(frequentItemsets) - 1]) < k-1):
            break
        frequentItemsets = trimToSkyline(frequentItemsets, k)
        k = k+1
    return (frequentItemsets, supportDict)

def genRules(itemsets, supportDict, minConf):
    confDict = {}
    finalDict = {}
    for item in itemsets:
        if(len(item) > 1):
            itemsForRule = []
            for single in item:
                confDict[(single, frozenset(item))] = float(supportDict[frozenset(item)])/supportDict[single]
    for key, value in confDict.items():
        if(value >= minConf):
            finalDict[key] = value
    return finalDict

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
        approvedCandidates = []
        for i in range(len(prevFreqItemsets)):
            for j in range(len(prevFreqItemsets)):
                if(i+1 != len(prevFreqItemsets)):
                    if(i != j): # check there are no duplicates in here
                        nextLevel = list(itertools.combinations(np.append(prevFreqItemsets[i], prevFreqItemsets[j]), k+1))
                        valid = prune(prevFreqItemsets, nextLevel, k)
                        if len(valid) > 0:
                            approvedCandidates.append(valid)
        return filterDuplicates(approvedCandidates)

def trimToSkyline(items, k):
    itemSetInQuestion = set()
    itemSetPrevLevel = set()
    toDelete = []
    finalList = []
    for item in items:
        if(len(item) == k-1):
            itemSetPrevLevel.add(frozenset(item))
        elif(len(item) == k):
            itemSetInQuestion.add(frozenset(item))
    for item in itemSetInQuestion:
        for prev in itemSetPrevLevel:
            if(item.issuperset(prev)):
                toDelete.append(list(prev))
    for item in items:
        flag = True
        for itemToDelete in toDelete:
            if(set(item) == set(itemToDelete)):
                flag = False
        if flag:
            finalList.append(list(item))
    return finalList

def prune(prevFreqs, potentialCombs, k):
    finalList = []
    for combo in potentialCombs:
        if len(set(combo)) < k+1:
            continue
        matches = 0
        for subset in list(itertools.combinations(list(combo), k)):
            for prev in prevFreqs:
                if set(prev) == set(subset):
                    matches += 1
        if matches == k:
            finalList.append(list(combo)) 
    return finalList

def filterDuplicates(candidates):
    updatedCandidates = []
    for cand in candidates:
        for item in cand:
            updatedCandidates.append(frozenset(item))
    
    updatedCandidates = list(set(updatedCandidates))
    finalList = []
    for cand in updatedCandidates:
        finalList.append(list(cand))
    return finalList

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

def outputToTerminal(skylineFrequentItemsets, supportDict, confDict):
    print("Skyline Frequent Itemsets: ")    
    for itemset in skylineFrequentItemsets:
        print("%s  |  support: %d" % (itemset, supportDict[frozenset(itemset)]))
    print("\n\nAssociation Rules: ")
    i=0
    for (rightSide, leftSide), value in confDict.items():
        i+=1
        print("Rule %d: %s ----> %d  |  %f" % (i, list(leftSide), rightSide, value))

if __name__ == "__main__":
    main()