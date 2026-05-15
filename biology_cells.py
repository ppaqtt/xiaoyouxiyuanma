import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("细胞探索")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 150, 255)
GREEN = (0, 200, 100)
RED = (200, 50, 50)
YELLOW = (255, 200, 50)

cell_parts = [
    {"name": "细胞核", "color": RED, "x": 400, "y": 300, "radius": 30},
    {"name": "细胞膜", "color": BLUE, "x": 400, "y": 300, "radius": 100},
    {"name": "线粒体", "color": YELLOW, "x": 350, "y": 250, "radius": 15},
    {"name": "叶绿体", "color": GREEN, "x": 450, "y": 350, "radius": 20},
    {"name": "高尔基体", "color": (255, 100, 200), "x": 320, "y": 350, "radius": 18}
]

class CellGame:
    def __init__(self):
        self.score = 0
        self.current_part = None
        self.selected_part = None
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.next_question()

    def next_question(self):
        self.current_part = random.choice(cell_parts)
        self.selected_part = None

    def draw(self):
        screen.fill(BLACK)
        
        for part in cell_parts:
            pygame.draw.circle(screen, part["color"], (part["x"], part["y"]), part["radius"])
        
        question_text = self.font.render(f"问题: 找到{self.current_part['name']}", True, WHITE)
        screen.blit(question_text, (50, 30))
        
        score_text = self.small_font.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (50, 70))
        
        hint_text = self.small_font.render(f"提示: {self.current_part['name']}的颜色是特定的", True, (100, 100, 100))
        screen.blit(hint_text, (50, 560))

    def handle_click(self, pos):
        for part in cell_parts:
            distance = ((pos[0] - part["x"])**2 + (pos[1] - part["y"])**2)**0.5
            if distance < part["radius"] + 10:
                if part["name"] == self.current_part["name"]:
                    self.score += 10
                else:
                    self.score -= 5
                self.next_question()
                break

game = CellGame()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            game.handle_click(pygame.mouse.get_pos())
    
    game.draw()
    pygame.display.flip()

pygame.quit()