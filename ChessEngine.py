"""
This class holds all information about the current state of a chess game. It will be responsible for determining valid moves, as well as keeping a move log.
"""


class GameState():
    def __init__(self, fen):
        """
            8x8 2d array representing the board, each element is a 2 character string. The first character represents the color, second character represents the type of piece.
        """
        # self.fenString = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.fenString = "r3k2r/pppppppp/8/8/8/8/PPPPPnPP/R3K2R w KQkq - 0 1"
        self.board = fen.buildBoard(self.fenString)
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False

        # square where en passant is possible, right now it is empty
        self.enpassantPossible = ()

        self.currentCastleRights = Castle(True, True, True, True)
        self.castleLog = [Castle(self.currentCastleRights.whiteKingSideCastle,
                                 self.currentCastleRights.whiteQueenSideCastle,
                                 self.currentCastleRights.blackKingSideCastle,
                                 self.currentCastleRights.blackQueenSideCastle
                                 )]


    """
    Takes a move as a parameter and executes it

    TODO:
    This does not work on castling, en passant
    """

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = 0
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        # update king's location if moved
        piece = Piece()
        if piece.getPieceType(move.pieceMoved) == piece.King:
            if self.whiteToMove:
                self.whiteKingLocation = (move.endRow, move.endCol)
            else:
                self.blackKingLocation = (move.endRow, move.endCol)

        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = 0
            move.pieceCaptured = (
                piece.white if not self.whiteToMove else piece.black) | piece.Pawn


        if piece.getPieceType(move.pieceMoved) == piece.Pawn and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = (
                (move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                # kingside castle
                self.board[move.endRow][move.endCol -
                                        1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = 0
            else:
                # queenside castle
                self.board[move.endRow][move.endCol +
                                        1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = 0

        # castle rights

        self.updateCastleRights(move, piece)
        if self.castleLog is None:
            self.castleLog = [Castle(self.currentCastleRights.whiteKingSideCastle,
                                     self.currentCastleRights.whiteQueenSideCastle,
                                     self.currentCastleRights.blackKingSideCastle,
                                     self.currentCastleRights.blackQueenSideCastle
                                     )]
        else:
            self.castleLog.append(Castle(self.currentCastleRights.whiteKingSideCastle,
                                         self.currentCastleRights.whiteQueenSideCastle,
                                         self.currentCastleRights.blackKingSideCastle,
                                         self.currentCastleRights.blackQueenSideCastle
                                         ))
        self.whiteToMove = not self.whiteToMove                                       

    """ 

    Undo the last move made
    """

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            # update king's location if moved
            piece = Piece()
            if piece.getPieceType(move.pieceMoved) == piece.King:
                if self.whiteToMove:
                    self.whiteKingLocation = (move.startRow, move.startCol)
                else:
                    self.blackKingLocation = (move.startRow, move.startCol)

            # undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = 0
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)

            # undo 2 square pawn advance
            if move.pieceMoved == piece.Pawn and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            self.whiteToMove = not self.whiteToMove


        # undo castle rights

        self.castleLog.pop()
        self.castleLog = self.castleLog[-1]

        # undo castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                # kingside castle
                self.board[move.endRow][move.endCol +
                                        1] = self.board[move.endRow][move.endCol - 1]
                self.board[move.endRow][move.endCol - 1] = 0
            else:
                # queenside castle
                self.board[move.endRow][move.endCol -
                                        2] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = 0

    """ 

    Responsible for all the logic that determines if a move is valid, including checks
    """

    def getLegalMoves(self):
        tempEnpassantPossible = self.enpassantPossible
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
                                moves.remove(moves[i])

                        # There is a double check or more, so king must move
            else:
                moves = self.getKingMoves(kingRow, kingCol, piece=Piece())

        # the king is not in check
        else:
            moves = self.getPsuedoLegalMoves()
            if self.whiteToMove:
                moves.extend(self.getCastleMoves(
                    self.whiteKingLocation[0], self.whiteKingLocation[1], moves))
            else:
                moves.extend(self.getCastleMoves(
                    self.blackKingLocation[0], self.blackKingLocation[1], moves))

        if len(moves) == 0:
            # checkmate
            if self.kingInCheck():
                self.checkmate = True
            # stalemate
            else:
                self.stalemate = True
        # in the case that we undo a move and checkmate is true, we need to set it to false
        else:
            self.checkmate = False
            self.stalemate = False

        self.enpassantPossible = tempEnpassantPossible
        return moves

    """
        Helper function to check if king is in check
    """

    def kingInCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    """
        Helper function to check if a square is under attack
    """

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getPsuedoLegalMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

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
                        moves.extend(self.getPawnMoves(r, c, piece=Piece()))

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
                    endPieceColor = piece.getPieceColor(endPiece)
                    # Checks if the piece in the direction is ally for possible pin
                    if endPieceColor == allyColor:
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, direction)
                        # already an ally piece in direction, no possible pin or check
                        else:
                            break
                    elif endPieceColor == enemyColor:
                        # gets the type of piece in direction to check if it can move in given direction
                        enemyPieceType = piece.getPieceType(endPiece)

                        # checks for piece and the direction that a given piece can move for capture
                        #! Does not account for knights
                        if ((enemyPieceType == piece.Rook and 0 <= j <= 3)
                            or (enemyPieceType == piece.Bishop and 4 <= j <= 7)
                            or (enemyPieceType == piece.Queen)
                            or (enemyPieceType == piece.King and i == 1)
                            or (enemyPieceType == piece.Pawn and i == 1 and ((enemyColor == piece.white and 6 <= j <= 7)
                                                                             or (enemyColor == piece.black and 4 <= j <= 5)))):
                            # if pin is empty, then it is a check
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, direction))
                                break
                            # otherwise a piece is in the way, which is now pinned
                            else:
                                pins.append(possiblePin)
                                break
                        # if the piece is not a piece that can move in the given direction, then it is not a check or pin
                        else:
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
        Updates the castle rights given a certain move on the board
    """

    def updateCastleRights(self, move, piece):
        if move.pieceMoved == (piece.white | piece.King):
            self.whiteCastleKingside = False
            self.whiteCastleQueenside = False
        elif move.pieceMoved == (piece.black | piece.King):
            self.blackCastleKingside = False
            self.blackCastleQueenside = False
        elif move.pieceMoved == (piece.white | piece.Rook) or move.pieceCaptured == (piece.white | piece.Rook):
            if move.startRow == 7:
                if move.startCol == 0:
                    self.whiteCastleQueenside = False
                elif move.startCol == 7:
                    self.whiteCastleKingside = False
        elif move.pieceMoved == (piece.black | piece.Rook) | move.pieceCaptured == (piece.black | piece.Rook):
            if move.startRow == 0:
                if move.startCol == 0:
                    self.blackCastleQueenside = False
                elif move.startCol == 7:
                    self.blackCastleKingside = False

    """ 

    Gets all pawn moves for the pawn located at row, col and returns a list of moves

    TODO:
    - En passant
    """

    def getPawnMoves(self, r, c, piece):
        isPinned = False
        pinDirection = ()
        for pin in self.pins:
            if pin[0] == r and pin[1] == c:
                isPinned = True
                pinDirection = (pin[2][0], pin[2][1])
                self.pins.remove(pin)
                break

        pawnMoves = []
        if self.whiteToMove:
            if self.board[r-1][c] == 0:
                if not isPinned or pinDirection == (-1, 0):
                    pawnMoves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == 0:
                        pawnMoves.append(Move((r, c), (r-2, c), self.board))
            # capture left
            if c - 1 >= 0:
                # checks for black piece
                if piece.getPieceColor(self.board[r-1][c-1]) == piece.black:
                    if not isPinned or pinDirection == (-1, -1):
                        pawnMoves.append(Move((r, c), (r-1, c-1), self.board))
                # checks for en passant
                elif (r-1, c-1) == self.enpassantPossible:
                    pawnMoves.append(
                        Move((r, c), (r-1, c-1), self.board, isEnpassantPossible=True))
            # capture right
            if c + 1 <= 7:
                # checks for black piece
                if piece.getPieceColor(self.board[r-1][c+1]) == piece.black:
                    if not isPinned or pinDirection == (-1, 1):
                        pawnMoves.append(Move((r, c), (r-1, c+1), self.board))
                # checks for en passant
                elif (r-1, c+1) == self.enpassantPossible:
                    pawnMoves.append(
                        Move((r, c), (r-1, c+1), self.board, isEnpassantPossible=True))

        else:
            if self.board[r+1][c] == 0:
                if not isPinned or pinDirection == (1, 0):
                    pawnMoves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == 0:
                        pawnMoves.append(Move((r, c), (r+2, c), self.board))
            # capture left
            if c - 1 >= 0:
                if piece.getPieceColor(self.board[r+1][c-1]) == piece.white:
                    if not isPinned or pinDirection == (1, -1):
                        pawnMoves.append(Move((r, c), (r+1, c-1), self.board))
                # checks for en passant
                elif (r+1, c-1) == self.enpassantPossible:
                    pawnMoves.append(
                        Move((r, c), (r+1, c-1), self.board, isEnpassantPossible=True))
            # capture right
            if c + 1 <= 7:
                if piece.getPieceColor(self.board[r+1][c+1]) == piece.white:
                    if not isPinned or pinDirection == (1, 1):
                        pawnMoves.append(Move((r, c), (r+1, c+1), self.board))
                # checks for en passant
                elif (r+1, c+1) == self.enpassantPossible:
                    pawnMoves.append(
                        Move((r, c), (r+1, c+1), self.board, isEnpassantPossible=True))

        return pawnMoves

    """
    Gets all knight moves for the knight located at row, col and returns a list of moves
    """

    def getKnightMoves(self, r, c, piece):
        isPinned = False
        for pin in self.pins:
            if pin[0] == r and pin[1] == c:
                isPinned = True
                self.pins.remove(pin)
                break

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
            if not isPinned:
                endPositionColor = self.checkTurn(
                    self.board[endRow][endCol], piece)
                if endPositionColor != allyColor:
                    knightMoves.append(
                        Move((r, c), (endRow, endCol), self.board))

        return knightMoves

    """
    Gets all rook moves for the rook located at row, col and returns a list of moves

    TODO:
    - Castling
    """

    def getRookMoves(self, r, c, piece):
        isPinned = False
        pinDirection = ()
        for pin in self.pins:
            if pin[0] == r and pin[1] == c:
                isPinned = True
                pinDirection = (pin[2][0], pin[2][1])
                if piece.getPieceType(self.board[pin[0]][pin[1]]) != piece.Queen:
                    self.pins.remove(pin)
                break

        rookMoves = []
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        enemyColor = piece.black if self.whiteToMove else piece.white
        for direction in directions:
            for moveLength in range(1, 8):
                endRow = r + direction[0] * moveLength
                endCol = c + direction[1] * moveLength
                # checks if move is on board
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not isPinned or pinDirection == direction or pinDirection == (-direction[0], -direction[1]):
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
    """

    def getBishopMoves(self, r, c, piece):
        isPinned = False
        pinDirection = ()
        for pin in self.pins:
            if pin[0] == r and pin[1] == c:
                isPinned = True
                pinDirection = (pin[2][0], pin[2][1])
                if piece.getPieceType(self.board[pin[0]][pin[1]]) != piece.Queen:
                    self.pins.remove(pin)
                break

        bishopMoves = []
        directions = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
        enemyColor = piece.black if self.whiteToMove else piece.white
        for direction in directions:
            for moveLength in range(1, 8):
                endRow = r + direction[0] * moveLength
                endCol = c + direction[1] * moveLength
                # checks if move is on board
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not isPinned or pinDirection == direction or pinDirection == (-direction[0], -direction[1]):
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
    """

    def getQueenMoves(self, r, c, piece):
        queenMoves = []
        queenMoves.extend(self.getRookMoves(r, c, piece))
        queenMoves.extend(self.getBishopMoves(r, c, piece))
        return queenMoves

    """
    Gets all king moves for the king located at row, col and returns a list of moves

    TODO:
    - Castling
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
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPositionColor = self.checkTurn(
                    self.board[endRow][endCol], piece)
                if endPositionColor != allyColor:
                    if allyColor == piece.white:
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.getAllPinsAndChecks(piece)
                    if not inCheck:
                        kingMoves.append(
                            Move((r, c), (endRow, endCol), self.board))
                    if allyColor == piece.white:
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

        return kingMoves

    """ 
        Generates all valid castle moves for the king 
    """

    def getCastleMoves(self, r, c, piece):
        castleMoves = []
        if self.squareUnderAttack(r, c):
            return castleMoves

        if (self.whiteToMove and self.currentCastleRights.whiteKingSideCastle) or (not self.whiteToMove and self.currentCastleRights.blackKingSideCastle):
            castleMoves.extend(self.getKingSideCastleMoves(r, c, piece))

        if (self.whiteToMove and self.currentCastleRights.whiteQueenSideCastle) or (not self.whiteToMove and self.currentCastleRights.blackQueenSideCastle):
            castleMoves.extend(
                self.getQueenSideCastleMoves(r, c, piece))

        return castleMoves

    """ 
        Gets all the valid king side castle moves for the king
    """

    def getKingSideCastleMoves(self, r, c, piece):
        kingSideCastleMoves = []
        if self.board[r][c+1] == 0 or self.board[r][c+2] == 0:
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                kingSideCastleMoves.append(
                    Move((r, c), (r, c+2), self.board, isCastleMove=True))

        return kingSideCastleMoves

    """
        Gets all the valid queen side castle moves for the king
    """

    def getQueenSideCastleMoves(self, r, c, piece):
        queenSideCastleMoves = []
        if self.board[r][c-1] == 0 and self.board[r][c-2] == 0 and self.board[r][c-3] == 0:
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                queenSideCastleMoves.append(
                    Move((r, c), (r, c-2), self.board, isCastleMove=True))

        return queenSideCastleMoves

    """
        Gets the color of the piece passed into the function
    """

    def checkTurn(self, chessPiece, piece):
        return piece.getPieceColor(chessPiece)



