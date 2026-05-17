import pygame
import os
import random
import math

pygame.init()



# 尝试使用中文字体
def get_chinese_font(size):
    """获取支持中文的字体"""
    font_names = [
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
        "/System/Library/Fonts/PingFang.ttc",  # macOS
    ]
    for font_name in font_names:
        if os.path.exists(font_name):
            try:
                return pygame.font.Font(font_name, size)
            except:
                continue
    return get_chinese_font(size)

WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("贪吃蛇对战版")
clock = pygame.time.Clock()
font = get_chinese_font(30)
big_font = get_chinese_font(50)

class Snake:
    def __init__(self, x, y, color, controls, name):
        self.body = [(x, y)]
        self.color = color
        self.controls = controls
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.grow = False
        self.alive = True
        self.name = name
        self.score = 0
    
    def move(self):
        if not self.alive:
            return
        
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            self.alive = False
            return
        
        if new_head in self.body:
            self.alive = False
            return
        
        self.body.insert(0, new_head)
        
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
    
    def draw(self):
        if not self.alive:
            return
        
        for i, segment in enumerate(self.body):
            shade = max(50, 255 - i * 10)
            segment_color = tuple(min(255, c + 30) if i == 0 else c for c in self.color)
            pygame.draw.rect(screen, segment_color,
                           (segment[0]*GRID_SIZE, segment[1]*GRID_SIZE, 
                            GRID_SIZE-1, GRID_SIZE-1))
            
            if i == 0:
                eye_x = segment[0]*GRID_SIZE + GRID_SIZE//2
                eye_y = segment[1]*GRID_SIZE + GRID_SIZE//2
                pygame.draw.circle(screen, WHITE, (eye_x, eye_y), 3)
    
    def handle_input(self, keys):
        if not self.alive:
            return
        
        if keys[self.controls['up']] and self.direction != (0, 1):
            self.direction = (0, -1)
        elif keys[self.controls['down']] and self.direction != (0, -1):
            self.direction = (0, 1)
        elif keys[self.controls['left']] and self.direction != (1, 0):
            self.direction = (-1, 0)
        elif keys[self.controls['right']] and self.direction != (-1, 0):
            self.direction = (1, 0)

