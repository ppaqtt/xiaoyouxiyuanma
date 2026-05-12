import pygame
import random

pygame.init()

WIDTH, HEIGHT = 500, 700
COLS = 10
ROW_HEIGHT = 30
CELL_SIZE = WIDTH // COLS

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (255, 0, 0),    # 红
    (0, 255, 0),    # 绿
    (0, 0, 255),    # 蓝
    (255, 255, 0),  # 黄
    (255, 0, 255),  # 紫
    (0, 255, 255),  # 青
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("泡泡龙")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)

def create_board():
    board = []
    for row in range(5):
        board_row = []
        offset = 0 if row % 2 == 0 else CELL_SIZE // 2
        for col in range(COLS):
            if col < COLS - (row % 2):
                board_row.append(random.randint(0, len(COLORS) - 1))
            else:
                board_row.append(-1)
        board.append(board_row)
    return board

def draw_board(board, shoot_y, shoot_x, angle, current_color):
    screen.fill(BLACK)
    
    for row_idx, row in enumerate(board):
        offset = 0 if row_idx % 2 == 0 else CELL_SIZE // 2
        for col_idx, color_idx in enumerate(row):
            if color_idx >= 0:
                x = col_idx * CELL_SIZE + offset + CELL_SIZE // 2
                y = row_idx * ROW_HEIGHT + ROW_HEIGHT // 2
                pygame.draw.circle(screen, COLORS[color_idx], (x, y), ROW_HEIGHT // 2 - 2)
    
    pygame.draw.line(screen, WHITE, (0, HEIGHT - 150), (WIDTH, HEIGHT - 150), 2)
    
    shooter_x = WIDTH // 2
    shooter_y = HEIGHT - 80
    pygame.draw.circle(screen, COLORS[current_color], (shooter_x, shooter_y), 15)
    
    end_x = shooter_x + 200 * -1 * (1 if angle < 90 else -1) * abs((90 - angle) / 90)
    end_y = shooter_y - 200 * abs((90 - angle) / 90)
    pygame.draw.line(screen, WHITE, (shooter_x, shooter_y), (end_x, end_y), 2)

def find_matches(board, row, col):
    color = board[row][col]
    if color < 0:
        return []
    
    matches = [(row, col)]
    stack = [(row, col)]
    visited = {(row, col)}
    
    while stack:
        r, c = stack.pop()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if (nr, nc) not in visited:
                if 0 <= nr < len(board) and 0 <= nc < len(board[nr]) and board[nr][nc] == color:
                    visited.add((nr, nc))
                    matches.append((nr, nc))
                    stack.append((nr, nc))
    
    return matches

def bubble_shooter():
    board = create_board()
    score = 0
    game_over = False
    current_color = random.randint(0, len(COLORS) - 1)
    angle = 90
    
    while not game_over:
        draw_board(board, 0, 0, angle, current_color)
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        controls_text = font.render("← →调整角度 | 空格射击 | R重新开始", True, WHITE)
        screen.blit(controls_text, (10, HEIGHT - 30))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    angle = min(180, angle + 10)
                elif event.key == pygame.K_RIGHT:
                    angle = max(0, angle - 10)
                elif event.key == pygame.K_SPACE:
                    pass
                elif event.key == pygame.K_r:
                    board = create_board()
                    score = 0
        
        clock.tick(30)

if __name__ == "__main__":
    bubble_shooter()