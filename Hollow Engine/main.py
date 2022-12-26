import pygame

from board import Board
import engine
from multiprocessing import Process, Queue
import time

gs = Board()

# Set up Pygame window
window_width = 640
window_height = 640
pygame.init()
screen = pygame.display.set_mode((window_width, window_height))

# Set up colors
BLACK = (181,136,99)
WHITE = (240,217,181)

# Set up piece images
piece_images = {
    'P': pygame.image.load('images/wp.png'),
    'N': pygame.image.load('images/wn.png'),
    'B': pygame.image.load('images/wb.png'),
    'R': pygame.image.load('images/wr.png'),
    'Q': pygame.image.load('images/wq.png'),
    'K': pygame.image.load('images/wk.png'),
    'p': pygame.image.load('images/bp.png'),
    'n': pygame.image.load('images/bn.png'),
    'b': pygame.image.load('images/bb.png'),
    'r': pygame.image.load('images/br.png'),
    'q': pygame.image.load('images/bq.png'),
    'k': pygame.image.load('images/bk.png')
}

BOARD_WIDTH = BOARD_HEIGHT = 500
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
Dimension = 8
Sq_Size = BOARD_HEIGHT // Dimension
Max_FPS = 15

def print_bitboard(bitboard):
    # Convert the bitboard to a binary string
    binary = bin(bitboard)[2:]
    # Pad the binary string with zeros to make it 64 bits
    binary = binary.zfill(64)
    # Reverse the binary string so that the first bit is at the top right
    binary = binary[::-1]
    # Split the binary string into 8 chunks of 8 bits each
    rows = [binary[i:i+8] for i in range(0, len(binary), 8)]

    # Print the column labels
    # Print each row with a row label, in reverse order
    for i, row in enumerate(reversed(rows)):
        # Split the row into a list of single-character strings
        row_bits = [char for char in row]
        # Join the bits with a space
        row_string = " ".join(row_bits)
        print(i + 1, row_string)
    
    print("  a b c d e f g h")

def draw_pieces(screen,bitboards):

    # Draw the pieces
    for piece in bitboards:
        # Loop through each bit in the bitboard
        mask = 1
        for i in range(64):
            if bitboards[piece] & mask:
                # Calculate the row and column of the bit
                row = Dimension - 1 - i // Dimension
                col = i % Dimension
                # Flip the row and column indices to horizontally flip the board
                screen.blit(piece_images[piece], pygame.Rect(col*Sq_Size, row*Sq_Size, Sq_Size, Sq_Size))
            mask <<= 1

def highlightSqrs(screnn, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = find_row_col(sqSelected) 
        _index = sqSelected
        if gs.find_piece(_index) != None:
            if gs.find_piece(_index) == (gs.find_piece(_index).upper() if gs.color == 'w' else gs.find_piece(_index).lower()):
                s = pygame.Surface((Sq_Size, Sq_Size))
                s.set_alpha(100)
                s.fill(pygame.Color('red'))
                screnn.blit(s, (c*Sq_Size, abs(r - 7)*Sq_Size))
                s.fill(pygame.Color('yellow'))
                for move in validMoves:
                    if move[0] == _index:
                        screnn.blit(s, (Sq_Size*(find_row_col(move[1])[1]), Sq_Size*(abs(find_row_col(move[1])[0] - 7))))

def drawBoard(screen):
    global colors
    colors = [(240,217,181), (181,136,99)]
    for file in range(Dimension):
        for rank in range(Dimension):
            color = colors[((file + rank) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(rank*Sq_Size, file*Sq_Size, Sq_Size, Sq_Size))

def draw_game_state(screen, bitboard, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSqrs(screen, gs, validMoves, sqSelected)
    draw_pieces(screen, bitboard)
    
def find_row_col(bitboard):
    mask = 1

    for i in range(64):
        if bitboard & mask:
            row = i // 8
            col = i % 8
        mask <<= 1

    return row, col

def main():

    screen = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
    clock = pygame.time.Clock()
    screen.fill(pygame.Color("White"))

    moveMade = False
    MoveUndun = False

    running = True

    sqSelected = ()
    playerClicks = []

    gameOver = False

    playerOne = True
    playerTwo = False

    AIThinking = False
    MoveFinderProccess = None

    gs = Board()

    validMoves = gs.get_all_valid_moves()
    

    # Main game loop
    running = True
    while running:
        if gs.color == 'w' and playerOne:
            player_turn = True
        elif gs.color == 'b' and playerTwo:
            player_turn = True
        else:
            player_turn = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = pygame.mouse.get_pos()
                    file = location[0] // Sq_Size
                    rank = abs((location[1] // Sq_Size)-7)
                    
                    if sqSelected == (1 << (rank * 8 + file))  or file >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (1 <<  (rank * 8 + file))
                        if len(playerClicks) == 0 and gs.find_piece(1 <<  (rank * 8 + file)) == None:
                            continue
                        else:
                            playerClicks.append(1 <<  (rank * 8 + file))
                    if(len(playerClicks) == 2) and player_turn:
                        move = (playerClicks[0], playerClicks[1], gs.find_piece(playerClicks[0]))
                        for i in validMoves:
                            if move[0] == i[0] and move[1] == i[1] and move[2] == i[2]:
                                try:
                                    gs.make_move(i[0], i[1], i[2], i[3])
                                except:
                                    gs.make_move(i[0], i[1], i[2])
                                moveMade = True 
                                sqSelected = ()
                                playerClicks = []
                            if not moveMade:
                                playerClicks = [rank * 8 + file]

        if not player_turn and not gameOver and not MoveUndun:
            if not AIThinking:
                AIThinking = True
                print('Thinking. . .')
                AIMove = engine.findBestMove(gs, validMoves, False)
                if AIMove is None:
                    AIMove = engine.findRandomMove(validMoves)
                try:
                                    gs.make_move(AIMove[0], AIMove[1], AIMove[2], AIMove[3])
                except:
                                    gs.make_move(AIMove[0], AIMove[1], AIMove[2])
                print('current board evaluation:', engine.evaluate(gs) * .01)
                moveMade = True
                AIThinking = False
                MoveUndun = False 

                                


        if(moveMade):
            validMoves = gs.get_all_valid_moves()
            moveMade = False
        
        # Clear the screen
        screen.fill((0, 0, 0))
        if gs.checkmate:
            gameOver = True
            if gs.color == 'w':
                print('Black wins')
                gs.initialize_pieces()
                time.sleep(3)
                validMoves = gs.get_all_valid_moves()
                gameOver = False
            else:
                print('White wins')
                gs.initialize_pieces()
                time.sleep(3)
                validMoves = gs.get_all_valid_moves()
                gameOver = False
        elif gs.stalemate:
            gameOver = True
            print('game is stalemate', gs.bitboards['q'], gs.get_king_moves( 'w', gs.bitboards['K']), gs.get_queen_moves('b',gs.bitboards['q']))
            gs.initialize_pieces()
            time.sleep(3)
            validMoves = gs.get_all_valid_moves()
            gameOver = False

 

        # Display the board
        draw_game_state(screen, gs.bitboards, gs, validMoves, sqSelected)

        # Update the screen
        pygame.display.flip()

# Clean up Pygame
main()
pygame.quit()


