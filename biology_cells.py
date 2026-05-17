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
pygame.display.set_caption("细胞工厂")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 150, 255)
GREEN = (50, 200, 100)
RED = (200, 50, 50)
YELLOW = (255, 200, 50)
PURPLE = (150, 50, 200)
ORANGE = (255, 150, 50)

cell_parts = {
    "nucleus": {"name": "细胞核", "color": RED, "x": 400, "y": 300, "size": 45, "desc": "遗传物质中心"},
    "mitochondria": {"name": "线粒体", "color": ORANGE, "x": 250, "y": 250, "size": 25, "desc": "能量工厂"},
    "ribosomes": {"name": "核糖体", "color": YELLOW, "x": 550, "y": 280, "size": 15, "desc": "蛋白质合成"},
    "golgi": {"name": "高尔基体", "color": PURPLE, "x": 500, "y": 400, "size": 30, "desc": "包装与运输"},
    "membrane": {"name": "细胞膜", "color": BLUE, "x": 400, "y": 300, "size": 130, "desc": "保护屏障"},
}

class CellFactory:
    def __init__(self):
        self.money = 50
        self.owned_parts = {"membrane": True}
        self.productivity = 1
        self.selected_part = None
        self.message = "欢迎来到细胞工厂！建造细胞器来生产蛋白质。"
        self.font = get_chinese_font(32)
        self.large_font = get_chinese_font(48)

    def update(self):
        income = 0
        if self.owned_parts.get("nucleus"):
            income += 1
        if self.owned_parts.get("mitochondria"):
            income += 2
        if self.owned_parts.get("ribosomes"):
            income += 3
        if self.owned_parts.get("golgi"):
            income += 4
        self.money += income / 60
        self.productivity = max(1, income)

    def draw(self):
        screen.fill((200, 240, 255))
        
        pygame.draw.circle(screen, (200, 240, 240), (400, 300), 150)
        
        for key, part in cell_parts.items():
            if self.owned_parts.get(key):
                pygame.draw.circle(screen, part["color"], (part["x"], part["y"]), part["size"])
                pygame.draw.circle(screen, BLACK, (part["x"], part["y"]), part["size"], 2)
                if self.selected_part == key:
                    pygame.draw.circle(screen, YELLOW, (part["x"], part["y"]), part["size"] + 5, 3)
        
        pygame.draw.circle(screen, (100, 200, 150), (400, 300), 145, 3)
        
        title_text = self.large_font.render("细胞工厂", True, BLUE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 10))
        
        money_text = self.font.render(f"蛋白质: {int(self.money)}", True, BLACK)
        screen.blit(money_text, (50, 10))
        
        productivity_text = self.font.render(f"生产率: {self.productivity}/秒", True, GREEN)
        screen.blit(productivity_text, (50, 45))
        
        for i, (key, part) in enumerate(cell_parts.items()):
            if self.owned_parts.get(key):
                continue
            button_y = 80 + i * 80
            button_x = 600
            cost = 10 * (i + 1)
            color = (200, 200, 255) if self.money >= cost else (200, 200, 200)
            pygame.draw.rect(screen, color, (button_x, button_y, 180, 70), border_radius=5)
            pygame.draw.rect(screen, BLACK, (button_x, button_y, 180, 70), 2, border_radius=5)
            name_text = self.font.render(f"购买 {part['name']}", True, BLACK)
            screen.blit(name_text, (button_x + 10, button_y + 10))
            cost_text = self.font.render(f"{cost} 蛋白质", True, BLUE)
            screen.blit(cost_text, (button_x + 30, button_y + 35))
        
        pygame.draw.rect(screen, (240, 240, 240), (50, 450, 500, 80), border_radius=10)
        pygame.draw.rect(screen, BLACK, (50, 450, 500, 80), 2, border_radius=10)
        msg_y = 455
        lines = self.wrap_text(self.message, 480)
        for line in lines:
            text = self.font.render(line, True, BLACK)
            screen.blit(text, (60, msg_y))
            msg_y += 30
        
        hint_text = self.font.render("点击右侧按钮购买细胞器", True, PURPLE)
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, 540))

    def wrap_text(self, text, max_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test = current_line + word + " "
            if self.font.size(test)[0] <= max_width:
                current_line = test
            else:
                lines.append(current_line)
                current_line = word + " "
        if current_line:
            lines.append(current_line)
        return lines

    def handle_click(self, pos):
        for i, (key, part) in enumerate(cell_parts.items()):
            if self.owned_parts.get(key):
                continue
            button_y = 80 + i * 80
            if 600 <= pos[0] <= 780 and button_y <= pos[1] <= button_y + 70:
                cost = 10 * (i + 1)
                if self.money >= cost:
                    self.money -= cost
                    self.owned_parts[key] = True
                    self.message = f"成功购买了{part['name']}！{part['desc']}！"
                else:
                    self.message = "蛋白质不够！"
                return
        
        for key, part in cell_parts.items():
            if self.owned_parts.get(key):
                dist = ((pos[0]-part["x"])**2 + (pos[1]-part["y"])**2)**0.5
                if dist < part["size"] + 10:
                    self.message = f"{part['name']}：{part['desc']}"
                    self.selected_part = key
                    return
        
        self.selected_part = None

game = CellFactory()
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
