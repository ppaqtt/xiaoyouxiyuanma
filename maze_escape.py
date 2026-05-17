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

WIDTH, HEIGHT = 600, 600
CELL_SIZE = 30

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("迷宫逃生")

clock = pygame.time.Clock()
font = get_chinese_font(30)

def create_maze_dfs(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)]
    
    def carve(x, y):
        maze[y][x] = 0
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1:
                maze[y + dy//2][x + dx//2] = 0
                carve(nx, ny)
    
    carve(1, 1)
    return maze

def draw_maze(maze, player_x, player_y, exit_x, exit_y):
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if maze[y][x] == 1:
                pygame.draw.rect(screen, BLACK, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1))
            else:
                pygame.draw.rect(screen, WHITE, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1))
    
    pygame.draw.rect(screen, GREEN, (exit_x*CELL_SIZE, exit_y*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1))
    pygame.draw.circle(screen, BLUE, (player_x*CELL_SIZE+CELL_SIZE//2, player_y*CELL_SIZE+CELL_SIZE//2), CELL_SIZE//3)

def maze_escape():
    maze_width = WIDTH // CELL_SIZE
    maze_height = HEIGHT // CELL_SIZE
    
    maze = create_maze_dfs(maze_width, maze_height)
    
    player_x, player_y = 1, 1
    exit_x, exit_y = maze_width - 2, maze_height - 2
    maze[exit_y][exit_x] = 0
    
    moves = 0
    time_left = 120
    game_over = False
    start_ticks = pygame.time.get_ticks()
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and player_y > 0 and maze[player_y-1][player_x] == 0:
                    player_y -= 1
                    moves += 1
                elif event.key == pygame.K_DOWN and player_y < maze_height-1 and maze[player_y+1][player_x] == 0:
                    player_y += 1
                    moves += 1
                elif event.key == pygame.K_LEFT and player_x > 0 and maze[player_y][player_x-1] == 0:
                    player_x -= 1
                    moves += 1
                elif event.key == pygame.K_RIGHT and player_x < maze_width-1 and maze[player_y][player_x+1] == 0:
                    player_x += 1
                    moves += 1
                elif event.key == pygame.K_r:
                    maze = create_maze_dfs(maze_width, maze_height)
                    maze[exit_y][exit_x] = 0
                    player_x, player_y = 1, 1
                    moves = 0
                    start_ticks = pygame.time.get_ticks()
        
        seconds = max(0, 120 - (pygame.time.get_ticks() - start_ticks) // 1000)
        if seconds == 0:
            game_over = True
        
        if player_x == exit_x and player_y == exit_y:
            game_over = True
        
        draw_maze(maze, player_x, player_y, exit_x, exit_y)
        
        moves_text = font.render(f"步数: {moves}", True, BLACK)
        screen.blit(moves_text, (10, 10))
        
        time_text = font.render(f"时间: {seconds}秒", True, BLACK)
        screen.blit(time_text, (WIDTH - 120, 10))
        
        instruction_text = font.render("方向键移动 | R重新开始", True, BLACK)
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, HEIGHT - 25))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(GREEN if player_x == exit_x and player_y == exit_y else RED)
    
    if player_x == exit_x and player_y == exit_y:
        result_text = font.render(f"成功! 步数: {moves}", True, WHITE)
    else:
        result_text = font.render(f"时间到! 步数: {moves}", True, WHITE)
    
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    maze_escape()