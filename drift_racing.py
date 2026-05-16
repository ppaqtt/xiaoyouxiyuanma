import pygame
import sys
import math
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("漂移大师")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (0, 100, 255)
YELLOW = (255, 200, 50)
GRAY = (100, 100, 100)
ORANGE = (255, 140, 0)
DARK_GRAY = (40, 40, 40)

class DriftRacing:
    def __init__(self):
        self.player_x = 400
        self.player_y = 300
        self.player_angle = 0
        self.player_speed = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.drift_score = 0
        self.total_score = 0
        self.drift_active = False
        self.drift_angle = 0
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 48)
        self.cones = self.generate_cones()
        self.skid_marks = []
        self.game_over = False

    def generate_cones(self):
        cones = []
        for i in range(10):
            angle = i * (2 * math.pi / 10)
            radius = 200
            x = WIDTH // 2 + math.cos(angle) * radius
            y = HEIGHT // 2 + math.sin(angle) * radius
            cones.append((x, y))
        return cones

    def draw(self):
        screen.fill(DARK_GRAY)
        
        if not self.game_over:
            self.update()
        
        self.draw_track()
        self.draw_skid_marks()
        self.draw_cones()
        self.draw_player()
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()

    def draw_track(self):
        pygame.draw.circle(screen, (60, 60, 60), (WIDTH//2, HEIGHT//2), 250)
        pygame.draw.circle(screen, DARK_GRAY, (WIDTH//2, HEIGHT//2), 150)
        
        pygame.draw.circle(screen, WHITE, (WIDTH//2, HEIGHT//2), 250, 2)
        pygame.draw.circle(screen, WHITE, (WIDTH//2, HEIGHT//2), 150, 2)

    def draw_cones(self):
        for i, (x, y) in enumerate(self.cones):
            passed = i < int(self.total_score / 100) % len(self.cones)
            color = GREEN if passed else ORANGE
            pygame.draw.circle(screen, color, (int(x), int(y)), 12)
            pygame.draw.circle(screen, WHITE, (int(x), int(y)), 8)

    def draw_skid_marks(self):
        for mark in self.skid_marks:
            pygame.draw.circle(screen, (30, 30, 30), (int(mark[0]), int(mark[1])), 3)

    def draw_player(self):
        car_surface = pygame.Surface((40, 20), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, RED, (0, 0, 40, 20), border_radius=3)
        pygame.draw.rect(car_surface, (100, 0, 0), (5, 5, 15, 10))
        
        rotated_surface = pygame.transform.rotate(car_surface, -self.player_angle)
        rect = rotated_surface.get_rect(center=(self.player_x, self.player_y))
        screen.blit(rotated_surface, rect)
        
        if self.drift_active:
            pygame.draw.circle(screen, (100, 100, 100), (int(self.player_x - 15 * math.cos(math.radians(self.player_angle))), 
                                                            int(self.player_y - 15 * math.sin(math.radians(self.player_angle)))), 8)
            pygame.draw.circle(screen, (100, 100, 100), (int(self.player_x + 15 * math.cos(math.radians(self.player_angle))), 
                                                            int(self.player_y + 15 * math.sin(math.radians(self.player_angle)))), 8)

    def draw_hud(self):
        if self.drift_active:
            drift_text = self.large_font.render(f"漂移! +{int(self.drift_score)}", True, YELLOW)
            screen.blit(drift_text, (WIDTH//2 - drift_text.get_width()//2, 50))
        
        score_text = self.font.render(f"总分: {int(self.total_score)}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        speed_text = self.font.render(f"速度: {int(abs(self.player_speed))}", True, WHITE)
        screen.blit(speed_text, (20, 60))

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        text = self.large_font.render("游戏结束!", True, RED)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
        
        score_text = self.font.render(f"最终分数: {int(self.total_score)}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 280))
        
        restart_text = self.font.render("按 R 重新开始", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 360))

    def update(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP]:
            self.player_speed = min(self.player_speed + 0.3, 10)
        elif keys[pygame.K_DOWN]:
            self.player_speed = max(self.player_speed - 0.3, -5)
        else:
            self.player_speed *= 0.98
        
        steering = 0
        handbrake = keys[pygame.K_SPACE]
        
        if keys[pygame.K_LEFT]:
            steering = -3
        if keys[pygame.K_RIGHT]:
            steering = 3
        
        if handbrake and abs(self.player_speed) > 2:
            self.drift_active = True
            steering *= 2
        else:
            self.drift_active = False
        
        self.player_angle += steering * (abs(self.player_speed) / 5)
        
        self.velocity_x = math.cos(math.radians(self.player_angle)) * self.player_speed
        self.velocity_y = math.sin(math.radians(self.player_angle)) * self.player_speed
        
        self.player_x += self.velocity_x
        self.player_y += self.velocity_y
        
        if self.drift_active:
            self.drift_score += 0.5
            self.skid_marks.append((self.player_x, self.player_y))
            if len(self.skid_marks) > 200:
                self.skid_marks.pop(0)
        else:
            if self.drift_score > 10:
                self.total_score += self.drift_score
            self.drift_score = 0
        
        for i, (cone_x, cone_y) in enumerate(self.cones):
            dist = math.hypot(self.player_x - cone_x, self.player_y - cone_y)
            if dist < 30 and i == int(self.total_score / 100) % len(self.cones):
                self.total_score += 100
        
        dist_from_center = math.hypot(self.player_x - WIDTH//2, self.player_y - HEIGHT//2)
        if dist_from_center > 260 or dist_from_center < 140:
            self.game_over = True

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.__init__()

game = DriftRacing()
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
