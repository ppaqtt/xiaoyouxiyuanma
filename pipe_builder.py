import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 700, 700
GRID_SIZE = 50

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("管道连接大师")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
big_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 22)

PIPE_TYPES = {
    'straight_h': {'connects': ['left', 'right'], 'symbol': '═'},
    'straight_v': {'connects': ['up', 'down'], 'symbol': '║'},
    'corner_tl': {'connects': ['right', 'down'], 'symbol': '╔'},
    'corner_tr': {'connects': ['left', 'down'], 'symbol': '╗'},
    'corner_bl': {'connects': ['right', 'up'], 'symbol': '╚'},
    'corner_br': {'connects': ['left', 'up'], 'symbol': '╝'},
    'cross': {'connects': ['up', 'down', 'left', 'right'], 'symbol': '╬'},
}

PIPE_KEYS = {
    'straight_h': pygame.K_1,
    'straight_v': pygame.K_2,
    'corner_tl': pygame.K_3,
    'corner_tr': pygame.K_4,
    'corner_bl': pygame.K_5,
    'corner_br': pygame.K_6,
    'cross': pygame.K_7,
}

class Pipe:
    def __init__(self, pipe_type, rotation=0):
        self.pipe_type = pipe_type
        self.rotation = rotation
        self.connected = False
        self.flowing = False
    
    def get_connections(self):
        base = PIPE_TYPES[self.pipe_type]['connects']
        rotations = rotation // 90
        return base

class Level:
    def __init__(self, level_num):
        self.size = 5 + level_num
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.source = (0, random.randint(1, self.size - 2))
        self.drain = (self.size - 1, random.randint(1, self.size - 2))
        self.level_num = level_num
    
    def generate_level(self):
        for y in range(self.size):
            for x in range(self.size):
                if (x, y) == self.source or (x, y) == self.drain:
                    continue
                if random.random() < 0.3:
                    pipe_types = list(PIPE_TYPES.keys())
                    self.grid[y][x] = Pipe(random.choice(pipe_types))

def check_connection(level, player_grid):
    size = level.size
    connected = [[False] * size for _ in range(size)]
    queue = [level.source]
    connected[level.source[1]][level.source[0]] = True
    
    directions = {
        'left': (-1, 0),
        'right': (1, 0),
        'up': (0, -1),
        'down': (0, 1)
    }
    
    opposite = {'left': 'right', 'right': 'left', 'up': 'down', 'down': 'up'}
    
    while queue:
        x, y = queue.pop(0)
        
        if (x, y) == level.drain:
            return True
        
        for pipe in [player_grid[y][x]] if player_grid[y][x] else []:
            for direction in PIPE_TYPES[pipe.pipe_type]['connects']:
                dx, dy = directions[direction]
                nx, ny = x + dx, y + dy
                
                if 0 <= nx < size and 0 <= ny < size and not connected[ny][nx]:
                    if player_grid[ny][nx]:
                        next_pipe = player_grid[ny][nx]
                        if opposite[direction] in PIPE_TYPES[next_pipe.pipe_type]['connects']:
                            connected[ny][nx] = True
                            queue.append((nx, ny))
    
    return False

