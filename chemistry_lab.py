#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
化学实验模拟器
使用pygame实现的化学实验学习游戏
"""

import pygame
import os
import sys
import random

class Chemical:
    def __init__(self, name, formula, color, state='liquid'):
        self.name = name
        self.formula = formula
        self.color = color
        self.state = state

class Beaker:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 100
        self.height = 150
        self.chemicals = []
        self.temperature = 25
        self.stirring = False
    
    def add_chemical(self, chemical):
        self.chemicals.append(chemical)
        if len(self.chemicals) == 1:
            self.color = chemical.color
        else:
            self.mix_colors()
    
    def mix_colors(self):
        if not self.chemicals:
            self.color = (200, 200, 200)
            return
        
        r = sum(c.color[0] for c in self.chemicals) // len(self.chemicals)
        g = sum(c.color[1] for c in self.chemicals) // len(self.chemicals)
        b = sum(c.color[2] for c in self.chemicals) // len(self.chemicals)
        self.color = (r, g, b)
    
    def get_mixture_name(self):
        if len(self.chemicals) == 0:
            return '空'
        elif len(self.chemicals) == 1:
            return self.chemicals[0].name
        else:
            return ' + '.join(c.name for c in self.chemicals)
    
    def empty(self):
        self.chemicals = []
        self.color = (200, 200, 200)
        self.temperature = 25

class ChemistryLab:
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

self.width = 900
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('化学实验室')
        self.clock = pygame.time.Clock()
        self.font = get_chinese_font(28)
        self.large_font = get_chinese_font(40)
        
        self.chemicals = [
            Chemical('水', 'H₂O', (100, 150, 255)),
            Chemical('盐酸', 'HCl', (255, 200, 100)),
            Chemical('氢氧化钠', 'NaOH', (100, 255, 100)),
            Chemical('硫酸铜', 'CuSO₄', (0, 150, 200)),
            Chemical('石蕊', '石蕊', (180, 100, 150)),
            Chemical('酚酞', '酚酞', (200, 200, 200)),
            Chemical('硫酸', 'H₂SO₄', (255, 180, 0)),
            Chemical('氨水', 'NH₃·H₂O', (150, 200, 255)),
        ]
        
        self.selected_chemical = None
        self.dragging = False
        self.drag_pos = (0, 0)
        
        self.beakers = [
            Beaker(150, 400),
            Beaker(350, 400),
            Beaker(550, 400),
        ]
        
        self.colors = {
            'bg': (230, 230, 250),
            'table': (139, 90, 43),
            'beaker': (150, 150, 150),
            'text': (30, 30, 30),
            'button': (100, 150, 255),
            'button_hover': (130, 180, 255),
        }
        
        self.buttons = [
            {'text': '清空', 'x': 750, 'y': 450, 'w': 100, 'h': 40, 'action': 'empty'},
            {'text': '搅拌', 'x': 750, 'y': 500, 'w': 100, 'h': 40, 'action': 'stir'},
            {'text': '加热', 'x': 750, 'y': 550, 'w': 100, 'h': 40, 'action': 'heat'},
            {'text': '实验说明', 'x': 750, 'y': 600, 'w': 100, 'h': 40, 'action': 'help'},
        ]
        
        self.hovered_button = None
        self.show_help = False
        self.selected_beaker = 0
        self.message = ''
        self.message_timer = 0
    
    def get_chemical_at(self, pos):
        for i, chem in enumerate(self.chemicals):
            x = 50 + (i % 4) * 120
            y = 80 + (i // 4) * 80
            rect = pygame.Rect(x, y, 80, 60)
            if rect.collidepoint(pos):
                return chem
        return None
    
    def get_beaker_at(self, pos):
        for i, beaker in enumerate(self.beakers):
            rect = pygame.Rect(beaker.x, beaker.y, beaker.width, beaker.height)
            if rect.collidepoint(pos):
                return i, beaker
        return None, None
    
    def add_chemical_to_beaker(self, chemical, beaker_idx):
        if beaker_idx is not None:
            self.beakers[beaker_idx].add_chemical(chemical)
            self.check_reaction(beaker_idx)
    
    def check_reaction(self, beaker_idx):
        beaker = self.beakers[beaker_idx]
        chemicals = [c.name for c in beaker.chemicals]
        
        if '盐酸' in chemicals and '氢氧化钠' in chemicals:
            self.message = '中和反应！产生盐和水'
            beaker.color = (200, 200, 230)
            self.message_timer = 180
        elif '盐酸' in chemicals and '石蕊' in chemicals:
            self.message = '石蕊遇酸变红！'
            beaker.color = (255, 50, 50)
            self.message_timer = 180
        elif '氢氧化钠' in chemicals and '石蕊' in chemicals:
            self.message = '石蕊遇碱变蓝！'
            beaker.color = (50, 50, 255)
            self.message_timer = 180
        elif '氢氧化钠' in chemicals and '酚酞' in chemicals:
            self.message = '酚酞遇碱变红！'
            beaker.color = (255, 100, 150)
            self.message_timer = 180
        elif '硫酸铜' in chemicals and '氢氧化钠' in chemicals:
            self.message = '产生蓝色沉淀！'
            beaker.color = (50, 100, 200)
            self.message_timer = 180
        elif '硫酸' in chemicals and '氨水' in chemicals:
            self.message = '产生白烟！'
            beaker.color = (240, 240, 255)
            self.message_timer = 180
    
    def draw_chemicals(self):
        for i, chem in enumerate(self.chemicals):
            x = 50 + (i % 4) * 120
            y = 80 + (i // 4) * 80
            
            rect = pygame.Rect(x, y, 80, 60)
            color = (220, 220, 220) if self.selected_chemical != chem else (255, 255, 150)
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            pygame.draw.rect(self.screen, self.colors['text'], rect, 2, border_radius=5)
            
            pygame.draw.circle(self.screen, chem.color, (x + 40, y + 20), 15)
            
            text = self.font.render(chem.name, True, self.colors['text'])
            text_rect = text.get_rect(center=(x + 40, y + 45))
            self.screen.blit(text, text_rect)
            
            formula_text = self.font.render(chem.formula, True, (80, 80, 80))
            formula_rect = formula_text.get_rect(center=(x + 40, y + 58))
            self.screen.blit(formula_text, formula_rect)
    
    def draw_beakers(self):
        for i, beaker in enumerate(self.beakers):
            pygame.draw.rect(self.screen, self.colors['table'], 
                          (beaker.x - 10, beaker.y + beaker.height, beaker.width + 20, 30))
            
            pygame.draw.rect(self.screen, self.colors['beaker'], 
                          (beaker.x, beaker.y, beaker.width, beaker.height), 3)
            
            if beaker.chemicals:
                liquid_height = min(beaker.height - 20, 30 + len(beaker.chemicals) * 20)
                pygame.draw.rect(self.screen, beaker.color,
                              (beaker.x + 5, beaker.y + beaker.height - liquid_height, 
                               beaker.width - 10, liquid_height - 5))
            
            label = f'烧杯 {i + 1}'
            text = self.font.render(label, True, self.colors['text'])
            text_rect = text.get_rect(center=(beaker.x + beaker.width // 2, beaker.y - 20))
            self.screen.blit(text, text_rect)
            
            mixture = beaker.get_mixture_name()
            mixture_text = self.font.render(mixture, True, self.colors['text'])
            mixture_rect = mixture_text.get_rect(center=(beaker.x + beaker.width // 2, 
                                                        beaker.y + beaker.height + 25))
            self.screen.blit(mixture_text, mixture_rect)
            
            if i == self.selected_beaker:
                pygame.draw.rect(self.screen, (255, 200, 0), 
                              (beaker.x - 5, beaker.y - 5, beaker.width + 10, beaker.height + 10), 3)
    
    def draw_buttons(self):
        for btn in self.buttons:
            color = self.colors['button_hover'] if btn == self.hovered_button else self.colors['button']
            pygame.draw.rect(self.screen, color, (btn['x'], btn['y'], btn['w'], btn['h']), border_radius=5)
            
            text = self.font.render(btn['text'], True, (255, 255, 255))
            text_rect = text.get_rect(center=(btn['x'] + btn['w'] // 2, btn['y'] + btn['h'] // 2))
            self.screen.blit(text, text_rect)
    
    def draw_help(self):
        if self.show_help:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            help_text = [
                '化学实验说明',
                '',
                '1. 点击选择化学试剂',
                '2. 点击烧杯添加试剂',
                '3. 观察化学反应现象',
                '',
                '可能的反应:',
                '• 盐酸 + 氢氧化钠 → 中和反应',
                '• 酸/碱 + 石蕊 → 变色',
                '• 碱 + 酚酞 → 变红',
                '• 硫酸铜 + 氢氧化钠 → 蓝色沉淀',
                '• 硫酸 + 氨水 → 白烟',
                '',
                '按任意键关闭'
            ]
            
            y_offset = 150
            for line in help_text:
                text = self.font.render(line, True, (255, 255, 255))
                text_rect = text.get_rect(center=(self.width // 2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 35
    
    def draw_message(self):
        if self.message and self.message_timer > 0:
            text = self.large_font.render(self.message, True, (200, 0, 0))
            text_rect = text.get_rect(center=(self.width // 2, 350))
            pygame.draw.rect(self.screen, (255, 255, 200), 
                          (text_rect.x - 20, text_rect.y - 10, text_rect.width + 40, text_rect.height + 20),
                          border_radius=10)
            self.screen.blit(text, text_rect)
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.message = ''
    
    def handle_click(self, pos):
        if self.show_help:
            self.show_help = False
            return
        
        for btn in self.buttons:
            if btn['x'] <= pos[0] <= btn['x'] + btn['w'] and btn['y'] <= pos[1] <= btn['y'] + btn['h']:
                self.handle_button(btn['action'])
                return
        
        beaker_idx, beaker = self.get_beaker_at(pos)
        if beaker_idx is not None:
            self.selected_beaker = beaker_idx
            if self.selected_chemical:
                self.add_chemical_to_beaker(self.selected_chemical, beaker_idx)
                self.selected_chemical = None
            return
        
        chem = self.get_chemical_at(pos)
        if chem:
            self.selected_chemical = chem
    
    def handle_button(self, action):
        if action == 'empty':
            self.beakers[self.selected_beaker].empty()
        elif action == 'stir':
            self.beakers[self.selected_beaker].stirring = True
            pygame.time.set_timer(pygame.USEREVENT, 500)
        elif action == 'heat':
            self.beakers[self.selected_beaker].temperature += 20
            if self.beakers[self.selected_beaker].temperature > 100:
                self.beakers[self.selected_beaker].temperature = 100
            self.message = f'加热！温度: {self.beakers[self.selected_beaker].temperature}°C'
            self.message_timer = 120
        elif action == 'help':
            self.show_help = True
    
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
                elif event.type == pygame.USEREVENT:
                    for beaker in self.beakers:
                        beaker.stirring = False
                    pygame.time.set_timer(pygame.USEREVENT, 0)
                elif event.type == pygame.KEYDOWN:
                    if self.show_help:
                        self.show_help = False
            
            self.screen.fill(self.colors['bg'])
            
            title = self.large_font.render('化学实验室', True, self.colors['text'])
            title_rect = title.get_rect(center=(self.width // 2, 30))
            self.screen.blit(title, title_rect)
            
            self.draw_chemicals()
            self.draw_beakers()
            self.draw_buttons()
            self.draw_message()
            self.draw_help()
            
            if self.selected_chemical:
                hint = f'已选择: {self.selected_chemical.name} - 点击烧杯添加'
                hint_text = self.font.render(hint, True, (100, 100, 200))
                self.screen.blit(hint_text, (50, 200))
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == '__main__':
    game = ChemistryLab()
    game.run()
