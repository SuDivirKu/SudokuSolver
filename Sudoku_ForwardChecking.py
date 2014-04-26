#!/usr/bin/env python
import struct, string, math

#this will be the game object your player will manipulate
class SudokuBoard:

    #the constructor for the SudokuBoard
    def __init__(self, size, board, checks):
      self.BoardSize = size #the size of the board
      self.CurrentGameboard= board #the current state of the game board
      self.checks = checks

    #This function will create a new sudoku board object
    #with the input value placed on the GameBoard row and col are
    #both zero-indexed
    def set_value(self, row, col, value):
        self.CurrentGameboard[row][col]=value #add the value to the appropriate position on the board
        return SudokuBoard(self.BoardSize, self.CurrentGameboard, self.checks) #return a new board of the same size with the value added

    def __repr__(self):
        """ returns a string representation for a SudokuBoard """
        s = dashes = "".join([ ' -' for i in range(self.BoardSize) ])
        for row in range( self.BoardSize ):
            sRow = '|'
            for col in range( self.BoardSize ):
                sRow += str(self.CurrentGameboard[row][col]) + '|'
            s += '\n' + sRow + '\n' + dashes
        return s

    


# parse_file
#this function will parse a sudoku text file (like those posted on the website)
#into a BoardSize, and a 2d array [row,col] which holds the value of each cell.
#array elements with a value of 0 are considered to be empty

def parse_file(filename):
    f = open(filename, 'r')
    BoardSize = int( f.readline())
    NumVals = int(f.readline())

    #initialize a blank board
    board= [ [ 0 for i in range(BoardSize) ] for j in range(BoardSize) ]

    #populate the board with initial values
    for i in range(NumVals):
        line = f.readline()
        chars = line.split()
        row = int(chars[0])
        col = int(chars[1])
        val = int(chars[2])
        board[row-1][col-1]=val
    
    return board
    



#takes in an array representing a sudoku board and tests to
#see if it has been filled in correctly
def iscomplete( BoardArray ):
        size = len(BoardArray)
        subsquare = int(math.sqrt(size))

        #check each cell on the board for a 0, or if the value of the cell
        #is present elsewhere within the same row, column, or square
        for row in range(size):
            for col in range(size):
                """
                if BoardArray[row][col]==0:
                    return False
                """
                for i in range(size):
                    if ((BoardArray[row][i] == BoardArray[row][col]) and i != col and BoardArray[row][col] != 0):
                        return False
                    if ((BoardArray[i][col] == BoardArray[row][col]) and i != row and BoardArray[row][col] != 0):
                        return False
                #determine which square the cell is in
                SquareRow = row // subsquare
                SquareCol = col // subsquare
                for i in range(subsquare):
                    for j in range(subsquare):
                        if((BoardArray[SquareRow*subsquare + i][SquareCol*subsquare + j] == BoardArray[row][col])
                           and (SquareRow*subsquare + i != row) and (SquareCol*subsquare + j != col)
                              and BoardArray[row][col] != 0):
                            return False
        return True

# creates a SudokuBoard object initialized with values from a text file like those found on the course website
def init_board( file_name, checks ):
    board = parse_file(file_name)
    return SudokuBoard(len(board), board, checks)

""" -------------------------------- Backtracking ---------------------------------"""

# student code
def backtracking( sudoku ):
    # stop when limit is reached
    ##sudoku.checks -= 1
    ##if sudoku.checks<0: return False
    # get an unassigned cell
    row, col = getUnassignedVar( sudoku )
    if (row == -1 and col == -1): return True
    # try different values for a cell
    for val in range(1, sudoku.BoardSize+1):
        sudoku.set_value(row,col,val)
        sudoku.checks -= 1
        if sudoku.checks<0: return False
        if iscomplete(sudoku.CurrentGameboard) and backtracking( sudoku ):
            return True
        sudoku.set_value(row,col,0)
    return False

