#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音乐可视化
使用pygame实现的音频可视化游戏
"""

import pygame
import sys
import math
import random

class Bar:
    def __init__(self, x, width, height):
        self.x = x
        self.width = width
        self.height = height
        self.target_height = height
        self.color = (0, 0, 0)

class MusicVisualizer:
    def __init__(self):
        pygame.init()
        self.width = 900
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('音乐可视化')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.large_font = pygame.font.Font(None, 36)
        
        self.bars = []
        bar_width = 15
        bar_spacing = 3
        for i in range(50):
            x = 50 + i * (bar_width + bar_spacing)
            bar = Bar(x, bar_width, 50)
            bar.color = self.get_color(i, 50)
            self.bars.append(bar)
        
        self.current_mode = 0
        self.mode_names = ['频谱柱', '波形图', '环形', '粒子', '跳动球']
        self.playing = False
        self.time = 0
        
        self.particles = []
        self.balls = []
        
        self.colors = {
            'bg': (20, 20, 30),
            'text': (255, 255, 255),
            'button': (60, 80, 120),
            'button_hover': (80, 100, 150),
        }
        
        self.buttons = [
            {'text': '播放', 'x': 50, 'y': 520, 'w': 100, 'h': 50, 'action': 'play'},
            {'text': '切换', 'x': 160, 'y': 520, 'w': 100, 'h': 50, 'action': 'mode'},
            {'text': '随机', 'x': 270, 'y': 520, 'w': 100, 'h': 50, 'action': 'random'},
            {'text': '重置', 'x': 380, 'y': 520, 'w': 100, 'h': 50, 'action': 'reset'},
        ]
        
        self.hovered_button = None
        self.init_balls()
    
    def get_color(self, index, total):
        hue = index / total
        r = int(255 * (0.5 + 0.5 * math.sin(hue * 6.28 + 0)))
        g = int(255 * (0.5 + 0.5 * math.sin(hue * 6.28 + 2.09)))
        b = int(255 * (0.5 + 0.5 * math.sin(hue * 6.28 + 4.18)))
        return (r, g, b)
    
    def init_balls(self):
        self.balls = []
        for i in range(10):
            ball = {
                'x': self.width // 2,
                'y': self.height // 2 - 50,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-2, -5),
                'radius': random.randint(8, 20),
                'color': self.get_color(i, 10),
            }
            self.balls.append(ball)
    
    def get_audio_level(self, bar_index):
        t = self.time / 60
        base_level = 0.3 + 0.3 * math.sin(t + bar_index * 0.2)
        beat = 0.4 * math.sin(t * 4) ** 4
        high_freq = 0.2 * math.sin(t * 8 + bar_index * 0.5)
        
        level = base_level + beat + high_freq
        
        if bar_index < 10:
            level *= 1.2
        elif bar_index > 35:
            level *= 0.8
        
        return max(0.1, min(1.0, level))
    
    def update_bars(self):
        for i, bar in enumerate(self.bars):
            level = self.get_audio_level(i)
            bar.target_height = 50 + level * 250
            bar.height += (bar.target_height - bar.height) * 0.2
    
    def update_particles(self):
        if self.playing:
            for _ in range(3):
                particle = {
                    'x': random.randint(100, self.width - 100),
                    'y': self.height - 100,
                    'vx': random.uniform(-2, 2),
                    'vy': random.uniform(-5, -2),
                    'life': 60,
                    'color': self.get_color(random.randint(0, 49), 50),
                    'size': random.randint(3, 8),
                }
                self.particles.append(particle)
        
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
    
    def update_balls(self):
        beat = math.sin(self.time / 15 * 4) > 0.9
        
        for ball in self.balls:
            if beat:
                ball['vy'] = -8 - random.random() * 4
            
            ball['x'] += ball['vx']
            ball['y'] += ball['vy']
            ball['vy'] += 0.5
            
            if ball['x'] - ball['radius'] < 50 or ball['x'] + ball['radius'] > self.width - 50:
                ball['vx'] *= -0.8
                ball['x'] = max(50 + ball['radius'], min(self.width - 50 - ball['radius'], ball['x']))
            
            if ball['y'] + ball['radius'] > self.height - 120:
                ball['y'] = self.height - 120 - ball['radius']
                ball['vy'] *= -0.7
                ball['vx'] *= 0.98
    
    def draw_bars_mode(self):
        for i, bar in enumerate(self.bars):
            x = bar.x
            y = self.height - 120 - bar.height
            w = bar.width
            h = bar.height
            
            gradient_surface = pygame.Surface((w, h), pygame.SRCALPHA)
            for dy in range(h):
                alpha = int(255 * (1 - dy / h))
                pygame.draw.line(gradient_surface, (*bar.color, alpha), (0, dy), (w, dy))
            
            self.screen.blit(gradient_surface, (x, y))
            pygame.draw.rect(self.screen, bar.color, (x, y, w, h), 2)
    
    def draw_waveform_mode(self):
        points = []
        for i in range(self.width - 100):
            t = self.time / 30 + i / 50
            y = self.height // 2 - 50 + int(100 * math.sin(t) * math.sin(t * 2))
            if i % 3 == 0:
                y += int(30 * math.sin(self.time / 10 + i / 20))
            points.append((50 + i, y))
        
        if len(points) > 1:
            pygame.draw.lines(self.screen, (100, 200, 255), False, points, 3)
            
            points_bottom = [(x, self.height // 2 - 50 + (self.height // 2 - 50 - y)) for x, y in points]
            pygame.draw.lines(self.screen, (255, 100, 200), False, points_bottom, 3)
            
            for i in range(0, len(points), 10):
                pygame.draw.circle(self.screen, (255, 255, 150), points[i], 4)
    
    def draw_circular_mode(self):
        center_x = self.width // 2
        center_y = self.height // 2 - 50
        
        for i in range(60):
            angle = i / 60 * math.pi * 2 + self.time / 50
            inner_radius = 100
            level = self.get_audio_level(i % 50)
            outer_radius = 100 + level * 150
            
            x1 = center_x + math.cos(angle) * inner_radius
            y1 = center_y + math.sin(angle) * inner_radius
            x2 = center_x + math.cos(angle) * outer_radius
            y2 = center_y + math.sin(angle) * outer_radius
            
            color = self.get_color(i, 60)
            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 4)
        
        pygame.draw.circle(self.screen, (40, 40, 60), (center_x, center_y), 90)
        pygame.draw.circle(self.screen, (80, 80, 120), (center_x, center_y), 90, 3)
    
    def draw_particle_mode(self):
        for p in self.particles:
            alpha = int(255 * (p['life'] / 60))
            s = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p['color'], alpha), (p['size'], p['size']), p['size'])
            self.screen.blit(s, (p['x'] - p['size'], p['y'] - p['size']))
    
    def draw_ball_mode(self):
        for ball in self.balls:
            x = int(ball['x'])
            y = int(ball['y'])
            
            glow_surface = pygame.Surface((ball['radius'] * 4, ball['radius'] * 4), pygame.SRCALPHA)
            for r in range(ball['radius'], 0, -2):
                alpha = int(50 * (1 - r / ball['radius']))
                pygame.draw.circle(glow_surface, (*ball['color'], alpha), (ball['radius'] * 2, ball['radius'] * 2), r + ball['radius'])
            self.screen.blit(glow_surface, (x - ball['radius'] * 2, y - ball['radius'] * 2))
            
            pygame.draw.circle(self.screen, ball['color'], (x, y), ball['radius'])
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), ball['radius'], 2)
    
    def draw_floor(self):
        pygame.draw.rect(self.screen, (50, 50, 70), (50, self.height - 120, self.width - 100, 10))
        
        if self.playing:
            for i in range(0, self.width - 100, 30):
                level = self.get_audio_level(i // 30 % 50)
                h = int(level * 20)
                pygame.draw.rect(self.screen, (100, 150, 200), (50 + i, self.height - 120 - h, 20, h))
    
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
    
    def handle_button(self, action):
        if action == 'play':
            self.playing = not self.playing
        elif action == 'mode':
            self.current_mode = (self.current_mode + 1) % len(self.mode_names)
        elif action == 'random':
            for bar in self.bars:
                bar.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        elif action == 'reset':
            self.time = 0
            self.particles = []
            self.init_balls()
    
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
            
            if self.playing:
                self.time += 1
                self.update_bars()
                self.update_particles()
                self.update_balls()
            
            self.screen.fill(self.colors['bg'])
            
            if self.current_mode == 0:
                self.draw_bars_mode()
            elif self.current_mode == 1:
                self.draw_waveform_mode()
            elif self.current_mode == 2:
                self.draw_circular_mode()
            elif self.current_mode == 3:
                self.draw_particle_mode()
            elif self.current_mode == 4:
                self.draw_ball_mode()
            
            self.draw_floor()
            self.draw_buttons()
            
            mode_text = self.large_font.render(f'模式: {self.mode_names[self.current_mode]}', True, self.colors['text'])
            self.screen.blit(mode_text, (500, 530))
            
            status_text = self.font.render('播放中' if self.playing else '暂停', True, (100, 255, 100) if self.playing else (255, 200, 100))
            self.screen.blit(status_text, (750, 535))
            
            title = self.large_font.render('音乐可视化', True, self.colors['text'])
            title_rect = title.get_rect(center=(self.width // 2, 30))
            self.screen.blit(title, title_rect)
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == '__main__':
    game = MusicVisualizer()
    game.run()
