import pygame
import os
import sys

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
pygame.display.set_caption("法拉利赛车")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
GRAY = (100, 100, 100)

class FerrariRacing:
    def __init__(self):
        self.car_x = WIDTH // 2
        self.car_y = HEIGHT - 100
        self.speed = 0
        self.acceleration = 0.3
        self.max_speed = 18
        self.score = 0
        self.obstacles = []
        self.font = get_chinese_font(32)
        self.clock = pygame.time.Clock()

    def update(self):
        self.car_y -= self.speed
        
        if self.car_y <= -50:
            self.car_y = HEIGHT
            self.score += 10
        
        for obstacle in self.obstacles:
            obstacle["y"] += 5
            if obstacle["y"] > HEIGHT:
                self.obstacles.remove(obstacle)
        
        if random.random() < 0.02:
            self.obstacles.append({
                "x": random.randint(150, 650),
                "y": -50
            })
        
        for obstacle in self.obstacles:
            distance = ((self.car_x - obstacle["x"])**2 + (self.car_y - obstacle["y"])**2)**0.5
            if distance < 30:
                self.game_over()

    def draw(self):
        screen.fill(GRAY)
        
        pygame.draw.rect(screen, WHITE, (100, 0, 10, HEIGHT))
        pygame.draw.rect(screen, WHITE, (700, 0, 10, HEIGHT))
        
        pygame.draw.rect(screen, RED, (self.car_x - 25, self.car_y - 35, 50, 70), border_radius=10)
        pygame.draw.circle(screen, BLACK, (self.car_x - 15, self.car_y + 30), 10)
        pygame.draw.circle(screen, BLACK, (self.car_x + 15, self.car_y + 30), 10)
        
        for obstacle in self.obstacles:
            pygame.draw.rect(screen, BLACK, (obstacle["x"] - 15, obstacle["y"], 30, 30))
        
        speed_text = self.font.render(f"速度: {int(self.speed)}", True, WHITE)
        screen.blit(speed_text, (50, 50))
        
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (50, 80))

    def handle_input(self, event):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] and self.car_x > 120:
            self.car_x -= 6
        if keys[pygame.K_RIGHT] and self.car_x < 680:
            self.car_x += 6
        if keys[pygame.K_UP] and self.speed < self.max_speed:
            self.speed += self.acceleration
        if keys[pygame.K_DOWN] and self.speed > 0:
            self.speed -= self.acceleration * 2

    def game_over(self):
        screen.fill(BLACK)
        game_over_text = self.font.render(f"游戏结束！得分: {self.score}", True, RED)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, 250))
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

game = FerrariRacing()
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