import math
import stockfish
import random
import chess
import time
from operator import itemgetter
import pygame as p
# import numpy
import MCTS
import visualize
import neat
import os

def updateSettings():

    global blackAIplaying, whiteAIplaying, IterativeMinimax, MonteCarlo, NormalStockfish, NeuralNetworkMove, NeuralNetworkTraining, loadCheckpoint, checkpointing, runGenerations, NEATactive, randomMoves
    blackAIplaying = True
    whiteAIplaying = False
    IterativeMinimax = False
    MonteCarlo = False
    NormalStockfish = False
    NeuralNetworkMove = False
    NeuralNetworkTraining = True
    loadCheckpoint = 0
    checkpointing = False
    runGenerations = 300
    randomMoves = False
    NEATactive = False
    if NeuralNetworkMove or NeuralNetworkTraining:
        NEATactive = True

board = chess.Board()
screenSize = 512
WIDHT = HEIGHT = screenSize
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
path = "openingBook.txt"
openingbook = []
generation = 0

with open(path, "r") as file:
    for line in file:
        tempLine = line.split(" ")
        openingbook.append(tempLine)

class game:
    def __init__(self, ID, stockfishELO):
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
        self.NNStockFishElo = stockfishELO
        self.NNStockfishy = stockfish.Stockfish(path=r"C:\Users\Renze Koper\Documents\stockfish_14.1_win_x64_avx2/stockfish_14.1_win_x64_avx2", depth=2, parameters={"Threads": 4, "Minimum Thinking Time": 30})
        self.NNStockfishy.set_elo_rating(self.NNStockFishElo)
        self.whiteToMove = True
        self.stockfishy = stockfish.Stockfish(
        path=r"C:\Users\Renze Koper\Documents\stockfish_14.1_win_x64_avx2/stockfish_14.1_win_x64_avx2", depth=2, parameters={"Threads": 4, "Minimum Thinking Time": 30})
        self.stockfishy2 = stockfish.Stockfish(
            path=r"C:\Users\Renze Koper\Documents\stockfish_14.1_win_x64_avx2/stockfish_14.1_win_x64_avx2", depth=18,
            parameters={"Threads": 4, "Minimum Thinking Time": 30})
        self.gameOver = False
        self.whiteWin = True
        self.NNplaying = False
        self.whiteNN = False

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

    def getNNStockFishMove(self):
        fenn = self.getFen()
        self.NNStockfishy.set_fen_position(fenn)
        test = self.NNStockfishy.get_best_move()
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

    def makeMoveNN(self, move):
        tempmove = self.board.san(move)
        self.board.push(move)
        self.moveCatalog.append(tempmove)
        self.moveTracker += 1
        self.whiteNN = not self.whiteToMove
        self.NNGameOverUpdate()

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

    def NNGameOverUpdate(self):
        self.draw = self.checkDraw()
        if self.board.is_game_over():
            boardfen = self.board.fen
            boardfen = str(boardfen)
            boardfen = boardfen.split(" ")
            if boardfen[1] == "b":
                if self.whiteNN:
                    index = self.ID -1
                    ge[index].fitness -= 100
                    removeBoard(index)
                else:
                    index = self.ID - 1
                    ge[index].fitness += 1000
                    tempELO = stockfishELO
                    stockfishELO += 50
                    f = open("NNwins.txt", "a")
                    writingString = "NN win" + str(tempELO) + str(self.moveCatalog)
                    f.write(writingString)
                    f.close()
            elif boardfen[1] == "w":
                if self.whiteNN:
                    index = self.ID -1
                    ge[index].fitness += 1000
                    removeBoard(index)
                    tempELO = stockfishELO
                    stockfishELO += 50
                    f = open("NNwins.txt", "a")
                    writingString = "NN win" + str(tempELO) + str(self.moveCatalog)
                    f.write(writingString)
                    f.close()


                else:
                    index = self.ID - 1
                    ge[index].fitness -= 100
                    removeBoard(index)

            else:
                index = self.ID -1
                ge[index].fitness += 500
                stockfishELO += 10
                removeBoard(index)

            self.gameOver = True



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
        if self.moveTracker < 16:
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
        if self.moveTracker < 17:
            mover = self.findBestMove()[0]
        else:
            mover = MCTS.getMCTSmove(self.getFen())
        return mover
    def getMCTSpure(self):
        fen = self.getFen()
        mover = MCTS.getMCTSmove(fen)
        return mover

    def getNNmove(self):
        input = getInput(self.getFen(), self.getLegalMovesUCI())
        index = self.ID -1
        legalmoves = self.getLegalMovesUCI()
        NNMoveMade = False
        for i in range(10):
            output = nets[index].activate(
                input
            )
            print("output", output)
            if len(str(output)) == 4:
                ge[index].fitness += 5
                move = str(getMover(output[0], output[1]) + getMover(output[2], output[3]))
                if move in legalmoves:
                    ge[index].fitness += 100
                    print(1000-i)
                    NNMoveMade = True
                    return move
        if not NNMoveMade:
            ge[index].fitness -= 10000
            removeBoard(index)





