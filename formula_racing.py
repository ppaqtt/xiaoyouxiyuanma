import pygame
import os
import sys
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
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("方程式赛车")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (0, 100, 255)
YELLOW = (255, 200, 50)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)

class FormulaRacing:
    def __init__(self):
        self.player_x = 400
        self.player_y = 500
        self.player_speed = 5
        self.opponents = []
        self.lap = 0
        self.score = 0
        self.nitro = 100
        self.nitro_active = False
        self.font = get_chinese_font(36)
        self.large_font = get_chinese_font(48)
        self.game_over = False
        self.road_offset = 0
        
        for _ in range(4):
            self.opponents.append({
                'x': random.choice([200, 300, 400, 500, 600]),
                'y': random.randint(-200, -50),
                'speed': random.uniform(2, 4),
                'color': random.choice([RED, GREEN, BLUE, YELLOW])
            })

    def draw(self):
        screen.fill((0, 100, 0))
        
        if not self.game_over:
            self.update()
        
        self.draw_track()
        self.draw_player()
        self.draw_opponents()
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()

    def draw_track(self):
        pygame.draw.rect(screen, DARK_GRAY, (150, 0, 500, HEIGHT))
        pygame.draw.rect(screen, WHITE, (150, 0, 5, HEIGHT))
        pygame.draw.rect(screen, WHITE, (645, 0, 5, HEIGHT))
        
        for i in range(20):
            y = (i * 40 + self.road_offset) % HEIGHT
            pygame.draw.rect(screen, WHITE, (395, y, 10, 20))

    def draw_player(self):
        color = YELLOW if self.nitro_active else BLUE
        pygame.draw.rect(screen, color, (self.player_x - 15, self.player_y - 25, 30, 50), border_radius=5)
        pygame.draw.rect(screen, (0, 50, 100), (self.player_x - 10, self.player_y - 15, 20, 30))
        
        if self.nitro_active:
            pygame.draw.rect(screen, YELLOW, (self.player_x - 8, self.player_y + 25, 16, 10))

    def draw_opponents(self):
        for opp in self.opponents:
            pygame.draw.rect(screen, opp['color'], (opp['x'] - 15, opp['y'] - 25, 30, 50), border_radius=5)
            pygame.draw.rect(screen, (50, 50, 50), (opp['x'] - 10, opp['y'] - 15, 20, 30))

    def draw_hud(self):
        lap_text = self.font.render(f"圈数: {self.lap}", True, WHITE)
        screen.blit(lap_text, (20, 20))
        
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 60))
        
        nitro_text = self.font.render(f"氮气: {int(self.nitro)}%", True, YELLOW)
        screen.blit(nitro_text, (20, 100))
        
        pygame.draw.rect(screen, GRAY, (20, 130, 150, 20))
        pygame.draw.rect(screen, YELLOW, (20, 130, self.nitro * 1.5, 20))

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        text = self.large_font.render("游戏结束!", True, RED)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
        
        score_text = self.font.render(f"最终分数: {self.score}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 280))
        
        restart_text = self.font.render("按 R 重新开始", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 360))

    def update(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] and self.player_x > 170:
            self.player_x -= 6
        if keys[pygame.K_RIGHT] and self.player_x < 630:
            self.player_x += 6
        
        if keys[pygame.K_SPACE] and self.nitro > 0:
            self.nitro_active = True
            self.nitro -= 0.5
            self.road_offset += 15
        else:
            self.nitro_active = False
        
        if not self.nitro_active and self.nitro < 100:
            self.nitro += 0.1
        
        self.road_offset += 8
        
        for opp in self.opponents:
            opp['y'] += self.player_speed - opp['speed']
            if opp['y'] > HEIGHT + 50:
                opp['y'] = random.randint(-300, -100)
                opp['x'] = random.choice([200, 300, 400, 500, 600])
                self.score += 10
                self.lap += 0.25
            
            if self.check_collision(self.player_x, self.player_y, opp['x'], opp['y']):
                self.game_over = True

    def check_collision(self, x1, y1, x2, y2):
        return abs(x1 - x2) < 30 and abs(y1 - y2) < 50

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.__init__()

game = FormulaRacing()
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.handle_input(event)
    
    game.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
