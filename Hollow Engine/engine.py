import random
import time
from board import Board
import threading
import copy

gs = Board()

TransposeDict = {}

CHECKMATE = 100000000000
STALEMATE = 0
DEPTH = 3

piece_value = {
    'P' : 100,
    'N' : 300,
    'B' : 300,
    'Q' : 900,
    'R' : 500,
    'p' : -100,
    'n' : -300,
    'b' : -300,
    'q' : -900,
    'r' : -500, 
    'k' : 0,
    'K' : 0      
}

pawns_table = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]

knights_table = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

bishops_table = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

rooks_table = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0
]

queens_table = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
    0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

king_middle_table = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20
]

king_end_table = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]

nodes = 0

def findRandomMove(validMoves):
    print('Random move made')
    return validMoves[random.randint(0, len(validMoves)-1)]


def findBestMove(gs, validMoves, returnQue, savebestMove = True):
    global next_move, Counter, _score, nodes
    next_move = None
    Counter = 0
    _score = 0

    start_time = time.perf_counter()  # Get the current time

    next_move = root_search(gs, DEPTH)
    #negamax_alpha_beta(gs,DEPTH,  -CHECKMATE, CHECKMATE, True if gs.color == 'w' else False)

    elapsed_time = time.perf_counter() - start_time  # Calculate elapsed time

    print(nodes, ' Moves evaluated, Computer Score:', _score, elapsed_time, next_move)
    return next_move


'OLD NEGAMAX SEARCH'
def negamax_alpha_beta(gs, depth, alpha, beta, maximizing_player):
    global next_move, Counter, _score
    Counter = Counter + 1
    print(Counter)

    if depth == 0:
        return evaluate(gs)

    best_move = None
    if maximizing_player:
        max_score = -float('inf')
        for move in gs.get_all_valid_moves():
            gs.make_move(move[0], move[1], move[2])
            score = negamax_alpha_beta(gs, depth - 1, -beta, -alpha, False)
            gs.undo_move()
            if score > max_score:
                max_score = score
                best_move = move
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        next_move = best_move
    else:
        min_score = float('inf')
        for move in gs.get_all_valid_moves():
            gs.make_move(move[0], move[1], move[2])
            score = negamax_alpha_beta(gs, depth - 1, -beta, -alpha, True)
            gs.undo_move()
            if score < min_score:
                min_score = score
                best_move = move
            beta = min(beta, score)
            if alpha >= beta:
                break
        next_move = best_move
    _score = max_score if maximizing_player else min_score
    #print('Score: ', _score)
    return max_score if maximizing_player else min_score

def count_flags(bitboard):
  # Convert the bitboard to a binary string
  binary_string = bin(bitboard)
  # Count the number of 1s in the string
  count = binary_string.count("1")
  return count

"SORT MOVES FUNCTION AND QUIESCENCE NEED TO BE IMPLIMETED"
def quiescence(board, alpha, beta, depth):
    global nodes

    pos_eval = evaluate(board, depth)

    if (pos_eval >= beta):
        return beta

    if (alpha < pos_eval):
        alpha = pos_eval

    capture_moves = list(board.generate_legal_captures())

    sort_moves(board, capture_moves)

    for move in capture_moves:
        nodes += 1
        make_move(board, move)
        score = -quiescence(board, -beta, -alpha, depth)
        unmake_move(board)

        if score >= beta:
            return beta
        
        if score > alpha:
            alpha = score
    
    return alpha

def negamax(gs, alpha, beta, depth):
    global nodes
    nodes += 1
    print(nodes)

    if depth == 0 or gs.checkmate:
        return evaluate(gs)

    max = -99999
    moveList = list(gs.get_all_valid_moves())

    #sort_moves(board, moveList)

    for move in moveList:
        nodes += 1
        
        gs.make_move(move[0], move[1], move[2])
        score = -negamax(gs, -beta, -alpha, depth-1)
        gs.undo_move()

        

        if (score > max):
            max = score

        if max > alpha:
            alpha = max

        if (alpha >= beta):
            break

    return max

# Begin search here
def root_search(gs, depth):
    global nodes
    nodes = 0
    nodes += 1

    best_move = None

    max = -99999
    moveList = list(gs.get_all_valid_moves())

    if len(list(moveList)) == 0:
        if gs.in_check(gs.color):
            return -99999     
        return 0

    #sort_moves(board, moveList)

    for move in moveList:
        nodes += 1

        gs.make_move(move[0], move[1], move[2])
        score = -negamax(gs, -99999, 99999, depth - 1)
        #score = -negamax_alpha_beta(gs, -99999, 99999, depth - 1, True)
        gs.undo_move()

        if (score > max):
            max = score
            best_move = move

    return best_move

def evaluate(gs):
    if gs.checkmate:
        if gs.color == 'w':
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0

    # Loop through each piece in the bitboards dictionary
    for piece in gs.bitboards:
        # Get the bitboard for the current piece
        bitboard = gs.bitboards[piece]

        value = piece_value[piece]

        # Add the value of the piece to the score if it is white
        score += (value * count_flags(bitboard))

    score += evaluate_pawn_structure(gs.bitboards, 'P')
    score -= evaluate_pawn_structure(gs.bitboards, 'p')
    return score

def evaluate_pawn_structure(bitboards, color):
    total_evaluation = 0

    # Loop through each piece type in the bitboards dictionary
        # Skip pieces that are not pawns
        # Get the pawn bitboard for the current piece type
    pawn_bitboard = bitboards[color]

        # Initialize the evaluation for the current pawn bitboard
    pawn_evaluation = 0

        # Iterate through each bit in the pawn bitboard
    mask = 1
    for i in range(64):
            # Check if the current bit is set in the pawn bitboard
            if pawn_bitboard & mask:
                # Calculate the row and column of the current pawn
                row = i // 8
                col = i % 8

                # Evaluate the pawn structure based on the pawn's position
                if col in [3, 4] and row in  [2, 3, 4, 5] :
                        pawn_evaluation += 15

                # Check for isolated pawns
                if col > 0 and col < 7:
                    if not (pawn_bitboard & (mask << 1) or pawn_bitboard & (mask >> 1)):
                        pawn_evaluation -= 10

                # Check for doubled pawns
                if row > 0 and row < 7:
                    if pawn_bitboard & (mask << 8):
                        pawn_evaluation -= 10

                # Check if the pawn is in the center columns
                
                
            mask <<= 1

        # Add the evaluation for the current pawn bitboard to the total evaluation
        
    total_evaluation += pawn_evaluation

    return total_evaluation

