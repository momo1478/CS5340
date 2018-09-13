import sys
from collections import defaultdict

dictionary = defaultdict(list) # word -> [(POS , ?Root)]
rules = []        # (FIX, actual fix, replace letters, POS origin, POS derived)
tests = []

def analyze(word, originPOS, derivedPOS):
    if(word in dictionary):
        root = word
        source = "morphology"
        if(len(dictionary[word][0]) == 2): # Has Root
            root = dictionary[word][0][1]
            POS  = dictionary[word][0][0]
        else:
            POS = dictionary[word][0]
        
        # Match POS in dictionary
        valid = False
        for entry in dictionary[word]:
            if( originPOS == entry or (len(dictionary[word]) > 1 and originPOS == entry[0])):
                valid = True

        return [word,derivedPOS,root,source] if valid else None
    else:
        for rule in rules:
            if(rule[0] == "PREFIX"):
                if(word.startswith(rule[1])):
                    newWord = word[len(rule[1]):]
                    if(rule[2] != "-"):
                        newWord = rule[2] + newWord
                    return analyze(newWord,rule[3],rule[4])
            else:
                if(word.endswith(rule[1])):
                    newWord = word[:-len(rule[1])]
                    if(rule[2] != "-"):
                        newWord = newWord + rule[2]
                    return analyze(newWord,rule[3],rule[4])
    
def analyzeWord(word):
    if(word in dictionary):
        root = word
        source = "dictionary"
        if(len(dictionary[word][0]) == 2): # Has Root
            root = dictionary[word][0][1]
            POS  = dictionary[word][0][0]
        else:
            POS = dictionary[word][0]

        return [word,POS,root,source]
    else:
        results = []
        for rule in rules:
            if(rule[0] == "PREFIX"):
                if(word.startswith(rule[1])):
                    newWord = word[len(rule[1]):]
                    if(rule[2] != "-"):
                        newWord = rule[2] + newWord
                    results.append(analyze(newWord,rule[3],rule[4]))
            else:
                if(word.endswith(rule[1])):
                    newWord = word[:-len(rule[1])]
                    if(rule[2] != "-"):
                        newWord = newWord + rule[2]
                    results.append(analyze(newWord,rule[3],rule[4]))
        
        if(all(result is None for result in results)):
            return [word,"noun",word,"default"]
        else:
            return filter(None,results)
 
    # if(word in dictionary or word in roots):
    #     if(word in roots):
    #         POS = rootPOS[word]
    #         word = roots[word]
    #         firstCall = False
    #     else:
    #         POS = dictionary[word]
    #     source = ("dictionary" if firstCall else "morphology")
    #     return [word,dictionary[word],word,source]
    # else:
    #     results = []
    #     for rule in rules:
    #         if(rule[0] == "PREFIX"):
    #             if(word.startswith(rule[1])):
    #                 newWord = word[len(rule[1]):]
    #                 if(rule[2] != "-"):
    #                     newWord = rule[2] + newWord
    #                 results.append(analyze(newWord, False, rule[4]))
    #         else:
    #             if(word.endswith(rule[1])):
    #                 newWord = word[:-len(rule[1])]
    #                 if(rule[2] != "-"):
    #                     newWord = newWord + rule[2]
    #                 results.append(analyze(newWord, False, rule[4]))
    #     print(results)
    #     if(all(result is None for result in results) and firstCall):
    #         # No rules apply
    #         source = "default"
    #         return [word, "noun", word, source]
    #     if(any(result is not None for result in results)):
    #         newRes = filter(None, results)
    #         return newRes
    #     return None

with open(sys.argv[1],'r') as f:
    for line in f:
        sp = line.split()
        if  (len(sp) == 2):
            dictionary[sp[0]].append((sp[1]))
        elif(len(sp) == 4):
            dictionary[sp[0]].append((sp[1],sp[3]))

with open(sys.argv[2],'r') as f:
    for line in f:
        s = line.split()
        rule = (s[0],s[1],s[2],s[3],s[5])
        rules.append(rule)

with open(sys.argv[3],'r') as f:
    for line in f:
        tests.append(line.strip())

for word in tests:
    results = analyzeWord(word)
    # print(results)
    if(isinstance(results[0],list) == False):
        print(word + " " + results[1] + " ROOT=" + results[2] + " SOURCE=" + results[3] )
    else:
        for result in results:
            print(word + " " + result[1] + " ROOT=" + result[2] + " SOURCE=" + result[3] )

    print("")
    