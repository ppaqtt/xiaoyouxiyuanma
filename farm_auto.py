"""
农场自动种植
一个自动种植和收获的农场管理游戏
"""

import pygame
import os
import sys
import math

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

WIDTH, HEIGHT = 950, 680
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("农场自动种植")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (50, 50, 50)
BROWN = (139, 69, 19)
GREEN = (34, 139, 34)
LIGHT_GREEN = (50, 200, 50)
YELLOW = (255, 200, 50)
GOLD = (255, 215, 0)
BLUE = (30, 144, 255)

class Plant:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.growth = 0
        self.max_growth = 100
        self.watered = False
        self.plant_type = 0
    
    def grow(self):
        if self.watered:
            self.growth += 0.5
        else:
            self.growth += 0.2
        
        if self.growth > self.max_growth:
            self.growth = self.max_growth
    
    def harvest(self):
        if self.growth >= self.max_growth:
            return [10, 25, 50, 100][self.plant_type]
        return 0

class FarmGame:
    def __init__(self):
        self.money = 100
        self.plants = []
        self.auto_water = False
        self.auto_harvest = False
        self.auto_plant = False
        self.water_cost = 2
        self.water_timer = 0
        self.harvest_timer = 0
        self.plant_timer = 0
        self.font_large = get_chinese_font(64)
        self.font_medium = get_chinese_font(36)
        self.font_small = get_chinese_font(26)
        
        # 初始化土地
        for row in range(4):
            for col in range(8):
                x = 100 + col * 90
                y = 100 + row * 100
                self.plants.append(Plant(x, y))
    
    def update(self):
        self.water_timer += 1
        self.harvest_timer += 1
        self.plant_timer += 1
        
        # 自动浇水
        if self.auto_water and self.water_timer >= 120:
            self.water_timer = 0
            for plant in self.plants:
                plant.watered = True
        
        # 自动种植
        if self.auto_plant and self.plant_timer >= 180:
            self.plant_timer = 0
            self.auto_buy_seeds()
        
        # 自动收获
        if self.auto_harvest and self.harvest_timer >= 100:
            self.harvest_timer = 0
            for plant in self.plants:
                if plant.growth >= plant.max_growth:
                    amount = plant.harvest()
                    self.money += amount
                    plant.growth = 0
        
        # 生长
        for plant in self.plants:
            plant.grow()
    
    def auto_buy_seeds(self):
        for plant in self.plants:
            if plant.growth <= 0 and self.money >= 10:
                self.money -= 10
                plant.growth = 1
    
    def draw(self):
        screen.fill((100, 150, 100))
        
        # 天空和太阳
        pygame.draw.rect(screen, (135, 206, 250), (0, 0, WIDTH, 80))
        pygame.draw.circle(screen, YELLOW, (850, 40), 35)
        
        # 顶部状态栏
        pygame.draw.rect(screen, (200, 180, 100), (0, 80, WIDTH, 60))
        money_text = self.font_large.render(f"💰 {self.money}", True, GOLD)
        screen.blit(money_text, (50, 88))
        
        # 土地
        for i, plant in enumerate(self.plants):
            x = plant.x
            y = plant.y
            
            pygame.draw.rect(screen, BROWN, (x, y, 80, 90), border_radius=5)
            
            if plant.watered:
                pygame.draw.rect(screen, (100, 100, 50), (x + 5, y + 5, 70, 80), border_radius=3)
            
            if plant.growth > 0:
                progress = min(1.0, plant.growth / plant.max_growth)
                height = int(70 * progress)
                color = LIGHT_GREEN if progress < 1 else GOLD
                
                if progress > 0.3:
                    pygame.draw.rect(screen, color, (x + 35, y + 85 - height, 10, height))
                    pygame.draw.circle(screen, color, (x + 40, y + 85 - height), 12)
                
                if progress >= 1:
                    pygame.draw.circle(screen, GOLD, (x + 40, y + 10), 18)
        
        # 升级按钮
        buttons = [
            ("自动浇水", 200, self.auto_water, BLUE),
            ("自动收获", 500, self.auto_harvest, GREEN),
            ("自动种植", 800, self.auto_plant, PURPLE if 'PURPLE' in globals() else (150,50,200))
        ]
        
        costs = [500, 1000, 2000]
        for i, (name, x, active, color) in enumerate(buttons):
            cost = costs[i]
            btn_rect = pygame.Rect(x, 520, 180, 60)
            pygame.draw.rect(screen, color if active else GRAY, btn_rect, border_radius=10)
            
            name_text = self.font_medium.render(name, True, WHITE)
            cost_text = self.font_small.render(f"💰 {cost}", True, YELLOW)
            
            screen.blit(name_text, (x + 20, 525))
            screen.blit(cost_text, (x + 40, 555))
        
        # 购买种子按钮
        seed_btn = pygame.Rect(30, 520, 160, 60)
        pygame.draw.rect(screen, GREEN, seed_btn, border_radius=10)
        seed_text = self.font_medium.render("买种子", True, WHITE)
        cost_text = self.font_small.render("💰 10", True, YELLOW)
        screen.blit(seed_text, (55, 525))
        screen.blit(cost_text, (70, 555))
        
        # 说明
        instructions = [
            "点击土地浇水/收获",
            "购买升级来自动化"
        ]
        y = 600
        for line in instructions:
            text = self.font_small.render(line, True, WHITE)
            screen.blit(text, (30, y))
            y += 25
        
        pygame.display.flip()
    
    def handle_click(self, pos):
        # 升级按钮
        buttons = [
            ("water", 200, 500),
            ("harvest", 500, 1000),
            ("plant", 800, 2000)
        ]
        
        for name, x, cost in buttons:
            btn_rect = pygame.Rect(x, 520, 180, 60)
            if btn_rect.collidepoint(pos):
                if self.money >= cost:
                    self.money -= cost
                    if name == "water":
                        self.auto_water = True
                    elif name == "harvest":
                        self.auto_harvest = True
                    elif name == "plant":
                        self.auto_plant = True
                return
        
        # 买种子
        seed_btn = pygame.Rect(30, 520, 160, 60)
        if seed_btn.collidepoint(pos):
            if self.money >= 10:
                for plant in self.plants:
                    if plant.growth <= 0:
                        self.money -= 10
                        plant.growth = 1
                        break
                return
        
        # 点击土地
        for plant in self.plants:
            rect = pygame.Rect(plant.x, plant.y, 80, 90)
            if rect.collidepoint(pos):
                if plant.growth >= plant.max_growth:
                    amount = plant.harvest()
                    self.money += amount
                    plant.growth = 0
                else:
                    plant.watered = True
                    if self.money >= self.water_cost:
                        self.money -= self.water_cost
                return

def main():
    game = FarmGame()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        game.update()
        game.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
