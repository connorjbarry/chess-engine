import random


class AI():
    def __init__(self, gs):
        self.gs = gs
        self.validMoves = gs.getLegalMoves()

    def findRandomMove(validMoves):
        return random.choice(validMoves)
