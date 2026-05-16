import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("街头篮球")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 140, 0)
RED = (200, 50, 50)
BLUE = (50, 100, 200)
GREEN = (50, 200, 50)

class BasketballGame:
    def __init__(self):
        self.player_x = 400
        self.player_y = 450
        self.ball_x = self.player_x
        self.ball_y = self.player_y - 30
        self.ball_velocity_x = 0
        self.ball_velocity_y = 0
        self.score = 0
        self.attempts = 0
        self.ball_in_hand = True
        self.power = 0
        self.angle = 45
        self.combo = 0
        self.opponent_score = 0
        self.game_over = False
        self.turn = "player"
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 48)
        self.hoop_x = 650
        self.hoop_y = 150
    
    def draw(self):
        screen.fill((135, 206, 235))
        
        pygame.draw.rect(screen, (139, 90, 43), (0, 520, WIDTH, 80))
        
        pygame.draw.rect(screen, (200, 200, 200), (620, 100, 80, 10))
        pygame.draw.rect(screen, (255, 255, 255), (640, 110, 40, 60))
        pygame.draw.ellipse(screen, ORANGE, (645, 170, 30, 60))
        
        pygame.draw.circle(screen, self.player_x == 400 and GREEN or BLUE, (int(self.player_x), int(self.player_y)), 25)
        pygame.draw.circle(screen, ORANGE, (int(self.ball_x), int(self.ball_y)), 12)
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
    
    def draw_hud(self):
        pygame.draw.rect(screen, (0, 0, 0, 128), (10, 10, 250, 100), border_radius=10)
        
        score_text = self.font.render(f"得分: {self.score}/{self.attempts}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        if self.attempts > 0:
            percent = int(self.score / self.attempts * 100)
            percent_text = self.font.render(f"命中率: {percent}%", True, GREEN)
            screen.blit(percent_text, (20, 50))
        
        combo_text = self.font.render(f"连进: {self.combo}", True, ORANGE)
        screen.blit(combo_text, (20, 80))
        
        if not self.ball_in_hand:
            power_text = self.font.render(f"力度: {int(self.power)}%", True, RED)
            screen.blit(power_text, (600, 500))
            
            pygame.draw.rect(screen, (100, 100, 100), (580, 520, 150, 20))
            pygame.draw.rect(screen, GREEN, (580, 520, self.power * 1.5, 20))
    
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        text = self.large_font.render("游戏结束!", True, ORANGE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
        
        score_text = self.font.render(f"最终得分: {self.score}/{self.attempts}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 280))
        
        restart_text = self.font.render("按 R 重新开始", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 350))
    
    def update(self):
        if self.game_over:
            return
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.player_x = max(50, self.player_x - 5)
        if keys[pygame.K_RIGHT]:
            self.player_x = min(750, self.player_x + 5)
        
        if self.ball_in_hand:
            self.ball_x = self.player_x
            self.ball_y = self.player_y - 30
            
            if keys[pygame.K_UP]:
                self.angle = min(90, self.angle + 1)
            if keys[pygame.K_DOWN]:
                self.angle = max(10, self.angle - 1)
            
            if keys[pygame.K_SPACE]:
                self.power = min(100, self.power + 2)
            elif self.power > 0:
                self.ball_in_hand = False
                angle_rad = math.radians(self.angle)
                self.ball_velocity_x = math.cos(angle_rad) * self.power * 0.15
                self.ball_velocity_y = -math.sin(angle_rad) * self.power * 0.15
                self.attempts += 1
        else:
            self.ball_x += self.ball_velocity_x
            self.ball_y += self.ball_velocity_y
            self.ball_velocity_y += 0.5
            
            if 630 <= self.ball_x <= 690 and 170 <= self.ball_y <= 230:
                dist_to_hoop = abs(self.ball_x - self.hoop_x)
                if dist_to_hoop < 25 and self.ball_velocity_y > 0:
                    self.score += 1
                    self.combo += 1
                    self.ball_in_hand = True
                    self.ball_x = self.player_x
                    self.ball_y = self.player_y - 30
                    self.power = 0
            
            if self.ball_y > 550 or self.ball_x < 0 or self.ball_x > 800:
                self.combo = 0
                self.ball_in_hand = True
                self.ball_x = self.player_x
                self.ball_y = self.player_y - 30
                self.power = 0
        
        if self.attempts >= 20:
            self.game_over = True
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.__init__()

game = BasketballGame()
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
