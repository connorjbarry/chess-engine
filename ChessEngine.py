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
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False

    """ 
    TODO:
    This does not work on castling, en passant, pawn promotion, or checks
    """

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = 0
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        # update king's location if moved
        piece = Piece()
        if piece.getPieceType(move.pieceMoved) == piece.King:
            if self.whiteToMove:
                self.whiteKingLocation = (move.endRow, move.endCol)
            else:
                self.blackKingLocation = (move.endRow, move.endCol)

    """ 
    Undo the last move made
    """

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # update king's location if moved
            piece = Piece()
            if piece.getPieceType(move.pieceMoved) == piece.King:
                if self.whiteToMove:
                    self.whiteKingLocation = (move.startRow, move.startCol)
                else:
                    self.blackKingLocation = (move.startRow, move.startCol)

    """ 
    Responsible for all the logic that determines if a move is valid, including checks
    """

    def getLegalMoves(self):
        piece = Piece()
        moves = []
        self.inCheck, self.pins, self.checks = self.getAllPinsAndChecks(piece)
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.inCheck:
            # There is only one check so we can block, take or move king
            if len(self.checks) == 1:
                print("here in checks > 1")
                moves = self.getPsuedoLegalMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                # if knight, must capture knight or move king
                if piece.getPieceType(pieceChecking) == piece.Knight:
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        availableSquare = (
                            kingRow + check[2][0] * i, kingCol + check[2][1] * i)
                        print(availableSquare)
                        validSquares.append(availableSquare)

                        # stop checking for available squares when you reach the checking piece
                        if availableSquare[0] == checkRow and availableSquare[1] == checkCol:
                            break

                    # get rid of any moves that are dont block check, take checking piece or move king
                    for i in range(len(moves) - 1, -1, -1):
                        # king moves are already generated so those stay
                        if piece.getPieceType(moves[i].pieceMoved) != piece.King:
                            # check if move is inside of valid moves, if not remove from list
                            if not (moves[i].endRow, moves[i].endCol) in validSquares:
                                print("here")
                                moves.remove(moves[i])

                        # There is a double check or more, so king must move
            else:
                moves = self.getKingMoves(kingRow, kingCol, piece=Piece())

        # the king is not in check
        else:
            moves = self.getPsuedoLegalMoves()

        if len(moves) == 0:
            # checkmate
            if self.inCheck:
                self.checkmate = True
            # stalemate
            else:
                self.stalemate = True
        # in the case that we undo a move and checkmate is true, we need to set it to false
        else:
            self.checkmate = False
            self.stalemate = False

        return moves

    """ 
    Responsible for all valid moves of a given piece 
    """

    def getPsuedoLegalMoves(self):
        moves = []
        piece = Piece()
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.checkTurn(self.board[r][c], piece)

                if (turn == piece.white and self.whiteToMove) or (turn == piece.black and not self.whiteToMove):
                    chessPiece = self.board[r][c]
                    # TODO: can try to simplify this if statement
                    if piece.getPieceType(chessPiece) == piece.Pawn:
                        moves.extend(self.getPawnMoves(r, c))

                    elif piece.getPieceType(chessPiece) == piece.Knight:
                        moves.extend(self.getKnightMoves(r, c, piece=Piece()))

                    elif piece.getPieceType(chessPiece) == piece.Rook:
                        moves.extend(self.getRookMoves(r, c, piece=Piece()))

                    elif piece.getPieceType(chessPiece) == piece.Bishop:
                        moves.extend(self.getBishopMoves(r, c, piece=Piece()))

                    elif piece.getPieceType(chessPiece) == piece.Queen:
                        moves.extend(self.getQueenMoves(r, c, piece=Piece()))

                    elif piece.getPieceType(chessPiece) == piece.King:
                        moves.extend(self.getKingMoves(r, c, piece=Piece()))

        return moves

    """ 
    Checks moves for a check on the king or if a piece is pinned and cannot move
    """

    def getAllPinsAndChecks(self, piece):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = piece.black
            allyColor = piece.white
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = piece.white
            allyColor = piece.black
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))

        # check for pins and checks
        for j in range(len(directions)):
            direction = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + direction[0] * i
                endCol = startCol + direction[1] * i
                # ensures endRow and endCol are on the board
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    # Checks if the piece in the direction is ally for possible pin
                    if piece.getPieceColor(endPiece) == allyColor:
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, direction)
                        # already an ally piece in direction, no possible pin or check
                        else:
                            break
                    elif piece.getPieceColor(endPiece) == enemyColor:
                        # gets the type of piece in direction to check if it can move in given direction
                        pieceType = piece.getPieceType(endPiece)

                        # checks for piece and the direction that a given piece can move for capture
                        #!Does not account for knights
                        if (pieceType == piece.Rook and 0 <= j <= 3) or (pieceType == piece.Bishop and 4 <= j <= 7) or piece.Queen or (pieceType == piece.King and i == 1) or (pieceType == piece.Pawn and i == 1 and ((enemyColor == piece.white and 6 <= j <= 7) or (enemyColor == piece.black and 4 <= j <= 5))):
                            # if pin is empty, then it is a check
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, direction))
                                break
                            # otherwise a piece is in the way, which is now pinned
                            else:
                                pins.append(possiblePin)
                                break
                else:
                    break

        # checks for knight checks, since the knight is not a sliding piece
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        for move in knightMoves:
            endRow = startRow + move[0]
            endCol = startCol + move[1]
            # check if move is on board
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                # checks if piece is enemy knight
                if piece.getPieceColor(endPiece) == enemyColor and piece.getPieceType(endPiece) == piece.Knight:
                    inCheck = True
                    checks.append((endRow, endCol, move))

        return inCheck, pins, checks

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
        enemyColor = piece.black if self.whiteToMove else piece.white
        for direction in directions:
            for moveLength in range(1, 8):
                endRow = r + direction[0] * moveLength
                endCol = c + direction[1] * moveLength
                # checks if move is on board
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    endPieceColor = self.checkTurn(endPiece, piece)
                    if endPiece == 0:
                        rookMoves.append(
                            Move((r, c), (endRow, endCol), self.board))
                    elif endPieceColor == enemyColor:
                        rookMoves.append(
                            Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

        return rookMoves

    """ 
    Gets all bishop moves for the bishop located at row, col and returns a list of moves

    TODO:
    - Checks
    """

    def getBishopMoves(self, r, c, piece):
        bishopMoves = []
        directions = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
        enemyColor = piece.black if self.whiteToMove else piece.white
        for direction in directions:
            for moveLength in range(1, 8):
                endRow = r + direction[0] * moveLength
                endCol = c + direction[1] * moveLength
                # checks if move is on board
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    endPieceColor = self.checkTurn(endPiece, piece)
                    if endPiece == 0:
                        bishopMoves.append(
                            Move((r, c), (endRow, endCol), self.board))
                    elif endPieceColor == enemyColor:
                        bishopMoves.append(
                            Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

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
            if endPositionColor == allyColor:
                break
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
