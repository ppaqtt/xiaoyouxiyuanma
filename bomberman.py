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

WIDTH, HEIGHT = 630, 630
CELL_SIZE = 45
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("炸弹人")

clock = pygame.time.Clock()
font = get_chinese_font(30)

def create_map():
    map_data = []
    for i in range(GRID_HEIGHT):
        row = []
        for j in range(GRID_WIDTH):
            if i == 0 or i == GRID_HEIGHT - 1 or j == 0 or j == GRID_WIDTH - 1:
                row.append(1)
            elif i % 2 == 0 and j % 2 == 0:
                row.append(1)
            elif random.randint(1, 10) < 3:
                row.append(1)
            else:
                row.append(0)
        map_data.append(row)
    
    map_data[1][1] = 0
    map_data[1][2] = 0
    map_data[2][1] = 0
    
    return map_data

class Player:
    def __init__(self):
        self.x = 1
        self.y = 1
        self.speed = 1
    
    def move(self, dx, dy, map_data):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and map_data[new_y][new_x] == 0:
            self.x = new_x
            self.y = new_y
    
    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x * CELL_SIZE + 5, self.y * CELL_SIZE + 5, CELL_SIZE - 10, CELL_SIZE - 10))

class Bomb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 180
        self.radius = 3
    
    def update(self):
        self.timer -= 1
        return self.timer <= 0
    
    def draw(self):
        if self.timer // 30 % 2 == 0:
            color = BLUE
        else:
            color = RED
        pygame.draw.circle(screen, color, (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)

def bomberman():
    map_data = create_map()
    player = Player()
    bombs = []
    score = 0
    game_over = False
    
    while not game_over:
        screen.fill(BLACK)
        
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                if map_data[i][j] == 1:
                    pygame.draw.rect(screen, GRAY, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))
                else:
                    pygame.draw.rect(screen, BLACK, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bombs.append(Bomb(player.x, player.y))
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player.move(0, -1, map_data)
        if keys[pygame.K_DOWN]:
            player.move(0, 1, map_data)
        if keys[pygame.K_LEFT]:
            player.move(-1, 0, map_data)
        if keys[pygame.K_RIGHT]:
            player.move(1, 0, map_data)
        
        bombs_to_remove = []
        for bomb in bombs:
            if bomb.update():
                bombs_to_remove.append(bomb)
                score += 50
        
        bombs = [b for b in bombs if b not in bombs_to_remove]
        
        player.draw()
        for bomb in bombs:
            bomb.draw()
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        controls_text = font.render("方向键移动 | 空格放炸弹", True, WHITE)
        screen.blit(controls_text, (10, HEIGHT - 30))
        
        pygame.display.update()
        clock.tick(30)
    
    pygame.quit()

if __name__ == "__main__":
    bomberman()