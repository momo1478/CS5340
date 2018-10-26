from sys import argv
from collections import namedtuple
import json

# { NP : Context }
trainingSet = {}
# { NP : Context }
testSet = {}

# { word : Rule}
spelling = {}
# { word : Rule}
context = {}

def printDict(d):
    for key, val in d.items():
        print(str(key) + " : " + str(val))

class Rule(object):
   def __init__(self,t,word,label,prob,freq):
       self.t = t
       self.word = word
       self.label = label
       self.prob = prob
       self.freq = freq
   
   def __eq__(self,other):
       return self.t == other.t and self.word == other.word and \
              self.label == other.label and self.prob == other.prob and \
              self.freq == other.freq
              
   def __repr__(self):
       return self.t + " " + "Contains("+self.word+") -> "+self.label+" (prob="+str(self.prob)+" ; freq="+str(self.freq)+")"

with open(argv[1]) as f:
    for line in f:
        split = line.split(' ')
        t = split[0]
        word = split[1][9:(str(split[1])).find(")")]
        label = split[3].strip("\n")
        prob = -1.0
        freq = -1
        spelling[word] = Rule(t,word,label,prob,freq)

with open(argv[2]) as f:
    while True:
        contextLine = str(f.readline().strip('\n'))
        NPLine      = str(f.readline().strip('\n'))
        blankLine   = f.readline()
        if not blankLine :
            break
        else:
            trainingSet[' '.join(NPLine.split(' ')[1:])] = ' '.join(contextLine.split(' ')[1:])

with open(argv[3]) as f:
    while True:
        contextLine = str(f.readline().strip('\n'))
        NPLine      = str(f.readline().strip('\n'))
        blankLine   = f.readline()
        if not blankLine :
            break
        else:
            testSet[' '.join(NPLine.split(' ')[1:])] = ' '.join(contextLine.split(' ')[1:])

def bootstrapping():
    for i in range(3):
        # {Context : RuleMatched}
        labeled_instances = {}
        for NP , C in trainingSet.items():
            for rule in spelling.values():
                if (rule.word in NP):
                    labeled_instances[C] = rule
        
        printDict(labeled_instances)
        
            
bootstrapping()
#printDict(trainingSet)
#printDict(spelling)
#printDict(testSet)
#print(context)
