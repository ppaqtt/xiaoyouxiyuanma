"""
点击英雄挂机
经典的放置挂机游戏
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

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("点击英雄挂机")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (40, 40, 50)
BLUE = (0, 120, 220)
GREEN = (0, 200, 100)
RED = (220, 60, 60)
GOLD = (255, 200, 50)
PURPLE = (150, 50, 200)

class Game:
    def __init__(self):
        self.gold = 0
        self.damage = 1
        self.auto_damage = 0
        self.level = 1
        self.enemy_hp = 10
        self.enemy_max_hp = 10
        self.kills = 0
        self.font_large = get_chinese_font(64)
        self.font_medium = get_chinese_font(36)
        self.font_small = get_chinese_font(28)
        
        self.upgrades = [
            {"name": "铁剑", "cost": 10, "damage": 1, "count": 0},
            {"name": "钢剑", "cost": 50, "damage": 5, "count": 0},
            {"name": "魔法剑", "cost": 200, "damage": 20, "count": 0},
            {"name": "学徒", "cost": 100, "auto": 1, "count": 0},
            {"name": "战士", "cost": 500, "auto": 10, "count": 0},
            {"name": "法师", "cost": 2000, "auto": 50, "count": 0}
        ]
        
        self.particles = []
        self.last_auto = 0
    
    def update(self):
        now = pygame.time.get_ticks()
        
        # 自动攻击
        if now - self.last_auto >= 1000:
            if self.auto_damage > 0:
                self.deal_damage(self.auto_damage, False)
            self.last_auto = now
        
        # 更新粒子
        new_particles = []
        for p in self.particles:
            p[0] += p[3]
            p[1] -= 1
            p[2] -= 0.02
            if p[2] > 0:
                new_particles.append(p)
        self.particles = new_particles
    
    def deal_damage(self, dmg, click=True):
        self.enemy_hp -= dmg
        
        if click:
            self.particles.append([400 + (10 - 20 * (pygame.time.get_ticks() % 2)), 
                                250, 1.0, 
                                (pygame.time.get_ticks() % 20 - 10) / 10])
        
        if self.enemy_hp <= 0:
            self.kills += 1
            self.gold += int(math.sqrt(self.level) * 10)
            self.level += 1
            self.enemy_max_hp = 10 + int(self.level ** 1.5 * 5)
            self.enemy_hp = self.enemy_max_hp
    
    def draw(self):
        screen.fill(DARK_GRAY)
        
        # 顶部状态栏
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 80))
        
        gold_text = self.font_large.render(f"💰 {self.gold}", True, GOLD)
        screen.blit(gold_text, (30, 15))
        
        level_text = self.font_medium.render(f"Level {self.level}", True, WHITE)
        screen.blit(level_text, (WIDTH - 250, 15))
        
        kills_text = self.font_medium.render(f"击杀: {self.kills}", True, RED)
        screen.blit(kills_text, (WIDTH - 250, 45))
        
        # 敌人区域
        pygame.draw.rect(screen, (50, 30, 30), (WIDTH//2 - 120, 120, 240, 200), border_radius=10)
        
        enemy_x = WIDTH//2 - 60
        enemy_y = 170
        pygame.draw.ellipse(screen, RED, (enemy_x, enemy_y, 120, 100))
        pygame.draw.circle(screen, RED, (WIDTH//2, 150), 35)
        
        # 眼睛
        pygame.draw.circle(screen, WHITE, (WIDTH//2 - 12, 145), 8)
        pygame.draw.circle(screen, WHITE, (WIDTH//2 + 12, 145), 8)
        pygame.draw.circle(screen, BLACK, (WIDTH//2 - 12, 145), 4)
        pygame.draw.circle(screen, BLACK, (WIDTH//2 + 12, 145), 4)
        
        # 血条
        hp_percent = self.enemy_hp / self.enemy_max_hp
        pygame.draw.rect(screen, DARK_GRAY, (WIDTH//2 - 150, 340, 300, 25))
        pygame.draw.rect(screen, GREEN, (WIDTH//2 - 150, 340, int(300 * hp_percent), 25))
        
        hp_text = self.font_medium.render(f"{self.enemy_hp} / {self.enemy_max_hp}", True, WHITE)
        screen.blit(hp_text, (WIDTH//2 - hp_text.get_width()//2, 342))
        
        # 伤害显示
        dmg_text = self.font_small.render(f"点击伤害: {self.damage}  自动: {self.auto_damage}/s", True, BLUE)
        screen.blit(dmg_text, (WIDTH//2 - dmg_text.get_width()//2, 380))
        
        # 粒子效果
        for p in self.particles:
            alpha = int(255 * p[2])
            color = (255, min(255, 100 + alpha), 50, alpha)
            pygame.draw.circle(screen, (255, 200, 50), (int(p[0]), int(p[1])), 5)
        
        # 升级按钮
        button_y = 430
        for i, upgrade in enumerate(self.upgrades):
            x = 30 + (i % 2) * 430
            y = button_y + (i // 2) * 80
            btn_rect = pygame.Rect(x, y, 410, 70)
            
            color = GREEN if self.gold >= upgrade["cost"] else GRAY
            pygame.draw.rect(screen, color, btn_rect, border_radius=10)
            
            name = self.font_medium.render(upgrade["name"], True, WHITE)
            cost = self.font_small.render(f"💰 {upgrade['cost']} (×{upgrade['count']})", True, GOLD)
            
            screen.blit(name, (x + 20, y + 10))
            screen.blit(cost, (x + 20, y + 38))
        
        pygame.display.flip()
    
    def handle_click(self, pos):
        # 点击敌人
        enemy_rect = pygame.Rect(WIDTH//2 - 120, 120, 240, 200)
        if enemy_rect.collidepoint(pos):
            self.deal_damage(self.damage, True)
            return
        
        # 升级按钮
        button_y = 430
        for i, upgrade in enumerate(self.upgrades):
            x = 30 + (i % 2) * 430
            y = button_y + (i // 2) * 80
            btn_rect = pygame.Rect(x, y, 410, 70)
            
            if btn_rect.collidepoint(pos) and self.gold >= upgrade["cost"]:
                self.gold -= upgrade["cost"]
                upgrade["count"] += 1
                
                if "damage" in upgrade:
                    self.damage += upgrade["damage"]
                elif "auto" in upgrade:
                    self.auto_damage += upgrade["auto"]
                
                upgrade["cost"] = int(upgrade["cost"] * 1.15)

def main():
    game = Game()
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