def removeBoard(index):
    games.pop(index)
    ge.pop(index)
    nets.pop(index)

def getInput(fen, allmoves):
    generatedInput = []
    moveInput = []
    boardInput = map_fen_to_input(fen)

    for move in allmoves:
        temp = returnMover(move[0], move[1]) + returnMover(move[2], move[3])
        moveInput.append(temp)
    generatedInput.append(moveInput)
    generatedInput.append(boardInput)
    generatedInput.extend([])

    return generatedInput

def getInput(fen, allmoves):
    generatedInput = []
    moveInput = []
    boardInput = map_fen_to_input(fen)
    nodes_moves = 100
    tempfen = fen.split(" ")
    if tempfen[1] == 'w':
        generatedInput.append(1)
    else:
        generatedInput.append(-1)

    for move in allmoves:
        move = str(move)
        temp = int(NNInputMover(move[0], move[1]) + NNInputMover(move[2], move[3]))
        moveInput.append(temp)
    for k in range(nodes_moves - len(moveInput)):
        moveInput.append(-1)
    generatedInput.extend(moveInput)
    generatedInput.extend(boardInput)

    return generatedInput

def map_fen_to_input(fen):
    chunks = fen.split(" ")
    grid = chunks[0]
    rows = grid.split("/")

    n_input = []
    _square_depth = 9

    for row in rows:
        for square in row:
            activations = {
                'p': (0, 6),
                'n': (1, 6),
                'b': (2, 6),
                'r': (3, 6),
                'q': (4, 6),
                'k': (5, 6),
                'P': (0, 7),
                'N': (1, 7),
                'B': (2, 7),
                'R': (3, 7),
                'Q': (4, 7),
                'K': (5, 7),
            }
            indices = activations.get(square, False)

            if not indices:
                for k in range(int(square)):
                    to_append = [0 for j in range(_square_depth)]
                    to_append[8] = -1  # Signal this square is empty
                    n_input.append(to_append)
            else:
                to_append = [0 for j in range(_square_depth)]
                to_append[indices[0]] = 1
                to_append[indices[1]] = 1
                to_append[8] = 1  # Signal this square is occupied
                n_input.append(to_append)

    flat_n_input = [n for square in n_input for n in square]
    flat_n_input.extend([])
    return flat_n_input


def NNInputMover(letter, number):
    rowstoRanks = {7: "1", 6: "2", 5: "3", 4: "4", 3: "5", 2: "6", 1: "7", 0: "8"}
    rankstoRows = {v: k for k, v in rowstoRanks.items()}
    colstoFiles = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
    filestoCols = {v: k for k, v in colstoFiles.items()}
    return (str(rankstoRows[number]) + str(filestoCols[letter]))

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



