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
CELL_SIZE = 50
GRID_WIDTH = 8
GRID_HEIGHT = 8

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
pygame.display.set_caption("找不同")

clock = pygame.time.Clock()
font = get_chinese_font(40)
big_font = get_chinese_font(60)

def create_image():
    return [[random.randint(0, len(COLORS) - 1) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def create_difference():
    differences = []
    num_differences = random.randint(3, 5)
    while len(differences) < num_differences:
        row = random.randint(0, GRID_HEIGHT - 1)
        col = random.randint(0, GRID_WIDTH - 1)
        if (row, col) not in differences:
            differences.append((row, col))
    return differences

def draw_grid(grid, x_offset, y_offset):
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            rect = pygame.Rect(
                x_offset + j * CELL_SIZE,
                y_offset + i * CELL_SIZE,
                CELL_SIZE - 2,
                CELL_SIZE - 2
            )
            pygame.draw.rect(screen, COLORS[grid[i][j]], rect)

def spot_difference():
    image1 = create_image()
    image2 = [row[:] for row in image1]
    
    differences = create_difference()
    
    for row, col in differences:
        original_color = image1[row][col]
        new_color = (original_color + 1) % len(COLORS)
        image2[row][col] = new_color
    
    found = set()
    score = 0
    time_left = 60
    game_over = False
    
    while not game_over:
        screen.fill(BLACK)
        
        time_text = font.render(f"时间: {time_left}秒", True, WHITE)
        screen.blit(time_text, (WIDTH - 150, 10))
        
        draw_grid(image1, 50, 50)
        draw_grid(image2, WIDTH // 2 + 20, 50)
        
        label1 = font.render("原图", True, WHITE)
        label2 = font.render("修改图", True, WHITE)
        screen.blit(label1, (50 + CELL_SIZE * GRID_WIDTH // 2 - 30, 20))
        screen.blit(label2, (WIDTH // 2 + 20 + CELL_SIZE * GRID_WIDTH // 2 - 30, 20))
        
        for row, col in found:
            x1 = 50 + col * CELL_SIZE + CELL_SIZE // 2
            y1 = 50 + row * CELL_SIZE + CELL_SIZE // 2
            x2 = WIDTH // 2 + 20 + col * CELL_SIZE + CELL_SIZE // 2
            y2 = 50 + row * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(screen, WHITE, (x1, y1), 15, 3)
            pygame.draw.circle(screen, WHITE, (x2, y2), 15, 3)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                if 50 <= x <= 50 + GRID_WIDTH * CELL_SIZE:
                    col = (x - 50) // CELL_SIZE
                    row = (y - 50) // CELL_SIZE
                    if (row, col) in differences and (row, col) not in found:
                        found.add((row, col))
                        score += 20
                
                elif WIDTH // 2 + 20 <= x <= WIDTH // 2 + 20 + GRID_WIDTH * CELL_SIZE:
                    col = (x - WIDTH // 2 - 20) // CELL_SIZE
                    row = (y - 50) // CELL_SIZE
                    if (row, col) in differences and (row, col) not in found:
                        found.add((row, col))
                        score += 20
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        found_text = font.render(f"已找到: {len(found)}/{len(differences)}", True, WHITE)
        screen.blit(found_text, (10, 50))
        
        if len(found) == len(differences):
            game_over = True
            win = True
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    if win:
        result_text = big_font.render("恭喜全部找到!", True, WHITE)
    else:
        result_text = big_font.render("时间到!", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2))
    
    final_score = font.render(f"最终得分: {score}", True, WHITE)
    screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, HEIGHT//2 + 60))
    
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    spot_difference()