class Food:
    def __init__(self, snakes):
        self.respawn(snakes)
    
    def respawn(self, snakes):
        while True:
            self.x = random.randint(0, GRID_WIDTH-1)
            self.y = random.randint(0, GRID_HEIGHT-1)
            occupied = False
            for snake in snakes:
                if (self.x, self.y) in snake.body:
                    occupied = True
                    break
            if not occupied:
                break
    
    def draw(self):
        pygame.draw.circle(screen, YELLOW,
                         (self.x*GRID_SIZE + GRID_SIZE//2, 
                          self.y*GRID_SIZE + GRID_SIZE//2), 
                          GRID_SIZE//2 - 2)
        
        pygame.draw.circle(screen, ORANGE,
                         (self.x*GRID_SIZE + GRID_SIZE//2 - 3,
                          self.y*GRID_SIZE + GRID_SIZE//2 - 3),
                          4)

class PowerUp:
    def __init__(self, snakes):
        self.respawn(snakes)
    
    def respawn(self, snakes):
        while True:
            self.x = random.randint(0, GRID_WIDTH-1)
            self.y = random.randint(0, GRID_HEIGHT-1)
            occupied = False
            for snake in snakes:
                if (self.x, self.y) in snake.body:
                    occupied = True
                    break
            if not occupied:
                break
        self.types = ['speed', 'shrink', 'ghost']
        self.type = random.choice(self.types)
        self.lifetime = 300
    
    def draw(self):
        self.lifetime -= 1
        colors = {'speed': GREEN, 'shrink': RED, 'ghost': PURPLE}
        pygame.draw.rect(screen, colors[self.type],
                       (self.x*GRID_SIZE + 2, self.y*GRID_SIZE + 2,
                        GRID_SIZE-4, GRID_SIZE-4))

def snake_variants():
    mode = "menu"
    
    screen.fill(BLACK)
    title = big_font.render("贪吃蛇对战版", True, YELLOW)
    screen.blit(title, (WIDTH // 2 - 150, 100))
    
    modes = ["1. 单人模式", "2. 双人对战", "3. 合作模式", "4. 退出"]
    for i, m in enumerate(modes):
        text = font.render(m, True, WHITE)
        screen.blit(text, (WIDTH // 2 - 80, 250 + i * 50))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = "single"
                    waiting = False
                elif event.key == pygame.K_2:
                    mode = "vs"
                    waiting = False
                elif event.key == pygame.K_3:
                    mode = "coop"
                    waiting = False
                elif event.key == pygame.K_4:
                    return
    
    snakes = []
    
    if mode == "single":
        snakes.append(Snake(10, 10, GREEN, 
                          {'up': pygame.K_w, 'down': pygame.K_s, 
                           'left': pygame.K_a, 'right': pygame.K_d}, "玩家"))
    elif mode == "vs":
        snakes.append(Snake(10, 10, GREEN, 
                          {'up': pygame.K_w, 'down': pygame.K_s, 
                           'left': pygame.K_a, 'right': pygame.K_d}, "玩家1"))
        snakes.append(Snake(GRID_WIDTH-11, GRID_HEIGHT-11, BLUE,
                          {'up': pygame.K_UP, 'down': pygame.K_DOWN,
                           'left': pygame.K_LEFT, 'right': pygame.K_RIGHT}, "玩家2"))
    elif mode == "coop":
        snakes.append(Snake(10, 10, GREEN,
                          {'up': pygame.K_w, 'down': pygame.K_s,
                           'left': pygame.K_a, 'right': pygame.K_d}, "玩家1"))
        snakes.append(Snake(10, GRID_HEIGHT-11, BLUE,
                          {'up': pygame.K_i, 'down': pygame.K_k,
                           'left': pygame.K_j, 'right': pygame.K_l}, "玩家2"))
    
    food = Food(snakes)
    powerups = []
    game_over = False
    frame_count = 0
    speed = 8
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        keys = pygame.key.get_pressed()
        for snake in snakes:
            snake.handle_input(keys)
        
        frame_count += 1
        if frame_count % speed == 0:
            for snake in snakes:
                snake.move()
                
                if snake.alive:
                    head = snake.body[0]
                    
                    if head == (food.x, food.y):
                        snake.grow = True
                        snake.score += 10
                        food.respawn(snakes)
                    
                    for powerup in powerups[:]:
                        if head == (powerup.x, powerup.y):
                            if powerup.type == 'shrink' and len(snake.body) > 3:
                                snake.body.pop()
                            elif powerup.type == 'speed':
                                speed = max(3, speed - 1)
                            powerups.remove(powerup)
                    
                    for other in snakes:
                        if other != snake and other.alive:
                            if head in other.body:
                                snake.alive = False
        
        if frame_count % 300 == 0 and len(powerups) < 2:
            powerups.append(PowerUp(snakes))
        
        for powerup in powerups[:]:
            if powerup.lifetime <= 0:
                powerups.remove(powerup)
        
        if mode in ["vs", "coop"]:
            alive_snakes = [s for s in snakes if s.alive]
            if mode == "vs" and len(alive_snakes) <= 1:
                game_over = True
            elif mode == "coop" and len(alive_snakes) == 0:
                game_over = True
        
        if mode == "single":
            if not snakes[0].alive:
                game_over = True
        
        pygame.draw.rect(screen, (20, 20, 20), (0, 0, WIDTH, 50))
        
        for i, snake in enumerate(snakes):
            name_text = font.render(f"{snake.name}: {snake.score}", True, snake.color)
            screen.blit(name_text, (10 + i * 200, 15))
            if not snake.alive:
                dead = font.render("(死亡)", True, RED)
                screen.blit(dead, (10 + i * 200 + 80, 15))
        
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, (20, 20, 20), (0, y), (WIDTH, y))
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(screen, (20, 20, 20), (x, 0), (x, HEIGHT))
        
        food.draw()
        
        for powerup in powerups:
            powerup.draw()
        
        for snake in snakes:
            snake.draw()
        
        inst = font.render("WASD/方向键移动 | R重新开始 | ESC退出", True, WHITE)
        screen.blit(inst, (WIDTH // 2 - inst.get_width() // 2, HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(60)
    
    screen.fill(BLACK)
    result = big_font.render("游戏结束!", True, YELLOW)
    screen.blit(result, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
    
    if mode == "vs":
        winner = max(snakes, key=lambda s: s.score)
        winner_text = font.render(f"获胜者: {winner.name} - {winner.score}分", True, winner.color)
        screen.blit(winner_text, (WIDTH // 2 - 100, HEIGHT // 2 + 20))
    elif mode == "single":
        score_text = font.render(f"最终得分: {snakes[0].score}", True, GREEN)
        screen.blit(score_text, (WIDTH // 2 - 80, HEIGHT // 2 + 20))
    else:
        total_score = sum(s.score for s in snakes)
        score_text = font.render(f"总分: {total_score}", True, YELLOW)
        screen.blit(score_text, (WIDTH // 2 - 60, HEIGHT // 2 + 20))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    snake_variants()
