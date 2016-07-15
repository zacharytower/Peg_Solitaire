import peg
import pygame, sys, copy, random, time

from pygame.locals import *

# RGB Color definitions

RED = 	(255,  0,  0)
BLUE =  (  0,  0,255)
GREEN = (  0,255,  0)
BLACK = (  0,  0,  0)
WHITE = (255,255,255)

N_RED = (232, 14,116)
N_GREEN=( 14,232,130)
N_BLUE =( 21, 14,232)
N_YELLOW = (225,232,14)


# Game Default Definitions
randomizeColors = True

if randomizeColors:

	N_RED = [random.randint(0,255) for x in range(3)]
	N_GREEN = [random.randint(0,255) for x in range(3)]
	N_BLUE = [random.randint(0,255) for x in range(3)]
	N_YELLOW = [random.randint(0,255) for x in range(3)]

	WHITE = [random.randint(0,255) for x in range(3)]
	BLACK = [random.randint(0,255) for x in range(3)]


rowCountDefault = 5
try:
	rowCountDefault = int(sys.argv[1])

except ValueError:
	print 'Value passed not a valid integer: Defaulting to 5 rows.'
	
except IndexError: pass
	
	

windowWidth = abs(2 * (-1 * (rowCountDefault/2 * 100) - 100)) # formula for calculating board width
windowHeight = 200 + (rowCountDefault + 1) * 50

emptyBoard = [[True] * n for n in range(1,rowCountDefault + 1)]



# Pygame Global Variables1

FPS = 30
FPSCLOCK = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((windowWidth, windowHeight))
pygame.display.set_caption('Peg Solitaire')

pygame.init()

