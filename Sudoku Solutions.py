#! /usr/bin/env python
'''
Created on Oct 13, 2009

CS420 Lab 4
Sudoku Puzzle Solver

Usage: <command_options> <input_file.sdk> <output_file.sdk>
    
Note: Input and output files must end in .sdk. 

The input file must exist and be a properly formatted sudoku puzzle file.
A properly formatted file is 9 lines of 9 numbers or dashes separated by blanks,
where a dash indicates a blank location in the puzzle.

Command line options for the solution algorithm:
    -b: Backtracking
    -bh: Backtracking with variable ordering heuristic
    -f: Forward checking
    -fh: Forward checking and variable ordering
    -cp: Constraint propagation

'''
import os
import sys
import copy
import time
from Queue import PriorityQueue
from Queue import Queue

class SudokuSolver():
    
    def __init__(self):
        #Common fields
        self.fileExt="sdk" #The allowable file extension
        self.puzzle=[] #Initialize the puzzle
        self.blanks=[] #Initialize blank spots
        self.initPuzzleArray() #Construct an array of 0 0 0 0 0...
        
        #Heuristics related
        self.blankValues={} #Initialize the dictionary for heuristic
                       
        #Initialize the metrics
        self.pathLengths=[] #Hold all the path lengths for metrics
        self.currentPathLength=0 #Hold the local path length
        self.constraintChecks=0 
        self.runningTime=0
        
        #Select a default algorithm option to initialize
        self.option=1
        self.start()
        
    def start(self):
        #Not enough arguments; print usage and exit
        if len(sys.argv)!=4:
            self.printUsage()
            sys.exit(2)
            
        #Set the command line option from the argument list
        self.option=self.getOption(sys.argv[1])
    
        #Invlalid option
        options=[1, 2, 3, 4, 5]
        if self.option not in options:
            print "Invalid option."
            sys.exit(2)
            
        #Get arguments for input-output
        inputFile=sys.argv[2]
        self.outputFile=sys.argv[3]
           
        #Make sure filenames are ok 
        self.checkFiles(inputFile, self.outputFile)
        #Load the puzzle file into array
        self.loadPuzzle(inputFile)
        #Construct the list of blanks
        self.blanks=self.getEmptyCells(self.puzzle)
        #Solve using the specified command line option
        
        print "Solving file: "+inputFile
        print str(len(self.blanks))+" blanks."
        print ""
        self.solve(self.puzzle, self.option)
        
#######################################################
# WRAPPER METHODS                                     #
#######################################################

    '''
    Solve the Sudoku puzzle using the selected algorithm.
    '''
    def solve(self, puzzleArray, method):
        #Branch depending on method
        if method==1:
            print "Solving with backtracking."
            self.runningTime=time.clock()
            self.backTrack(0)

        elif method==2:
            print "Solving with backtracking and heuristic."
            self.runningTime=time.clock()
            self.backTrackHeuristic()
            
        elif method==3:
            print "Solving with forward checking."
            self.processVariablesF()
            self.forwardCheck(0 )

        elif method==4:
            print "Solving with forward checking and heuristic."
            self.processVariablesFH()
            self.forwardCheckHeuristic()

        elif method==5:
            print "Solving with constraint propagation."
            self.processVariablesFH()
            self.constraintProp()
    