def getUnassignedVar( sudoku ):
    for row in range(sudoku.BoardSize):
        for col in range(sudoku.BoardSize):
            if (sudoku.CurrentGameboard[row][col] == 0): return row, col
    return -1, -1

""" -------------------------------- Forward Checking ---------------------------------"""

def createPossMatrix( sudoku ):
    poss = [[range(1,sudoku.BoardSize+1) for row in range(sudoku.BoardSize)] for col in range(sudoku.BoardSize)]
    return poss

def updatePoss( poss, r, c, val ):
    size = len(poss)
    for x in range(size):
        if (x != c and val in poss[r][x]): poss[r][x].remove(val)   # Eliminates repeating possibilites in the same row
        if (x != r and val in poss[x][c]): poss[x][c].remove(val)   # Eliminates repeating possibilites in the same Column
        #determine which square the cell is in (Updates within the grid)
        subsquare = int(math.sqrt(size))
        SquareRow = r // subsquare
        SquareCol = c // subsquare
        for i in range(subsquare):
            for j in range(subsquare):
                if(val in poss[SquareRow*subsquare + i][SquareCol*subsquare + j]
                   and (SquareRow*subsquare + i != r) and (SquareCol*subsquare + j != c)):
                    poss[SquareRow*subsquare + i][SquareCol*subsquare + j].remove(val)
    return poss



def AddtoPoss( poss, r, c, val ): # This function will be used to re-add the values to the rows and columns (same as updatePoss, but reverse purpose)
    size = len(poss)
    for x in range(size):
        if (x != c and val not in poss[r][x]): poss[r][x].append(val)   # Adds possibilites in the same row
        if (x != r and val not in poss[x][c]): poss[x][c].append(val)   # Adds possibilites in the same Column
        #determine which square the cell is in (Updates within the grid)
        subsquare = int(math.sqrt(size))
        SquareRow = r // subsquare
        SquareCol = c // subsquare
        for i in range(subsquare):
            for j in range(subsquare):
                if(val not in poss[SquareRow*subsquare + i][SquareCol*subsquare + j]
                   and (SquareRow*subsquare + i != r) and (SquareCol*subsquare + j != c)):
                    poss[SquareRow*subsquare + i][SquareCol*subsquare + j].append(val)
    return poss

def preProcess( sudoku ):
    poss = createPossMatrix( sudoku )
    for row in range(sudoku.BoardSize):
        for col in range(sudoku.BoardSize):
            val = sudoku.CurrentGameboard[row][col]
            if (val != 0):
                poss[row][col] = []
                poss = updatePoss (poss, row, col, val)
    return poss

def PrintPoss(poss):    # This function is to display the possibility matrix
    print "------Possibilty Matrix--------"
    for x in poss:
        print x
    return "-----------------------------"

def forwardChecking( sudoku, poss ):
    # stop when limit is reached
    ##sudoku.checks -= 1
    ##if sudoku.checks<0: return False
    # get an unassigned cell
    row, col = getUnassignedVar( sudoku )
    if (row == -1 and col == -1): return True
    # try different values for a cell
    for val in poss[row][col]:          # Here we loop only through the values in Possibility Matrix
        sudoku.set_value(row,col,val)
        sudoku.checks -= 1
        if sudoku.checks<0: return False
        updatePoss(poss,row,col,val)    # Update the Possibility Matrix
        if iscomplete(sudoku.CurrentGameboard) and forwardChecking( sudoku, poss ):
            return True
        sudoku.set_value(row,col,0)
        AddtoPoss( poss, row, col, val ) # If the value did not return a solution, we need re-add them to the other elements after removing them earlier
    return False

# test code
testBoard = init_board( '4x4-1.txt', 10000 )
print 'Original Board:\n', testBoard
#print '\nSolved: %s\n' % backtracking( testBoard )
print 'Returned Board:\n', testBoard
poss = preProcess( testBoard )
print '\nSolved: %s\n' % forwardChecking( testBoard,poss )
print 'Returned Board:\n', testBoard
print testBoard.checks
