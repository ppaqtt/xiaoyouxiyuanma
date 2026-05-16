import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("高尔夫精英")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 150, 50)
BROWN = (139, 90, 43)
RED = (200, 50, 50)
BLUE = (50, 100, 200)
YELLOW = (255, 200, 0)

class GolfGame:
    def __init__(self):
        self.ball_x = 400
        self.ball_y = 500
        self.power = 0
        self.angle = 45
        self.shots = 0
        self.score = 0
        self.hole_x = random.randint(100, 700)
        self.hole_y = random.randint(50, 150)
        self.in_water = False
        self.game_over = False
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 48)
        self.particles = []
        
        self.holes_completed = 0
        self.total_shots = 0
        
        self.wind = random.uniform(-2, 2)
    
    def draw(self):
        screen.fill(GREEN)
        
        for i in range(10):
            pygame.draw.circle(screen, (60 + i * 5, 160 + i * 3, 60 + i * 3), 
                            (400, 300), 200 + i * 30, 3)
        
        pygame.draw.circle(screen, WHITE, (int(self.hole_x), int(self.hole_y)), 15)
        pygame.draw.circle(screen, BLACK, (int(self.hole_x), int(self.hole_y)), 12)
        
        for i in range(5):
            water_x = 100 + i * 150
            water_y = 400
            if not (abs(water_x - self.hole_x) < 50 and abs(water_y - self.hole_y) < 50):
                pygame.draw.ellipse(screen, BLUE, (water_x, water_y, 80, 40))
        
        if self.in_water:
            pygame.draw.circle(screen, BLUE, (int(self.ball_x), int(self.ball_y)), 8)
        else:
            pygame.draw.circle(screen, WHITE, (int(self.ball_x), int(self.ball_y)), 8)
        
        for p in self.particles:
            pygame.draw.circle(screen, (200, 200, 200), (int(p['x']), int(p['y'])), int(p['size']))
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
    
    def draw_hud(self):
        pygame.draw.rect(screen, (0, 0, 0, 180), (10, 10, 300, 100), border_radius=10)
        
        shots_text = self.font.render(f"击球次数: {self.shots}", True, WHITE)
        screen.blit(shots_text, (20, 20))
        
        hole_text = self.font.render(f"洞数: {self.holes_completed}", True, WHITE)
        screen.blit(hole_text, (20, 50))
        
        wind_text = self.font.render(f"风向: {'←' if self.wind < 0 else '→'} {abs(self.wind):.1f}", True, YELLOW)
        screen.blit(wind_text, (20, 80))
        
        pygame.draw.rect(screen, (100, 100, 100), (500, 550, 200, 30))
        pygame.draw.rect(screen, GREEN, (500, 550, self.power * 2, 30))
        
        power_text = self.font.render(f"力度: {int(self.power)}%", True, WHITE)
        screen.blit(power_text, (520, 555))
        
        angle_text = self.font.render(f"角度: {self.angle}°", True, WHITE)
        screen.blit(angle_text, (500, 510))
        
        controls = self.font.render("空格蓄力 | ↑↓调角度 | R重置", True, (150, 150, 150))
        screen.blit(controls, (500, 20))
    
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        text = self.large_font.render("游戏结束!", True, YELLOW)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
        
        stats_text = self.font.render(f"完成洞数: {self.holes_completed} | 总击球: {self.total_shots}", True, WHITE)
        screen.blit(stats_text, (WIDTH//2 - stats_text.get_width()//2, 280))
        
        restart_text = self.font.render("按 R 重新开始", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 350))
    
    def update(self):
        if self.game_over:
            return
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP]:
            self.angle = min(135, self.angle + 1)
        if keys[pygame.K_DOWN]:
            self.angle = max(45, self.angle - 1)
        
        if keys[pygame.K_SPACE]:
            self.power = min(100, self.power + 1.5)
        elif self.power > 0 and not self.in_water:
            self.shoot()
        
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['size'] *= 0.95
        
        self.particles = [p for p in self.particles if p['size'] > 0.5]
    
    def shoot(self):
        angle_rad = math.radians(self.angle)
        vx = math.cos(angle_rad) * self.power * 0.2
        vy = -math.sin(angle_rad) * self.power * 0.2
        
        self.shots += 1
        self.total_shots += 1
        
        for _ in range(10):
            self.particles.append({
                'x': self.ball_x,
                'y': self.ball_y,
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-2, 2),
                'size': random.uniform(2, 4)
            })
        
        self.power = 0
        
        for _ in range(50):
            self.ball_x += vx * 0.1
            self.ball_y += vy * 0.1
            vy += 0.05
            vx += self.wind * 0.01
            
            self.ball_x = max(10, min(WIDTH - 10, self.ball_x))
            self.ball_y = max(10, min(HEIGHT - 10, self.ball_y))
            
            if 95 < self.ball_x < 175 and 380 < self.ball_y < 420:
                self.in_water = True
                break
            
            dist_to_hole = math.hypot(self.ball_x - self.hole_x, self.ball_y - self.hole_y)
            if dist_to_hole < 15 and abs(vy) < 2:
                self.holes_completed += 1
                self.next_hole()
                return
        
        if abs(vx) < 0.1 and abs(vy) < 0.1:
            self.in_water = False
    
    def next_hole(self):
        self.ball_x = 400
        self.ball_y = 500
        self.shots = 0
        self.hole_x = random.randint(100, 700)
        self.hole_y = random.randint(50, 200)
        self.wind = random.uniform(-2, 2)
        
        if self.holes_completed >= 9:
            self.game_over = True
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.__init__()

game = GolfGame()
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
