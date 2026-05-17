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

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
RED = (255, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("超级玛丽风格平台跳跃")

clock = pygame.time.Clock()
font = get_chinese_font(30)

class Player:
    def __init__(self):
        self.width = 40
        self.height = 50
        self.x = 50
        self.y = HEIGHT - 150
        self.dx = 0
        self.dy = 0
        self.on_ground = False
        self.jumping = False
        self.facing_right = True
    
    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.dx = -5
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            self.dx = 5
            self.facing_right = True
        else:
            self.dx = 0
        
        if keys[pygame.K_SPACE] and self.on_ground:
            self.dy = -15
            self.on_ground = False
            self.jumping = True
    
    def update(self, platforms):
        self.dy += 0.8
        self.x += self.dx
        self.y += self.dy
        
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - self.width:
            self.x = WIDTH - self.width
        
        self.on_ground = False
        for platform in platforms:
            if self.dy > 0:
                if (self.x + self.width > platform.x and 
                    self.x < platform.x + platform.width and
                    self.y + self.height > platform.y and
                    self.y + self.height < platform.y + platform.height + 10):
                    self.y = platform.y - self.height
                    self.dy = 0
                    self.on_ground = True
                    self.jumping = False
        
        if self.y > HEIGHT:
            return True
        return False
    
    def draw(self):
        if self.facing_right:
            pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
        else:
            pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))

class Platform:
    def __init__(self, x, y, width, height=20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def draw(self):
        pygame.draw.rect(screen, BROWN, (self.x, self.y, self.width, self.height))

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.direction = 1
        self.speed = 2
    
    def update(self, left_bound, right_bound):
        self.x += self.speed * self.direction
        if self.x <= left_bound or self.x >= right_bound:
            self.direction *= -1
    
    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

def platformer():
    platforms = [
        Platform(0, HEIGHT - 20, WIDTH),
        Platform(100, 450, 150),
        Platform(300, 380, 150),
        Platform(500, 300, 150),
        Platform(200, 220, 150),
        Platform(400, 150, 200),
        Platform(650, 400, 100),
    ]
    
    player = Player()
    enemies = [Enemy(300, 410), Enemy(500, 260)]
    
    score = 0
    game_over = False
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        keys = pygame.key.get_pressed()
        player.move(keys)
        
        if player.update(platforms):
            game_over = True
        
        for enemy in enemies:
            enemy.update(100, 700)
            if (player.x < enemy.x + enemy.width and
                player.x + player.width > enemy.x and
                player.y < enemy.y + enemy.height and
                player.y + player.height > enemy.y):
                game_over = True
        
        if player.y < 200:
            score += 1
            player.y = 200
        
        for platform in platforms:
            platform.draw()
        
        player.draw()
        
        for enemy in enemies:
            enemy.draw()
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        instruction_text = font.render("方向键移动 | 空格跳跃", True, WHITE)
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, 10))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(RED)
    game_over_text = font.render(f"游戏结束! 得分: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    platformer()