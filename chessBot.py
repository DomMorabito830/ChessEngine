import random as r

pointsOfMaterial = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 5

#Random move finder.

def findRandomMove(validMoves):
    return validMoves[r.randint(0, len(validMoves) - 1)]

#Best move finder. Greedy Algorithm & MinMax Algorithm. NOT USED.

def findBestMoveOld(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    oppMinMaxScore = CHECKMATE
    bestPlayerMove = None
    r.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        oppMoves = gs.getValidMoves()
        if gs.stalemate:
                oppMaxScore = STALEMATE
        elif gs.checkmate:
            oppMaxScore = -CHECKMATE
        else:
            oppMaxScore = -CHECKMATE
            for oppMove in oppMoves:
                gs.makeMove(oppMove)
                gs.getValidMoves()
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)
                if score > oppMaxScore:
                    oppMaxScore = score
                gs.undoMove()
        if oppMaxScore < oppMinMaxScore:
            oppMinMaxScore = oppMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove

#Helper method for minMax(). Used to make first recursive call.

def findBestMove(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None
    r.shuffle(validMoves)
    negaMaxAB(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    returnQueue.put(nextMove)

#Recursive MinMax Algorithm.

def minMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = minMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = minMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore
    
#NegaMax Algorithm

def negaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -negaMax(gs, nextMoves, depth - 1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore

#NegaMax Algorithm + Alpha Beta Pruning.

def negaMaxAB(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -negaMaxAB(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha: #Pruning begins.
            alpha = maxScore
        if alpha >= beta:
            break #This is when we stop looking. We have already found that this score is impossible to beat.
    return maxScore

#Gives the current position a score in terms of material. NOT USED.

def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += pointsOfMaterial[square[1]]
            elif square[0] == "b":
                score -= pointsOfMaterial[square[1]]
    return score

#Scores the current position based on more factors than just material present on the board (King safety, Pins, Checks, Piece Activity...)

def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE #Black wins.
        else:
            return CHECKMATE #White wins.
    elif gs.stalemate:
        return STALEMATE #Neither side wins.
    
    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == "w":
                score += pointsOfMaterial[square[1]]
            elif square[0] == "b":
                score -= pointsOfMaterial[square[1]]
    return score