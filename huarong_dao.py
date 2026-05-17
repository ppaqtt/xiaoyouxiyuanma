import pygame
import os

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

WIDTH, HEIGHT = 400, 500
CELL_WIDTH = 80
CELL_HEIGHT = 50

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("华容道")

clock = pygame.time.Clock()
font = get_chinese_font(30)

BLOCKS = [
    {'x': 0, 'y': 0, 'w': 2, 'h': 2, 'color': RED, 'name': '曹操'},
    {'x': 0, 'y': 2, 'w': 2, 'h': 1, 'color': BLUE, 'name': '关羽'},
    {'x': 2, 'y': 0, 'w': 1, 'h': 2, 'color': GREEN, 'name': '张飞'},
    {'x': 3, 'y': 0, 'w': 1, 'h': 2, 'color': YELLOW, 'name': '赵云'},
    {'x': 2, 'y': 2, 'w': 1, 'h': 2, 'color': (255, 165, 0), 'name': '马超'},
    {'x': 3, 'y': 2, 'w': 1, 'h': 2, 'color': (128, 0, 128), 'name': '黄忠'},
    {'x': 0, 'y': 4, 'w': 1, 'h': 1, 'color': WHITE, 'name': '兵1'},
    {'x': 1, 'y': 4, 'w': 1, 'h': 1, 'color': WHITE, 'name': '兵2'},
    {'x': 2, 'y': 4, 'w': 1, 'h': 1, 'color': WHITE, 'name': '兵3'},
    {'x': 3, 'y': 4, 'w': 1, 'h': 1, 'color': WHITE, 'name': '兵4'},
]

WIN_STATE = [
    {'x': 1, 'y': 3, 'w': 2, 'h': 2, 'color': RED, 'name': '曹操'},
]

def draw_blocks(blocks):
    screen.fill(BLACK)
    
    pygame.draw.rect(screen, WHITE, (0, 2*CELL_HEIGHT, WIDTH, 2*CELL_HEIGHT), 2)
    
    for block in blocks:
        x = block['x'] * CELL_WIDTH + 5
        y = block['y'] * CELL_HEIGHT + 5
        w = block['w'] * CELL_WIDTH - 10
        h = block['h'] * CELL_HEIGHT - 10
        pygame.draw.rect(screen, block['color'], (x, y, w, h), border_radius=5)
        pygame.draw.rect(screen, WHITE, (x, y, w, h), 2, border_radius=5)

def can_move(blocks, block, dx, dy):
    new_x = block['x'] + dx
    new_y = block['y'] + dy
    
    if new_x < 0 or new_x + block['w'] > 4 or new_y < 0 or new_y + block['h'] > 5:
        return False
    
    for other in blocks:
        if other == block:
            continue
        if (new_x < other['x'] + other['w'] and
            new_x + block['w'] > other['x'] and
            new_y < other['y'] + other['h'] and
            new_y + block['h'] > other['y']):
            return False
    
    return True

def huarong_dao():
    blocks = [b.copy() for b in BLOCKS]
    moves = 0
    selected = None
    game_over = False
    
    while not game_over:
        draw_blocks(blocks)
        
        moves_text = font.render(f"步数: {moves}", True, WHITE)
        screen.blit(moves_text, (10, 10))
        
        instruction_text = font.render("点击选择 | 方向键移动 | R重置", True, WHITE)
        screen.blit(instruction_text, (10, HEIGHT - 30))
        
        if selected is not None:
            block = blocks[selected]
            x = block['x'] * CELL_WIDTH + 5
            y = block['y'] * CELL_HEIGHT + 5
            w = block['w'] * CELL_WIDTH - 10
            h = block['h'] * CELL_HEIGHT - 10
            pygame.draw.rect(screen, WHITE, (x, y, w, h), 3, border_radius=5)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = x // CELL_WIDTH
                row = y // CELL_HEIGHT
                
                selected = None
                for i, block in enumerate(blocks):
                    if (block['x'] <= col < block['x'] + block['w'] and
                        block['y'] <= row < block['y'] + block['h']):
                        selected = i
                        break
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    blocks = [b.copy() for b in BLOCKS]
                    moves = 0
                    selected = None
                    continue
                
                if selected is not None:
                    dx, dy = 0, 0
                    if event.key == pygame.K_UP:
                        dy = -1
                    elif event.key == pygame.K_DOWN:
                        dy = 1
                    elif event.key == pygame.K_LEFT:
                        dx = -1
                    elif event.key == pygame.K_RIGHT:
                        dx = 1
                    
                    if dx != 0 or dy != 0:
                        if can_move(blocks, blocks[selected], dx, dy):
                            blocks[selected]['x'] += dx
                            blocks[selected]['y'] += dy
                            moves += 1
                            
                            if (blocks[selected]['name'] == '曹操' and
                                blocks[selected]['x'] == 1 and
                                blocks[selected]['y'] == 3):
                                game_over = True
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(GREEN)
    win_text = font.render(f"恭喜通关! 步数: {moves}", True, WHITE)
    screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    huarong_dao()