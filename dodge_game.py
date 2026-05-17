import pygame
import os
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

WIDTH, HEIGHT = 600, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("躲避球")

clock = pygame.time.Clock()
font = get_chinese_font(30)

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 50
        self.radius = 20
        self.speed = 6
    
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > self.radius:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.radius:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > self.radius:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.radius:
            self.y += self.speed
    
    def draw(self):
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), self.radius)

class Ball:
    def __init__(self):
        self.x = random.randint(20, WIDTH - 20)
        self.y = random.randint(20, HEIGHT // 2)
        self.radius = random.randint(10, 25)
        self.dx = random.uniform(-3, 3)
        self.dy = random.uniform(-3, 3)
        self.color = random.choice([RED, BLUE, YELLOW])
    
    def move(self):
        self.x += self.dx
        self.y += self.dy
        
        if self.x <= self.radius or self.x >= WIDTH - self.radius:
            self.dx *= -1
        if self.y <= self.radius or self.y >= HEIGHT - self.radius:
            self.dy *= -1
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

def dodge_game():
    player = Player()
    balls = []
    score = 0
    game_over = False
    
    for _ in range(5):
        balls.append(Ball())
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        keys = pygame.key.get_pressed()
        player.move(keys)
        
        if random.randint(1, 100) == 1:
            balls.append(Ball())
        
        for ball in balls[:]:
            ball.move()
            
            distance = ((player.x - ball.x) ** 2 + (player.y - ball.y) ** 2) ** 0.5
            if distance < player.radius + ball.radius:
                game_over = True
        
        player.draw()
        for ball in balls:
            ball.draw()
        
        score += 1
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        balls_text = font.render(f"球数: {len(balls)}", True, WHITE)
        screen.blit(balls_text, (WIDTH - 100, 10))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    game_over_text = font.render(f"游戏结束! 得分: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    dodge_game()