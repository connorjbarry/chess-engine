from ChessEngine import *


piece = Piece()
material = Material()
CHECKMATE = 9999


class Evaluate:
    def __init__(self):
        self.pieceEval = {
            piece.Non: 0,
            piece.Pawn: 10,
            piece.Knight: 30,
            piece.Bishop: 30,
            piece.Rook: 50,
            piece.Queen: 90,
            piece.King: 900
        }

    """ 
    Evaluates the state of the board, a positive value means white is winning, a negative value means black is winning in terms of pieces
    """

    def evaluatePieceValues(self, gs):
        if gs.checkmate:
            if gs.whiteToMove:
                return -CHECKMATE
            else:
                return CHECKMATE
        elif gs.stalemate:
            return 0

        evaluation = 0

        for row in range(len(gs.board)):
            for col in range(len(gs.board[row])):
                pieceType = piece.getPieceType(gs.board[row][col])
                if gs.whiteToMove:
                    evaluation += self.pieceEval[pieceType]
                else:
                    evaluation -= self.pieceEval[pieceType]

        return evaluation
