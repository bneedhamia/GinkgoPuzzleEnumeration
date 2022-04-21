# Enumerate the valid Ginkgo Puzzle board states.
# The 3D printed board and pieces are on Cults3D,
# at https://cults3d.com/en/3d-model/game/ginkgo-combination-puzzle

# See LICENSE for the program's license.

# Written to answer the question: How many valid board states are there
# in the Ginkgo Puzzle? ...and is it feasible to build a matrix of moves from
# any arbitrary board position to any other?
#
# A valid board layout is one in which all the pieces are placed,
# no part of one piece overlaps another,
# and there are no 4-piece, mutually-dependent loops.
# See function isPieceDirectionLegal(), below.
# For an example of a loop, see ImpossibleLayout.jpg.
#
# The current answer: 3,625,093,120 total complete, non-overlapping,
# non-looping board layouts,
# calculated in about 18 hours on a 2017 Dell laptop
# with 16GB of ram and a 2.8GHz Intel Core i7.
# 
# Clearly it's not feasible to record all those positions,
# let alone calculate and record all the valid moves between them.

# The 25 spaces on the board fit into a diagonal, two-dimensional grid.
# Our board is centered on the center piece,
# and axes go diagonally relative to the board.
# +Y is to the Northeast of center; +X is to the SouthEast of center.
# The range of X is -3 through 3; the range of Y is -3 through 3.
# Because the axes are on a diagonal not all coordinates within
# the X and Y range are valid:
# valid coordinates are where the City Block Distance from 0, 0 is under 4.
# That is, abs(x) + abs(y) <= 3.

import sys
import cProfile

# The number of valid board layouts found so far.
validBoards = 0

# Representation of directions
NOWHERE = -1    # pointing in no direction (no piece at these coordinates).
NORTH = 0
EAST = 1
WEST = 2
SOUTH = 3

# The directions to attempt placing each piece in.
directions = [NORTH, EAST, WEST, SOUTH]

# The worksheet for enumerating board positions.
# Indexed by indexOfCoord(x, y),
# holds the current direction of the piece at those coordinates.
# NOWHERE means there is no piece at those coordinates.
# Coordinates representing a place outside the board
# are set to NOWHERE.
pieceDirection = [
    NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE
    ,NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE
    ,NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE
    ,NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE
    ,NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE
    ,NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE
    ,NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE, NOWHERE
    ]

# Given the coordinates of a board position,
# return the pieceDirection[] index
# of the direction of the piece at those coordinates.
def indexOfCoord(x, y):
    # Changes the values to strictly positive numbers.
    return (x + 3) * 7 + (y + 3);

# Returns True if the given coordinate is on the board,
# False otherwise.
# "On the board" = "has a city block distance of under 4 from the center"
def isOnBoard(x, y):
    # Optimization notes:
    # cProfile suggested this function consumed a lot of time.
    # The absolute seconds is irrelevant.
    # The relative speeds are all that matter.
    
##    # 83 seconds for <= 16 spiral steps
##    return (abs(x) + abs(y)) < 4

##    # 38 seconds for <= 16 spiral steps
##    distance = x
##    if x < 0:
##        distance = -x
##    distance += y
##    if y < 0:
##        distance -= 2 * y
##    return distance <= 3

##    # 32 seconds for <= 16 spiral steps.
##    if x < 0:
##        distance = -x
##    else:
##        distance = x
##
##    if y < 0:
##        distance -= y
##    else:
##        distance += y
##
##    return distance < (3 + 1)
    
    # 30 seconds for <= 16 spiral steps.
    if x < 0:
        if y < 0:
            return -x - y <= 3
        return y - x <= 3
    # x >= 0
    if y < 0:
        return x - y <= 3
    return x + y <= 3

# (debug) Print the current configuration of the board
def printBoard():
    global pieceDirection
    
    for x in range(-3, 3 + 1):
        for y in range(-3, 3 + 1):
            # print only coordinates that are inside the board
            if isOnBoard(x, y):
                print("[", x, ",", y, "] = ", pieceDirection[indexOfCoord(x, y)])

