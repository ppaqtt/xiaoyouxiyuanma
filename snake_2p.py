import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("贪吃蛇 双人对战")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)
big_font = pygame.font.Font(None, 50)

class Snake:
    def __init__(self, color, start_pos, controls):
        self.body = [start_pos]
        self.color = color
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.grow = False
        self.controls = controls
        self.alive = True
    
    def move(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
            new_head in self.body):
            self.alive = False
            return
        
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
    
    def draw(self):
        for segment in self.body:
            pygame.draw.rect(screen, self.color,
                          (segment[0]*GRID_SIZE, segment[1]*GRID_SIZE, GRID_SIZE-1, GRID_SIZE-1))

def get_food(snakes):
    while True:
        food = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
        if all(food not in snake.body for snake in snakes):
            return food

def snake_2p():
    snake1 = Snake(GREEN, (10, 10), {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d})
    snake2 = Snake(BLUE, (GRID_WIDTH-11, GRID_HEIGHT-11), {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT})
    
    snakes = [snake1, snake2]
    food = get_food(snakes)
    scores = [0, 0]
    game_over = False
    winner = None
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                for snake in snakes:
                    if event.key == snake.controls['up'] and snake.direction != (0, 1):
                        snake.direction = (0, -1)
                    elif event.key == snake.controls['down'] and snake.direction != (0, -1):
                        snake.direction = (0, 1)
                    elif event.key == snake.controls['left'] and snake.direction != (1, 0):
                        snake.direction = (-1, 0)
                    elif event.key == snake.controls['right'] and snake.direction != (-1, 0):
                        snake.direction = (1, 0)
        
        for snake in snakes:
            if snake.alive:
                snake.move()
        
        for i, snake in enumerate(snakes):
            if not snake.alive:
                winner = "玩家1" if i == 1 else "玩家2"
                game_over = True
        
        head1 = snake1.body[0]
        if head1 in snake2.body:
            winner = "玩家2"
            game_over = True
        
        head2 = snake2.body[0]
        if head2 in snake1.body:
            winner = "玩家1"
            game_over = True
        
        for i, snake in enumerate(snakes):
            if snake.body[0] == food:
                snake.grow = True
                scores[i] += 10
                food = get_food(snakes)
        
        pygame.draw.rect(screen, RED, (food[0]*GRID_SIZE, food[1]*GRID_SIZE, GRID_SIZE-1, GRID_SIZE-1))
        
        for snake in snakes:
            snake.draw()
        
        score_text = font.render(f"绿队: {scores[0]}", True, GREEN)
        screen.blit(score_text, (10, 10))
        
        score_text = font.render(f"蓝队: {scores[1]}", True, BLUE)
        screen.blit(score_text, (WIDTH - 120, 10))
        
        controls_text = font.render("绿队: WASD | 蓝队: 方向键", True, WHITE)
        screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT - 30))
        
        pygame.display.update()
        clock.tick(10)
    
    screen.fill(BLACK)
    if winner:
        winner_text = big_font.render(f"{winner}获胜!", True, WHITE)
    else:
        winner_text = big_font.render("平局!", True, WHITE)
    screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    snake_2p()