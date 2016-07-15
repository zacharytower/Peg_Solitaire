import copy

def main():

	i_board = [[True] * n for n in range(1,10)]
	i_board[0][0] = False

	board = [[False],
	[True, True],
	[True, True, True],
	[True, True, True, True],
	[True, True, True, True, True]] # 6 rows

	testBoard = [[True],
	[True,False],
	[False,True,False],
	[True, True,False, False],
	[False, True, True, True, True]]
	
	hashwall = '#' * 20
	for i, x in enumerate(pegSolitaireOneSolution(board)):
		print hashwall + 'GAME SOLUTION {}:'.format(i + 1) + hashwall
		
			
		printFormatted(x)

		raw_input()

def pegSolitaire(board, previousStates = []):
	'''
	generator function that generates solutions to boards. Recursive.
	INPUT: current board state
	OUTPUT: returns list of board states
	'''

	if gameLost(board): yield []
	if gameWon(board): yield previousStates + [board]

	
	for p in [x for x in possibleMoves(board) if gameLost(x) == False and x != []]: # iterate through valid game states

		# p is a 'board'-structured list in this example.
		# that is, it is a list of row values, each row containing as many boolean values
		# proportional to its index in the board plus one.

		
		solutions = [y for y in pegSolitaire(p, previousStates + [board]) if y != []]

		for solution in solutions:
			yield solution

def pegSolitaireOneSolution(board,previousStates = []):
	'''
	function that returns the first solution generated given the current board.
	very similar to pegSolitaire(), but only generates one solution.
	INPUT:  current board state
	OUTPUT: one solved board state (and history)
	'''
	if gameLost(board): return []
	if gameWon(board): return previousStates + [board]

	
	for p in [x for x in possibleMoves(board) if gameLost(x) == False and x != []]: # iterate through valid game states

		# p is a 'board'-structured list in this example.
		# that is, it is a list of row values, each row containing as many boolean values
		# proportional to its index in the board plus one.


		
		for e in [pegSolitaireOneSolution(p, previousStates + [board])]:

			if e != []:
				return e

	return []
		

def gameWon(board):

	return pegCount(board) == 1

def pegCount(board):
	x = 0
	for row in board:
		for element in row:
			if element == True: x += 1

	return x

def gameLost(board):

	return len(possibleMoves(board)) == 0 and pegCount(board) > 1

def printFormatted(board):
	for row in board:

		print row

	print '\n************************************'


def possibleMovesPoint(board,point, returnMods = False):

	'''
	function finds all the game states given a board and a peg that has to be moved.
	the point must be true.

	If returnMods is passed as True, then it will return {mod tuples : board states}.
	'''
	possible = [((-2,-2),(-1,-1)), ((-2,0),(-1,0)),
	((2,0),(1,0)),((2,2),(1,1)),
	((0,2),(0,1)),((0,-2),(0,-1))]

	gameStates = []
	gameDictionary = {}
	for possibleBoard in possibleMoves(board): #iterate through all possible game states.

		for mod in possible:
			try:

				if point[0] + mod[1][0] < 0 or\
				point[1] + mod[1][1] < 0 or \
				point[0] + mod[0][0] < 0 or \
				point[1] + mod[0][1] < 0:
					continue
				
				
				if possibleBoard[point[0]][point[1]] == False and \
				possibleBoard[point[0] + mod[1][0]][point[1] + mod[1][1]] == False and\
				possibleBoard[point[0] + mod[0][0]][point[1] + mod[0][1]] == True and \
				board[point[0]][point[1]] == True and\
				board[point[0] + mod[1][0]][point[1] + mod[1][1]] == True and \
				board[point[0] + mod[0][0]][point[1] + mod[0][1]] == False: # if game state moved the piece in question

					if returnMods == True: # the mod value is requested for return,
						gameDictionary[mod] = [possibleBoard]

					else: # the states are needed,
						gameStates += [possibleBoard]

			except IndexError: continue


	if returnMods == True: return gameDictionary
	else: return gameStates

def possibleMoves(board):

	'''
	function returns all possible game states in the next move.
	INPUT: board state (list of lists)
	OUTPUT: list of possible board states

	This function is stable and works properly.
	'''

	# all these are are the "modifiers" to the indeces of the values.
	# these represent all of the possible moves for one piece.
	# if the move goes out of bounds, an IndexError will be raised and
	# it will be skipped.

	possible = [((-2,-2),(-1,-1)), ((-2,0),(-1,0)),
	((2,0),(1,0)),((2,2),(1,1)),
	((0,2),(0,1)),((0,-2),(0,-1))] # chinese junk

	returnList = []
	board_copy = copy.deepcopy(board)
	for i, row in enumerate(board):

		for j, item in enumerate(row): # for peg in row

			
			if item == False:
				continue

			for moveTuple in possible: # iterate through possible moves

				outmostMod, middleMod = moveTuple
				
				try:
					if i + outmostMod[0] < 0 or \
					j + outmostMod[1] < 0 or \
					i + middleMod[0] < 0 or \
					j + middleMod[1] < 0:

						continue

					if board[i + outmostMod[0]][j + outmostMod[1]] == False and \
					 board[i + middleMod[0]][j + middleMod[1]] == True: # a jump is possible
					 	
					 	
						modList = copy.deepcopy(board) # was being funny - modifications to modList
						# resulted in modifications to board for some reason.

						modList[i + outmostMod[0]][j + outmostMod[1]] = True
						modList[i + middleMod[0]][j + middleMod[1]] = False

						modList[i][j] = False
						
						returnList += [modList]


				except IndexError:

					continue

	return returnList

def weedCopies(array):

	'''
	this function returns an array with any repeat elements exterminated.
	'''

	newList = []
	for element in array:
		if element not in newList:
			newList.append(element)

	return newList


if __name__ == '__main__':
	main()