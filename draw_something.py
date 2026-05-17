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

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("画图猜词")

clock = pygame.time.Clock()
font = get_chinese_font(40)

DRAWING_TOOLS = ['circle', 'rectangle', 'line']
COLORS = [RED, GREEN, BLUE, YELLOW, WHITE, (255, 165, 0), (128, 0, 128)]

class Drawer:
    def __init__(self):
        self.drawing = False
        self.start_pos = None
        self.shapes = []
        self.current_color = WHITE
        self.current_tool = 'circle'
        self.current_size = 5
    
    def add_shape(self, shape_type, start, end, color, size):
        self.shapes.append({
            'type': shape_type,
            'start': start,
            'end': end,
            'color': color,
            'size': size
        })
    
    def draw_shapes(self):
        for shape in self.shapes:
            if shape['type'] == 'circle':
                radius = int(((shape['end'][0] - shape['start'][0])**2 + 
                           (shape['end'][1] - shape['start'][1])**2)**0.5)
                pygame.draw.circle(screen, shape['color'], shape['start'], radius, shape['size'])
            elif shape['type'] == 'rectangle':
                rect = pygame.Rect(min(shape['start'][0], shape['end'][0]),
                                 min(shape['start'][1], shape['end'][1]),
                                 abs(shape['end'][0] - shape['start'][0]),
                                 abs(shape['end'][1] - shape['start'][1]))
                pygame.draw.rect(screen, shape['color'], rect, shape['size'])
            elif shape['type'] == 'line':
                pygame.draw.line(screen, shape['color'], shape['start'], shape['end'], shape['size'])

WORDS = [
    "HOUSE", "TREE", "CAT", "DOG", "CAR", "SUN", "MOON", "STAR",
    "BIRD", "FISH", "APPLE", "FLOWER", "MOUNTAIN", "RIVER", "CLOUD"
]

def draw_something():
    drawer = Drawer()
    current_word = random.choice(WORDS)
    score = 0
    time_left = 120
    game_over = False
    start_ticks = pygame.time.get_ticks()
    
    pygame.font.init()
    
    while not game_over:
        screen.fill(BLACK)
        
        seconds = max(0, 120 - (pygame.time.get_ticks() - start_ticks) // 1000)
        if seconds == 0:
            game_over = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    drawer.shapes = []
                    current_word = random.choice(WORDS)
                elif event.key == pygame.K_c:
                    drawer.current_color = random.choice(COLORS)
                elif event.key == pygame.K_1:
                    drawer.current_tool = 'circle'
                elif event.key == pygame.K_2:
                    drawer.current_tool = 'rectangle'
                elif event.key == pygame.K_3:
                    drawer.current_tool = 'line'
                elif event.key == pygame.K_s:
                    drawer.current_size = max(1, drawer.current_size - 1)
                elif event.key == pygame.K_b:
                    drawer.current_size = min(20, drawer.current_size + 1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                drawer.drawing = True
                drawer.start_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if drawer.drawing and drawer.start_pos:
                    drawer.add_shape(drawer.current_tool, drawer.start_pos, event.pos,
                                  drawer.current_color, drawer.current_size)
                    drawer.drawing = False
                    drawer.start_pos = None
        
        drawer.draw_shapes()
        
        word_hint = font.render(f"提示: {current_word}", True, GREEN)
        screen.blit(word_hint, (10, 10))
        
        tool_text = font.render(f"工具: {drawer.current_tool} (1-3切换)", True, WHITE)
        screen.blit(tool_text, (10, 50))
        
        color_text = font.render(f"颜色: {drawer.current_color} (C换)", True, WHITE)
        screen.blit(color_text, (10, 90))
        
        size_text = font.render(f"粗细: {drawer.current_size} (S/B调)", True, WHITE)
        screen.blit(size_text, (10, 130))
        
        time_text = font.render(f"时间: {seconds}秒", True, WHITE)
        screen.blit(time_text, (WIDTH - 120, 10))
        
        instruction_text = font.render("鼠标画画 | R重置 | C换色 | 1-3工具 | S/B粗细", True, WHITE)
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, HEIGHT - 30))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    result_text = font.render("时间到! 继续画...", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    draw_something()