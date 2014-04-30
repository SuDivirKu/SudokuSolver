#!/usr/bin/env python
import struct, string, math, copy
from time import time

# this will be the game object your player will manipulate
class SudokuBoard:

    # the constructor for the SudokuBoard
    def __init__( self, size, board, numChecks ):
      self.BoardSize = size #the size of the board
      self.CurrentGameboard= board #the current state of the game board
      self.numChecks = numChecks

    # This function will create a new sudoku board object
    # with the input value placed on the GameBoard row and col are
    # both zero-indexed
    def set_value( self, row, col, value ):
        self.CurrentGameboard[row][col]=value #add the value to the appropriate position on the board
        return SudokuBoard( self.BoardSize, self.CurrentGameboard, self.numChecks ) #return a new board of the same size with the value added

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
# this function will parse a sudoku text file (like those posted on the website)
# into a BoardSize, and a 2d array [row,col] which holds the value of each cell.
# array elements with a value of 0 are considered to be empty

def parse_file(filename):
    f = open(filename, 'r')
    BoardSize = int( f.readline())
    NumVals = int(f.readline())

    # initialize a blank board
    board= [ [ 0 for i in range(BoardSize) ] for j in range(BoardSize) ]

    # populate the board with initial values
    for i in range(NumVals):
        line = f.readline()
        chars = line.split()
        row = int(chars[0])
        col = int(chars[1])
        val = int(chars[2])
        board[row-1][col-1]=val
    
    return board


# creates a SudokuBoard object initialized with values from a text file like those found on the course website
def init_board( file_name ):
    board = parse_file(file_name)
    return SudokuBoard( len(board), board, 0 )


# checks if a test value will be consistent with the board
def isConsistent( BoardArray, testCellRow, testCellCol, testCellVal ):
        size = len(BoardArray)
        subsquare = int(math.sqrt(size))

        # check if any other cell in the row, column, or grid of the test cell has the test value
        for i in range(size):
            if ( (BoardArray[testCellRow][i] == testCellVal) or (BoardArray[i][testCellCol] == testCellVal) ):
                return False
            
            # determine which square the cell is in
            SquareRow = testCellRow // subsquare
            SquareCol = testCellCol // subsquare
            for i in range(subsquare):
                for j in range(subsquare):
                    if( BoardArray[SquareRow*subsquare + i][SquareCol*subsquare + j] == testCellVal ):
                        return False
        return True
""" -------------------------------- Backtracking ---------------------------------"""

def getUnassignedVar( sudoku ):
    for row in range(sudoku.BoardSize):
        for col in range(sudoku.BoardSize):
            if ( sudoku.CurrentGameboard[row][col] == 0 ): return row, col
    return -1, -1


def backtracking( sudoku ):
    # stop when time is maxed out
    global start_time
    if ( time() - start_time ) > 200:
        print 'Time Limit Exceeded \n'
        return False
        
    # get an unassigned cell
    row, col = getUnassignedVar( sudoku )
    if ( row == col == -1 ): return True
    
    # try different values for a cell
    for value in range( 1, sudoku.BoardSize+1 ):
        sudoku.numChecks += 1
        if isConsistent( sudoku.CurrentGameboard, row, col, value ):
            sudoku.set_value( row, col, value )
            if ( backtracking( sudoku ) ): return True
        sudoku.set_value( row, col, 0 )
    return False


""" -------------------------------- Forward Checking ---------------------------------"""

# prints a matrix for possible values for every cell 
def printPoss(matrix):
    print " ---------  Possibility Matrix --------------- "
    for row in matrix: print row
    print " ---------------------------------------------\n " 


# sets the intial possibility matrix 
def initialPoss( sudoku ):
    poss = [[range(1,sudoku.BoardSize+1) for row in range(sudoku.BoardSize)] for col in range(sudoku.BoardSize)]
    for row in range(sudoku.BoardSize):
        for col in range(sudoku.BoardSize):
            value = sudoku.CurrentGameboard[row][col]
            if (value != 0): # check for cells already assigned
                #poss[row][col] = [] # no possibilities for cells already assigned
                poss = updatePoss ( sudoku, poss, row, col, value, 'removePoss' ) # update cells in same row, column, and grid
    return poss


