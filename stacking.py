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

WIDTH, HEIGHT = 400, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (100, 100, 200)
RED = (200, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("叠杯子")

clock = pygame.time.Clock()
font = get_chinese_font(40)

class Block:
    def __init__(self, x, y, width, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = 40
        self.color = color
    
    def draw(self):
        pygame.draw.rect(screen, self.color,
            (self.x, self.y, self.width, self.height), border_radius=5)

def stacking():
    blocks = []
    current_block = Block(WIDTH // 2 - 50, 100, 100, GREEN)
    dx = 3
    stack_y = HEIGHT - 40
    score = 0
    game_over = False
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    new_width = current_block.width
                    
                    if blocks:
                        top_block = blocks[-1]
                        
                        if (current_block.x > top_block.x + top_block.width or
                            current_block.x + current_block.width < top_block.x):
                            game_over = True
                            continue
                        
                        left = max(current_block.x, top_block.x)
                        right = min(current_block.x + current_block.width, top_block.x + top_block.width)
                        new_width = right - left
                        
                        if new_width <= 0:
                            game_over = True
                            continue
                        
                        current_block.x = left
                        current_block.width = new_width
                    
                    blocks.append(current_block)
                    
                    stack_y -= 50
                    
                    if stack_y < 150:
                        for block in blocks:
                            block.y += 50
                        stack_y += 50
                    
                    colors = [GREEN, BLUE, RED, (255, 165, 0), (255, 0, 255)]
                    current_block = Block(WIDTH // 2 - 50, 100, new_width, colors[len(blocks) % 5])
                    score += 10
        
        current_block.x += dx
        if current_block.x <= 0 or current_block.x + current_block.width >= WIDTH:
            dx *= -1
        
        for block in blocks:
            block.draw()
        
        current_block.draw()
        
        pygame.draw.line(screen, WHITE, (0, stack_y + 40), (WIDTH, stack_y + 40), 2)
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    game_over_text = font.render(f"游戏结束! 得分: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    stacking()