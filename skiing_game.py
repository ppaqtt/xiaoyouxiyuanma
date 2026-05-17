import pygame
import os
import sys
import random
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

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("滑雪大冒险")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
SKY_BLUE = (135, 206, 250)

class SkiGame:
    def __init__(self):
        self.player_x = 400
        self.player_y = 100
        self.player_angle = 0
        self.speed = 5
        self.score = 0
        self.distance = 0
        self.obstacles = []
        self.particles = []
        self.game_over = False
        self.font = get_chinese_font(36)
        self.large_font = get_chinese_font(48)
        
        for _ in range(5):
            self.spawn_obstacle()
    
    def spawn_obstacle(self):
        obstacle_type = random.choice(['tree', 'rock', 'flag'])
        x = random.randint(100, 700)
        y = HEIGHT + random.randint(50, 200)
        self.obstacles.append({
            'x': x, 'y': y, 'type': obstacle_type,
            'speed': random.uniform(3, 6)
        })
    
    def draw(self):
        screen.fill(SKY_BLUE)
        
        for i in range(20):
            y = (i * 50 + self.distance * 3) % (HEIGHT + 200) - 100
            pygame.draw.line(screen, (220, 220, 230), (0, y), (WIDTH, y), 2)
        
        for obs in self.obstacles:
            if obs['type'] == 'tree':
                pygame.draw.rect(screen, (101, 67, 33), (obs['x'] - 8, obs['y'] - 20, 16, 25))
                pygame.draw.circle(screen, GREEN, (int(obs['x']), int(obs['y'] - 30)), 20)
            elif obs['type'] == 'rock':
                pygame.draw.polygon(screen, (128, 128, 128), [(obs['x'], obs['y'] - 15), (obs['x'] - 20, obs['y']), (obs['x'] + 20, obs['y'])])
            else:
                pygame.draw.circle(screen, RED, (int(obs['x']), int(obs['y'])), 8)
        
        pygame.draw.circle(screen, RED, (int(self.player_x), int(self.player_y)), 15)
        
        for p in self.particles:
            pygame.draw.circle(screen, WHITE, (int(p['x']), int(p['y'])), int(p['size']))
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
    
    def draw_hud(self):
        pygame.draw.rect(screen, (0, 0, 0, 128), (10, 10, 200, 80), border_radius=10)
        
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        dist_text = self.font.render(f"距离: {self.distance}m", True, WHITE)
        screen.blit(dist_text, (20, 60))
    
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        text = self.large_font.render("游戏结束!", True, RED)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
        
        score_text = self.font.render(f"最终分数: {self.score}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 280))
        
        restart_text = self.font.render("按 R 重新开始", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 350))
    
    def update(self):
        if self.game_over:
            return
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.player_x -= 8
            self.particles.append({'x': self.player_x + 15, 'y': self.player_y + 10, 'vx': 3, 'vy': -2, 'size': 3})
        if keys[pygame.K_RIGHT]:
            self.player_x += 8
            self.particles.append({'x': self.player_x - 15, 'y': self.player_y + 10, 'vx': -3, 'vy': -2, 'size': 3})
        
        self.player_x = max(30, min(WIDTH - 30, self.player_x))
        
        self.distance += 1
        
        for obs in self.obstacles:
            obs['y'] -= obs['speed']
        
        self.obstacles = [o for o in self.obstacles if o['y'] > -50]
        
        while len(self.obstacles) < 6:
            self.spawn_obstacle()
        
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['size'] *= 0.95
        
        self.particles = [p for p in self.particles if p['size'] > 0.5]
        
        for obs in self.obstacles:
            dist = math.hypot(self.player_x - obs['x'], self.player_y - obs['y'])
            if dist < 30:
                self.game_over = True
        
        if random.random() < 0.05:
            self.score += 1
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.__init__()

game = SkiGame()
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
