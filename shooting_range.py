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
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("打靶游戏")

clock = pygame.time.Clock()
font = get_chinese_font(40)

class Target:
    def __init__(self):
        self.radius = random.randint(20, 50)
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT - 100)
        self.dx = random.choice([-3, 3])
        self.dy = random.choice([-2, 2])
        self.points = 50 - self.radius
    
    def move(self):
        self.x += self.dx
        self.y += self.dy
        
        if self.x <= self.radius or self.x >= WIDTH - self.radius:
            self.dx *= -1
        if self.y <= self.radius or self.y >= HEIGHT - self.radius:
            self.dy *= -1
    
    def draw(self):
        pygame.draw.circle(screen, RED, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius - 10)
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius // 2)
        pygame.draw.circle(screen, RED, (self.x, self.y), 5)

def shooting_range():
    targets = []
    for _ in range(3):
        targets.append(Target())
    
    score = 0
    time_left = 30
    game_over = False
    start_ticks = pygame.time.get_ticks()
    
    pygame.mouse.set_visible(False)
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                
                for target in targets[:]:
                    distance = ((x - target.x) ** 2 + (y - target.y) ** 2) ** 0.5
                    if distance <= target.radius:
                        score += target.points
                        targets.remove(target)
                        targets.append(Target())
                        break
        
        for target in targets:
            target.move()
            target.draw()
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.circle(screen, WHITE, (mouse_x, mouse_y), 5)
        pygame.draw.circle(screen, WHITE, (mouse_x, mouse_y), 15, 2)
        pygame.draw.line(screen, WHITE, (mouse_x - 20, mouse_y), (mouse_x + 20, mouse_y), 1)
        pygame.draw.line(screen, WHITE, (mouse_x, mouse_y - 20), (mouse_x, mouse_y + 20), 1)
        
        seconds = max(0, time_left - (pygame.time.get_ticks() - start_ticks) // 1000)
        if seconds == 0:
            game_over = True
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        time_text = font.render(f"时间: {seconds}秒", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (WIDTH - 150, 10))
        
        pygame.display.update()
        clock.tick(60)
    
    pygame.mouse.set_visible(True)
    
    screen.fill(BLACK)
    game_over_text = font.render(f"游戏结束! 得分: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    shooting_range()