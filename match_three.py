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

WIDTH, HEIGHT = 500, 600
GRID_SIZE = 8
CELL_SIZE = 60
TOP_MARGIN = 50

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (255, 0, 0),    # 红
    (0, 255, 0),    # 绿
    (0, 0, 255),    # 蓝
    (255, 255, 0),  # 黄
    (255, 0, 255),  # 紫
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("消消乐")

clock = pygame.time.Clock()
font = get_chinese_font(30)

def create_board():
    board = []
    for _ in range(GRID_SIZE):
        row = []
        for _ in range(GRID_SIZE):
            row.append(random.randint(0, len(COLORS) - 1))
        board.append(row)
    return board

def draw_board(board, score):
    screen.fill(BLACK)
    
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = j * CELL_SIZE
            y = i * CELL_SIZE + TOP_MARGIN
            color = COLORS[board[i][j]]
            pygame.draw.rect(screen, color, (x + 5, y + 5, CELL_SIZE - 10, CELL_SIZE - 10))
    
    score_text = font.render(f"分数: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def find_matches(board):
    matches = set()
    
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE - 2):
            if board[i][j] == board[i][j+1] == board[i][j+2]:
                matches.add((i, j))
                matches.add((i, j+1))
                matches.add((i, j+2))
    
    for i in range(GRID_SIZE - 2):
        for j in range(GRID_SIZE):
            if board[i][j] == board[i+1][j] == board[i+2][j]:
                matches.add((i, j))
                matches.add((i+1, j))
                matches.add((i+2, j))
    
    return matches

def remove_matches(board, matches):
    for i, j in matches:
        board[i][j] = -1
    return board

def fill_board(board):
    for j in range(GRID_SIZE):
        empty_spots = 0
        for i in range(GRID_SIZE - 1, -1, -1):
            if board[i][j] == -1:
                empty_spots += 1
            elif empty_spots > 0:
                board[i + empty_spots][j] = board[i][j]
                board[i][j] = -1
        
        for i in range(empty_spots):
            board[i][j] = random.randint(0, len(COLORS) - 1)
    
    return board

def match_three():
    board = create_board()
    score = 0
    selected = None
    game_over = False
    
    while True:
        matches = find_matches(board)
        while matches:
            score += len(matches) * 10
            board = remove_matches(board, matches)
            board = fill_board(board)
            matches = find_matches(board)
            draw_board(board, score)
            pygame.display.update()
            pygame.time.wait(100)
        
        draw_board(board, score)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = x // CELL_SIZE
                row = (y - TOP_MARGIN) // CELL_SIZE
                
                if 0 <= col < GRID_SIZE and 0 <= row < GRID_SIZE:
                    if selected is None:
                        selected = (row, col)
                    else:
                        if (abs(selected[0] - row) == 1 and selected[1] == col) or \
                           (abs(selected[1] - col) == 1 and selected[0] == row):
                            board[selected[0]][selected[1]], board[row][col] = board[row][col], board[selected[0]][selected[1]]
                            matches = find_matches(board)
                            if not matches:
                                board[selected[0]][selected[1]], board[row][col] = board[row][col], board[selected[0]][selected[1]]
                        selected = None
        
        pygame.display.update()
        clock.tick(30)

if __name__ == "__main__":
    match_three()