import math
import stockfish
import random
import chess
import time
from operator import itemgetter
import pygame as p
# import numpy
import MCTS

board = chess.Board()
screenSize = 512
WIDHT = HEIGHT = screenSize
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
path = "openingBook.txt"
openingbook = []

with open(path, "r") as file:
    for line in file:
        tempLine = line.split(" ")
        openingbook.append(tempLine)

class game:
    def __init__(self, ID):
        self.ID = ID
        self.moveTracker = 0
        self.OGplayer = None
        self.iterativeMinimax = True
        self.starting = True
        self.miniMaxOGgoing = True
        self.minimaxGameOver = False
        self.minimxDraw = False
        self.board = None
        self.stockFishmove = None
        self.selfMove = None
        self.moveCatalog = []
        self.whiteToMove = True
        self.stockfishy = stockfish.Stockfish(
        path=r"C:\Users\Bob Steeg\Documents\stockfish_14.1_win_x64_avx2/stockfish_14.1_win_x64_avx2", depth=2, parameters={"Threads": 4, "Minimum Thinking Time": 30})
        self.stockfishy2 = stockfish.Stockfish(
            path=r"C:\Users\Bob Steeg\Documents\stockfish_14.1_win_x64_avx2/stockfish_14.1_win_x64_avx2", depth=18,
            parameters={"Threads": 4, "Minimum Thinking Time": 30})
        self.gameOver = False
        self.whiteWin = True

    def startGame(self):
        self.board = board
        self.starting = False

    def getFen(self):
        return self.board.fen()

    def getBoard(self):
        return self.board

    def getStockFishMove(self):
        fenn = self.getFen()
        self.stockfishy2.set_fen_position(fenn)
        test = self.stockfishy2.get_best_move()
        return test

    def makeMove(self, move):
        self.board.push_san(move)
        self.moveTracker += 1
        self.moveCatalog.append(move)
        self.whiteToMove = not self.whiteToMove

    def makeMoveUCI(self, move):
        tempmove = self.board.san(move)
        self.board.push(move)
        self.moveCatalog.append(tempmove)
        self.moveTracker +=1
        self.whiteToMove = not self.whiteToMove
        self.updateGameOver()

    def undoMove(self):
        self.board.pop()
        self.moveTracker -= 1
        self.moveCatalog.pop()
        if self.gameOver:
            self.gameOver = False
        self.whiteToMove = not self.whiteToMove

    def updateGameOver(self):
        self.winChecker = self.CheckGameOver()
        self.draw = self.checkDraw()
        print("test2")
        self.checkWinColor()
        if self.draw or self.winChecker == True:
            self.gameOver = True


    def checkWinColor(self):
        print("test3")
        boardfen = self.board.fen
        boardfen = str(boardfen)
        boardfen = boardfen.split(" ")
        if boardfen[1] == "b":
            self.whiteWin = True
            print("chekcing white win")
        elif boardfen[1] == "w":
            self.whiteWin = False
            print("checking black win")

    def showBoard(self):
        print(self.ID)
        print(self.board)

    def getUserMove(self):
        legalMoves = self.getLegalMoves()
        print(legalMoves)
        mover = input("Indicate your movement: ")
        self.verifyMove(mover, legalMoves)
        return mover

    def verifyMove(self, move, legalMoves):

        if move in legalMoves:
            return move
        else:
            print(move)
            print("This is not a valid move.")
            print(legalMoves)
            move = input("Another move: ")
            self.verifyMove(move, legalMoves)

    def getRandomMove(self):
        legalMoves = self.getLegalMoves()
        leng = int(len(legalMoves)-1)
        randomm = random.randint(0, leng)
        return legalMoves[randomm]

    def getLegalMoves(self):
        legalMoves = str(self.board.legal_moves)
        legalMoves = legalMoves.split("(")
        legalMoves = legalMoves[1].split(")")
        legalMoves = legalMoves[0].split(", ")
        return legalMoves

    def getLegalMovesUCI(self):
        return list(self.board.legal_moves)

    def CheckGameOver(self):
        return self.board.is_checkmate()

    def checkDraw(self):
        threefold = board.can_claim_threefold_repetition()
        fiftymoves = board.can_claim_fifty_moves()
        draw = board.can_claim_draw()
        seventyfive = board.is_seventyfive_moves()
        stalemate = board.is_stalemate()
        material = board.is_insufficient_material()
        if threefold or fiftymoves or draw or seventyfive or stalemate or material:
            return True
        else:
            return False

    def getMovesAdvanced(self):
        possibleMoves = []
        if self.moveTracker < 7:
            for i in openingbook:
                if self.moveTracker == 0:
                    mover = i[self.moveTracker]
                    if mover not in possibleMoves:
                        possibleMoves.append(mover)
                elif self.moveTracker != 0:
                    lastMove = self.moveCatalog[self.moveTracker - 1]
                    if i[self.moveTracker - 1] == lastMove:
                        mover = i[self.moveTracker]
                        legalMoves = self.getLegalMoves()
                        if mover in legalMoves:
                            if mover not in possibleMoves:
                                possibleMoves.append(mover)
            if len(possibleMoves) == 0:
                possibleMoves = self.getLegalMoves()
        else:
            possibleMoves = self.getLegalMoves()
        return possibleMoves


    def analyseBoard(self):
        fen = self.getFen()
        self.stockfishy2.set_fen_position(fen)
        self.stockfishy.set_fen_position(fen)
        val1 = self.stockfishy2.get_evaluation()
        val2 = self.stockfishy.get_evaluation()
        print("Stockfish depth 18 analysis: ", val1, "Stockfish depth 2 analysis", val2)

    def findBestMove(self):
        self.startTime = time.time()
        self.moveTime = 10
        fen = self.getFen()
        fen = fen.split(" ")
        if fen[1] == 'b':
            self.OGplayer = "b"
        elif fen[1] == "w":
            self.OGplayer = "w"
        moves = self.getLegalMoves()
        ri = random.randint(0, len(moves) - 1)
        bestMove = moves[ri]
        bestScore = -math.inf
        previousMoves = []
        startMoves = []
        for depth in range(100):
            if depth == 1:
                startMoves = self.getMovesAdvanced()
            else:
                startMoves = previousMoves
            self.iterativeMinimax = True
            move, score, allMoves = self.Minimax(depth, depth, True, math.inf, -math.inf, startMoves)
            if move:
                allMoves.sort(key=itemgetter(1),reverse=True)
                previousMoves = allMoves
                bestScore, bestMove = score, move
                print(bestMove, depth)
        return bestMove, bestScore

    def Minimax(self, depth, OGDepth, maxPlayer, alpha, beta, startMoves):
        if time.time() - self.startTime > self.moveTime and depth == OGDepth and self.iterativeMinimax:
            return None, None, None
        if depth == OGDepth:
            self.miniMaxOGgoing = self.whiteToMove
        self.minimxDraw = self.checkDraw()
        self.minimaxGameOver = self.CheckGameOver()
        if depth == 0:
            fen = self.getFen()
            self.stockfishy.set_fen_position(fen)
            score = self.stockfishy.get_evaluation()
            score = score["value"]
            if self.OGplayer == "b":
                score = -score
            return None, score, None
        elif self.board.is_game_over():
            score = 0
            if (self.OGplayer == "w" and self.board.result() == "1-0") or (self.OGplayer == "b" and self.board.result() == "0-1"):
                score = math.inf
            elif (self.OGplayer == "b" and self.board.result() == "1-0") or (self.OGplayer == "w" and self.board.result() == "0-1"):
                score = -math.inf
            else:
                score = 4200
            return None, score, None
        allmoves = []
        if not depth == OGDepth or OGDepth == 1 or not self.iterativeMinimax:
            moves = self.getMovesAdvanced()
            ri = random.randint(0, len(moves)-1)
            bestMove = moves[ri]
        else:
            movestemp = startMoves
            moves = []
            for tempmove in movestemp:
                moves.append(tempmove[0])
            bestMove = moves[0]

        if maxPlayer:
            maxEval = -math.inf
            for move in moves:
                self.makeMove(move)
                currentEval = self.Minimax(depth-1, OGDepth, False, alpha, beta, None)[1]
                self.undoMove()
                if currentEval > maxEval:
                    maxEval = currentEval
                    bestMove = move
                alpha = max(alpha, currentEval)
                if alpha <= beta:
                    break

                if depth == OGDepth:
                    allmoves.append((move, currentEval))
            return bestMove, maxEval, allmoves
        if not maxPlayer:
            minEval = math.inf
            for move in moves:
                self.makeMove(move)
                currentEval = self.Minimax(depth-1, OGDepth, True, alpha, beta, None)[1]
                self.undoMove()
                if currentEval < minEval:
                    minEval = currentEval
                    bestMove = move
                beta =min(beta, currentEval)
                if beta <= alpha:
                    break
            return bestMove, minEval, allmoves

    def getMinimaxMove(self, depth):
        legalmoves = self.getMovesAdvanced()
        self.iterativeMinimax = False
        move = self.Minimax(depth, depth, True, math.inf, -math.inf, legalmoves)
        print("move", move)
        return move

    def getMCTSmove(self):
        fen = self.getFen()
        fen = fen.split(" ")
        turn = int(fen[5])
        if turn < 4:
            mover = self.findBestMove()[0]
        else:
            mover = MCTS.getMCTSmove(self.getFen())
        return mover