# adds/removes value from the possibility matrix if it in the same row, column, or grid as the curretn cell
def updatePoss( sudoku, poss, currentRow, currentCol, value, action ):
    size = len(poss)
    # remove value if in the same row or column as the curretn cell
    for i in range(size):
        if action == 'removePoss':
            if ( value in poss[currentRow][i] ): poss[currentRow][i].remove(value)
            if ( value in poss[i][currentCol] ): poss[i][currentCol].remove(value)
        elif action == 'addPoss':
            if ( isConsistent(sudoku.CurrentGameboard, currentRow, i, value) \
                 and (value not in poss[currentRow][i]) ):
                poss[currentRow][i].append(value)
            if ( isConsistent(sudoku.CurrentGameboard, i, currentCol, value) \
                 and (value not in poss[i][currentCol]) ):
                poss[i][currentCol].append(value)
            
    # determine which square the cell is in
    subsquare = int(math.sqrt(size))
    SquareRow = currentRow // subsquare
    SquareCol = currentCol // subsquare

    # remove value if in the same grid as the current cell
    for i in range( subsquare ):
        for j in range( subsquare ):
            row, col = SquareRow*subsquare + i, SquareCol*subsquare + j
            if( value in poss[row][col] and action == 'removePoss' ):
                poss[row][col].remove(value)
            elif ( action == 'addPoss' and (value not in poss[row][col]) and \
                   isConsistent( sudoku.CurrentGameboard, row, col, value ) ): 
                poss[row][col].append(value)
    return poss


def forwardChecking( sudoku, poss ):
    # stop when time is maxed out
    global start_time
    if ( time() - start_time ) > 300:
        print 'Time Limit Exceeded \n'
        return False
        
    # get an unassigned cell
    row, col = getUnassignedVar( sudoku )
    if ( row == col == -1 ): return True

    # try different values for a cell
    possCopy = copy.deepcopy(poss[row][col])
    for value in possCopy:
        sudoku.numChecks += 1
        
        if isConsistent( sudoku.CurrentGameboard, row, col, value ):
            sudoku.set_value( row, col, value )
            updatePoss( sudoku, poss, row, col, value, 'removePoss' )
            if ( forwardChecking( sudoku, poss ) ): return True

        sudoku.set_value( row, col, 0 )
        updatePoss( sudoku, poss, row, col, value, 'addPoss' )
                    
    return False

#----------------MCV--------------------------------------
"""
def mostConstrainedVariable(poss, sudoku):
    size = len(poss)
    smallest = 16
    for x in range(size):
        for y in range(size):
            tempx, tempy = x, y
            if ((len(poss[x][y])) == 1):
                    sudoku.set_value(x,y,(poss[x][y]))
            if ((len(poss[x][y]) < smallest) and (len(poss[x][y]) > 1)):
                smallest = len(poss[x][y])
                tempx = x
                tempy = y

    return tempx, tempy
"""
def mostConstrainedVariable(poss, sudoku):
    size = maxPoss = len(poss)
    rowMCV, colMCV = -1, -1
    for row in range(size):
        for col in range(size):
            if (sudoku.CurrentGameboard[row][col] == 0 and len(poss[row][col]) < maxPoss):
                rowMCV, colMCV = row, col
                maxPoss = len(poss[row][col])
    return rowMCV, colMCV
                              

"""def getUnassignedVar( sudoku ):
    for row in range(sudoku.BoardSize):
        for col in range(sudoku.BoardSize):
            if ( sudoku.CurrentGameboard[row][col] == 0 ): return row, col
    return -1, -1"""

def forwardCheckingMCV( sudoku, poss ):
    # stop when time is maxed out
    global start_time
    if ( time() - start_time ) > 1800:
        print 'Time Limit Exceeded \n'
        return False
        
    # get an unassigned cell
    row, col = mostConstrainedVariable( poss, sudoku )
    if ( row == col == -1 ): return True

    # try different values for a cell
    possCopy = copy.deepcopy(poss[row][col])
    for value in possCopy:
        sudoku.numChecks += 1
        
        if isConsistent( sudoku.CurrentGameboard, row, col, value ):
            sudoku.set_value( row, col, value )
            updatePoss( sudoku, poss, row, col, value, 'removePoss' )
            if ( forwardCheckingMCV( sudoku, poss ) ): return True

        sudoku.set_value( row, col, 0 )
        updatePoss( sudoku, poss, row, col, value, 'addPoss' )
                    
    return False


#--------------MCV and LCVAl------------------------------
"""ORIGINAL CODE BY CAMERON
def leastConstrainingValue(poss, x, y):
    minConst = 0
    leastVal = 0
    count = 0
    leastConstVal = 0
    size = len(poss)
    subsquare = int(math.sqrt(size))
    for i in range(1, size + 1, 1):
        if i in poss[x][y]:
            for j in range(0, size, 1):
                minConst = minConst + (poss[x][j]).count(i)
                minConst = minConst + (poss[j][y]).count(i)
            topleftx = (x - (x % subsquare))
            toplefty = (y - (y % subsquare))
            for k in range(subsquare):
                for m in range(subsquare):
                    minConst = minConst + (poss[topleftx + k][toplefty + m].count(i))
            if count == 0:
                leastVal = minConst
                count+1
                leastConstVal =i
            if count > 0 and (minConst < leastVal):
                leastVal = minConst
                leastConstVal = i

    return leastConstVal
"""

