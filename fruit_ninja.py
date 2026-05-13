import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 800

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (255, 0, 0),    # 苹果 - 红
    (255, 165, 0),  # 橙子 - 橙
    (255, 255, 0),  # 柠檬 - 黄
    (0, 255, 0),    # 青苹果 - 绿
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("水果忍者")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)

class Fruit:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = HEIGHT + 50
        self.radius = 30
        self.color = random.choice(COLORS)
        self.dx = random.uniform(-3, 3)
        self.dy = random.uniform(-20, -15)
        self.gravity = 0.5
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
    
    def move(self):
        self.dy += self.gravity
        self.x += self.dx
        self.y += self.dy
        self.rotation += self.rotation_speed
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x - 10), int(self.y - 10)), 8)

def fruit_ninja():
    fruits = []
    score = 0
    missed = 0
    game_over = False
    trail = []
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                trail.append((mouse_x, mouse_y, WHITE))
                if len(trail) > 10:
                    trail.pop(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                for fruit in fruits[:]:
                    distance = ((mouse_x - fruit.x)**2 + (mouse_y - fruit.y)**2)**0.5
                    if distance < fruit.radius + 20:
                        fruits.remove(fruit)
                        score += 10
        
        if random.randint(1, 30) == 1:
            fruits.append(Fruit())
        
        fruits = [f for f in fruits if f.y < HEIGHT + 50]
        for fruit in fruits:
            fruit.move()
            if fruit.y > HEIGHT - 50 and fruit not in [f for f in fruits if hasattr(f, 'missed')]:
                fruit.missed = True
                missed += 1
                if missed >= 10:
                    game_over = True
        
        fruits = [f for f in fruits if not (hasattr(f, 'missed') and f.y > HEIGHT)]
        
        for i, (x, y, color) in enumerate(trail):
            alpha = int(255 * (i / len(trail)))
            pygame.draw.circle(screen, color, (x, y), 5)
        
        for fruit in fruits:
            fruit.draw()
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        missed_text = font.render(f"漏掉: {missed}/10", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(missed_text, (WIDTH - 120, 10))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    game_over_text = font.render(f"游戏结束! 得分: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(2000)
    pygame.quit()

if __name__ == "__main__":
    fruit_ninja()