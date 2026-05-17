import pygame
import os

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

WIDTH, HEIGHT = 600, 600
GRID_SIZE = 15
CELL_SIZE = 40

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (180, 130, 80)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("五子棋")

clock = pygame.time.Clock()
font = get_chinese_font(30)

def create_board():
    return [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def draw_board(board):
    screen.fill(BROWN)
    
    for i in range(GRID_SIZE):
        pygame.draw.line(screen, BLACK, (CELL_SIZE, CELL_SIZE * (i + 1)), 
                         (WIDTH - CELL_SIZE, CELL_SIZE * (i + 1)), 1)
        pygame.draw.line(screen, BLACK, (CELL_SIZE * (i + 1), CELL_SIZE), 
                         (CELL_SIZE * (i + 1), HEIGHT - CELL_SIZE), 1)
    
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if board[i][j] == 1:
                pygame.draw.circle(screen, BLACK, 
                                  (CELL_SIZE * (j + 1), CELL_SIZE * (i + 1)), 15)
            elif board[i][j] == 2:
                pygame.draw.circle(screen, WHITE, 
                                  (CELL_SIZE * (j + 1), CELL_SIZE * (i + 1)), 15)

def check_winner(board, player):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if board[i][j] == player:
                for di, dj in directions:
                    count = 1
                    for k in range(1, 5):
                        ni, nj = i + di * k, j + dj * k
                        if 0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE and board[ni][nj] == player:
                            count += 1
                        else:
                            break
                    if count >= 5:
                        return True
    return False

def gomoku():
    board = create_board()
    current_player = 1
    game_over = False
    winner = None
    
    while not game_over:
        draw_board(board)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = pygame.mouse.get_pos()
                col = round(x / CELL_SIZE) - 1
                row = round(y / CELL_SIZE) - 1
                
                if 0 <= col < GRID_SIZE and 0 <= row < GRID_SIZE and board[row][col] == 0:
                    board[row][col] = current_player
                    
                    if check_winner(board, current_player):
                        winner = current_player
                        game_over = True
                    else:
                        current_player = 2 if current_player == 1 else 1
        
        pygame.display.update()
        clock.tick(30)
    
    if winner is not None:
        winner_text = "黑棋获胜!" if winner == 1 else "白棋获胜!"
        text = font.render(winner_text, True, BLACK)
    else:
        text = font.render("平局!", True, BLACK)
    
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 20))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    gomoku()