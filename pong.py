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

WIDTH, HEIGHT = 800, 500

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong 乒乓球")

clock = pygame.time.Clock()
font = get_chinese_font(50)

class Paddle:
    def __init__(self, x, color):
        self.x = x
        self.y = HEIGHT // 2 - 50
        self.width = 10
        self.height = 100
        self.color = color
        self.speed = 6
        self.score = 0
    
    def move(self, keys, is_left):
        if is_left:
            if keys[pygame.K_w] and self.y > 0:
                self.y -= self.speed
            if keys[pygame.K_s] and self.y < HEIGHT - self.height:
                self.y += self.speed
        else:
            if keys[pygame.K_UP] and self.y > 0:
                self.y -= self.speed
            if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height:
                self.y += self.speed
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Ball:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.size = 15
        self.dx = random.choice([-4, 4])
        self.dy = random.choice([-3, 3])
    
    def move(self):
        self.x += self.dx
        self.y += self.dy
        
        if self.y <= 0 or self.y >= HEIGHT - self.size:
            self.dy *= -1
    
    def draw(self):
        pygame.draw.ellipse(screen, WHITE, (self.x, self.y, self.size, self.size))

def pong():
    left_paddle = Paddle(30, WHITE)
    right_paddle = Paddle(WIDTH - 40, WHITE)
    ball = Ball()
    game_over = False
    winner = None
    
    while not game_over:
        screen.fill(BLACK)
        
        pygame.draw.line(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 3)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        keys = pygame.key.get_pressed()
        left_paddle.move(keys, is_left=True)
        right_paddle.move(keys, is_left=False)
        
        ball.move()
        
        if ball.x <= left_paddle.x + left_paddle.width and ball.y >= left_paddle.y and ball.y <= left_paddle.y + left_paddle.height:
            ball.dx *= -1.1
            ball.x = left_paddle.x + left_paddle.width
        if ball.x >= right_paddle.x - ball.size and ball.y >= right_paddle.y and ball.y <= right_paddle.y + right_paddle.height:
            ball.dx *= -1.1
            ball.x = right_paddle.x - ball.size
        
        if ball.x < 0:
            right_paddle.score += 1
            ball.reset()
            if right_paddle.score >= 5:
                winner = "右边"
                game_over = True
        if ball.x > WIDTH:
            left_paddle.score += 1
            ball.reset()
            if left_paddle.score >= 5:
                winner = "左边"
                game_over = True
        
        left_paddle.draw()
        right_paddle.draw()
        ball.draw()
        
        left_score = font.render(str(left_paddle.score), True, WHITE)
        right_score = font.render(str(right_paddle.score), True, WHITE)
        screen.blit(left_score, (WIDTH // 4, 30))
        screen.blit(right_score, (WIDTH - WIDTH // 4, 30))
        
        instruction_text = font.render("W/S 左 | ↑/↓ 右", True, WHITE)
        screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT - 50))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    win_text = font.render(f"{winner}获胜!", True, WHITE)
    screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    pong()