# Iteration over spiral[] walks the the board coordinates
# in an order of laying down the pieces.
# spiral[n][0] = x; [1] = y.
#
# I now believe the order of pieces in the spiral is relatively unimportant.
spiral = [
    # abs(x) + abs(y) = 0
    [0, 0]
    # abs(x) + abs(y) = 1
    ,[1, 0]
    ,[0, 1]
    ,[-1, 0]
    ,[0, -1]
    # abs(x) + abs(y) = 2
    ,[1, -1]
    ,[2, 0]
    ,[1, 1]
    ,[0, 2]
    ,[-1, 1]
    ,[-2, 0]
    ,[-1, -1]
    ,[0, -2]
    # abs(x) + abs(y) = 3
    ,[1, -2]
    ,[2, -1]
    ,[3, 0]
    ,[2, 1]
    ,[1, 2]
    ,[0, 3]
    ,[-1, 2]
    ,[-2, 1]
    ,[-3, 0]
    ,[-2, -1]
    ,[-1, -2]
    ,[0, -3]
]

# (debug) Print the pieceDirection[] index
# corresponding to each coordinate.
# A test of indexOfCoord().
def debugPrintIndexOfEachCoord():
    for x in range(-3, 3 + 1):
        for y in range(-3, 3 + 1):
            print("index of [", x, ",", y, "] = ", indexOfCoord(x, y))

# (debug) Print the coordinates of the spiral, in order of placement.
def debugPrintSpiral():
    global spiral
    
    for xy in spiral:
        print("x = ", xy[0], " y = ", xy[1])

