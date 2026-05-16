import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("化学元素猜猜乐")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
YELLOW = (255, 200, 50)
ORANGE = (255, 150, 50)

elements = [
    {"symbol": "H", "name": "氢", "category": "非金属"},
    {"symbol": "He", "name": "氦", "category": "稀有气体"},
    {"symbol": "Li", "name": "锂", "category": "碱金属"},
    {"symbol": "Be", "name": "铍", "category": "碱土金属"},
    {"symbol": "B", "name": "硼", "category": "类金属"},
    {"symbol": "C", "name": "碳", "category": "非金属"},
    {"symbol": "N", "name": "氮", "category": "非金属"},
    {"symbol": "O", "name": "氧", "category": "非金属"},
    {"symbol": "F", "name": "氟", "category": "卤素"},
    {"symbol": "Ne", "name": "氖", "category": "稀有气体"},
    {"symbol": "Na", "name": "钠", "category": "碱金属"},
    {"symbol": "Mg", "name": "镁", "category": "碱土金属"},
    {"symbol": "Al", "name": "铝", "category": "金属"},
    {"symbol": "Si", "name": "硅", "category": "类金属"},
    {"symbol": "P", "name": "磷", "category": "非金属"},
    {"symbol": "S", "name": "硫", "category": "非金属"},
    {"symbol": "Cl", "name": "氯", "category": "卤素"},
    {"symbol": "Ar", "name": "氩", "category": "稀有气体"},
    {"symbol": "K", "name": "钾", "category": "碱金属"},
    {"symbol": "Ca", "name": "钙", "category": "碱土金属"},
]

category_colors = {
    "非金属": BLUE,
    "稀有气体": GREEN,
    "碱金属": YELLOW,
    "碱土金属": ORANGE,
    "类金属": (150, 50, 200),
    "金属": (100, 100, 100),
    "卤素": (255, 100, 200),
}

class ChemistryGame:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.round = 1
        self.max_rounds = 10
        self.current_element = None
        self.options = []
        self.animation_frame = 0
        self.correct_sound = None
        self.wrong_sound = None
        self.game_over = False
        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 48)
        self.next_question()

    def next_question(self):
        self.current_element = random.choice(elements)
        self.options = [self.current_element["name"]]
        while len(self.options) < 4:
            other = random.choice(elements)
            if other["name"] not in self.options:
                self.options.append(other["name"])
        random.shuffle(self.options)

    def draw(self):
        screen.fill(WHITE)
        
        if self.game_over:
            self.draw_game_over()
            return
        
        title_text = self.large_font.render("化学元素猜猜乐", True, BLUE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 20))
        
        score_text = self.font.render(f"分数: {self.score}", True, BLACK)
        screen.blit(score_text, (50, 20))
        
        lives_text = self.font.render(f"生命: {'❤' * self.lives}", True, RED)
        screen.blit(lives_text, (200, 20))
        
        round_text = self.font.render(f"回合: {self.round}/{self.max_rounds}", True, BLACK)
        screen.blit(round_text, (650, 20))
        
        category = self.current_element["category"]
        cat_color = category_colors.get(category, BLACK)
        cat_text = self.font.render(f"类别: {category}", True, cat_color)
        screen.blit(cat_text, (WIDTH//2 - cat_text.get_width()//2, 80))
        
        symbol_text = self.large_font.render(self.current_element["symbol"], True, BLACK)
        pygame.draw.circle(screen, cat_color, (WIDTH//2, 200), 80)
        pygame.draw.circle(screen, WHITE, (WIDTH//2, 200), 75)
        screen.blit(symbol_text, (WIDTH//2 - symbol_text.get_width()//2, 180))
        
        hint_text = self.font.render("这个元素的中文名称是什么？", True, BLACK)
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, 300))
        
        for i, option in enumerate(self.options):
            button_x = 150 + (i % 2) * 300
            button_y = 360 + (i // 2) * 70
            pygame.draw.rect(screen, (200, 200, 255), (button_x, button_y, 280, 60), border_radius=10)
            pygame.draw.rect(screen, (150, 150, 200), (button_x, button_y, 280, 60), 3, border_radius=10)
            option_text = self.font.render(f"{i+1}. {option}", True, BLACK)
            screen.blit(option_text, (button_x + 20, button_y + 18))

    def draw_game_over(self):
        screen.fill(BLACK)
        title_text = self.large_font.render("游戏结束！", True, YELLOW)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 150))
        
        score_text = self.large_font.render(f"最终分数: {self.score}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 250))
        
        restart_text = self.font.render("按空格键重新开始", True, GREEN)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 350))

    def handle_click(self, pos):
        if self.game_over:
            return
        
        for i, option in enumerate(self.options):
            button_x = 150 + (i % 2) * 300
            button_y = 360 + (i // 2) * 70
            if button_x <= pos[0] <= button_x + 280 and button_y <= pos[1] <= button_y + 60:
                if option == self.current_element["name"]:
                    self.score += 10 + (4 - i) * 2
                    self.round += 1
                    if self.round > self.max_rounds:
                        self.game_over = True
                    else:
                        self.next_question()
                else:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.game_over and event.key == pygame.K_SPACE:
                self.__init__()
            elif not self.game_over and pygame.K_1 <= event.key <= pygame.K_4:
                idx = event.key - pygame.K_1
                if 0 <= idx < len(self.options):
                    if self.options[idx] == self.current_element["name"]:
                        self.score += 10 + (4 - idx) * 2
                        self.round += 1
                        if self.round > self.max_rounds:
                            self.game_over = True
                        else:
                            self.next_question()
                    else:
                        self.lives -= 1
                        if self.lives <= 0:
                            self.game_over = True

game = ChemistryGame()
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            game.handle_click(pygame.mouse.get_pos())
        game.handle_input(event)
    
    game.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