def loadImages():
    pieces = {'wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ'}
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('Images/' + piece + '.png'), ((SQ_SIZE) ,(SQ_SIZE)))

def drawGameState(screen, board, validmoves, whiteToMove, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, validmoves, whiteToMove, board, sqSelected)
    drawPieces(screen, board)

def drawBoard(screen):
    global Colors
    Colors = [p.Color("#ebc28e"), p.Color("#89420B")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            Color = Colors[((r+c)%2)]
            p.draw.rect(screen, Color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlightSquares(screen, validmoves, whiteToMove, board, sqSelected):
    if len(sqSelected) > 0:
        r, c = sqSelected
        if board[r][c][0] == ('w' if whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('yellow'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color("red"))
            for move in validmoves:
                move = str(move)
                startRow, startCol = returnMover(move[0], move[1])
                if startRow == r and startCol == c:
                    endRow, endCol = returnMover(move[2], move[3])
                    screen.blit(s, (SQ_SIZE*endCol, SQ_SIZE*endRow))

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                image = IMAGES[piece]
                screen.blit(image, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def createBoardArray(fen):
    ttboard = []
    pieces = fen.split(" ", 1)[0]
    rows = pieces.split("/")
    for row in rows:
        tempboard = []
        for piece in row:
            if piece.isdigit():
                for i in range(0, int(piece)):
                    tempboard.append("--")
            else:
                if piece.islower():
                    tempboard.append("b" + piece.upper())
                elif piece.upper():
                    tempboard.append("w" + piece)
        ttboard.append(tempboard)
    return ttboard

def main():
    MultipleGames = False #System for enabling multiple gamess at a time, IE training AI
    numGames = 1
    games = None
    if MultipleGames:
        games = []
        for x in range(numGames):
            games.append(game(x))
    elif not MultipleGames:
        games = game(numGames)
    running = True
    p.init()
    screen = p.display.set_mode((WIDHT, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("Black"))
    loadImages()
    moveMade = False
    sqselected = ()
    playerclicks = []
    tempoboard = chess.Board()
    tempoarray = createBoardArray(tempoboard.fen())
    validMoves = []
    validMoves = None
    drawGameState(screen, tempoarray, validMoves, games.whiteToMove, sqselected)
    clock.tick(MAX_FPS)
    p.display.flip()
    whiteAI = True
    blackAI = True
    movesPossible = True
    while running:
        if MultipleGames:
            for x in games:
                if not x.gameOver:
                    if x.starting == True:
                        x.startGame()
                    x.showBoard()
                    fen = x.getFen()
                    fen = fen.split(" ")
                    if fen[1] == 'w' and whiteAI and x.gameOver:
                        temp = x.findBestMove()
                        print(temp[1], "white move eval")
                        temp = temp[0]
                        x.makeMove(temp)
                    elif fen[1] == 'b' and blackAI and x.gameOver:
                        temp = x.findBestMove()
                        print(temp[1], "black move eval")
                        temp = temp[0]
                        x.makeMove(temp)
                    games[x].updateGameOver()
                else:
                    pass
        if MultipleGames and movesPossible:
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
            fen = games[0].getFen()
            arrayBoard = createBoardArray(fen)
            legalMoves = games[0].getLegalMovesUCI()
            whiteToMove = games[0].whiteToMove
            sqselected = []
            drawGameState(screen, arrayBoard, legalMoves, whiteToMove, sqselected)
            clock.tick(MAX_FPS)
            p.display.flip()
        else:
            games.startGame()
            arrayBoard = createBoardArray(games.getFen())
            whiteToMove = games.whiteToMove
            validmoves = games.getLegalMovesUCI()
            drawGameState(screen, arrayBoard, validmoves, whiteToMove, sqselected)
            clock.tick(MAX_FPS)
            p.display.flip()
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                elif e.type ==p.MOUSEBUTTONDOWN and not games.gameOver:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqselected == (row, col):
                        sqselected = ()
                        playerclicks = []
                    else:
                        sqselected = (row, col)
                        playerclicks.append(sqselected)
                    if len(playerclicks) == 2:
                        move = str(getMover(playerclicks[0][0], playerclicks[0][1]) + getMover(playerclicks[1][0], playerclicks[1][1]))
                        if games.whiteToMove and playerclicks[0][0] == 1 and playerclicks[1][0] == 0:
                            board = createBoardArray(games.getFen())
                            if board[playerclicks[0][0]][playerclicks[0][1]] == "wP":
                                move = getPromotionInput(move)

                        elif not games.whiteToMove and playerclicks[0][0] == 6 and playerclicks[1][0] == 7:
                            board = createBoardArray(games.getFen())
                            if board[playerclicks[0][0]][playerclicks[0][1]] == "bP":
                                move = getPromotionInput(move)

                        validmoves = games.getLegalMovesUCI()
                        for x in validmoves:
                            if str(x) == move:
                                games.makeMoveUCI(x)
                                xt = str(x)
                                print(move)
                                sqselected = []
                                playerclicks = []
                                games.analyseBoard()
                                moveMade = True


                        if not moveMade:
                            playerclicks = [sqselected]
                elif e.type == p.KEYDOWN:
                    if e.key == p.K_z:
                        games.undoMove()
                        moveMade = True
                    if e.key == p.K_r:
                        numGames = games.ID =+ 1
                        games = game(numGames)

            if whiteAI and games.whiteToMove and not games.gameOver:
                print("white Minimax move")
                Minimax = False
                mover = games.getMCTSmove()
                if Minimax:
                    print(mover[1], "White move eval")
                    mover = mover[0]
                games.makeMove(mover)
                drawGameState(screen, arrayBoard, validmoves, whiteToMove, sqselected)
                clock.tick(MAX_FPS)
                p.display.flip()
                moveMade = True
            elif blackAI and not games.whiteToMove and not games.gameOver:
                print("black Minimax move")
                Minimax = True
                mover = games.findBestMove()
                if Minimax == True:
                    print(mover[1], "Black move eval")
                    mover = mover[0]
                print("mover,", mover)
                games.makeMove(mover)
                drawGameState(screen, arrayBoard, validmoves, whiteToMove, sqselected)
                clock.tick(MAX_FPS)
                p.display.flip()
                moveMade = True
            if games.gameOver:
                if games.whiteWin and movesPossible:
                    print("Game Over, white win")
                elif not games.whiteWin and not games.checkDraw() and movesPossible:
                    print("Game Over, Black win")
                elif not games.whiteWin and games.checkDraw() and movesPossible:
                    print("Game Over, Draw")
                movesPossible = False


            if moveMade:
                games.updateGameOver()
                print("move catalog: ", games.moveCatalog)
                print("Move done")
                if games.whiteToMove:
                    print("White Move")
                else:
                    print("black Move")
                sqselected = []
                playerclicks = []

                moveMade = False


def getMover(r, c):
    rankstoRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowstoRanks = {v: k for k, v in rankstoRows.items()}
    filestoCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colstoFiles = {v: k for k, v in filestoCols.items()}
    return colstoFiles[c] + rowstoRanks[r]

def returnMover(letter, number):
    rowstoRanks = {7: "1", 6: "2", 5: "3", 4: "4", 3: "5", 2: "6", 1: "7", 0: "8"}
    rankstoRows = {v: k for k, v in rowstoRanks.items()}
    colstoFiles = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
    filestoCols = {v: k for k, v in colstoFiles.items()}
    return rankstoRows[number], filestoCols[letter]

def getPromotionInput(move):
    print("Castlemove, input desired piece (lowercases(, options = q, b, r, n")
    desired = str(input())
    if desired == "q" or "b" or "r" or "n":
        move = str(move + desired)
        print("Promotion: ", move)
    else:
        print("wrong, try again")
        move = getPromotionInput(move)
    return move

if __name__ == "__main__":
    main()
