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

WIDTH, HEIGHT = 400, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("赛车游戏")

clock = pygame.time.Clock()
font = get_chinese_font(30)

class Player:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.speed = 6
    
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 50:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - 50 - self.width:
            self.x += self.speed
    
    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))

class Obstacle:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = random.randint(60, WIDTH - 100)
        self.y = -self.height
        self.speed = 5
    
    def move(self):
        self.y += self.speed
    
    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

def draw_road(offset):
    screen.fill(GRAY)
    
    pygame.draw.rect(screen, BLACK, (0, 0, 50, HEIGHT))
    pygame.draw.rect(screen, BLACK, (WIDTH - 50, 0, 50, HEIGHT))
    
    for i in range(-1, HEIGHT // 100 + 2):
        pygame.draw.rect(screen, WHITE, 
                        (WIDTH//2 - 5, i*100 + (offset % 100), 10, 50))

def racing():
    player = Player()
    obstacles = []
    score = 0
    offset = 0
    game_over = False
    
    while not game_over:
        draw_road(offset)
        offset += 5
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        keys = pygame.key.get_pressed()
        player.move(keys)
        
        if random.randint(1, 60) == 1:
            obstacles.append(Obstacle())
        
        obstacles = [o for o in obstacles if o.y < HEIGHT]
        for obstacle in obstacles:
            obstacle.move()
        
        for obstacle in obstacles:
            if (obstacle.x < player.x + player.width and
                obstacle.x + obstacle.width > player.x and
                obstacle.y < player.y + player.height and
                obstacle.y + obstacle.height > player.y):
                game_over = True
        
        score += 1
        
        player.draw()
        for obstacle in obstacles:
            obstacle.draw()
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(RED)
    game_over_text = font.render(f"游戏结束! 得分: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    racing()