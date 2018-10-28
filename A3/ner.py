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
       freq_mutation = (-1   if self.freq == 1 << 32 else self.freq)
       prob_mutation = (-1.0 if self.prob == 1 << 32 else self.prob)
       return self.t + " " + "Contains("+self.word+") -> "+self.label+" (prob="+str(prob_mutation)+" ; freq="+str(freq_mutation)+") iter=" + str(self.iteration)

with open(argv[1]) as f:
    for line in f:
        split = line.split(' ')
        t = split[0]
        word = split[1][9:(str(split[1])).find(")")]
        label = split[3].strip("\n")
        prob = 1 << 32
        freq = 1 << 32
        spelling[word] = Rule(t,word,label,prob,freq,0)

with open(argv[2]) as f:
    while True:
        contextLine = str(f.readline().strip('\n'))
        NPLine      = str(f.readline().strip('\n'))
        blankLine   = f.readline()
        if not blankLine :
            break
        else:
            trainingSet.append( (' '.join(NPLine.split(' ')[1:]) , ' '.join(contextLine.split(' ')[1:]) ) )

with open(argv[3]) as f:
    while True:
        contextLine = str(f.readline().strip('\n'))
        NPLine      = str(f.readline().strip('\n'))
        blankLine   = f.readline()
        if not blankLine :
            break
        else:
            testSet.append( (' '.join(NPLine.split(' ')[1:]) , ' '.join(contextLine.split(' ')[1:]) ) )

def bootstrapping():
    
    for i in range(1,2):
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
                if(cword not in allContextRules.keys()):
                    allContextRules[cword] = Rule("CONTEXT",cword,rule.label,0.0,0,i)
        
        # Match and increment frequencies and probabilities
        for cword in allContextRules.iterkeys():
            for NP_C,rule in temp_instances:
                C = NP_C[1]
                if(cword in C):
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
        sorterRules.sort(key = (lambda r : r.freq), reverse = True)
        sorterRules.sort(key = (lambda r : r.prob), reverse = True)

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
        
        # Generate all posible context rules
        allSpellingRules = {}
        for NP_C,rule in temp_instances:
            NP = NP_C[0]
            split = NP.split(' ')
            for npword in split:
                if(npword not in allContextRules.keys()):
                    allSpellingRules[npword] = Rule("SPELLING",npword,rule.label,0.0,0,i)
        
        # Match and increment frequencies and probabilities
        for npword in allSpellingRules.iterkeys():
            for NP_C,rule in temp_instances:
                NP = NP_C[0]
                if(npword in NP):
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
        sorterRules.sort(key = (lambda r : r.freq), reverse = True)
        sorterRules.sort(key = (lambda r : r.prob), reverse = True)

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
                    pass#spelling[rule.word] = rule

bootstrapping()
printDict(context)
printDict(spelling)
#printDict(trainingSet)
#printDict(spelling)
#printDict(testSet)
#print(context)