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

WIDTH, HEIGHT = 500, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
COLORS = [
    (255, 0, 0),    # 苹果 - 红
    (255, 165, 0),  # 橙子 - 橙
    (255, 255, 0),  # 柠檬 - 黄
    (0, 255, 0),    # 苹果 - 绿
    (255, 192, 203), # 草莓 - 粉
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("接水果")

clock = pygame.time.Clock()
font = get_chinese_font(40)

class Basket:
    def __init__(self):
        self.width = 100
        self.height = 40
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.speed = 8
    
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed
    
    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
        pygame.draw.ellipse(screen, GREEN, (self.x - 10, self.y - 20, self.width + 20, 30))

class Fruit:
    def __init__(self):
        self.radius = 20
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = -self.radius
        self.color = random.choice(COLORS)
        self.speed = random.randint(3, 7)
    
    def move(self):
        self.y += self.speed
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class Bomb:
    def __init__(self):
        self.radius = 20
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = -self.radius
        self.speed = random.randint(3, 7)
    
    def move(self):
        self.y += self.speed
    
    def draw(self):
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius, 3)
        pygame.draw.line(screen, BLACK, (self.x - 15, self.y - 20), (self.x + 15, self.y + 20), 3)
        pygame.draw.line(screen, BLACK, (self.x + 15, self.y - 20), (self.x - 15, self.y + 20), 3)

def catch_fruit():
    basket = Basket()
    fruits = []
    bombs = []
    score = 0
    lives = 3
    game_over = False
    
    while not game_over:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        keys = pygame.key.get_pressed()
        basket.move(keys)
        
        if random.randint(1, 40) == 1:
            fruits.append(Fruit())
        
        if random.randint(1, 100) == 1:
            bombs.append(Bomb())
        
        for fruit in fruits[:]:
            fruit.move()
            if fruit.y > HEIGHT:
                fruits.remove(fruit)
            else:
                if (basket.x < fruit.x < basket.x + basket.width and
                    basket.y < fruit.y < basket.y + basket.height):
                    fruits.remove(fruit)
                    score += 10
        
        for bomb in bombs[:]:
            bomb.move()
            if bomb.y > HEIGHT:
                bombs.remove(bomb)
            else:
                if (basket.x < bomb.x < basket.x + basket.width and
                    basket.y < bomb.y < basket.y + basket.height):
                    bombs.remove(bomb)
                    lives -= 1
                    if lives == 0:
                        game_over = True
        
        basket.draw()
        for fruit in fruits:
            fruit.draw()
        for bomb in bombs:
            bomb.draw()
        
        score_text = font.render(f"分数: {score}", True, BLACK)
        lives_text = font.render(f"生命: {lives}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 80, 10))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    game_over_text = font.render(f"游戏结束! 得分: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    catch_fruit()