import sys
import itertools
from collections import defaultdict
from sets import Set

board = []
fullBoard = []

grammar = defaultdict(list)
words = defaultdict(list)

probs = {}

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
	return list(res)

def getAllInRowFull(board,r,c):
	res = []
	for x in xrange(c):
		for item in fullBoard[x]:
			res = res + item
	res = [e for e in res if e[0] != "-"]
	
	return list(set(res))

def getAllInColumn(board,r,c):
	res = Set()
	for item in board[r]:
		res.update(item)
	try:
		res = list(res).remove("-")
	except ValueError:
		pass
	return list(res)

def getAllInColumnFull(board,r,c):
	res = []
	for item in fullBoard[r]:
		res = res + item
	
	res = [e for e in res if e[0] != "-"]

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
			fullBoard[c][c] = ("-","-","-")

		for r in xrange(c - 1,-1,-1):
			for s in xrange(r + 1, c + 1):
				rowConst = getAllInRow(board,r, s)
				colConst = getAllInColumn(board, s,c)
				fullRowConst = getAllInRowFull(board,r,s)
				fullColConst = getAllInColumnFull(board,s,c)
				print("fullRowConst = " + str(fullRowConst))
				print("fullColConst = " + str(fullColConst))
				allConstPairs = [(x, y) for x in rowConst for y in colConst]
				#print("Processing : " + str((r,s)))
				#print("rowConst = " + str(rowConst))
				#print("colConst = " + str(colConst))
				#print("allConstPairs = " + str(allConstPairs))
				for pairs in allConstPairs:
					ruleToSearchFor = ' '.join(pairs)
					grammarToAdd = grammar.get(ruleToSearchFor)
					if(grammarToAdd != None):
						board[c][r] = board[c][r] + grammarToAdd
				if(len(board[c][r]) == 0):
					 board[c][r] = board[c][r] + "-"
	
	print("Sentence : " + str(sentence))
	print(fullBoard)

prob = len(sys.argv) == 4 and sys.argv[3] == "-prob"

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

with open(sys.argv[2],'r') as f:
    for line in f:
        sp = line.split()
        board = [[[] for x in range(y + 1)] for y in range(len(sp))]
        fullBoard = [[[] for x in range(y + 1)] for y in range(len(sp))]
        CKY(sp)

print("Grammar")
print(grammar)
# print("Probs")
# print(probs)
# print("Words")
# print(words)