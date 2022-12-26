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
    TODO:
    This does not work on castling, en passant, pawn promotion, or checks
    """

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = 0
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    """ 
    Undo the last move made
    """

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

    """ 
    Responsible for all the logic that determines if a move is valid, including checks
    """

    def getValidMoves(self):
        return self.getPossibleMoves()

    """ 
    Responsible for all valid moves of a given piece 
    """

    def getPossibleMoves(self):
        moves = []
        piece = Piece()
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.checkTurn(self.board[r][c], piece)
                # print(
                #     f'piece: {self.board[r][c]} == {turn | piece.Pawn} type of piece = {type(turn | piece.Pawn)} turn = {turn}')
                if (turn == piece.white and self.whiteToMove) or (turn == piece.black and not self.whiteToMove):
                    chessPiece = self.board[r][c]
                    # TODO: can try to simplify this if statement
                    if chessPiece == (turn | piece.Pawn):
                        moves.extend(self.getPawnMoves(r, c))
                    elif chessPiece == (turn | piece.Knight):
                        moves.extend(self.getKnightMoves(r, c, piece=Piece()))
                    elif chessPiece == (turn | piece.Rook):
                        moves.extend(self.getRookMoves(r, c, piece=Piece()))
                    elif chessPiece == (turn | piece.Bishop):
                        moves.extend(self.getBishopMoves(r, c, piece=Piece()))
                    elif chessPiece == (turn | piece.Queen):
                        moves.extend(self.getQueenMoves(r, c, piece=Piece()))
                    elif chessPiece == (turn | piece.King):
                        moves.extend(self.getKingMoves(r, c, piece=Piece()))
        return moves

    """ 
    Gets all pawn moves for the pawn located at row, col and returns a list of moves
    
    TODO: 
    - En passant, Pawn promotion, Checks
    """

    def getPawnMoves(self, r, c):
        pawnMoves = []
        if self.whiteToMove:
            if self.board[r-1][c] == 0:
                pawnMoves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == 0:
                    pawnMoves.append(Move((r, c), (r-2, c), self.board))
            # capture left
            if c - 1 >= 0:
                if self.board[r-1][c-1] > 16:  # checks for black piece
                    pawnMoves.append(Move((r, c), (r-1, c-1), self.board))
            # capture right
            if c + 1 <= 7:
                if self.board[r-1][c+1] > 16:  # checks for black piece
                    pawnMoves.append(Move((r, c), (r-1, c+1), self.board))
        else:
            if self.board[r+1][c] == 0:
                pawnMoves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == 0:
                    pawnMoves.append(Move((r, c), (r+2, c), self.board))
            # capture left
            if c - 1 >= 0:
                if self.board[r+1][c-1] < 16 and self.board[r+1][c-1] != 0:
                    pawnMoves.append(Move((r, c), (r+1, c-1), self.board))
            # capture right
            if c + 1 <= 7:
                if self.board[r+1][c+1] < 16 and self.board[r+1][c+1] != 0:
                    pawnMoves.append(Move((r, c), (r+1, c+1), self.board))

        return pawnMoves

    """ 
    Gets all knight moves for the knight located at row, col and returns a list of moves

    TODO:
    - Checks
    """

    def getKnightMoves(self, r, c, piece):
        knightMoves = []
        directions = [(1, 2), (2, 1), (-1, 2), (-2, 1),
                      (1, -2), (2, -1), (-1, -2), (-2, -1)]
        allyColor = piece.white if self.whiteToMove else piece.black
        for direction in directions:
            endRow = r + direction[0]
            endCol = c + direction[1]
            # checks if move is on board
            if (endRow < 0 or endRow >= 8) or (endCol < 0 or endCol >= 8):
                continue

            endPositionColor = self.checkTurn(
                self.board[endRow][endCol], piece)
            if endPositionColor != allyColor:
                knightMoves.append(Move((r, c), (endRow, endCol), self.board))

        return knightMoves

    """ 
    Gets all rook moves for the rook located at row, col and returns a list of moves

    TODO:
    - Castling, Checks
    """

    def getRookMoves(self, r, c, piece):
        rookMoves = []
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        allyColor = piece.white if self.whiteToMove else piece.black
        for direction in directions:
            for moveLength in range(8):
                endRow = r + direction[0] * moveLength
                endCol = c + direction[1] * moveLength
                # checks if move is on board
                if (endRow < 0 or endRow >= 8) or (endCol < 0 or endCol >= 8):
                    break

                endPositionColor = self.checkTurn(
                    self.board[endRow][endCol], piece)
                if endPositionColor != allyColor:
                    rookMoves.append(
                        Move((r, c), (endRow, endCol), self.board))

        return rookMoves

    """ 
    Gets all bishop moves for the bishop located at row, col and returns a list of moves

    TODO:
    - Checks
    """

    def getBishopMoves(self, r, c, piece):
        bishopMoves = []
        directions = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
        allyColor = piece.white if self.whiteToMove else piece.black
        for direction in directions:
            for moveLength in range(8):
                endRow = r + direction[0] * moveLength
                endCol = c + direction[1] * moveLength
                # checks if move is on board
                if (endRow < 0 or endRow >= 8) or (endCol < 0 or endCol >= 8):
                    break

                endPositionColor = self.checkTurn(
                    self.board[endRow][endCol], piece)
                if endPositionColor != allyColor:
                    bishopMoves.append(
                        Move((r, c), (endRow, endCol), self.board))

        return bishopMoves

    """ 
    Gets all queen moves for the queen located at row, col and returns a list of moves

    TODO:
    - Checks
    """

    def getQueenMoves(self, r, c, piece):
        queenMoves = []
        queenMoves.extend(self.getRookMoves(r, c, piece))
        queenMoves.extend(self.getBishopMoves(r, c, piece))
        return queenMoves

    """
    Gets all king moves for the king located at row, col and returns a list of moves

    TODO:
    - Castling, Checks
    """

    def getKingMoves(self, r, c, piece):
        kingMoves = []
        possibleKingMoves = [(1, 0), (1, 1), (0, 1), (-1, 1),
                             (-1, 0), (-1, -1), (0, -1), (1, -1)]
        allyColor = piece.white if self.whiteToMove else piece.black

        for move in possibleKingMoves:
            endRow = r + move[0]
            endCol = c + move[1]
            # check if move not on board
            if (endRow < 0 or endRow >= 8) or (endCol < 0 or endCol >= 8):
                continue

            endPositionColor = self.checkTurn(
                self.board[endRow][endCol], piece)
            if endPositionColor != allyColor:
                kingMoves.append(Move((r, c), (endRow, endCol), self.board))

        return kingMoves

    """
        Gets the color of the piece passed into the function
    """

    def checkTurn(self, chessPiece, piece):
        if chessPiece == 0:
            return None
        return piece.getPieceColor(chessPiece)


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
    # move Piece.White | Piece.Rook -> 0b01110 -> 14
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

    def fenNotationDict(self):
        return {
            "p": self.Pawn | self.white,
            "P": self.Pawn | self.black,
            "r": self.Rook | self.white,
            "R": self.Rook | self.black,
            "n": self.Knight | self.white,
            "N": self.Knight | self.black,
            "b": self.Bishop | self.white,
            "B": self.Bishop | self.black,
            "q": self.Queen | self.white,
            "Q": self.Queen | self.black,
            "k": self.King | self.white,
            "K": self.King | self.black
        }


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

    # ? Init function not needed
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
