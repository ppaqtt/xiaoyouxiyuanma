import pygame
import random
import time

pygame.init()

WIDTH, HEIGHT = 600, 700

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
pygame.display.set_caption("颜色记忆挑战")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 50)
big_font = pygame.font.Font(None, 80)

class Button:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 80
        self.color = color
        self.pressed = False
        self.show = False
    
    def draw(self):
        if self.show:
            pygame.draw.rect(screen, self.color, 
                           (self.x, self.y, self.width, self.height), border_radius=10)
        else:
            pygame.draw.rect(screen, WHITE, 
                           (self.x, self.y, self.width, self.height), border_radius=10)

def color_memory():
    grid_size = 4
    buttons = []
    
    for i in range(grid_size):
        for j in range(grid_size):
            x = 100 + j * 100
            y = 150 + i * 100
            buttons.append(Button(x, y, COLORS[i * grid_size + j]))
    
    sequence = []
    level = 1
    score = 0
    input_index = 0
    showing = True
    game_over = False
    waiting_for_input = False
    
    def add_to_sequence():
        sequence.append(random.choice(buttons))
        for btn in buttons:
            btn.show = False
        showing = True
        time.sleep(0.5)
    
    add_to_sequence()
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if waiting_for_input:
                    x, y = event.pos
                    for btn in buttons:
                        if (btn.x <= x <= btn.x + btn.width and
                            btn.y <= y <= btn.y + btn.height and btn.show):
                            if btn == sequence[input_index]:
                                score += 10 * level
                                input_index += 1
                                btn.show = False
                                
                                if input_index >= len(sequence):
                                    level += 1
                                    score += 50
                                    input_index = 0
                                    add_to_sequence()
                            else:
                                game_over = True
        
        if showing and waiting_for_input == False:
            for btn in sequence[:input_index]:
                btn.show = False
            
            for btn in sequence:
                btn.show = True
                pygame.display.update()
                time.sleep(0.8)
                btn.show = False
                pygame.display.update()
                time.sleep(0.3)
            
            showing = False
            waiting_for_input = True
        
        for btn in buttons:
            btn.draw()
        
        level_text = font.render(f"等级: {level}", True, WHITE)
        screen.blit(level_text, (10, 10))
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH - 150, 10))
        
        if waiting_for_input:
            instruction_text = font.render(f"按顺序点击 ({input_index}/{len(sequence)})", True, WHITE)
            screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, 80))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    result_text = font.render(f"游戏结束! 最终等级: {level} 得分: {score}", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    color_memory()