#######################################################
# THE DIFFERENT SOLUTIONS                             #
#######################################################
    '''
    Solve Sudoku using plain backtracking
    Uses a recursive algorithm to try each value 1-9 in each blank square, 
    backtracking when it was not able to put in any value into the square.
    '''
    def backTrack(self, index):
        #Found a solution if we have gone past the last blank
        if index>len(self.blanks)-1:
            self.endAlgorithm()
        
        #Haven't found a solution yet; get coords of the blank
        row=self.blanks[index][0]
        col=self.blanks[index][1]
        
        #Try numbers 1-9.
        for num in range(1, 10):
            if self.puzzleValid(row, col, num, False):   
                #If the number is valid, increment current path by 1.
                self.currentPathLength+=1 
                self.puzzle[row][col] = num
                self.backTrack(index+1)
        
        #No number found...set back to 0 and return to the previous blank
        self.pathLengths.append(self.currentPathLength) #Add the current path length to the overall list.
        self.currentPathLength-=1 #-1 from path.
        index-=1
        self.puzzle[row][col]=0

    '''
    Solve Sudoku using backtracking with MRV+MD.
    '''
    def backTrackHeuristic(self):
        #No more blanks; solution found
        if len(self.blanks)==0:
            self.endAlgorithm()    
            
        nextBlank=self.getMRV()#Get the most constrained blank
        
        row=nextBlank[0]
        col=nextBlank[1]

        #Try 1-9 for each blank
        for num in range(1, 10):
            if self.puzzleValid(row, col, num, False):
                self.blanks.remove(nextBlank)
                self.currentPathLength+=1
                self.puzzle[row][col] = num
                result=self.backTrackHeuristic()
                if result!=None:    
                   return
            
                #Backtrack
                self.currentPathLength-=1
                self.pathLengths.append(self.currentPathLength)
                self.blanks.append(nextBlank)
                self.puzzle[row][col]=0 
                
        return None
    
    '''
    Solve Sudoku using forward checking
    '''
    def forwardCheck(self, index):
        #Found a solution if we have gone past the last blank
        if index>len(self.blanks)-1:
            self.endAlgorithm()
        
        #Haven't found a solution yet; get coords of the blank
        blank=self.blanks[index]
        row=blank[0]
        col=blank[1]
        
        #Try numbers in the domain.
        blankDomain=copy.deepcopy(self.blankValues[blank])
        
        for num in blankDomain:            
            tempDomain=copy.deepcopy(self.blankValues) #Copy of current domain before pruning
            consistent=self.pruneInvalid(blank, num)
            if (consistent==True): #Assign a value and recurse if domain processing returned true
                self.puzzle[row][col] = num
                self.currentPathLength+=1
                
                result=self.forwardCheck(index+1)
                if result!=None:
                    return
            
            self.blankValues=tempDomain #Fell through; restore the domain
                
        self.puzzle[row][col]=0
        self.pathLengths.append(self.currentPathLength) #Add the current path length to the overall list.
        self.currentPathLength-=1 #-1 from path.
        index-=1
        return None
    
    '''
    Solve Sudoku using forward checking+MRV+MD
    '''
    def forwardCheckHeuristic(self):
        #No more blanks; found a solution
        if len(self.blanks)==0:
            self.endAlgorithm()
        
        #Haven't found a solution yet; get coords of the blank
        blank=self.getMRV()
        row=blank[0]
        col=blank[1]

        #Try numbers in the domain of the current blank
        blankDomain=copy.deepcopy(self.blankValues[blank])

        for num in blankDomain:
            tempDomain=copy.deepcopy(self.blankValues) #Copy of current domain before pruning
            consistent=self.pruneInvalid(blank, num)
            if (consistent==True): #Assign a value and recurse if domain processing returned true
                self.blanks.remove(blank)
                self.puzzle[row][col] = num
                self.currentPathLength+=1
                
                result=self.forwardCheckHeuristic()
                if result!=None:
                    return  
                
                self.blankValues=tempDomain #Restore the original domain
                
                #Backtrack
                self.blanks.append(blank)
                self.puzzle[row][col]=0
                self.pathLengths.append(self.currentPathLength) #Add the current path length to the overall list.
                self.currentPathLength-=1
        return None
    
    '''
    Solve Sudoku using AC-3 constraint propagation
    '''
    def constraintProp(self):
        #No blanks left; solution found
        if len(self.blanks)==0:
            self.endAlgorithm()
        
        #Haven't found a solution yet; get coords of the blank
        blank=self.getMRV()
        row=blank[0]
        col=blank[1]

        #Try numbers in the domain.
        blankDomain=copy.deepcopy(self.blankValues[blank])

        for num in blankDomain:
            tempDomain=copy.deepcopy(self.blankValues) #Copy of current domain before pruning
            self.blankValues[blank]=[num]
            #Propagate the constraints
            self.propagateConstraints()
            #Assign value
            self.puzzle[row][col]=num
            
            self.currentPathLength+=1
            self.blanks.remove(blank)   
            
            result=self.constraintProp()
            if result!=None:
                return
            #Restore the domain and backtrack
            self.blankValues=tempDomain
            self.blanks.append(blank)
            self.puzzle[row][col]=0
            self.pathLengths.append(self.currentPathLength) #Add the current path length to the overall list.
            self.currentPathLength-=1
        return None

