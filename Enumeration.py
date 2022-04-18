# Enumerate the valid Ginkgo Puzzle board states.
# The 3D printed board and pieces are on Cults3D,
# at https://cults3d.com/en/3d-model/game/ginkgo-combination-puzzle

# See LICENSE for the program's license.

# Written to answer the question: How many valid board states are there
# in the Ginkgo Puzzle? And is it feasible to build a matrix of moves from
# any arbitrary board position to any other?
#
# A valid board layout is one in which all the pieces are placed
# and no part of one piece overlaps another.
#
# The current answer: 5,435,817,984 total valid board positions,
# calculated in about 23 hours on a 2017 Dell laptop
# with 16GB of ram and a 2.8GHz Intel Core i7.
# Clearly it's not feasible to record all those positions,
# let alone calculate and record all the valid moves between them.

# The 25 spaces on the board fit into a diagonal, two-dimensional grid.
# Our board is centered on the center piece,
# and axes go diagonally relative to the board.
# +Y is to the Northeast of center; +X is to the SouthEast of center.
# The range of X is -3 through 3; the range of Y is -3 through 3.
# Because the axes are on a diagonal not all coordinates within
# the X and Y range are valid:
# valid coordinates are where abs(x) + abs(y) <= 3.

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
# holds the direction of the piece at those coordinates.
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
    # Change the values to strictly positive numbers first.
    i = (x + 3) * 7 + (y + 3);
    return i

# (debug) Print the current configuration of the board
def printBoard():
    global pieceDirection
    
    for x in range(-3, 3 + 1):
        for y in range(-3, 3 + 1):
            # print only coordinates that are inside the board
            if abs(x) + abs(y) <= 3:
                print("[", x, ",", y, "] = ", pieceDirection[indexOfCoord(x, y)])

# Iteration over spiral[] walks the the board coordinates
# in an order of laying down the pieces.
# spiral[n][0] = x; [1] = y.
#
# I now believe the order of pieces in the spiral ia unimportant.
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
# and no parts of pieces overlap.
def recordValidBoard():
    global validBoards
    
    validBoards += 1

    # Print occasionally, to let us know the program is making progress.
    if validBoards % 100000 == 0:
        print(validBoards // 1000, "K");

# Return True if the given piece overlaps with any of its neighbors,
# False if it doesn't overlap.
# This code is basically a pile of special cases.
#
# The piece at [myX, myY] must have been placed (is not NOWHERE).
def pieceOverlaps(myX, myY):
    global pieceDirection
    global NOWHERE
    global NORTH
    global SOUTH
    global EAST
    global WEST
    
    myDirection = pieceDirection[indexOfCoord(myX, myY)];
    if myDirection == NOWHERE:
        print("Error: piece at [", myX, ",", myY, "] points NOWHERE")
        return;

    # Check overlap with the piece to the Northwest
    otherX = myX - 1
    otherY = myY
    if abs(otherX) + abs(otherY) <= 3: # piece is on the board
        otherDirection = pieceDirection[indexOfCoord(otherX, otherY)]
        # overlaps if we have an 'outie' to the NW and other has an 'outie' to the SE.
        if (myDirection == SOUTH or myDirection == EAST) and \
        (otherDirection == NORTH or otherDirection == WEST):
            return True

    # ...the piece to the SouthWest
    otherX = myX
    otherY = myY -1
    if abs(otherX) + abs(otherY) <= 3: # piece is on the board
        otherDirection = pieceDirection[indexOfCoord(otherX, otherY)]
        # overlaps if we have an 'outie' to the SW and other has an 'outie' to the NE.
        if (myDirection == NORTH or myDirection == EAST) and \
        (otherDirection == SOUTH or otherDirection == WEST):
            return True

    # ...the piece to the SouthEast
    otherX = myX + 1
    otherY = myY
    if abs(otherX) + abs(otherY) <= 3: # piece is on the board
        otherDirection = pieceDirection[indexOfCoord(otherX, otherY)]
        # overlaps if we have an 'outie' to the SE and other has an 'outie' to the NW.
        if (myDirection == NORTH or myDirection == WEST) and \
        (otherDirection == SOUTH or otherDirection == EAST):
            return True

    # ...the piece to the NorthEast
    otherX = myX
    otherY = myY + 1
    if abs(otherX) + abs(otherY) <= 3: # piece is on the board
        otherDirection = pieceDirection[indexOfCoord(otherX, otherY)]
        # overlaps if we have an 'outie' to the NE and other has an 'outie' to the SW.
        if (myDirection == SOUTH or myDirection == WEST) and \
        (otherDirection == NORTH or otherDirection == EAST):
            return True

    # Nothing overlaps with the passed piece.
    return False

# Place the piece from the given index in the spiral.
# Attempt to place the piece in all four directions,
# recursing for each direction, to walk the entire spiral.
def placePiece(spiralIndex):
    global spiral
    global pieceDirection
    global directions
    global NOWHERE

    # DEBUG to profile a version that eventually finishes.
    # I added this code because I believed the code would take
    # over a century to run. It turns out it takes less than a day.
    # >=16 takes 151 seconds and produces 3,110,400 * 4 boards.
    # >= 18 takes 599 seconds and produces 37,324,800 boards.
    # >= 19 takes 1161 seconds (20 minutes) and produces 99,532,800 boards.
    # >= 21 takes 5261 seconds (87 minutes) and produces 298,598,400 boards.
    # >= 23 takes 23138 seconds (385 minutes = 6.5 hours) and produces 1,274,019,840 boards.
    # full run took 82921 seconds (23 hours) and produced 5,435,817,984 boards.
#    if spiralIndex >= 23:
#        recordValidBoard()
#        return


    # If we've reached the end of the spiral
    # We should have filled the board, and have a valid board.
    if spiralIndex > len(spiral) - 1:
        recordValidBoard()
        return

    coord = spiral[spiralIndex];
    pieceIndex = indexOfCoord(coord[0], coord[1])
    
    for d in directions:
        pieceDirection[pieceIndex] = d
        # see if there's an overlap, if not,
        # leave this piece here and place the following pieces.
        if not pieceOverlaps(coord[0], coord[1]):
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

# Profile the main function so we get a print of how long it took to run
# and so that we get some hints of where the time went.

# walkBoards()
cProfile.run('walkBoards()')

