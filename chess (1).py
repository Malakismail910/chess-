import tkinter as tk
import copy
import random
import time
import chess

LIGHT = "#EEEED2"
DARK = "#769656"
HIGHLIGHT = "#BACA44"
MOVE_HINT = "#A9C46C"
BG = "#1E1E1E"  
SIDE = "#6B4A2D"

class ChessGame:
    def __init__(self, ai_level=2):
        self.root = tk.Tk()
        self.root.title("Chess")
        self.root.geometry("900x680")
        self.root.configure(bg=BG)

        self.square_size = 80
        self.ai_level = ai_level

        self.board = self.init_board()
        self.current_player = "white"
        self.selected_square = None
        self.possible_moves = []

        self.move_history = []
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_a_moved = False
        self.white_rook_h_moved = False
        self.black_rook_a_moved = False
        self.black_rook_h_moved = False
        self.last_pawn_double_move = None

        self.piece_values = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 100}
        self.piece_symbols = {
            'K': '♚', 'Q': '♛', 'R': '♜', 'B': '♝', 'N': '♞', 'P': '♟',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
        }

        self.setup_gui()
        self.update_board()

    def init_board(self):
        board = [[' '] * 8 for _ in range(8)]
        board[0] = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
        board[1] = ['p'] * 8
        board[6] = ['P'] * 8
        board[7] = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        return board

    def setup_gui(self):
        main = tk.Frame(self.root, bg=BG)
        main.pack(padx=20, pady=20)

        self.canvas = tk.Canvas(
            main,
            width=640,
            height=640,
            bg=BG,
            highlightthickness=0
        )
        self.canvas.grid(row=0, column=0)
        self.canvas.bind("<Button-1>", self.canvas_click)

        side = tk.Frame(main, bg=SIDE, width=200)
        side.grid(row=0, column=1, padx=20, sticky="n")

        self.add_side_buttons(side)

    def add_side_buttons(self, side_frame):
        self.add_button(side_frame, "🔄", self.reset_game)
        self.add_button(side_frame, "🤝", self.resign_game)
        self.add_button(side_frame, "💻", self.play_with_computer)

    def add_button(self, frame, text, command):
        button = tk.Button(
            frame, text=text, font=("Segoe UI Emoji", 26),
            bg=SIDE, relief="flat", command=command
        )
        button.pack(pady=25)

    def show_end_screen(self, title, message, emoji=""):
        end_win = tk.Toplevel(self.root)
        end_win.title(title)
        end_win.geometry("800x600")
        end_win.configure(bg=BG)

        end_win.attributes('-topmost', True)

        end_win.transient(self.root)
        end_win.grab_set()
        end_win.focus_force()
        end_win.lift()
        end_win.deiconify()

        emoji_label = tk.Label(end_win, text=emoji, font=("Segoe UI Emoji", 150), bg=BG, fg="#FFD700")
        emoji_label.pack(pady=60)

        msg_label = tk.Label(end_win, text=message, font=("Arial", 32, "bold"), bg=BG, fg="white", justify="center")
        msg_label.pack(expand=True, pady=30)

        ok_button = tk.Button(end_win, text="OK - New Game", font=("Arial", 24), width=15, height=2,
                              bg="#4CAF50", fg="white",
                              command=lambda: [end_win.destroy(), self.reset_game()])
        ok_button.pack(pady=60)

        end_win.update_idletasks()

    def resign_game(self):
        self.show_end_screen("You Resigned", "You gave up!\nAI Wins!", "🤝💔")
        self.disable_board()

    def disable_board(self):
        self.canvas.unbind("<Button-1>")

    def play_with_computer(self):
        print("Playing with the computer...")

    def reset_game(self):
        self.board = self.init_board()
        self.current_player = 'white'
        self.selected_square = None
        self.possible_moves = []
        self.move_history = []
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_a_moved = False
        self.white_rook_h_moved = False
        self.black_rook_a_moved = False
        self.black_rook_h_moved = False
        self.last_pawn_double_move = None
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.update_board()

    def canvas_click(self, event):
        c = event.x // self.square_size
        r = event.y // self.square_size

        if not (0 <= r < 8 and 0 <= c < 8):
            return

        if self.current_player != "white":
            return

        piece = self.board[r][c]

        if self.selected_square:
            if (r, c) in self.possible_moves:
                move_type = self.get_move_type(self.selected_square, (r, c))
                self.execute_move(self.selected_square, (r, c), move_type)
                self.clear_selection()
                self.update_board()

                if self.check_game_end():
                    return

                self.current_player = "black"
                self.root.after(300, self.ai_turn)
                return
            self.clear_selection()

        if piece != ' ' and piece.isupper():
            self.selected_square = (r, c)
            self.possible_moves = self.get_legal_moves(r, c)
            print(f"Selected: {self.piece_symbols.get(self.board[r][c], '?')} at ({r},{c}) - Moves: {self.possible_moves}")

        self.update_board()

    def clear_selection(self):
        self.selected_square = None
        self.possible_moves = []

    def update_board(self):
        self.canvas.delete("all")
        self.draw_board()
        self.draw_hints()
        self.draw_pieces()

    def draw_board(self):
        for r in range(8):
            for c in range(8):
                x1 = c * self.square_size
                y1 = r * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                color = LIGHT if (r + c) % 2 == 0 else DARK
                if self.selected_square == (r, c):
                    color = HIGHLIGHT

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

    def draw_hints(self):
        for r, c in self.possible_moves:
            x = c * self.square_size + 40
            y = r * self.square_size + 40
            self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill=MOVE_HINT, outline="")

    def draw_pieces(self):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != ' ':
                    color = "#B1ACAC" if piece.isupper() else "#111111"
                    self.canvas.create_text(c * self.square_size + 41, r * self.square_size + 43,
                                            text=self.piece_symbols[piece], font=("Segoe UI Emoji", 48), fill="black")
                    self.canvas.create_text(c * self.square_size + 40, r * self.square_size + 42,
                                            text=self.piece_symbols[piece], font=("Segoe UI Emoji", 48), fill=color)

    def ai_turn(self):
        self.root.update()
        time.sleep(0.5)
        depth = 1 + self.ai_level
        _, best_move = self.minimax(depth, float('-inf'), float('inf'), True)
        
        if best_move:
            move_type = self.get_move_type(best_move[0], best_move[1])
            self.execute_move(best_move[0], best_move[1], move_type)
            self.update_board()

        self.root.update_idletasks()
        self.root.after(200, self.force_check_game_end)

        if not self.check_game_end():
            self.current_player = 'white'

    def force_check_game_end(self):
        if self.check_game_end():
            return
        self.current_player = 'white'

    def is_valid_pos(self, r, c): 
        return 0 <= r < 8 and 0 <= c < 8
    
    def is_enemy(self, p1, p2): 
        return p1 != ' ' and p2 != ' ' and p1.isupper() != p2.isupper()
    
    def is_ally(self, p1, p2): 
        return p1 != ' ' and p2 != ' ' and p1.isupper() == p2.isupper()

    def get_possible_moves(self, r, c):
        piece = self.board[r][c]
        if piece == ' ': return []
        moves = []
        p = piece.lower()

        if p == 'p':
            d = -1 if piece.isupper() else 1
            start = 6 if piece.isupper() else 1
            if self.is_valid_pos(r+d, c) and self.board[r+d][c] == ' ': 
                moves.append((r+d, c))
                if r == start and self.is_valid_pos(r+2*d, c) and self.board[r+2*d][c] == ' ':
                    moves.append((r+2*d, c))
            for dc in [-1, 1]:
                nr, nc = r+d, c+dc
                if self.is_valid_pos(nr, nc) and self.is_enemy(piece, self.board[nr][nc]):
                    moves.append((nr, nc))
            
            if self.last_pawn_double_move:
                last_r, last_c = self.last_pawn_double_move
                expected_row = 4 if piece.isupper() else 3
                if r == expected_row and abs(c - last_c) == 1:
                    moves.append((r+d, last_c))
                    
        elif p == 'n':
            for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
                nr, nc = r+dr, c+dc
                if self.is_valid_pos(nr, nc) and not self.is_ally(piece, self.board[nr][nc]):
                    moves.append((nr, nc))
                    
        elif p in ['b','r','q']:
            dirs = []
            if p in ['b','q']: dirs += [(-1,-1),(-1,1),(1,-1),(1,1)]
            if p in ['r','q']: dirs += [(-1,0),(1,0),(0,-1),(0,1)]
            for dr, dc in dirs:
                nr, nc = r+dr, c+dc
                while self.is_valid_pos(nr, nc):
                    if self.board[nr][nc] == ' ': 
                        moves.append((nr, nc))
                    elif self.is_enemy(piece, self.board[nr][nc]): 
                        moves.append((nr, nc))
                        break
                    else: 
                        break
                    nr += dr
                    nc += dc
                    
        elif p == 'k':
            for dr in [-1,0,1]:
                for dc in [-1,0,1]:
                    if dr or dc:
                        nr, nc = r+dr, c+dc
                        if self.is_valid_pos(nr, nc) and not self.is_ally(piece, self.board[nr][nc]):
                            moves.append((nr, nc))
            
            if piece.isupper():
                if not self.white_king_moved and r==7 and c==4:
                    if (not self.white_rook_h_moved and self.board[7][5]==' ' and self.board[7][6]==' ' and
                        not self.is_square_attacked(7,4,False) and not self.is_square_attacked(7,5,False) and not self.is_square_attacked(7,6,False)):
                        moves.append((7,6))
                    if (not self.white_rook_a_moved and self.board[7][1]==' ' and self.board[7][2]==' ' and self.board[7][3]==' ' and
                        not self.is_square_attacked(7,4,False) and not self.is_square_attacked(7,3,False) and not self.is_square_attacked(7,2,False)):
                        moves.append((7,2))
            else:
                if not self.black_king_moved and r==0 and c==4:
                    if (not self.black_rook_h_moved and self.board[0][5]==' ' and self.board[0][6]==' ' and
                        not self.is_square_attacked(0,4,True) and not self.is_square_attacked(0,5,True) and not self.is_square_attacked(0,6,True)):
                        moves.append((0,6))
                    if (not self.black_rook_a_moved and self.board[0][1]==' ' and self.board[0][2]==' ' and self.board[0][3]==' ' and
                        not self.is_square_attacked(0,4,True) and not self.is_square_attacked(0,3,True) and not self.is_square_attacked(0,2,True)):
                        moves.append((0,2))
        
        return moves

    def get_move_type(self, from_pos, to_pos):
        fr, fc = from_pos
        tr, tc = to_pos
        piece = self.board[fr][fc]
        
        if piece.lower() == 'k' and abs(tc - fc) == 2:
            return 'castling'
        
        if piece.lower() == 'p' and tc != fc and self.board[tr][tc] == ' ':
            return 'en_passant'
        
        if piece.lower() == 'p':
            if (piece.isupper() and tr == 0) or (not piece.isupper() and tr == 7):
                return 'promotion'
        
        return 'normal'

    def execute_move(self, from_pos, to_pos, move_type):
        fr, fc = from_pos
        tr, tc = to_pos
        piece = self.board[fr][fc]
        
        self.last_pawn_double_move = None
        
        if move_type == 'castling':
            self.board[tr][tc] = self.board[fr][fc]
            self.board[fr][fc] = ' '
            if tc == 6:
                self.board[tr][5] = self.board[tr][7]
                self.board[tr][7] = ' '
            else:
                self.board[tr][3] = self.board[tr][0]
                self.board[tr][0] = ' '
        
        elif move_type == 'en_passant':
            self.board[tr][tc] = self.board[fr][fc]
            self.board[fr][fc] = ' '
            captured_row = fr
            self.board[captured_row][tc] = ' '
        
        elif move_type == 'promotion':
            self.board[tr][tc] = 'Q' if piece.isupper() else 'q'
            self.board[fr][fc] = ' '
        
        else:
            self.board[tr][tc] = self.board[fr][fc]
            self.board[fr][fc] = ' '
            
            if piece.lower() == 'p' and abs(tr - fr) == 2:
                self.last_pawn_double_move = (tr, tc)
        
        if piece == 'K':
            self.white_king_moved = True
        elif piece == 'k':
            self.black_king_moved = True
        elif piece == 'R':
            if fr == 7 and fc == 0: self.white_rook_a_moved = True
            elif fr == 7 and fc == 7: self.white_rook_h_moved = True
        elif piece == 'r':
            if fr == 0 and fc == 0: self.black_rook_a_moved = True
            elif fr == 0 and fc == 7: self.black_rook_h_moved = True

    def find_king(self, is_white):
        king = 'K' if is_white else 'k'
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == king:
                    return (r, c)
        return None

    def is_square_attacked(self, r, c, by_white):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != ' ' and piece.isupper() == by_white:
                    moves = self.get_basic_moves(row, col)
                    if (r, c) in moves:
                        return True
        return False

    def get_basic_moves(self, r, c):
        piece = self.board[r][c]
        if piece == ' ': return []
        moves = []
        p = piece.lower()

        if p == 'p':
            d = -1 if piece.isupper() else 1
            for dc in [-1, 1]:
                nr, nc = r + d, c + dc
                if self.is_valid_pos(nr, nc):
                    moves.append((nr, nc))
        elif p == 'n':
            for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
                nr, nc = r + dr, c + dc
                if self.is_valid_pos(nr, nc):
                    moves.append((nr, nc))
        elif p in ['b', 'r', 'q']:
            dirs = []
            if p in ['b', 'q']: dirs += [(-1,-1),(-1,1),(1,-1),(1,1)]
            if p in ['r', 'q']: dirs += [(-1,0),(1,0),(0,-1),(0,1)]
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                while self.is_valid_pos(nr, nc):
                    moves.append((nr, nc))
                    if self.board[nr][nc] != ' ':
                        break
                    nr += dr
                    nc += dc
        elif p == 'k':
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr or dc:
                        nr, nc = r + dr, c + dc
                        if self.is_valid_pos(nr, nc):
                            moves.append((nr, nc))
        return moves

    def is_in_check(self, is_white):
        king_pos = self.find_king(is_white)
        if not king_pos:
            return False
        return self.is_square_attacked(king_pos[0], king_pos[1], not is_white)

    def get_legal_moves(self, r, c):
        piece = self.board[r][c]
        if piece == ' ':
            return []
        
        possible = self.get_possible_moves(r, c)
        # مؤقتًا بنرجع possible عشان نختبر لو الحركات بتظهر
        return possible

    def evaluate_board_human_like(self):
        score = 0
        center = [(3,3),(3,4),(4,3),(4,4)]
        extended_center = [(2,2),(2,3),(2,4),(2,5),(3,2),(3,5),(4,2),(4,5),(5,2),(5,3),(5,4),(5,5)]
        
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p != ' ':
                    v = self.piece_values[p.lower()]
                    multiplier = -1 if p.isupper() else 1
                    score += v * multiplier
                    
                    if (r,c) in center: 
                        score += 0.3 * multiplier
                    elif (r,c) in extended_center:
                        score += 0.1 * multiplier
                    
                    if p.lower() in ['n','b']:
                        if p.islower() and r > 1:
                            score += 0.2
                        elif p.isupper() and r < 6:
                            score -= 0.2
                    
                    if p.lower() == 'k':
                        if p.islower() and r < 2:
                            score += 0.5
                        elif p.isupper() and r > 5:
                            score -= 0.5
                    
                    moves = self.get_possible_moves(r, c)
                    score += 0.05 * len(moves) * multiplier
        
        if self.is_in_check(True):
            score += 5
        if self.is_in_check(False):
            score -= 5
        
        if self.ai_level < 2:
            score += random.uniform(-0.3, 0.3)
        
        return score

    def get_all_moves(self, is_white):
        moves = []
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p != ' ' and p.isupper() == is_white:
                    legal = self.get_legal_moves(r, c)
                    for m in legal:
                        move_type = self.get_move_type((r,c), m)
                        moves.append(((r,c), m, move_type))
        return moves

    def minimax(self, depth, alpha, beta, maximizing):
        if depth == 0: 
            return self.evaluate_board_human_like(), None
        
        if maximizing:
            moves = self.get_all_moves(False)
            if not moves:
                if self.is_in_check(False):
                    return float('-inf'), None
                return 0, None
            
            max_eval = float('-inf')
            best_moves = []
            for move in moves:
                backup_board = copy.deepcopy(self.board)
                backup_last_move = self.last_pawn_double_move
                backup_flags = (self.white_king_moved, self.black_king_moved,
                              self.white_rook_a_moved, self.white_rook_h_moved,
                              self.black_rook_a_moved, self.black_rook_h_moved)
                
                self.execute_move(move[0], move[1], move[2])
                val, _ = self.minimax(depth-1, alpha, beta, False)
                
                self.board = backup_board
                self.last_pawn_double_move = backup_last_move
                (self.white_king_moved, self.black_king_moved,
                 self.white_rook_a_moved, self.white_rook_h_moved,
                 self.black_rook_a_moved, self.black_rook_h_moved) = backup_flags
                
                if val > max_eval: 
                    max_eval = val
                    best_moves = [move]
                elif val == max_eval: 
                    best_moves.append(move)
                    
                alpha = max(alpha, val)
                if beta <= alpha: 
                    break
            return max_eval, random.choice(best_moves) if best_moves else None
            
        else:
            moves = self.get_all_moves(True)
            if not moves:
                if self.is_in_check(True):
                    return float('inf'), None
                return 0, None
            
            min_eval = float('inf')
            best_moves = []
            for move in moves:
                backup_board = copy.deepcopy(self.board)
                backup_last_move = self.last_pawn_double_move
                backup_flags = (self.white_king_moved, self.black_king_moved,
                              self.white_rook_a_moved, self.white_rook_h_moved,
                              self.black_rook_a_moved, self.black_rook_h_moved)
                
                self.execute_move(move[0], move[1], move[2])
                val, _ = self.minimax(depth-1, alpha, beta, True)
                
                self.board = backup_board
                self.last_pawn_double_move = backup_last_move
                (self.white_king_moved, self.black_king_moved,
                 self.white_rook_a_moved, self.white_rook_h_moved,
                 self.black_rook_a_moved, self.black_rook_h_moved) = backup_flags
                
                if val < min_eval: 
                    min_eval = val
                    best_moves = [move]
                elif val == min_eval: 
                    best_moves.append(move)
                    
                beta = min(beta, val)
                if beta <= alpha: 
                    break
            return min_eval, random.choice(best_moves) if best_moves else None

    def check_game_end(self):
        white_king_count = sum(1 for row in self.board for cell in row if cell == 'K')
        black_king_count = sum(1 for row in self.board for cell in row if cell == 'k')
        
        if black_king_count == 0: 
            self.show_end_screen("You Win!", "Congratulations!\nYou captured the black king!", "🎉👑")
            self.disable_board()
            return True
            
        if white_king_count == 0: 
            self.show_end_screen("You Lost!", "Your king has been captured!\nAI Wins!", "💀🤖")
            self.disable_board()
            return True
        
        current_is_white = (self.current_player == 'white')
        moves = self.get_all_moves(current_is_white)
        
        if not moves:
            if self.is_in_check(current_is_white):
                if current_is_white:
                    self.show_end_screen("Checkmate!", "You have no legal moves!\nAI Wins!", "♔💀")
                else:
                    self.show_end_screen("You Win!", "Checkmate for the AI!\nCongratulations!", "🎉👑")
            else:
                self.show_end_screen("Draw!", "Stalemate!\nNo legal moves but not in check.", "🤝⚖️")
            self.disable_board()
            return True
        
        if self.is_insufficient_material():
            self.show_end_screen("Draw!", "Insufficient material!\nNo possible checkmate.", "🤝⚖️")
            self.disable_board()
            return True
        
        return False
    
    def is_insufficient_material(self):
        pieces = []
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p != ' ' and p.lower() != 'k':
                    pieces.append(p.lower())
        
        if len(pieces) == 0:
            return True
        
        if len(pieces) == 1 and pieces[0] in ['n', 'b']:
            return True
        
        if len(pieces) == 2 and pieces.count('b') == 2:
            bishops_pos = [(r, c) for r in range(8) for c in range(8) if self.board[r][c].lower() == 'b']
            if len(bishops_pos) == 2:
                color1 = (bishops_pos[0][0] + bishops_pos[0][1]) % 2
                color2 = (bishops_pos[1][0] + bishops_pos[1][1]) % 2
                if color1 == color2:
                    return True
        
        return False

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = ChessGame(ai_level=1)
    game.run()