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


# student code
def backtracking( sudoku ):
    #print sudoku.checks
    sudoku.checks -= 1
    if sudoku.checks<0: return False
    #print sudoku
    row, col = getUnassignedVar( sudoku )
    if (row == -1 and col == -1): return True
    for val in range(1, sudoku.BoardSize+1):
        sudoku.set_value(row,col,val)
        if iscomplete(sudoku.CurrentGameboard) and backtracking( sudoku ):
            return True
        sudoku.set_value(row,col,0)
    return False

def getUnassignedVar( sudoku ):
    for row in range(sudoku.BoardSize):
        for col in range(sudoku.BoardSize):
            if (sudoku.CurrentGameboard[row][col] == 0): return row, col
    return -1, -1


# test code
testBoard = init_board( '4x4-1.txt', 1000 )
print 'Original Board:\n', testBoard
print '\nSolved: %s\n' % backtracking( testBoard )
print 'Returned Board:\n', testBoard


    