class Board(object):

	def __init__(self, startBoard = emptyBoard, rowCount = rowCountDefault, pegRadius = 13, backdropColor = N_RED, pegColor = N_GREEN,
		textColor = N_BLUE, alternateColor = N_YELLOW):

		self.board = copy.deepcopy(startBoard)
		self.rowCount = rowCount
		self.pegRadius = pegRadius

		self.backdropColor = backdropColor
		self.pegColor = pegColor
		self.textColor = textColor

		self.alternateColorList =[]
		self.alternateColor = alternateColor

		self.pegMovedOn = None
		self.message = ''

	def generateSolution(self):
		self.solution = peg.pegSolitaireOneSolution(self.board)

	def generatePointDictionary(self):
		'''
		this method generates a dictionary of points on the board to boolean
		values, which correspond to whether or not the peg is present on the
		board.
		'''
		self.generatePoints()
		self.pointDictionary = {}

		
		for i, row in enumerate(self.pointList):
			for j, element in enumerate(row):

				self.pointDictionary[element] = self.board[i][j] == True

	def generatePoints(self):

		'''
		this method generates a list of points onto which the pegs will be 
		drawn upon.
		It works with any value of rowCount.
		It also generates points A,B, and C.

					* A
				/		\
			/				\
		  C*-----------------*B
		'''
		self.pointList = []


		for row in range(1, self.rowCount + 1):
			yVal = 50 * row + 50

			if row == 1: # if it is the first row
				self.pointList.append([(windowWidth / 2, 100)]) # first peg is always here
				firstPeg = self.pointList[0][0]
				
			else:
				
				self.pointList.append([(x,yVal) for x in range(firstPeg[0] - (50 * (row - 1)), \
					firstPeg[0] + (50 * (row - 1)) + 1, 100)])

		self.a = (firstPeg[0], firstPeg[1] - 50)
		self.b = (self.pointList[-1][-1][0] + 100, self.pointList[-1][-1][1] + 50)
		self.c = (self.pointList[-1][0][0] - 100, self.pointList[-1][0][1] + 50)

		self.underBoardPos = ((self.b[0] - self.c[0]) / 2, self.b[1] + 75)

	def findNextBestMove(self):
		self.generateSolution()
		self.nextBest = self.solution[0]

	def drawBoard(self):
		'''
		draws the current board to DISPLAYSURF.
		'''

		self.generatePointDictionary()

		# first, lets display the backdrop.
		# a triangle in all of its majesty.
		# points lying on A,B,C.

		pygame.draw.polygon(DISPLAYSURF, self.backdropColor, [self.a, self.b, self.c])

		# lets draw all of the true points onto the board as pegs and the false as holes.

		for i,row in enumerate(self.pointList):
			for j,point in enumerate(row):

				if self.pointDictionary[point] == True: # the peg is in

					if self.pegMovedOn == (i,j): # a player is hovering over a peg,
						pegColor = self.alternateColor

					else:
						pegColor = self.pegColor
					
					pygame.draw.circle(DISPLAYSURF, pegColor, point, self.pegRadius)


				else: # the peg is not in
					

					if [i,j] not in self.alternateColorList:
						
						colorToDraw = BLACK

					else:

						colorToDraw = self.alternateColor

					pygame.draw.circle(DISPLAYSURF, colorToDraw, point, self.pegRadius / 2)

		if self.message != None:
			self.displayText(self.message, self.underBoardPos)

		

	def findPegClicked(self, clickPos):

		'''
		function processes click on the board and returns points (i,j), where the peg clicked on is at board[i][j]
		if no peg or hole was clicked, the function will return -1.
		'''

		assert len(clickPos) == 2, 'clickPos is illegitimate: len is {} and type is {}.'.format(len(clickPos), type(clickPos))

		# first, lets find all the possible pegs that could have been clicked.

		for i,row in enumerate(self.pointList):
			for j, point in enumerate(row):


				if self.pointDictionary[point] == True:
					divisor = 1
				else:
					divisor = 2


				
				if (clickPos[0] - point[0]) ** 2 + (clickPos[1] - point[1]) ** 2 <= (self.pegRadius / 1) ** 2: # it is in,
					return (i,j)

		# if no peg has been found by now, return -1
		return -1

	def moveSelected(self, pos, specifyMod = None):

		'''
		method moves the peg clicked. If there is multiple options, this method will call the
		presentOptions method which will get the user response.

		If this method completed successfully, it will return 0.
		If it had to present options, it will return -1.
		'''

		boards = peg.possibleMovesPoint(self.board, pos)
		mods = peg.possibleMovesPoint(self.board, pos, True)

		boards = peg.weedCopies(boards)
		
		if specifyMod != None:
			
			self.board = mods[specifyMod]
			self.alternateColorList = []
			#print self.board
			return 0

		if len(boards) == 1: # there is only one possible move
			self.board = boards[0]
			return 0

		else: # there are multiple possible moves
			self.tempPos = pos
			self.tempMods = mods

			self.alternateColorList = []
			for mod in mods:
				outMod = mod[0]
				self.alternateColorList.append([pos[0] + outMod[0], pos[1] + outMod[1]])

			
			return -1

	def hasWon(self):

		'''
		method determines if the current board is winner.
		'''
		return peg.gameWon(self.board)

	def hasLost(self):

		'''
		method determines if the current board is loser.
		'''

		return peg.gameLost(self.board)

	def displayText(self,text,pos, textSize = 20):

		'''
		displays string 'text' at position 'pos'
		you may also define the text size.
		'''
		fontObj = pygame.font.Font('/usr/share/fonts/truetype/droid/DroidSerif-Bold.ttf',textSize)
		textSurfaceObj = fontObj.render(text, True, self.textColor)

		textRectObj = textSurfaceObj.get_rect()
		textRectObj.center = (pos)

		DISPLAYSURF.blit(textSurfaceObj, textRectObj)
		

	def youWin(self):

		assert self.hasWon() == True, 'player has not won.'
		
		text = 'You\'re Winner!'
		self.displayText(text, self.underBoardPos, 32)

		for x in range(4): # this should always be an even number (or else the colors will be swapped when it ends)
			self.pegColor, self.backdropColor = self.backdropColor, self.pegColor # swap the colors
			self.drawBoard()

			pygame.time.delay(700) # delay for 7/10ths of a second (700ms)

		self.resetBoard()

	def youLose(self):
		assert self.hasLost() == True, 'player has not lost'


		text = 'You Lose.'
		self.message = text
		self.drawBoard()
		pygame.display.update()
		
		time.sleep(3)# delay for four seconds.

		self.resetBoard()


	def resetBoard(self):

		self.board = copy.deepcopy(emptyBoard)

	def solveBoard(self):

		self.generateSolution()

		
		if len(self.solution) == 0:
			return -1

		for board in self.solution:

			self.board = board

			DISPLAYSURF.fill(WHITE)
			self.drawBoard()

			pygame.display.update()
			FPSCLOCK.tick(FPS)
			basicEventHandle()
			pygame.time.delay(500)

		pygame.time.delay(3000)
		self.resetBoard()
		return 0

	def boardUntouched(self):

		return self.board == emptyBoard

