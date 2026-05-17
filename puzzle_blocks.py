import pygame
import os
import random

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
GRID_SIZE = 40
GRID_WIDTH = 10
GRID_HEIGHT = 12

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)

COLORS = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, ORANGE]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("方块拼图")

clock = pygame.time.Clock()
font = get_chinese_font(30)

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]

class Tetromino:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
        self.rotation = 0
    
    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]
    
    def get_cells(self):
        cells = []
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    cells.append((self.x + x, self.y + y))
        return cells

def puzzle_blocks():
    grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    current_piece = Tetromino()
    next_piece = Tetromino()
    score = 0
    level = 1
    fall_time = 0
    fall_speed = 500
    game_over = False
    
    def check_lines():
        nonlocal grid, score, level, fall_speed
        lines_cleared = 0
        for y in range(len(grid)):
            if all(cell is not None for cell in grid[y]):
                lines_cleared += 1
                grid.pop(y)
                grid.insert(0, [None for _ in range(GRID_WIDTH)])
        
        if lines_cleared > 0:
            score += lines_cleared * 100
            if score > level * 500:
                level += 1
                fall_speed = max(100, 500 - (level - 1) * 50)
    
    def valid_move(piece, dx, dy, new_shape=None):
        if new_shape is None:
            new_shape = piece.shape
        else:
            piece.shape = new_shape
        
        for cell_x, cell_y in piece.get_cells():
            new_x = cell_x + dx
            new_y = cell_y + dy
            
            if new_x < 0 or new_x >= GRID_WIDTH:
                return False
            if new_y >= GRID_HEIGHT:
                return False
            if new_y >= 0 and grid[new_y][new_x]:
                return False
        
        return True
    
    def lock_piece():
        for x, y in current_piece.get_cells():
            if y < 0:
                return True
            grid[y][x] = current_piece.color
        check_lines()
        return False
    
    while not game_over:
        screen.fill(BLACK)
        
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and valid_move(current_piece, -1, 0):
                    current_piece.x -= 1
                elif event.key == pygame.K_RIGHT and valid_move(current_piece, 1, 0):
                    current_piece.x += 1
                elif event.key == pygame.K_DOWN and valid_move(current_piece, 0, 1):
                    current_piece.y += 1
                elif event.key == pygame.K_UP:
                    old_shape = current_piece.shape.copy()
                    current_piece.rotate()
                    if not valid_move(current_piece, 0, 0):
                        current_piece.shape = old_shape
                elif event.key == pygame.K_SPACE:
                    while valid_move(current_piece, 0, 1):
                        current_piece.y += 1
                    game_over = lock_piece()
                    current_piece = next_piece
                    next_piece = Tetromino()
        
        if current_time - fall_time > fall_speed:
            if valid_move(current_piece, 0, 1):
                current_piece.y += 1
            else:
                game_over = lock_piece()
                current_piece = next_piece
                next_piece = Tetromino()
            fall_time = current_time
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x]:
                    rect = pygame.Rect(100 + x * GRID_SIZE, 100 + y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1)
                    pygame.draw.rect(screen, grid[y][x], rect)
        
        for x, y in current_piece.get_cells():
            rect = pygame.Rect(100 + x * GRID_SIZE, 100 + y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1)
            pygame.draw.rect(screen, current_piece.color, rect)
        
        for y, row in enumerate(next_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(WIDTH - 150 + x * GRID_SIZE, 100 + y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1)
                    pygame.draw.rect(screen, next_piece.color, rect)
        
        pygame.draw.rect(screen, WHITE, (100, 100, GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE), 2)
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        level_text = font.render(f"关卡: {level}", True, WHITE)
        next_text = font.render("下一个:", True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))
        screen.blit(next_text, (WIDTH - 150, 70))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    result_text = font.render(f"游戏结束! 最终得分: {score}", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - 150, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    puzzle_blocks()