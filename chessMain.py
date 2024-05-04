# Handles user input and displays current GameState object.

import pygame as p
from pygame import mixer
import chessEngineSmart
import chessBot as c
from multiprocessing import Process, Queue

WIDTH = HEIGHT = 512
LOG_WIDTH = 256
LOG_HEIGHT = HEIGHT
DIMENSION = 8
SQ_SIZE = HEIGHT / DIMENSION
MAX_FPS = 15
PIECES = {}
LETTERS = {}
NUMBERS = {}

#Initialize a global directory of pieces, letter coordinates, and number coordinates as images. This will be called one time in the main.

def loadImages():
    pieces = ["wP", 'wN', "wB", "wR", "wQ", "wK", "bP", "bN", "bB", "bR", "bQ", "bK"]
    letters = ["-a", "-b", "-c", "-d", "-e", "-f", "-g", "-h"]
    numbers = ["8-", "7-", "6-", "5-", "4-", "3-", "2-", "1-"]

    for piece in pieces:
        PIECES[piece] = p.transform.scale(p.image.load("Chess/pieces/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    for letter in letters:
        LETTERS[letter] = p.transform.scale(p.image.load("Chess/letterCoordinates/" + letter + ".png"), (SQ_SIZE, SQ_SIZE))
    for number in numbers:
        NUMBERS[number] = p.transform.scale(p.image.load("Chess/numberCoordinates/" + number + ".png"), (SQ_SIZE, SQ_SIZE))

#Accesses an image by calling 'PIECES['wQ']', 'LETTERS['a']', 'NUMBERS['1']' etc.

#This is the main driver, will handle user input and updating graphics.

def main():
    p.init()
    mixer.init()
    mixer.music.load("Chess/sounds/game-start.mp3")
    mixer.music.play()
    screen = p.display.set_mode((WIDTH + LOG_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("#FFFFFF"))
    logFont = p.font.SysFont("Segoe_UI", 16, True, False)
    gs = chessEngineSmart.gameState()
    validMoves = gs.getValidMoves()
    moveMade = False #Flag variable for when a move is made.
    animate = False #Flag variable for when a move is animated.
    loadImages()
    running = True
    sqSelected = () #No square is initially selected and will keep track of the last click of the user (tuple).
    playerClicks = [] #Keep track of player clicks (two tuples).
    gameOver = False #Flag variable for when either Checkmate, Stalemate, or a Resignation occurs.
    playerOne = True #If a human is playing White, then this will be true. If an AI is playing White, then false.
    playerTwo = False #If a human is playing Black, then this will be true. If an AI is playing Black, then false.
    AIThinking = False #True whenever AI is coming up with a move, false otherwise.
    moveFinderProcess = None
    moveUndone = False

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #Mouse handler.
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() #(x, y) position of mouse.
                    col = int(location[0] / SQ_SIZE)
                    row = int(location[1] / SQ_SIZE)
                    if sqSelected == (row, col) or col >= 8: #User clicked same square twice or user clicked the move log.
                        sqSelected = () #Deselect.
                        playerClicks = [] #Clear player's clicks.
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2 and humanTurn:          
                        move = chessEngineSmart.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = () #Reset user clicks.
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            #Event handlers.
            elif e.type == p.KEYDOWN:               
                if e.key == p.K_u: #Undo last made move when the "u" key is pressed.
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r: #Resets the board when the "r" key is pressed.
                    gs = chessEngineSmart.gameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                    mixer.music.load("Chess/sounds/game-start.mp3")
                    mixer.music.play()

        #AI move finder logic.

        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue() #Used to pass data between threads.
                moveFinderProcess = Process(target = c.findBestMove, args = (gs, validMoves, returnQueue))
                moveFinderProcess.start() #Calls the function with these parameters.

            if not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = c.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False

        if moveMade:
            if gs.isCheck():
                sound = p.mixer.Sound("Chess/sounds/move-check.mp3")
                p.mixer.Sound.play(sound)
            elif gs.moveIsCastle:
                sound = p.mixer.Sound("Chess/sounds/castle.mp3")
                p.mixer.Sound.play(sound)
            elif gs.moveIsCapture:
                sound = p.mixer.Sound("Chess/sounds/capture.mp3")
                p.mixer.Sound.play(sound)    
            elif moveUndone:
                sound = p.mixer.Sound("Chess/sounds/move-self.mp3")
                p.mixer.Sound.play(sound)
            else:
                sound = p.mixer.Sound("Chess/sounds/move-self.mp3")
                p.mixer.Sound.play(sound)
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock, gs.numberCoordinates, gs.letterCoordinates)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, sqSelected, logFont)
        #Checks if game is over.
        soundPlayed = False
        if gs.checkmate:
            while not soundPlayed:
                sound = p.mixer.Sound("Chess/sounds/game-end.mp3")
                p.mixer.Sound.play(sound)
                soundPlayed = True
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black Won! By Checkmate.')
            else:
                drawText(screen, 'White Won! By Checkmate.')
        elif gs.stalemate:
            while not soundPlayed:
                sound = p.mixer.Sound("Chess/sounds/game-end.mp3")
                p.mixer.Sound.play(sound)
                soundPlayed = True
            gameOver = True
            drawText(screen, 'Stalemate.')

        clock.tick(MAX_FPS)
        p.display.flip()

#Highlights square selected, draws dots on squares with valid moves

def highlightSquares(screen, gs, sqSelected):
    if sqSelected != ():
        row, col = sqSelected
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'): #Makes sure square selected is a piece that can be moved
            state = p.mouse.get_pressed()
            if state[2]: #Will handle right-clicks
                s = p.Surface((SQ_SIZE, SQ_SIZE))
                rightClickColor = [p.Color("#DE846F"), p.Color("#C87358")]
                s.fill(rightClickColor[(row + col) % 2])
                screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))
            if state[0]: #Will handle left-clicks
                t = p.Surface((SQ_SIZE, SQ_SIZE))
                leftClickColor = [p.Color("#F5F598"), p.Color("#BFCB5F")]
                t.fill(leftClickColor[(row + col) % 2])
                screen.blit(t, (col * SQ_SIZE, row * SQ_SIZE))

