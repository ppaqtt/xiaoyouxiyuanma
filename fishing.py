import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 200)
GOLD = (255, 215, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("捕鱼达人")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)
big_font = pygame.font.Font(None, 60)

class Fish:
    def __init__(self):
        self.x = random.choice([-50, WIDTH + 50])
        self.y = random.randint(50, HEIGHT - 50)
        self.size = random.randint(15, 40)
        self.speed = random.uniform(1, 3)
        self.direction = 1 if self.x < 0 else -1
        self.points = int(self.size * 2)
    
    def move(self):
        self.x += self.speed * self.direction
        self.y += math.sin(self.x * 0.02) * 0.5
    
    def draw(self):
        color = random.choice([BLUE, GREEN, GOLD, RED, (255, 165, 0)])
        pygame.draw.ellipse(screen, color, 
            (self.x - self.size, self.y - self.size//2, self.size*2, self.size))
        
        tail_x = self.x + self.size * 2 * self.direction
        points = [(tail_x, self.y),
                  (tail_x + 20 * self.direction, self.y - 15),
                  (tail_x + 20 * self.direction, self.y + 15)]
        pygame.draw.polygon(screen, color, points)

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 15
    
    def move(self):
        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y += self.speed * math.sin(rad)
    
    def draw(self):
        pygame.draw.circle(screen, GOLD, (int(self.x), int(self.y)), 5)

def fishing_game():
    score = 0
    bullets = []
    fishes = []
    time_left = 60
    game_over = False
    start_ticks = pygame.time.get_ticks()
    
    while not game_over:
        screen.fill(BLUE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                cannon_x, cannon_y = WIDTH // 2, HEIGHT - 30
                angle = math.degrees(math.atan2(cannon_y - mouse_y, mouse_x - cannon_x))
                bullets.append(Bullet(cannon_x, cannon_y, angle))
        
        if random.randint(1, 30) == 1:
            fishes.append(Fish())
        
        for bullet in bullets[:]:
            bullet.move()
            bullet.draw()
            if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
                bullets.remove(bullet)
        
        for fish in fishes[:]:
            fish.move()
            fish.draw()
            
            if fish.x < -100 or fish.x > WIDTH + 100:
                fishes.remove(fish)
                continue
            
            for bullet in bullets[:]:
                distance = math.sqrt((fish.x - bullet.x)**2 + (fish.y - bullet.y)**2)
                if distance < fish.size:
                    score += fish.points
                    fishes.remove(fish)
                    bullets.remove(bullet)
                    break
        
        cannon_x, cannon_y = WIDTH // 2, HEIGHT - 30
        pygame.draw.rect(screen, GREEN, (cannon_x - 20, cannon_y, 40, 30))
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = math.degrees(math.atan2(cannon_y - mouse_y, mouse_x - cannon_x))
        pygame.draw.line(screen, WHITE, (cannon_x, cannon_y), 
                        (cannon_x + 50 * math.cos(math.radians(angle)),
                         cannon_y - 50 * math.sin(math.radians(angle))), 3)
        
        seconds = max(0, time_left - (pygame.time.get_ticks() - start_ticks) // 1000)
        if seconds == 0:
            game_over = True
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        time_text = font.render(f"时间: {seconds}秒", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (WIDTH - 120, 10))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    game_over_text = big_font.render(f"游戏结束! 得分: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    fishing_game()