from ChessEngine import *


piece = Piece()
material = Material()


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
                return -9999
            else:
                return 9999
        elif gs.stalemate:
            return 0

        pawnMaterial = material.getPawnMaterial(gs)
        knightMaterial = material.getKnightMaterial(gs)
        bishopMaterial = material.getBishopMaterial(gs)
        rookMaterial = material.getRookMaterial(gs)
        queenMaterial = material.getQueenMaterial(gs)
        kingMaterial = material.getKingMaterial(gs)

        evaluation = 0

        evaluation += self.pieceEval[piece.Pawn] * \
            (pawnMaterial['white'] - pawnMaterial['black'])
        evaluation += self.pieceEval[piece.Knight] * \
            (knightMaterial['white'] - knightMaterial['black'])
        evaluation += self.pieceEval[piece.Bishop] * \
            (bishopMaterial['white'] - bishopMaterial['black'])
        evaluation += self.pieceEval[piece.Rook] * \
            (rookMaterial['white'] - rookMaterial['black'])
        evaluation += self.pieceEval[piece.Queen] * \
            (queenMaterial['white'] - queenMaterial['black'])
        evaluation += self.pieceEval[piece.King] * \
            (kingMaterial['white'] - kingMaterial['black'])

        return evaluation
