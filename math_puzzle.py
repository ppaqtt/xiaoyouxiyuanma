import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("数学谜题")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

class MathPuzzleGame:
    def __init__(self):
        self.score = 0
        self.round = 1
        self.max_rounds = 10
        self.num1 = 0
        self.num2 = 0
        self.operator = ""
        self.answer = 0
        self.player_input = ""
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.next_question()

    def next_question(self):
        operators = ["+", "-", "*"]
        self.operator = random.choice(operators)
        
        if self.operator == "+":
            self.num1 = random.randint(1, 50)
            self.num2 = random.randint(1, 50)
            self.answer = self.num1 + self.num2
        elif self.operator == "-":
            self.num1 = random.randint(10, 100)
            self.num2 = random.randint(1, self.num1)
            self.answer = self.num1 - self.num2
        else:
            self.num1 = random.randint(1, 12)
            self.num2 = random.randint(1, 12)
            self.answer = self.num1 * self.num2
        
        self.player_input = ""

    def draw(self):
        screen.fill(WHITE)
        
        title_text = self.font.render("数学谜题", True, BLUE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
        
        score_text = self.small_font.render(f"分数: {self.score} | 回合: {self.round}/{self.max_rounds}", True, BLACK)
        screen.blit(score_text, (50, 50))
        
        question_text = self.font.render(f"{self.num1} {self.operator} {self.num2} = ?", True, BLACK)
        screen.blit(question_text, (WIDTH//2 - question_text.get_width()//2, 200))
        
        input_text = self.font.render(f"你的答案: {self.player_input}", True, BLACK)
        screen.blit(input_text, (WIDTH//2 - input_text.get_width()//2, 300))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.player_input = self.player_input[:-1]
            elif event.key == pygame.K_RETURN:
                self.check_answer()
            elif event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                self.player_input += event.unicode

    def check_answer(self):
        try:
            if int(self.player_input) == self.answer:
                self.score += 10
        except:
            pass
        
        self.round += 1
        
        if self.round > self.max_rounds:
            self.show_result()
        else:
            self.next_question()

    def show_result(self):
        screen.fill(WHITE)
        result_text = self.font.render(f"游戏结束！得分: {self.score}", True, BLUE)
        screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, 250))
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

game = MathPuzzleGame()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.handle_input(event)
    
    game.draw()
    pygame.display.flip()

pygame.quit()