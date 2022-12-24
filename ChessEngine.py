""" 
This class holds all information about the current state of a chess game. It will be responsible for determining valid moves, as well as keeping a move log.
"""


class GameState():
    def __init__(self, fen):
        """ 
            8x8 2d array representing the board, each element is a 2 character string. The first character represents the color, second character represents the type of piece.
        """
        self.board = fen.buildStartingBoard()
        self.whiteToMove = True
        self.moveLog = []

    """ 
    This does not work on castling, en passant, pawn promotion, or checks
    """

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = 0
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove


""" 
Responsible for storing all information about the current move. It will also be responsible for determining if a move is valid.
"""


class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * \
            100 + self.endRow * 10 + self.endCol

    def getChessNotation(self):
        # can turn into real chess notation if need be
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


"""
    Responsible for logic having to do with each piece, holds a binary 
    representation of the piece.
"""


class Piece():
    # move Piece.White | Piece.Rook -> 0b10110
    def __init__(self):
        self.Non = 0
        self.King = 1
        self.Pawn = 2
        self.Knight = 3
        self.Bishop = 5
        self.Rook = 6
        self.Queen = 7

        self.white = 8
        self.black = 16

        self.typeMask = 0b111
        self.whiteMask = 0b01000
        self.blackMask = 0b10000
        self.colorMask = self.whiteMask | self.blackMask

    def getPieceType(self, piece):
        return piece & self.typeMask

    def getPieceColor(self, piece):
        return piece & self.colorMask

    def isRookOrQueen(self, piece):
        return piece & 0b110 == 0b110

    def isBishopOrQueen(self, piece):
        return piece & 0b101 == 0b101

    def isSlidingPiece(self, piece):
        return piece & 0b100 == 0b100


""" 
    This is responsible for handling fen strings and utility
"""


class Fen:
    startingFenString = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    piece = Piece()

    pieceTypeFromSymbol = {
        "p": piece.Pawn,
        "r": piece.Rook,
        "n": piece.Knight,
        "b": piece.Bishop,
        "q": piece.Queen,
        "k": piece.King
    }

    # Init function not needed?
    def __init__(self):
        self.squares = [None] * 64

    def buildStartingBoard(self):
        return self.buildBoard(self.startingFenString)

    def buildBoard(self, fenString):
        fenParts = fenString.split(" ")
        if len(fenParts) != 6:
            return "Invalid FEN string"

        # Get board layout
        boardLayout = fenParts[0]
        boardRows = boardLayout.split("/")
        if len(boardRows) != 8:
            return "Invalid board layout in FEN string"

        # Build board
        board = []
        for row in boardRows:
            board_row = []
            for char in row:
                if char.isdigit():
                    for i in range(int(char)):
                        board_row.append(0)
                else:
                    board_row.append(self.getPiece(char))
            board.append(board_row)

        return board

    def getPiece(self, char, piece=Piece()):
        pieceColor = piece.white if char.isupper() else piece.black
        pieceType = self.pieceTypeFromSymbol[char.lower()]
        return pieceColor | pieceType