def pipe_builder():
    current_level = 1
    selected_pipe = 'straight_h'
    max_level = 5
    levels_completed = 0
    
    while current_level <= max_level:
        level = Level(current_level)
        level.generate_level()
        
        player_grid = [[None for _ in range(level.size)] for _ in range(level.size)]
        
        running = True
        
        while running:
            screen.fill(BLACK)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    gx = mx // GRID_SIZE
                    gy = my // GRID_SIZE
                    
                    if 0 <= gx < level.size and 0 <= gy < level.size:
                        if (gx, gy) != level.source and (gx, gy) != level.drain:
                            if event.button == 1:
                                if player_grid[gy][gx]:
                                    player_grid[gy][gx].rotation = (player_grid[gy][gx].rotation + 90) % 360
                                else:
                                    player_grid[gy][gx] = Pipe(selected_pipe)
                            elif event.button == 3:
                                player_grid[gy][gx] = None
                
                elif event.type == pygame.KEYDOWN:
                    for pipe_type, key in PIPE_KEYS.items():
                        if event.key == key:
                            selected_pipe = pipe_type
                    if event.key == pygame.K_SPACE:
                        if check_connection(level, player_grid):
                            levels_completed += 1
                            current_level += 1
                            running = False
                    elif event.key == pygame.K_r:
                        running = False
            
            pygame.draw.rect(screen, (20, 20, 40), (0, 0, WIDTH, 50))
            
            title = font.render(f"关卡 {current_level}/{max_level}", True, YELLOW)
            screen.blit(title, (10, 15))
            
            level_complete = check_connection(level, player_grid)
            status = "连接成功! 按空格继续" if level_complete else "继续连接管道..."
            status_color = GREEN if level_complete else WHITE
            status_text = font.render(status, True, status_color)
            screen.blit(status_text, (200, 15))
            
            size_pixels = level.size * GRID_SIZE
            offset_x = (WIDTH - size_pixels) // 2
            offset_y = (HEIGHT - size_pixels) // 2
            
            for y in range(level.size):
                for x in range(size_pixels):
                    px = offset_x + x * GRID_SIZE
                    py = offset_y + y * GRID_SIZE
                    pygame.draw.rect(screen, (30, 30, 30), (px, py, GRID_SIZE, GRID_SIZE), 1)
            
            sx = offset_x + level.source[0] * GRID_SIZE
            sy = offset_y + level.source[1] * GRID_SIZE
            pygame.draw.circle(screen, GREEN, (sx + GRID_SIZE // 2, sy + GRID_SIZE // 2), 15)
            pygame.draw.circle(screen, WHITE, (sx + GRID_SIZE // 2, sy + GRID_SIZE // 2), 15, 2)
            
            dx = offset_x + level.drain[0] * GRID_SIZE
            dy = offset_y + level.drain[1] * GRID_SIZE
            pygame.draw.circle(screen, RED, (dx + GRID_SIZE // 2, dy + GRID_SIZE // 2), 15)
            pygame.draw.circle(screen, WHITE, (dx + GRID_SIZE // 2, dy + GRID_SIZE // 2), 15, 2)
            
            for y in range(level.size):
                for x in range(level.size):
                    pipe = player_grid[y][x]
                    if pipe:
                        px = offset_x + x * GRID_SIZE
                        py = offset_y + y * GRID_SIZE
                        
                        pipe_color = GREEN if check_connection(level, player_grid) else YELLOW
                        pygame.draw.rect(screen, pipe_color, 
                                       (px + 5, py + 5, GRID_SIZE - 10, GRID_SIZE - 10), border_radius=5)
            
            pygame.draw.rect(screen, (20, 20, 40), (0, HEIGHT - 80, WIDTH, 80))
            
            pipe_names = list(PIPE_TYPES.keys())
            for i, pipe_type in enumerate(pipe_names):
                key_char = chr(49 + i)
                color = GREEN if pipe_type == selected_pipe else GRAY
                text = f"{key_char}: {PIPE_TYPES[pipe_type]['symbol']}"
                t = small_font.render(text, True, color)
                screen.blit(t, (20 + i * 90, HEIGHT - 60))
            
            inst = small_font.render("左键放置 | 右键删除 | 滚轮旋转 | 1-7选择管道类型", True, WHITE)
            screen.blit(inst, (20, HEIGHT - 25))
            
            pygame.display.flip()
            clock.tick(60)
    
    screen.fill(BLACK)
    result = big_font.render("恭喜通关!", True, YELLOW)
    screen.blit(result, (WIDTH // 2 - 120, HEIGHT // 2 - 30))
    
    complete = font.render(f"完成了 {levels_completed} 个关卡!", True, GREEN)
    screen.blit(complete, (WIDTH // 2 - 100, HEIGHT // 2 + 30))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    pipe_builder()
