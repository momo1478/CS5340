import sys
import itertools
from collections import defaultdict
from sets import Set

board = []
fullBoard = []

grammar = defaultdict(list)
words = defaultdict(list)

probs = {}
prob = False

#Row = board[x][0]
#Col = board[x]
def getAllInRow(board,r,c):
	res = Set()
	for x in xrange(c):
		for item in board[x]:
			res.update(item)
	try:
		res = list(res).remove("-")
	except ValueError:
		pass
	return list(res) if res != None else []

def getAllInRowFull(board,r,c):
	res = []
	for x in xrange(c):
		for item in fullBoard[x]:
			res.append(item)
	res = [e for e in res if e[0] != "-"]
	res = [x for x in res if x != []]
	if(isinstance(res[0],list)):
		return list(set(res[0]))
	else:
		return list(set(res))

def getAllInColumn(board,r,c):
	res = Set()
	for item in board[r]:
		res.update(item)
	try:
		res = list(res).remove("-")
	except ValueError:
		pass
	return list(res) if res != None else []

def getAllInColumnFull(board,r,c):
	res = []
	for item in fullBoard[r]:
		res.append(item)
	res = [e for e in res if len(e) > 0 and e[0] != "-"]
	res = [x for x in res if x != []]
	if(res != [] and isinstance(res[0],list)):
		return list(set(res[0]))
	else:
		return list(set(res))
		
def CKY(sentence):
	for c in xrange(len(sentence)):
		if(sentence[c] in words):
			POS = words[sentence[c]]
			board[c][c] = board[c][c] + POS
			for pos in POS:
				fullBoard[c][c].append( (pos,sentence[c],probs[(sentence[c],''.join(pos))]) )
		else:
			board[c][c] = "-"
			fullBoard[c][c] = []

		for r in xrange(c - 1,-1,-1):
			for s in xrange(r + 1, c + 1):
				rowConst = getAllInRow(board,r, s)
				colConst = getAllInColumn(board, s,c)
				fullRowConst = getAllInRowFull(board,r,s)
				fullColConst = getAllInColumnFull(board,s,c)
				allConstPairs = [(x, y) for x in rowConst for y in colConst]
				fullAllConstPairs = [(x, y) for x in fullRowConst for y in fullColConst]
				#print("fullRowConst = " + str(fullRowConst))
				#print("fullColConst = " + str(fullColConst))
				#print("Processing : " + str((r,s)))
				#print("rowConst = " + str(rowConst))
				#print("colConst = " + str(colConst))
				#print("allConstPairs = " + str(allConstPairs))
				#print("fullallConstPairs = " + str(fullAllConstPairs))
				for pairs in allConstPairs:
					ruleToSearchFor = ' '.join(pairs)
					grammarToAdd = grammar.get(ruleToSearchFor)
					if(grammarToAdd != None):
						board[c][r] = board[c][r] + grammarToAdd
				if(len(board[c][r]) == 0):
					 board[c][r] = board[c][r] + list("-")
				
				for fullPair in fullAllConstPairs:
					ruleToSearchFor = ' '.join([fullPair[0][0],fullPair[1][0]])
					grammarToAdd = grammar.get(ruleToSearchFor)
					if(grammarToAdd != None):
						wordToAdd = fullPair[0][1] + " " + fullPair[1][1]
						probToAdd = fullPair[0][2] * fullPair[1][2] * probs[(ruleToSearchFor,grammarToAdd[0])]
						fullGrammarToAdd = (grammarToAdd[0], wordToAdd , probToAdd )
						
						fullBoard[c][r].append( fullGrammarToAdd )
				if(len(fullBoard[c][r]) == 0):
					 fullBoard[c][r].append( ("-","-","-") )
	
	print("")
	print("")
	print("~~~~~~Internal Representation of CKY Algorithm Board~~~~~~")
	print(fullBoard)
	print("~~~~~~Internal Representation of CKY Algorithm Board~~~~~~")
	print("")
	print("")
	
	# for c in xrange(len(sentence)):
	# 	for item in fullBoard[c]:
	# 		print("item is " + str(item))
	#print("Sentence : " + str(sentence))
	#print(fullBoard)
	#print(board)

	allSentences = []
	maxSProb = {}
	SCount = 0
	for col in xrange(len(fullBoard)):
		for item in fullBoard[col][0]:
			if(item[0] == "S"):
				allSentences.append(item)
				SCount+=1
				currentMaxSProb = maxSProb.get(col) 
				if currentMaxSProb == None or currentMaxSProb < item[1]:
					maxSProb[col] = item[2]
	if not allSentences:
		allSentences.append(("","",""))

	if(prob):
		print("PARSING SENTENCE: " + str(allSentences[0][1]))
		print("NUMBER OF PARSES FOUND: " + str(len(maxSProb)))
		print("TABLE:")
		for row in xrange(len(fullBoard)):
			for col in xrange(len(fullBoard[row])):
				if( any("S" in x[0] for x in fullBoard[row][col]) ):
					try:
						stat = ("%0.4f" % round(maxSProb[row],4))
					except:
						stat = "-"
					print("cell[" + str(col + 1) + "," + str(row + 1) + "]: " + "S" + "(" + stat + ")")
				else:
					join = ""
					for tup in fullBoard[row][col]:
						try:
							stat = ("%0.4f" % round(tup[2],4))
						except:
							stat = "-"
						join += tup[0] + "(" + stat + ") "
					print("cell[" + str(col + 1) + "," + str(row + 1) + "]: " + join)
	else:
		print("PARSING SENTENCE: " + str(allSentences[0][1]))
		print("NUMBER OF PARSES FOUND: " + str(SCount))
		print("TABLE:")
		for row in xrange(len(fullBoard)):
			for col in xrange(len(fullBoard[row])):
				print("cell[" + str(col + 1) + "," + str(row + 1) + "]: " + ' '.join(x[0] for x in fullBoard[row][col]))
						
prob = (len(sys.argv) == 4 and sys.argv[3] == "-prob")

with open(sys.argv[1],'r') as f:
    for line in f:
        sp = line.split()
    	partOne = sp[0]
    	partTwo = ' '.join(sp[2:len(sp)-1])
    	partThree = float(sp[len(sp) - 1])
        grammar[partTwo].append(partOne)
        probs[(partTwo,partOne)] = partThree
        if(len(sp) == 4):
        	words[sp[2]].append(sp[0])
print("")
with open(sys.argv[2],'r') as f:
	for line in f:
		sp = line.split()
		board = [[[] for x in range(y + 1)] for y in range(len(sp))]
		fullBoard = [[[] for x in range(y + 1)] for y in range(len(sp))]
		CKY(sp)
		print("")
# print("Grammar")
# print(grammar)
# print("Probs")
# print(probs)
# print("Words")
# print(words)