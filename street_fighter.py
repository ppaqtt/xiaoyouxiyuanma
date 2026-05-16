import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("街头格斗")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
BLUE = (50, 100, 255)
GREEN = (50, 200, 50)
YELLOW = (255, 200, 0)
ORANGE = (255, 140, 0)

class Fighter:
    def __init__(self, x, color, name, is_player=False):
        self.x = x
        self.y = 400
        self.width = 60
        self.height = 100
        self.color = color
        self.name = name
        self.is_player = is_player
        self.hp = 100
        self.max_hp = 100
        self.mp = 100
        self.max_mp = 100
        self.velocity_x = 0
        self.velocity_y = 0
        self.jumping = False
        self.attacking = False
        self.attack_timer = 0
        self.blocking = False
        self.special_ready = False
        self.hit_effect = 0
    
    def draw(self):
        if self.hit_effect > 0:
            pygame.draw.rect(screen, RED, (self.x - self.width//2, self.y - self.height, self.width, self.height), border_radius=10)
            self.hit_effect -= 1
        else:
            pygame.draw.rect(screen, self.color, (self.x - self.width//2, self.y - self.height, self.width, self.height), border_radius=10)
        
        if self.attacking:
            pygame.draw.rect(screen, YELLOW, (self.x + self.width//2, self.y - 60, 40, 20))
        
        if self.blocking:
            pygame.draw.rect(screen, BLUE, (self.x - self.width//2 - 10, self.y - self.height, 10, self.height))
    
    def update(self, opponent):
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        self.x = max(self.width//2, min(WIDTH - self.width//2, self.x))
        
        if self.y < 300:
            self.velocity_y += 1
        else:
            self.y = 400
            self.velocity_y = 0
            self.jumping = False
        
        if self.attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False
        
        if not self.attacking and not self.blocking:
            self.velocity_x *= 0.9
        
        if self.mp < self.max_mp:
            self.mp += 0.1
        if self.mp >= 50:
            self.special_ready = True
        
        if self.check_hit(opponent):
            if not opponent.blocking:
                opponent.hp -= 5
                opponent.hit_effect = 10
    
    def jump(self):
        if not self.jumping:
            self.velocity_y = -15
            self.jumping = True
    
    def move_left(self):
        self.velocity_x = -5
    
    def move_right(self):
        self.velocity_x = 5
    
    def attack(self):
        if not self.attacking:
            self.attacking = True
            self.attack_timer = 15
    
    def special_attack(self):
        if self.special_ready:
            self.mp = 0
            self.special_ready = False
            return True
        return False
    
    def block(self, blocking):
        self.blocking = blocking
    
    def check_hit(self, opponent):
        if not self.attacking:
            return False
        
        attack_range = self.width + 40
        if self.is_player:
            return opponent.x - opponent.width//2 < self.x + attack_range < opponent.x + opponent.width//2
        else:
            return opponent.x - opponent.width//2 < self.x - attack_range < opponent.x + opponent.width//2

class FightingGame:
    def __init__(self):
        self.player = Fighter(200, BLUE, "玩家", True)
        self.enemy = Fighter(700, RED, "AI")
        self.game_over = False
        self.winner = None
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 48)
        self.ai_timer = 0
    
    def draw(self):
        screen.fill((50, 50, 80))
        
        pygame.draw.rect(screen, (100, 100, 100), (0, 500, WIDTH, 100))
        
        self.player.draw()
        self.enemy.draw()
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
    
    def draw_hud(self):
        pygame.draw.rect(screen, (0, 0, 0, 180), (10, 10, 250, 80), border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0, 180), (640, 10, 250, 80), border_radius=10)
        
        name_text = self.font.render(self.player.name, True, WHITE)
        screen.blit(name_text, (20, 15))
        
        pygame.draw.rect(screen, (100, 100, 100), (20, 45, 200, 20))
        pygame.draw.rect(screen, GREEN, (20, 45, self.player.hp * 2, 20))
        
        pygame.draw.rect(screen, (100, 100, 100), (20, 70, 200, 15))
        pygame.draw.rect(screen, BLUE, (20, 70, self.player.mp * 2, 15))
        
        name_text = self.font.render(self.enemy.name, True, WHITE)
        screen.blit(name_text, (650, 15))
        
        pygame.draw.rect(screen, (100, 100, 100), (650, 45, 200, 20))
        pygame.draw.rect(screen, GREEN, (650, 45, self.enemy.hp * 2, 20))
        
        pygame.draw.rect(screen, (100, 100, 100), (650, 70, 200, 15))
        pygame.draw.rect(screen, BLUE, (650, 70, self.enemy.mp * 2, 15))
    
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        if self.winner == "player":
            text = self.large_font.render("你赢了!", True, GREEN)
        else:
            text = self.large_font.render("你输了!", True, RED)
        
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
        
        restart_text = self.font.render("按 R 重新开始", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 300))
    
    def update(self):
        if self.game_over:
            return
        
        keys = pygame.key.get_pressed()
        
        self.player.move_left() if keys[pygame.K_a] else None
        self.player.move_right() if keys[pygame.K_d] else None
        self.player.jump() if keys[pygame.K_w] else None
        self.player.attack() if keys[pygame.K_j] else None
        self.player.block(keys[pygame.K_k])
        
        if keys[pygame.K_l] and self.player.special_ready:
            if self.player.special_attack():
                self.enemy.hp -= 25
                self.enemy.hit_effect = 20
        
        self.player.update(self.enemy)
        self.enemy.update(self.player)
        
        self.ai_timer += 1
        if self.ai_timer > 30:
            self.ai_timer = 0
            action = random.choice(['left', 'right', 'jump', 'attack', 'idle'])
            if action == 'left':
                self.enemy.move_left()
            elif action == 'right':
                self.enemy.move_right()
            elif action == 'jump':
                self.enemy.jump()
            elif action == 'attack':
                self.enemy.attack()
            
            if self.enemy.special_ready and random.random() < 0.3:
                if self.enemy.special_attack():
                    self.player.hp -= 25
                    self.player.hit_effect = 20
        
        if self.player.hp <= 0:
            self.game_over = True
            self.winner = "enemy"
        elif self.enemy.hp <= 0:
            self.game_over = True
            self.winner = "player"
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.__init__()

game = FightingGame()
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
