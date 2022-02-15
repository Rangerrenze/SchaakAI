import math

import stockfish
import random
import chess
import chess.svg
import time
from operator import itemgetter
import pygame as p
import numpy

board = chess.Board()
screenSize = 512
WIDHT = HEIGHT = screenSize
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

class game:
    def __init__(self, ID):
        self.ID = ID
        self.OGplayer = None
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
        self.whiteToMove = not self.whiteToMove

    def makeMoveUCI(self, move):
        self.board.push(move)
        self.whiteToMove = not self.whiteToMove

    def undoMove(self):
        self.board.pop()
        self.whiteToMove = not self.whiteToMove

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
        return board.outcome()

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

    def analyseBoard(self):
        fen = self.getFen()
        self.stockfishy2.set_fen_position(fen)
        self.stockfishy.set_fen_position(fen)
        val1 = self.stockfishy2.get_evaluation()
        val2 = self.stockfishy.get_evaluation()
        print("Stockfish depth 18 analysis: ", val1, "Stockfish depth 2 analysis", val2)

    def findBestMove(self):
        self.startTime = time.time()
        self.moveTime = 5
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
                startMoves = self.getLegalMoves()
            else:
                startMoves = previousMoves

            move, score, allMoves = self.Minimax(depth, depth, True, math.inf, -math.inf, startMoves)
            if move:
                allMoves.sort(key=itemgetter(1),reverse=True)
                previousMoves = allMoves
                bestScore, bestMove = score, move
                print(bestMove, depth)
        return bestMove, bestScore


    def Minimax(self, depth, OGDepth, maxPlayer, alpha, beta, startMoves):
        if time.time() - self.startTime > self.moveTime and depth == OGDepth:
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
        elif self.minimaxGameOver != None:
            score = 0
            if (self.OGplayer == "w" and self.whiteToMove) or (self.OGplayer == "b" and not self.whiteToMove):
                score = math.inf
            if (self.OGplayer == "w" and not self.whiteToMove) or (self.OGplayer == "b" and self.whiteToMove):
                score = -math.inf
            return None, score
        elif self.minimxDraw:
            score = 100000
            return None, score, None
        allmoves = []
        if not depth == OGDepth or OGDepth == 1:
            moves = self.getLegalMoves()
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
        move = self.Minimax(depth, depth, True, math.inf, -math.inf, None)
        return move

def loadImages():
    pieces = {'wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ'}
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('Images/' + piece + '.png'), ((SQ_SIZE) ,(SQ_SIZE)))

def drawGameState(screen, board):
    drawBoard(screen)
    # highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, board)

def drawBoard(screen):
    global Colors
    Colors = [p.Color("#ebc28e"), p.Color("#89420B")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            Color = Colors[((r+c)%2)]
            p.draw.rect(screen, Color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlightSquares(screen, gs, validMoves, sqSelected):
    if not gs.gameOver:
        if len(sqSelected) > 0:
            r, c = sqSelected
            if gs.board[r][c][0] == ('w' if gs.WhiteToMove else 'b'):
                s = p.Surface((SQ_SIZE, SQ_SIZE))
                s.set_alpha(100)
                s.fill(p.Color('yellow'))
                screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
                s.fill(p.Color("red"))
                for move in validMoves:
                    if move.startRow == r and move.startCol == c:
                        screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))




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
    tempoboard = chess.Board()
    tempoarray = createBoardArray(tempoboard.fen())
    drawGameState(screen, tempoarray)
    clock.tick(MAX_FPS)
    p.display.flip()
    whiteAI = False
    blackAI = False
    sqselected = ()
    playerclicks = []


    while running:
        lastmove = None
        if MultipleGames:
            for x in games:
                if x.starting == True:
                    x.startGame()
                x.showBoard()
                fen = x.getFen()
                fen = fen.split(" ")
                if fen[1] == 'w' and whiteAI:
                    temp = x.findBestMove()
                    print(temp[1], "white move eval")
                    temp = temp[0]
                    lastmove = temp
                    x.makeMove(temp)
                    x.moveCatalog.append(temp)
                elif fen[1] == 'b' and blackAI:
                    temp = x.findBestMove()
                    print(temp[1], "black move eval")
                    temp = temp[0]
                    lastmove = temp
                    x.makeMove(temp)
                    x.moveCatalog.append(temp)
        if MultipleGames:
            fen = games[0].getFen()
        else:
            games.startGame()
            fen = games.getFen()
        arrayBoard = createBoardArray(fen)
        drawGameState(screen, arrayBoard)
        clock.tick(MAX_FPS)
        p.display.flip()
        if MultipleGames:
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
        else:
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                elif e.type ==p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqselected == (row, col):
                        sqselected = ()
                        playerclicks = []
                    else:
                        sqselected = (row, col)
                        playerclicks.append(sqselected)
                    print(len(playerclicks))
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
                        temp = True
                        for x in validmoves:
                            # print(x)
                            if str(x) == move:
                                print(move)
                                games.makeMoveUCI(x)
                                games.moveCatalog.append(x)
                                playerclicks = []
                                sqselected = ()
                                fen = games.getFen()
                                arrayBoard = createBoardArray(fen)
                                drawGameState(screen, arrayBoard)
                                p.display.flip()
                                games.analyseBoard()
                                print(games.whiteToMove)
                                temp = False
                        if temp:
                            playerclicks = []
                            sqselected = []








            if whiteAI and games.whiteToMove:
                mover = games.findBestMove()
                if type(mover) == list or bytearray:
                    print(mover[1], "White move eval")
                    mover = mover[0]
                games.makeMove(mover)
                games.moveCatalog.append(mover)
            elif blackAI and not games.whiteToMove:
                mover = games.findBestMove()
                if type(mover) == list or bytearray:
                    print(mover[1], "Black move eval")
                    mover = mover[0]
                games.makeMove(mover)
                games.moveCatalog.append(mover)



def getMover(r, c):
    rankstoRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowstoRanks = {v: k for k, v in rankstoRows.items()}
    filestoCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colstoFiles = {v: k for k, v in filestoCols.items()}
    return colstoFiles[c] + rowstoRanks[r]


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
