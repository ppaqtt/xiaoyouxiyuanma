import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("历史知识问答")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

questions = [
    {"question": "中国历史上第一个皇帝是谁？", "options": ["秦始皇", "汉武帝", "唐太宗", "宋太祖"], "answer": 0},
    {"question": "长城最初是哪个朝代修建的？", "options": ["汉朝", "秦朝", "明朝", "清朝"], "answer": 1},
    {"question": "四大发明不包括以下哪项？", "options": ["造纸术", "印刷术", "蒸汽机", "火药"], "answer": 2},
    {"question": "唐朝的开国皇帝是？", "options": ["李渊", "李世民", "李隆基", "李治"], "answer": 0},
    {"question": "三国时期的三国是指？", "options": ["魏蜀吴", "楚汉燕", "齐楚燕", "秦赵韩"], "answer": 0},
    {"question": "孔子是哪个朝代的人？", "options": ["商朝", "周朝", "秦朝", "汉朝"], "answer": 1},
    {"question": "世界上最早的文明发源地是？", "options": ["美索不达米亚", "古埃及", "古印度", "中国"], "answer": 0},
    {"question": "第一次世界大战爆发于哪一年？", "options": ["1912", "1914", "1916", "1918"], "answer": 1},
    {"question": "中国古代四大名著不包括？", "options": ["红楼梦", "西游记", "水浒传", "聊斋志异"], "answer": 3},
    {"question": "秦始皇统一六国是在哪一年？", "options": ["公元前221年", "公元前206年", "公元前256年", "公元前230年"], "answer": 0}
]

class HistoryGame:
    def __init__(self):
        self.score = 0
        self.round = 1
        self.max_rounds = 10
        self.current_question = None
        self.selected_option = None
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        self.next_question()

    def next_question(self):
        self.current_question = random.choice(questions)
        self.selected_option = None

    def draw(self):
        screen.fill(WHITE)
        
        title_text = self.font.render("历史知识问答", True, BLUE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 30))
        
        score_text = self.small_font.render(f"分数: {self.score} | 回合: {self.round}/{self.max_rounds}", True, BLACK)
        screen.blit(score_text, (50, 30))
        
        question_text = self.font.render(self.current_question["question"], True, BLACK)
        screen.blit(question_text, (WIDTH//2 - question_text.get_width()//2, 120))
        
        option_y = 200
        for i, option in enumerate(self.current_question["options"]):
            color = BLACK
            if self.selected_option == i:
                color = BLUE
            option_text = self.small_font.render(f"{i+1}. {option}", True, color)
            screen.blit(option_text, (WIDTH//2 - option_text.get_width()//2, option_y))
            option_y += 50

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_1, pygame.K_KP1]:
                self.selected_option = 0
                self.check_answer()
            elif event.key in [pygame.K_2, pygame.K_KP2]:
                self.selected_option = 1
                self.check_answer()
            elif event.key in [pygame.K_3, pygame.K_KP3]:
                self.selected_option = 2
                self.check_answer()
            elif event.key in [pygame.K_4, pygame.K_KP4]:
                self.selected_option = 3
                self.check_answer()

    def check_answer(self):
        if self.selected_option == self.current_question["answer"]:
            self.score += 10
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

game = HistoryGame()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.handle_input(event)
    
    game.draw()
    pygame.display.flip()

pygame.quit()