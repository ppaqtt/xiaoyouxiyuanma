#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数织（Nonogram）- 逻辑解谜游戏
根据行列提示填充格子
"""

import pygame
import random

pygame.init()

WIDTH, HEIGHT = 900, 700
CELL_SIZE = 30
GRID_SIZES = {
    "简单(5x5)": 5,
    "中等(8x8)": 8,
    "困难(10x10)": 10,
}

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 100)
RED = (255, 50, 50)
BLUE = (0, 100, 200)
YELLOW = (255, 200, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("数织（Nonogram）- 逻辑解谜")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 50)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

class Nonogram:
    def __init__(self, size):
        self.size = size
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.player_grid = [[None for _ in range(size)] for _ in range(size)]
        self.row_hints = []
        self.col_hints = []
        self.generate_puzzle()
    
    def generate_puzzle(self):
        for y in range(self.size):
            row = [random.randint(0, 1) for _ in range(self.size)]
            self.grid[y] = row
        
        self.row_hints = [self.get_line_hints(row) for row in self.grid]
        
        for x in range(self.size):
            col = [self.grid[y][x] for y in range(self.size)]
            self.col_hints.append(self.get_line_hints(col))
    
    def get_line_hints(self, line):
        hints = []
        count = 0
        for cell in line:
            if cell == 1:
                count += 1
            elif count > 0:
                hints.append(count)
                count = 0
        if count > 0:
            hints.append(count)
        return hints if hints else [0]
    
    def check_win(self):
        return self.player_grid == self.grid

def draw_nonogram(game, offset_x, offset_y, selected=None):
    cell_size = min(30, 600 // game.size)
    
    max_row_hint = max(len(h) for h in game.row_hints)
    max_col_hint = max(len(h) for h in game.col_hints)
    
    header_size = max_row_hint * 20 + 10
    v_header_size = max_col_hint * 20 + 10
    
    for y in range(game.size):
        for x in range(game.size):
            px = offset_x + v_header_size + x * cell_size
            py = offset_y + header_size + y * cell_size
            
            pygame.draw.rect(screen, WHITE, (px, py, cell_size, cell_size), 1)
            
            if game.player_grid[y][x] == True:
                pygame.draw.rect(screen, BLACK, (px + 2, py + 2, cell_size - 4, cell_size - 4))
            elif game.player_grid[y][x] == False:
                pygame.draw.line(screen, RED, (px + 5, py + 5), (px + cell_size - 5, py + cell_size - 5), 2)
                pygame.draw.line(screen, RED, (px + cell_size - 5, py + 5), (px + 5, py + cell_size - 5), 2)
    
    for y, hints in enumerate(game.row_hints):
        hint_x = offset_x + v_header_size - max_row_hint * 20 - 5
        for i, hint in enumerate(hints):
            text = font_small.render(str(hint), True, BLUE)
            screen.blit(text, (hint_x + i * 20, offset_y + header_size + y * cell_size + 5))
    
    for x, hints in enumerate(game.col_hints):
        hint_y = offset_y + header_size - max_col_hint * 20 - 5
        for i, hint in enumerate(hints):
            text = font_small.render(str(hint), True, BLUE)
            screen.blit(text, (offset_x + v_header_size + x * cell_size + 10, hint_y + i * 20))
    
    if selected:
        sx, sy = selected
        px = offset_x + v_header_size + sx * cell_size
        py = offset_y + header_size + sy * cell_size
        pygame.draw.rect(screen, YELLOW, (px, py, cell_size, cell_size), 3)

def nonogram_game():
    size = 8
    game = Nonogram(size)
    selected = None
    completed_count = 0
    
    while True:
        screen.fill(BLACK)
        
        title = font_large.render("数织（Nonogram）", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
        
        offset_x = (WIDTH - (max(len(game.col_hints) * 30 + 100, 400))) // 2
        offset_y = 100
        
        draw_nonogram(game, offset_x, offset_y, selected)
        
        instructions = [
            "规则:",
            "• 左键填充(X)",
            "• 右键标记(.)",
            "• 数字表示连续黑格数",
            "",
            f"完成度: {completed_count}/{game.size * game.size}"
        ]
        
        for i, line in enumerate(instructions):
            text = font_small.render(line, True, WHITE)
            screen.blit(text, (20, 100 + i * 25))
        
        pygame.draw.rect(screen, (50, 50, 70), (WIDTH - 220, 100, 200, 300))
        controls = [
            "操作:",
            "R - 重新开始",
            "1 - 简单5x5",
            "2 - 中等8x8",
            "3 - 困难10x10",
            "",
            "目标:",
            "根据行列数字",
            "推理出所有黑格"
        ]
        
        for i, line in enumerate(controls):
            text = font_small.render(line, True, WHITE)
            screen.blit(text, (WIDTH - 210, 110 + i * 25))
        
        if game.check_win():
            win_text = font_large.render("🎉 恭喜通关！", True, GREEN)
            screen.blit(win_text, (WIDTH // 2 - 120, HEIGHT - 100))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game = Nonogram(size)
                    selected = None
                elif event.key == pygame.K_1:
                    size = 5
                    game = Nonogram(size)
                    selected = None
                elif event.key == pygame.K_2:
                    size = 8
                    game = Nonogram(size)
                    selected = None
                elif event.key == pygame.K_3:
                    size = 10
                    game = Nonogram(size)
                    selected = None
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                cell_size = min(30, 600 // game.size)
                max_row_hint = max(len(h) for h in game.row_hints)
                max_col_hint = max(len(h) for h in game.col_hints)
                header_size = max_row_hint * 20 + 10
                v_header_size = max_col_hint * 20 + 10
                
                gx = (mx - offset_x - v_header_size) // cell_size
                gy = (my - offset_y - header_size) // cell_size
                
                if 0 <= gx < game.size and 0 <= gy < game.size:
                    selected = (gx, gy)
                    
                    if event.button == 1:
                        game.player_grid[gy][gx] = True
                    elif event.button == 3:
                        game.player_grid[gy][gx] = False
        
        completed_count = sum(1 for y in range(game.size) for x in range(game.size) 
                             if game.player_grid[y][x] == game.grid[y][x])
        
        clock.tick(60)

if __name__ == "__main__":
    nonogram_game()
