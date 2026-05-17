"""
双摇杆射击
经典射击游戏
"""

import pygame
import os
import sys
import random
import math

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

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("双摇杆射击")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
BLUE = (0, 100, 200)
RED = (200, 50, 50)
GREEN = (0, 180, 100)
PURPLE = (150, 50, 200)
YELLOW = (255, 220, 0)

class Player:
    def __init__(self):
        self.x = WIDTH//2
        self.y = HEIGHT//2
        self.radius = 20
        self.speed = 5
        self.health = 100
    
    def update(self, keys):
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.speed
        
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))
    
    def draw(self):
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius - 5)

class Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = 6
        self.speed = 10
    
    def update(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
    
    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)

class Enemy:
    def __init__(self):
        self.x = random.choice([-50, WIDTH + 50, random.randint(0, WIDTH)])
        if self.x < 0 or self.x > WIDTH:
            self.y = random.randint(0, HEIGHT)
        else:
            self.y = random.choice([-50, HEIGHT + 50])
        
        self.radius = random.randint(15, 30)
        self.speed = random.uniform(1, 3)
        self.color = random.choice([RED, PURPLE, (200, 100, 0)])
    
    def update(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius - 5)

class ShooterGame:
    def __init__(self):
        self.phase = "menu"
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.score = 0
        self.last_shot = 0
        self.font_large = get_chinese_font(64)
        self.font_medium = get_chinese_font(36)
        self.font_small = get_chinese_font(26)
    
    def reset(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.score = 0
        self.phase = "game"
    
    def draw(self):
        screen.fill((30, 30, 40))
        
        # 网格
        for x in range(0, WIDTH, 50):
            pygame.draw.line(screen, (50, 50, 60), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 50):
            pygame.draw.line(screen, (50, 50, 60), (0, y), (WIDTH, y))
        
        if self.phase == "menu":
            self.draw_menu()
        elif self.phase in ["game", "gameover"]:
            self.draw_game()
        
        pygame.display.flip()
    
    def draw_menu(self):
        title = self.font_large.render("双摇杆射击", True, GREEN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        instructions = [
            "WASD/方向键移动",
            "鼠标瞄准",
            "点击射击!",
            "",
            "按 空格键 开始!"
        ]
        
        y = 230
        for line in instructions:
            text = self.font_medium.render(line, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 40
    
    def draw_game(self):
        # 绘制敌人
        for e in self.enemies:
            e.draw()
        
        # 绘制子弹
        for b in self.bullets:
            b.draw()
        
        # 绘制玩家
        self.player.draw()
        
        # 准星
        mx, my = pygame.mouse.get_pos()
        pygame.draw.line(screen, WHITE, (mx - 10, my), (mx + 10, my), 2)
        pygame.draw.line(screen, WHITE, (mx, my - 10), (mx, my + 10), 2)
        
        # HUD
        pygame.draw.rect(screen, (0, 0, 0, 150), (0, 0, WIDTH, 60))
        
        score_text = self.font_medium.render(f"分数: {self.score}", True, YELLOW)
        screen.blit(score_text, (20, 15))
        
        health_text = self.font_medium.render(f"生命: {self.player.health}", True, GREEN)
        screen.blit(health_text, (200, 15))
        
        if self.phase == "gameover":
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            title = self.font_large.render("游戏结束!", True, RED)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
            
            final = self.font_medium.render(f"最终分数: {self.score}", True, WHITE)
            screen.blit(final, (WIDTH//2 - final.get_width()//2, 300))
            
            restart = self.font_medium.render("按 R 再来一局", True, GREEN)
            screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 400))
    
    def update(self):
        if self.phase != "game":
            return
        
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        
        # 生成敌人
        if random.random() < 0.02 + min(0.05, self.score / 5000):
            self.enemies.append(Enemy())
        
        # 更新子弹
        for b in self.bullets:
            b.update()
        
        self.bullets = [b for b in self.bullets 
                       if 0 < b.x < WIDTH and 0 < b.y < HEIGHT]
        
        # 更新敌人
        for e in self.enemies:
            e.update(self.player)
        
        # 碰撞检测
        for e in self.enemies[:]:
            for b in self.bullets[:]:
                dx = e.x - b.x
                dy = e.y - b.y
                if dx*dx + dy*dy < (e.radius + b.radius)**2:
                    if e in self.enemies:
                        self.enemies.remove(e)
                    if b in self.bullets:
                        self.bullets.remove(b)
                    self.score += 10
        
        # 敌人碰撞玩家
        for e in self.enemies[:]:
            dx = e.x - self.player.x
            dy = e.y - self.player.y
            if dx*dx + dy*dy < (e.radius + self.player.radius)**2:
                self.player.health -= 10
                if e in self.enemies:
                    self.enemies.remove(e)
        
        if self.player.health <= 0:
            self.phase = "gameover"
    
    def shoot(self, pos):
        now = pygame.time.get_ticks()
        if now - self.last_shot < 150:
            return
        
        self.last_shot = now
        
        dx = pos[0] - self.player.x
        dy = pos[1] - self.player.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            self.bullets.append(Bullet(self.player.x, self.player.y, 
                                      dx/dist, dy/dist))
    
    def handle_key(self, key):
        if self.phase == "menu":
            if key == pygame.K_SPACE:
                self.reset()
        elif self.phase == "gameover":
            if key == pygame.K_r:
                self.reset()

def main():
    game = ShooterGame()
    pygame.mouse.set_visible(False)
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.shoot(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    game.handle_key(event.key)
        
        game.update()
        game.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
