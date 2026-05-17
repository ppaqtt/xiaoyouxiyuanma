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

WIDTH, HEIGHT = 800, 400

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (255, 0, 0),    # 红
    (0, 255, 0),    # 绿
    (0, 0, 255),    # 蓝
    (255, 255, 0),  # 黄
    (255, 0, 255),  # 紫
    (0, 255, 255),  # 青
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("数字赛马")

clock = pygame.time.Clock()
font = get_chinese_font(30)

def number_race():
    num_horses = 6
    horses = []
    
    for i in range(num_horses):
        horses.append({
            'x': 0,
            'y': 50 + i * 55,
            'color': COLORS[i],
            'number': i + 1,
            'speed': random.uniform(2, 5)
        })
    
    finished = []
    game_over = False
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for horse in horses:
                        horse['x'] += random.randint(1, int(horse['speed'] * 10))
        
        for horse in horses[:]:
            horse['x'] += random.randint(1, int(horse['speed']))
            
            if horse['x'] >= WIDTH - 100:
                finished.append(horse)
                horses.remove(horse)
        
        for horse in horses + finished:
            pygame.draw.circle(screen, horse['color'], 
                             (50 + horse['x'], horse['y']), 20)
            number = font.render(str(horse['number']), True, WHITE)
            screen.blit(number, (45 + horse['x'], horse['y'] - 10))
        
        pygame.draw.line(screen, WHITE, (WIDTH - 50, 0), (WIDTH - 50, HEIGHT), 3)
        
        for i in range(num_horses):
            y = 50 + i * 55
            pygame.draw.line(screen, WHITE, (0, y), (WIDTH, y), 1)
        
        if len(finished) == num_horses:
            game_over = True
        
        instruction_text = font.render("按空格键加速!", True, WHITE)
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, HEIGHT - 30))
        
        position_text = font.render(f"完成: {len(finished)}/{num_horses}", True, WHITE)
        screen.blit(position_text, (10, 10))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    
    result_text = font.render("最终排名:", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - 100, 50))
    
    for i, horse in enumerate(finished):
        result_text = font.render(f"{i+1}. 马匹 {horse['number']}", True, horse['color'])
        screen.blit(result_text, (WIDTH//2 - 100, 100 + i * 40))
    
    pygame.display.update()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    number_race()