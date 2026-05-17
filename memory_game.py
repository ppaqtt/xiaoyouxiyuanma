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

WIDTH, HEIGHT = 500, 500
GRID_SIZE = 4
CELL_SIZE = 100
CELL_PADDING = 10

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

COLORS = [
    (255, 0, 0),    # 红
    (0, 255, 0),    # 绿
    (0, 0, 255),    # 蓝
    (255, 255, 0),  # 黄
    (255, 0, 255),  # 紫
    (0, 255, 255),  # 青
    (255, 165, 0),  # 橙
    (128, 0, 128),  # 深紫
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("记忆配对游戏")

clock = pygame.time.Clock()
font = get_chinese_font(30)

def create_board():
    cards = COLORS * 2
    random.shuffle(cards)
    return [cards[i:i+GRID_SIZE] for i in range(0, len(cards), GRID_SIZE)]

def draw_board(board, revealed):
    screen.fill(BLACK)
    
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            card_x = x * (CELL_SIZE + CELL_PADDING) + CELL_PADDING
            card_y = y * (CELL_SIZE + CELL_PADDING) + CELL_PADDING
            
            if revealed[y][x]:
                pygame.draw.rect(screen, board[y][x], (card_x, card_y, CELL_SIZE, CELL_SIZE))
            else:
                pygame.draw.rect(screen, GRAY, (card_x, card_y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, WHITE, (card_x + 5, card_y + 5, CELL_SIZE - 10, CELL_SIZE - 10), 2)

def memory_game():
    board = create_board()
    revealed = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    selected = []
    matches = 0
    game_over = False
    
    while not game_over:
        draw_board(board, revealed)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = x // (CELL_SIZE + CELL_PADDING)
                row = y // (CELL_SIZE + CELL_PADDING)
                
                if 0 <= col < GRID_SIZE and 0 <= row < GRID_SIZE and not revealed[row][col]:
                    revealed[row][col] = True
                    selected.append((row, col))
                    
                    if len(selected) == 2:
                        r1, c1 = selected[0]
                        r2, c2 = selected[1]
                        
                        if board[r1][c1] == board[r2][c2]:
                            matches += 1
                            if matches == GRID_SIZE * GRID_SIZE // 2:
                                game_over = True
                        else:
                            pygame.display.update()
                            pygame.time.wait(500)
                            revealed[r1][c1] = False
                            revealed[r2][c2] = False
                        
                        selected = []
        
        clock.tick(30)
    
    screen.fill(BLACK)
    win_text = font.render("恭喜你赢了!", True, WHITE)
    screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    pygame.time.wait(2000)
    pygame.quit()

if __name__ == "__main__":
    memory_game()