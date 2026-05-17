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
GREEN = (0, 200, 0)
BLUE = (100, 100, 200)
RED = (200, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("跳一跳")

clock = pygame.time.Clock()
font = get_chinese_font(40)

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 150
        self.radius = 20
        self.dy = 0
        self.gravity = 0.5
        self.jumping = False
    
    def update(self):
        self.dy += self.gravity
        self.y += self.dy
        
        if self.y > HEIGHT + 50:
            return True
        return False
    
    def draw(self):
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.radius)

class Platform:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = random.randint(60, 120)
        self.height = 20
    
    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height), border_radius=5)

def jump_game():
    player = Player()
    platforms = []
    
    for i in range(10):
        platforms.append(Platform(
            random.randint(50, WIDTH - 150),
            HEIGHT - 100 - i * 60
        ))
    
    score = 0
    game_over = False
    camera_y = 0
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not player.jumping:
                    player.dy = -12
                    player.jumping = True
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x = max(player.radius, player.x - 4)
        if keys[pygame.K_RIGHT]:
            player.x = min(WIDTH - player.radius, player.x + 4)
        
        if player.update():
            game_over = True
        
        for platform in platforms:
            if (player.dy > 0 and
                platform.y - player.y > 0 and
                platform.y - player.y < 20 and
                platform.x < player.x < platform.x + platform.width):
                player.y = platform.y - player.radius
                player.dy = 0
                player.jumping = False
                
                if platform.y < HEIGHT // 2:
                    camera_y = HEIGHT // 2 - platform.y
        
        if player.y < HEIGHT // 2:
            camera_y = HEIGHT // 2 - player.y
        
        while platforms[-1].y + camera_y > -50:
            new_platform = Platform(
                random.randint(50, WIDTH - 150),
                platforms[-1].y - random.randint(50, 80)
            )
            platforms.append(new_platform)
        
        platforms = [p for p in platforms if p.y + camera_y < HEIGHT + 50]
        
        for platform in platforms:
            pygame.draw.rect(screen, GREEN,
                (platform.x, platform.y + camera_y, platform.width, platform.height), border_radius=5)
        
        pygame.draw.circle(screen, BLUE,
            (int(player.x), int(player.y + camera_y)), player.radius)
        
        score = int(-camera_y // 10)
        score_text = font.render(f"分数: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    game_over_text = font.render(f"游戏结束! 得分: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    jump_game()