def leastConstrainingValue(poss, x, y):
    minConst = 0
    leastVal = 0
    count = 0
    leastConstVal = 0
    size = len(poss)
    subsquare = int(math.sqrt(size))
    for i in range(1, size + 1, 1):
        for m in range(0, len(poss[x][y])):#tried to edit these to get rid of 'int' object has no attribute '__getitem__' error
            if i == m:
                for j in range(0, size, 1):
                    minConst = minConst + (poss[x][j]).count(i)
                    minConst = minConst + (poss[j][y]).count(i)
                topleftx = (x - (x % subsquare))
                toplefty = (y - (y % subsquare))
                for k in range(subsquare):
                    for m in range(subsquare):
                        minConst = minConst + (poss[topleftx + k][toplefty + m].count(i))
                if count == 0:
                    leastVal = minConst
                    count+1
                    leastConstVal =i
                if count > 0 and (minConst < leastVal):
                    leastVal = minConst
                    leastConstVal = i

    return leastConstVal



def forwardCheckingMCVLCV( sudoku, poss ):
    # stop when time is maxed out
    global start_time
    if ( time() - start_time ) > 300:
        print 'Time Limit Exceeded \n'
        return False
        
    # get an unassigned cell
    row, col = mostConstrainedVariable( poss, sudoku )
    if ( row == col == -1 ): return True

    # try different values for a cell
    possCopy = copy.deepcopy(poss[row][col])
    value = leastConstrainingValue(possCopy, row, col)
    sudoku.numChecks += 1
        
    if isConsistent( sudoku.CurrentGameboard, row, col, value ):
        sudoku.set_value( row, col, value )
        updatePoss( sudoku, poss, row, col, value, 'removePoss' )
        if ( forwardCheckingMCVLCV( sudoku, poss ) ): return True

    sudoku.set_value( row, col, 0 )
    updatePoss( sudoku, poss, row, col, value, 'addPoss' )
                    
    return False



""" -------------------------------- Test Code ---------------------------------"""

size, num = '16', '8'
#test with 16.4 or 16.8
path = 'ExtraExamples/%sx%s/%sx%s.%s.sudoku' % (size,size,size,size,num)

"""------- Backtracking -----------
print '--------Backtracking--------'
testBoard = init_board( path )
#print 'Original Board: \n %s \n' % testBoard

start_time = time()
result = backtracking( testBoard )
elapsed_time = time() - start_time

#print 'Backtracking, returned Board: \n %s \n' % testBoard
print 'Solved: %s' % result
print 'Number of checks: %d' % testBoard.numChecks
print 'Time elapsed: %.2f seconds \n' % elapsed_time
--------------------------------"""


""" ------- Forward Checking -----------"""
print '--------Forward Checking--------'
testBoard = init_board( path )
#print 'Original Board: \n %s \n' % testBoard

start_time = time()
poss = initialPoss( testBoard )
result = forwardChecking( testBoard, poss )
elapsed_time = time() - start_time

#print 'Forward Checking, returned Board: \n %s \n' % testBoard
print 'Solved: %s' % result
print 'Number of checks: %d' % testBoard.numChecks
print 'Time elapsed: %.2f seconds \n' % elapsed_time
"""------------------------------------"""


""" ------- MCV -----------"""
print '---------MCV--------'
testBoard = init_board( path )
#print 'Original Board: \n %s \n' % testBoard

start_time = time()
poss = initialPoss( testBoard )
result = forwardCheckingMCV( testBoard, poss )
elapsed_time = time() - start_time

#print 'MCV, returned Board: \n %s \n' % testBoard
print 'Solved: %s' % result
print 'Number of checks: %d' % testBoard.numChecks
print 'Time elapsed: %.2f seconds \n' % elapsed_time
"""------------------------------------"""

""" ------- MCV and LCV -----------
print '---------MCV and LCV--------'
testBoard = init_board( path )
#print 'Original Board: \n %s \n' % testBoard

start_time = time()
poss = initialPoss( testBoard )
result = forwardCheckingMCVLCV( testBoard, poss )
elapsed_time = time() - start_time

#print 'MCV, returned Board: \n %s \n' % testBoard
print 'Solved: %s' % result
print 'Number of checks: %d' % testBoard.numChecks
print 'Time elapsed: %.2f seconds \n' % elapsed_time
------------------------------------"""