""" 
    Determines the validity of a castle move, acts as a storage class for the castle rights
"""


class Castle():
    def __init__(self, whiteKingSideCastle, whiteQueenSideCastle, blackKingSideCastle, blackQueenSideCastle):
        self.whiteKingSideCastle = whiteKingSideCastle
        self.whiteQueenSideCastle = whiteQueenSideCastle
        self.blackKingSideCastle = blackKingSideCastle
        self.blackQueenSideCastle = blackQueenSideCastle


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


    def __init__(self, startSq, endSq, board, isEnpassantPossible=False, isCastleMove=False):

        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * \
            100 + self.endRow * 10 + self.endCol

        piece = Piece()
        self.pawnPromotion = (piece.getPieceType(self.pieceMoved) == piece.Pawn and (
            self.endRow == 0 or self.endRow == 7))
        self.promotionChoice = piece.Queen
        self.isEnpassantMove = isEnpassantPossible
        if self.isEnpassantMove:
            self.pieceCaptured = piece.Pawn
            if self.pieceMoved == (piece.white | piece.Pawn):
                self.pieceCaptured = piece.black
            else:
                self.pieceCaptured = piece.white

        self.isCastleMove = isCastleMove

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
                    for _ in range(int(char)):
                        board_row.append(0)
                else:
                    board_row.append(self.getPiece(char))
            board.append(board_row)

        return board

    def getPiece(self, char, piece=Piece()):
        pieceColor = piece.white if char.isupper() else piece.black
        pieceType = self.pieceTypeFromSymbol[char.lower()]
        return pieceColor | pieceType


