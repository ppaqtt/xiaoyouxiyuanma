import pygame
import random

pygame.init()

WIDTH, HEIGHT = 500, 500
GRID_SIZE = 3
CELL_SIZE = 150
MARGIN = (WIDTH - GRID_SIZE * CELL_SIZE) // 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
PINK = (255, 182, 193)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("打地鼠")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)

def draw_holes():
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = j * CELL_SIZE + MARGIN
            y = i * CELL_SIZE + MARGIN
            pygame.draw.ellipse(screen, BROWN, (x, y, CELL_SIZE, CELL_SIZE // 2))

def draw_mole(x, y, show):
    if show:
        mole_x = j * CELL_SIZE + MARGIN + CELL_SIZE // 2
        mole_y = i * CELL_SIZE + MARGIN + CELL_SIZE // 4
        pygame.draw.circle(screen, PINK, (int(mole_x), int(mole_y)), 30)

def whack_a_mole():
    score = 0
    time_left = 30
    game_over = False
    moles = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
    mole_timer = 0
    
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
                    if moles[row][col]:
                        score += 10
                        moles[row][col] = False
        
        mole_timer += 1
        if mole_timer > 15:
            mole_timer = 0
            i = random.randint(0, GRID_SIZE - 1)
            j = random.randint(0, GRID_SIZE - 1)
            moles[i][j] = True
            pygame.time.wait(200)
            moles[i][j] = False
        
        draw_holes()
        
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if moles[i][j]:
                    mole_x = j * CELL_SIZE + MARGIN + CELL_SIZE // 2
                    mole_y = i * CELL_SIZE + MARGIN + CELL_SIZE // 4
                    pygame.draw.circle(screen, PINK, (mole_x, mole_y), 30)
                    pygame.draw.circle(screen, BLACK, (mole_x - 10, mole_y - 5), 5)
                    pygame.draw.circle(screen, BLACK, (mole_x + 10, mole_y - 5), 5)
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    game_over_text = font.render(f"游戏结束! 得分: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(2000)
    pygame.quit()

if __name__ == "__main__":
    whack_a_mole()