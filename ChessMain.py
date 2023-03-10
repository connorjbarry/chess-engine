""" 
This is the main file for the chess game.
"""

from ChessEngine import *
from ChessAI import *
import pygame as pg
import time


# --- Global Variables ---
piece = Piece()
WIDTH = 512
HEIGHT = 512
DIMENSION = 8  # Can potentially allow for the board size to be changed
SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # For animations later on
IMAGES = {}
PIECESTOIMAGE = {
    piece.black | piece.Rook: "bR",
    piece.black | piece.Knight: "bN",
    piece.black | piece.Bishop: "bB",
    piece.black | piece.Queen: "bQ",
    piece.black | piece.King: "bK",
    piece.black | piece.Pawn: "bP",
    piece.white | piece.Rook: "wR",
    piece.white | piece.Knight: "wN",
    piece.white | piece.Bishop: "wB",
    piece.white | piece.Queen: "wQ",
    piece.white | piece.King: "wK",
    piece.white | piece.Pawn: "wP",
    piece.Non: None
}

""" 
Initializes a global dictionary of images. This will be called exactly once in the main

TODO:
    ADD DIFFERENT PIECE SETS
"""


def loadPieceImages():
    for piece in PIECESTOIMAGE.values():
        if piece == None:
            continue
        IMAGES[piece] = pg.transform.scale(pg.image.load(
            "images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


""" 
The main driver for our code. This will handle user input and updating the graphics.
"""


def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Chess")
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))
    fen = Fen()
    gs = GameState(fen)
    ai = AI(gs)
    validMoves = gs.getLegalMoves()
    moveMade = False  # Flag variable for when a move is made
    loadPieceImages()
    # keeps track of the last click of the user (tuple: (row, col))
    selectedSquare = ()
    # keeps track of the player clicks (two tuples: [(6,4), (4,4)])
    playerCLicks = []

    running = True
    gameOver = False
    useTestBench = False


    playingWhite = True   # if a human is playing white

    playingBlack = True  # if a human is playing black

    while running:
        playersTurn = (gs.whiteToMove and playingWhite) or (
            not gs.whiteToMove and playingBlack)
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            # mouse handler
            elif e.type == pg.MOUSEBUTTONDOWN:

                if not gameOver and playersTurn:

                    location = pg.mouse.get_pos()  # gets (x,y) location of mouse
                    # gets row and column of mouse click (0-7) by floor dividing by square size
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE

                    # user clicked the same square twice
                    if selectedSquare == (row, col):
                        selectedSquare = ()  # deselect
                        playerCLicks = []  # clear player clicks
                    else:
                        selectedSquare = (row, col)
                        playerCLicks.append(selectedSquare)

                    # Checks if the user selected an empty square on first click and resets the user clicks
                    if (len(playerCLicks) == 1) and (gs.board[row][col] == 0):
                        selectedSquare = ()  # deselect
                        playerCLicks = []

                    # check if user is selecting another piece of same color
                    if (len(playerCLicks) > 1):
                        # gets the color of the first piece selected
                        firstPieceColor = piece.getPieceColor(
                            gs.board[playerCLicks[0][0]][playerCLicks[0][1]])

                        # gets the color of the second piece selected
                        secondPieceColor = piece.getPieceColor(
                            gs.board[playerCLicks[1][0]][playerCLicks[1][1]])
                        # if the user selects a piece of the same color, it will deselect the first piece and select the new piece
                        if firstPieceColor == secondPieceColor:
                            selectedSquare = playerCLicks[1]
                            playerCLicks = [selectedSquare]

                    if len(playerCLicks) == 2:  # after 2nd click
                        move = Move(playerCLicks[0], playerCLicks[1], gs.board)
                        # prints the move in chess notation
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                print(move.getChessNotation())
                                if validMoves[i].pawnPromotion:
                                    gs.board[validMoves[i].endRow][validMoves[i].endCol] = \
                                        piece.getPieceColor(
                                        gs.board[validMoves[i].endRow][validMoves[i].endCol]) | \
                                        validMoves[i].promotionChoice
                                moveMade = True
                            selectedSquare = ()  # reset user clicks
                            playerCLicks = []

            # key handler
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_z:
                    gs.undoMove()
                    moveMade = True
                if e.key == pg.K_r:
                    gs = GameState(fen)
                    validMoves = gs.getLegalMoves()
                    selectedSquare = ()
                    playerCLicks = []
                    moveMade = False
                    gameOver = False

        # AI move finder
        if not gameOver and not playersTurn:

            AIMove = ai.findBestMove(gs, validMoves)
            if AIMove == None:
                AIMove = ai.findRandomMove(validMoves)
                print("AI move was random")
            for i in range(len(validMoves)):
                if AIMove == validMoves[i]:
                    gs.makeMove(validMoves[i])
                    print(AIMove.getChessNotation())
                    if validMoves[i].pawnPromotion:
                        gs.board[validMoves[i].endRow][validMoves[i].endCol] = \
                            piece.getPieceColor(
                            gs.board[validMoves[i].endRow][validMoves[i].endCol]) | \
                            validMoves[i].promotionChoice
            moveMade = True
            time.sleep(1)

        if moveMade:
            validMoves = gs.getLegalMoves()
            moveMade = False

        drawGameState(screen, gs, validMoves, selectedSquare)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                print("Black wins by checkmate")
            else:
                print("White wins by checkmate")
        elif gs.stalemate:
            gameOver = True
            print("Stalemate")

        clock.tick(MAX_FPS)
        pg.display.flip()

    if useTestBench:
        testBench(ai, 3)


""" 
    Responsible for all the graphics within a current game state.
"""


def drawGameState(screen, gs, validMoves, selectedSquare):
    # Draws squares on board
    drawBoard(screen)
    # Highlights selected square and highlights moves from that square
    highlightSquares(screen, gs, validMoves, selectedSquare)
    # Draws pieces on top of squares from gamestate
    drawPieces(screen, gs.board)


""" 
    Draws the squares on the board.  Handles the colors of the squares, if wanted to change.
"""


def drawBoard(screen):
    colors = [pg.Color("white"), pg.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            pg.draw.rect(screen, color, pg.Rect(
                c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


"""
    Draws the pieces on the board using the current GameState.board  
"""


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            imageFromPiece = PIECESTOIMAGE[piece]
            if imageFromPiece != None:
                screen.blit(IMAGES[imageFromPiece], pg.Rect(
                    c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def highlightSquares(screen, gs, validMoves, selectedSquare):
    if selectedSquare != ():
        r, c = selectedSquare
        if piece.getPieceColor(gs.board[r][c]) == (piece.white if gs.whiteToMove else piece.black):
            # highlight selected square
            s = pg.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)
            s.fill(pg.Color('blue'))
            screen.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))
            # highlight moves from that square
            s.set_alpha(75)
            s.fill(pg.Color('red'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQUARE_SIZE,
                                    move.endRow * SQUARE_SIZE))


def testBench(ai, depth):
    for i in range(0, depth+1):
        numPositions = 0
        start = time.time()
        numPositions += ai.testMoveGeneration(depth=i)
        end = time.time()
        print(
            f'At depth {i}, there are {numPositions} positions\n TIME: {end-start:.2f} seconds\n')


if __name__ == "__main__":
    main()