#######################################################
# CSP VALIDATORS                                      #
#######################################################
    '''
    Check if the current puzzle is legal after placing num in (row, col)
    The "heur" option is to bypass the constraint check increment 
    when using this method for a heuristic, in which case the 
    heuristic usage shouldn't count toward the constraint checks.
    '''
    def puzzleValid(self, row, col ,num, heur):
        if heur==False:
            self.constraintChecks+=1 #Increment number of constraint checks
        valid=False
        if num==0:
            return True
        else:
            #Return true if row, column, and box have no violations
            rowValid=self.checkRow(row, num)
            colValid=self.checkColumn(col, num)
            boxValid=self.checkBox(row, col, num)                                   
            valid=(rowValid&colValid&boxValid)
    
        return valid

    '''
    Check if num is a legal value for the given row. 
    '''
    def checkRow(self, row, num ):
        for col in range(9):
            currentValue=self.puzzle[row][col]
            if num==currentValue:
                return False        
        return True
    
    '''
    Check if num is a legal value for the given column. 
    '''
    def checkColumn(self, col, num ):
        for row in range(9):
            currentValue=self.puzzle[row][col]
            if num==currentValue:
                return False
        return True

    '''
    Check if num is a legal value for the box (one of 9 boxes) containing given row/col
    '''
    def checkBox(self, row, col, num):       
        row=(row/3)*3
        col=(col/3)*3
        
        for r in range(3):
            for c in range(3):
                if self.puzzle[row+r][col+c]==num:
                    return False
        return True
    
