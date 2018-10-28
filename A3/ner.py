from sys import argv
from collections import OrderedDict
import json
import copy

# { NP : Context }
trainingSet = []
# { NP : Context }
testSet = []

# { word : Rule}
spelling = OrderedDict()
# { word : Rule}
context = OrderedDict()

#Final list of rules
finalList = []
#Result of testSet applied to learned rules ((NP,C),label)
result = []

def printDict(d):
    print("* * * * *")
    for key, val in d.items():
        print(str(key) + " : " + str(val))

def printTuples(t):
    print("- - - - -")
    for tup in t:
        print( "(" + str(tup[0]) + " , " + str(tup[1]) + ")" )

def printList(l):
    for e in l:
        print(e)

class Rule(object):
   def __init__(self,t,word,label,prob,freq,iteration):
       self.t = t
       self.word = word
       self.label = label
       self.prob = prob
       self.freq = freq
       self.iteration = iteration 
   
   def __eq__(self,other):
       return self.t == other.t and self.word == other.word and \
              self.label == other.label and self.prob == other.prob and \
              self.freq == other.freq
              
   def __repr__(self):
       return self.t + " " + "Contains("+self.word+") -> "+self.label+" (prob="+("{0:.3f}".format(self.prob))+" ; freq="+str(self.freq)+")"

with open(argv[1]) as f:
    for line in f:
        split = line.split(' ')
        t = split[0]
        word = split[1][9:(str(split[1])).find(")")]
        label = split[3].strip("\n")
        prob = -1.0
        freq = -1
        spelling[word] = Rule(t,word,label,prob,freq,0)

with open(argv[2]) as f:
    lines = f.readlines()
    for i in range(0,len(lines),3):
        contextLine = str(lines[i].strip('\n'))
        NPLine      = str(lines[i+1].strip('\n'))
        trainingSet.append( (' '.join(NPLine.split(' ')[1:]) , ' '.join(contextLine.split(' ')[1:]) ) )

with open(argv[3]) as f:
    lines = f.readlines()
    for i in range(0,len(lines),3):
        contextLine = str(lines[i].strip('\n'))
        NPLine      = str(lines[i+1].strip('\n'))
        testSet.append( (' '.join(NPLine.split(' ')[1:]) , ' '.join(contextLine.split(' ')[1:]) ) )
        

def bootstrapping():
    for i in range(1,4):
        ### GENERATE CONTEXT RULES ###
        temp_instances = []
        for NP_C in trainingSet:
            NP = NP_C[0]
            C  = NP_C[1]
            for rule in spelling.values():
                if (rule.word in NP.split(' ')):
                    temp_instances.append( ( (NP,C) , rule) )
                    break
        
        # Generate all posible context rules
        allContextRules = {}
        for NP_C,rule in temp_instances:
            C = NP_C[1]
            split = C.split(' ')
            for cword in split:
                if(cword not in allContextRules.keys() and cword not in context):
                    allContextRules[cword] = Rule("CONTEXT",cword,rule.label,0.0,0,i)
        
        # Match and increment frequencies and probabilities
        for cword in allContextRules.iterkeys():
            for NP_C,rule in temp_instances:
                C = NP_C[1]
                if(cword in C.split(' ')):
                    if(allContextRules[cword].label == rule.label):
                        allContextRules[cword].prob += 1
                        allContextRules[cword].freq += 1
                    else:
                        allContextRules[cword].freq += 1

        #  Divide to get final probabilities and remove probailities less than 0.80 and freq of 5
        for cword in allContextRules.keys():
            if(allContextRules[cword].freq < 5):
                del allContextRules[cword]
            else:
                allContextRules[cword].prob /= allContextRules[cword].freq
                if(allContextRules[cword].prob < 0.8):
                    del allContextRules[cword]
        
        sorterRules = allContextRules.values()
        sorterRules.sort(key = (lambda r : r.word))
        sorterRules.sort(key = (lambda r : 1 << 32 if r.freq == -1 else r.freq), reverse = True)
        sorterRules.sort(key = (lambda r : 1 << 32 if r.prob == -1 else r.prob), reverse = True)

        # Get top 2 rules
        labelCounts = {}
        labelCounts["PERSON"] = 0
        labelCounts["LOCATION"] = 0
        labelCounts["ORGANIZATION"] = 0
        for rule in sorterRules:
            if (all([count > 2 for count in labelCounts.values()])):
                break
            else:
                labelCounts[rule.label] += 1
                if (labelCounts[rule.label] < 3):
                    context[rule.word] = rule

        ### GENERATE SPELLING RULES ###
        temp_instances = []
        for NP_C in trainingSet:
            NP = NP_C[0]
            C  = NP_C[1]
            for rule in context.values():
                if (rule.word in C.split(' ')):
                    temp_instances.append( ( (NP,C) , rule) )
                    break

        # Generate all posible spelling rules
        allSpellingRules = {}
        for NP_C,rule in temp_instances:
            NP = NP_C[0]
            split = NP.split(' ')
            for npword in split:
                if(npword not in allSpellingRules.keys() and npword not in spelling):
                    allSpellingRules[npword] = Rule("SPELLING",npword,rule.label,0.0,0,i)
        
        # Match and increment frequencies and probabilities
        for npword in allSpellingRules.iterkeys():
            for NP_C,rule in temp_instances:
                NP = NP_C[0]
                if(npword in NP.split(' ')):
                    if(allSpellingRules[npword].label == rule.label):
                        allSpellingRules[npword].prob += 1
                        allSpellingRules[npword].freq += 1
                    else:
                        allSpellingRules[npword].freq += 1

        #  Divide to get final probabilities and remove probailities less than 0.80 and freq of 5
        for npword in allSpellingRules.keys():
            if(allSpellingRules[npword].freq < 5):
                del allSpellingRules[npword]
            else:
                allSpellingRules[npword].prob /= allSpellingRules[npword].freq
                if(allSpellingRules[npword].prob < 0.8):
                    del allSpellingRules[npword]
            
        sorterRules = allSpellingRules.values()
        sorterRules.sort(key = (lambda r : r.word))
        sorterRules.sort(key = (lambda r : 1 << 32 if r.freq == -1 else r.freq), reverse = True)
        sorterRules.sort(key = (lambda r : 1 << 32 if r.prob == -1 else r.prob), reverse = True)

        #printList(sorterRules)

        # Get top 2 rules
        labelCounts = {}
        labelCounts["PERSON"] = 0
        labelCounts["LOCATION"] = 0
        labelCounts["ORGANIZATION"] = 0
        for rule in sorterRules:
            if (all([count > 2 for count in labelCounts.values()])):
                break
            else:
                labelCounts[rule.label] += 1
                if (labelCounts[rule.label] < 3):
                    spelling[rule.word] = rule
