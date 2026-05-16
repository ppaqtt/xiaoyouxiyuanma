import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("海盗冒险")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 90, 43)
BLUE = (0, 100, 200)
RED = (200, 50, 50)
GOLD = (255, 200, 0)
GREEN = (50, 200, 50)

class PirateAdventure:
    def __init__(self):
        self.player_x = 400
        self.player_y = 300
        self.gold = 0
        self.health = 100
        self.level = 1
        self.exp = 0
        self.weapons = [{"name": "短剑", "damage": 10, "cost": 0}]
        self.current_weapon = 0
        self.enemies = []
        self.treasures = []
        self.map_level = 1
        self.game_over = False
        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 48)
        
        for _ in range(3):
            self.spawn_enemy()
    
    def spawn_enemy(self):
        enemy_types = ["海盗", "骷髅", "章鱼", "鲨鱼"]
        enemy = {
            "type": random.choice(enemy_types),
            "x": random.randint(50, 750),
            "y": random.randint(50, 550),
            "hp": 20 + self.level * 10,
            "max_hp": 20 + self.level * 10,
            "damage": 5 + self.level * 2,
            "gold": 10 + self.level * 5
        }
        self.enemies.append(enemy)
    
    def spawn_treasure(self):
        treasure = {
            "x": random.randint(50, 750),
            "y": random.randint(50, 550),
            "gold": 20 + self.level * 10
        }
        self.treasures.append(treasure)
    
    def draw(self):
        screen.fill((30, 60, 90))
        
        for x in range(0, WIDTH, 50):
            pygame.draw.line(screen, (40, 70, 100), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 50):
            pygame.draw.line(screen, (40, 70, 100), (0, y), (WIDTH, y), 1)
        
        for enemy in self.enemies:
            color = RED if enemy["type"] == "海盗" else (200, 200, 200) if enemy["type"] == "骷髅" else PURPLE if enemy["type"] == "章鱼" else (100, 150, 200)
            pygame.draw.circle(screen, color, (int(enemy["x"]), int(enemy["y"])), 20)
            pygame.draw.rect(screen, GREEN, (enemy["x"] - 20, enemy["y"] - 35, 40, 5))
            pygame.draw.rect(screen, RED, (enemy["x"] - 20, enemy["y"] - 35, 40 * enemy["hp"] // enemy["max_hp"], 5))
        
        for treasure in self.treasures:
            pygame.draw.circle(screen, GOLD, (int(treasure["x"]), int(treasure["y"])), 15)
            pygame.draw.circle(screen, (255, 220, 0), (int(treasure["x"]), int(treasure["y"])), 10)
        
        pygame.draw.circle(screen, BROWN, (int(self.player_x), int(self.player_y)), 25)
        pygame.draw.rect(screen, BLUE, (self.player_x - 5, self.player_y - 20, 10, 25))
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
    
    def draw_hud(self):
        pygame.draw.rect(screen, (0, 0, 0, 180), (10, 10, 250, 120), border_radius=10)
        
        gold_text = self.font.render(f"金币: {self.gold}", True, GOLD)
        screen.blit(gold_text, (20, 20))
        
        health_text = self.font.render(f"生命: {self.health}", True, RED)
        screen.blit(health_text, (20, 50))
        
        level_text = self.font.render(f"等级: {self.level}", True, WHITE)
        screen.blit(level_text, (20, 80))
        
        exp_text = self.font.render(f"经验: {self.exp}", True, GREEN)
        screen.blit(exp_text, (20, 110))
        
        weapon_text = self.font.render(f"武器: {self.weapons[self.current_weapon]['name']}", True, WHITE)
        screen.blit(weapon_text, (150, 20))
    
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        text = self.large_font.render("你被击败了!", True, RED)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
        
        stats_text = self.font.render(f"最终等级: {self.level} | 金币: {self.gold}", True, WHITE)
        screen.blit(stats_text, (WIDTH//2 - stats_text.get_width()//2, 280))
        
        restart_text = self.font.render("按 R 重新开始", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 350))
    
    def update(self):
        if self.game_over:
            return
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:
            self.player_y = max(30, self.player_y - 5)
        if keys[pygame.K_s]:
            self.player_y = min(570, self.player_y + 5)
        if keys[pygame.K_a]:
            self.player_x = max(30, self.player_x - 5)
        if keys[pygame.K_d]:
            self.player_x = min(770, self.player_x + 5)
        
        for enemy in self.enemies[:]:
            dist = math.hypot(self.player_x - enemy["x"], self.player_y - enemy["y"])
            if dist < 50:
                if keys[pygame.K_SPACE]:
                    enemy["hp"] -= self.weapons[self.current_weapon]["damage"]
                    if enemy["hp"] <= 0:
                        self.gold += enemy["gold"]
                        self.exp += 10
                        self.enemies.remove(enemy)
                        self.spawn_enemy()
            else:
                enemy["x"] += (self.player_x - enemy["x"]) * 0.01
                enemy["y"] += (self.player_y - enemy["y"]) * 0.01
                
                if random.random() < 0.02:
                    self.health -= enemy["damage"]
        
        for treasure in self.treasures[:]:
            dist = math.hypot(self.player_x - treasure["x"], self.player_y - treasure["y"])
            if dist < 40:
                self.gold += treasure["gold"]
                self.treasures.remove(treasure)
        
        if random.random() < 0.01:
            self.spawn_treasure()
        
        if self.exp >= 100:
            self.level += 1
            self.exp -= 100
            self.health = min(100, self.health + 20)
        
        if self.health <= 0:
            self.game_over = True
        
        if keys[pygame.K_1] and len(self.weapons) > 1:
            self.current_weapon = 0
        if keys[pygame.K_2] and len(self.weapons) > 1:
            self.current_weapon = 1
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.__init__()

game = PirateAdventure()
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.handle_input(event)
    
    game.update()
    game.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
