# Stores all information about the current state of the chess game. Also will be responsible for determining valid moves at current GameState, and will keep a log of all played moves.

class gameState():

    def __init__(self):

        #Board is 8x8 2D List, each element of the list has 2 Characters
        #First character represents color of piece (Black "b", or White "w")
        #Second piece represents type of piece (King "K", Queen "Q", Rook "R", Bishop "B", Knight "N", or Pawn "P")
        #"--" represents an empty space on the board

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]

        self.numberCoordinates = [
            ["8-", "--", "--", "--", "--", "--", "--", "--"],
            ["7-", "--", "--", "--", "--", "--", "--", "--"],
            ["6-", "--", "--", "--", "--", "--", "--", "--"],
            ["5-", "--", "--", "--", "--", "--", "--", "--"],
            ["4-", "--", "--", "--", "--", "--", "--", "--"],
            ["3-", "--", "--", "--", "--", "--", "--", "--"],
            ["2-", "--", "--", "--", "--", "--", "--", "--"],
            ["1-", "--", "--", "--", "--", "--", "--", "--"],
        ]

        self.letterCoordinates = [
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["-a", "-b", "-c", "-d", "-e", "-f", "-g", "-h"],
        ]

        self.moveFunctions = {
            'P': self.getPawnMoves,
            'N': self.getKnightMoves,
            'B': self.getBishopMoves,
            'R': self.getRookMoves,
            'Q': self.getQueenMoves,
            'K': self.getKingMoves
        }

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.moveIsCastle = False
        self.moveIsCapture = False
        self.enPassantPossible = () #Square where En Passant capture can occur
        self.enPassantPossibleLog = [self.enPassantPossible]
        self.currentCastlingRights = castleRights(True, True, True, True)
        self.castleRightsLog = [castleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, 
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

    #Takes a move as a parameter and executes accordingly, does not work for En Passant/Castle/Pawn Promotion

    def makeMove(self, move):
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.board[move.startRow][move.startCol] = "--"
        self.moveLog.append(move) #Log move to the move log
        self.whiteToMove = not self.whiteToMove #Switch turns between Black & White
        if move.pieceMoved == 'wK': #Updates King's position
            self.whiteKingLocation == (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation == (move.endRow, move.endCol)

        #En Passant, Pawn Promotion, & Castling

        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.endRow + move.startRow) / 2, move.endCol)
        else:
            self.enPassantPossible = ()
        if move.enPassant:
            self.board[move.startRow][move.endCol] = "--"
        if move.pawnPromotion:
            #print("Pawn promotion!") #FOR DEBUGGING
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"
        if move.castleMove:
            if move.endCol - move.startCol == 2: #Kingside Castle move.
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1] #Moves Rook to new Square.
                self.board[move.endRow][move.endCol + 1] = "--" #Erases Rook from old Square.
            else: #Queenside Castle move.
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2] #Moves Rook to new Square.
                self.board[move.endRow][move.endCol - 2] = "--" #Erases Rook from old Square.
            self.moveIsCastle = True
        else:
            self.moveIsCastle = False

        self.enPassantPossibleLog.append(self.enPassantPossible)
        self.updateCastleRights(move)
        self.castleRightsLog.append(castleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, 
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))
        if move.pieceCaptured != "--":
            self.moveIsCapture = True
        else:
            self.moveIsCapture = False

    #Undo last move

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == 'wK': #Reverts King's position
                self.whiteKingLocation == (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation == (move.startRow, move.startCol)
            
            #En Passant.

            if move.enPassant:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]
            
            #Castling.

            self.castleRightsLog.pop() #Remove the new Castle rights from the move we are undoing.
            self.currentCastlingRights = self.castleRightsLog[-1] #Set the current Castle rights to the last one in the list.
            if move.castleMove:
                if move.endCol - move.startCol == 2: #Kingside Castle move.
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else: #Queenside Castle move.
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"
                    
            self.checkmate = False #Undoes a Checkmate.
            self.stalemate = False #Undoes a Stalemate.

    #Updates Castling rights.

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: #Left Rook.
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7: #Right Rook.
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: #Left Rook.
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7: #Right Rook.
                    self.currentCastlingRights.bks = False
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False

    #Gets all moves considering Checks

    def getValidMoves(self):
        tempCastleRights = castleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, 
                                        self.currentCastlingRights.wqs, self.currentCastlingRights.bqs) #Copies the current Castling rights.
        moves = []
        self.inCheck, self.pins, self.checks = self.pinsOrChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: #Only one piece is attacking King, King is able to move
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) #Variables "check[2]" & "check[3]" are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves) - 1, -1, -1): #Removes illegal moves traversing the list in reverse
                    if moves[i].pieceMoved[1] != 'K': #Must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: #Move does not address the Check
                            moves.remove(moves[i])
            else: #If the king is being attacked by 2 different pieces simoultaneously, the King must move
                self.getKingMoves(kingRow, kingCol, moves)
        else: #King is not in check, all moves are legal
            moves = self.getAllPossibleMoves()
            if self.whiteToMove:
                self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        self.currentCastlingRights = tempCastleRights
        return moves

    #Determine if current player is in Check. Important for sound effects.

    def isCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    
    #Determine if the enemy can attack the square (row, col).

    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove #Switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove #Switch back to current player's turn
        for move in oppMoves:
            if move.endRow == row and move.endCol == col: #Is square under attack?
                return True
        return False

    # Gets all moves without considering Checks

    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves) #Calls the appropriate move function based on piece type
        return moves

    #Gets all legal moves for each individual type of piece

    def getPawnMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if self.whiteToMove == True:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor = 'b'
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'
            kingRow, kingCol = self.blackKingLocation
        pawnPromotion = False

        if self.board[row + moveAmount][col] == '--': #1-Square Pawn advance
            if not piecePinned or pinDirection == (moveAmount, 0):
                if row + moveAmount == backRow: #If the Pawn gets to the back rank, there is a Pawn Promotion
                    pawnPromotion = True
                moves.append(Move((row, col), (row + moveAmount, col), self.board, pawnPromotion = pawnPromotion))
                if row == startRow and self.board[row + 2 * moveAmount][col] == '--': #2-Square Pawn advance
                    moves.append(Move((row, col), (row + 2 * moveAmount, col), self.board))
        if col - 1 >= 0: #Makes sure pawn cannot capture across the board (Left Capture)
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[row + moveAmount][col - 1][0] == enemyColor:
                    if row + moveAmount == backRow: #If the Pawn gets to the back rank, there is a Pawn Promotion
                        pawnPromotion = True
                    moves.append(Move((row, col), (row + moveAmount, col - 1), self.board, pawnPromotion = pawnPromotion))
                if (row + moveAmount, col - 1) == self.enPassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingCol < col: #King is to the left of the Pawn.
                            insideRange = range(kingCol + 1, col - 1)
                            outsideRange = range(col + 1, 8)
                        else:
                            insideRange = range(kingCol - 1, col, -1)
                            outsideRange = range(col - 2, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != "--": #There is another piece besides the en-passant pawns blocking.
                                blockingPiece = True
                        for j in outsideRange:
                            square = self.board[row][j]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row, col), (row + moveAmount, col - 1), self.board, enPassant = True))
        if col + 1 <= 7: #Makes sure pawn cannot capture across the board (Right Capture)
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[row + moveAmount][col + 1][0] == enemyColor:
                    if row + moveAmount == backRow: #If the Pawn gets to the back rank, there is a Pawn Promotion
                        pawnPromotion = True
                    moves.append(Move((row, col), (row + moveAmount, col + 1), self.board, pawnPromotion = pawnPromotion))
                if (row + moveAmount, col + 1) == self.enPassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingCol < col: #King is to the left of the Pawn.
                            insideRange = range(kingCol + 1, col)
                            outsideRange = range(col + 2, 8)
                        else:
                            insideRange = range(kingCol - 1, col + 1, -1)
                            outsideRange = range(col - 1, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != "--": #There is another piece besides the en-passant pawns blocking.
                                blockingPiece = True
                        for j in outsideRange:
                            square = self.board[row][j]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row, col), (row + moveAmount, col + 1), self.board, enPassant = True))

    def getRookMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q': #You cannot unpin a Queen with a Rook move, only a Bishop move can accomplish that
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #Up, Left, Down, Right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #Makes sure piece is still on the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--': #Is the space the Rook is moving to empty?
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: #Does the space the Rook is moving to have an enemy piece on it?
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else: #Friendly Piece
                            break
                else: #Off Board
                    break

    def getBishopMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) #4 Diagonals
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #Makes sure piece is still on the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--': #Is the space the Bishop is moving to empty?
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: #Does the space the Bishop is moving to have an enemy piece on it?
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else: #Friendly Piece
                            break
                else: #Off Board
                    break

    def getKnightMoves(self, row, col, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)) #All 8 different possible Knight moves
        allyColor = "w" if self.whiteToMove else "b"
        for d in directions:
            endRow = row + d[0]
            endCol = col + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: #Makes sure piece is still on the board
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor: #Is the square the Knight is moving to empty/have an enemy piece on it?
                        moves.append(Move((row, col), (endRow, endCol), self.board))

    def getQueenMoves(self, row, col, moves):
        self.getBishopMoves(row, col, moves)
        self.getRookMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = row + rowMoves[i]
            endCol = col + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: #Not an ally piece, could also be an empty square
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.pinsOrChecks()
                    if not inCheck:
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    if allyColor == 'w': #Place the King back into its original position
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)

    #Generates all valid Castling moves for the king at (row, col) and adds them to the list of valid moves

    def getCastleMoves(self, row, col, moves):
        if self.squareUnderAttack(row, col):
            return #Cannot Castle while in Check.
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingSideCastleMoves(row, col, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(row, col, moves)
        
    def getKingSideCastleMoves(self, row, col, moves):
        if self.board[row][col + 1] == "--" and self.board[row][col + 2] == "--":
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, castleMove = True))

    def getQueenSideCastleMoves(self, row, col, moves):
        if self.board[row][col - 1] == "--" and self.board[row][col - 2] == "--" and self.board[row][col - 3] == "--"  and \
        not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, castleMove = True))

    #Returns if the player is in Check, a list of possible Pins, and a list of possible Checks
    
    def pinsOrChecks(self):
        pins = [] #Squares that contain allied pinned pieces
        checks = [] #Squares where enemy pieces are putting King in Check
        inCheck = False
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)) #First 4 are for Rook, last 4 are for Bishop. Also covers all 8 Queen diretions.
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () #Reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == (): #Checks if a pin is not on the board
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: #There are 2 allied pieces between the King and the attacking piece, no pin is present on the board
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]

                        #Checks all possible Checks & Pins for all pieces except the Knight, if a Knight checks a King the King must move because the Knight disregards pins as it can jump over pieces
                        #1) Piece is Rook and is Orthogonally away from King
                        #2) Piece is a Bishop and is Diagonally away from King
                        #3) Piece is a Pawn and is Diagonally 1 square away from King, must also check which direction the Pawn is attacking. Pawn is the only piece that cannot attack/move backwards
                        #4) Piece is a Queen and is either Orthogonally or Diagonally away from King
                        #5) Piece is a King and is either Orthogonally or Diagonally away from King

                        if (0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'P' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                            (type == 'Q') or \
                            (i == 1 and type == 'K'):
                            if possiblePin == (): #No pin is present, King is in Check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: #Pin is present, King is not in Check
                                pins.append(possiblePin)
                                break
                        else: #There is an enemy piece between the King and attacking piece that is not putting the King in check, none of the above conditions are present on the board
                            break
                else:
                    break #Piece is off the board

        #Conditions for Knight Checks

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for k in knightMoves:
            endRow = startRow + k[0]
            endCol = startCol + k[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: #Piece is on the board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N': #Knight is attacking King
                    inCheck = True
                    checks.append((endRow, endCol, k[0], k[1]))
        #print(inCheck) VERY IMPORTANT FOR DEBUGGING
        return inCheck, pins, checks

class castleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():

    #Maps keys to values (key : value)

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enPassant = False, pawnPromotion = False, castleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.enPassant = enPassant
        self.pawnPromotion = pawnPromotion
        self.castleMove = castleMove
        self.isCapture = self.pieceCaptured != "--"

        if enPassant:
            self.pieceCaptured = 'bP' if self.pieceMoved == 'wP' else 'wP' #En Passant captures pawn of opposite color


        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    #Overrides equals method

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        if self.pawnPromotion:
            return self.getRankFile(self.endRow, self.endCol) + "Q"
        if self.castleMove:
            if self.end_col == 1:
                return "0-0-0"
            else:
                return "0-0"
        if self.enPassant:
            return self.getRankFile(self.startRow, self.startCol)[0] + "x" + self.getRankFile(self.endRow, self.endCol) + " e.p."
        if self.pieceCaptured != "--":
            if self.pieceMoved[1] == "P":
                return self.getRankFile(self.startRow, self.startCol)[0] + "x" + self.getRankFile(self.endRow, self.endCol)
            else:
                return self.pieceMoved[1] + "x" + self.getRankFile(self.endRow, self.endCol)
        else:
            if self.pieceMoved[1] == "P":
                return self.getRankFile(self.endRow, self.endCol)
            else:
                return self.pieceMoved[1] + self.getRankFile(self.endRow, self.endCol)


    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]
    
    #Overriding the str() function
    
    def __str__(self):
        if self.castleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"
        
        endSq = self.getRankFile(self.endRow, self.endCol)
        if self.pieceMoved == 'P':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSq
            else:
                return endSq + "Q" if self.pawnPromotion else endSq
            
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSq
        