#Draw dots on squares with valid moves

def drawDots(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        row, col = sqSelected
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'): #Makes sure square selected is a piece that can be moved
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    if gs.board[move.endRow][move.endCol] == "--": #Empty Squares
                        u = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                        p.draw.circle(u, p.Color(0, 0, 0, 128), (0, 0), 10)
                        screen.blit(u, ((move.endCol * SQ_SIZE + SQ_SIZE // 2, move.endRow * SQ_SIZE + SQ_SIZE // 2)))
                    else: #Squares with another piece
                        v = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                        p.draw.circle(v, (0, 0, 0, 128), (0, 0), 30)
                        screen.blit(v, ((move.endCol * SQ_SIZE + SQ_SIZE // 2, move.endRow * SQ_SIZE + SQ_SIZE // 2)))

#Responsible for all graphics within current game state

def drawGameState(screen, gs, validMoves, sqSelected, logFont):
    drawBoard(screen) #Draws squares
    drawLetters(screen, gs.letterCoordinates)
    drawNumbers(screen, gs.numberCoordinates)
    drawLog(screen, gs, logFont)
    highlightSquares(screen, gs, sqSelected)
    drawPieces(screen, gs.board)
    drawDots(screen, gs, validMoves, sqSelected)

#Draws the squares on the board. Top-left squares is ALWAYS LIGHT. Also keeps track of which squares are light and dark.

def drawBoard(screen):
    global colors
    colors = [p.Color("#eeeed2"), p.Color("#769656")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


#Draws the pieces.

def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(PIECES[piece], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

#Draws the letters in the top right corner of the first column of squares.

def drawLetters(screen, letterCoordinates):
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                letter = letterCoordinates[row][col]
                if letter != "--":
                    screen.blit(LETTERS[letter], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

#Draws the numbers in the bottom right corner of the bottom row of squares.

def drawNumbers(screen, numberCoordinates):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            number = numberCoordinates[row][col]
            if number != "--":
                screen.blit(NUMBERS[number], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

#Draws the move log on the side of the board.

def drawLog(screen, gs, font):

    moveLogRect = p.Rect(WIDTH, 0, LOG_WIDTH, LOG_HEIGHT)
    p.draw.rect(screen, p.Color("#302E2B"), moveLogRect)
    moveLog = gs.moveLog
    moveText = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog): #Make sure Black made a move.
            moveString += str(moveLog[i + 1])
        moveText.append(moveString)
    movesPerRow = 3
    padding = 5
    spacing = 2
    textY = padding
    for i in range(0, len(moveText), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveText):
                text += moveText[i + j]
        textObject = font.render(text, True, p.Color("#FFFFFF"))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + spacing

#Animation of moves.

def animateMove(move, screen, board, clock, numberCoordinates, letterCoordinates):
    global colors
    dR = move.endRow - move.startRow #Delta move row (Change in row)
    dC = move.endCol - move.startCol #Delta move column (Change in column)
    fps = 3 #FramesPerSquare
    frameCount = (abs(dR) + abs(dC)) * fps
    for frame in range(frameCount + 1):
        row, col = ((move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount))
        drawBoard(screen)
        drawPieces(screen, board)
        drawNumbers(screen, numberCoordinates)
        drawLetters(screen, letterCoordinates)
        #Erase the piece moved from its ending square.
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #Draw captured piece back onto square.
        if move.pieceCaptured != '--':
            screen.blit(PIECES[move.pieceCaptured], endSquare)
        #Draw the moving piece.
        screen.blit(PIECES[move.pieceMoved], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont('Segoe_UI', 32, True, False)
    textObject = font.render(text, 0, p.Color("#9B9B9B"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)

if __name__ == "__main__":
    main()


#IDEAS: Move highlight for last move made, a UI for when the game concludes, stalemate on repeated moves