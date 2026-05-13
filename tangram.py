#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
七巧板拼图 - 传统益智游戏
用七块几何图形拼出目标图案
"""

import pygame
import math

pygame.init()

WIDTH, HEIGHT = 900, 700

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 100)
RED = (255, 50, 50)
BLUE = (0, 100, 200)
YELLOW = (255, 200, 0)
PURPLE = (150, 50, 200)
ORANGE = (255, 150, 0)
PINK = (255, 200, 200)
CYAN = (0, 200, 200)
GRAY = (150, 150, 150)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("七巧板拼图 - 传统益智")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 50)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

class TangramPiece:
    def __init__(self, points, color, name):
        self.points = points
        self.original_points = points[:]
        self.color = color
        self.name = name
        self.center_x = sum(p[0] for p in points) / len(points)
        self.center_y = sum(p[1] for p in points) / len(points)
        self.x = 0
        self.y = 0
        self.rotation = 0
        self.selected = False
        self.locked = False
    
    def get_screen_points(self):
        cos_r = math.cos(math.radians(self.rotation))
        sin_r = math.sin(math.radians(self.rotation))
        
        result = []
        for px, py in self.points:
            rx = (px - self.center_x) * cos_r - (py - self.center_y) * sin_r + self.center_x + self.x
            ry = (px - self.center_x) * sin_r + (py - self.center_y) * cos_r + self.center_y + self.y
            result.append((rx, ry))
        return result
    
    def contains_point(self, mx, my):
        points = self.get_screen_points()
        n = len(points)
        inside = False
        
        j = n - 1
        for i in range(n):
            xi, yi = points[i]
            xj, yj = points[j]
            
            if ((yi > my) != (yj > my)) and (mx < (xj - xi) * (my - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        
        return inside
    
    def draw(self):
        points = self.get_screen_points()
        
        if self.selected:
            pygame.draw.polygon(screen, WHITE, points, 3)
        
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, BLACK, points, 2)
        
        name_text = font_small.render(self.name, True, BLACK)
        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)
        screen.blit(name_text, (cx - 10, cy - 8))

class TangramGame:
    def __init__(self):
        self.pieces = []
        self.target_area_x = WIDTH // 2 - 150
        self.target_area_y = 100
        self.target_width = 300
        self.target_height = 300
        self.current_level = 0
        self.rotation_speed = 5
        self.setup_pieces()
        self.setup_levels()
        self.dragging = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
    
    def setup_pieces(self):
        size = 50
        self.pieces = [
            TangramPiece([
                (0, 0), (size * 2, 0), (size, size)
            ], RED, "大三角1"),
            
            TangramPiece([
                (0, 0), (size * 2, 0), (size, size)
            ], BLUE, "大三角2"),
            
            TangramPiece([
                (0, 0), (size, 0), (size * 0.5, size * 0.5), (0, size)
            ], GREEN, "中三角"),
            
            TangramPiece([
                (0, 0), (size, 0), (size * 0.5, size * 0.5), (0, size)
            ], YELLOW, "小三角1"),
            
            TangramPiece([
                (0, 0), (size, 0), (size * 0.5, size * 0.5), (0, size)
            ], PURPLE, "小三角2"),
            
            TangramPiece([
                (0, 0), (size, 0), (size, size), (0, size)
            ], ORANGE, "正方形"),
            
            TangramPiece([
                (0, 0), (size * 2, 0), (size * 2, size), (size, size), (size, size * 0.5), (0, size * 0.5)
            ], PINK, "平行四边形"),
        ]
        
        start_x = 50
        start_y = 450
        spacing = 110
        
        for i, piece in enumerate(self.pieces):
            piece.x = start_x + (i % 4) * spacing
            piece.y = start_y + (i // 4) * 110
            piece.rotation = random.choice([0, 90, 180, 270])
    
    def setup_levels(self):
        self.levels = [
            {
                "name": "正方形",
                "hint": "把所有碎片拼成正方形",
                "target_points": [
                    (self.target_area_x, self.target_area_y),
                    (self.target_area_x + self.target_width, self.target_area_y),
                    (self.target_area_x + self.target_width, self.target_area_y + self.target_height),
                    (self.target_area_x, self.target_area_y + self.target_height)
                ]
            },
            {
                "name": "三角形",
                "hint": "拼成一个大三角形",
                "target_points": [
                    (self.target_area_x, self.target_area_y + self.target_height),
                    (self.target_area_x + self.target_width // 2, self.target_area_y),
                    (self.target_area_x + self.target_width, self.target_area_y + self.target_height)
                ]
            },
            {
                "name": "平行四边形",
                "hint": "拼成平行四边形",
                "target_points": [
                    (self.target_area_x + 50, self.target_area_y),
                    (self.target_area_x + self.target_width - 50, self.target_area_y),
                    (self.target_area_x + self.target_width, self.target_area_y + self.target_height),
                    (self.target_area_x + 100, self.target_area_y + self.target_height)
                ]
            }
        ]
    
    def check_placement(self):
        placed_count = 0
        in_area_count = 0
        
        for piece in self.pieces:
            if piece.x > self.target_area_x and \
               piece.x < self.target_area_x + self.target_width and \
               piece.y > self.target_area_y and \
               piece.y < self.target_area_y + self.target_height:
                in_area_count += 1
                
                if abs(piece.rotation % 90) < 10 or abs(piece.rotation % 90 - 360) < 10:
                    placed_count += 1
        
        return in_area_count == len(self.pieces), placed_count == len(self.pieces)
    
    def draw_target_area(self):
        if self.current_level < len(self.levels):
            level = self.levels[self.current_level]
            
            pygame.draw.rect(screen, (200, 200, 200), 
                           (self.target_area_x, self.target_area_y, 
                            self.target_width, self.target_height), 3)
            
            hint_text = font_small.render(f"目标: {level['name']}", True, BLUE)
            screen.blit(hint_text, (self.target_area_x, self.target_area_y - 30))
            
            desc_text = font_small.render(level['hint'], True, GRAY)
            screen.blit(desc_text, (self.target_area_x, self.target_area_y - 55))
    
    def draw(self):
        self.draw_target_area()
        
        for piece in self.pieces:
            piece.draw()
        
        pygame.draw.rect(screen, BLACK, (0, HEIGHT - 80, WIDTH, 80))
        
        instructions = [
            f"关卡 {self.current_level + 1}/{len(self.levels)}",
            "←→旋转碎片 | 鼠标拖动",
            "R 重置碎片位置"
        ]
        
        for i, text in enumerate(instructions):
            t = font_small.render(text, True, WHITE)
            screen.blit(t, (20 + i * 300, HEIGHT - 50))

def tangram_game():
    game = TangramGame()
    
    while True:
        screen.fill(WHITE)
        
        title = font_large.render("七巧板拼图", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))
        
        game.draw()
        
        complete, perfect = game.check_placement()
        
        if perfect and game.current_level < len(game.levels) - 1:
            complete_text = font_large.render("🎉 完成! 按空格进入下一关", True, GREEN)
            screen.blit(complete_text, (WIDTH // 2 - 180, HEIGHT // 2))
        elif perfect and game.current_level == len(game.levels) - 1:
            win_text = font_large.render("🏆 全部通关! 恭喜!", True, YELLOW)
            screen.blit(win_text, (WIDTH // 2 - 150, HEIGHT // 2))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    for piece in game.pieces:
                        piece.x = 0
                        piece.y = 0
                        piece.rotation = random.choice([0, 90, 180, 270])
                    game.setup_pieces()
                
                elif event.key == pygame.K_LEFT:
                    if game.dragging:
                        game.dragging.rotation -= game.rotation_speed
                
                elif event.key == pygame.K_RIGHT:
                    if game.dragging:
                        game.dragging.rotation += game.rotation_speed
                
                elif event.key == pygame.K_SPACE:
                    if complete and game.current_level < len(game.levels) - 1:
                        game.current_level += 1
                        for piece in game.pieces:
                            piece.x = 0
                            piece.y = 0
                        game.setup_pieces()
                
                elif event.key == pygame.K_1:
                    if game.dragging:
                        game.dragging.rotation = 0
                elif event.key == pygame.K_2:
                    if game.dragging:
                        game.dragging.rotation = 90
                elif event.key == pygame.K_3:
                    if game.dragging:
                        game.dragging.rotation = 180
                elif event.key == pygame.K_4:
                    if game.dragging:
                        game.dragging.rotation = 270
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                for piece in reversed(game.pieces):
                    if piece.contains_point(mx, my):
                        game.dragging = piece
                        game.drag_offset_x = mx - piece.x
                        game.drag_offset_y = my - piece.y
                        game.pieces.remove(piece)
                        game.pieces.append(piece)
                        piece.selected = True
                        break
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if game.dragging:
                    game.dragging.selected = False
                    game.dragging = None
            
            elif event.type == pygame.MOUSEMOTION:
                if game.dragging:
                    mx, my = event.pos
                    game.dragging.x = mx - game.drag_offset_x
                    game.dragging.y = my - game.drag_offset_y
        
        clock.tick(60)

if __name__ == "__main__":
    tangram_game()
