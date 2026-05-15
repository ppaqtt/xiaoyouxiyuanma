import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("漂移赛车")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 200, 50)

class DriftRacing:
    def __init__(self):
        self.car_x = WIDTH // 2
        self.car_y = HEIGHT - 100
        self.speed = 5
        self.drift_angle = 0
        self.score = 0
        self.drift_points = 0
        self.font = pygame.font.Font(None, 32)
        self.clock = pygame.time.Clock()

    def update(self):
        self.car_y -= self.speed
        
        if self.car_y <= -50:
            self.car_y = HEIGHT
        
        if self.drift_angle != 0:
            self.drift_points += 1
            if self.drift_points % 10 == 0:
                self.score += 1

    def draw(self):
        screen.fill(GRAY)
        
        for i in range(0, HEIGHT, 50):
            pygame.draw.rect(screen, YELLOW, (350, i, 100, 25))
        
        rotated_car = pygame.Surface((50, 70), pygame.SRCALPHA)
        pygame.draw.rect(rotated_car, BLUE, (0, 0, 50, 70), border_radius=10)
        
        rotated = pygame.transform.rotate(rotated_car, self.drift_angle)
        rect = rotated.get_rect(center=(self.car_x, self.car_y))
        screen.blit(rotated, rect)
        
        speed_text = self.font.render(f"速度: {int(self.speed)}", True, WHITE)
        screen.blit(speed_text, (50, 50))
        
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (50, 80))
        
        drift_text = self.font.render(f"漂移: {'是' if self.drift_angle != 0 else '否'}", True, YELLOW)
        screen.blit(drift_text, (50, 110))

    def handle_input(self, event):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.car_x -= 4 + self.drift_angle * 0.1
            if self.speed > 8:
                self.drift_angle = -30
        elif keys[pygame.K_RIGHT]:
            self.car_x += 4 - self.drift_angle * 0.1
            if self.speed > 8:
                self.drift_angle = 30
        else:
            self.drift_angle = 0
        
        if keys[pygame.K_UP] and self.speed < 15:
            self.speed += 0.3
        if keys[pygame.K_DOWN] and self.speed > 0:
            self.speed -= 0.5
        
        self.car_x = max(100, min(700, self.car_x))

game = DriftRacing()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    game.handle_input(event)
    game.update()
    game.draw()
    pygame.display.flip()
    game.clock.tick(60)

pygame.quit()