#######################################################
# ALGORITHM HELPERS                                   #
#######################################################

    '''
    Get the most constrained blank (least number of possible values) with max degree
    MRV+MD
    '''
    def getMRV(self):
        
        #Build the MRV priority queue
        q = PriorityQueue()
        for blank in self.blanks:
            possible = self.getPossibleValues(blank, True)
            q.put((len(possible), blank))

        #Get the first one among (possibly equal)
        blanks = []
        blanks.append(q.get())
        minVal = blanks[0][0]

        #Build max Degree list
        while not q.empty(): #Get all equally-prioritized blanks
            next = q.get()
            if next[0] == minVal:
                blanks.append(next)
            else:
                break
            
        maxDeg = len(self.getNeighborBlanks(blanks[0][1]))
        maxDegBlank = blanks[0]

        for blank in blanks:
            degree = len(self.getNeighborBlanks(blank[1]))
            if degree > maxDeg:
                maxDegBlank = blank
                maxDeg = degree
        return maxDegBlank[1]
    '''
    Preprocessing for forward checking
    '''
    def processVariablesF(self):        
        #Construct the dictionary
        for blank in self.blanks:
            possibleValues=self.getPossibleValues(blank, False)
            self.blankValues[blank]=possibleValues
    
    '''
    Preprocessing for forward checking
    '''
    def processVariablesFH(self):
        #Construct the dictionary
        for blank in self.blanks:
            possibleValues=self.getPossibleValues(blank, False)
            self.blankValues[blank]=possibleValues

    '''
    deletes val from the domain 
    for all constraint-neighbors of (row, col).
    
    @return True if putting this value in is possible, false otherwise.
    '''
    def pruneInvalid(self, blank, num):
        #Get all the neighbors
        neighbors=self.getNeighborBlanks(blank)
        for neighborBlank in neighbors:
            neighborDomain=self.blankValues[neighborBlank]
            if num in neighborDomain:
                self.blankValues[neighborBlank].remove(num)
                if len(self.blankValues[neighborBlank])==0: #Detect empty domain
                    return False
        return True
    '''
    Propagates current constraints on the entire
    grid via AC3
    '''
    def propagateConstraints(self):
        queue=Queue() #Build a queue of all arcs in the grid
        for blank in self.blanks:
            neighbors=self.getNeighborBlanks(blank)
            for neighbor in neighbors:
                queue.put((blank, neighbor))

        while not queue.empty():
            arc=queue.get()
            orig=arc[0]
            dest=arc[1]
            if self.removeInconsistencies(orig, dest): #Removal occurred from orig
                neighbors=self.getNeighborBlanks(orig) #Go through neighbors, add an arc from neighbor->orig to detect possible inconsistencies
                neighbors.remove(dest)
                for neighbor in neighbors:
                    queue.put((neighbor, orig))

    '''
    AC3
    Deletes values in orig that are not compatible with dest 
    '''
    def removeInconsistencies(self, orig, dest):
        removed=False
        originDomain=copy.deepcopy(self.blankValues[orig])
        for val in originDomain:
            neighborDomain=copy.deepcopy(self.blankValues[dest])
            if val in neighborDomain: 
                neighborDomain.remove(val)                
            if len(neighborDomain)==0: #Any value of original domain caused neighbor domain to become 0
                self.blankValues[orig].remove(val)
                removed=True
        return removed
    '''
    Generic method to end the algorithm in process,
    calculate the running time, output the solution file, 
    print the metrics and exit.
    '''
    def endAlgorithm(self):
            self.pathLengths.append(self.currentPathLength) #Append the final path's length
            self.runningTime=time.clock()-self.runningTime
            print "Solution found."
            #print ""
            self.outputSolutionFile()       
            self.printMetrics()
            sys.exit(0)
            
    '''
    Get all legal values for a cell. 
    '''
    def getPossibleValues(self, cell, heur):
        row=cell[0]
        col=cell[1]
        allowed=[]
        for i in range(1,10):
            if self.puzzleValid(row, col, i, heur):
                allowed.append(i)
    
        return allowed
    
    '''
    Get all the empty cells in the puzzle.
    '''
    def getEmptyCells(self, puzzle):
        emptyCells=[]
        for i in range(9):
            for j in range(9):
                if self.puzzle[i][j]==0:
                    emptyCells.append((i, j))
        return emptyCells
    
    '''
    Get the blank neighbors (squares that are affected by a constraint from a given blank)
    of the square (row, col).
    '''
    def getNeighborBlanks(self, blank):
        row=blank[0]
        col=blank[1]
        
        neighbors=[]
        associatedBlanks=self.getRowBlanks(row)+self.getColumnBlanks(col)+self.getBoxBlanks(row, col)
        for blank in associatedBlanks:
            if blank not in neighbors and blank!=(row,col): 
                #Might be that box collided with row / col so check here
                neighbors.append(blank)
        return neighbors
        
    '''
    Get neighboring cells in row
    '''
    def getRowBlanks(self, row):
        cells=[]
        for col in range(9):
            if self.puzzle[row][col]==0:
                cells.append((row, col))
        return cells
    
    '''
    Get neighboring cells in column
    '''
    def getColumnBlanks(self, col ):
        cells=[]
        for row in range(9):
            if self.puzzle[row][col]==0:    
                cells.append((row,col))
        
        return cells
    
    '''
    Get neighboring cells in box
    '''
    def getBoxBlanks(self, row, col):       
        cells=[]
        row=(row/3)*3
        col=(col/3)*3
        
        for r in range(3):
            for c in range(3):
                if self.puzzle[row+r][col+c]==0:
                    cells.append((row+r,col+c))
                    
        return cells

