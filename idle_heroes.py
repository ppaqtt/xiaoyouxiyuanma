import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("英雄传奇")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
GOLD = (255, 200, 50)
PURPLE = (150, 50, 200)

hero_types = [
    {"name": "战士", "color": RED, "power": 10, "cost": 50, "desc": "近战勇士"},
    {"name": "法师", "color": BLUE, "power": 15, "cost": 80, "desc": "魔法专家"},
    {"name": "弓手", "color": GREEN, "power": 8, "cost": 60, "desc": "远程射手"},
    {"name": "牧师", "color": GOLD, "power": 5, "cost": 100, "desc": "治疗支援"},
]

monsters = [
    {"name": "史莱姆", "hp": 30, "reward": 10, "level": 1},
    {"name": "哥布林", "hp": 60, "reward": 25, "level": 2},
    {"name": "骷髅兵", "hp": 100, "reward": 50, "level": 3},
    {"name": "巨魔", "hp": 200, "reward": 100, "level": 5},
]

class IdleHeroes:
    def __init__(self):
        self.gold = 200
        self.heroes = []
        self.level = 1
        self.exp = 0
        self.exp_needed = 100
        self.current_monster = None
        self.battle_hp = 0
        self.battle_max_hp = 0
        self.message = ""
        self.message_timer = 0
        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 48)
        self.spawn_monster()

    def spawn_monster(self):
        level_factor = 0.8 + self.level * 0.2
        candidates = [m for m in monsters if m["level"] <= self.level + 1]
        self.current_monster = random.choice(candidates)
        self.battle_max_hp = int(self.current_monster["hp"] * level_factor)
        self.battle_hp = self.battle_max_hp

    def update(self):
        if self.current_monster:
            total_power = sum(hero_types[h["type"]]["power"] * (1 + h["level"] * 0.2) for h in self.heroes)
            if total_power > 0:
                damage = total_power * 0.01
                self.battle_hp -= damage
                
                if self.battle_hp <= 0:
                    reward = int(self.current_monster["reward"] * (1 + self.level * 0.1))
                    self.gold += reward
                    self.exp += reward // 2
                    self.message = f"击败了{self.current_monster['name']}！获得{reward}金币！"
                    self.message_timer = 120
                    self.spawn_monster()
        
        while self.exp >= self.exp_needed:
            self.exp -= self.exp_needed
            self.level += 1
            self.exp_needed = int(100 * (1.5 ** (self.level - 1)))
        
        if self.message_timer > 0:
            self.message_timer -= 1

    def draw(self):
        screen.fill((30, 30, 50))
        
        pygame.draw.rect(screen, (100, 100, 150), (0, 0, 800, 100))
        pygame.draw.rect(screen, BLACK, (0, 0, 800, 100), 2)
        
        title_text = self.large_font.render("英雄传奇", True, GOLD)
        screen.blit(title_text, (320, 25))
        
        gold_text = self.font.render(f"金币: {int(self.gold)}", True, WHITE)
        screen.blit(gold_text, (30, 35))
        
        level_text = self.font.render(f"等级: {self.level}", True, WHITE)
        screen.blit(level_text, (200, 35))
        
        exp_text = self.font.render(f"经验: {self.exp}/{self.exp_needed}", True, WHITE)
        screen.blit(exp_text, (350, 35))
        
        if self.current_monster:
            hp_percent = max(0, self.battle_hp / self.battle_max_hp)
            pygame.draw.rect(screen, (80, 40, 40), (50, 120, 300, 40))
            pygame.draw.rect(screen, GREEN, (50, 120, 300 * hp_percent, 40))
            pygame.draw.rect(screen, BLACK, (50, 120, 300, 40), 2)
            
            monster_name = self.font.render(self.current_monster["name"], True, WHITE)
            screen.blit(monster_name, (80, 128))
        
        for i, hero in enumerate(self.heroes):
            x = 450 + (i % 2) * 160
            y = 120 + (i // 2) * 120
            hero_type = hero_types[hero["type"]]
            pygame.draw.rect(screen, hero_type["color"], (x, y, 140, 100), border_radius=10)
            pygame.draw.rect(screen, BLACK, (x, y, 140, 100), 2, border_radius=10)
            
            name = self.font.render(hero_type["name"], True, WHITE)
            screen.blit(name, (x+20, y+15))
            level = self.font.render(f"Lv{hero['level']}", True, WHITE)
            screen.blit(level, (x+20, y+50))
            
            if self.gold >= 50 * (1.5 ** hero["level"]):
                pygame.draw.rect(screen, (255, 150, 0), (x+20, y+75, 100, 15), border_radius=3)
                upgrade_text = self.font.render("升级", True, BLACK)
                screen.blit(upgrade_text, (x+45, y+72))
        
        pygame.draw.rect(screen, (240, 240, 240), (30, 380, 340, 200), border_radius=10)
        pygame.draw.rect(screen, BLACK, (30, 380, 340, 200), 2, border_radius=10)
        
        shop_title = self.font.render("英雄商店", True, BLACK)
        screen.blit(shop_title, (140, 390))
        
        for i, hero_type in enumerate(hero_types):
            button_y = 430 + i * 35
            color = (200, 220, 255) if self.gold >= hero_type["cost"] else (200, 200, 200)
            pygame.draw.rect(screen, color, (40, button_y, 320, 30), border_radius=3)
            pygame.draw.rect(screen, BLACK, (40, button_y, 320, 30), 2, border_radius=3)
            name_text = self.font.render(f"{hero_type['name']} ¥{hero_type['cost']} - {hero_type['desc']}", True, BLACK)
            screen.blit(name_text, (50, button_y+4))
        
        if self.message:
            msg_text = self.font.render(self.message, True, WHITE)
            screen.blit(msg_text, (WIDTH//2 - msg_text.get_width()//2, 550))

    def handle_click(self, pos):
        for i, hero_type in enumerate(hero_types):
            button_y = 430 + i * 35
            if 40 <= pos[0] <= 360 and button_y <= pos[1] <= button_y+30:
                if self.gold >= hero_type["cost"] and len(self.heroes) < 6:
                    self.gold -= hero_type["cost"]
                    self.heroes.append({"type": i, "level": 1})
        
        for i, hero in enumerate(self.heroes):
            x = 450 + (i % 2) * 160
            y = 120 + (i // 2) * 120
            if x+20 <= pos[0] <= x+120 and y+75 <= pos[1] <= y+90:
                cost = int(50 * (1.5 ** hero["level"]))
                if self.gold >= cost:
                    self.gold -= cost
                    hero["level"] += 1

game = IdleHeroes()
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
