import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("地理知识问答")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

questions = [
    {"question": "世界上最大的海洋是？", "options": ["大西洋", "印度洋", "太平洋", "北冰洋"], "answer": 2},
    {"question": "中国的首都是？", "options": ["上海", "北京", "广州", "深圳"], "answer": 1},
    {"question": "世界上最高的山峰是？", "options": ["乔戈里峰", "珠穆朗玛峰", "干城章嘉峰", "洛子峰"], "answer": 1},
    {"question": "哪个国家的领土面积最大？", "options": ["中国", "美国", "俄罗斯", "加拿大"], "answer": 2},
    {"question": "世界上最长的河流是？", "options": ["亚马逊河", "尼罗河", "长江", "密西西比河"], "answer": 1},
    {"question": "澳大利亚的首都是？", "options": ["悉尼", "墨尔本", "堪培拉", "珀斯"], "answer": 2},
    {"question": "欧洲最大的国家是？", "options": ["法国", "德国", "英国", "俄罗斯"], "answer": 3},
    {"question": "非洲最大的沙漠是？", "options": ["撒哈拉沙漠", "阿拉伯沙漠", "戈壁沙漠", "塔克拉玛干"], "answer": 0},
    {"question": "日本的首都是？", "options": ["大阪", "京都", "东京", "神户"], "answer": 2},
    {"question": "世界上最深的湖泊是？", "options": ["贝加尔湖", "里海", "苏必利尔湖", "维多利亚湖"], "answer": 0}
]

class GeographyGame:
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
        
        title_text = self.font.render("地理知识问答", True, BLUE)
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

game = GeographyGame()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.handle_input(event)
    
    game.draw()
    pygame.display.flip()

pygame.quit()