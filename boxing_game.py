import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("拳击冠军")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
BLUE = (50, 100, 200)
GREEN = (50, 200, 50)
YELLOW = (255, 200, 0)
PINK = (255, 150, 150)

class BoxingGame:
    def __init__(self):
        self.player_x = 200
        self.player_y = 350
        self.enemy_x = 550
        self.enemy_y = 350
        self.player_hp = 100
        self.enemy_hp = 100
        self.player_energy = 100
        self.enemy_energy = 100
        self.punching = False
        self.punch_type = None
        self.punch_timer = 0
        self.enemy_punching = False
        self.enemy_punch_timer = 0
        self.game_over = False
        self.winner = None
        self.round = 1
        self.player_wins = 0
        self.enemy_wins = 0
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 48)
        self.particles = []
    
    def draw_fighter(self, x, y, color, punching, punch_type, is_enemy=False):
        pygame.draw.circle(screen, color, (int(x), int(y - 50)), 30)
        
        body_color = PINK if color == RED else color
        pygame.draw.rect(screen, body_color, (x - 25, y - 20, 50, 60))
        
        if punching and punch_type == "jab":
            arm_x = x + 40 if not is_enemy else x - 40
            pygame.draw.line(screen, body_color, (x + 20 if not is_enemy else x - 20, y - 10), (arm_x, y - 10), 8)
        elif punching and punch_type == "hook":
            arm_x = x + 50 if not is_enemy else x - 50
            pygame.draw.line(screen, body_color, (x + 20 if not is_enemy else x - 20, y - 20), (arm_x, y - 30), 10)
        elif punching and punch_type == "uppercut":
            arm_x = x + 30 if not is_enemy else x - 30
            pygame.draw.line(screen, body_color, (x + 20 if not is_enemy else x - 20, y), (arm_x, y - 40), 10)
        else:
            pygame.draw.line(screen, body_color, (x + 20 if not is_enemy else x - 20, y - 10), (x + 30 if not is_enemy else x - 30, y + 10), 8)
            pygame.draw.line(screen, body_color, (x - 20 if not is_enemy else x + 20, y - 10), (x - 30 if not is_enemy else x + 30, y + 10), 8)
        
        pygame.draw.rect(screen, body_color, (x - 15, y + 40, 12, 40))
        pygame.draw.rect(screen, body_color, (x + 3, y + 40, 12, 40))
        
        pygame.draw.rect(screen, (100, 100, 200), (x - 25, y + 80, 50, 30))
    
    def draw(self):
        screen.fill((40, 40, 60))
        
        pygame.draw.rect(screen, (80, 60, 40), (0, 520, WIDTH, 80))
        
        self.draw_fighter(self.player_x, self.player_y, BLUE, self.punching, self.punch_type)
        self.draw_fighter(self.enemy_x, self.enemy_y, RED, self.enemy_punching, "jab", True)
        
        for p in self.particles:
            pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), int(p['size']))
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
    
    def draw_hud(self):
        pygame.draw.rect(screen, (0, 0, 0, 180), (10, 10, 200, 120), border_radius=10)
        
        player_label = self.font.render("玩家", True, WHITE)
        screen.blit(player_label, (20, 15))
        
        pygame.draw.rect(screen, (100, 100, 100), (20, 45, 180, 20))
        pygame.draw.rect(screen, GREEN, (20, 45, self.player_hp * 1.8, 20))
        
        pygame.draw.rect(screen, (100, 100, 100), (20, 75, 180, 15))
        pygame.draw.rect(screen, YELLOW, (20, 75, self.player_energy * 1.8, 15))
        
        round_text = self.font.render(f"回合 {self.round}", True, WHITE)
        screen.blit(round_text, (20, 100))
        
        pygame.draw.rect(screen, (0, 0, 0, 180), (590, 10, 200, 120), border_radius=10)
        
        enemy_label = self.font.render("对手", True, WHITE)
        screen.blit(enemy_label, (600, 15))
        
        pygame.draw.rect(screen, (100, 100, 100), (600, 45, 180, 20))
        pygame.draw.rect(screen, GREEN, (600, 45, self.enemy_hp * 1.8, 20))
        
        pygame.draw.rect(screen, (100, 100, 100), (600, 75, 180, 15))
        pygame.draw.rect(screen, YELLOW, (600, 75, self.enemy_energy * 1.8, 15))
        
        score_text = self.font.render(f"{self.player_wins} - {self.enemy_wins}", True, WHITE)
        screen.blit(score_text, (680, 100))
        
        controls_text = self.font.render("A/D移动 J:直拳 K:勾拳 L:上勾拳", True, (150, 150, 150))
        screen.blit(controls_text, (250, 560))
    
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        if self.winner == "player":
            text = self.large_font.render("你赢了比赛!", True, GREEN)
        else:
            text = self.large_font.render("你输了比赛!", True, RED)
        
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
        
        score_text = self.font.render(f"最终比分: {self.player_wins} - {self.enemy_wins}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 280))
        
        restart_text = self.font.render("按 R 重新开始", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 350))
    
    def spawn_hit_effect(self, x, y):
        for _ in range(10):
            self.particles.append({
                'x': x + random.randint(-20, 20),
                'y': y + random.randint(-20, 20),
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'size': random.uniform(3, 6),
                'color': RED
            })
    
    def update(self):
        if self.game_over:
            return
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_a]:
            self.player_x = max(80, self.player_x - 5)
        if keys[pygame.K_d]:
            self.player_x = min(400, self.player_x + 5)
        
        if keys[pygame.K_j] and not self.punching and self.player_energy >= 10:
            self.punching = True
            self.punch_type = "jab"
            self.punch_timer = 15
            self.player_energy -= 10
        elif keys[pygame.K_k] and not self.punching and self.player_energy >= 20:
            self.punching = True
            self.punch_type = "hook"
            self.punch_timer = 25
            self.player_energy -= 20
        elif keys[pygame.K_l] and not self.punching and self.player_energy >= 30:
            self.punching = True
            self.punch_type = "uppercut"
            self.punch_timer = 30
            self.player_energy -= 30
        
        if self.punching:
            self.punch_timer -= 1
            if self.punch_timer <= 10 and self.punch_timer > 5:
                if self.enemy_x - self.player_x < 200:
                    damage = 5 if self.punch_type == "jab" else (12 if self.punch_type == "hook" else 15)
                    self.enemy_hp -= damage
                    self.spawn_hit_effect(self.enemy_x, self.enemy_y - 30)
            if self.punch_timer <= 0:
                self.punching = False
        
        if not self.punching and self.player_energy < 100:
            self.player_energy += 0.5
        
        self.enemy_ai()
        
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['size'] *= 0.9
        
        self.particles = [p for p in self.particles if p['size'] > 1]
        
        if self.player_hp <= 0 or self.enemy_hp <= 0:
            self.end_round()
    
    def enemy_ai(self):
        if self.enemy_energy >= 20 and not self.enemy_punching and random.random() < 0.03:
            self.enemy_punching = True
            self.enemy_punch_timer = 20
            self.enemy_energy -= 20
            if self.enemy_x - self.player_x < 200:
                self.player_hp -= 8
                self.spawn_hit_effect(self.player_x, self.player_y - 30)
        
        if self.enemy_punching:
            self.enemy_punch_timer -= 1
            if self.enemy_punch_timer <= 0:
                self.enemy_punching = False
        
        if not self.enemy_punching and self.enemy_energy < 100:
            self.enemy_energy += 0.3
        
        if self.enemy_x > 500:
            self.enemy_x -= 1
        if self.enemy_x < self.player_x + 100:
            self.enemy_x += 0.5
    
    def end_round(self):
        if self.player_hp > self.enemy_hp:
            self.player_wins += 1
        else:
            self.enemy_wins += 1
        
        if self.player_wins >= 3 or self.enemy_wins >= 3:
            self.game_over = True
            self.winner = "player" if self.player_wins >= 3 else "enemy"
        else:
            self.round += 1
            self.player_hp = 100
            self.enemy_hp = 100
            self.player_x = 200
            self.enemy_x = 550
            self.punching = False
            self.enemy_punching = False
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.__init__()

game = BoxingGame()
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
