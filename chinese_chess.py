#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国象棋
使用pygame实现的中国象棋游戏
"""

import pygame
import os
import sys
from enum import Enum

class PieceType(Enum):
    KING = '将'
    ADVISOR = '士'
    ELEPHANT = '象'
    HORSE = '马'
    CHARIOT = '车'
    CANNON = '炮'
    PAWN = '卒'

class Color(Enum):
    RED = '红'
    BLACK = '黑'

class Piece:
    def __init__(self, piece_type, color, x, y):
        self.piece_type = piece_type
        self.color = color
        self.x = x
        self.y = y

class ChineseChess:
    def __init__(self):
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

self.width = 600
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('中国象棋')
        self.clock = pygame.time.Clock()
        self.font = get_chinese_font(36)
        self.large_font = get_chinese_font(48)
        
        self.cell_size = 60
        self.board_offset_x = 30
        self.board_offset_y = 50
        
        self.selected_piece = None
        self.current_player = Color.RED
        self.game_over = False
        self.winner = None
        
        self.pieces = []
        self.init_pieces()
        
        self.colors = {
            'bg': (245, 222, 179),
            'board': (139, 69, 19),
            'red': (200, 0, 0),
            'black': (0, 0, 0),
            'highlight': (255, 255, 0),
            'selected': (0, 255, 0),
            'text': (50, 50, 50)
        }
    
    def init_pieces(self):
        piece_order = [PieceType.CHARIOT, PieceType.HORSE, PieceType.ELEPHANT, 
                      PieceType.ADVISOR, PieceType.KING, PieceType.ADVISOR,
                      PieceType.ELEPHANT, PieceType.HORSE, PieceType.CHARIOT]
        
        for i in range(9):
            self.pieces.append(Piece(piece_order[i], Color.BLACK, i, 0))
            self.pieces.append(Piece(piece_order[i], Color.RED, i, 9))
        
        self.pieces.append(Piece(PieceType.CANNON, Color.BLACK, 1, 2))
        self.pieces.append(Piece(PieceType.CANNON, Color.BLACK, 7, 2))
        self.pieces.append(Piece(PieceType.CANNON, Color.RED, 1, 7))
        self.pieces.append(Piece(PieceType.CANNON, Color.RED, 7, 7))
        
        for i in range(0, 9, 2):
            self.pieces.append(Piece(PieceType.PAWN, Color.BLACK, i, 3))
            self.pieces.append(Piece(PieceType.PAWN, Color.RED, i, 6))
    
    def get_piece_at(self, x, y):
        for piece in self.pieces:
            if piece.x == x and piece.y == y:
                return piece
        return None
    
    def is_valid_position(self, x, y):
        return 0 <= x < 9 and 0 <= y < 10
    
    def is_in_palace(self, x, y, color):
        if color == Color.RED:
            return 3 <= x <= 5 and 7 <= y <= 9
        return 3 <= x <= 5 and 0 <= y <= 2
    
    def is_valid_move(self, piece, to_x, to_y):
        if not self.is_valid_position(to_x, to_y):
            return False
        
        target = self.get_piece_at(to_x, to_y)
        if target and target.color == piece.color:
            return False
        
        dx = to_x - piece.x
        dy = to_y - piece.y
        
        if piece.piece_type == PieceType.KING:
            if abs(dx) + abs(dy) != 1:
                return False
            if not self.is_in_palace(to_x, to_y, piece.color):
                return False
        
        elif piece.piece_type == PieceType.ADVISOR:
            if abs(dx) != 1 or abs(dy) != 1:
                return False
            if not self.is_in_palace(to_x, to_y, piece.color):
                return False
        
        elif piece.piece_type == PieceType.ELEPHANT:
            if abs(dx) != 2 or abs(dy) != 2:
                return False
            mid_x = piece.x + dx // 2
            mid_y = piece.y + dy // 2
            if self.get_piece_at(mid_x, mid_y):
                return False
            if piece.color == Color.RED and to_y < 5:
                return False
            if piece.color == Color.BLACK and to_y > 4:
                return False
        
        elif piece.piece_type == PieceType.HORSE:
            if (abs(dx) == 2 and abs(dy) == 1) or (abs(dx) == 1 and abs(dy) == 2):
                if abs(dx) == 2:
                    mid_x = piece.x + dx // 2
                    if self.get_piece_at(mid_x, piece.y):
                        return False
                else:
                    mid_y = piece.y + dy // 2
                    if self.get_piece_at(piece.x, mid_y):
                        return False
            else:
                return False
        
        elif piece.piece_type == PieceType.CHARIOT:
            if dx != 0 and dy != 0:
                return False
            if dx == 0:
                step = 1 if dy > 0 else -1
                for y in range(piece.y + step, to_y, step):
                    if self.get_piece_at(piece.x, y):
                        return False
            else:
                step = 1 if dx > 0 else -1
                for x in range(piece.x + step, to_x, step):
                    if self.get_piece_at(x, piece.y):
                        return False
        
        elif piece.piece_type == PieceType.CANNON:
            if dx != 0 and dy != 0:
                return False
            pieces_between = 0
            if dx == 0:
                step = 1 if dy > 0 else -1
                for y in range(piece.y + step, to_y, step):
                    if self.get_piece_at(piece.x, y):
                        pieces_between += 1
            else:
                step = 1 if dx > 0 else -1
                for x in range(piece.x + step, to_x, step):
                    if self.get_piece_at(x, piece.y):
                        pieces_between += 1
            if target:
                if pieces_between != 1:
                    return False
            else:
                if pieces_between != 0:
                    return False
        
        elif piece.piece_type == PieceType.PAWN:
            if piece.color == Color.RED:
                if piece.y <= 4 and dy > 0:
                    if abs(dx) + abs(dy) != 1:
                        return False
                else:
                    if dy > 0:
                        return False
                    if abs(dx) + abs(dy) != 1:
                        return False
            else:
                if piece.y >= 5 and dy < 0:
                    if abs(dx) + abs(dy) != 1:
                        return False
                else:
                    if dy < 0:
                        return False
                    if abs(dx) + abs(dy) != 1:
                        return False
        
        return True
    
    def get_valid_moves(self, piece):
        moves = []
        for x in range(9):
            for y in range(10):
                if self.is_valid_move(piece, x, y):
                    moves.append((x, y))
        return moves
    
    def make_move(self, from_x, from_y, to_x, to_y):
        piece = self.get_piece_at(from_x, from_y)
        if not piece:
            return False
        
        target = self.get_piece_at(to_x, to_y)
        
        if self.is_valid_move(piece, to_x, to_y):
            if target:
                if target.piece_type == PieceType.KING:
                    self.game_over = True
                    self.winner = piece.color
                self.pieces.remove(target)
            
            piece.x = to_x
            piece.y = to_y
            
            self.current_player = Color.BLACK if self.current_player == Color.RED else Color.RED
            return True
        return False
    
    def draw_board(self):
        self.screen.fill(self.colors['bg'])
        
        for i in range(10):
            start_x = self.board_offset_x
            end_x = self.board_offset_x + 8 * self.cell_size
            y = self.board_offset_y + i * self.cell_size
            pygame.draw.line(self.screen, self.colors['board'], 
                          (start_x, y), (end_x, y), 2)
        
        for i in range(9):
            x = self.board_offset_x + i * self.cell_size
            top_y = self.board_offset_y
            bottom_y = self.board_offset_y + 9 * self.cell_size
            pygame.draw.line(self.screen, self.colors['board'], 
                          (x, top_y), (x, bottom_y), 2)
        
        palace_points = [
            (3, 0), (5, 0), (4, 1), (3, 2), (5, 2),
            (3, 7), (5, 7), (4, 8), (3, 9), (5, 9)
        ]
        for x, y in palace_points:
            cx = self.board_offset_x + x * self.cell_size
            cy = self.board_offset_y + y * self.cell_size
            pygame.draw.circle(self.screen, self.colors['board'], (cx, cy), 3)
        
        river_text = self.large_font.render('楚  河        汉  界', True, self.colors['board'])
        text_rect = river_text.get_rect(center=(self.width // 2, self.board_offset_y + 4.5 * self.cell_size))
        self.screen.blit(river_text, text_rect)
    
    def draw_pieces(self):
        for piece in self.pieces:
            x = self.board_offset_x + piece.x * self.cell_size
            y = self.board_offset_y + piece.y * self.cell_size
            
            if self.selected_piece == piece:
                pygame.draw.circle(self.screen, self.colors['selected'], (x, y), 28, 3)
            
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 25)
            pygame.draw.circle(self.screen, self.colors['board'], (x, y), 25, 2)
            
            piece_color = self.colors['red'] if piece.color == Color.RED else self.colors['black']
            text = self.font.render(piece.piece_type.value, True, piece_color)
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
    
    def draw_valid_moves(self):
        if self.selected_piece:
            valid_moves = self.get_valid_moves(self.selected_piece)
            for x, y in valid_moves:
                cx = self.board_offset_x + x * self.cell_size
                cy = self.board_offset_y + y * self.cell_size
                pygame.draw.circle(self.screen, self.colors['highlight'], (cx, cy), 8, 2)
    
    def draw_ui(self):
        if not self.game_over:
            turn_text = '当前回合：{}方'.format('红' if self.current_player == Color.RED else '黑')
            text = self.font.render(turn_text, True, self.colors['text'])
            self.screen.blit(text, (20, 10))
        else:
            winner_text = '游戏结束！{}方获胜！'.format('红' if self.winner == Color.RED else '黑')
            text = self.large_font.render(winner_text, True, self.colors['red'])
            text_rect = text.get_rect(center=(self.width // 2, 30))
            self.screen.blit(text, text_rect)
            
            restart_text = self.font.render('按 R 重新开始', True, self.colors['text'])
            restart_rect = restart_text.get_rect(center=(self.width // 2, self.height - 30))
            self.screen.blit(restart_text, restart_rect)
    
    def handle_click(self, pos):
        if self.game_over:
            return
        
        x = (pos[0] - self.board_offset_x + self.cell_size // 2) // self.cell_size
        y = (pos[1] - self.board_offset_y + self.cell_size // 2) // self.cell_size
        
        if not self.is_valid_position(x, y):
            return
        
        clicked_piece = self.get_piece_at(x, y)
        
        if self.selected_piece:
            if clicked_piece and clicked_piece.color == self.current_player:
                self.selected_piece = clicked_piece
            else:
                if self.make_move(self.selected_piece.x, self.selected_piece.y, x, y):
                    self.selected_piece = None
        else:
            if clicked_piece and clicked_piece.color == self.current_player:
                self.selected_piece = clicked_piece
    
    def reset_game(self):
        self.pieces = []
        self.init_pieces()
        self.selected_piece = None
        self.current_player = Color.RED
        self.game_over = False
        self.winner = None
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        self.reset_game()
            
            self.draw_board()
            self.draw_valid_moves()
            self.draw_pieces()
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == '__main__':
    game = ChineseChess()
    game.run()
