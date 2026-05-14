"""
摩托车狂飙
刺激的摩托车竞速游戏
"""

import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("摩托车狂飙")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (50, 50, 50)
RED = (220, 40, 40)
BLUE = (30, 100, 200)
GREEN = (34, 139, 34)
YELLOW = (255, 200, 0)
ORANGE = (255, 150, 0)
CYAN = (0, 200, 200)

class Bike:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = 0
        self.color = color
        self.angle = 0
        self.speed = 0
        self.max_speed = 12
        self.acceleration = 0.2
        self.wheelie = 0
        self.lean = 0
        self.trail = []
    
    def update(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.lean = max(-0.3, self.lean - 0.03)
        elif keys[pygame.K_RIGHT]:
            self.lean = min(0.3, self.lean + 0.03)
        else:
            self.lean *= 0.9
        
        if keys[pygame.K_UP]:
            self.speed += self.acceleration
        if keys[pygame.K_DOWN]:
            self.speed -= self.acceleration * 0.8
        
        if keys[pygame.K_LSHIFT] and self.speed > 5:
            self.wheelie = min(1.0, self.wheelie + 0.05)
        else:
            self.wheelie *= 0.9
        
        self.speed = max(-2, min(self.max_speed, self.speed))
        if not (keys[pygame.K_UP] or keys[pygame.K_DOWN]):
            self.speed *= 0.98
        
        self.vx = self.lean * self.speed * 2
        self.x += self.vx
        
        self.x = max(100, min(WIDTH - 100, self.x))
        
        self.trail.append((self.x, self.y))
        if len(self.trail) > 15:
            self.trail.pop(0)
    
    def draw(self):
        # 轨迹
        if self.wheelie > 0.3:
            for i, (tx, ty) in enumerate(self.trail):
                alpha = int(255 * (i / len(self.trail)) * 0.3)
                pygame.draw.circle(screen, (100, 100, 100, alpha), 
                                  (tx, ty + 25), 4)
        
        # 车身
        pygame.draw.ellipse(screen, self.color, 
                           (self.x - 35, self.y - 15 + self.wheelie * 10, 
                            70, 28))
        
        # 车头
        pygame.draw.rect(screen, self.color, 
                        (self.x + 20, self.y - 10 + self.wheelie * 15, 
                         20, 15))
        
        # 轮子
        wheel_y = self.y + 18
        pygame.draw.circle(screen, BLACK, (self.x - 25, wheel_y), 14)
        if self.wheelie < 0.8:
            pygame.draw.circle(screen, BLACK, (self.x + 30, wheel_y), 14)
        
        # 骑手
        pygame.draw.ellipse(screen, (200, 150, 100), 
                           (self.x - 10, self.y - 40 + self.wheelie * 20, 25, 40))
        pygame.draw.circle(screen, (255, 200, 150), 
                          (self.x + 5, self.y - 50 + self.wheelie * 25), 12)
        
        # 头盔
        pygame.draw.circle(screen, RED, 
                          (self.x + 5, self.y - 52 + self.wheelie * 25), 13)
        
        # 加速特效
        if self.speed > 8:
            for i in range(3):
                px = self.x - 40 - random.randint(0, 20)
                py = self.y - 5 + random.randint(-5, 10)
                pygame.draw.circle(screen, ORANGE, (px, py), 5)

class Obstacle:
    def __init__(self):
        self.x = random.randint(120, WIDTH - 120)
        self.y = -100
        self.width = random.randint(60, 100)
        self.height = random.randint(30, 50)
        self.color = random.choice([BLUE, ORANGE, GRAY, CYAN])
        self.type = random.choice(["car", "truck", "cone"])
    
    def update(self, speed):
        self.y += speed
    
    def draw(self):
        if self.type == "car":
            pygame.draw.rect(screen, self.color, 
                           (self.x - self.width//2, self.y, self.width, self.height))
            pygame.draw.rect(screen, (100, 150, 200), 
                           (self.x - self.width//2 + 10, self.y + 5, self.width - 20, 15))
        elif self.type == "truck":
            pygame.draw.rect(screen, self.color, 
                           (self.x - self.width//2, self.y, self.width, self.height))
            pygame.draw.rect(screen, (200, 100, 50), 
                           (self.x - self.width//2, self.y - 20, 40, 20))
        else:
            pygame.draw.polygon(screen, ORANGE, 
                               [(self.x, self.y), 
                                (self.x - 20, self.y + self.height), 
                                (self.x + 20, self.y + self.height)])

class TurboBikeGame:
    def __init__(self):
        self.player = Bike(WIDTH//2, HEIGHT - 150, RED)
        self.obstacles = []
        self.score = 0
        self.speed = 5
        self.game_over = False
        self.phase = "menu"
        self.road_offset = 0
        self.stripe_offset = 0
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 26)
    
    def reset(self):
        self.player = Bike(WIDTH//2, HEIGHT - 150, RED)
        self.obstacles = []
        self.score = 0
        self.speed = 5
        self.game_over = False
    
    def update(self):
        if self.phase != "game" or self.game_over:
            return
        
        self.player.update()
        
        self.speed = 5 + min(10, self.score // 2000) + max(0, self.player.speed // 3)
        self.score += int(self.speed // 2)
        
        self.road_offset = (self.road_offset + self.speed * 2) % (HEIGHT // 2)
        self.stripe_offset = (self.stripe_offset + self.speed) % 100
        
        # 生成障碍物
        spawn_rate = 0.015 + self.speed / 800
        if random.random() < spawn_rate:
            self.obstacles.append(Obstacle())
        
        # 更新
        for obs in self.obstacles:
            obs.update(self.speed)
        
        self.obstacles = [o for o in self.obstacles if o.y < HEIGHT + 100]
        
        # 碰撞
        for obs in self.obstacles:
            if self.check_collision(obs):
                self.game_over = True
                self.phase = "gameover"
    
    def check_collision(self, obs):
        obs_rect = pygame.Rect(obs.x - obs.width//2, obs.y, obs.width, obs.height)
        player_rect = pygame.Rect(self.player.x - 40, self.player.y - 30, 80, 60)
        return obs_rect.colliderect(player_rect)
    
    def draw(self):
        screen.fill(GREEN)
        
        # 道路
        pygame.draw.rect(screen, DARK_GRAY, (50, 0, WIDTH - 100, HEIGHT))
        
        # 路边
        pygame.draw.rect(screen, WHITE, (50, 0, 10, HEIGHT))
        pygame.draw.rect(screen, WHITE, (WIDTH - 60, 0, 10, HEIGHT))
        
        # 车道线
        for y in range(-100, HEIGHT + 100, 100):
            pygame.draw.rect(screen, YELLOW, 
                           (WIDTH//2 - 5, y + self.stripe_offset, 10, 50))
            pygame.draw.rect(screen, WHITE, 
                           (WIDTH//4 - 3, y + self.stripe_offset, 6, 40))
            pygame.draw.rect(screen, WHITE, 
                           (3*WIDTH//4 - 3, y + self.stripe_offset, 6, 40))
        
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
        overlay.set_alpha(160)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        title = self.font_large.render("摩托车狂飙", True, ORANGE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        instructions = [
            "← → 移动/倾斜",
            "↑ 加速",
            "↓ 减速",
            "Shift 抬前轮",
            "",
            "按 空格键 开始!!"
        ]
        
        y = 230
        for line in instructions:
            text = self.font_medium.render(line, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 40
        
        # 展示摩托
        bike = Bike(WIDTH//2, 520, RED)
        bike.draw()
    
    def draw_game(self):
        for obs in self.obstacles:
            obs.draw()
        
        self.player.draw()
        
        # HUD
        pygame.draw.rect(screen, (0, 0, 0, 150), (10, 10, 200, 90))
        
        score_text = self.font_medium.render(f"分数: {self.score}", True, YELLOW)
        speed_text = self.font_small.render(f"速度: {int(self.player.speed*30)} km/h", True, WHITE)
        wheely_text = self.font_small.render(f"抬前轮: {int(self.player.wheelie*100)}%", 
                                            True, ORANGE if self.player.wheelie>0.5 else WHITE)
        
        screen.blit(score_text, (20, 15))
        screen.blit(speed_text, (20, 45))
        screen.blit(wheely_text, (20, 70))
    
    def draw_gameover(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        title = self.font_large.render("游戏结束!", True, RED)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 180))
        
        final_score = self.font_medium.render(f"最终分数: {self.score}", True, WHITE)
        screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, 300))
        
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
    game = TurboBikeGame()
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
