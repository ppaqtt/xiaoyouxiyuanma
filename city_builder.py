#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
城市建造模拟器 - City Builder
操作说明：
- 使用数字键 1-4 选择建筑类型：1=住宅 2=商业 3=工业 4=道路
- 鼠标点击放置建筑
- 右键取消选择
- 观察资源变化和城市发展
"""

import pygame
import sys
import random
from pygame.locals import *

# 初始化pygame
pygame.init()

# 游戏窗口设置
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('城市建造模拟器')

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
GREEN = (50, 150, 50)
BLUE = (50, 50, 200)
RED = (200, 50, 50)
YELLOW = (255, 200, 50)
BROWN = (139, 69, 19)
ORANGE = (255, 140, 0)
DARK_GREEN = (0, 100, 0)
PURPLE = (128, 0, 128)

# 字体设置
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# 网格设置
GRID_SIZE = 40
GRID_WIDTH = 20
GRID_HEIGHT = 12
GRID_OFFSET_X = 100
GRID_OFFSET_Y = 150

# 建筑类型
BUILDING_TYPES = {
    0: {'name': '空地', 'color': GREEN, 'cost': 0},
    1: {'name': '住宅', 'color': BLUE, 'cost': 100, 'population': 10, 'demand': 5},
    2: {'name': '商业', 'color': RED, 'cost': 200, 'jobs': 8, 'income': 5},
    3: {'name': '工业', 'color': ORANGE, 'cost': 150, 'jobs': 15, 'pollution': 1},
    4: {'name': '道路', 'color': GRAY, 'cost': 20}
}

class CityBuilder:
    def __init__(self):
        # 游戏状态
        self.money = 1000
        self.population = 0
        self.jobs = 0
        self.pollution = 0
        self.day = 1
        self.game_speed = 1
        
        # 网格数据
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # 建筑等级
        self.building_levels = [[1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # 选中的建筑类型
        self.selected_building = 1
        
        # 消息系统
        self.message = ''
        self.message_timer = 0
        
        # 美观度
        self.beauty = 50
        
    def show_message(self, msg):
        self.message = msg
        self.message_timer = 180
    
    def calculate_resources(self):
        # 重新计算所有资源
        self.population = 0
        self.jobs = 0
        self.pollution = 0
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                building_type = self.grid[y][x]
                if building_type == 1:  # 住宅
                    self.population += BUILDING_TYPES[1]['population'] * self.building_levels[y][x]
                elif building_type == 2:  # 商业
                    self.jobs += BUILDING_TYPES[2]['jobs'] * self.building_levels[y][x]
                elif building_type == 3:  # 工业
                    self.jobs += BUILDING_TYPES[3]['jobs'] * self.building_levels[y][x]
                    self.pollution += BUILDING_TYPES[3]['pollution'] * self.building_levels[y][x]
    
    def update_economy(self):
        # 每天更新经济
        # 商业收入
        commercial_count = sum(1 for row in self.grid for cell in row if cell == 2)
        industrial_count = sum(1 for row in self.grid for cell in row if cell == 3)
        
        income = commercial_count * 10 * self.game_speed
        industrial_income = industrial_count * 5 * self.game_speed
        total_income = income + industrial_income
        
        # 人口支出（公共服务）
        expenses = (self.population // 10) * 2
        
        # 计算就业平衡
        job_balance = self.jobs - self.population
        if job_balance < 0:
            # 失业问题，收入减少
            total_income *= 0.8
        
        # 污染影响
        if self.pollution > 10:
            total_income *= 0.9
        
        self.money += int(total_income - expenses)
    
    def place_building(self, grid_x, grid_y):
        if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y < 0 or grid_y >= GRID_HEIGHT:
            return
        
        current_type = self.grid[grid_y][grid_x]
        if current_type == self.selected_building and current_type != 0:
            # 升级现有建筑
            if self.building_levels[grid_y][grid_x] < 3:
                upgrade_cost = BUILDING_TYPES[current_type]['cost'] * self.building_levels[grid_y][grid_x]
                if self.money >= upgrade_cost:
                    self.money -= upgrade_cost
                    self.building_levels[grid_y][grid_x] += 1
                    self.calculate_resources()
                    self.show_message(f'{BUILDING_TYPES[current_type]["name"]} 升级到 {self.building_levels[grid_y][grid_x]} 级！')
                else:
                    self.show_message('金钱不足！')
            else:
                self.show_message('已达最高等级！')
            return
        
        # 放置新建筑
        cost = BUILDING_TYPES[self.selected_building]['cost']
        if self.money >= cost:
            self.money -= cost
            self.grid[grid_y][grid_x] = self.selected_building
            self.building_levels[grid_y][grid_x] = 1
            self.calculate_resources()
            self.show_message(f'建造了 {BUILDING_TYPES[self.selected_building]["name"]}！')
        else:
            self.show_message('金钱不足！')
    
    def remove_building(self, grid_x, grid_y):
        if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y < 0 or grid_y >= GRID_HEIGHT:
            return
        
        if self.grid[grid_y][grid_x] != 0:
            # 拆除返还部分金钱
            refund = BUILDING_TYPES[self.grid[grid_y][grid_x]]['cost'] // 2
            self.money += refund
            self.grid[grid_y][grid_x] = 0
            self.building_levels[grid_y][grid_x] = 1
            self.calculate_resources()
            self.show_message(f'拆除建筑，返还 ¥{refund}')
    
    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    GRID_OFFSET_X + x * GRID_SIZE,
                    GRID_OFFSET_Y + y * GRID_SIZE,
                    GRID_SIZE,
                    GRID_SIZE
                )
                
                building_type = self.grid[y][x]
                color = BUILDING_TYPES[building_type]['color']
                
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)
                
                # 显示建筑等级
                if building_type != 0 and building_type != 4:
                    level = self.building_levels[y][x]
                    if level > 1:
                        text = font_small.render(str(level), True, WHITE)
                        text_rect = text.get_rect(center=rect.center)
                        screen.blit(text, text_rect)
    
    def draw_ui(self):
        # 顶部状态栏
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 120))
        pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, 120), 3)
        
        texts = [
            (f'金钱: ¥{self.money}', GREEN, 20, 20),
            (f'人口: {self.population}', BLUE, 200, 20),
            (f'就业: {self.jobs}', RED, 380, 20),
            (f'污染: {self.pollution}', PURPLE, 540, 20),
            (f'天数: {self.day}', BLACK, 700, 20),
            (f'选中: {BUILDING_TYPES[self.selected_building]["name"]}', YELLOW, 20, 70)
        ]
        
        for text, color, x, y in texts:
            text_surf = font_medium.render(text, True, color)
            screen.blit(text_surf, (x, y))
        
        # 建筑选择按钮
        button_y = 600
        buttons = [
            ('1-住宅', 1, 100),
            ('2-商业', 2, 250),
            ('3-工业', 3, 400),
            ('4-道路', 4, 550),
            ('拆除', 0, 700)
        ]
        
        for text, b_type, x in buttons:
            color = YELLOW if self.selected_building == b_type else LIGHT_GRAY
            pygame.draw.rect(screen, color, (x, button_y, 130, 50))
            pygame.draw.rect(screen, BLACK, (x, button_y, 130, 50), 2)
            text_surf = font_small.render(text, True, BLACK)
            text_rect = text_surf.get_rect(center=(x + 65, button_y + 25))
            screen.blit(text_surf, text_rect)
        
        # 操作说明
        help_text = font_small.render('数字键选择建筑，左键放置/升级，右键拆除', True, BLACK)
        screen.blit(help_text, (20, HEIGHT - 30))
        
        # 显示消息
        if self.message_timer > 0:
            self.message_timer -= 1
            text = font_medium.render(self.message, True, RED)
            text_rect = text.get_rect(center=(WIDTH//2, 550))
            pygame.draw.rect(screen, WHITE, (text_rect.x - 10, text_rect.y - 10, text_rect.width + 20, text_rect.height + 20))
            screen.blit(text, text_rect)
    
    def draw(self):
        screen.fill(LIGHT_GRAY)
        self.draw_grid()
        self.draw_ui()
    
    def handle_click(self, pos, button):
        x, y = pos
        
        # 检查建筑选择按钮
        button_y = 600
        buttons = [
            (1, 100),
            (2, 250),
            (3, 400),
            (4, 550),
            (0, 700)
        ]
        
        for b_type, bx in buttons:
            if bx <= x <= bx + 130 and button_y <= y <= button_y + 50:
                self.selected_building = b_type
                return
        
        # 检查网格点击
        grid_x = (x - GRID_OFFSET_X) // GRID_SIZE
        grid_y = (y - GRID_OFFSET_Y) // GRID_SIZE
        
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            if button == 1:  # 左键
                if self.selected_building == 0:
                    self.remove_building(grid_x, grid_y)
                else:
                    self.place_building(grid_x, grid_y)
            elif button == 3:  # 右键
                self.remove_building(grid_x, grid_y)
    
    def update(self):
        # 每天更新
        self.day += 0.01 * self.game_speed
        if int(self.day) > int(self.day - 0.01 * self.game_speed):
            self.update_economy()
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    self.handle_click(event.pos, event.button)
                elif event.type == KEYDOWN:
                    if event.key == K_1:
                        self.selected_building = 1
                    elif event.key == K_2:
                        self.selected_building = 2
                    elif event.key == K_3:
                        self.selected_building = 3
                    elif event.key == K_4:
                        self.selected_building = 4
                    elif event.key == K_0 or event.key == K_r:
                        self.selected_building = 0
            
            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = CityBuilder()
    game.run()
