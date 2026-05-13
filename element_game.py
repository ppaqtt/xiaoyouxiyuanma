"""
元素周期表小游戏
学习化学元素
"""

import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 950, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("元素周期表小游戏")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 120, 200)
RED = (220, 60, 60)
GREEN = (0, 180, 100)
YELLOW = (255, 220, 0)
PURPLE = (150, 50, 200)

elements = [
    ("H", "氢", 1),
    ("He", "氦", 2),
    ("Li", "锂", 3),
    ("Be", "铍", 4),
    ("B", "硼", 5),
    ("C", "碳", 6),
    ("N", "氮", 7),
    ("O", "氧", 8),
    ("F", "氟", 9),
    ("Ne", "氖", 10),
    ("Na", "钠", 11),
    ("Mg", "镁", 12),
    ("Al", "铝", 13),
    ("Si", "硅", 14),
    ("P", "磷", 15),
    ("S", "硫", 16),
    ("Cl", "氯", 17),
    ("Ar", "氩", 18),
    ("K", "钾", 19),
    ("Ca", "钙", 20)
]

class ElementGame:
    def __init__(self):
        self.phase = "menu"
        self.score = 0
        self.current_element = None
        self.options = []
        self.font_large = pygame.font.Font(None, 60)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 26)
        self.next_question()
    
    def next_question(self):
        self.current_element = random.choice(elements)
        self.options = [self.current_element]
        
        while len(self.options) < 4:
            el = random.choice(elements)
            if el not in self.options:
                self.options.append(el)
        
        random.shuffle(self.options)
    
    def draw(self):
        screen.fill((240, 245, 255))
        
        if self.phase == "menu":
            self.draw_menu()
        elif self.phase == "game":
            self.draw_game()
        
        pygame.display.flip()
    
    def draw_menu(self):
        title = self.font_large.render("元素周期表小游戏", True, BLUE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        instructions = [
            "学习化学元素!",
            "根据符号猜中文名称",
            "",
            "按 空格键 开始!"
        ]
        
        y = 230
        for line in instructions:
            text = self.font_medium.render(line, True, BLACK)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 45
    
    def draw_game(self):
        # 标题
        pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, 70))
        title = self.font_large.render(f"分数: {self.score}", True, WHITE)
        screen.blit(title, (30, 15))
        
        # 问题
        question = f"{self.current_element[0]} 的中文名称是?"
        q_text = self.font_large.render(question, True, BLACK)
        screen.blit(q_text, (WIDTH//2 - q_text.get_width()//2, 150))
        
        num_text = self.font_small.render(f"原子序数: {self.current_element[2]}", True, GRAY)
        screen.blit(num_text, (WIDTH//2 - num_text.get_width()//2, 200))
        
        # 选项
        colors = [RED, BLUE, GREEN, PURPLE]
        for i, opt in enumerate(self.options):
            x = 100 + (i % 2) * 400
            y = 280 + (i // 2) * 120
            
            btn = pygame.Rect(x, y, 350, 90)
            pygame.draw.rect(screen, colors[i], btn, border_radius=15)
            pygame.draw.rect(screen, WHITE, btn, 3, border_radius=15)
            
            text = self.font_medium.render(opt[1], True, WHITE)
            screen.blit(text, (x + 150 - text.get_width()//2, y + 25))
    
    def handle_click(self, pos):
        if self.phase != "game":
            return
        
        for i, opt in enumerate(self.options):
            x = 100 + (i % 2) * 400
            y = 280 + (i // 2) * 120
            btn = pygame.Rect(x, y, 350, 90)
            
            if btn.collidepoint(pos):
                if opt == self.current_element:
                    self.score += 10
                else:
                    self.score = max(0, self.score - 5)
                self.next_question()
    
    def handle_key(self, key):
        if self.phase == "menu":
            if key == pygame.K_SPACE:
                self.phase = "game"

def main():
    game = ElementGame()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    game.handle_key(event.key)
        
        game.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
