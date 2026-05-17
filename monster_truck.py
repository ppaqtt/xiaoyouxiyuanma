import pygame
import os
import sys
import random

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
pygame.display.set_caption("怪物卡车")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
BROWN = (139, 90, 43)
GREEN = (50, 200, 50)

class MonsterTruck:
    def __init__(self):
        self.truck_x = WIDTH // 2
        self.truck_y = HEIGHT - 150
        self.speed = 3
        self.score = 0
        self.obstacles = []
        self.font = get_chinese_font(32)
        self.clock = pygame.time.Clock()

    def update(self):
        self.truck_y -= self.speed
        
        if self.truck_y <= -100:
            self.truck_y = HEIGHT
            self.score += 20
        
        for obstacle in self.obstacles:
            obstacle["y"] += 4
            if obstacle["y"] > HEIGHT:
                self.obstacles.remove(obstacle)
        
        if random.random() < 0.015:
            self.obstacles.append({
                "x": random.randint(150, 650),
                "y": -50,
                "type": random.choice(["rock", "barrier"])
            })
        
        for obstacle in self.obstacles:
            distance = ((self.truck_x - obstacle["x"])**2 + (self.truck_y - obstacle["y"])**2)**0.5
            if distance < 40:
                if obstacle["type"] == "rock":
                    self.score += 5
                    self.obstacles.remove(obstacle)
                else:
                    self.game_over()

    def draw(self):
        screen.fill(GREEN)
        
        pygame.draw.rect(screen, BROWN, (100, 0, 20, HEIGHT))
        pygame.draw.rect(screen, BROWN, (680, 0, 20, HEIGHT))
        
        pygame.draw.rect(screen, RED, (self.truck_x - 35, self.truck_y - 50, 70, 80), border_radius=5)
        pygame.draw.circle(screen, BLACK, (self.truck_x - 20, self.truck_y + 25), 18)
        pygame.draw.circle(screen, BLACK, (self.truck_x + 20, self.truck_y + 25), 18)
        
        for obstacle in self.obstacles:
            if obstacle["type"] == "rock":
                pygame.draw.circle(screen, (100, 100, 100), (obstacle["x"], obstacle["y"]), 20)
            else:
                pygame.draw.rect(screen, BLACK, (obstacle["x"] - 25, obstacle["y"], 50, 40))
        
        speed_text = self.font.render(f"速度: {int(self.speed)}", True, BLACK)
        screen.blit(speed_text, (50, 50))
        
        score_text = self.font.render(f"分数: {self.score}", True, BLACK)
        screen.blit(score_text, (50, 80))

    def handle_input(self, event):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] and self.truck_x > 130:
            self.truck_x -= 5
        if keys[pygame.K_RIGHT] and self.truck_x < 670:
            self.truck_x += 5
        if keys[pygame.K_UP] and self.speed < 12:
            self.speed += 0.2
        if keys[pygame.K_DOWN] and self.speed > 2:
            self.speed -= 0.3

    def game_over(self):
        screen.fill(BLACK)
        game_over_text = self.font.render(f"游戏结束！得分: {self.score}", True, RED)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, 250))
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

game = MonsterTruck()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    game.handle_input(event)
    game.update()
    game.draw()
    pygame.display.flip()
    game.clock.tick(60)

pygame.quit()