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

WIDTH, HEIGHT = 400, 400
GRID_SIZE = 10
CELL_SIZE = 40

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

NUM_COLORS = {
    1: (0, 0, 255),
    2: (0, 128, 0),
    3: (255, 0, 0),
    4: (0, 0, 128),
    5: (128, 0, 0),
    6: (0, 128, 128),
    7: (0, 0, 0),
    8: (128, 128, 128),
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("扫雷游戏")

clock = pygame.time.Clock()
font = get_chinese_font(25)

def create_board(mines=10):
    board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    mine_positions = random.sample([(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)], mines)
    
    for i, j in mine_positions:
        board[i][j] = -1
    
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if board[i][j] != -1:
                count = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE and board[ni][nj] == -1:
                            count += 1
                board[i][j] = count
    
    return board

def draw_board(board, revealed, flags):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = j * CELL_SIZE
            y = i * CELL_SIZE
            
            if revealed[i][j]:
                if board[i][j] == -1:
                    pygame.draw.rect(screen, RED, (x, y, CELL_SIZE - 1, CELL_SIZE - 1))
                else:
                    pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE - 1, CELL_SIZE - 1))
                    if board[i][j] > 0:
                        text = font.render(str(board[i][j]), True, NUM_COLORS[board[i][j]])
                        screen.blit(text, (x + CELL_SIZE // 3, y + CELL_SIZE // 4))
            else:
                pygame.draw.rect(screen, GRAY, (x, y, CELL_SIZE - 1, CELL_SIZE - 1))
                if (i, j) in flags:
                    pygame.draw.circle(screen, RED, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 10)

def reveal(board, revealed, i, j):
    if i < 0 or i >= GRID_SIZE or j < 0 or j >= GRID_SIZE or revealed[i][j]:
        return
    
    revealed[i][j] = True
    
    if board[i][j] == 0:
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                reveal(board, revealed, i + di, j + dj)

def minesweeper():
    board = create_board()
    revealed = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    flags = set()
    game_over = False
    won = False
    
    while not game_over:
        screen.fill(BLACK)
        draw_board(board, revealed, flags)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = x // CELL_SIZE
                row = y // CELL_SIZE
                
                if event.button == 1:
                    if (row, col) not in flags:
                        if board[row][col] == -1:
                            for i in range(GRID_SIZE):
                                for j in range(GRID_SIZE):
                                    if board[i][j] == -1:
                                        revealed[i][j] = True
                            game_over = True
                        else:
                            reveal(board, revealed, row, col)
                elif event.button == 3:
                    if (row, col) in flags:
                        flags.remove((row, col))
                    else:
                        flags.add((row, col))
        
        if all(revealed[i][j] for i in range(GRID_SIZE) for j in range(GRID_SIZE) if board[i][j] != -1):
            won = True
            game_over = True
        
        clock.tick(30)
    
    screen.fill(BLACK)
    if won:
        game_over_text = font.render("恭喜你赢了!", True, (0, 255, 0))
    else:
        game_over_text = font.render("游戏结束!", True, (255, 0, 0))
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    pygame.time.wait(2000)
    pygame.quit()

if __name__ == "__main__":
    minesweeper()