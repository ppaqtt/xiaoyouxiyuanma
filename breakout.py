import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255)]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("打砖块游戏")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)

class Ball:
    def __init__(self):
        self.radius = 10
        self.x = WIDTH // 2
        self.y = HEIGHT - 50
        self.dx = 5 * random.choice([-1, 1])
        self.dy = -5
    
    def move(self):
        self.x += self.dx
        self.y += self.dy
        
        if self.x <= self.radius or self.x >= WIDTH - self.radius:
            self.dx *= -1
        if self.y <= self.radius:
            self.dy *= -1
    
    def draw(self):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius)

class Paddle:
    def __init__(self):
        self.width = 100
        self.height = 15
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 30
        self.speed = 8
    
    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        elif direction == "right" and self.x < WIDTH - self.width:
            self.x += self.speed
    
    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))

class Brick:
    def __init__(self, x, y, color):
        self.width = 70
        self.height = 25
        self.x = x
        self.y = y
        self.color = color
        self.visible = True
    
    def draw(self):
        if self.visible:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

def create_bricks():
    bricks = []
    for row in range(5):
        for col in range(10):
            x = col * 80 + 50
            y = row * 35 + 50
            bricks.append(Brick(x, y, COLORS[row]))
    return bricks

def breakout():
    ball = Ball()
    paddle = Paddle()
    bricks = create_bricks()
    score = 0
    game_over = False
    lives = 3
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    paddle.move("left")
                elif event.key == pygame.K_RIGHT:
                    paddle.move("right")
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move("left")
        if keys[pygame.K_RIGHT]:
            paddle.move("right")
        
        ball.move()
        
        if ball.y > HEIGHT:
            lives -= 1
            if lives == 0:
                game_over = True
            else:
                ball = Ball()
        
        if ball.y + ball.radius >= paddle.y and \
           paddle.x <= ball.x <= paddle.x + paddle.width:
            ball.dy *= -1
        
        for brick in bricks:
            if brick.visible:
                if (brick.x <= ball.x <= brick.x + brick.width and
                    brick.y <= ball.y <= brick.y + brick.height):
                    brick.visible = False
                    ball.dy *= -1
                    score += 10
        
        if all(not brick.visible for brick in bricks):
            game_over = True
        
        ball.draw()
        paddle.draw()
        for brick in bricks:
            brick.draw()
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        lives_text = font.render(f"生命: {lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 80, 10))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    if lives == 0:
        game_over_text = font.render("游戏结束!", True, (255, 0, 0))
    else:
        game_over_text = font.render("恭喜通关!", True, (0, 255, 0))
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    pygame.time.wait(2000)
    pygame.quit()

if __name__ == "__main__":
    breakout()