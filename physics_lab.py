"""
物理实验室
简单的物理模拟
"""

import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("物理实验室")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
BLUE = (0, 100, 200)
RED = (200, 50, 50)
GREEN = (0, 180, 100)
PURPLE = (150, 50, 200)

class Ball:
    def __init__(self, x, y, vx=0, vy=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 20
        self.color = RED
    
    def update(self):
        self.vy += 0.5
        self.x += self.vx
        self.y += self.vy
        
        if self.x < self.radius:
            self.x = self.radius
            self.vx *= -0.8
        if self.x > WIDTH - self.radius:
            self.x = WIDTH - self.radius
            self.vx *= -0.8
        
        if self.y > HEIGHT - 80 - self.radius:
            self.y = HEIGHT - 80 - self.radius
            self.vy *= -0.7
            self.vx *= 0.95
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x - 5), int(self.y - 5)), 5)

class PhysicsLab:
    def __init__(self):
        self.balls = []
        self.grabbing = False
        self.grab_pos = None
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
    
    def draw(self):
        screen.fill((230, 240, 255))
        
        # 地面
        pygame.draw.rect(screen, (100, 80, 60), (0, HEIGHT - 80, WIDTH, 80))
        pygame.draw.rect(screen, (50, 150, 50), (0, HEIGHT - 85, WIDTH, 10))
        
        # 球
        for ball in self.balls:
            ball.draw()
        
        # UI
        pygame.draw.rect(screen, (0, 0, 0, 100), (0, 0, WIDTH, 60))
        help_text = [
            "点击添加球 | 拖动抛掷",
            f"球数: {len(self.balls)}"
        ]
        
        for i, text in enumerate(help_text):
            t = self.font_medium.render(text, True, WHITE)
            screen.blit(t, (20, 15 + i * 25))
        
        # 重置按钮
        reset_btn = pygame.Rect(WIDTH - 150, 10, 130, 40)
        pygame.draw.rect(screen, RED, reset_btn, border_radius=8)
        rt = self.font_medium.render("重置", True, WHITE)
        screen.blit(rt, (WIDTH - 115, 15))
        
        pygame.display.flip()
    
    def update(self):
        for ball in self.balls:
            ball.update()
    
    def handle_click(self, pos, event_type):
        if event_type == pygame.MOUSEBUTTONDOWN:
            reset_btn = pygame.Rect(WIDTH - 150, 10, 130, 40)
            if reset_btn.collidepoint(pos):
                self.balls = []
            else:
                self.grabbing = True
                self.grab_pos = pos
        elif event_type == pygame.MOUSEBUTTONUP and self.grabbing:
            if self.grab_pos:
                dx = pos[0] - self.grab_pos[0]
                dy = pos[1] - self.grab_pos[1]
                self.balls.append(Ball(self.grab_pos[0], self.grab_pos[1], 
                                      dx / 10, dy / 10))
            self.grabbing = False
            self.grab_pos = None

def main():
    lab = PhysicsLab()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
                lab.handle_click(event.pos, event.type)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    lab.balls.append(Ball(WIDTH//2, 100, 
                                         (pygame.time.get_ticks() % 100 - 50) / 10, 0))
        
        lab.update()
        lab.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
