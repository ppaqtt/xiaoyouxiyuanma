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
pygame.display.set_caption("农场大亨")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
BROWN = (139, 90, 43)
YELLOW = (255, 200, 50)
RED = (200, 50, 50)
BLUE = (50, 100, 255)
ORANGE = (255, 150, 50)

crops = [
    {"name": "小麦", "cost": 10, "time": 3, "income": 15, "color": YELLOW},
    {"name": "玉米", "cost": 25, "time": 5, "income": 40, "color": YELLOW},
    {"name": "胡萝卜", "cost": 15, "time": 4, "income": 25, "color": ORANGE},
    {"name": "西红柿", "cost": 30, "time": 7, "income": 55, "color": RED},
    {"name": "向日葵", "cost": 50, "time": 10, "income": 100, "color": YELLOW},
]

class FarmGame:
    def __init__(self):
        self.money = 100
        self.farm_spots = [{"crop": None, "time_left": 0} for _ in range(9)]
        self.hired_workers = 0
        self.worker_cost = 50
        self.font = get_chinese_font(32)
        self.large_font = get_chinese_font(48)
        self.selected_shop = 0

    def update(self):
        for spot in self.farm_spots:
            if spot["time_left"] > 0:
                spot["time_left"] -= 0.016
            if spot["time_left"] <= 0 and spot["crop"] is not None:
                self.money += spot["crop"]["income"]
                spot["crop"] = None

    def draw(self):
        screen.fill(GREEN)
        
        pygame.draw.rect(screen, (200, 240, 200), (0, 0, 800, 80))
        title_text = self.large_font.render("农场大亨", True, BLACK)
        screen.blit(title_text, (300, 20))
        
        money_text = self.font.render(f"金币: {int(self.money)}", True, BLACK)
        screen.blit(money_text, (30, 90))
        
        worker_text = self.font.render(f"工人: {self.hired_workers}", True, BLACK)
        screen.blit(worker_text, (250, 90))
        
        for i in range(3):
            for j in range(3):
                x = 100 + j * 200
                y = 180 + i * 110
                spot = self.farm_spots[i*3 + j]
                color = BROWN if spot["crop"] is None else spot["crop"]["color"]
                pygame.draw.rect(screen, color, (x, y, 180, 90), border_radius=5)
                pygame.draw.rect(screen, BLACK, (x, y, 180, 90), 2, border_radius=5)
                
                if spot["crop"]:
                    name = self.font.render(spot["crop"]["name"], True, BLACK)
                    screen.blit(name, (x+20, y+25))
                    progress = max(0, 100 - spot["time_left"]/spot["crop"]["time"] * 100)
                    pygame.draw.rect(screen, (200, 200, 200), (x+20, y+55, 140, 20))
                    pygame.draw.rect(screen, GREEN, (x+20, y+55, 140 * progress/100, 20))
                else:
                    hint = self.font.render("点击种植", True, (100, 100, 100))
                    screen.blit(hint, (x+35, y+35))
        
        pygame.draw.rect(screen, (240, 240, 240), (550, 150, 230, 420), border_radius=10)
        pygame.draw.rect(screen, BLACK, (550, 150, 230, 420), 2, border_radius=10)
        
        shop_title = self.font.render("商店", True, BLACK)
        screen.blit(shop_title, (620, 165))
        
        for i, crop in enumerate(crops):
            button_y = 200 + i * 50
            pygame.draw.rect(screen, (200, 220, 255), (560, button_y, 210, 45), border_radius=3)
            pygame.draw.rect(screen, BLACK, (560, button_y, 210, 45), 2, border_radius=3)
            crop_name = self.font.render(crop["name"], True, BLACK)
            screen.blit(crop_name, (570, button_y+5))
            crop_info = self.font.render(f"¥{crop['cost']} → ¥{crop['income']}", True, (100, 100, 100))
            screen.blit(crop_info, (570, button_y+22))
        
        hire_text = self.font.render(f"雇佣工人 ¥{self.worker_cost}", True, BLACK)
        pygame.draw.rect(screen, (200, 255, 200), (560, 450, 210, 45), border_radius=3)
        pygame.draw.rect(screen, BLACK, (560, 450, 210, 45), 2, border_radius=3)
        screen.blit(hire_text, (570, 458))
        
        hint_text = self.font.render("点击商店选择作物，再点击农田种植", True, BLUE)
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, 550))

    def handle_click(self, pos):
        for i in range(3):
            for j in range(3):
                x = 100 + j * 200
                y = 180 + i * 110
                if x <= pos[0] <= x+180 and y <= pos[1] <= y+90:
                    idx = i*3 + j
                    if self.farm_spots[idx]["crop"] is None:
                        crop = crops[self.selected_shop]
                        if self.money >= crop["cost"]:
                            self.money -= crop["cost"]
                            self.farm_spots[idx]["crop"] = crop
                            self.farm_spots[idx]["time_left"] = crop["time"]
        
        for i, crop in enumerate(crops):
            if 560 <= pos[0] <= 770 and 200 + i*50 <= pos[1] <= 245 + i*50:
                self.selected_shop = i
        
        if 560 <= pos[0] <= 770 and 450 <= pos[1] <= 495:
            if self.money >= self.worker_cost:
                self.money -= self.worker_cost
                self.hired_workers += 1
                self.worker_cost *= 1.5

game = FarmGame()
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
