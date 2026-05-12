import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("塔防游戏")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)

class Enemy:
    def __init__(self):
        self.path = [(0, HEIGHT//2), (WIDTH//4, HEIGHT//2), 
                   (WIDTH//4, HEIGHT//4), (WIDTH//2, HEIGHT//4),
                   (WIDTH//2, HEIGHT*3//4), (WIDTH*3//4, HEIGHT*3//4),
                   (WIDTH*3//4, HEIGHT//2), (WIDTH, HEIGHT//2)]
        self.path_index = 0
        self.x, self.y = self.path[0]
        self.radius = 15
        self.speed = 2
        self.health = 100
        self.max_health = 100
        self.color = RED
    
    def move(self):
        if self.path_index < len(self.path) - 1:
            target = self.path[self.path_index + 1]
            dx = target[0] - self.x
            dy = target[1] - self.y
            distance = (dx**2 + dy**2)**0.5
            
            if distance < self.speed:
                self.path_index += 1
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x - 20, self.y - 30, 40, 5))
        pygame.draw.rect(screen, GREEN, (self.x - 20, self.y - 30, 40 * health_ratio, 5))

class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 30
        self.range = 150
        self.damage = 20
        self.cooldown = 0
        self.cooldown_max = 30
    
    def update(self, enemies):
        if self.cooldown > 0:
            self.cooldown -= 1
        else:
            for enemy in enemies:
                distance = ((self.x - enemy.x)**2 + (self.y - enemy.y)**2)**0.5
                if distance <= self.range:
                    enemy.health -= self.damage
                    self.cooldown = self.cooldown_max
                    break
    
    def draw(self):
        pygame.draw.circle(screen, BLUE, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (200, 200, 255), (self.x, self.y), self.range, 1)

def tower_defense():
    enemies = []
    towers = []
    money = 100
    score = 0
    wave = 0
    game_over = False
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and money >= 50:
                    tower = Tower(event.pos[0], event.pos[1])
                    towers.append(tower)
                    money -= 50
        
        if random.randint(1, 120) == 1:
            enemies.append(Enemy())
            wave += 1
        
        for enemy in enemies[:]:
            enemy.move()
            enemy.draw()
            
            if enemy.health <= 0:
                enemies.remove(enemy)
                money += 10
                score += 100
            elif enemy.path_index >= len(enemy.path) - 1:
                enemies.remove(enemy)
                score = max(0, score - 50)
        
        for tower in towers:
            tower.update(enemies)
            tower.draw()
        
        pygame.draw.lines(screen, (100, 100, 100), False, 
                          [(0, HEIGHT//2), (WIDTH//4, HEIGHT//2), 
                           (WIDTH//4, HEIGHT//4), (WIDTH//2, HEIGHT//4),
                           (WIDTH//2, HEIGHT*3//4), (WIDTH*3//4, HEIGHT*3//4),
                           (WIDTH*3//4, HEIGHT//2), (WIDTH, HEIGHT//2)], 5)
        
        money_text = font.render(f"金币: {money}", True, YELLOW)
        score_text = font.render(f"得分: {score}", True, WHITE)
        wave_text = font.render(f"波数: {wave}", True, WHITE)
        
        screen.blit(money_text, (10, 10))
        screen.blit(score_text, (10, 50))
        screen.blit(wave_text, (10, 90))
        
        instruction_text = font.render("点击购买塔 (50金币)", True, WHITE)
        screen.blit(instruction_text, (WIDTH//2 - 100, HEIGHT - 30))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    result_text = font.render(f"游戏结束! 最终得分: {score}", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - 150, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    tower_defense()