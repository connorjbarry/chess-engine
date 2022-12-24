""" 
This is the main file for the chess game.
"""

from ChessEngine import *
import pygame as pg


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
    0: None
}

""" 
Initializes a global dictionary of images. This will be called exactly once in the main. Can be edited to allow for different pieces.
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
    loadPieceImages()
    # keeps track of the last click of the user (tuple: (row, col))
    selectedSquare = ()
    # keeps track of the player clicks (two tuples: [(6,4), (4,4)])
    playerCLicks = []

    running = True

    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif e.type == pg.MOUSEBUTTONDOWN:
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

                if len(playerCLicks) == 2:  # after 2nd click
                    move = Move(playerCLicks[0], playerCLicks[1], gs.board)
                    print(move.getChessNotation())
                    gs.makeMove(move)
                    selectedSquare = ()  # reset user clicks
                    playerCLicks = []

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        pg.display.flip()


""" 
    Responsible for all the graphics within a current game state.
"""


def drawGameState(screen, gs):
    # Draws squares on board
    drawBoard(screen)
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

    TODO:
    - Change the gamestate.board to fen notation
"""


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            imageFromPiece = PIECESTOIMAGE[piece]
            if imageFromPiece != None:
                screen.blit(IMAGES[imageFromPiece], pg.Rect(
                    c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


if __name__ == "__main__":
    main()
