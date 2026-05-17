#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版国际象棋
使用pygame制作
操作说明：
- 鼠标左键点击选中棋子
- 再点击目标位置移动
- 支持玩家vs玩家或玩家vs简单AI
"""

import pygame
import os
import sys
import random

# 初始化pygame
pygame.init()



# 尝试使用中文字体
def get_chinese_font(size):
    """获取支持中文的字体"""
    font_names = [
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
        "/System/Library/Fonts/PingFang.ttc",  # macOS
    ]
    for font_name in font_names:
        if os.path.exists(font_name):
            try:
                return pygame.font.Font(font_name, size)
            except:
                continue
    return get_chinese_font(size)

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (76, 175, 80)
DARK_GREEN = (56, 142, 60)
HIGHLIGHT = (255, 235, 59)
SELECTED = (33, 150, 243)
GRAY = (158, 158, 158)

# 窗口大小
WIDTH, HEIGHT = 640, 700
ROWS, COLS = 8, 8
CELL_SIZE = 80

# 棋子缩写：王(K), 后(Q), 车(R), 象(B), 马(N), 兵(P)
PIECES = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
    'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
}

# 初始化棋盘
def init_board():
    board = [
        ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
        ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    ]
    return board

class ChessGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('简化版国际象棋')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('segoeuisymbol', 60)
        self.small_font = pygame.font.SysFont('simhei', 24)
        self.board = init_board()
        self.selected = None
        self.current_player = 'white'  # 当前玩家
        self.game_mode = 'pvp'  # pvp或pvc
        self.game_over = False
        self.winner = None
        self.turn_count = 0

    def draw_board(self):
        for row in range(ROWS):
            for col in range(COLS):
                color = GREEN if (row + col) % 2 == 0 else DARK_GREEN
                pygame.draw.rect(self.screen, color, 
                                (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def draw_pieces(self):
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece:
                    text = self.font.render(PIECES.get(piece, piece), True, WHITE if piece.isupper() else BLACK)
                    x = col * CELL_SIZE + CELL_SIZE // 2 - text.get_width() // 2
                    y = row * CELL_SIZE + CELL_SIZE // 2 - text.get_height() // 2
                    self.screen.blit(text, (x, y))

    def draw_selected(self):
        if self.selected:
            row, col = self.selected
            pygame.draw.rect(self.screen, SELECTED, 
                            (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 4)
            moves = self.get_valid_moves(row, col)
            for move_row, move_col in moves:
                pygame.draw.circle(self.screen, HIGHLIGHT, 
                                  (move_col * CELL_SIZE + CELL_SIZE // 2, 
                                   move_row * CELL_SIZE + CELL_SIZE // 2), 15, 5)

    def get_piece_color(self, piece):
        if not piece:
            return None
        return 'white' if piece.isupper() else 'black'

    def is_valid_position(self, row, col):
        return 0 <= row < ROWS and 0 <= col < COLS

    def get_valid_moves(self, row, col):
        piece = self.board[row][col]
        if not piece:
            return []
        color = self.get_piece_color(piece)
        moves = []
        piece_type = piece.lower()
        
        # 简化版移动规则
        if piece_type == 'p':  # 兵
            direction = -1 if color == 'white' else 1
            if self.is_valid_position(row + direction, col) and not self.board[row + direction][col]:
                moves.append((row + direction, col))
                start_row = 6 if color == 'white' else 1
                if row == start_row and not self.board[row + 2 * direction][col]:
                    moves.append((row + 2 * direction, col))
            for dc in [-1, 1]:
                nr, nc = row + direction, col + dc
                if self.is_valid_position(nr, nc):
                    target = self.board[nr][nc]
                    if target and self.get_piece_color(target) != color:
                        moves.append((nr, nc))
        elif piece_type == 'r':  # 车
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = row + dr, col + dc
                while self.is_valid_position(nr, nc):
                    target = self.board[nr][nc]
                    if not target:
                        moves.append((nr, nc))
                    else:
                        if self.get_piece_color(target) != color:
                            moves.append((nr, nc))
                        break
                    nr += dr
                    nc += dc
        elif piece_type == 'n':  # 马
            for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                          (1, -2), (1, 2), (2, -1), (2, 1)]:
                nr, nc = row + dr, col + dc
                if self.is_valid_position(nr, nc):
                    target = self.board[nr][nc]
                    if not target or self.get_piece_color(target) != color:
                        moves.append((nr, nc))
        elif piece_type == 'b':  # 象
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nr, nc = row + dr, col + dc
                while self.is_valid_position(nr, nc):
                    target = self.board[nr][nc]
                    if not target:
                        moves.append((nr, nc))
                    else:
                        if self.get_piece_color(target) != color:
                            moves.append((nr, nc))
                        break
                    nr += dr
                    nc += dc
        elif piece_type == 'q':  # 后
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1),
                          (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nr, nc = row + dr, col + dc
                while self.is_valid_position(nr, nc):
                    target = self.board[nr][nc]
                    if not target:
                        moves.append((nr, nc))
                    else:
                        if self.get_piece_color(target) != color:
                            moves.append((nr, nc))
                        break
                    nr += dr
                    nc += dc
        elif piece_type == 'k':  # 王
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1),
                          (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nr, nc = row + dr, col + dc
                if self.is_valid_position(nr, nc):
                    target = self.board[nr][nc]
                    if not target or self.get_piece_color(target) != color:
                        moves.append((nr, nc))
        return moves

    def make_move(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        captured = self.board[to_row][to_col]
        
        if captured and captured.lower() == 'k':
            self.game_over = True
            self.winner = self.current_player
            
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = ''
        
        # 兵升变
        if piece.lower() == 'p' and (to_row == 0 or to_row == 7):
            self.board[to_row][to_col] = 'Q' if piece.isupper() else 'q'
        
        self.current_player = 'black' if self.current_player == 'white' else 'white'
        self.turn_count += 1

    def ai_move(self):
        pieces = []
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece and self.get_piece_color(piece) == 'black':
                    moves = self.get_valid_moves(row, col)
                    if moves:
                        pieces.append((row, col, moves))
        if pieces:
            from_row, from_col, moves = random.choice(pieces)
            to_row, to_col = random.choice(moves)
            self.make_move(from_row, from_col, to_row, to_col)

    def draw_ui(self):
        pygame.draw.rect(self.screen, GRAY, (0, HEIGHT - 60, WIDTH, 60))
        status = f"当前回合: {'白方' if self.current_player == 'white' else '黑方'}"
        text = self.small_font.render(status, True, BLACK)
        self.screen.blit(text, (10, HEIGHT - 50))
        if self.game_over:
            winner_text = f"游戏结束! {'白方' if self.winner == 'white' else '黑方'}获胜!"
            text = self.small_font.render(winner_text, True, (255, 0, 0))
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 50))

    def handle_click(self, pos):
        if self.game_over:
            self.__init__()
            return
            
        x, y = pos
        col = x // CELL_SIZE
        row = y // CELL_SIZE
        
        if y >= HEIGHT - 60:
            return
            
        if self.selected:
            from_row, from_col = self.selected
            valid_moves = self.get_valid_moves(from_row, from_col)
            if (row, col) in valid_moves:
                self.make_move(from_row, from_col, row, col)
                self.selected = None
                if self.game_mode == 'pvc' and not self.game_over and self.current_player == 'black':
                    self.ai_move()
            else:
                piece = self.board[row][col]
                if piece and self.get_piece_color(piece) == self.current_player:
                    self.selected = (row, col)
                else:
                    self.selected = None
        else:
            piece = self.board[row][col]
            if piece and self.get_piece_color(piece) == self.current_player:
                self.selected = (row, col)

    def run(self):
        running = True
        while running:
            self.screen.fill(BLACK)
            self.draw_board()
            self.draw_selected()
            self.draw_pieces()
            self.draw_ui()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())
                    
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = ChessGame()
    print("=== 简化版国际象棋 ===")
    print("操作说明：")
    print("- 鼠标左键点击选中棋子")
    print("- 再点击目标位置移动")
    print("- 默认玩家vs玩家模式")
    game.run()