def main(genomes, config):
    global games, nets, ge, generation, stockfishELO
    NN = NEATactive
    whiteAI = True
    MultipleGames = False #System for enabling multiple gamess at a time, IE training AI
    if NN :
        if NeuralNetworkTraining:
            MultipleGames = True
        else:
            MultipleGames = False
    games = None
    stockfishELO = 100
    idtemp = 1
    if MultipleGames:
        games = []
    elif not MultipleGames:
        games = game(1, stockfishELO)
    ge = []
    nets = []
    generation += 1
    if NN and MultipleGames:
        for _,g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            games.append(game(idtemp, stockfishELO))
            idtemp += 1
            g.fitness = 0
            ge.append(g)
    print(nets, ge)
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
    if MultipleGames:
        drawGameState(screen, tempoarray, validMoves, games[0].whiteToMove, sqselected)
    else:
        drawGameState(screen, tempoarray, validMoves, games.whiteToMove, sqselected)
    clock.tick(MAX_FPS)
    p.display.flip()
    blackAI = blackAIplaying
    whiteAI = whiteAIplaying
    training = NeuralNetworkTraining
    movesPossible = True
    while running:
        if MultipleGames:
            for x in games:
                if not x.gameOver:
                    if x.starting == True:
                        x.startGame()
                    fen = x.getFen()
                    tempfen = fen.split(" ")
                    # if tempfen[1] == 'w':
                    #     if x.ID % 2 == 0:
                    #         temp = x.getNNmove()
                    #         print("nn move", temp)
                    #         x.makeNNmove(temp)
                    #     else:
                    #         temp = x.getNNStockFishMove()
                    #         print(temp)
                    #         x.makeMove(temp)
                    # elif tempfen[1] == 'b':
                    #     if x.ID % 2 == 0:
                    #         temp = x.getNNStockFishMove()
                    #         x.makeMove(temp)
                    #     else:
                    #         temp = x.getNNmove()
                    #         print("nn move", temp)
                    #         x.makeNNmove(temp)
                    temp = x.getNNmove()
                    print("nn move", temp)
                    x.makeMoveNN(temp)
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
            print(games[0].ID)
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
                        games = game(numGames, stockfishELO)

            if whiteAI and games.whiteToMove and not games.gameOver:
                print("White AI move")
                if IterativeMinimax:
                    mover = games.findBestMove()
                    print(mover[1], "White move eval")
                    mover = mover[0]
                    games.makeMove(mover)
                    drawGameState(screen, arrayBoard, validmoves, whiteToMove, sqselected)
                    clock.tick(MAX_FPS)
                    p.display.flip()
                    moveMade = True
                elif MonteCarlo:
                    mover = games.getMCTSmove()
                    games.makeMove(mover)
                    drawGameState(screen, arrayBoard, validmoves, whiteToMove, sqselected)
                    clock.tick(MAX_FPS)
                    p.display.flip()
                elif NormalStockfish:
                    mover = games.getStockFishMove()
                    games.makeMove(mover)
                    drawGameState(screen, arrayBoard, validmoves, whiteToMove, sqselected)
                    clock.tick(MAX_FPS)
                    p.display.flip()
                elif NeuralNetworkMove:
                    mover = games.getNNmove()
                    games.makeMove(mover)
                    drawGameState(screen, arrayBoard, validmoves, whiteToMove, sqselected)
                    clock.tick(MAX_FPS)
                    p.display.flip()
                elif randomMoves:
                    mover = games.getRandomMove()
                    games.makeMove(mover)
                    drawGameState(screen, arrayBoard, validmoves, whiteToMove, sqselected)
                    clock.tick(MAX_FPS)
                    p.display.flip()
                else:
                    mover = games.findBestMove()
                    print(mover[1], "White move eval")
                    mover = mover[0]
                    games.makeMove(mover)
                    drawGameState(screen, arrayBoard, validmoves, whiteToMove, sqselected)
                    clock.tick(MAX_FPS)
                    p.display.flip()
                    moveMade = True
            elif blackAI and not games.whiteToMove and not games.gameOver:
                print("Black AI move")
                if IterativeMinimax:
                    mover = games.findBestMove()
                    print(mover[1], "Black move eval")
                    mover = mover[0]
                    games.makeMove(mover)
                    drawGameState(screen, arrayBoard, validmoves, whiteToMove, sqselected)
                    clock.tick(MAX_FPS)
                    p.display.flip()
                    moveMade = True
                elif MonteCarlo:
                    mover = games.getMCTSmove()
                    games.makeMove(mover)
                    drawGameState(screen, arrayBoard, validmoves, whiteToMove, sqselected)
                    clock.tick(MAX_FPS)
                    p.display.flip()
                elif NormalStockfish:
                    mover = games.getStockFishMove()
                    games.makeMove(mover)
                    drawGameState(screen, arrayBoard, validmoves, whiteToMove, sqselected)
                    clock.tick(MAX_FPS)
                    p.display.flip()
                elif NeuralNetworkMove:
                    mover = games.getNNmove()
                    games.makeMove(mover)
                    drawGameState(screen, arrayBoard, validmoves, whiteToMove, sqselected)
                    clock.tick(MAX_FPS)
                    p.display.flip()
                elif randomMoves:
                    mover = games.getRandomMove()
                    games.makeMove(mover)
                    drawGameState(screen, arrayBoard, validmoves, whiteToMove, sqselected)
                    clock.tick(MAX_FPS)
                    p.display.flip()
                else:
                    mover = games.findBestMove()
                    print(mover[1], "Black move eval")
                    mover = mover[0]
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



def run(config_path):
    if NEATactive:
        print("test")
        config = neat.config.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path
        )

        if checkpointing:
            tmpGens = loadCheckpoint - 1
            tmpname = 'neat-checkpoint-{0}'.format(tmpGens)

            p = neat.checkpoint.Checkpointer.restore_checkpoint(tmpname)
            generation = p.generation
        else:
            p = neat.Population(config)

        p.add_reporter(neat.StdOutReporter(True))
        p.add_reporter(neat.checkpoint.Checkpointer(20,None))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)

        winner = p.run(main, runGenerations)
        visualize.plot_stats(stats, ylog=True, view=True, filename="feedforward-fitness.svg")
        visualize.plot_species(stats, view=True, filename="feedforward-speciation.svg")

        node_names = {-1: 'x', -2: 'dx', -3: 'theta', -4: 'dtheta', 0: 'control'}
        visualize.draw_net(config, winner, True, node_names=node_names)

        visualize.draw_net(config, winner, view=True, node_names=node_names,
                           filename="winner-feedforward.gv")
        visualize.draw_net(config, winner, view=True, node_names=node_names,
                           filename="winner-feedforward-enabled.gv", show_disabled=False)
        visualize.draw_net(config, winner, view=True, node_names=node_names,
                           filename="winner-feedforward-enabled-pruned.gv", show_disabled=False, prune_unused=True)
    else:
        main(None, None)



if __name__ == "__main__":
    updateSettings()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
