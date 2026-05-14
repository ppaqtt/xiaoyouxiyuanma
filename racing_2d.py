"""
2D赛车竞速
经典的2D赛车竞速游戏
"""

import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D赛车竞速")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (60, 60, 60)
RED = (200, 50, 50)
BLUE = (50, 100, 200)
GREEN = (50, 180, 50)
YELLOW = (255, 200, 0)
ORANGE = (255, 150, 0)

class Car:
    def __init__(self, x, y, color, is_player=False):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.color = color
        self.is_player = is_player
        self.width = 40
        self.height = 70
        self.angle = 0
        self.speed = 0
        self.max_speed = 8
        self.acceleration = 0.15
    
    def update(self):
        if self.is_player:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.angle -= 3
            if keys[pygame.K_RIGHT]:
                self.angle += 3
            if keys[pygame.K_UP]:
                self.speed += self.acceleration
            if keys[pygame.K_DOWN]:
                self.speed -= self.acceleration * 0.8
        
        # 限制速度
        self.speed = max(-3, min(self.max_speed, self.speed))
        
        # 摩擦力
        if self.is_player:
            if not pygame.key.get_pressed()[pygame.K_UP] and not pygame.key.get_pressed()[pygame.K_DOWN]:
                self.speed *= 0.98
        
        # 移动
        rad = math.radians(self.angle)
        self.x += math.sin(rad) * self.speed
        self.y -= math.cos(rad) * self.speed
        
        # 边界检查
        self.x = max(200, min(WIDTH - 200, self.x))
    
    def draw(self):
        # 保存原始坐标
        orig_x, orig_y = self.x, self.y
        
        # 绘制车身
        pygame.draw.rect(screen, self.color, 
                       (self.x - self.width//2, self.y - self.height//2, 
                        self.width, self.height), border_radius=8)
        
        # 车窗
        pygame.draw.rect(screen, (150, 200, 255), 
                       (self.x - 12, self.y - 15, 24, 25), border_radius=3)
        
        # 轮子
        pygame.draw.rect(screen, BLACK, (self.x - 18, self.y - 30, 8, 15))
        pygame.draw.rect(screen, BLACK, (self.x + 10, self.y - 30, 8, 15))
        pygame.draw.rect(screen, BLACK, (self.x - 18, self.y + 15, 8, 15))
        pygame.draw.rect(screen, BLACK, (self.x + 10, self.y + 15, 8, 15))

