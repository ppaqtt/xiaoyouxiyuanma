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
pygame.display.set_caption("街头滑板")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 200)
ORANGE = (255, 165, 0)
PURPLE = (138, 43, 226)

class SkateboardGame:
    def __init__(self):
        self.player_x = 400
        self.player_y = 300
        self.velocity_x = 0
        self.velocity_y = 0
        self.rotation = 0
        self.score = 0
        self.combo = 0
        self.tricks = []
        self.ramps = []
        self.grinds = []
        self.particles = []
        self.game_over = False
        self.font = get_chinese_font(36)
        self.large_font = get_chinese_font(48)
        
        for i in range(5):
            self.ramps.append({
                'x': 100 + i * 180,
                'y': 450 + random.randint(-50, 50),
                'width': 120,
                'height': 40
            })
    
    def draw(self):
        screen.fill((135, 206, 235))
        
        pygame.draw.rect(screen, (139, 90, 43), (0, 500, WIDTH, 100))
        pygame.draw.line(screen, WHITE, (0, 500), (WIDTH, 500), 3)
        
        for ramp in self.ramps:
            pygame.draw.polygon(screen, (100, 100, 100), [
                (ramp['x'], ramp['y'] + ramp['height']),
                (ramp['x'] + ramp['width'], ramp['y'] + ramp['height']),
                (ramp['x'] + ramp['width']//2, ramp['y'])
            ])
        
        pygame.draw.rect(screen, RED, (int(self.player_x) - 25, int(self.player_y) + 15, 50, 8))
        
        board_surface = pygame.Surface((60, 15), pygame.SRCALPHA)
        pygame.draw.rect(board_surface, (139, 69, 19), (0, 0, 60, 12), border_radius=3)
        rotated_board = pygame.transform.rotate(board_surface, self.rotation)
        rect = rotated_board.get_rect(center=(self.player_x, self.player_y))
        screen.blit(rotated_board, rect)
        
        for p in self.particles:
            pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), int(p['size']))
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
    
    def draw_hud(self):
        pygame.draw.rect(screen, (0, 0, 0, 128), (10, 10, 180, 100), border_radius=10)
        
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        combo_text = self.font.render(f"连击: {self.combo}x", True, ORANGE)
        screen.blit(combo_text, (20, 50))
        
        trick_text = self.font.render(f"动作: {len(self.tricks)}", True, GREEN)
        screen.blit(trick_text, (20, 80))
    
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        text = self.large_font.render("撞到障碍物!", True, RED)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
        
        score_text = self.font.render(f"最终分数: {self.score}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 280))
        
        restart_text = self.font.render("按 R 重新开始", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 350))
    
    def update(self):
        if self.game_over:
            return
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.velocity_x -= 0.5
        if keys[pygame.K_RIGHT]:
            self.velocity_x += 0.5
        
        if keys[pygame.K_SPACE] and self.player_y > 200:
            self.velocity_y = -15
            self.tricks.append('Ollie')
            self.combo += 1
            self.score += 10 * self.combo
        
        if keys[pygame.K_UP]:
            self.rotation = (self.rotation + 10) % 360
            if self.rotation % 90 == 0:
                self.tricks.append('Kickflip')
                self.combo += 1
                self.score += 20 * self.combo
        
        if keys[pygame.K_DOWN]:
            self.rotation = (self.rotation - 10) % 360
            if self.rotation % 90 == 0:
                self.tricks.append('Heelflip')
                self.combo += 1
                self.score += 20 * self.combo
        
        self.velocity_x *= 0.98
        self.velocity_y += 0.8
        
        self.player_x += self.velocity_x
        self.player_y += self.velocity_y
        
        self.player_x = max(30, min(WIDTH - 30, self.player_x))
        
        if self.player_y > 450:
            self.player_y = 450
            self.velocity_y = 0
            if abs(self.velocity_x) > 1:
                for _ in range(3):
                    self.particles.append({
                        'x': self.player_x + random.randint(-20, 20),
                        'y': self.player_y + 20,
                        'vx': random.uniform(-2, 2),
                        'vy': random.uniform(-3, 0),
                        'size': random.uniform(2, 4),
                        'color': (200, 200, 200)
                    })
        
        if abs(self.velocity_x) < 0.1:
            self.combo = 0
        
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1
            p['size'] *= 0.95
        
        self.particles = [p for p in self.particles if p['size'] > 0.5]
        
        if self.player_y < 100:
            self.game_over = True
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.__init__()

game = SkateboardGame()
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.handle_input(event)
    
    game.update()
    game.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
