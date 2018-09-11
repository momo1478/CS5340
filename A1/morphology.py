import sys;

dictionary = {} # word -> POS
roots = {}      # word -> root
rules = []      # (FIX, actual fix, replace letters, POS origin, POS derived)
tests = []

def analyze(word,firstCall,POS):
    #result = [word,POS,root,source]

    if(word in dictionary):
        source = ("dictionary" if firstCall else "morphology")
        return [word,dictionary[word],word,source]
    elif(word in roots):
        return analyze(roots[word], True, dictionary[roots[word]])
    else:
        for rule in rules:
            if(rule[0] == "PREFIX"):
                if(word.startswith(rule[1])):
                    newWord = word[len(rule[1]):]
                    if(rule[2] != "-"):
                        newWord = rule[2] + newWord
                    return analyze(newWord, False, POS = rule[4])
            else:
                if(word.endswith(rule[1])):
                    newWord = word[:-len(rule[1])]
                    if(rule[2] != "-"):
                        newWord = newWord + rule[2]
                    return analyze(newWord, False, POS = rule[4])
        
        # No rules apply
        source = "default"
        dictionary[word] = "noun"
        return [word, "noun", word, source]


with open(sys.argv[1],'r') as f:
    for line in f:
        sp = line.split()
        if  (len(sp) == 2):
            dictionary[sp[0]] = sp[1]
        elif(len(sp) == 4):
            roots[sp[0]] = sp[3]

with open(sys.argv[2],'r') as f:
    for line in f:
        s = line.split()
        rule = (s[0],s[1],s[2],s[3],s[5])
        rules.append(rule)

with open(sys.argv[3],'r') as f:
    for line in f:
        tests.append(line.strip())

for word in tests:
    result = analyze(word, firstCall = True, POS = "")
    form = "{0: <15} {1: <15} ROOT={2: <15} SOURCE={3: <15}"
    print(form.format(word,result[1],result[2],result[3]))