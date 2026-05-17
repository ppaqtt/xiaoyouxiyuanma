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

WIDTH, HEIGHT = 540, 600
CELL_SIZE = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("数独")

clock = pygame.time.Clock()
font = get_chinese_font(40)
small_font = get_chinese_font(30)

def create_sudoku():
    base = [[(j*3 + j//3 + i) % 9 + 1 for j in range(9)] for i in range(9)]
    
    for _ in range(40):
        row1 = random.randint(0, 8)
        row2 = random.randint(0, 8)
        for col in range(9):
            base[row1][col], base[row2][col] = base[row2][col], base[row1][col]
    
    for _ in range(40):
        col1 = random.randint(0, 8)
        col2 = random.randint(0, 8)
        for row in range(9):
            base[row][col1], base[row][col2] = base[row][col2], base[row][col1]
    
    puzzle = [row[:] for row in base]
    
    blanks = 40
    while blanks > 0:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        if puzzle[row][col] != 0:
            puzzle[row][col] = 0
            blanks -= 1
    
    return base, puzzle

def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num:
            return False
    
    for i in range(9):
        if board[i][col] == num:
            return False
    
    box_row = (row // 3) * 3
    box_col = (col // 3) * 3
    for i in range(3):
        for j in range(3):
            if board[box_row + i][box_col + j] == num:
                return False
    
    return True

def solve_sudoku(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def sudoku():
    solution, puzzle = create_sudoku()
    board = [row[:] for row in puzzle]
    
    selected = None
    error_pos = None
    game_over = False
    won = False
    
    while not game_over:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 0 <= x < WIDTH and 0 <= y < HEIGHT - 60:
                    selected = (y // CELL_SIZE, x // CELL_SIZE)
                    if puzzle[selected[0]][selected[1]] != 0:
                        selected = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    solution, puzzle = create_sudoku()
                    board = [row[:] for row in puzzle]
                    selected = None
                    won = False
                    error_pos = None
                elif selected and puzzle[selected[0]][selected[1]] == 0:
                    if event.key == pygame.K_1:
                        board[selected[0]][selected[1]] = 1
                    elif event.key == pygame.K_2:
                        board[selected[0]][selected[1]] = 2
                    elif event.key == pygame.K_3:
                        board[selected[0]][selected[1]] = 3
                    elif event.key == pygame.K_4:
                        board[selected[0]][selected[1]] = 4
                    elif event.key == pygame.K_5:
                        board[selected[0]][selected[1]] = 5
                    elif event.key == pygame.K_6:
                        board[selected[0]][selected[1]] = 6
                    elif event.key == pygame.K_7:
                        board[selected[0]][selected[1]] = 7
                    elif event.key == pygame.K_8:
                        board[selected[0]][selected[1]] = 8
                    elif event.key == pygame.K_9:
                        board[selected[0]][selected[1]] = 9
                    elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_0:
                        board[selected[0]][selected[1]] = 0
                    
                    if board[selected[0]][selected[1]] != solution[selected[0]][selected[1]]:
                        error_pos = selected
                    else:
                        error_pos = None
        
        for i in range(10):
            if i % 3 == 0:
                pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT - 60), 3)
                pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), 3)
            else:
                pygame.draw.line(screen, GRAY, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT - 60), 1)
                pygame.draw.line(screen, GRAY, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), 1)
        
        for i in range(9):
            for j in range(9):
                if board[i][j] != 0:
                    if puzzle[i][j] != 0:
                        color = BLACK
                    elif (i, j) == error_pos:
                        color = RED
                    else:
                        color = BLUE
                    text = font.render(str(board[i][j]), True, color)
                    screen.blit(text, (j * CELL_SIZE + 20, i * CELL_SIZE + 10))
        
        if selected:
            row, col = selected
            pygame.draw.rect(screen, LIGHT_BLUE, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
        
        instruction_text = small_font.render("按1-9填入数字 | R重置 | 点击选择格子", True, BLACK)
        screen.blit(instruction_text, (10, HEIGHT - 40))
        
        if all(board[i][j] == solution[i][j] for i in range(9) for j in range(9)):
            won = True
            game_over = True
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(GREEN)
    win_text = font.render("恭喜完成数独!", True, WHITE)
    screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    sudoku()