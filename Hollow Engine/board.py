import numpy as np

class Board ():
  
  #Rook
  #Knight
  #Bishop
  #King
  #Queen
  #Pawn

  def __init__(self):
    
    # Create an array of zeros with the same shape as a bitboard
    self.bitboard = np.zeros((8, 8), dtype=np.uint64)

    # Convert the array to a dictionary of bitboards
    self.bitboards = {
      'P': np.uint64(self.bitboard),
      'N': np.uint64(self.bitboard),
      'B': np.uint64(self.bitboard),
      'R': np.uint64(self.bitboard),
      'Q': np.uint64(self.bitboard),
      'K': np.uint64(self.bitboard),
      'p': np.uint64(self.bitboard),
      'n': np.uint64(self.bitboard),
      'b': np.uint64(self.bitboard),
      'r': np.uint64(self.bitboard),
      'q': np.uint64(self.bitboard),
      'k': np.uint64(self.bitboard)
    }

    self.occupied_squares = 0
    self.occupied_white_sqaures = 0
    self.occupied_black_sqaures = 0
    self.attacked_white_sqaures = 0
    self.attacked_black_sqaures = 0

    self.move_log = []

    self.white_casltes = [True, True]
    self.black_casltes = [True, True]

    #self.initialize_pieces()
    self.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

    self.color = "w"

    self.checkmate = False
    self.stalemate = False



  def initialize_pieces(self):
    #White pieces
    self.bitboards['R'] = 1 << 0 | 1 << 7
    self.bitboards['N'] = 1 << 1 | 1 << 6
    self.bitboards['B'] = 1 << 2 | 1 << 5
    self.bitboards['Q'] = 1 << 3
    self.bitboards['K'] = 1 << 4
    self.bitboards['P'] = (1 << 8) | (1 << 9) | (1 << 10) | (1 << 11) | (1 << 12) | (1 << 13) | (1 << 14) | (1 << 15)

    # Black pieces
    self.bitboards['r'] = 1 << 56 | 1 << 63
    self.bitboards['n'] = 1 << 57 | 1 << 62
    self.bitboards['b'] = 1 << 58 | 1 << 61
    self.bitboards['q'] = 1 << 59
    self.bitboards['k'] = 1 << 60
    self.bitboards['p'] = (1 << 48) | (1 << 49) | (1 << 50) | (1 << 51) | (1 << 52) | (1 << 53) | (1 << 54) | (1 << 55)

    self.update_occupied_sqaures()

    # Set the active color according to the color component of the FEN string
    self.color = 'w'
    self.update_caslte_rights()
    # Update the occupied squares and attacked bitboards
    self.update_attacked_occupied_sqaures()

  'works completely'
  def load_fen(self, fen):
    # Split the FEN string into its different components
    position, color, _, _, _, _ = fen.split()

    # Initialize the board
    self.bitboards = {
        'P': 0,
        'N': 0,
        'B': 0,
        'R': 0,
        'Q': 0,
        'K': 0,
        'p': 0,
        'n': 0,
        'b': 0,
        'r': 0,
        'q': 0,
        'k': 0
    }

    # Set the pieces on the board according to the position component of the FEN string
    rank = 7
    file = 0
    for c in position:
        if c == '/':
            rank -= 1
            file = 0
        elif c.isdigit():
            file += int(c)
        else:
            self.bitboards[c] |= 1 << (rank * 8 + file)
            file += 1

    # Set the active color according to the color component of the FEN string
    self.color = color

    # Update the occupied squares and attacked bitboards
    self.update_caslte_rights()
    self.update_attacked_occupied_sqaures()
  
  def find_piece(self, square):
    for piece in self.bitboards:
        if square & self.bitboards[piece]:
            return piece
    return None

  def generate_attackbitmap(self, bitboard, piece, color, return_position=False):
    piece_moves = {
      'p' : self.get_pawn_moves,
      'q' : self.get_queen_moves,
      'b' : self.get_bishop_moves,
      'n' : self.get_knight_moves,
      'r' : self.get_rook_moves,
      'k' : self.get_king_moves
    }
    file_a = 0x4040404040404040
    file_h = 0x0101010101010101

    # Initialize an empty bitboard for the total moves
    total_moves = 0

    # Set a mask with only the least significant bit set to 1
    mask = 1
    # Loop until the bitboard is empty
    for i in range(64):
        # Check if the least significant bit is set
        if bitboard & mask:
              total_moves |= piece_moves[piece.lower()](color, bitboard & mask)

        mask <<= 1

    if return_position == False:
      return total_moves
    else:
      return bitboard, total_moves, piece

  def get_square_index(self, row, col):
    # Calculate the index in the bitboard
    index = np.uint64(self.bitboard)
    index = 1 << (row * 8 + col)
    return index

  def update_caslte_rights(self):
    if self.color == 'w' and (self.white_casltes[0] or self.white_casltes[1]):
      if self.bitboards['K'] != 16:
        self.white_casltes = (False, False)
      else:
        if not self.bitboards['R'] & 1:
          print('white queen is false')
          self.white_casltes[0] = False
        if not self.bitboards['R'] & 128:
          self.white_casltes[1] = False
    elif self.color == 'b' and (self.black_casltes[0] or self.black_casltes[1]):
      if self.bitboards['k'] != 1152921504606846976:
        self.black_casltes = (False, False)
      else:
        if not self.bitboards['r'] & 72057594037927936:
          self.black_casltes[0] = False
        if not self.bitboards['r'] & 9223372036854775808:
          self.black_casltes[1] = False

  def generate_caslte_moves(self):
    self.update_caslte_rights()
    self.update_attacked_occupied_sqaures()

    moves = []

    if self.color == 'w':
      if self.white_casltes[0] != False:
        if not self.attacked_black_sqaures & 12 and not self.occupied_white_sqaures & 14:
          moves.append((16, 4, 'K', True))
      if self.white_casltes[1] != False:
        if not self.attacked_black_sqaures & 96 and not self.occupied_white_sqaures & 96:
          moves.append((16, 64, 'K', True))
    else:
      if self.black_casltes[0] != False:
        if not self.attacked_white_sqaures & 864691128455135232 and not self.occupied_black_sqaures & 1008806316530991104:
          moves.append((1152921504606846976, 288230376151711744, 'k', True))
      if self.white_casltes[1] != False:
        if not self.attacked_white_sqaures & 6917529027641081856 and not self.occupied_black_sqaures & 6917529027641081856:
          moves.append((1152921504606846976, 4611686018427387904, 'k', True))

    return moves

  def make_move(self, current_position, move, piece_name, caslte=False):

    king_bitboard = self.bitboards['k'] | self.bitboards['K']

    if current_position & king_bitboard and move & 4899916394579099716:
      caslte = True

    piece_captured = None

    enemy_occupied_sqaures = self.occupied_black_sqaures if self.color == 'w' else self.occupied_white_sqaures

    mask = ~current_position
    if caslte == False:

      if move & enemy_occupied_sqaures:
        piece_captured = self.find_piece(move)
        self.bitboards[self.find_piece(move)] &= ~move
      
      if piece_name == 'P' and move & 0xff00000000000000:

        self.bitboards[piece_name] &= mask

        self.bitboards['Q'] |= move

        piece_name = piece_name + 'Q'

      elif piece_name == 'p' and move & 0x00000000000000ff:

        self.bitboards[piece_name] &= mask

        self.bitboards['q'] |= move

        piece_name = piece_name + 'q'

      else:

        self.bitboards[piece_name] &= mask

        self.bitboards[piece_name] |= move
    else:
      print('is king move')
      if move == 4:
        self.bitboards[piece_name] &= mask
        self.bitboards[piece_name] |= move

        self.bitboards['R'] &= ~1

        self.bitboards['R'] |= 8
      if move == 64:
        print('castling king side white')
        self.bitboards[piece_name] &= mask
        self.bitboards[piece_name] |= move

        self.bitboards['R'] &= ~128 

        self.bitboards['R'] |= 32
      if move == 288230376151711744:

        self.bitboards[piece_name] &= mask
        self.bitboards[piece_name] |= move

        self.bitboards['r'] &= ~72057594037927936

        self.bitboards['r'] |= 576460752303423488
      if move == 4611686018427387904:
        self.bitboards[piece_name] &= mask
        self.bitboards[piece_name] |= move

        self.bitboards['r'] &= ~9223372036854775808 

        self.bitboards['r'] |= 2305843009213693952

    self.move_log.append((current_position, move, piece_name, piece_captured, caslte))
    # Clear the bit in the current position bitboard

    self.color = 'w' if self.color == 'b' else 'b'

    self.update_attacked_occupied_sqaures()

  def undo_move(self):
    if len(self.move_log) > 0:
      # Get the last move from the log
      current_position, move, piece_name, piece_captured, castle = self.move_log.pop()
      # Clear the bit in the move bitboard
      mask = ~move
      if castle != True:
        if len(piece_name) > 1:
          self.bitboards[piece_name[1]] &= mask
          piece_name = piece_name[:-1]

        # Update the piece's bitboard
        self.bitboards[piece_name] &= mask
        self.bitboards[piece_name] |= current_position
        
        if piece_captured != None:
          self.bitboards[piece_captured] |= move
      else:
        if move == 4:
          self.white_casltes[0] = True
          self.bitboards[piece_name] &= mask

          self.bitboards[piece_name] |= current_position
          self.bitboards['R'] &= ~8

          self.bitboards['R'] |= 1
        if move == 64:
          self.white_casltes[1] = True
          self.bitboards[piece_name] &= mask

          self.bitboards[piece_name] |= current_position

          self.bitboards['R'] &= ~32

          self.bitboards['R'] |= 1
        if move == 288230376151711744:
          self.black_casltes[0] = True
          self.bitboards[piece_name] &= mask

          self.bitboards[piece_name] |= current_position

          self.bitboards['r'] &= ~576460752303423488 

          self.bitboards['r'] |= 72057594037927936
        if move == 4611686018427387904:
          self.black_casltes[1] = True
          self.bitboards[piece_name] &= mask

          self.bitboards[piece_name] |= current_position

          self.bitboards['r'] &= ~2305843009213693952

          self.bitboards['r'] |= 9223372036854775808
      
      # Update the occupied squares bitboard
      self.checkmate = False
      self.stalemate = False
      self.update_attacked_occupied_sqaures()
      self.color = 'w' if self.color == 'b' else 'b'

    else:
      # There are no moves to undo
      print("There are no moves to undo.")

  def get_all_posible_moves(self, color):
    moves = []
    piece_names = ['p', 'r', 'b', 'k', 'q', 'n']
    for piece in piece_names:
      if color == 'w':
        mask = 1
        # Loop until the bitboard is empty
        for i in range(64):
            # Check if the least significant bit is set
            if self.bitboards[piece.upper()] & mask:
              moves.append(self.generate_attackbitmap(self.bitboards[piece.upper()] & mask, piece.upper(), 'w', True))

            mask <<= 1

      elif color == 'b':
        mask = 1
        # Loop until the bitboard is empty
        for i in range(64):
            # Check if the least significant bit is set
            if self.bitboards[piece] & mask:
              moves.append(self.generate_attackbitmap(self.bitboards[piece] & mask, piece, 'b', True))

            mask <<= 1
    return moves

  def get_all_valid_moves(self):
    all_moves = self.get_all_posible_moves(self.color)
    valid_moves = []
    for move in all_moves:
        current_position = move[0]
        piece_name = move[2]
        move_bitboard = move[1]
        if move_bitboard != 0:
          mask = 1
          for i in range(64):
          # Check if the least significant bit is set
            if move_bitboard & mask:
              self.make_move(current_position, move_bitboard & mask, piece_name)
              self.color = 'w' if self.color == 'b' else 'b'
              if not self.in_check(self.color):
                  valid_moves.append((current_position, move_bitboard & mask, piece_name))
              self.color = 'w' if self.color == 'b' else 'b'
              self.undo_move()
    
            mask <<= 1
    
    if not self.in_check(self.color):
      castle_moves = self.generate_caslte_moves()
      for m in castle_moves:
        valid_moves.append(m)

    if(len(valid_moves) == 0):
            if(self.in_check(self.color)):
                self.checkmate = True
            else:
                self.stalemate = True
    return valid_moves

  def in_check(self, color):
    self.update_attacked_sqaures()
    if color == 'w':
      return True if self.bitboards['K'] & self.attacked_black_sqaures else False
    else:
      return True if self.bitboards['k'] & self.attacked_white_sqaures else False

  ###BOARD UPDATES###
  def update_attacked_occupied_sqaures(self):
    self.update_occupied_sqaures()

    self.update_attacked_sqaures()
  def update_occupied_sqaures(self):
    
    self.occupied_squares = 0
    self.occupied_white_sqaures = 0
    self.occupied_black_sqaures = 0

    for piece in self.bitboards:
      self.occupied_squares |= self.bitboards[piece]
      if piece.isupper():
        self.occupied_white_sqaures |= self.bitboards[piece]

      elif piece.islower():
        self.occupied_black_sqaures |= self.bitboards[piece]
  def update_attacked_sqaures(self):
    self.attacked_white_sqaures = 0
    self.attacked_black_sqaures = 0

    for piece in self.bitboards:
      if piece.isupper():
        self.attacked_white_sqaures |= self.generate_attackbitmap(self.bitboards[piece], piece, 'w')

      elif piece.islower():
        self.attacked_black_sqaures |= self.generate_attackbitmap(self.bitboards[piece], piece, 'b')
  ###BOARD UPDATES###

  ###PIECE MOVES###
  'add castling, en passants, queen promotion'
  def get_pawn_moves(self, color, position_bitboard):
    # Get the bitboard for the pawns of the given color
    self.update_occupied_sqaures()

    rank_8 = 0xff00000000000000
    rank_1 = 0x00000000000000ff
    file_a = 0x101010101010101
    file_h = 0x8080808080808080


    # Initialize an empty list of moves
    moves = 0 #np.uint64(self.bitboard)

    

    # Check if the pawn is white or black
    if color == "w":
      # Check if the pawn is on the starting row
      if position_bitboard & 0x00000000000ff00:
        # Check if the square two rows ahead is empty
        shifted_bitboard = position_bitboard << 8
        if not (self.occupied_squares & shifted_bitboard):
          moves |= (position_bitboard << 8)
          shifted_bitboard = position_bitboard << 16
          if not (self.occupied_squares & shifted_bitboard):
            moves |= (position_bitboard << 16)
        # Check if the square one row ahead is empty
      else:
        # Check if the square one row ahead is empty if pawn not on starting row
        shifted_bitboard = position_bitboard << 8
        if not (self.occupied_squares & shifted_bitboard):
          moves |= (position_bitboard << 8)
      
      # Check if the pawn can capture diagonally
      shifted_bitboard = position_bitboard << 7
      shifted_bitboard2 = position_bitboard << 9
      if self.occupied_squares & shifted_bitboard:
        # Check if the square to the upper left is occupied by a black piece
        if self.occupied_black_sqaures & shifted_bitboard and not position_bitboard & file_a:
          moves |= (position_bitboard << 7)
      if  self.occupied_squares & shifted_bitboard2:
        # Check if the square to the upper right is occupied by a black piece
        if self.occupied_black_sqaures & shifted_bitboard2 and not position_bitboard & file_h:
          moves |= ((position_bitboard << 9))
      

    # Repeat the same process for black pawns

    else:
      if position_bitboard & 0xff000000000000:
        shifted_bitboard = position_bitboard >> 8
        if not (self.occupied_squares & shifted_bitboard):
          moves |= (position_bitboard >> 8)
          shifted_bitboard = position_bitboard >> 16
          if not (self.occupied_squares & shifted_bitboard):
            moves |= (position_bitboard >> 16)
      else:
        shifted_bitboard = position_bitboard >> 8
        if not (self.occupied_squares & shifted_bitboard):
          moves |= (position_bitboard >> 8)
      shifted_bitboard = position_bitboard >> 7
      shifted_bitboard2 = position_bitboard >> 9
      if self.occupied_squares & shifted_bitboard:
        # Check if the square to the upper left is occupied by a black piece
        if self.occupied_white_sqaures & shifted_bitboard and not position_bitboard & file_h:
          moves |= (position_bitboard >> 7)
      if  self.occupied_squares & shifted_bitboard2 and not position_bitboard & file_a:
        # Check if the square to the upper right is occupied by a black piece
        if self.occupied_white_sqaures & shifted_bitboard2:
          moves |= ((position_bitboard >> 9))
  
    # Return the list of moves
    return moves
  def get_knight_moves(self, color, position_bitboard):
    # Get the bitboard for the knight's current position

    # Initialize an empty bitboard for the knight's moves
    moves = 0

    # Define bitboards for the ranks and files
    rank_8_7 = 0xffff000000000000
    rank_8 = 0xff00000000000000
    rank_1_2 = 0x000000000000ffff
    rank_1 = 0x000000000000ff
    file_a = 0x101010101010101
    file_a_b = 0x303030303030303
    file_h = 0x8080808080808080
    file_h_g = 0xc0c0c0c0c0c0c0c0
    
    friendly_occupied_sqaures = self.occupied_white_sqaures if color == 'w' else self.occupied_black_sqaures

    #shift to left
    if not position_bitboard & file_a_b:
      if not position_bitboard & rank_8:
        moves |= (position_bitboard << 6) & ~friendly_occupied_sqaures
      if not position_bitboard & rank_1:
        moves |= (position_bitboard >> 10) & ~friendly_occupied_sqaures
    #shift to right
    if not position_bitboard & file_h_g:
      if not position_bitboard & rank_1:
        moves |= (position_bitboard >> 6) & ~friendly_occupied_sqaures
      if not position_bitboard & rank_8:
        moves |= (position_bitboard << 10) & ~friendly_occupied_sqaures
    #shift down
    if not position_bitboard & rank_1_2:
      if not position_bitboard & file_a:
        moves |= (position_bitboard >> 17) & ~friendly_occupied_sqaures
      if not position_bitboard & file_h:
        moves |= (position_bitboard >> 15) & ~friendly_occupied_sqaures
    #shift up
    if not position_bitboard & rank_8_7:
      if not position_bitboard & file_a:
        moves |= (position_bitboard << 15) & ~friendly_occupied_sqaures
      if not position_bitboard & file_h:
        moves |= (position_bitboard << 17) & ~friendly_occupied_sqaures
    

    # Remove any illegal moves that would take the knight to a square occupied by a friendly piece
    if color == "w":
        moves &= ~self.occupied_white_sqaures
    else:
        moves &= ~self.occupied_black_sqaures

    return moves
  def get_bishop_moves(self, color, position_bitboard):
    # Get the bitboard for the bishop's position
    self.update_occupied_sqaures()
    original_position_bitboard = position_bitboard

    moves = 0

    rank_8 = 0xff00000000000000
    rank_1 = 0x00000000000000ff
    file_a = 0x101010101010101
    file_h = 0x8080808080808080

    enemy_occupied_sqaures = self.occupied_black_sqaures if color == 'w' else self.occupied_white_sqaures
    friendly_occupied_sqaures = self.occupied_white_sqaures if color == 'w' else self.occupied_black_sqaures
    #diagonal 1 or north east
    while not position_bitboard & rank_8 and not position_bitboard & file_h:
      position_bitboard <<= 9
      if position_bitboard & enemy_occupied_sqaures:
        moves |= position_bitboard
        break
      elif position_bitboard & friendly_occupied_sqaures:
        break
      moves |= position_bitboard
    

    position_bitboard =  original_position_bitboard
    #diagonal 2 or south east
    while not position_bitboard & rank_1 and not position_bitboard & file_h:
      position_bitboard >>= 7
      if position_bitboard & enemy_occupied_sqaures:
        moves |= position_bitboard
        break
      elif position_bitboard & friendly_occupied_sqaures:
        break
      moves |= position_bitboard

    position_bitboard =  original_position_bitboard
    #diagonal 2 or south east
    while not position_bitboard & rank_8 and not position_bitboard & file_a:

      position_bitboard <<= 7
      if position_bitboard & enemy_occupied_sqaures:
        moves |= position_bitboard
        break
      elif position_bitboard & friendly_occupied_sqaures:
        break
      moves |= position_bitboard
    
    position_bitboard =  original_position_bitboard
    #diagonal 2 or south east
    while not position_bitboard & rank_1 and not position_bitboard & file_a:

      position_bitboard >>= 9
      if position_bitboard & enemy_occupied_sqaures:
        moves |= position_bitboard
        break
      elif position_bitboard & friendly_occupied_sqaures:
        break
      moves |= position_bitboard

    # Return the final bitboard containing the bishop's legal moves
    return moves
  def get_rook_moves(self, color, position_bitboard):

    # Get the bitboard for the bishop's position
    self.update_occupied_sqaures()
    original_position_bitboard = position_bitboard

    moves = 0

    rank_8 = 0xff00000000000000
    rank_1 = 0x00000000000000ff
    file_a = 0x101010101010101
    file_h = 0x8080808080808080

    enemy_occupied_sqaures = self.occupied_black_sqaures if color == 'w' else self.occupied_white_sqaures
    friendly_occupied_sqaures = self.occupied_white_sqaures if color == 'w' else self.occupied_black_sqaures
    #diagonal 1 or north east
    while not position_bitboard & rank_8:
      position_bitboard <<= 8
      if position_bitboard & enemy_occupied_sqaures:
        moves |= position_bitboard
        break
      elif position_bitboard & friendly_occupied_sqaures:
        break
      moves |= position_bitboard
    

    position_bitboard = original_position_bitboard
    #diagonal 2 or south east
    while not position_bitboard & rank_1:
      position_bitboard >>= 8
      if position_bitboard & enemy_occupied_sqaures:
        moves |= position_bitboard
        break
      elif position_bitboard & friendly_occupied_sqaures:
        break
      moves |= position_bitboard

    position_bitboard = original_position_bitboard
    #diagonal 2 or south east
    while not position_bitboard & file_h:
      position_bitboard <<= 1
      if position_bitboard & enemy_occupied_sqaures:
        moves |= position_bitboard
        break
      elif position_bitboard & friendly_occupied_sqaures:
        break
      moves |= position_bitboard
    
    position_bitboard = original_position_bitboard
    #diagonal 2 or south east
    while not position_bitboard & file_a:
      position_bitboard >>= 1
      if position_bitboard & enemy_occupied_sqaures:
        moves |= position_bitboard
        break
      elif position_bitboard & friendly_occupied_sqaures:
        break
      moves |= position_bitboard

    # Return the final bitboard containing the bishop's legal moves
    return moves
  def get_queen_moves(self, color, position_bitboard):
    return self.get_bishop_moves(color, position_bitboard) | self.get_rook_moves(color, position_bitboard)
  def get_king_moves(self, color, position_bitboard):

    rank_8 = 0xff00000000000000
    rank_1 = 0x00000000000000ff
    file_a = 0x101010101010101
    file_h = 0x8080808080808080

    self.update_occupied_sqaures()

    enemy_attcked_sqaures = self.attacked_black_sqaures if color == 'w' else self.attacked_white_sqaures
    friendly_occupied_sqaures = self.occupied_white_sqaures if color == 'w' else self.occupied_black_sqaures

    moves = 0
    
    if not position_bitboard & rank_1:
        moves |= (position_bitboard >> 8) & ~friendly_occupied_sqaures
        if not position_bitboard & file_a:
          moves |= (position_bitboard >> 9) &  ~friendly_occupied_sqaures
        if not position_bitboard & file_h:
          moves |= (position_bitboard >> 7) &  ~friendly_occupied_sqaures
    if not position_bitboard & rank_8:
        moves |= (position_bitboard << 8) & ~friendly_occupied_sqaures
        if not position_bitboard & file_h:
          moves |= (position_bitboard << 9) &  ~friendly_occupied_sqaures
        if not position_bitboard & file_a:
          moves |= (position_bitboard << 7) &  ~friendly_occupied_sqaures
    if not position_bitboard & file_h:
        moves |= (position_bitboard << 1) &  ~friendly_occupied_sqaures
    if not position_bitboard & file_a:
        moves |= (position_bitboard >> 1) &  ~friendly_occupied_sqaures

    return moves
  ###PIECE MOVES###





  