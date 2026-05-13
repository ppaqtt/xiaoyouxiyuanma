import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = {
    'up': (255, 0, 0),
    'down': (0, 255, 0),
    'left': (255, 255, 0),
    'right': (0, 0, 255),
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simon Says")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)
big_font = pygame.font.Font(None, 60)

class SimonButton:
    def __init__(self, direction, x, y, color):
        self.direction = direction
        self.x = x
        self.y = y
        self.width = 250
        self.height = 250
        self.color = color
        self.active = False
    
    def draw(self):
        color = WHITE if self.active else self.color
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), border_radius=20)
    
    def contains(self, pos):
        return (self.x <= pos[0] <= self.x + self.width and
                self.y <= pos[1] <= self.y + self.height)

def simon_says():
    buttons = [
        SimonButton('up', 25, 25, COLORS['up']),
        SimonButton('down', 25, 325, COLORS['down']),
        SimonButton('left', 325, 25, COLORS['left']),
        SimonButton('right', 325, 325, COLORS['right']),
    ]
    
    sequence = []
    level = 1
    score = 0
    index = 0
    showing = True
    game_over = False
    
    def add_to_sequence():
        sequence.append(random.choice(buttons))
        for btn in buttons:
            btn.active = False
    
    add_to_sequence()
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    sequence = []
                    level = 1
                    score = 0
                    index = 0
                    showing = True
                    add_to_sequence()
            elif event.type == pygame.MOUSEBUTTONDOWN and not showing:
                mouse_pos = pygame.mouse.get_pos()
                for btn in buttons:
                    if btn.contains(mouse_pos):
                        btn.active = True
                        if btn == sequence[index]:
                            score += 10 * level
                            index += 1
                            
                            if index >= len(sequence):
                                level += 1
                                score += 50
                                index = 0
                                showing = True
                                add_to_sequence()
                        else:
                            game_over = True
        
        if showing:
            for i, btn in enumerate(sequence):
                pygame.time.wait(500)
                btn.active = True
                pygame.display.update()
                pygame.time.wait(500)
                btn.active = False
                pygame.display.update()
            
            showing = False
            index = 0
        
        for btn in buttons:
            btn.draw()
        
        level_text = font.render(f"等级: {level}", True, WHITE)
        screen.blit(level_text, (10, 10))
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH - 120, 10))
        
        if showing:
            instruction_text = font.render("记住顺序...", True, WHITE)
        else:
            instruction_text = font.render(f"点击 ({index}/{len(sequence)})", True, WHITE)
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, HEIGHT//2 - 300))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(BLACK)
    result_text = font.render(f"游戏结束! 等级: {level} 得分: {score}", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2))
    
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    simon_says()