import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("方程式赛车")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 255)

class FormulaRacing:
    def __init__(self):
        self.car_x = WIDTH // 2
        self.car_y = HEIGHT - 100
        self.speed = 5
        self.acceleration = 0.2
        self.max_speed = 15
        self.lap_time = 0
        self.best_time = 999
        self.font = pygame.font.Font(None, 32)
        self.clock = pygame.time.Clock()
        self.last_time = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_time >= 1000:
            self.lap_time += 1
            self.last_time = now

    def draw(self):
        screen.fill(GREEN)
        
        pygame.draw.rect(screen, WHITE, (100, 0, 20, HEIGHT))
        pygame.draw.rect(screen, WHITE, (680, 0, 20, HEIGHT))
        
        pygame.draw.rect(screen, YELLOW, (120, 0, 20, HEIGHT))
        pygame.draw.rect(screen, YELLOW, (660, 0, 20, HEIGHT))
        
        pygame.draw.rect(screen, RED, (self.car_x - 20, self.car_y - 30, 40, 60))
        pygame.draw.circle(screen, BLACK, (self.car_x - 12, self.car_y + 25), 8)
        pygame.draw.circle(screen, BLACK, (self.car_x + 12, self.car_y + 25), 8)
        pygame.draw.circle(screen, BLACK, (self.car_x - 12, self.car_y - 25), 6)
        pygame.draw.circle(screen, BLACK, (self.car_x + 12, self.car_y - 25), 6)
        
        speed_text = self.font.render(f"速度: {int(self.speed)}", True, BLACK)
        screen.blit(speed_text, (50, 50))
        
        lap_text = self.font.render(f"圈时间: {self.lap_time}s", True, BLACK)
        screen.blit(lap_text, (50, 80))
        
        best_text = self.font.render(f"最佳: {self.best_time}s", True, BLACK)
        screen.blit(best_text, (50, 110))

    def handle_input(self, event):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] and self.car_x > 120:
            self.car_x -= 5
        if keys[pygame.K_RIGHT] and self.car_x < 660:
            self.car_x += 5
        if keys[pygame.K_UP] and self.speed < self.max_speed:
            self.speed += self.acceleration
        if keys[pygame.K_DOWN] and self.speed > 0:
            self.speed -= self.acceleration * 2
        
        if self.car_y <= 50:
            self.car_y = HEIGHT - 100
            if self.lap_time < self.best_time:
                self.best_time = self.lap_time
            self.lap_time = 0
        
        self.car_y -= self.speed

game = FormulaRacing()
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