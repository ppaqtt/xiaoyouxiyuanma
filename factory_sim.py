"""
工厂生产线模拟
建立并优化你的工厂生产线！
"""

import pygame
import os
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

WIDTH, HEIGHT = 1000, 680
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("工厂生产线模拟")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (40, 40, 50)
BLUE = (0, 120, 220)
GREEN = (0, 200, 100)
RED = (220, 60, 60)
ORANGE = (255, 140, 0)
PURPLE = (150, 50, 200)
YELLOW = (255, 215, 0)
BROWN = (139, 69, 19)

class Machine:
    def __init__(self, x, y, m_type):
        self.x = x
        self.y = y
        self.type = m_type
        self.progress = 0
        self.working = False
        self.has_item = False
        
    def update(self):
        if self.working and self.has_item:
            self.progress += 1
            if self.progress >= 100:
                self.progress = 0
                self.has_item = False
                return True
        return False

class FactoryGame:
    def __init__(self):
        self.money = 500
        self.machines = []
        self.items = []
        self.item_value = 10
        self.raw_materials = 100
        self.production_rate = 0
        self.auto_sell = False
        self.font_large = get_chinese_font(60)
        self.font_medium = get_chinese_font(32)
        self.font_small = get_chinese_font(24)
        self.init_factory()
    
    def init_factory(self):
        # 初始机器布局
        self.machines = [
            Machine(100, 200, "miner"),
            Machine(250, 200, "conveyor"),
            Machine(400, 200, "processor"),
            Machine(550, 200, "conveyor"),
            Machine(700, 200, "packager"),
            Machine(850, 200, "seller")
        ]
    
    def update(self):
        # 更新机器
        produced = 0
        
        for i, machine in enumerate(self.machines):
            if machine.type == "miner":
                if self.raw_materials > 0 and not machine.has_item:
                    machine.has_item = True
                    machine.working = True
                    self.raw_materials -= 1
            
            result = machine.update()
            
            if result:
                if i < len(self.machines) - 1:
                    next_m = self.machines[i + 1]
                    if not next_m.has_item:
                        next_m.has_item = True
                        next_m.working = True
                elif machine.type == "seller":
                    produced += 1
        
        if produced > 0:
            if self.auto_sell:
                self.money += produced * self.item_value
            else:
                # 暂时存储
                pass
        
        # 生产统计
        self.production_rate = produced
        
        # 自动补充原材料（如果有钱）
        if self.raw_materials < 10 and self.money >= 50:
            self.money -= 50
            self.raw_materials += 100
    
    def draw(self):
        screen.fill(DARK_GRAY)
        
        # 顶部状态栏
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 70))
        
        money_text = self.font_large.render(f"💰 {self.money}", True, YELLOW)
        screen.blit(money_text, (30, 10))
        
        mat_text = self.font_medium.render(f"原材料: {self.raw_materials}", True, ORANGE)
        screen.blit(mat_text, (300, 20))
        
        rate_text = self.font_medium.render(f"生产: {self.production_rate}/s", True, GREEN)
        screen.blit(rate_text, (600, 20))
        
        # 工厂地板
        pygame.draw.rect(screen, (80, 80, 90), (0, 70, WIDTH, HEIGHT - 200))
        
        # 画机器
        for i, machine in enumerate(self.machines):
            colors = {
                "miner": BROWN,
                "conveyor": GRAY,
                "processor": BLUE,
                "packager": GREEN,
                "seller": RED
            }
            
            color = colors.get(machine.type, PURPLE)
            
            rect = pygame.Rect(machine.x, machine.y, 120, 100)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, rect, 3, border_radius=10)
            
            # 机器名称
            names = {
                "miner": "采矿机",
                "conveyor": "传送带",
                "processor": "加工机",
                "packager": "包装机",
                "seller": "售卖机"
            }
            name = self.font_small.render(names.get(machine.type, "机器"), True, WHITE)
            screen.blit(name, (machine.x + 20, machine.y + 35))
            
            # 进度条
            if machine.working and machine.has_item:
                pygame.draw.rect(screen, DARK_GRAY, (machine.x + 10, machine.y + 70, 100, 15))
                pygame.draw.rect(screen, YELLOW, (machine.x + 10, machine.y + 70, 
                                               int(100 * (machine.progress / 100)), 15))
            
            # 物品
            if machine.has_item:
                pygame.draw.circle(screen, (255, 255, 150), (machine.x + 60, machine.y + 50), 12)
        
        # 底部升级面板
        pygame.draw.rect(screen, BLACK, (0, HEIGHT - 130, WIDTH, 130))
        
        upgrades = [
            ("购买原材料", 50, 30),
            ("升级加工速度", 200, 280),
            ("自动售卖", 1000, 530)
        ]
        
        for name, cost, x in upgrades:
            btn_rect = pygame.Rect(x, HEIGHT - 110, 230, 80)
            color = GREEN if (name == "自动售卖" and self.auto_sell) or self.money >= cost else GRAY
            
            pygame.draw.rect(screen, color, btn_rect, border_radius=10)
            
            name_text = self.font_medium.render(name, True, WHITE)
            cost_text = self.font_small.render(f"💰 {cost}", True, YELLOW)
            
            screen.blit(name_text, (x + 20, HEIGHT - 100))
            screen.blit(cost_text, (x + 40, HEIGHT - 65))
        
        pygame.display.flip()
    
    def handle_click(self, pos):
        # 升级按钮
        upgrades = [
            ("material", 50, 30),
            ("speed", 200, 280),
            ("auto", 1000, 530)
        ]
        
        for name, cost, x in upgrades:
            btn_rect = pygame.Rect(x, HEIGHT - 110, 230, 80)
            if btn_rect.collidepoint(pos):
                if self.money >= cost:
                    self.money -= cost
                    if name == "material":
                        self.raw_materials += 200
                    elif name == "speed":
                        self.item_value *= 2
                    elif name == "auto":
                        self.auto_sell = True
                return

def main():
    game = FactoryGame()
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
