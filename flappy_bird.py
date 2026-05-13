import pygame
import random

pygame.init()

WIDTH, HEIGHT = 400, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
SKY_BLUE = (135, 206, 235)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("飞翔的小鸟")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)

class Bird:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT // 2
        self.radius = 15
        self.velocity = 0
        self.gravity = 0.5
    
    def jump(self):
        self.velocity = -8
    
    def move(self):
        self.velocity += self.gravity
        self.y += self.velocity
    
    def draw(self):
        pygame.draw.circle(screen, (255, 255, 0), (self.x, int(self.y)), self.radius)

class Pipe:
    def __init__(self):
        self.x = WIDTH
        self.width = 60
        self.gap = 150
        self.top_height = random.randint(50, HEIGHT - 150 - self.gap)
        self.bottom_y = self.top_height + self.gap
        self.speed = 5
    
    def move(self):
        self.x -= self.speed
    
    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, self.top_height))
        pygame.draw.rect(screen, GREEN, (self.x, self.bottom_y, self.width, HEIGHT - self.bottom_y))

def flappy_bird():
    bird = Bird()
    pipes = []
    score = 0
    game_over = False
    
    while not game_over:
        screen.fill(SKY_BLUE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                bird.jump()
        
        bird.move()
        
        if bird.y > HEIGHT - bird.radius or bird.y < bird.radius:
            game_over = True
        
        if random.randint(1, 60) == 1 or not pipes:
            pipes.append(Pipe())
        
        pipes = [p for p in pipes if p.x > -p.width]
        for pipe in pipes:
            pipe.move()
            
            if bird.x + bird.radius > pipe.x and bird.x - bird.radius < pipe.x + pipe.width:
                if bird.y - bird.radius < pipe.top_height or bird.y + bird.radius > pipe.bottom_y:
                    game_over = True
            
            if pipe.x + pipe.width == bird.x and not hasattr(pipe, 'scored'):
                pipe.scored = True
                score += 1
        
        bird.draw()
        for pipe in pipes:
            pipe.draw()
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    game_over_text = font.render(f"游戏结束! 得分: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(2000)
    pygame.quit()

if __name__ == "__main__":
    flappy_bird()