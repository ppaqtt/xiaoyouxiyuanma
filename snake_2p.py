import pygame
import random
import time

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
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("贪吃蛇大战: 竞技场")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
big_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 22)

POWERUP_TYPES = {
    'SPEED': {'color': (0, 255, 255), 'name': '加速', 'duration': 5},
    'SHIELD': {'color': (255, 215, 0), 'name': '护盾', 'duration': 8},
    'PHANTOM': {'color': (180, 180, 255), 'name': '隐身', 'duration': 4},
    'BOMB': {'color': (255, 0, 100), 'name': '炸弹', 'duration': 0},
}

FOOD_TYPES = {
    'NORMAL': {'color': RED, 'points': 10},
    'GOLDEN': {'color': YELLOW, 'points': 30},
    'POISON': {'color': (100, 0, 100), 'points': -20},
}

class Snake:
    def __init__(self, color, start_pos, controls, name):
        self.body = [start_pos]
        self.color = color
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.grow = False
        self.controls = controls
        self.alive = True
        self.name = name
        self.active_powerups = {}
        self.bomb_ready = False
        self.original_speed = 10
        self.current_speed = self.original_speed
    
    def apply_powerup(self, p_type):
        self.active_powerups[p_type] = time.time() + POWERUP_TYPES[p_type]['duration']
        if p_type == 'SPEED':
            self.current_speed = 15
        elif p_type == 'BOMB':
            self.bomb_ready = True
    
    def update_powerups(self):
        now = time.time()
        expired = [k for k, v in self.active_powerups.items() if v < now]
        for k in expired:
            if k == 'SPEED':
                self.current_speed = self.original_speed
            del self.active_powerups[k]
    
    def is_phantom(self):
        return 'PHANTOM' in self.active_powerups
    
    def has_shield(self):
        return 'SHIELD' in self.active_powerups
    
    def use_bomb(self):
        if self.bomb_ready:
            self.bomb_ready = False
            return True
        return False
    
    def move(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        if not self.is_phantom():
            if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
                if self.has_shield():
                    del self.active_powerups['SHIELD']
                    new_head = (
                        (new_head[0] + GRID_WIDTH) % GRID_WIDTH,
                        (new_head[1] + GRID_HEIGHT) % GRID_HEIGHT
                    )
                else:
                    self.alive = False
                    return
            if new_head in self.body[1:]:
                if self.has_shield():
                    del self.active_powerups['SHIELD']
                else:
                    self.alive = False
                    return
        else:
            new_head = (
                (new_head[0] + GRID_WIDTH) % GRID_WIDTH,
                (new_head[1] + GRID_HEIGHT) % GRID_HEIGHT
            )
        
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
    
    def draw(self):
        is_phantom = self.is_phantom()
        for i, segment in enumerate(self.body):
            alpha = 100 if is_phantom else 255
            if i == 0 and self.has_shield():
                pygame.draw.circle(screen, (255, 255, 0),
                               (segment[0]*GRID_SIZE + GRID_SIZE//2, 
                                segment[1]*GRID_SIZE + GRID_SIZE//2),
                               GRID_SIZE//2 + 5, 3)
            color = (*self.color, alpha) if is_phantom else self.color
            pygame.draw.rect(screen, color,
                          (segment[0]*GRID_SIZE, segment[1]*GRID_SIZE, GRID_SIZE-1, GRID_SIZE-1))

def get_random_pos(exclude=[]):
    while True:
        pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
        if pos not in exclude:
            return pos

def get_food(snakes, powerups, bombs):
    exclude = []
    for s in snakes:
        exclude.extend(s.body)
    exclude.extend(powerups)
    exclude.extend(bombs)
    pos = get_random_pos(exclude)
    if random.random() < 0.1:
        return pos, 'GOLDEN'
    elif random.random() < 0.15:
        return pos, 'POISON'
    return pos, 'NORMAL'

def spawn_powerup(snakes, food, powerups, bombs):
    exclude = []
    for s in snakes:
        exclude.extend(s.body)
    exclude.append(food)
    exclude.extend(powerups)
    exclude.extend(bombs)
    if random.random() < 0.02:
        pos = get_random_pos(exclude)
        types = list(POWERUP_TYPES.keys())
        return pos, random.choice(types)
    return None

def draw_explosion(x, y, radius):
    for r in range(0, radius, 5):
        pygame.draw.circle(screen, (255, 100, 0), (x, y), r, 3)

def snake_2p_battle():
    snake1 = Snake(GREEN, (10, 10), 
                  {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d, 'skill': pygame.K_LSHIFT},
                  "绿队")
    snake2 = Snake(BLUE, (GRID_WIDTH-11, GRID_HEIGHT-11), 
                  {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'skill': pygame.K_RSHIFT},
                  "蓝队")
    
    snakes = [snake1, snake2]
    food, food_type = get_food(snakes, [], [])
    powerups = []
    bombs = []
    explosions = []
    scores = [0, 0]
    game_over = False
    winner = None
    time_left = 180
    last_time = time.time()
    
    while not game_over:
        dt = time.time() - last_time
        last_time = time.time()
        time_left -= dt
        
        if time_left <= 0:
            if scores[0] > scores[1]:
                winner = snake1.name
            elif scores[1] > scores[0]:
                winner = snake2.name
            else:
                winner = "平局"
            game_over = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                for snake in snakes:
                    if event.key == snake.controls['skill']:
                        if snake.use_bomb():
                            for other in snakes:
                                if other != snake and len(other.body) > 1:
                                    other.body.pop()
                                    other.body.pop()
                            explosions.append((snake.body[0][0]*GRID_SIZE + GRID_SIZE//2, 
                                              snake.body[0][1]*GRID_SIZE + GRID_SIZE//2, time.time()))
                    elif event.key == snake.controls['up'] and snake.direction != (0, 1):
                        snake.direction = (0, -1)
                    elif event.key == snake.controls['down'] and snake.direction != (0, -1):
                        snake.direction = (0, 1)
                    elif event.key == snake.controls['left'] and snake.direction != (1, 0):
                        snake.direction = (-1, 0)
                    elif event.key == snake.controls['right'] and snake.direction != (-1, 0):
                        snake.direction = (1, 0)
        
        for snake in snakes:
            if snake.alive:
                snake.update_powerups()
                snake.move()
        
        for i, snake in enumerate(snakes):
            if not snake.alive:
                winner = snakes[1-i].name
                game_over = True
        
        head1 = snake1.body[0]
        head2 = snake2.body[0]
        
        if not snake1.is_phantom() and head1 in snake2.body:
            winner = snake2.name
            game_over = True
        if not snake2.is_phantom() and head2 in snake1.body:
            winner = snake1.name
            game_over = True
        
        for i, snake in enumerate(snakes):
            if snake.body[0] == food:
                snake.grow = True
                scores[i] += FOOD_TYPES[food_type]['points']
                if scores[i] < 0:
                    scores[i] = 0
                food, food_type = get_food(snakes, powerups, bombs)
        
        new_powerup = spawn_powerup(snakes, food, powerups, bombs)
        if new_powerup:
            powerups.append(new_powerup)
        
        for i, snake in enumerate(snakes):
            for j, (pos, p_type) in list(enumerate(powerups)):
                if snake.body[0] == pos:
                    snake.apply_powerup(p_type)
                    del powerups[j]
        
        explosions = [(x, y, t) for x, y, t in explosions if time.time() - t < 0.5]
        
        screen.fill(BLACK)
        
        pygame.draw.rect(screen, GRAY, (0, HEIGHT-60, WIDTH, 60))
        
        pygame.draw.rect(screen, FOOD_TYPES[food_type]['color'], 
                      (food[0]*GRID_SIZE, food[1]*GRID_SIZE, GRID_SIZE-1, GRID_SIZE-1))
        
        for pos, p_type in powerups:
            pygame.draw.circle(screen, POWERUP_TYPES[p_type]['color'],
                            (pos[0]*GRID_SIZE + GRID_SIZE//2, pos[1]*GRID_SIZE + GRID_SIZE//2), GRID_SIZE//2-2)
        
        for x, y, t in explosions:
            draw_explosion(x, y, int((time.time() - t) * 100))
        
        for snake in snakes:
            snake.draw()
        
        for i, snake in enumerate(snakes):
            name_text = font.render(snake.name, True, snake.color)
            y_pos = HEIGHT - 50 if i == 0 else HEIGHT - 30
            screen.blit(name_text, (10, y_pos))
            
            score_text = font.render(f"分数: {scores[i]}", True, WHITE)
            screen.blit(score_text, (120, y_pos))
            
            p_texts = []
            for p_type in snake.active_powerups:
                remaining = int(snake.active_powerups[p_type] - time.time())
                if remaining > 0:
                    p_texts.append(f"{POWERUP_TYPES[p_type]['name']}({remaining}s)")
            if snake.bomb_ready:
                p_texts.append("💣准备!")
            if p_texts:
                p_str = " ".join(p_texts)
                p_render = small_font.render(p_str, True, ORANGE)
                screen.blit(p_render, (250, y_pos))
        
        time_text = big_font.render(f"{int(time_left)}", True, WHITE)
        screen.blit(time_text, (WIDTH//2 - 20, 10))
        
        pygame.display.update()
        clock.tick(max(snake1.current_speed, snake2.current_speed))
    
    screen.fill(BLACK)
    if winner:
        winner_text = big_font.render(f"{winner}获胜!", True, WHITE)
    else:
        winner_text = big_font.render("平局!", True, WHITE)
    screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, HEIGHT//2 - 50))
    
    final_score1 = font.render(f"绿队最终分数: {scores[0]}", True, GREEN)
    final_score2 = font.render(f"蓝队最终分数: {scores[1]}", True, BLUE)
    screen.blit(final_score1, (WIDTH//2 - final_score1.get_width()//2, HEIGHT//2 + 20))
    screen.blit(final_score2, (WIDTH//2 - final_score2.get_width()//2, HEIGHT//2 + 60))
    
    pygame.display.update()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    snake_2p_battle()
