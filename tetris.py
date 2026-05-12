import pygame
import random

pygame.init()

WIDTH, HEIGHT = 300, 600
GRID_SIZE = 30
COLS = WIDTH // GRID_SIZE
ROWS = HEIGHT // GRID_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),   # I
    (255, 165, 0),   # O
    (128, 0, 128),   # T
    (0, 0, 255),     # S
    (255, 0, 0),     # Z
    (0, 255, 0),     # J
    (255, 255, 0),   # L
]

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("俄罗斯方块")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)

class Piece:
    def __init__(self):
        self.type = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.type]
        self.color = COLORS[self.type]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0
    
    def rotate(self):
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        for i in range(rows):
            for j in range(cols):
                rotated[j][rows - 1 - i] = self.shape[i][j]
        self.shape = rotated

def create_board():
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

def draw_board(board):
    for y in range(ROWS):
        for x in range(COLS):
            if board[y][x]:
                pygame.draw.rect(screen, board[y][x], 
                               (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))

def draw_piece(piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, piece.color,
                               ((piece.x + x) * GRID_SIZE, (piece.y + y) * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))

def is_valid_position(board, piece, offset_x=0, offset_y=0):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = piece.x + x + offset_x
                new_y = piece.y + y + offset_y
                if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                    return False
                if new_y >= 0 and board[new_y][new_x]:
                    return False
    return True

def merge_piece(board, piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                board[piece.y + y][piece.x + x] = piece.color

def clear_lines(board):
    lines_cleared = 0
    new_board = []
    for row in board:
        if all(row):
            lines_cleared += 1
        else:
            new_board.append(row)
    for _ in range(lines_cleared):
        new_board.insert(0, [0 for _ in range(COLS)])
    return new_board, lines_cleared

def tetris():
    board = create_board()
    piece = Piece()
    score = 0
    game_over = False
    fall_time = 0
    fall_speed = 1000
    
    while not game_over:
        screen.fill(BLACK)
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and is_valid_position(board, piece, offset_x=-1):
                    piece.x -= 1
                elif event.key == pygame.K_RIGHT and is_valid_position(board, piece, offset_x=1):
                    piece.x += 1
                elif event.key == pygame.K_DOWN and is_valid_position(board, piece, offset_y=1):
                    piece.y += 1
                elif event.key == pygame.K_UP:
                    rotated_piece = Piece()
                    rotated_piece.shape = piece.shape
                    rotated_piece.rotate()
                    rotated_piece.x = piece.x
                    rotated_piece.y = piece.y
                    if is_valid_position(board, rotated_piece):
                        piece = rotated_piece
        
        if current_time - fall_time > fall_speed:
            if is_valid_position(board, piece, offset_y=1):
                piece.y += 1
            else:
                merge_piece(board, piece)
                board, lines = clear_lines(board)
                score += lines * 100
                piece = Piece()
                if not is_valid_position(board, piece):
                    game_over = True
            fall_time = current_time
        
        draw_board(board)
        draw_piece(piece)
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.update()
        clock.tick(60)
    
    game_over_text = font.render("游戏结束!", True, (255, 0, 0))
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    pygame.time.wait(2000)
    pygame.quit()

if __name__ == "__main__":
    tetris()