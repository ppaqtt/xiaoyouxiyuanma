import pygame
import os
import random
import sys

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

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("挖矿大亨")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BROWN = (139, 90, 43)
GOLD = (255, 200, 50)
DIAMOND = (100, 255, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)

ores = [
    {"name": "煤炭", "color": (50, 50, 50), "value": 2, "rarity": 1.0},
    {"name": "铜矿", "color": (200, 120, 50), "value": 5, "rarity": 0.7},
    {"name": "铁矿", "color": (180, 100, 80), "value": 8, "rarity": 0.5},
    {"name": "银矿", "color": (200, 200, 220), "value": 15, "rarity": 0.3},
    {"name": "金矿", "color": GOLD, "value": 25, "rarity": 0.15},
    {"name": "钻石", "color": DIAMOND, "value": 100, "rarity": 0.05},
]

upgrades = [
    {"name": "镐子升级", "cost": 50, "effect": "power", "level": 0, "max_level": 5},
    {"name": "矿工速度", "cost": 80, "effect": "speed", "level": 0, "max_level": 5},
    {"name": "幸运加成", "cost": 120, "effect": "luck", "level": 0, "max_level": 5},
]

class MiningGame:
    def __init__(self):
        self.money = 100
        self.power = 1
        self.speed = 1
        self.luck = 1
        self.miners = 1
        self.mining_progress = 0
        self.current_ore = None
        self.storage = {ore["name"]: 0 for ore in ores}
        self.font = get_chinese_font(32)
        self.large_font = get_chinese_font(48)

    def mine_ore(self):
        luck_factor = 1 + (self.luck - 1) * 0.1
        roll = random.random()
        
        for i in reversed(range(len(ores))):
            ore = ores[i]
            if roll < ore["rarity"] * luck_factor:
                return ore
        
        return ores[0]

    def update(self):
        self.mining_progress += 0.002 * self.speed * self.miners
        
        if self.mining_progress >= 1:
            self.mining_progress = 0
            ore = self.mine_ore()
            count = self.power
            self.storage[ore["name"]] += count

    def draw(self):
        screen.fill((200, 160, 120))
        
        pygame.draw.rect(screen, (100, 60, 30), (0, 250, 800, 350))
        
        pygame.draw.rect(screen, (240, 240, 240), (0, 0, 800, 80))
        pygame.draw.rect(screen, BLACK, (0, 0, 800, 80), 2)
        
        title_text = self.large_font.render("挖矿大亨", True, BLACK)
        screen.blit(title_text, (320, 20))
        
        money_text = self.font.render(f"资金: ¥{int(self.money)}", True, BLACK)
        screen.blit(money_text, (30, 90))
        
        progress = int(self.mining_progress * 100)
        pygame.draw.rect(screen, (200, 200, 200), (30, 130, 300, 25))
        pygame.draw.rect(screen, GREEN, (30, 130, 300 * self.mining_progress, 25))
        pygame.draw.rect(screen, BLACK, (30, 130, 300, 25), 2)
        
        pygame.draw.rect(screen, (240, 240, 240), (550, 90, 230, 450), border_radius=10)
        pygame.draw.rect(screen, BLACK, (550, 90, 230, 450), 2, border_radius=10)
        
        shop_title = self.font.render("升级商店", True, BLACK)
        screen.blit(shop_title, (610, 105))
        
        for i, upgrade in enumerate(upgrades):
            button_y = 145 + i * 70
            cost = int(upgrade["cost"] * (1.5 ** upgrade["level"]))
            color = (200, 255, 200) if self.money >= cost and upgrade["level"] < upgrade["max_level"] else (200, 200, 200)
            pygame.draw.rect(screen, color, (560, button_y, 210, 65), border_radius=5)
            pygame.draw.rect(screen, BLACK, (560, button_y, 210, 65), 2, border_radius=5)
            
            name_text = self.font.render(f"{upgrade['name']} Lv{upgrade['level']}", True, BLACK)
            screen.blit(name_text, (570, button_y+8))
            
            if upgrade["level"] < upgrade["max_level"]:
                cost_text = self.font.render(f"¥{cost}", True, RED)
                screen.blit(cost_text, (570, button_y+35))
            else:
                max_text = self.font.render("已满级", True, GRAY)
                screen.blit(max_text, (570, button_y+35))
        
        storage_y = 180
        storage_text = self.font.render("仓库:", True, BLACK)
        screen.blit(storage_text, (30, storage_y))
        storage_y += 35
        
        for i, ore in enumerate(ores):
            text = self.font.render(f"{ore['name']}: {self.storage[ore['name']]}", True, BLACK)
            pygame.draw.rect(screen, ore["color"], (20, storage_y-3, 15, 15))
            screen.blit(text, (45, storage_y-8))
            storage_y += 30
        
        pygame.draw.rect(screen, BLUE, (30, storage_y, 180, 40), border_radius=5)
        pygame.draw.rect(screen, BLACK, (30, storage_y, 180, 40), 2, border_radius=5)
        sell_text = self.font.render("全部出售", True, WHITE)
        screen.blit(sell_text, (70, storage_y+8))
        
        miner_btn_y = 510
        miner_cost = int(100 * (1.5 ** (self.miners - 1)))
        color = (200, 220, 255) if self.money >= miner_cost else (200, 200, 200)
        pygame.draw.rect(screen, color, (560, miner_btn_y, 210, 55), border_radius=5)
        pygame.draw.rect(screen, BLACK, (560, miner_btn_y, 210, 55), 2, border_radius=5)
        miner_text = self.font.render(f"雇佣矿工 ¥{miner_cost}", True, BLACK)
        screen.blit(miner_text, (570, miner_btn_y+15))
        
        miners_count = self.font.render(f"矿工: {self.miners}", True, BLACK)
        screen.blit(miners_count, (280, 90))

    def handle_click(self, pos):
        for i, upgrade in enumerate(upgrades):
            button_y = 145 + i * 70
            if 560 <= pos[0] <= 770 and button_y <= pos[1] <= button_y + 65:
                if upgrade["level"] < upgrade["max_level"]:
                    cost = int(upgrade["cost"] * (1.5 ** upgrade["level"]))
                    if self.money >= cost:
                        self.money -= cost
                        upgrade["level"] += 1
                        if upgrade["effect"] == "power":
                            self.power = upgrade["level"] + 1
                        elif upgrade["effect"] == "speed":
                            self.speed = upgrade["level"] + 1
                        elif upgrade["effect"] == "luck":
                            self.luck = upgrade["level"] + 1
        
        miner_cost = int(100 * (1.5 ** (self.miners - 1)))
        if 560 <= pos[0] <= 770 and 510 <= pos[1] <= 565:
            if self.money >= miner_cost:
                self.money -= miner_cost
                self.miners += 1
        
        if 30 <= pos[0] <= 210 and 330 <= pos[1] <= 370:
            total = 0
            for ore in ores:
                total += self.storage[ore["name"]] * ore["value"]
            self.money += total
            for ore in ores:
                self.storage[ore["name"]] = 0

game = MiningGame()
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            game.handle_click(pygame.mouse.get_pos())
    
    game.update()
    game.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