def applyLearning():
    unlabled = list(testSet)
    temp_instances = {}
    for NP_C in testSet:
        NP = NP_C[0]
        C  = NP_C[1]
        for rule in spelling.values():
            if (rule.word in NP.split(' ')):
                temp_instances[(NP,C)] = rule
                unlabled.remove( (NP,C) )
                break
    for NP_C in unlabled:
        NP = NP_C[0]
        C  = NP_C[1]
        for rule in context.values():
            if (rule.word in C.split(' ')):
                temp_instances[(NP,C)] = rule
                break
        
    for NP_C in testSet:
        if(NP_C in temp_instances):
            result.append( (NP_C,temp_instances[NP_C].label) )
        else:
            result.append( (NP_C,"NONE") )

def printTrace():
    print("SEED DECISION LIST\n")
    printList([rule for rule in finalList if (rule.t == "SPELLING" and rule.iteration == 0)])
    print("\nITERATION #1: NEW CONTEXT RULES\n")
    printList([rule for rule in finalList if (rule.t == "CONTEXT" and rule.iteration == 1)])
    print("\nITERATION #1: NEW SPELLING RULES\n")
    printList([rule for rule in finalList if (rule.t == "SPELLING" and rule.iteration == 1)])
    print("\nITERATION #2 NEW CONTEXT RULES\n")
    printList([rule for rule in finalList if (rule.t == "CONTEXT" and rule.iteration == 2)])
    print("\nITERATION #2: NEW SPELLING RULES\n")
    printList([rule for rule in finalList if (rule.t == "SPELLING" and rule.iteration == 2)])
    print("\nITERATION #3: NEW CONTEXT RULES\n")
    printList([rule for rule in finalList if (rule.t == "CONTEXT" and rule.iteration == 3)])
    print("\nITERATION #3: NEW SPELLING RULES\n")
    printList([rule for rule in finalList if (rule.t == "SPELLING" and rule.iteration == 3)])
    print("\nFINAL DECISION LIST\n")
    printList(finalList)
    print("\nAPPLYING FINAL DECISION LIST TO TEST INSTANCES\n")
    for NPC_L in result:
        NP = NPC_L[0][0]
        C  = NPC_L[0][1]
        L  = NPC_L[1]
        print("CONTEXT: " + C)
        print("NP: " + NP)
        print("CLASS: " + L)
        print("")


bootstrapping()
finalList = list(spelling.values())
finalList.extend(context.values())
applyLearning()
printTrace()
#printList(finalList)
#printDict(context)
#printDict(spelling)
#printList(spelling.values())
#printList(context.values())
#printDict(trainingSet)
#printDict(spelling)
#printDict(testSet)
#print(context)