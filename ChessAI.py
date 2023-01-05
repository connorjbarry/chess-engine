import random
from ChessEngine import *
from EvaluateState import *

fen = Fen()

boardEval = Evaluate()
DEPTH = 2


class AI():
    def __init__(self, gs):
        self.piece = Piece()
        self.gs = gs

    """ 
    Returns a random move from the list of valid moves
    """

    def findRandomMove(self, validMoves):
        return random.choice(validMoves)

    """ 
    Makes the best move using whichever algorithm is chosen
    """

    def findBestMove(self, gs, validMoves):
        global bestMove
        bestMove = 0
        self.minmax(gs, validMoves, 2, self.gs.whiteToMove)
        return bestMove

    """ 
    Returns the best move from the list of valid moves using minmax algo without alpha beta pruning
    """

    def minmax(self, gs, validMoves, depth, whiteToMove):
        global bestMove
        if depth == 0:
            return boardEval.evaluatePieceValues(gs)

        if whiteToMove:
            maxScore = -9999
            for move in validMoves:
                gs.makeMove(move)
                score = self.minmax(gs, gs.getLegalMoves(), depth - 1, False)
                gs.undoMove()
                if score > maxScore:
                    maxScore = score
                    if depth == DEPTH:
                        bestMove = move
            return maxScore

        else:
            minScore = 9999
            for move in validMoves:
                gs.makeMove(move)
                score = self.minmax(gs, gs.getLegalMoves(), depth - 1, True)
                gs.undoMove()
                if score < minScore:
                    minScore = score
                    if depth == DEPTH:
                        bestMove = move
            return minScore

    """  
        Tests the amount of moves being generated at a certain depth for a given state
    """

    def testMoveGeneration(self, depth):
        if depth == 0:
            return 1

        validMoves = gs.getLegalMoves()

        numPositions = 0

        for move in validMoves:
            self.gs.makeMove(move)
            numPositions += self.testMoveGeneration(depth - 1)
            self.gs.undoMove()

        return numPositions
