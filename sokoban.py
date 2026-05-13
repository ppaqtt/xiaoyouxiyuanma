import pygame

pygame.init()

WIDTH, HEIGHT = 500, 500
CELL_SIZE = 50
GRID_SIZE = 10

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
RED = (255, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("推箱子")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)

LEVEL = [
    [1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1],
]

def create_level():
    level = [row[:] for row in LEVEL]
    player_pos = (2, 5)
    box_pos = [(4, 4), (5, 5), (4, 6)]
    target_pos = [(7, 3), (7, 5), (7, 7)]
    return level, player_pos, box_pos, target_pos

def draw_board(level, player_pos, box_pos, target_pos):
    screen.fill(BLACK)
    
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = j * CELL_SIZE
            y = i * CELL_SIZE
            if level[i][j] == 1:
                pygame.draw.rect(screen, BROWN, (x, y, CELL_SIZE - 1, CELL_SIZE - 1))
            else:
                pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE - 1, CELL_SIZE - 1))
    
    for tx, ty in target_pos:
        pygame.draw.circle(screen, GREEN, (tx * CELL_SIZE + CELL_SIZE // 2, ty * CELL_SIZE + CELL_SIZE // 2), 15)
    
    for bx, by in box_pos:
        pygame.draw.rect(screen, BLUE, (bx * CELL_SIZE + 5, by * CELL_SIZE + 5, CELL_SIZE - 10, CELL_SIZE - 10))
    
    px, py = player_pos
    pygame.draw.circle(screen, RED, (px * CELL_SIZE + CELL_SIZE // 2, py * CELL_SIZE + CELL_SIZE // 2), 15)

def sokoban():
    level, player_pos, box_pos, target_pos = create_level()
    moves = 0
    game_over = False
    
    while not game_over:
        draw_board(level, player_pos, box_pos, target_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                elif event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                elif event.key == pygame.K_r:
                    level, player_pos, box_pos, target_pos = create_level()
                    moves = 0
                    continue
                
                if dx != 0 or dy != 0:
                    new_x = player_pos[0] + dx
                    new_y = player_pos[1] + dy
                    
                    if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and level[new_y][new_x] == 0:
                        if (new_x, new_y) in box_pos:
                            box_new_x = new_x + dx
                            box_new_y = new_y + dy
                            
                            if 0 <= box_new_x < GRID_SIZE and 0 <= box_new_y < GRID_SIZE and \
                               level[box_new_y][box_new_x] == 0 and (box_new_x, box_new_y) not in box_pos:
                                box_pos = [(bx + dx if bx == new_x and by == new_y else bx,
                                           by + dy if bx == new_x and by == new_y else by)
                                          for bx, by in box_pos]
                                player_pos = (new_x, new_y)
                                moves += 1
                        else:
                            player_pos = (new_x, new_y)
                            moves += 1
                
                if all((bx, by) in target_pos for bx, by in box_pos):
                    game_over = True
        
        moves_text = font.render(f"步数: {moves}", True, WHITE)
        screen.blit(moves_text, (10, 10))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(GREEN)
    win_text = font.render(f"恭喜通关! 步数: {moves}", True, BLACK)
    screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    sokoban()