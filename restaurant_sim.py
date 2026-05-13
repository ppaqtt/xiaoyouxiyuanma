#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
餐厅模拟器 - Restaurant Simulator
操作说明：
- 使用鼠标点击菜单按钮进行操作
- 点击食材进行采购
- 点击客人进行点餐服务
- 升级装饰和设施提升满意度
"""

import pygame
import sys
import random
import math
from pygame.locals import *

# 初始化pygame
pygame.init()

# 游戏窗口设置
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('餐厅模拟器')

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
YELLOW = (255, 200, 50)
BROWN = (139, 69, 19)
LIGHT_BROWN = (210, 180, 140)
PINK = (255, 192, 203)

# 字体设置
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

class RestaurantSimulator:
    def __init__(self):
        # 游戏状态
        self.money = 500
        self.day = 1
        self.hour = 9
        self.minute = 0
        self.game_speed = 1
        self.paused = False
        
        # 餐厅属性
        self.satisfaction = 50  # 顾客满意度 0-100
        self.decoration_level = 1
        self.kitchen_level = 1
        
        # 菜单 {菜品: 价格, 成本}
        self.menu = {
            '炒饭': {'price': 25, 'cost': 10, 'time': 3},
            '面条': {'price': 20, 'cost': 8, 'time': 2},
            '汉堡': {'price': 30, 'cost': 12, 'time': 4},
            '沙拉': {'price': 18, 'cost': 6, 'time': 2},
            '咖啡': {'price': 15, 'cost': 4, 'time': 1}
        }
        
        # 食材库存 {食材: 数量, 成本}
        self.ingredients = {
            '米': {'stock': 50, 'cost': 3},
            '面': {'stock': 50, 'cost': 2},
            '肉': {'stock': 30, 'cost': 5},
            '蔬菜': {'stock': 40, 'cost': 3},
            '面包': {'stock': 30, 'cost': 2},
            '咖啡豆': {'stock': 20, 'cost': 4}
        }
        
        # 食材与菜品的对应关系
        self.recipe = {
            '炒饭': ['米', '肉', '蔬菜'],
            '面条': ['面', '肉', '蔬菜'],
            '汉堡': ['面包', '肉', '蔬菜'],
            '沙拉': ['蔬菜'],
            '咖啡': ['咖啡豆']
        }
        
        # 客人列表
        self.customers = []
        self.customer_id = 0
        
        # 订单列表
        self.orders = []
        self.order_id = 0
        
        # 烹饪中的菜品
        self.cooking = []
        
        # UI状态
        self.current_tab = 'main'
        self.selected_item = None
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
            if self.hour >= 22:
                self.end_day()
            elif self.hour >= 10 and self.hour <= 20:
                self.spawn_customer()
    
    def spawn_customer(self):
        if random.random() < 0.1 * self.game_speed and len(self.customers) < 8:
            self.customer_id += 1
            customer = {
                'id': self.customer_id,
                'x': 100 + random.randint(0, 500),
                'y': 200 + random.randint(0, 150),
                'patience': 100,
                'order': None,
                'satisfied': False,
                'color': (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            }
            self.customers.append(customer)
    
    def customer_order(self, customer):
        if customer['order']:
            return
        
        available_dishes = [dish for dish in self.menu.keys() if self.check_ingredients(dish)]
        if available_dishes:
            dish = random.choice(available_dishes)
            customer['order'] = dish
            self.order_id += 1
            self.orders.append({
                'id': self.order_id,
                'customer_id': customer['id'],
                'dish': dish,
                'time_left': self.menu[dish]['time'] * 60
            })
            self.show_message(f'客人点了 {dish}！')
            self.use_ingredients(dish)
        else:
            customer['patience'] -= 2
    
    def check_ingredients(self, dish):
        if dish not in self.recipe:
            return False
        for ing in self.recipe[dish]:
            if self.ingredients[ing]['stock'] <= 0:
                return False
        return True
    
    def use_ingredients(self, dish):
        for ing in self.recipe[dish]:
            self.ingredients[ing]['stock'] -= 1
    
    def cook(self):
        to_remove = []
        for order in self.orders:
            order['time_left'] -= self.game_speed
            if order['time_left'] <= 0:
                to_remove.append(order)
                for customer in self.customers:
                    if customer['id'] == order['customer_id']:
                        customer['satisfied'] = True
                        self.money += self.menu[order['dish']]['price']
                        satisfaction_bonus = 5 + self.decoration_level * 2
                        self.satisfaction = min(100, self.satisfaction + satisfaction_bonus)
                        self.show_message(f'完成 {order["dish"]}，收入 {self.menu[order["dish"]]["price"]} 元！')
        
        for order in to_remove:
            self.orders.remove(order)
    
    def update_customers(self):
        to_remove = []
        for customer in self.customers:
            if not customer['order']:
                self.customer_order(customer)
            else:
                customer['patience'] -= 0.1 * self.game_speed
            
            if customer['satisfied']:
                to_remove.append(customer)
            elif customer['patience'] <= 0:
                to_remove.append(customer)
                self.satisfaction = max(0, self.satisfaction - 10)
                self.show_message('客人失去耐心离开了！')
        
        for customer in to_remove:
            if customer in self.customers:
                self.customers.remove(customer)
    
    def buy_ingredient(self, ing):
        cost = self.ingredients[ing]['cost'] * 10
        if self.money >= cost:
            self.money -= cost
            self.ingredients[ing]['stock'] += 10
            self.show_message(f'购买了 10 份 {ing}，花费 {cost} 元')
        else:
            self.show_message('金钱不足！')
    
    def upgrade_decoration(self):
        cost = self.decoration_level * 200
        if self.money >= cost and self.decoration_level < 5:
            self.money -= cost
            self.decoration_level += 1
            self.show_message(f'装饰升级到 {self.decoration_level} 级！')
        elif self.decoration_level >= 5:
            self.show_message('装饰已达最高级！')
        else:
            self.show_message('金钱不足！')
    
    def upgrade_kitchen(self):
        cost = self.kitchen_level * 300
        if self.money >= cost and self.kitchen_level < 5:
            self.money -= cost
            self.kitchen_level += 1
            self.game_speed = min(3, self.kitchen_level)
            self.show_message(f'厨房升级到 {self.kitchen_level} 级，烹饪速度提升！')
        elif self.kitchen_level >= 5:
            self.show_message('厨房已达最高级！')
        else:
            self.show_message('金钱不足！')
    
    def end_day(self):
        self.hour = 9
        self.minute = 0
        self.day += 1
        self.customers = []
        self.orders = []
        self.show_message(f'第 {self.day} 天开始了！')
    
    def draw(self):
        screen.fill(LIGHT_BROWN)
        
        # 绘制餐厅区域
        pygame.draw.rect(screen, BROWN, (50, 150, 700, 400))
        pygame.draw.rect(screen, (160, 82, 45), (50, 150, 700, 400), 5)
        
        # 绘制装饰
        if self.decoration_level >= 1:
            pygame.draw.circle(screen, YELLOW, (400, 350), 30 + self.decoration_level * 10)
        
        # 绘制客人
        for customer in self.customers:
            pygame.draw.circle(screen, customer['color'], (int(customer['x']), int(customer['y'])), 25)
            pygame.draw.circle(screen, BLACK, (int(customer['x'] - 8), int(customer['y'] - 5)), 5)
            pygame.draw.circle(screen, BLACK, (int(customer['x'] + 8), int(customer['y'] - 5)), 5)
            
            # 耐心条
            patience_width = 40 * (customer['patience'] / 100)
            pygame.draw.rect(screen, RED, (customer['x'] - 20, customer['y'] - 45, 40, 8))
            pygame.draw.rect(screen, GREEN, (customer['x'] - 20, customer['y'] - 45, patience_width, 8))
            
            # 订单显示
            if customer['order']:
                text = font_small.render(customer['order'], True, BLACK)
                screen.blit(text, (customer['x'] - 20, customer['y'] + 30))
        
        # 绘制顶部状态栏
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 100))
        pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, 100), 3)
        
        money_text = font_medium.render(f'金钱: ¥{self.money}', True, GREEN)
        day_text = font_medium.render(f'第 {self.day} 天', True, BLACK)
        time_text = font_medium.render(f'{self.hour:02d}:{self.minute:02d}', True, BLACK)
        satisfaction_text = font_medium.render(f'满意度: {self.satisfaction}%', True, BLUE)
        
        screen.blit(money_text, (20, 20))
        screen.blit(day_text, (200, 20))
        screen.blit(time_text, (350, 20))
        screen.blit(satisfaction_text, (500, 20))
        
        # 绘制按钮区域
        button_y = 120
        button_width = 120
        button_height = 40
        spacing = 10
        
        buttons = [
            ('食材', 'ingredients', 50),
            ('菜单', 'menu', 180),
            ('升级', 'upgrade', 310),
            ('暂停', 'pause', 440)
        ]
        
        for text, tab, x in buttons:
            color = YELLOW if self.current_tab == tab else GRAY
            pygame.draw.rect(screen, color, (x, button_y, button_width, button_height))
            pygame.draw.rect(screen, BLACK, (x, button_y, button_width, button_height), 2)
            text_surf = font_small.render(text, True, BLACK)
            text_rect = text_surf.get_rect(center=(x + button_width//2, button_y + button_height//2))
            screen.blit(text_surf, text_rect)
        
        # 绘制侧边面板
        panel_x = 770
        panel_y = 150
        panel_width = 200
        panel_height = 500
        pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 3)
        
        if self.current_tab == 'ingredients':
            self.draw_ingredients_panel(panel_x, panel_y, panel_width)
        elif self.current_tab == 'menu':
            self.draw_menu_panel(panel_x, panel_y, panel_width)
        elif self.current_tab == 'upgrade':
            self.draw_upgrade_panel(panel_x, panel_y, panel_width)
        
        # 显示消息
        if self.message_timer > 0:
            self.message_timer -= 1
            text = font_medium.render(self.message, True, RED)
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT - 50))
            pygame.draw.rect(screen, WHITE, (text_rect.x - 10, text_rect.y - 10, text_rect.width + 20, text_rect.height + 20))
            screen.blit(text, text_rect)
        
        # 绘制操作说明
        help_text = font_small.render('点击按钮操作，服务客人获得收入！', True, BLACK)
        screen.blit(help_text, (20, HEIGHT - 30))
    
    def draw_ingredients_panel(self, x, y, width):
        title = font_medium.render('食材采购', True, BLACK)
        screen.blit(title, (x + 20, y + 20))
        
        y_offset = 60
        for ing, data in self.ingredients.items():
            pygame.draw.rect(screen, GRAY, (x + 10, y + y_offset, width - 20, 45))
            pygame.draw.rect(screen, BLACK, (x + 10, y + y_offset, width - 20, 45), 2)
            
            text1 = font_small.render(f'{ing} - 库存: {data["stock"]}', True, BLACK)
            text2 = font_small.render(f'买10份: ¥{data["cost"] * 10}', True, BLACK)
            screen.blit(text1, (x + 20, y + y_offset + 5))
            screen.blit(text2, (x + 20, y + y_offset + 25))
            
            y_offset += 55
    
    def draw_menu_panel(self, x, y, width):
        title = font_medium.render('菜单', True, BLACK)
        screen.blit(title, (x + 20, y + 20))
        
        y_offset = 60
        for dish, data in self.menu.items():
            pygame.draw.rect(screen, PINK, (x + 10, y + y_offset, width - 20, 50))
            pygame.draw.rect(screen, BLACK, (x + 10, y + y_offset, width - 20, 50), 2)
            
            text1 = font_small.render(dish, True, BLACK)
            text2 = font_small.render(f'售价: ¥{data["price"]}', True, BLACK)
            screen.blit(text1, (x + 20, y + y_offset + 5))
            screen.blit(text2, (x + 20, y + y_offset + 28))
            
            y_offset += 60
    
    def draw_upgrade_panel(self, x, y, width):
        title = font_medium.render('升级', True, BLACK)
        screen.blit(title, (x + 20, y + 20))
        
        # 装饰升级
        dec_cost = self.decoration_level * 200
        pygame.draw.rect(screen, YELLOW, (x + 10, y + 60, width - 20, 60))
        pygame.draw.rect(screen, BLACK, (x + 10, y + 60, width - 20, 60), 2)
        text1 = font_small.render(f'装饰等级: {self.decoration_level}/5', True, BLACK)
        text2 = font_small.render(f'升级: ¥{dec_cost}', True, BLACK)
        screen.blit(text1, (x + 20, y + 65))
        screen.blit(text2, (x + 20, y + 90))
        
        # 厨房升级
        kit_cost = self.kitchen_level * 300
        pygame.draw.rect(screen, BLUE, (x + 10, y + 130, width - 20, 60))
        pygame.draw.rect(screen, BLACK, (x + 10, y + 130, width - 20, 60), 2)
        text3 = font_small.render(f'厨房等级: {self.kitchen_level}/5', True, WHITE)
        text4 = font_small.render(f'升级: ¥{kit_cost}', True, WHITE)
        screen.blit(text3, (x + 20, y + 135))
        screen.blit(text4, (x + 20, y + 160))
    
    def handle_click(self, pos):
        x, y = pos
        
        # 按钮区域
        button_y = 120
        button_width = 120
        button_height = 40
        
        buttons = [
            ('ingredients', 50),
            ('menu', 180),
            ('upgrade', 310),
            ('pause', 440)
        ]
        
        for tab, bx in buttons:
            if bx <= x <= bx + button_width and button_y <= y <= button_y + button_height:
                if tab == 'pause':
                    self.paused = not self.paused
                else:
                    self.current_tab = tab
                return
        
        # 食材面板点击
        if self.current_tab == 'ingredients' and 770 <= x <= 970:
            y_offset = 150 + 60
            for ing in self.ingredients.keys():
                if y_offset <= y <= y_offset + 45:
                    self.buy_ingredient(ing)
                    return
                y_offset += 55
        
        # 升级面板点击
        if self.current_tab == 'upgrade' and 770 <= x <= 970:
            if 210 <= y <= 270:
                self.upgrade_decoration()
            elif 280 <= y <= 340:
                self.upgrade_kitchen()
    
    def update(self):
        self.update_time()
        self.update_customers()
        self.cook()
    
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
    game = RestaurantSimulator()
    game.run()