class Obstacle:
    def __init__(self):
        self.x = random.randint(250, WIDTH - 250)
        self.y = -100
        self.width = random.randint(50, 80)
        self.height = random.randint(20, 30)
        self.color = random.choice([RED, BLUE, ORANGE])
    
    def update(self, speed):
        self.y += speed
    
    def draw(self):
        pygame.draw.rect(screen, self.color, 
                       (self.x - self.width//2, self.y, self.width, self.height), border_radius=5)

class Coin:
    def __init__(self):
        self.x = random.randint(250, WIDTH - 250)
        self.y = -50
        self.radius = 12
        self.collected = False
    
    def update(self, speed):
        self.y += speed
    
    def draw(self):
        if not self.collected:
            pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius)
            pygame.draw.circle(screen, (200, 150, 0), (self.x, self.y), self.radius, 2)

class RacingGame:
    def __init__(self):
        self.player = Car(WIDTH//2, HEIGHT - 150, RED, True)
        self.obstacles = []
        self.coins = []
        self.score = 0
        self.distance = 0
        self.speed = 3
        self.game_over = False
        self.phase = "menu"
        self.road_offset = 0
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
    
    def reset(self):
        self.player = Car(WIDTH//2, HEIGHT - 150, RED, True)
        self.obstacles = []
        self.coins = []
        self.score = 0
        self.distance = 0
        self.speed = 3
        self.game_over = False
    
    def update(self):
        if self.phase != "game" or self.game_over:
            return
        
        self.player.update()
        
        # 速度根据玩家调整
        self.speed = 3 + self.distance // 2000 + max(0, self.player.speed // 2)
        
        self.distance += self.speed // 2
        self.road_offset = (self.road_offset + self.speed) % 100
        
        # 生成障碍物
        if random.random() < 0.02 + self.distance / 20000:
            self.obstacles.append(Obstacle())
        
        if random.random() < 0.015:
            self.coins.append(Coin())
        
        # 更新
        for obs in self.obstacles:
            obs.update(self.speed)
        for coin in self.coins:
            coin.update(self.speed)
        
        # 移除超出屏幕的
        self.obstacles = [o for o in self.obstacles if o.y < HEIGHT + 50]
        self.coins = [c for c in self.coins if c.y < HEIGHT + 50]
        
        # 碰撞检测
        for obs in self.obstacles:
            if self.check_collision(obs):
                self.game_over = True
                self.phase = "gameover"
        
        for coin in self.coins:
            if not coin.collected and self.check_coin_collision(coin):
                coin.collected = True
                self.score += 10
    
    def check_collision(self, obs):
        return (self.player.x - self.player.width//2 < obs.x + obs.width//2 and
                self.player.x + self.player.width//2 > obs.x - obs.width//2 and
                self.player.y - self.player.height//2 < obs.y + obs.height and
                self.player.y + self.player.height//2 > obs.y)
    
    def check_coin_collision(self, coin):
        dx = self.player.x - coin.x
        dy = self.player.y - coin.y
        return dx*dx + dy*dy < (30 + coin.radius) ** 2
    
    def draw(self):
        screen.fill(GREEN)
        
        # 道路
        pygame.draw.rect(screen, DARK_GRAY, (150, 0, WIDTH - 300, HEIGHT))
        pygame.draw.rect(screen, WHITE, (150, 0, 5, HEIGHT))
        pygame.draw.rect(screen, WHITE, (WIDTH - 155, 0, 5, HEIGHT))
        
        # 道路线
        for y in range(-100, HEIGHT + 100, 100):
            pygame.draw.rect(screen, YELLOW, (WIDTH//2 - 5, y + self.road_offset, 10, 50))
        
        if self.phase == "menu":
            self.draw_menu()
        elif self.phase == "game":
            self.draw_game()
        elif self.phase == "gameover":
            self.draw_game()
            self.draw_gameover()
        
        pygame.display.flip()
    
    def draw_menu(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        title = self.font_large.render("2D赛车竞速", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        instructions = [
            "↑ ↓ 加速/减速",
            "← → 左右移动",
            "收集金币得分",
            "躲避障碍",
            "",
            "按 空格键 开始"
        ]
        
        y = 250
        for line in instructions:
            text = self.font_medium.render(line, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 40
    
    def draw_game(self):
        # 障碍物
        for obs in self.obstacles:
            obs.draw()
        
        for coin in self.coins:
            coin.draw()
        
        # 玩家
        self.player.draw()
        
        # HUD
        pygame.draw.rect(screen, (0, 0, 0, 150), (10, 10, 180, 80), border_radius=10)
        score_text = self.font_medium.render(f"分数: {self.score}", True, YELLOW)
        dist_text = self.font_small.render(f"距离: {self.distance}", True, WHITE)
        screen.blit(score_text, (20, 15))
        screen.blit(dist_text, (20, 45))
        
        if self.game_over:
            self.draw_gameover()
    
    def draw_gameover(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        title = self.font_large.render("游戏结束!", True, RED)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        
        final = self.font_medium.render(f"最终分数: {self.score}", True, WHITE)
        screen.blit(final, (WIDTH//2 - final.get_width()//2, 300))
        
        restart = self.font_medium.render("按 R 重新开始", True, GREEN)
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 400))
    
    def handle_key(self, key):
        if self.phase == "menu":
            if key == pygame.K_SPACE:
                self.phase = "game"
        elif self.phase == "gameover":
            if key == pygame.K_r:
                self.reset()
                self.phase = "game"

def main():
    game = RacingGame()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.phase == "game":
                        game.phase = "menu"
                    else:
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
