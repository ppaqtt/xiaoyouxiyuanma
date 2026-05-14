"""
狙击精英简化版
狙击射击游戏
"""

import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("狙击精英")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (50, 50, 50)
RED = (200, 50, 50)
GREEN = (0, 180, 100)
BLUE = (0, 100, 200)
BROWN = (139, 69, 19)

class Target:
    def __init__(self):
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(100, HEIGHT - 150)
        self.radius = 30
        self.move_dir = random.choice([-1, 1])
        self.speed = random.uniform(0.5, 1.5)
    
    def update(self):
        self.x += self.speed * self.move_dir
        if self.x < 80 or self.x > WIDTH - 80:
            self.move_dir *= -1
    
    def draw(self):
        pygame.draw.circle(screen, RED, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius - 8)
        pygame.draw.circle(screen, RED, (self.x, self.y), self.radius - 16)
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius - 24)

class SniperGame:
    def __init__(self):
        self.phase = "menu"
        self.targets = []
        self.score = 0
        self.time = 60
        self.breath = 0
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 26)
        self.start_time = 0
        self.mouse_pos = (WIDTH//2, HEIGHT//2)
    
    def reset(self):
        self.targets = []
        self.score = 0
        self.time = 60
        self.phase = "game"
        self.start_time = pygame.time.get_ticks()
    
    def draw(self):
        screen.fill((100, 150, 100))
        
        # 背景
        pygame.draw.rect(screen, (80, 120, 80), (0, HEIGHT - 100, WIDTH, 100))
        for x in range(0, WIDTH, 50):
            pygame.draw.circle(screen, (50, 100, 50), (x, HEIGHT - 90), 20)
        
        if self.phase == "menu":
            self.draw_menu()
        elif self.phase in ["game", "gameover"]:
            self.draw_game()
        
        pygame.display.flip()
    
    def draw_menu(self):
        title = self.font_large.render("🎯 狙击精英", True, RED)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        
        instructions = [
            "移动鼠标瞄准",
            "点击射击!",
            "射击红心得分",
            "时间限制60秒",
            "",
            "按 空格键 开始!"
        ]
        
        y = 240
        for line in instructions:
            text = self.font_medium.render(line, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 40
    
    def draw_game(self):
        # 目标
        for t in self.targets:
            t.draw()
        
        # 准星
        mx, my = pygame.mouse.get_pos()
        pygame.draw.circle(screen, (255, 0, 0, 100), (mx, my), 40, 2)
        pygame.draw.line(screen, RED, (mx - 50, my), (mx - 10, my), 2)
        pygame.draw.line(screen, RED, (mx + 10, my), (mx + 50, my), 2)
        pygame.draw.line(screen, RED, (mx, my - 50), (mx, my - 10), 2)
        pygame.draw.line(screen, RED, (mx, my + 10), (mx, my + 50), 2)
        
        # HUD
        pygame.draw.rect(screen, (0, 0, 0, 150), (0, 0, WIDTH, 60))
        
        score_text = self.font_large.render(f"分数: {self.score}", True, GREEN)
        screen.blit(score_text, (30, 10))
        
        if self.phase == "game":
            elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
            remaining = max(0, 60 - elapsed)
        else:
            remaining = 0
        
        time_text = self.font_large.render(f"时间: {remaining}", True, RED if remaining < 10 else WHITE)
        screen.blit(time_text, (WIDTH - 200, 10))
        
        if self.phase == "gameover":
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            title = self.font_large.render("时间到!", True, RED)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
            
            final = self.font_medium.render(f"最终分数: {self.score}", True, WHITE)
            screen.blit(final, (WIDTH//2 - final.get_width()//2, 300))
            
            restart = self.font_medium.render("按 R 再来一局", True, GREEN)
            screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 400))
    
    def update(self):
        if self.phase != "game":
            return
        
        elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
        if elapsed >= 60:
            self.phase = "gameover"
            return
        
        while len(self.targets) < 3 + min(5, self.score // 50):
            self.targets.append(Target())
        
        for t in self.targets:
            t.update()
    
    def handle_click(self, pos):
        if self.phase != "game":
            return
        
        mx, my = pos
        
        hit = False
        for i, t in enumerate(self.targets):
            dx = mx - t.x
            dy = my - t.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < t.radius:
                hit = True
                self.targets.pop(i)
                if dist < t.radius / 2:
                    self.score += 15
                else:
                    self.score += 10
                break
        
        if not hit:
            self.score = max(0, self.score - 2)
    
    def handle_key(self, key):
        if self.phase == "menu":
            if key == pygame.K_SPACE:
                self.reset()
        elif self.phase == "gameover":
            if key == pygame.K_r:
                self.reset()

def main():
    game = SniperGame()
    pygame.mouse.set_visible(False)
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)
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
