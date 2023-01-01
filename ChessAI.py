import random
from ChessEngine import *
from EvaluateState import *

fen = Fen()
gs = GameState(fen)
boardEval = Evaluate()


class AI():
    def __init__(self, gs):
        self.piece = Piece()
        self.gs = gs

    """ 
    Returns a random move from the list of valid moves
    """

    def findRandomMove(self, validMoves):
        evaluation = boardEval.evaluatePieceValues(self.gs)
        print(
            f'Evaluation for {"white" if self.gs.whiteToMove else "black"}: {evaluation if self.gs.whiteToMove else -evaluation}')
        return random.choice(validMoves)

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
