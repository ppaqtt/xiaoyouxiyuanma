import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
CELL_SIZE = 30

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("迷宫游戏")

clock = pygame.time.Clock()

def create_maze():
    stack = []
    visited = set()
    maze = [[1 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    start_x, start_y = 0, 0
    maze[start_y][start_x] = 0
    visited.add((start_x, start_y))
    stack.append((start_x, start_y))
    
    while stack:
        x, y = stack[-1]
        neighbors = []
        
        for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in visited:
                neighbors.append((nx, ny))
        
        if neighbors:
            nx, ny = random.choice(neighbors)
            visited.add((nx, ny))
            maze[(y + ny) // 2][(x + nx) // 2] = 0
            maze[ny][nx] = 0
            stack.append((nx, ny))
        else:
            stack.pop()
    
    return maze

def draw_maze(maze, player_x, player_y):
    screen.fill(BLACK)
    
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = j * CELL_SIZE
            y = i * CELL_SIZE
            if maze[i][j] == 1:
                pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE - 1, CELL_SIZE - 1))
            else:
                pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE - 1, CELL_SIZE - 1))
    
    pygame.draw.rect(screen, GREEN, (0, 0, CELL_SIZE - 1, CELL_SIZE - 1))
    pygame.draw.rect(screen, RED, ((GRID_SIZE-1)*CELL_SIZE, (GRID_SIZE-1)*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1))
    pygame.draw.circle(screen, BLUE, 
                      (player_x*CELL_SIZE + CELL_SIZE//2, player_y*CELL_SIZE + CELL_SIZE//2), CELL_SIZE//3)

def maze_game():
    maze = create_maze()
    player_x, player_y = 0, 0
    game_over = False
    
    while not game_over:
        draw_maze(maze, player_x, player_y)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and player_y > 0 and maze[player_y-1][player_x] == 0:
                    player_y -= 1
                elif event.key == pygame.K_DOWN and player_y < GRID_SIZE-1 and maze[player_y+1][player_x] == 0:
                    player_y += 1
                elif event.key == pygame.K_LEFT and player_x > 0 and maze[player_y][player_x-1] == 0:
                    player_x -= 1
                elif event.key == pygame.K_RIGHT and player_x < GRID_SIZE-1 and maze[player_y][player_x+1] == 0:
                    player_x += 1
                
                if player_x == GRID_SIZE-1 and player_y == GRID_SIZE-1:
                    game_over = True
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(GREEN)
    font = pygame.font.Font(None, 50)
    win_text = font.render("恭喜过关!", True, BLACK)
    screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(2000)
    pygame.quit()

if __name__ == "__main__":
    maze_game()