""" 
Counts all the material on the board and returns a dictionary with the material count for each piece
"""


class Material():
    def __init__(self):
        self.piece = Piece()
        self.pawnMaterial = {
            'white': 0,
            'black': 0
        }
        self.knightMaterial = {
            'white': 0,
            'black': 0
        }
        self.bishopMaterial = {
            'white': 0,
            'black': 0
        }
        self.rookMaterial = {
            'white': 0,
            'black': 0
        }
        self.queenMaterial = {
            'white': 0,
            'black': 0
        }
        self.kingMaterial = {
            'white': 0,
            'black': 0
        }

    def getPawnMaterial(self, gs):
        self.pawnMaterial['white'] = 0
        self.pawnMaterial['black'] = 0
        for row in range(len(gs.board)):
            for col in range(len(gs.board[row])):
                if col == 0:
                    continue
                if self.piece.getPieceType(gs.board[row][col]) == self.piece.Pawn:
                    if self.piece.getPieceColor(gs.board[row][col]) == self.piece.white:
                        self.pawnMaterial['white'] += 1
                        if self.pawnMaterial['white'] > 8:
                            self.pawnMaterial['white'] = 8
                    else:
                        self.pawnMaterial['black'] += 1
                        if self.pawnMaterial['black'] > 8:
                            self.pawnMaterial['black'] = 8

        return self.pawnMaterial

    def getKnightMaterial(self, gs):
        self.knightMaterial['white'] = 0
        self.knightMaterial['black'] = 0

        for row in range(len(gs.board)):
            for col in range(len(gs.board[row])):
                if gs.board[row][col] == 0:
                    continue
                if self.piece.getPieceType(gs.board[row][col]) == self.piece.Knight:
                    if self.piece.getPieceColor(gs.board[row][col]) == self.piece.white:
                        self.knightMaterial['white'] += 1
                        if self.knightMaterial['white'] > 2:
                            self.knightMaterial['white'] = 2
                    else:
                        self.knightMaterial['black'] += 1
                        if self.knightMaterial['black'] > 2:
                            self.knightMaterial['black'] = 2

        return self.knightMaterial

    def getBishopMaterial(self, gs):
        self.bishopMaterial['white'] = 0
        self.bishopMaterial['black'] = 0

        for row in range(len(gs.board)):
            for col in range(len(gs.board[row])):
                if gs.board[row][col] == 0:
                    continue
                if self.piece.getPieceType(gs.board[row][col]) == self.piece.Bishop:
                    if self.piece.getPieceColor(gs.board[row][col]) == self.piece.white:
                        self.bishopMaterial['white'] += 1
                        if self.bishopMaterial['white'] > 2:
                            self.bishopMaterial['white'] = 2
                    else:
                        self.bishopMaterial['black'] += 1
                        if self.bishopMaterial['black'] > 2:
                            self.bishopMaterial['black'] = 2

        return self.bishopMaterial

    def getRookMaterial(self, gs):
        self.rookMaterial['white'] = 0
        self.rookMaterial['black'] = 0

        for row in range(len(gs.board)):
            for col in range(len(gs.board[row])):
                if gs.board[row][col] == 0:
                    continue
                if self.piece.getPieceType(gs.board[row][col]) == self.piece.Rook:
                    if self.piece.getPieceColor(gs.board[row][col]) == self.piece.white:
                        self.rookMaterial['white'] += 1
                        if self.rookMaterial['white'] > 2:
                            self.rookMaterial['white'] = 2
                    else:
                        self.rookMaterial['black'] += 1
                        if self.rookMaterial['black'] > 2:
                            self.rookMaterial['black'] = 2

        return self.rookMaterial

    def getQueenMaterial(self, gs):
        self.queenMaterial['white'] = 0
        self.queenMaterial['black'] = 0
        for row in range(len(gs.board)):
            for col in range(len(gs.board[row])):
                if gs.board[row][col] == 0:
                    continue
                if self.piece.getPieceType(gs.board[row][col]) == self.piece.Queen:
                    if self.piece.getPieceColor(gs.board[row][col]) == self.piece.white:
                        self.queenMaterial['white'] += 1
                        if self.queenMaterial['white'] > 1:
                            self.queenMaterial['white'] = 1
                    else:
                        self.queenMaterial['black'] += 1
                        if self.queenMaterial['black'] > 1:
                            self.queenMaterial['black'] = 1

        return self.queenMaterial

    def getKingMaterial(self, gs):
        self.kingMaterial['white'] = 0
        self.kingMaterial['black'] = 0
        for row in range(len(gs.board)):
            for col in range(len(gs.board[row])):
                if gs.board[row][col] == 0:
                    continue
                if self.piece.getPieceType(gs.board[row][col]) == self.piece.King:
                    if self.piece.getPieceColor(gs.board[row][col]) == self.piece.white:
                        self.kingMaterial['white'] += 1
                        if self.kingMaterial['white'] > 1:
                            self.kingMaterial['white'] = 1
                    else:
                        self.kingMaterial['black'] += 1
                        if self.kingMaterial['black'] > 1:
                            self.kingMaterial['black'] = 1

        return self.kingMaterial
