import chess
import math
import random
import time
from math import inf

class node:
    def __init__(self):
        self.state = chess.Board()
        self.action = ''
        self.children = set()
        self.parent = None
        self.N = 0
        self.n = 0
        self.v = 0

path = "openingBook.txt"
openingbook = []
with open(path, "r") as file:
    for line in file:
        tempLine = line.split(" ")
        openingbook.append(tempLine)


def ucb1(currentNode):
    ans = currentNode.v+2*(math.sqrt(math.log(currentNode.N+math.e+(10**-6))/(currentNode.n+(10**-10))))
    return ans

def MCTSRollout(currentNode):
    if currentNode.state.is_game_over():
        board = currentNode.state
        if board.result() =='1-0':
            return 1, currentNode
        elif board.result() =='0-1':
            return -1, currentNode
        else:
            return 0.5, currentNode
    moveCatalog = getAdvancedMoves(currentNode.state.fen())
    for i in moveCatalog:
        tempState = chess.Board(currentNode.state.fen())
        tempState.push_san(i)
        child = node()
        child.state = tempState
        child.parent = currentNode
        currentNode.children.add(child)
    randomState = random.choice(list(currentNode.children))
    return MCTSRollout(randomState)

def MCTSExpand(currentNode, white):
    if len(currentNode.children) == 0:
        return currentNode
    if white:
        maxUCB = -inf
        idx = -1
        selectedChild = None
        for i in currentNode.children:
            temp = ucb1(i)
            if temp > maxUCB:
                idx = i
                maxUCB = temp
                selectedChild = i
        return MCTSExpand(selectedChild, 0)

    else:
        idx = -1
        minUCB = inf
        selectedChild = None
        for i in currentNode.children:
            temp = ucb1(i)
            if temp<minUCB:
                idx = i
                minUCB = temp
                selectedChild = i
        return MCTSExpand(selectedChild, 1)

def MCTSRollback(currentNode, reward):
    currentNode.n += 1
    currentNode.v += reward
    while currentNode.parent!=None:
        currentNode.N+=1
        currentNode = currentNode.parent

    return currentNode



def MCTSPredict(currentNode, over, white, iterations = 30):
    if over:
        return -1
    moveCatalog = getAdvancedMoves(currentNode.state.fen())
    mapStateMove = dict()
    for i in moveCatalog:
        tempState = chess.Board(currentNode.state.fen())
        tempState.push_san(i)
        child = node()
        child.state = tempState
        child.parent = currentNode
        currentNode.children.add(child)
        mapStateMove[child] = i

    while iterations >0:
        if white:
            idx = -1
            maxUCB = -inf
            selectedChild = None
            for i in currentNode.children:
                temp = ucb1(i)
                if temp>maxUCB:
                    idx = i
                    maxUCB = temp
                    selectedChild = i
            exChild = MCTSExpand(selectedChild, 0)
            reward,state = MCTSRollout(exChild)
            currentNode = MCTSRollback(state, reward)
            iterations -=1
            print("MCTS search depth left", iterations)

        else:
            idx = -1
            minUCB = inf
            selectedChild = None
            for i in currentNode.children:
                temp = ucb1(i)
                if temp<minUCB:
                    idx = i
                    minUCB = temp
                    selectedChild = i
            exChild = MCTSExpand(selectedChild, 1)
            reward, state = MCTSRollout(exChild)
            currentNode = MCTSRollback(state, reward)
            iterations -= 1
            print("MCTS search depth left", iterations)

    if white:
        mx = -inf
        idx = -1
        selectedMove = ''
        for i in currentNode.children:
            temp = ucb1(i)
            if temp>mx:
                mx = temp
                selectedMove = mapStateMove[i]
        return selectedMove
    else:
        mn = inf
        idx = -1
        selectedMove = ''
        for i in currentNode.children:
            temp = ucb1(i)
            if temp<mn:
                mn = temp
                selectedMove = mapStateMove[i]
        return selectedMove

def getLegalMoves(fen):
    board = chess.Board(fen)
    legalMoves = str(board.legal_moves)
    legalMoves = legalMoves.split("(")
    legalMoves = legalMoves[1].split(")")
    legalMoves = legalMoves[0].split(", ")
    return legalMoves


def getAdvancedMoves(fen):
    possibleMoves = []
    temp = fen.split(" ")
    movetracker = int(temp[5])
    BlackToMove = False
    if temp[1] == "b":
        BlackToMove = True
    else:
        BlackToMove = False
    moveTracker = ((movetracker - 1) * 2) + (1 if BlackToMove else 0)

    if moveTracker < 7:
        for i in openingbook:
            if moveTracker == 0:
                mover = i[moveTracker]
                if mover not in possibleMoves:
                    possibleMoves.append(mover)
            elif moveTracker != 0:
                    mover = i[moveTracker]
                    legalMoves = getLegalMoves(fen)
                    if mover in legalMoves:
                        if mover not in possibleMoves:
                            possibleMoves.append(mover)
        if len(possibleMoves) == 0:
            possibleMoves = getLegalMoves(fen)
    else:
        possibleMoves = getLegalMoves(fen)
    return possibleMoves





def getMCTSmove(boardFen):
    print("working")
    board = chess.Board(boardFen)
    fen = boardFen.split(" ")
    mover = fen[1]
    white = 1 if mover == "w" else 0
    root = node()
    root.state = board
    result = MCTSPredict(root, board.is_game_over(), white)
    return result


