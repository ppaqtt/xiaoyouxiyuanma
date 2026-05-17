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

WIDTH, HEIGHT = 400, 500
GRID_SIZE = 4
CELL_SIZE = 80
CELL_PADDING = 10
TOP_MARGIN = 100

BACKGROUND_COLOR = (187, 173, 160)
CELL_COLOR = (205, 193, 180)
EMPTY_COLOR = (205, 193, 180)

COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}

TEXT_COLORS = {
    0: (205, 193, 180),
    2: (119, 110, 101),
    4: (119, 110, 101),
    8: (249, 246, 242),
    16: (249, 246, 242),
    32: (249, 246, 242),
    64: (249, 246, 242),
    128: (249, 246, 242),
    256: (249, 246, 242),
    512: (249, 246, 242),
    1024: (249, 246, 242),
    2048: (249, 246, 242),
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048游戏")

clock = pygame.time.Clock()
font = get_chinese_font(40)

def create_grid():
    return [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def add_random_tile(grid):
    empty_cells = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE) if grid[i][j] == 0]
    if empty_cells:
        i, j = random.choice(empty_cells)
        grid[i][j] = 2 if random.random() < 0.9 else 4

def draw_grid(grid, score):
    screen.fill(BACKGROUND_COLOR)
    
    score_text = font.render(f"分数: {score}", True, (255, 255, 255))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))
    
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            value = grid[i][j]
            x = j * (CELL_SIZE + CELL_PADDING) + CELL_PADDING
            y = i * (CELL_SIZE + CELL_PADDING) + TOP_MARGIN
            pygame.draw.rect(screen, COLORS[value], (x, y, CELL_SIZE, CELL_SIZE))
            
            if value != 0:
                text = font.render(str(value), True, TEXT_COLORS[value])
                text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                screen.blit(text, text_rect)

def slide_row(row):
    new_row = [i for i in row if i != 0]
    for i in range(len(new_row) - 1):
        if new_row[i] == new_row[i + 1]:
            new_row[i] *= 2
            new_row[i + 1] = 0
    new_row = [i for i in new_row if i != 0]
    return new_row + [0] * (GRID_SIZE - len(new_row))

def move_left(grid):
    new_grid = []
    score = 0
    for row in grid:
        new_row = slide_row(row)
        new_grid.append(new_row)
        for i in range(GRID_SIZE):
            if new_row[i] > row[i]:
                score += new_row[i]
    return new_grid, score

def move_right(grid):
    new_grid = []
    score = 0
    for row in grid:
        new_row = slide_row(row[::-1])[::-1]
        new_grid.append(new_row)
        for i in range(GRID_SIZE):
            if new_row[i] > row[i]:
                score += new_row[i]
    return new_grid, score

def transpose(grid):
    return [[grid[j][i] for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]

def move_up(grid):
    transposed = transpose(grid)
    new_transposed, score = move_left(transposed)
    return transpose(new_transposed), score

def move_down(grid):
    transposed = transpose(grid)
    new_transposed, score = move_right(transposed)
    return transpose(new_transposed), score

def has_empty_cells(grid):
    return any(0 in row for row in grid)

def can_merge(grid):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if j < GRID_SIZE - 1 and grid[i][j] == grid[i][j + 1]:
                return True
            if i < GRID_SIZE - 1 and grid[i][j] == grid[i + 1][j]:
                return True
    return False

def game_2048():
    grid = create_grid()
    add_random_tile(grid)
    add_random_tile(grid)
    score = 0
    game_over = False
    
    while not game_over:
        draw_grid(grid, score)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    new_grid, added_score = move_left(grid)
                elif event.key == pygame.K_RIGHT:
                    new_grid, added_score = move_right(grid)
                elif event.key == pygame.K_UP:
                    new_grid, added_score = move_up(grid)
                elif event.key == pygame.K_DOWN:
                    new_grid, added_score = move_down(grid)
                else:
                    continue
                
                if new_grid != grid:
                    grid = new_grid
                    score += added_score
                    add_random_tile(grid)
                
                if not has_empty_cells(grid) and not can_merge(grid):
                    game_over = True
    
    draw_grid(grid, score)
    game_over_text = font.render("游戏结束!", True, (255, 0, 0))
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    pygame.time.wait(2000)
    pygame.quit()

if __name__ == "__main__":
    game_2048()