# Record the fact that we've found a valid board position.
# That is, a board configuration where all coordinates are occupied by pieces
# and no parts of pieces overlap or form loops.
def recordValidBoard():
    global validBoards
    
    validBoards += 1

    # Print occasionally, to let us know the program is making progress.
    if validBoards % 100000 == 0:
        print(validBoards // 1000, "K");

# Return True if the given piece can legally be pointing in this direction,
# False otherwise.
# There are two illegal conditions:
# 1) This piece overlaps a neighbor, or
# 2) This piece forms a loop of mutual dependency (a locked loop).
#
# The piece at [myX, myY] must have been placed (is not NOWHERE)
# and is on the board.
def isPieceDirectionLegal(myX, myY):
    global pieceDirection
    global NOWHERE
    global NORTH
    global SOUTH
    global EAST
    global WEST

    # important because directions of pieces that are off the board
    # don't get set below, but are needed for loop detection.
    nwDirection = NOWHERE # direction of the piece to my Northwest
    swDirection = NOWHERE # ...Southwest
    seDirection = NOWHERE # ...Southeast
    neDirection = NOWHERE # ...Northeast
    
    myDirection = pieceDirection[indexOfCoord(myX, myY)];

    # Check overlap with the piece to the Northwest
    otherX = myX - 1
    otherY = myY
    if isOnBoard(otherX, otherY): # piece is on the board
        nwDirection = pieceDirection[indexOfCoord(otherX, otherY)]
        otherDirection = nwDirection
        # overlaps if we have an 'outie' to the NW and other has an 'outie' to the SE.
        if (myDirection == SOUTH or myDirection == EAST) and \
           (otherDirection == NORTH or otherDirection == WEST):
            return False

    # ...the piece to the SouthWest
    otherX = myX
    otherY = myY -1
    if isOnBoard(otherX, otherY): # piece is on the board
        swDirection = pieceDirection[indexOfCoord(otherX, otherY)]
        otherDirection = swDirection
        # overlaps if we have an 'outie' to the SW and other has an 'outie' to the NE.
        if (myDirection == NORTH or myDirection == EAST) and \
           (otherDirection == SOUTH or otherDirection == WEST):
            return False

    # ...the piece to the SouthEast
    otherX = myX + 1
    otherY = myY
    if isOnBoard(otherX, otherY): # piece is on the board
        seDirection = pieceDirection[indexOfCoord(otherX, otherY)]
        otherDirection = seDirection
        # overlaps if we have an 'outie' to the SE and other has an 'outie' to the NW.
        if (myDirection == NORTH or myDirection == WEST) and \
           (otherDirection == SOUTH or otherDirection == EAST):
            return False

    # ...the piece to the NorthEast
    otherX = myX
    otherY = myY + 1
    if isOnBoard(otherX, otherY): # piece is on the board
        neDirection = pieceDirection[indexOfCoord(otherX, otherY)]
        otherDirection = neDirection
        # overlaps if we have an 'outie' to the NE and other has an 'outie' to the SW.
        if (myDirection == SOUTH or myDirection == WEST) and \
           (otherDirection == NORTH or otherDirection == EAST):
            return False

    # Nothing overlaps with the passed piece.
    
    # Check for loops
    
    if myDirection == NORTH:
        
        # See if we are in a counterclockwise loop.
        farX = myX - 1
        farY = myY - 1
        if isOnBoard(farX, farY): # the far coordinate is in the board
            farDirection = pieceDirection[indexOfCoord(farX, farY)]
            if nwDirection == WEST and farDirection == SOUTH \
               and swDirection == EAST:
                return False

        # See if we are in a clockwise loop.
        farX = myX + 1
        farY = myY + 1
        if isOnBoard(farX, farY): # the far coordinate is in the board
            farDirection = pieceDirection[indexOfCoord(farX, farY)]
            if neDirection == EAST and farDirection == SOUTH \
               and seDirection == WEST:
                return False

    elif myDirection == EAST:
        
        # See if we are in a counterclockwise loop.
        farX = myX - 1
        farY = myY + 1
        if isOnBoard(farX, farY): # the far coordinate is in the board
            farDirection = pieceDirection[indexOfCoord(farX, farY)]
            if neDirection == NORTH and farDirection == WEST \
               and nwDirection == SOUTH:
                return False

        # See if we are in a clockwise loop.
        farX = myX + 1
        farY = myY - 1
        if isOnBoard(farX, farY): # the far coordinate is in the board
            farDirection = pieceDirection[indexOfCoord(farX, farY)]
            if seDirection == SOUTH and farDirection == WEST \
               and swDirection == NORTH:
                return False
 
    elif myDirection == SOUTH:
        
        # See if we are in a counterclockwise loop.
        farX = myX + 1
        farY = myY + 1
        if isOnBoard(farX, farY): # the far coordinate is in the board
            farDirection = pieceDirection[indexOfCoord(farX, farY)]
            if seDirection == EAST and farDirection == NORTH \
               and neDirection == WEST:
                return False

        # See if we are in a clockwise loop.
        farX = myX - 1
        farY = myY - 1
        if isOnBoard(farX, farY): # the far coordinate is in the board
            farDirection = pieceDirection[indexOfCoord(farX, farY)]
            if swDirection == WEST and farDirection == NORTH \
               and nwDirection == EAST:
                return False

    elif myDirection == WEST:
        
        # See if we are in a counterclockwise loop.
        farX = myX + 1
        farY = myY - 1
        if isOnBoard(farX, farY): # the far coordinate is in the board
            farDirection = pieceDirection[indexOfCoord(farX, farY)]
            if swDirection == SOUTH and farDirection == EAST \
               and seDirection == NORTH:
                return False

        # See if we are in a clockwise loop.
        farX = myX - 1
        farY = myY + 1
        if isOnBoard(farX, farY): # the far coordinate is in the board
            farDirection = pieceDirection[indexOfCoord(farX, farY)]
            if nwDirection == NORTH and farDirection == EAST \
               and neDirection == SOUTH:
                return False

        
    # This piece is not part of a loop either.
    return True

# Place the piece from the given index in the spiral.
# Attempt to place the piece in all four directions,
# recursing for each direction to walk the entire spiral.
def placePiece(spiralIndex):
    global spiral
    global pieceDirection
    global directions
    global NOWHERE

    # DEBUG to profile a version that eventually finishes.
    # I added this code because I believed the code would take
    # over a century to run. It turns out it takes less than a day.
    # >=16 takes 173 seconds and produces 11,460,096 boards.
    # >= 18 takes 678 seconds (~11 minutes) and produces 31,532,544 boards.
    # >= 19 takes 1256 seconds (20 minutes) and produces 82,990,848 boards.
    # A full run took 65285 seconds (18 hours) and produced 3,625,093,120 boards.
##    if spiralIndex >= 16:
##        recordValidBoard()
##        return

    # If we've reached the end of the spiral
    # We should have filled the board, and have a valid board.
    if spiralIndex > len(spiral) - 1:
        recordValidBoard()
        return

    coord = spiral[spiralIndex];
    pieceIndex = indexOfCoord(coord[0], coord[1])

    # Try placing this piece in each of the four directions
    for d in directions:
        pieceDirection[pieceIndex] = d
        # If this piece's direction is legal,
        # leave this piece here and place all the following pieces.
        if isPieceDirectionLegal(coord[0], coord[1]):
            placePiece(spiralIndex + 1)

    # Remove this piece from the board. We're done with it for now.
    pieceDirection[pieceIndex] = NOWHERE

# Enumerate all valid boards
def walkBoards():
    global validBoards
    global pieceDirection
    global NORTH

    print("Starting")

    # Because the whole puzzle takes days to enumerate
    # and because there is 4-fold rotational symmetry in the board layouts,
    # Manually place the first piece, then enumerate from there.
    # When done, multiply the result by 4 to take into account
    # the rotationally symmetric board layouts we didn't enumerate.

    pieceDirection[0] = NORTH
    placePiece(1) # Causes all valid boards to be enumerated
    print("validBoards (* 4) =", validBoards * 4)

# Report the output of isOnBoard() for every possible coordinate.
def testIsOnBoard():
    print("Test isOnBoard()")
    for x in range(-3, 3 + 1):
        for y in range(-3, 3 + 1):
            if isOnBoard(x, y):
                print("[", x, ", ", y, "] on board")

# Test a few of the conditions for isPieceDirectionLegal()
# This is nowhere near a complete Unit Test.
def testIsPieceDirectionLegal():
    global NORTH
    global SOUTH
    global EAST
    global WEST
    global NOWHERE
    global pieceDirection
    
    # Set up a clockwise loop,
    # Then test that each of its pieces show a loop.
    
    pieceDirection[indexOfCoord(0, 0)] = NORTH
    pieceDirection[indexOfCoord(0, 1)] = EAST
    pieceDirection[indexOfCoord(1, 1)] = SOUTH
    pieceDirection[indexOfCoord(1, 0)] = WEST
    if not isPieceDirectionLegal(0, 0):
        print("NORTH Clockwise loop: pass")
    else:
        print("-----FAIL: NORTH Clockwise loop")
    if not isPieceDirectionLegal(0, 1):
        print("EAST Clockwise loop: pass")
    else:
        print("-----FAIL: EAST Clockwise loop")
    if not isPieceDirectionLegal(1, 1):
        print("SOUTH Clockwise loop: pass")
    else:
        print("-----FAIL: SOUTH Clockwise loop")
    if not isPieceDirectionLegal(1, 0):
        print("WEST Clockwise loop: pass")
    else:
        print("-----FAIL: WEST Clockwise loop")
    # Restore the empty board
    pieceDirection[indexOfCoord(0, 0)] = NOWHERE
    pieceDirection[indexOfCoord(0, 1)] = NOWHERE
    pieceDirection[indexOfCoord(1, 1)] = NOWHERE
    pieceDirection[indexOfCoord(1, 0)] = NOWHERE

    # Set up a counterclockwise loop
    
    pieceDirection[indexOfCoord(0, 0)] = NORTH
    pieceDirection[indexOfCoord(-1, 0)] = WEST
    pieceDirection[indexOfCoord(-1, -1)] = SOUTH
    pieceDirection[indexOfCoord(0, -1)] = EAST
    if not isPieceDirectionLegal(0, 0):
        print("NORTH CCW loop: pass")
    else:
        print("-----FAIL: NORTH CCW loop")
    if not isPieceDirectionLegal(-1, 0):
        print("WEST CCW loop: pass")
    else:
        print("-----FAIL: WEST CCW loop")
    if not isPieceDirectionLegal(-1, -1):
        print("SOUTH CCW loop: pass")
    else:
        print("-----FAIL: SOUTH CCW loop")
    if not isPieceDirectionLegal(0, -1):
        print("EAST CCW loop: pass")
    else:
        print("-----FAIL: EAST CCW loop")


# Profile the main function so we get a print of how long it took to run
# and so that we get some hints of where the time went.

# testIsPieceDirectionLegal()
# testIsOnBoard()
# walkBoards()
cProfile.run('walkBoards()')

