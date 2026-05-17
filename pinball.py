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
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("简易弹球游戏")

clock = pygame.time.Clock()
font = get_chinese_font(30)

class Ball:
    def __init__(self):
        self.radius = 10
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.dx = 0
        self.dy = 0
        self.launched = False
    
    def launch(self):
        if not self.launched:
            self.dx = random.choice([-3, 3])
            self.dy = -7
            self.launched = True
    
    def move(self):
        if self.launched:
            self.x += self.dx
            self.y += self.dy
            self.dy += 0.1
    
    def bounce(self):
        if self.x <= self.radius or self.x >= WIDTH - self.radius:
            self.dx *= -1
        if self.y <= self.radius:
            self.dy *= -2

class Flipper:
    def __init__(self, x, y, width, height, is_left):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = 0
        self.is_left = is_left
    
    def flip(self, up):
        if up:
            self.angle = -30 if self.is_left else 30
        else:
            self.angle = 0
    
    def draw(self):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(surface, GREEN, (0, 0, self.width, self.height))
        rotated = pygame.transform.rotate(surface, self.angle)
        if self.is_left:
            screen.blit(rotated, (self.x, self.y))
        else:
            screen.blit(rotated, (self.x - self.width // 2, self.y))

class Bumper:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 25
    
    def draw(self):
        pygame.draw.circle(screen, RED, (self.x, self.y), self.radius)

def pinball():
    ball = Ball()
    left_flipper = Flipper(50, HEIGHT - 80, 80, 20, True)
    right_flipper = Flipper(WIDTH - 130, HEIGHT - 80, 80, 20, False)
    
    bumpers = [
        Bumper(100, 200), Bumper(WIDTH-100, 200), Bumper(WIDTH//2, 150),
        Bumper(150, 350), Bumper(WIDTH-150, 350), Bumper(WIDTH//2, 400)
    ]
    
    score = 0
    game_over = False
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    ball.launch()
            elif event.type == pygame.KEYUP:
                pass
        
        keys = pygame.key.get_pressed()
        left_flipper.flip(keys[pygame.K_LEFT])
        right_flipper.flip(keys[pygame.K_RIGHT])
        
        ball.move()
        ball.bounce()
        
        if ball.y > HEIGHT:
            game_over = True
        
        for bumper in bumpers:
            dx = ball.x - bumper.x
            dy = ball.y - bumper.y
            distance = (dx**2 + dy**2)**0.5
            if distance < ball.radius + bumper.radius:
                ball.dx = dx * 0.3
                ball.dy = -abs(ball.dy) * 1.2
                score += 100
        
        for bumper in bumpers:
            bumper.draw()
        left_flipper.draw()
        right_flipper.draw()
        pygame.draw.circle(screen, YELLOW, (ball.x, ball.y), ball.radius)
        
        if not ball.launched:
            start_text = font.render("按空格键发射!", True, WHITE)
            screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT - 150))
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    game_over_text = font.render(f"游戏结束! 得分: {score}", True, RED)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    pinball()