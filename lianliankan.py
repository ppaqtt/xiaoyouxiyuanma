import pygame
import random

pygame.init()

WIDTH, HEIGHT = 500, 550
GRID_SIZE = 8
CELL_SIZE = 60
MARGIN = (WIDTH - GRID_SIZE * CELL_SIZE) // 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
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
pygame.display.set_caption("连连看")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)

def create_board():
    pairs = GRID_SIZE * GRID_SIZE // 2
    board = []
    symbols = []
    
    for i in range(pairs):
        color_idx = i % len(COLORS)
        symbols.extend([color_idx, color_idx])
    
    random.shuffle(symbols)
    
    for i in range(GRID_SIZE):
        row = []
        for j in range(GRID_SIZE):
            idx = i * GRID_SIZE + j
            if idx < len(symbols):
                row.append(symbols[idx])
            else:
                row.append(-1)
        board.append(row)
    
    return board

def can_connect(board, r1, c1, r2, c2):
    if board[r1][c1] == -1 or board[r2][c2] == -1:
        return False
    if board[r1][c1] != board[r2][c2]:
        return False
    if r1 == r2 and c1 == c2:
        return False
    
    return True

def lianliankan():
    board = create_board()
    selected = None
    score = 0
    moves = 0
    game_over = False
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = (x - MARGIN) // CELL_SIZE
                row = (y - MARGIN) // CELL_SIZE
                
                if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                    if selected is None:
                        if board[row][col] != -1:
                            selected = (row, col)
                    else:
                        if can_connect(board, selected[0], selected[1], row, col):
                            board[selected[0]][selected[1]] = -1
                            board[row][col] = -1
                            score += 10
                            moves += 1
                        selected = None
        
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x = MARGIN + j * CELL_SIZE
                y = MARGIN + i * CELL_SIZE
                
                if board[i][j] != -1:
                    pygame.draw.rect(screen, COLORS[board[i][j]],
                        (x + 5, y + 5, CELL_SIZE - 10, CELL_SIZE - 10), border_radius=5)
                    pygame.draw.rect(screen, WHITE,
                        (x + 5, y + 5, CELL_SIZE - 10, CELL_SIZE - 10), 2, border_radius=5)
                
                if selected is not None and selected == (i, j):
                    pygame.draw.rect(screen, WHITE,
                        (x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4), 3, border_radius=5)
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        moves_text = font.render(f"步数: {moves}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(moves_text, (WIDTH - 100, 10))
        
        remaining = sum(1 for row in board for cell in row if cell != -1)
        remaining_text = font.render(f"剩余: {remaining}", True, WHITE)
        screen.blit(remaining_text, (WIDTH // 2 - 40, HEIGHT - 40))
        
        if remaining == 0:
            game_over = True
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    win_text = font.render(f"恭喜通关! 得分: {score} 步数: {moves}", True, WHITE)
    screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    lianliankan()