def basicEventHandle():

	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
def main():
 	
	mainBoardObj = Board() # constructs board object with all defaults.
	optionsPresented = False
	oldToMove = None

	firstPick = True

	typedCharacters = ''

	originalPegColor, originalBackdropColor = mainBoardObj.pegColor, mainBoardObj.backdropColor
	while True:
		DISPLAYSURF.fill(WHITE)

		for event in pygame.event.get():

			if event.type == QUIT:
				pygame.quit()
				sys.exit()

			if event.type == MOUSEBUTTONDOWN: # the mouse was clicked lickety split


				pos = event.pos # location where mouse was clicked.

				toMove = mainBoardObj.findPegClicked(pos) # returns index of peg clicked.
				
				if toMove != -1:

					if firstPick == True: # it is the first pick (and the player must choose the first peg to be removed from the board)
						
						firstPick = False
						mainBoardObj.board[toMove[0]][toMove[1]] = False

						break
					if len(peg.possibleMovesPoint(mainBoardObj.board,toMove)) == 0 and optionsPresented == False:

						break

					if optionsPresented == True: # the player picked an option 

						# toMove is now the option selection,
						# oldToMove is the original peg selection which had multiple possible moves.

						if oldToMove == toMove:
							mainBoardObj.alternateColorList = []
							oldToMove = None
							optionsPresented = False
							toMove = None
							break

						
						if toMove != -1:
							for mod in peg.possibleMovesPoint(mainBoardObj.board, oldToMove, True).keys():
								outMod = mod[0]
								#print '{} + mod({}) =  {}'.format((toMove[0] + outMod[0], toMove[1] + outMod[1]), mod[0], toMove)
								if (oldToMove[0] + outMod[0], oldToMove[1] + outMod[1]) == toMove:
									#print 'triggered'
									
									mainBoardObj.moveSelected(oldToMove, mod)
									mainBoardObj.board = mainBoardObj.board[0]

									oldToMove = None
									optionsPresented = False
									#print mainBoardObj.board
									break

							break
									
						

					if mainBoardObj.board[toMove[0]][toMove[1]] == True: # the peg is activated,
						exitValue = mainBoardObj.moveSelected(toMove)

						if exitValue == -1: # there are multiple options of where to move, 
							# the options will have already been presented,
							optionsPresented = True
							oldToMove = toMove
				


				
				if mainBoardObj.hasWon():
					mainBoardObj.youWin()
					firstPick = True

					mainBoardObj.message = ''

					break

				if mainBoardObj.hasLost():
					mainBoardObj.youLose()
					firstPick = True

					mainBoardObj.message = None
					break

			elif event.type == KEYDOWN:

				if event.key == K_LSHIFT:
					
					mainBoardObj.pegColor = originalBackdropColor

				

				else:
					try:
						typedCharacters += chr(event.key)

					except ValueError:
						pass

					secretSolveWord = 'zzz'
					
					if typedCharacters.endswith(secretSolveWord):

						mainBoardObj.message = 'Get Catfished ;)'
						mainBoardObj.drawBoard()
						time.sleep(2)

						pygame.display.update()


						rv = mainBoardObj.solveBoard()
						

						if rv == 0:
							firstPick = True

						elif rv == -1:
							mainBoardObj.message = 'Board is unsolvable! :P'
							pygame.display.update()
							time.sleep(2)

						mainBoardObj.message = ''

						typedCharacters = ''

			elif event.type == KEYUP:

				if event.key == K_LSHIFT:
					mainBoardObj.pegColor = originalPegColor

			elif event.type == MOUSEMOTION: # the mouse was moved,
				movedToPos = event.pos

				movedToIndeces = mainBoardObj.findPegClicked(movedToPos) # the peg was not clicked to in this instance

				if movedToIndeces != -1: # a peg was moved onto.
					mainBoardObj.pegMovedOn = movedToIndeces
				else:
					mainBoardObj.pegMovedOn = None

				





		mainBoardObj.drawBoard()
		

		pygame.display.update()
		FPSCLOCK.tick(FPS)

if __name__ == '__main__':
	main()
