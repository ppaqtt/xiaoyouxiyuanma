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

WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 28

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (0, 0, 0),      # 黑色
    (255, 255, 255),# 白色
    (255, 0, 0),    # 红色
    (0, 255, 0),    # 绿色
    (0, 0, 255),    # 蓝色
    (255, 255, 0),  # 黄色
    (255, 0, 255),  # 紫色
    (0, 255, 255),  # 青色
    (255, 165, 0),  # 橙色
    (128, 0, 128),  # 深紫
    (128, 128, 128),# 灰色
    (0, 128, 0),    # 深绿
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("像素绘画板")

clock = pygame.time.Clock()
font = get_chinese_font(24)

def pixel_art():
    grid = [[WHITE for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    current_color = BLACK
    drawing = False
    last_pos = None
    brush_size = 1
    
    def clear_grid():
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                grid[y][x] = WHITE
    
    def random_grid():
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                grid[y][x] = random.choice(COLORS)
    
    while True:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    clear_grid()
                elif event.key == pygame.K_r:
                    random_grid()
                elif event.key == pygame.K_UP:
                    brush_size = min(5, brush_size + 1)
                elif event.key == pygame.K_DOWN:
                    brush_size = max(1, brush_size - 1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    drawing = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drawing = False
                    last_pos = None
            elif event.type == pygame.MOUSEMOTION and drawing:
                x, y = event.pos
                grid_x = (x - 50) // GRID_SIZE
                grid_y = (y - 50) // GRID_SIZE
                
                if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                    for dy in range(-brush_size + 1, brush_size):
                        for dx in range(-brush_size + 1, brush_size):
                            nx, ny = grid_x + dx, grid_y + dy
                            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                                grid[ny][nx] = current_color
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(50 + x * GRID_SIZE, 50 + y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1)
                pygame.draw.rect(screen, grid[y][x], rect)
        
        palette_y = HEIGHT - 60
        for i, color in enumerate(COLORS):
            rect = pygame.Rect(50 + i * 30, palette_y, 25, 25)
            pygame.draw.rect(screen, color, rect)
            
            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                if rect.collidepoint(mx, my):
                    current_color = color
        
        pygame.draw.circle(screen, current_color, (50, 30), 15)
        pygame.draw.circle(screen, BLACK, (50, 30), 15, 2)
        
        size_text = font.render(f"笔刷: {brush_size} (↑↓调整)", True, BLACK)
        screen.blit(size_text, (100, 25))
        
        instruction_text = font.render("C-清空 | R-随机 | 点击选择颜色", True, BLACK)
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, 10))
        
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    pixel_art()