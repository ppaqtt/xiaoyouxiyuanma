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
GREEN = (0, 200, 0)
RED = (200, 0, 0)

elements = {
    "H": "氢", "He": "氦", "Li": "锂", "Be": "铍", "B": "硼",
    "C": "碳", "N": "氮", "O": "氧", "F": "氟", "Ne": "氖",
    "Na": "钠", "Mg": "镁", "Al": "铝", "Si": "硅", "P": "磷",
    "S": "硫", "Cl": "氯", "Ar": "氩", "K": "钾", "Ca": "钙"
}

class ChemistryGame:
    def __init__(self):
        self.score = 0
        self.round = 1
        self.max_rounds = 10
        self.current_element = None
        self.player_input = ""
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.next_question()

    def next_question(self):
        self.current_element = random.choice(list(elements.keys()))
        self.player_input = ""

    def draw(self):
        screen.fill(WHITE)
        
        title_text = self.font.render("化学元素猜猜乐", True, BLUE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
        
        score_text = self.small_font.render(f"分数: {self.score} | 回合: {self.round}/{self.max_rounds}", True, BLACK)
        screen.blit(score_text, (50, 50))
        
        question_text = self.font.render(f"元素符号: {self.current_element}", True, BLACK)
        screen.blit(question_text, (WIDTH//2 - question_text.get_width()//2, 200))
        
        input_text = self.font.render(f"你的答案: {self.player_input}", True, BLACK)
        screen.blit(input_text, (WIDTH//2 - input_text.get_width()//2, 300))
        
        hint_text = self.small_font.render("提示: 输入元素的中文名称", True, (100, 100, 100))
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, 400))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.player_input = self.player_input[:-1]
            elif event.key == pygame.K_RETURN:
                self.check_answer()
            else:
                self.player_input += event.unicode

    def check_answer(self):
        if self.player_input == elements[self.current_element]:
            self.score += 10
            self.round += 1
            if self.round > self.max_rounds:
                self.show_result()
            else:
                self.next_question()
        else:
            self.round += 1
            if self.round > self.max_rounds:
                self.show_result()

    def show_result(self):
        screen.fill(WHITE)
        result_text = self.font.render(f"游戏结束！得分: {self.score}", True, BLUE)
        screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, 250))
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

game = ChemistryGame()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.handle_input(event)
    
    game.draw()
    pygame.display.flip()

pygame.quit()