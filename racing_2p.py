import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("赛车大战")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)

class Car:
    def __init__(self, x, color, controls):
        self.x = x
        self.y = HEIGHT - 100
        self.width = 50
        self.height = 80
        self.color = color
        self.speed = 5
        self.controls = controls
    
    def move(self, keys):
        if keys[self.controls['left']] and self.x > 50:
            self.x -= self.speed
        if keys[self.controls['right']] and self.x < WIDTH - 100:
            self.x += self.speed
        if keys[self.controls['up']] and self.y > 0:
            self.y -= self.speed
        if keys[self.controls['down']] and self.y < HEIGHT - self.height:
            self.y += self.speed
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=10)

class Obstacle:
    def __init__(self, x):
        self.width = 50
        self.height = 80
        self.x = x
        self.y = -self.height
        self.speed = 5
    
    def move(self):
        self.y += self.speed
    
    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height), border_radius=10)

def racing_2p():
    car1 = Car(150, GREEN, {'left': pygame.K_a, 'right': pygame.K_d, 'up': pygame.K_w, 'down': pygame.K_s})
    car2 = Car(WIDTH - 200, BLUE, {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'up': pygame.K_UP, 'down': pygame.K_DOWN})
    
    obstacles = []
    score = 0
    game_over = False
    
    while not game_over:
        screen.fill(GRAY)
        
        for i in range(-1, HEIGHT // 100 + 2):
            pygame.draw.rect(screen, WHITE, (WIDTH//2 - 5, i*100, 10, 50))
        
        pygame.draw.rect(screen, BLACK, (0, 0, 50, HEIGHT))
        pygame.draw.rect(screen, BLACK, (WIDTH - 50, 0, 50, HEIGHT))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        keys = pygame.key.get_pressed()
        car1.move(keys)
        car2.move(keys)
        
        if random.randint(1, 40) == 1:
            obstacles.append(Obstacle(random.randint(60, WIDTH - 150)))
        
        obstacles = [o for o in obstacles if o.y < HEIGHT]
        for obstacle in obstacles:
            obstacle.move()
            obstacle.draw()
        
        car1.draw()
        car2.draw()
        
        for obstacle in obstacles:
            for car in [car1, car2]:
                if (car.x < obstacle.x + obstacle.width and
                    car.x + car.width > obstacle.x and
                    car.y < obstacle.y + obstacle.height and
                    car.y + car.height > obstacle.y):
                    game_over = True
        
        score += 1
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        controls_text = font.render("绿队: WASD | 蓝队: 方向键", True, WHITE)
        screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT - 30))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    game_over_text = font.render(f"游戏结束! 得分: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    racing_2p()