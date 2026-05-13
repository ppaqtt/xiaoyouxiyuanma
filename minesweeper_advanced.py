#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫雷高级版 - 益智游戏
多种难度和模式
"""

import pygame
import random

pygame.init()

WIDTH, HEIGHT = 900, 700

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 100)
RED = (255, 50, 50)
BLUE = (0, 100, 200)
YELLOW = (255, 200, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("扫雷高级版 - 益智游戏")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 50)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

DIFFICULTIES = {
    "简单": {"width": 9, "height": 9, "mines": 10},
    "中等": {"width": 16, "height": 16, "mines": 40},
    "困难": {"width": 20, "height": 15, "mines": 75},
    "噩梦": {"width": 25, "height": 20, "mines": 150},
}

class Minesweeper:
    def __init__(self, difficulty):
        self.diff = DIFFICULTIES[difficulty]
        self.width = self.diff["width"]
        self.height = self.diff["height"]
        self.mines = self.diff["mines"]
        
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.revealed = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.flagged = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.game_over = False
        self.won = False
        self.first_click = True
        self.time = 0
        self.flags_used = 0
        
        self.cell_size = min(30, 600 // max(self.width, self.height))
        self.offset_x = (WIDTH - self.width * self.cell_size) // 2
        self.offset_y = 100
    
    def place_mines(self, exclude_x, exclude_y):
        count = 0
        while count < self.mines:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            if abs(x - exclude_x) <= 1 and abs(y - exclude_y) <= 1:
                continue
            
            if self.board[y][x] != -1:
                self.board[y][x] = -1
                count += 1
        
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == -1:
                    continue
                
                count = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if self.board[ny][nx] == -1:
                                count += 1
                self.board[y][x] = count
    
    def reveal(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        
        if self.revealed[y][x] or self.flagged[y][x]:
            return
        
        self.revealed[y][x] = True
        
        if self.board[y][x] == -1:
            self.game_over = True
            return
        
        if self.board[y][x] == 0:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    self.reveal(x + dx, y + dy)
    
    def flag(self, x, y):
        if self.revealed[y][x]:
            return
        
        self.flagged[y][x] = not self.flagged[y][x]
        self.flags_used += 1 if self.flagged[y][x] else -1
    
    def check_win(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] != -1 and not self.revealed[y][x]:
                    return False
        self.won = True
        return True
    
    def draw(self):
        for y in range(self.height):
            for x in range(self.width):
                px = self.offset_x + x * self.cell_size
                py = self.offset_y + y * self.cell_size
                
                if self.game_over and self.board[y][x] == -1:
                    pygame.draw.rect(screen, RED, (px, py, self.cell_size - 2, self.cell_size - 2))
                    continue
                
                if self.revealed[y][x]:
                    pygame.draw.rect(screen, DARK_GRAY, (px, py, self.cell_size - 2, self.cell_size - 2))
                    
                    if self.board[y][x] > 0:
                        colors = [BLACK, BLUE, GREEN, RED, PURPLE, ORANGE, YELLOW, BLACK]
                        text = font_small.render(str(self.board[y][x]), True, colors[self.board[y][x] - 1])
                        screen.blit(text, (px + self.cell_size // 3, py + self.cell_size // 4))
                else:
                    pygame.draw.rect(screen, GRAY, (px, py, self.cell_size - 2, self.cell_size - 2))
                    pygame.draw.rect(screen, WHITE, (px, py, self.cell_size - 2, self.cell_size - 2), 2)
                    
                    if self.flagged[y][x]:
                        text = font_small.render("🚩", True, RED)
                        screen.blit(text, (px, py))
        
        for i in range(self.width + 1):
            x = self.offset_x + i * self.cell_size
            pygame.draw.line(screen, BLACK, (x, self.offset_y), 
                           (x, self.offset_y + self.height * self.cell_size), 1)
        
        for i in range(self.height + 1):
            y = self.offset_y + i * self.cell_size
            pygame.draw.line(screen, BLACK, (self.offset_x, y),
                           (self.offset_x + self.width * self.cell_size, y), 1)

def minesweeper_advanced():
    difficulty = "中等"
    game = Minesweeper(difficulty)
    timer_event = pygame.USEREVENT + 1
    pygame.time.set_timer(timer_event, 1000)
    
    while True:
        screen.fill(WHITE)
        
        title = font_large.render("扫雷高级版", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))
        
        pygame.draw.rect(screen, BLACK, (0, 60, WIDTH, 35))
        
        diff_text = font_medium.render(f"难度: {difficulty}", True, WHITE)
        screen.blit(diff_text, (20, 65))
        
        mine_count = game.mines - game.flags_used
        mine_text = font_medium.render(f"💣: {mine_count}", True, RED)
        screen.blit(mine_text, (200, 65))
        
        time_text = font_medium.render(f"⏱️: {game.time}", True, WHITE)
        screen.blit(time_text, (400, 65))
        
        diff_buttons = [
            ("简单", "E"),
            ("中等", "M"),
            ("困难", "H"),
            ("噩梦", "N")
        ]
        
        for i, (name, key) in enumerate(diff_buttons):
            bx = 600 + i * 70
            by = 65
            bw, bh = 60, 25
            
            color = GREEN if name == difficulty else GRAY
            pygame.draw.rect(screen, color, (bx, by, bw, bh), border_radius=5)
            
            text = font_small.render(f"{name}({key})", True, BLACK if name == difficulty else WHITE)
            screen.blit(text, (bx + 5, by + 3))
        
        game.draw()
        
        if game.won:
            win_text = font_large.render("🎉 恭喜通关!", True, GREEN)
            screen.blit(win_text, (WIDTH // 2 - 120, HEIGHT // 2 + 50))
        elif game.game_over:
            lose_text = font_large.render("💀 游戏结束", True, RED)
            screen.blit(lose_text, (WIDTH // 2 - 100, HEIGHT // 2 + 50))
        
        instructions = [
            "操作:",
            "左键 - 翻开格子",
            "右键 - 标记地雷",
            "E/M/H/N - 切换难度",
            "R - 重新开始"
        ]
        
        pygame.draw.rect(screen, (50, 50, 70), (10, HEIGHT - 180, 200, 170))
        
        for i, line in enumerate(instructions):
            text = font_small.render(line, True, WHITE)
            screen.blit(text, (20, HEIGHT - 170 + i * 28))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            elif event.type == timer_event:
                if not game.game_over and not game.won and not game.first_click:
                    game.time += 1
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game = Minesweeper(difficulty)
                elif event.key == pygame.K_e:
                    difficulty = "简单"
                    game = Minesweeper(difficulty)
                elif event.key == pygame.K_m:
                    difficulty = "中等"
                    game = Minesweeper(difficulty)
                elif event.key == pygame.K_h:
                    difficulty = "困难"
                    game = Minesweeper(difficulty)
                elif event.key == pygame.K_n:
                    difficulty = "噩梦"
                    game = Minesweeper(difficulty)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                for i, (name, key) in enumerate(diff_buttons):
                    bx = 600 + i * 70
                    by = 65
                    bw, bh = 60, 25
                    
                    if bx <= mx <= bx + bw and by <= my <= by + bh:
                        difficulty = name
                        game = Minesweeper(difficulty)
                
                gx = (mx - game.offset_x) // game.cell_size
                gy = (my - game.offset_y) // game.cell_size
                
                if 0 <= gx < game.width and 0 <= gy < game.height:
                    if event.button == 1:
                        if game.first_click:
                            game.place_mines(gx, gy)
                            game.first_click = False
                        game.reveal(gx, gy)
                        if not game.game_over:
                            game.check_win()
                    elif event.button == 3:
                        game.flag(gx, gy)
        
        clock.tick(60)

if __name__ == "__main__":
    minesweeper_advanced()
