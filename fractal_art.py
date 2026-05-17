#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分形艺术生成器
使用pygame实现的分形图案生成游戏
"""

import pygame
import os
import sys
import math

class FractalArt:
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

self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('分形艺术生成器')
        self.clock = pygame.time.Clock()
        self.font = get_chinese_font(28)
        self.large_font = get_chinese_font(36)
        
        self.canvas = pygame.Surface((600, 500))
        self.canvas.fill((240, 240, 240))
        
        self.current_fractal = 0
        self.fractal_names = ['曼德博集合', '朱利亚集合', '分形树', '谢尔宾斯基三角形', '科赫雪花']
        self.max_iter = 100
        self.zoom = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.color_mode = 0
        self.animating = False
        self.anim_time = 0
        
        self.colors = {
            'bg': (245, 245, 250),
            'panel': (255, 255, 255),
            'text': (30, 30, 30),
            'button': (100, 150, 255),
            'button_hover': (130, 180, 255),
        }
        
        self.buttons = [
            {'text': '上一个', 'x': 630, 'y': 50, 'w': 150, 'h': 40, 'action': 'prev'},
            {'text': '下一个', 'x': 630, 'y': 100, 'w': 150, 'h': 40, 'action': 'next'},
            {'text': '放大', 'x': 630, 'y': 150, 'w': 70, 'h': 40, 'action': 'zoom_in'},
            {'text': '缩小', 'x': 710, 'y': 150, 'w': 70, 'h': 40, 'action': 'zoom_out'},
            {'text': '换色', 'x': 630, 'y': 200, 'w': 150, 'h': 40, 'action': 'color'},
            {'text': '动画', 'x': 630, 'y': 250, 'w': 150, 'h': 40, 'action': 'animate'},
            {'text': '重置', 'x': 630, 'y': 300, 'w': 150, 'h': 40, 'action': 'reset'},
            {'text': '保存', 'x': 630, 'y': 350, 'w': 150, 'h': 40, 'action': 'save'},
        ]
        
        self.hovered_button = None
        self.needs_render = True
    
    def get_color(self, iteration, max_iter):
        if iteration == max_iter:
            return (0, 0, 0)
        
        t = iteration / max_iter
        if self.color_mode == 0:
            r = int(255 * t)
            g = int(255 * (1 - abs(2 * t - 1)))
            b = int(255 * (1 - t))
        elif self.color_mode == 1:
            r = int(128 + 127 * math.sin(t * math.pi))
            g = int(128 + 127 * math.sin(t * math.pi + 2))
            b = int(128 + 127 * math.sin(t * math.pi + 4))
        elif self.color_mode == 2:
            r = int(255 * t)
            g = int(255 * t ** 2)
            b = int(255 * math.sqrt(t))
        elif self.color_mode == 3:
            r = int(255 * (0.5 + 0.5 * math.cos(t * 6.28)))
            g = int(255 * (0.5 + 0.5 * math.cos(t * 6.28 + 2.09)))
            b = int(255 * (0.5 + 0.5 * math.cos(t * 6.28 + 4.18)))
        else:
            g = int(255 * t)
            r = int(g * 0.8)
            b = int(g * 0.5)
        
        return (r, g, b)
    
    def render_mandelbrot(self):
        for x in range(600):
            for y in range(500):
                zx = 0
                zy = 0
                cx = (x - 300) / (150 * self.zoom) + self.offset_x - 0.5
                cy = (y - 250) / (150 * self.zoom) + self.offset_y
                
                iteration = 0
                while zx * zx + zy * zy < 4 and iteration < self.max_iter:
                    tmp = zx * zx - zy * zy + cx
                    zy = 2 * zx * zy + cy
                    zx = tmp
                    iteration += 1
                
                self.canvas.set_at((x, y), self.get_color(iteration, self.max_iter))
    
    def render_julia(self):
        cx = -0.7 + 0.27015 * math.sin(self.anim_time / 50)
        cy = 0.27015 + 0.7 * math.cos(self.anim_time / 50)
        
        for x in range(600):
            for y in range(500):
                zx = (x - 300) / (180 * self.zoom) + self.offset_x
                zy = (y - 250) / (180 * self.zoom) + self.offset_y
                
                iteration = 0
                while zx * zx + zy * zy < 4 and iteration < self.max_iter:
                    tmp = zx * zx - zy * zy + cx
                    zy = 2 * zx * zy + cy
                    zx = tmp
                    iteration += 1
                
                self.canvas.set_at((x, y), self.get_color(iteration, self.max_iter))
    
    def render_tree(self, surface, x, y, angle, length, depth):
        if depth == 0:
            return
        
        x2 = x + int(math.cos(angle) * length)
        y2 = y + int(math.sin(angle) * length)
        
        color = (0, 100 + depth * 20, 0)
        pygame.draw.line(surface, color, (x, y), (x2, y2), max(1, depth))
        
        new_length = length * 0.7
        self.render_tree(surface, x2, y2, angle - 0.4, new_length, depth - 1)
        self.render_tree(surface, x2, y2, angle + 0.4, new_length, depth - 1)
    
    def render_sierpinski(self, surface, x, y, size, depth):
        if depth == 0:
            points = [(x, y - size), (x - size, y + size), (x + size, y + size)]
            pygame.draw.polygon(surface, (0, 100, 200), points)
            return
        
        half = size // 2
        self.render_sierpinski(surface, x, y - half, half, depth - 1)
        self.render_sierpinski(surface, x - half, y + half, half, depth - 1)
        self.render_sierpinski(surface, x + half, y + half, half, depth - 1)
    
    def render_koch(self, surface, x1, y1, x2, y2, depth):
        if depth == 0:
            pygame.draw.line(surface, (100, 50, 150), (x1, y1), (x2, y2), 2)
            return
        
        dx = x2 - x1
        dy = y2 - y1
        
        x3 = x1 + dx // 3
        y3 = y1 + dy // 3
        
        x5 = x1 + 2 * dx // 3
        y5 = y1 + 2 * dy // 3
        
        x4 = x3 + (dx - dy * 1.732) // 6
        y4 = y3 + (dy + dx * 1.732) // 6
        
        self.render_koch(surface, x1, y1, x3, y3, depth - 1)
        self.render_koch(surface, x3, y3, int(x4), int(y4), depth - 1)
        self.render_koch(surface, int(x4), int(y4), x5, y5, depth - 1)
        self.render_koch(surface, x5, y5, x2, y2, depth - 1)
    
    def render(self):
        self.canvas.fill((245, 245, 245))
        
        if self.current_fractal == 0:
            self.render_mandelbrot()
        elif self.current_fractal == 1:
            self.render_julia()
        elif self.current_fractal == 2:
            self.render_tree(self.canvas, 300, 480, -math.pi / 2, 120, 9)
        elif self.current_fractal == 3:
            self.canvas.fill((245, 245, 245))
            self.render_sierpinski(self.canvas, 300, 250, 200, 6)
        elif self.current_fractal == 4:
            self.canvas.fill((245, 245, 245))
            self.render_koch(self.canvas, 100, 350, 500, 350, 5)
            self.render_koch(self.canvas, 500, 350, 300, 100, 5)
            self.render_koch(self.canvas, 300, 100, 100, 350, 5)
        
        self.needs_render = False
    
    def draw_panel(self):
        pygame.draw.rect(self.screen, self.colors['panel'], (620, 10, 170, 580), border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 200), (620, 10, 170, 580), 2, border_radius=10)
        
        title = self.large_font.render('分形艺术', True, self.colors['text'])
        self.screen.blit(title, (640, 15))
        
        name = self.font.render(self.fractal_names[self.current_fractal], True, (100, 100, 200))
        self.screen.blit(name, (630, 450))
        
        info = [
            f'缩放: {self.zoom:.1f}x',
            f'迭代: {self.max_iter}',
            f'颜色模式: {self.color_mode + 1}',
        ]
        y = 480
        for line in info:
            text = self.font.render(line, True, (80, 80, 80))
            self.screen.blit(text, (630, y))
            y += 25
    
    def draw_buttons(self):
        for btn in self.buttons:
            color = self.colors['button_hover'] if btn == self.hovered_button else self.colors['button']
            pygame.draw.rect(self.screen, color, (btn['x'], btn['y'], btn['w'], btn['h']), border_radius=8)
            
            text = self.font.render(btn['text'], True, (255, 255, 255))
            text_rect = text.get_rect(center=(btn['x'] + btn['w'] // 2, btn['y'] + btn['h'] // 2))
            self.screen.blit(text, text_rect)
    
    def handle_click(self, pos):
        for btn in self.buttons:
            if btn['x'] <= pos[0] <= btn['x'] + btn['w'] and btn['y'] <= pos[1] <= btn['y'] + btn['h']:
                self.handle_button(btn['action'])
                return
        
        if 10 <= pos[0] <= 610 and 50 <= pos[1] <= 550:
            cx = (pos[0] - 310) / (150 * self.zoom)
            cy = (pos[1] - 300) / (150 * self.zoom)
            self.offset_x += cx
            self.offset_y += cy
            self.needs_render = True
    
    def handle_button(self, action):
        if action == 'prev':
            self.current_fractal = (self.current_fractal - 1) % len(self.fractal_names)
            self.needs_render = True
        elif action == 'next':
            self.current_fractal = (self.current_fractal + 1) % len(self.fractal_names)
            self.needs_render = True
        elif action == 'zoom_in':
            self.zoom *= 1.5
            self.needs_render = True
        elif action == 'zoom_out':
            self.zoom /= 1.5
            self.needs_render = True
        elif action == 'color':
            self.color_mode = (self.color_mode + 1) % 5
            self.needs_render = True
        elif action == 'animate':
            self.animating = not self.animating
        elif action == 'reset':
            self.zoom = 1.0
            self.offset_x = 0.0
            self.offset_y = 0.0
            self.needs_render = True
        elif action == 'save':
            pygame.image.save(self.canvas, 'fractal.png')
    
    def handle_mouse_move(self, pos):
        self.hovered_button = None
        for btn in self.buttons:
            if btn['x'] <= pos[0] <= btn['x'] + btn['w'] and btn['y'] <= pos[1] <= btn['y'] + btn['h']:
                self.hovered_button = btn
                break
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_move(event.pos)
            
            if self.animating and self.current_fractal == 1:
                self.anim_time += 1
                self.needs_render = True
            
            if self.needs_render:
                self.render()
            
            self.screen.fill(self.colors['bg'])
            self.screen.blit(self.canvas, (10, 50))
            self.draw_panel()
            self.draw_buttons()
            
            title = self.large_font.render('分形艺术生成器', True, self.colors['text'])
            title_rect = title.get_rect(center=(310, 30))
            self.screen.blit(title, title_rect)
            
            pygame.display.flip()
            self.clock.tick(30)

if __name__ == '__main__':
    game = FractalArt()
    game.run()