#######################################################
# I/O HELPERS                                         #
#######################################################
    '''
    Checks if the input file and output file have correct naming and input file exists
    '''
    def checkFiles(self, input, output):
        inputGood=False
        outputGood=False
        #Check if input file exists and is a file not a directory
        if os.path.exists(input):
            if os.path.isfile(input):
                tokens=input.split(".")
                #Check the file extension
                if tokens[len(tokens)-1]==self.fileExt :
                    inputGood=True
                else:
                    print "File extension for input must be '.sdk'"
                    sys.exit(2)
            else:
                print "Input is not a file."
                sys.exit(2)
        else:
            print "Input file does not exist."
            sys.exit(2)
        
        tokens=output.split(".")
        if tokens[len(tokens)-1]==self.fileExt :
            outputGood=True
        else:
            print "File extension for output must be '.sdk'"
            sys.exit(2)
                    
        #Both input/output must be legit for it to work
        if not (inputGood and outputGood):
            sys.exit(2)
        
    '''
    Convert an option string to an integer switch used internally
    to decide what algorithm to use for solving
    '''
    def getOption(self, o):
        if o == "-b":
            return 1
        elif o == "-bh":
            return 2
        elif o == "-f":
            return 3
        elif o == "-fh":
            return 4
        elif o == "-cp":
            return 5
        else:
            return None
    
    '''
    Prints help information to stdout.
    ''' 
    def printUsage(self):
        print "    "
        print "CS420 Sudoku Solver" 
        print "Written by Miguel Haruki Yamaguchi"
        print "    "
        print "Usage: <command_options> <input_file.sdk> <output_file.sdk>"
        print "    "
        print "Note: Input and output files must end in .sdk. "
        print ""
        print "The input file must exist and be a properly formatted sudoku puzzle file."
        print "A properly formatted file is 9 lines of 9 numbers or dashes separated by blanks,"
        print "where a dash indicates a blank location in the puzzle."
        print ""
        print "Command line options for the solution algorithm:"
        print "    -b: Backtracking"
        print "    -bh: Backtracking with variable ordering heuristic"
        print "    -f: Forward checking"
        print "    -fh: Forward checking and variable ordering"
        print "    -cp: Constraint propagation"
        print "    "

    '''
    Constructs the blank puzzle array to have 0 0 0 0 0...for all rows and columns
    '''
    def initPuzzleArray(self):
        del self.puzzle[:]
        for i in range(9):
            self.puzzle.append([])
            for j in range(9):
                self.puzzle[i].append([])
                self.puzzle[i][j]=0
                
    '''
    Loads a puzzle file into the program and makes sure that
    it is valid.
    '''
    def loadPuzzle(self, puzzleFile):
        possibleTokens=[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        puzzle=open(puzzleFile, 'r')
        puzzleText=puzzle.readlines()
        for row in range (9):
            lineTokens=puzzleText[row].split()
            if len(lineTokens)!=9:
                print "Improper file format! Line length must always be 9"
                sys.exit(1)
            for col in range(9):
                token=lineTokens[col].split()[0].strip()
                if token=='-':  
                    token=0 # Change the '-'s to 0s
                token=int(token)
                if token not in possibleTokens:
                    print "Invalid token found"
                    print "Token: "+str(token)+" possible: ", possibleTokens
                    sys.exit(1)
                    
                self.puzzle[row][col]=int(token)
        print ""
                
    '''
    Prints the puzzle as a visual representation.
    '''
    def printPuzzle(self):
        print "____________________" 
        rowStrings=[]
        for i in range(9):
            rowString=[]
            for j in range(9):
                rowString.append(str(self.puzzle[i][j])+" ")
            #print rowString
            rowStrings.append(self.formatRow(rowString))
        for i in range(0, len(rowStrings), 3):
            for j in range(0, 3):
                print rowStrings[i+j]
            print "--------------------" 
    
    '''
    Print the statistics accumulated during the run to stdout.
    '''
    def printMetrics(self):
        print "+++++++++Metrics+++++++++"
        print ""
        print "Constraint checks: "+str(self.constraintChecks)
        print "Running time: "+str(self.runningTime)
        print "Number of paths: "+str(len(self.pathLengths))
        print "Deepest path: "+str(max(self.pathLengths))
        print "Average path length: "+str(float(sum(self.pathLengths))/len(self.pathLengths))
        print ""
        print "Solved puzzle: "
        self.printPuzzle()
        print "+++++++++++++++++++++++++"
        print ""
        
        
    '''
    Return a string with '|'s inserted every 3 digits; format one row for printing the puzzle neatly
    '''
    def formatRow(self, rowString):
        formattedString=""
        for i in range(0, len(rowString), 3):
            for j in range(0, 3):
                formattedString+=rowString[i+j]
            formattedString+="|"
            
        return formattedString
    
    '''
    Write the solution file to disk, the output file being the 
    one specified by the user at execution
    '''
    def outputSolutionFile(self):
        outFile=open(self.outputFile, 'w')
        for i in range(9):
            rowString=""
            for j in range(9):
                rowString+=str(self.puzzle[i][j])+" "
            outFile.write(rowString+'\n')
            
SudokuSolver()
