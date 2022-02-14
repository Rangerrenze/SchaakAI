import math

import stockfish
import random
import chess
import chess.svg
import time

board = chess.Board()
running = True

class game:
    def __init__(self, ID):
        self.ID = ID
        self.starting = True
        self.miniMaxOGgoing = True
        self.minimaxGameOver = False
        self.minimxDraw = False
        self.board = None
        self.stockFishmove = None
        self.selfMove = None
        self.whiteToMove = True
        self.stockfishy = stockfish.Stockfish(
        path=r"C:\Users\Renze Koper\Documents\stockfish_14.1_win_x64_avx2/stockfish_14.1_win_x64_avx2", depth=1, parameters={"Threads": 4, "Minimum Thinking Time": 30})
    def startGame(self):
        self.board = board
        self.starting = False

    def getFen(self):
        return self.board.fen()

    def getStockFishMove(self):
        fenn = self.getFen()
        self.stockfishy.set_fen_position(fenn)
        test = self.stockfishy.get_best_move()
        return test

    def makeMove(self, move):
        self.board.push_san(move)
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


    def findBestMove(self):
        self.startTime = time.time()
        self.moveTime = 10
        moves = self.getLegalMoves()
        ri = random.randint(0, len(moves) - 1)
        bestMove = moves[ri]
        bestScore = -math.inf
        for depth in range(100):
            move, score = self.Minimax(depth, depth, True, math.inf, -math.inf)
            if move:
                bestScore, bestMove = score, move
                print(bestMove)
        print("returning")
        return bestMove, bestScore


    def Minimax(self, depth, OGDepth, maxPlayer, alpha, beta):
        if time.time() - self.startTime > self.moveTime and depth == OGDepth:
            return None, None
        
        if depth == OGDepth:
            self.miniMaxOGgoing = self.whiteToMove
        moves = self.getLegalMoves()
        self.minimxDraw = self.checkDraw()
        self.minimaxGameOver = self.CheckGameOver()
        if depth == 0:
            fen = self.getFen()
            self.stockfishy.set_fen_position(fen)
            score = self.stockfishy.get_evaluation()
            score = score["value"]
            return None, score
        elif self.minimaxGameOver != None:
            score = 0
            if self.whiteToMove == self.miniMaxOGgoing:
                score = 1000000
            elif self.whiteToMove != self.miniMaxOGgoing:
                score = -100000
            return None, score
        elif self.minimxDraw:
            score = 10
            return None, score

        ri = random.randint(0, len(moves)-1)
        bestMove = moves[ri]
        if maxPlayer:
            maxEval = -math.inf
            for move in moves:
                self.makeMove(move)
                currentEval = self.Minimax(depth-1, OGDepth, False, alpha, beta)[1]
                self.undoMove()
                if currentEval > maxEval:
                    maxEval = currentEval
                    bestMove = move
                alpha = max(alpha, currentEval)
                if alpha <= beta:
                    break
            return bestMove, maxEval
        if not maxPlayer:
            minEval = math.inf
            for move in moves:
                self.makeMove(move)
                currentEval = self.Minimax(depth-1, OGDepth, True, alpha, beta)[1]
                self.undoMove()
                if currentEval < minEval:
                    minEval = currentEval
                    bestMove = move
                beta =min(beta, currentEval)
                if beta <= alpha:
                    break
            return bestMove, minEval

    def getMinimaxMove(self, depth):
        move = self.Minimax(depth, depth, True, math.inf, -math.inf)
        return move






def main():
    numGames = 1
    while running:
        lastmove = None
        games = [game(numGames)]
        for x in games:
            if x.starting == True:
                x.startGame()
            x.showBoard()
            fen = x.getFen()
            fen = fen.split(" ")
            if fen[1] == 'w':
                temp = x.findBestMove()
                print(temp[1], "white move eval")
                temp = temp[0]
                lastmove = temp
                x.makeMove(temp)
            else:
                temp = x.findBestMove()
                print(temp[1], "black move eval")
                temp = temp[0]
                lastmove = temp
                x.makeMove(temp)

        board = chess.Board(games[0].getFen())
        squares = board.attacks(chess.E4)
        chess.svg.board(board, squares=squares, size=350)
if __name__ == "__main__":
    main()
