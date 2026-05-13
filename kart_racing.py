"""
卡丁车赛道
趣味卡丁车竞速游戏
"""

import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 900, 680
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("卡丁车赛道")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (80, 80, 80)
RED = (255, 50, 50)
BLUE = (50, 100, 255)
GREEN = (50, 200, 50)
YELLOW = (255, 220, 0)
ORANGE = (255, 140, 0)
PINK = (255, 105, 180)
PURPLE = (150, 50, 200)

class Kart:
    def __init__(self, x, y, color, is_player=False):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.color = color
        self.is_player = is_player
        self.width = 50
        self.height = 40
        self.angle = 0
        self.speed = 0
        self.max_speed = 6
        self.acceleration = 0.18
        self.drift_power = 0
        self.item = None
        self.boost_power = 1.0
    
    def update(self):
        if self.is_player:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.angle -= 3.5
            if keys[pygame.K_RIGHT]:
                self.angle += 3.5
            if keys[pygame.K_UP]:
                self.speed += self.acceleration * self.boost_power
            if keys[pygame.K_DOWN]:
                self.speed -= self.acceleration * 0.6
            if keys[pygame.K_LSHIFT] and abs(self.angle) > 5:
                self.drift_power = min(1.0, self.drift_power + 0.02)
            else:
                self.drift_power *= 0.95
        
        # 速度限制
        self.speed = max(-2, min(self.max_speed * self.boost_power, self.speed))
        
        # 减速
        if self.is_player:
            if not (pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_DOWN]):
                self.speed *= 0.97
        
        self.boost_power = max(1.0, self.boost_power - 0.002)
        
        rad = math.radians(self.angle)
        self.x += math.sin(rad) * self.speed
        self.y -= math.cos(rad) * self.speed
        
        # 边界
        self.x = max(50, min(WIDTH - 50, self.x))
        self.y = max(50, min(HEIGHT - 50, self.y))
    
    def draw(self):
        # 车身
        pygame.draw.ellipse(screen, self.color, 
                           (self.x - self.width//2, self.y - self.height//2, 
                            self.width, self.height), border_radius=15)
        
        # 车窗
        pygame.draw.rect(screen, (100, 180, 255), 
                       (self.x - 10, self.y - 8, 20, 15), border_radius=4)
        
        # 轮子
        pygame.draw.circle(screen, BLACK, (self.x - 20, self.y - 15), 8)
        pygame.draw.circle(screen, BLACK, (self.x + 20, self.y - 15), 8)
        pygame.draw.circle(screen, BLACK, (self.x - 20, self.y + 15), 8)
        pygame.draw.circle(screen, BLACK, (self.x + 20, self.y + 15), 8)
        
        # 漂移特效
        if self.drift_power > 0.2:
            alpha = int(self.drift_power * 200)
            s = pygame.Surface((30, 15))
            s.set_alpha(alpha)
            s.fill((100, 100, 100))
            screen.blit(s, (self.x - 25, self.y + 20))
            screen.blit(s, (self.x + 5, self.y + 20))
        
        # 加速特效
        if self.boost_power > 1.1:
            pygame.draw.rect(screen, YELLOW, 
                           (self.x - 5, self.y + self.height//2 - 5, 
                            10, 15), border_radius=5)

class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type
        self.collected = False
        self.anim = 0
    
    def update(self):
        self.anim += 0.1
    
    def draw(self):
        if self.collected:
            return
        
        colors = {
            "speed": YELLOW,
            "shield": BLUE,
            "banana": YELLOW
        }
        color = colors.get(self.type, ORANGE)
        
        y = self.y + int(math.sin(self.anim) * 5)
        pygame.draw.circle(screen, color, (self.x, y), 15)
        pygame.draw.circle(screen, WHITE, (self.x, y), 15, 3)

class KartGame:
    def __init__(self):
        self.player = Kart(WIDTH//2, HEIGHT//2, RED, True)
        self.ai_cars = [
            Kart(200, 200, BLUE),
            Kart(700, 500, GREEN),
            Kart(700, 200, PURPLE)
        ]
        self.items = []
        self.laps = 0
        self.score = 0
        self.position = 1
        self.phase = "menu"
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        self.track_points = []
        self.generate_track()
    
    def generate_track(self):
        self.track_points = [
            (100, 100), (700, 100), (800, 200), (800, 500), 
            (700, 600), (100, 600), (50, 500), (50, 200)
        ]
    
    def update(self):
        if self.phase != "game":
            return
        
        self.player.update()
        
        # AI简单行为
        for ai in self.ai_cars:
            ai.speed = min(ai.speed + 0.02, 4)
            # 简单路径跟随
            if ai.x < WIDTH//2:
                ai.angle += 0.5
            elif ai.x > WIDTH//2:
                ai.angle -= 0.5
            if ai.y < HEIGHT//2:
                ai.angle -= 0.3
            elif ai.y > HEIGHT//2:
                ai.angle += 0.3
            
            ai.update()
        
        # 生成道具
        if random.random() < 0.01 and len(self.items) < 8:
            t = random.choice(["speed", "shield", "banana"])
            self.items.append(Item(random.randint(100, WIDTH-100), 
                                 random.randint(100, HEIGHT-100), t))
        
        for item in self.items:
            item.update()
        
        # 碰撞检测
        for item in self.items:
            if not item.collected:
                dx = self.player.x - item.x
                dy = self.player.y - item.y
                if dx*dx + dy*dy < 40*40:
                    item.collected = True
                    if item.type == "speed":
                        self.player.boost_power = 2.0
                    self.score += 5
    
    def draw(self):
        screen.fill(GREEN)
        
        # 赛道
        pygame.draw.polygon(screen, DARK_GRAY, self.track_points)
        pygame.draw.polygon(screen, GRAY, self.track_points, 5)
        
        if self.phase == "menu":
            self.draw_menu()
        elif self.phase == "game":
            self.draw_game()
        
        pygame.display.flip()
    
    def draw_menu(self):
        title = self.font_large.render("卡丁车赛道", True, PINK)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        
        instructions = [
            "↑ 加速",
            "↓ 减速",
            "← → 转向",
            "Shift 漂移",
            "",
            "按 空格键 开始!"
        ]
        
        y = 200
        for line in instructions:
            text = self.font_medium.render(line, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 40
        
        # 示例卡丁车
        kart = Kart(WIDTH//2, 500, RED)
        kart.draw()
    
    def draw_game(self):
        # 道具
        for item in self.items:
            item.draw()
        
        # AI车
        for ai in self.ai_cars:
            ai.draw()
        
        # 玩家
        self.player.draw()
        
        # HUD
        pygame.draw.rect(screen, (0, 0, 0, 128), (10, 10, 180, 90), border_radius=10)
        
        score_text = self.font_medium.render(f"分数: {self.score}", True, YELLOW)
        pos_text = self.font_small.render(f"位置: {self.position}/4", True, WHITE)
        boost_text = self.font_small.render(f"加速: {int(self.player.boost_power*100)}%", True, 
                                             ORANGE if self.player.boost_power > 1.2 else WHITE)
        
        screen.blit(score_text, (20, 15))
        screen.blit(pos_text, (20, 45))
        screen.blit(boost_text, (20, 70))
    
    def handle_key(self, key):
        if self.phase == "menu":
            if key == pygame.K_SPACE:
                self.phase = "game"
        elif self.phase == "game":
            if key == pygame.K_SPACE and self.player.item:
                self.player.item = None

def main():
    game = KartGame()
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
