import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("热血足球")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 150, 50)
RED = (200, 50, 50)
BLUE = (50, 100, 200)
YELLOW = (255, 200, 0)

class SoccerGame:
    def __init__(self):
        self.player_x = 100
        self.player_y = 300
        self.ball_x = 400
        self.ball_y = 300
        self.ball_vx = 0
        self.ball_vy = 0
        self.goals_player = 0
        self.goals_ai = 0
        self.game_time = 90
        self.timer = 0
        self.kick_power = 0
        self.kicking = False
        self.ai_x = 700
        self.ai_y = 300
        self.game_over = False
        self.winner = None
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 48)
        self.particles = []
    
    def draw(self):
        screen.fill(GREEN)
        
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 40))
        pygame.draw.line(screen, WHITE, (400, 0), (400, 600), 3)
        pygame.draw.circle(screen, WHITE, (400, 300), 80, 3)
        pygame.draw.circle(screen, WHITE, (400, 300), 8)
        pygame.draw.rect(screen, WHITE, (0, 100, 15, 200))
        pygame.draw.rect(screen, WHITE, (785, 100, 15, 200))
        pygame.draw.line(screen, WHITE, (0, 200), (100, 200), 3)
        pygame.draw.line(screen, WHITE, (700, 200), (800, 200), 3)
        
        pygame.draw.circle(screen, BLUE, (int(self.player_x), int(self.player_y)), 20)
        player_num = self.font.render("1", True, WHITE)
        screen.blit(player_num, (int(self.player_x) - 6, int(self.player_y) - 10))
        
        pygame.draw.circle(screen, RED, (int(self.ai_x), int(self.ai_y)), 20)
        ai_num = self.font.render("2", True, WHITE)
        screen.blit(ai_num, (int(self.ai_x) - 6, int(self.ai_y) - 10))
        
        pygame.draw.circle(screen, YELLOW, (int(self.ball_x), int(self.ball_y)), 10)
        
        for p in self.particles:
            pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), int(p['size']))
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
    
    def draw_hud(self):
        pygame.draw.rect(screen, (0, 0, 0, 180), (10, 50, 250, 80), border_radius=10)
        
        score_text = self.large_font.render(f"{self.goals_player} - {self.goals_ai}", True, WHITE)
        screen.blit(score_text, (20, 55))
        
        time_text = self.font.render(f"时间: {int(self.timer)}s", True, WHITE)
        screen.blit(time_text, (20, 110))
    
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        if self.winner == "player":
            text = self.large_font.render("你赢了!", True, GREEN)
        elif self.winner == "ai":
            text = self.large_font.render("AI赢了!", True, RED)
        else:
            text = self.large_font.render("平局!", True, YELLOW)
        
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
        
        score_text = self.font.render(f"最终比分: {self.goals_player} - {self.goals_ai}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 280))
        
        restart_text = self.font.render("按 R 重新开始", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 350))
    
    def update(self):
        if self.game_over:
            return
        
        self.timer += 1/60
        if self.timer >= self.game_time:
            self.game_over = True
            if self.goals_player > self.goals_ai:
                self.winner = "player"
            elif self.goals_ai > self.goals_player:
                self.winner = "ai"
            else:
                self.winner = "draw"
            return
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.player_x = max(30, self.player_x - 5)
        if keys[pygame.K_RIGHT]:
            self.player_x = min(770, self.player_x + 5)
        if keys[pygame.K_UP]:
            self.player_y = max(50, self.player_y - 5)
        if keys[pygame.K_DOWN]:
            self.player_y = min(550, self.player_y + 5)
        
        if keys[pygame.K_SPACE] and not self.kicking:
            self.kicking = True
            self.kick_power = 0
        
        if self.kicking:
            self.kick_power = min(100, self.kick_power + 3)
            if not keys[pygame.K_SPACE]:
                dist = ((self.player_x - self.ball_x)**2 + (self.player_y - self.ball_y)**2)**0.5
                if dist < 50:
                    angle = (self.ball_y - self.player_y) / (dist + 0.1)
                    self.ball_vx = self.kick_power * 0.2
                    self.ball_vy = -angle * self.kick_power * 0.15
                self.kicking = False
        
        if abs(self.ball_x - self.player_x) < 30 and abs(self.ball_y - self.player_y) < 30:
            if not self.kicking:
                self.ball_x = self.player_x + 30
                self.ball_y = self.player_y
        
        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy
        self.ball_vx *= 0.98
        self.ball_vy *= 0.98
        
        if self.ball_y < 10 or self.ball_y > 590:
            self.ball_vy *= -0.8
        if self.ball_x < 10 or self.ball_x > 790:
            self.ball_vx *= -0.8
        
        if self.ball_x < 15 and 100 < self.ball_y < 300:
            self.goals_ai += 1
            self.reset_ball()
        if self.ball_x > 785 and 100 < self.ball_y < 300:
            self.goals_player += 1
            self.reset_ball()
        
        target_x = self.ball_x - 50
        target_y = self.ball_y
        self.ai_x += (target_x - self.ai_x) * 0.03
        self.ai_y += (target_y - self.ai_y) * 0.03
        
        if abs(self.ai_x - self.ball_x) < 30 and abs(self.ai_y - self.ball_y) < 30:
            self.ball_x = self.ai_x - 30
        
        for _ in range(2):
            self.particles.append({
                'x': self.ball_x + random.randint(-5, 5),
                'y': self.ball_y + random.randint(-5, 5),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1),
                'size': random.uniform(2, 4),
                'color': GREEN
            })
        
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['size'] *= 0.95
        
        self.particles = [p for p in self.particles if p['size'] > 0.5]
    
    def reset_ball(self):
        self.ball_x = 400
        self.ball_y = 300
        self.ball_vx = 0
        self.ball_vy = 0
        self.player_x = 100
        self.player_y = 300
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.__init__()

game = SoccerGame()
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
