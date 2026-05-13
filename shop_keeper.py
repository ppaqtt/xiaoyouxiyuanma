#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商店经营模拟器 - Shop Keeper
操作说明：
- 点击商品采购商品
- 使用 +/- 按钮调整价格
- 观察销售和库存变化
- 升级商店扩大经营
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
pygame.display.set_caption('商店经营模拟器')

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
RED = (200, 50, 50)
YELLOW = (255, 200, 50)
PURPLE = (128, 0, 128)
ORANGE = (255, 140, 0)
CYAN = (0, 255, 255)

# 字体设置
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

class ShopKeeper:
    def __init__(self):
        # 游戏状态
        self.money = 1000
        self.day = 1
        self.hour = 8
        self.minute = 0
        self.game_speed = 1
        self.paused = False
        
        # 商店属性
        self.shop_level = 1
        self.reputation = 50
        
        # 商品数据
        self.products = [
            {'name': '苹果', 'price': 10, 'cost': 5, 'stock': 50, 'sales': 0, 'demand': 0.3, 'color': RED},
            {'name': '面包', 'price': 8, 'cost': 3, 'stock': 40, 'sales': 0, 'demand': 0.4, 'color': YELLOW},
            {'name': '牛奶', 'price': 15, 'cost': 8, 'stock': 30, 'sales': 0, 'demand': 0.25, 'color': WHITE},
            {'name': '饼干', 'price': 12, 'cost': 6, 'stock': 35, 'sales': 0, 'demand': 0.2, 'color': ORANGE},
            {'name': '饮料', 'price': 5, 'cost': 2, 'stock': 60, 'sales': 0, 'demand': 0.35, 'color': CYAN},
            {'name': '糖果', 'price': 3, 'cost': 1, 'stock': 100, 'sales': 0, 'demand': 0.5, 'color': PURPLE}
        ]
        
        # 销售记录
        self.sales_history = []
        
        # 选中的商品
        self.selected_product = 0
        
        # 消息系统
        self.message = ''
        self.message_timer = 0
        
    def show_message(self, msg):
        self.message = msg
        self.message_timer = 180
    
    def update_time(self):
        if self.paused:
            return
        
        self.minute += self.game_speed
        if self.minute >= 60:
            self.minute = 0
            self.hour += 1
            if self.hour >= 20:
                self.end_day()
            elif 9 <= self.hour <= 18:
                self.generate_sale()
    
    def generate_sale(self):
        # 根据时间和声望调整销售概率
        hour_factor = 1.0
        if 11 <= self.hour <= 13 or 17 <= self.hour <= 19:
            hour_factor = 1.5
        
        reputation_factor = 0.5 + (self.reputation / 100)
        
        for i, product in enumerate(self.products):
            if product['stock'] > 0:
                # 价格影响需求
                price_factor = max(0.2, 2.0 - (product['price'] / (product['cost'] * 4)))
                base_demand = product['demand'] * hour_factor * reputation_factor * price_factor
                
                if random.random() < base_demand * 0.1 * self.game_speed:
                    # 销售成功
                    sale_amount = random.randint(1, min(5, product['stock']))
                    product['stock'] -= sale_amount
                    product['sales'] += sale_amount
                    revenue = product['price'] * sale_amount
                    self.money += revenue
                    self.reputation = min(100, self.reputation + 0.1)
                    self.sales_history.append((self.day, product['name'], sale_amount, revenue))
                    if len(self.sales_history) > 50:
                        self.sales_history.pop(0)
    
    def buy_product(self, index, amount=10):
        product = self.products[index]
        cost = product['cost'] * amount
        if self.money >= cost:
            self.money -= cost
            product['stock'] += amount
            self.show_message(f'采购了 {amount} 个{product["name"]}，花费 ¥{cost}')
        else:
            self.show_message('金钱不足！')
    
    def change_price(self, index, delta):
        product = self.products[index]
        new_price = product['price'] + delta
        if new_price >= product['cost'] and new_price <= product['cost'] * 10:
            product['price'] = new_price
    
    def upgrade_shop(self):
        cost = self.shop_level * 500
        if self.money >= cost and self.shop_level < 5:
            self.money -= cost
            self.shop_level += 1
            self.game_speed = min(3, self.shop_level)
            self.show_message(f'商店升级到 {self.shop_level} 级！销售速度提升！')
        elif self.shop_level >= 5:
            self.show_message('商店已达最高级！')
        else:
            self.show_message('金钱不足！')
    
    def end_day(self):
        self.hour = 8
        self.minute = 0
        self.day += 1
        # 重置每日销售计数
        for product in self.products:
            product['sales'] = 0
        self.show_message(f'第 {self.day} 天开始了！')
    
    def draw(self):
        screen.fill(LIGHT_GRAY)
        
        # 顶部状态栏
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 120))
        pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, 120), 3)
        
        texts = [
            (f'金钱: ¥{self.money}', GREEN, 20, 20),
            (f'第 {self.day} 天', BLACK, 200, 20),
            (f'{self.hour:02d}:{self.minute:02d}', BLACK, 350, 20),
            (f'声望: {self.reputation:.0f}%', BLUE, 500, 20),
            (f'商店等级: {self.shop_level}', YELLOW, 700, 20)
        ]
        
        for text, color, x, y in texts:
            text_surf = font_medium.render(text, True, color)
            screen.blit(text_surf, (x, y))
        
        # 商品展示区
        start_y = 140
        for i, product in enumerate(self.products):
            x = 50 + (i % 2) * 450
            y = start_y + (i // 2) * 120
            
            rect = pygame.Rect(x, y, 400, 100)
            color = YELLOW if self.selected_product == i else WHITE
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            
            # 商品图标
            pygame.draw.circle(screen, product['color'], (x + 40, y + 50), 30)
            
            # 商品信息
            text1 = font_small.render(f'{product["name"]} 库存: {product["stock"]}', True, BLACK)
            text2 = font_small.render(f'售价: ¥{product["price"]} 成本: ¥{product["cost"]}', True, BLACK)
            text3 = font_small.render(f'今日销售: {product["sales"]}', True, BLUE)
            
            screen.blit(text1, (x + 80, y + 15))
            screen.blit(text2, (x + 80, y + 40))
            screen.blit(text3, (x + 80, y + 65))
            
            # 价格调整按钮
            btn_x = x + 300
            btn_y = y + 30
            pygame.draw.rect(screen, RED, (btn_x, btn_y, 40, 30))
            pygame.draw.rect(screen, BLACK, (btn_x, btn_y, 40, 30), 2)
            minus_text = font_small.render('-', True, WHITE)
            screen.blit(minus_text, (btn_x + 15, btn_y + 5))
            
            pygame.draw.rect(screen, GREEN, (btn_x + 50, btn_y, 40, 30))
            pygame.draw.rect(screen, BLACK, (btn_x + 50, btn_y, 40, 30), 2)
            plus_text = font_small.render('+', True, WHITE)
            screen.blit(plus_text, (btn_x + 65, btn_y + 5))
            
            # 采购按钮
            buy_btn_y = y + 65
            pygame.draw.rect(screen, BLUE, (btn_x, buy_btn_y, 90, 30))
            pygame.draw.rect(screen, BLACK, (btn_x, buy_btn_y, 90, 30), 2)
            buy_text = font_small.render('采购10', True, WHITE)
            screen.blit(buy_text, (btn_x + 10, buy_btn_y + 5))
        
        # 右侧面板
        panel_x = 750
        panel_y = 140
        panel_width = 220
        panel_height = 500
        pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 3)
        
        # 升级按钮
        upgrade_y = panel_y + 20
        upgrade_cost = self.shop_level * 500
        pygame.draw.rect(screen, ORANGE, (panel_x + 20, upgrade_y, 180, 50))
        pygame.draw.rect(screen, BLACK, (panel_x + 20, upgrade_y, 180, 50), 2)
        upgrade_text1 = font_small.render(f'升级商店', True, WHITE)
        upgrade_text2 = font_small.render(f'¥{upgrade_cost}', True, WHITE)
        screen.blit(upgrade_text1, (panel_x + 50, upgrade_y + 5))
        screen.blit(upgrade_text2, (panel_x + 70, upgrade_y + 28))
        
        # 暂停按钮
        pause_y = panel_y + 90
        pygame.draw.rect(screen, PURPLE, (panel_x + 20, pause_y, 180, 40))
        pygame.draw.rect(screen, BLACK, (panel_x + 20, pause_y, 180, 40), 2)
        pause_text = font_small.render('暂停' if not self.paused else '继续', True, WHITE)
        screen.blit(pause_text, (panel_x + 75, pause_y + 8))
        
        # 销售记录
        history_y = panel_y + 150
        history_title = font_small.render('销售记录:', True, BLACK)
        screen.blit(history_title, (panel_x + 20, history_y))
        
        record_y = history_y + 30
        for record in self.sales_history[-8:]:
            day, name, amount, revenue = record
            record_text = font_small.render(f'D{day}: {name} x{amount} ¥{revenue}', True, BLACK)
            screen.blit(record_text, (panel_x + 20, record_y))
            record_y += 25
        
        # 显示消息
        if self.message_timer > 0:
            self.message_timer -= 1
            text = font_medium.render(self.message, True, RED)
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT - 50))
            pygame.draw.rect(screen, WHITE, (text_rect.x - 10, text_rect.y - 10, text_rect.width + 20, text_rect.height + 20))
            screen.blit(text, text_rect)
        
        # 操作说明
        help_text = font_small.render('点击商品选择，操作右侧按钮', True, BLACK)
        screen.blit(help_text, (20, HEIGHT - 30))
    
    def handle_click(self, pos):
        x, y = pos
        
        # 检查商品区域
        for i in range(len(self.products)):
            px = 50 + (i % 2) * 450
            py = 140 + (i // 2) * 120
            
            if px <= x <= px + 400 and py <= y <= py + 100:
                self.selected_product = i
                
                # 检查价格调整按钮
                btn_x = px + 300
                btn_y = py + 30
                if btn_x <= x <= btn_x + 40 and btn_y <= y <= btn_y + 30:
                    self.change_price(i, -1)
                elif btn_x + 50 <= x <= btn_x + 90 and btn_y <= y <= btn_y + 30:
                    self.change_price(i, 1)
                
                # 检查采购按钮
                buy_btn_y = py + 65
                if btn_x <= x <= btn_x + 90 and buy_btn_y <= y <= buy_btn_y + 30:
                    self.buy_product(i, 10)
                return
        
        # 检查右侧面板按钮
        panel_x = 750
        panel_y = 140
        
        # 升级按钮
        if panel_x + 20 <= x <= panel_x + 200 and panel_y + 20 <= y <= panel_y + 70:
            self.upgrade_shop()
        
        # 暂停按钮
        if panel_x + 20 <= x <= panel_x + 200 and panel_y + 90 <= y <= panel_y + 130:
            self.paused = not self.paused
    
    def update(self):
        self.update_time()
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = ShopKeeper()
    game.run()
