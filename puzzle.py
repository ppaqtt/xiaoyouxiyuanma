import pygame
import random

pygame.init()

WIDTH, HEIGHT = 450, 500
GRID_SIZE = 3
CELL_SIZE = 150

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("数字拼图")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 60)
small_font = pygame.font.Font(None, 30)

def create_board():
    numbers = list(range(1, GRID_SIZE * GRID_SIZE)) + [0]
    random.shuffle(numbers)
    return [numbers[i:i+GRID_SIZE] for i in range(0, len(numbers), GRID_SIZE)]

def find_empty(board):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if board[i][j] == 0:
                return (i, j)

def draw_board(board, moves):
    screen.fill(BLACK)
    
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = j * CELL_SIZE
            y = i * CELL_SIZE
            
            if board[i][j] != 0:
                pygame.draw.rect(screen, WHITE, (x + 5, y + 5, CELL_SIZE - 10, CELL_SIZE - 10))
                text = font.render(str(board[i][j]), True, BLUE)
                screen.blit(text, (x + CELL_SIZE // 3, y + CELL_SIZE // 3))
            else:
                pygame.draw.rect(screen, BLACK, (x + 5, y + 5, CELL_SIZE - 10, CELL_SIZE - 10))
    
    moves_text = small_font.render(f"步数: {moves}", True, WHITE)
    screen.blit(moves_text, (10, HEIGHT - 40))

def is_solved(board):
    expected = list(range(1, GRID_SIZE * GRID_SIZE)) + [0]
    flat = [num for row in board for num in row]
    return flat == expected

def puzzle():
    board = create_board()
    moves = 0
    game_over = False
    
    while not game_over:
        draw_board(board, moves)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = pygame.mouse.get_pos()
                col = x // CELL_SIZE
                row = y // CELL_SIZE
                
                if 0 <= col < GRID_SIZE and 0 <= row < GRID_SIZE:
                    empty_i, empty_j = find_empty(board)
                    
                    if (abs(row - empty_i) == 1 and col == empty_j) or \
                       (abs(col - empty_j) == 1 and row == empty_i):
                        board[empty_i][empty_j], board[row][col] = board[row][col], board[empty_i][empty_j]
                        moves += 1
                        
                        if is_solved(board):
                            game_over = True
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    win_text = font.render(f"恭喜! 步数: {moves}", True, WHITE)
    screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    puzzle()