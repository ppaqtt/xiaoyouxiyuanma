import pygame
import os
import random
import sys

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

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("时间旅行大冒险")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
YELLOW = (255, 200, 50)
PURPLE = (150, 50, 200)
GOLD = (255, 215, 0)

eras = [
    {
        "name": "古代中国",
        "color": (200, 150, 100),
        "questions": [
            {"q": "中国历史上第一个皇帝是谁？", "a": ["汉武帝", "秦始皇", "唐太宗", "明太祖"], "correct": 1},
            {"q": "长城最初是哪个朝代修建的？", "a": ["秦朝", "汉朝", "明朝", "清朝"], "correct": 0},
            {"q": "四大发明中不包括？", "a": ["指南针", "造纸术", "蒸汽机", "火药"], "correct": 2},
            {"q": "商朝最后的首都在哪里？", "a": ["安阳", "洛阳", "西安", "南京"], "correct": 0},
        ]
    },
    {
        "name": "中世纪欧洲",
        "color": (150, 150, 200),
        "questions": [
            {"q": "罗马帝国何时分裂为东西两部分？", "a": ["公元284年", "公元395年", "公元476年", "公元500年"], "correct": 1},
            {"q": "十字军东征共有几次主要的？", "a": ["5次", "7次", "8次", "10次"], "correct": 2},
            {"q": "英法百年战争持续了多少年？", "a": ["86年", "100年", "116年", "133年"], "correct": 2},
        ]
    },
    {
        "name": "文艺复兴",
        "color": (200, 200, 150),
        "questions": [
            {"q": "《蒙娜丽莎》的作者是？", "a": ["米开朗琪罗", "达芬奇", "拉斐尔", "梵高"], "correct": 1},
            {"q": "文艺复兴起源于哪个国家？", "a": ["法国", "意大利", "德国", "英国"], "correct": 1},
            {"q": "《神曲》的作者是？", "a": ["彼特拉克", "薄伽丘", "但丁", "马基雅维利"], "correct": 2},
        ]
    },
    {
        "name": "现代世界",
        "color": (100, 200, 200),
        "questions": [
            {"q": "第一次世界大战爆发于？", "a": ["1912年", "1914年", "1918年", "1939年"], "correct": 1},
            {"q": "互联网最初是为了什么目的而创建？", "a": ["商业用途", "军事研究", "教育", "娱乐"], "correct": 1},
            {"q": "人类首次登月是在哪一年？", "a": ["1961年", "1969年", "1976年", "1980年"], "correct": 1},
        ]
    }
]

class TimeTravelGame:
    def __init__(self):
        self.score = 0
        self.current_era = 0
        self.question_index = 0
        self.time_parts = 0
        self.answered = False
        self.game_over = False
        self.selected_option = -1
        self.font = get_chinese_font(32)
        self.large_font = get_chinese_font(48)
        self.next_question()

    def next_question(self):
        if self.question_index >= len(eras[self.current_era]["questions"]):
            self.current_era = (self.current_era + 1) % len(eras)
            self.question_index = 0
        self.current_question = eras[self.current_era]["questions"][self.question_index]
        self.options = self.current_question["a"]
        self.question_index += 1
        self.answered = False
        self.selected_option = -1

    def draw(self):
        screen.fill(WHITE)
        
        if self.game_over:
            self.draw_game_over()
            return
        
        era = eras[self.current_era]
        pygame.draw.rect(screen, era["color"], (100, 200, 600, 250), border_radius=20)
        pygame.draw.rect(screen, BLACK, (100, 200, 600, 250), 3, border_radius=20)
        
        title_text = self.large_font.render(f"时间旅行 - {era['name']}", True, BLACK)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 30))
        
        score_text = self.font.render(f"分数: {self.score}", True, BLACK)
        screen.blit(score_text, (50, 20))
        
        parts_text = self.font.render(f"时光碎片: {self.time_parts}/10", True, PURPLE)
        screen.blit(parts_text, (600, 20))
        
        question_text = self.font.render(self.current_question["q"], True, BLACK)
        screen.blit(question_text, (WIDTH//2 - question_text.get_width()//2, 240))
        
        for i, option in enumerate(self.options):
            button_x = 150 + (i % 2) * 300
            button_y = 300 + (i // 2) * 70
            color = (200, 200, 255)
            if self.answered:
                if i == self.current_question["correct"]:
                    color = GREEN
                elif i == self.selected_option:
                    color = RED
            pygame.draw.rect(screen, color, (button_x, button_y, 280, 50), border_radius=10)
            pygame.draw.rect(screen, (50, 50, 50), (button_x, button_y, 280, 50), 3, border_radius=10)
            option_text = self.font.render(f"{i+1}. {option}", True, BLACK)
            screen.blit(option_text, (button_x + 20, button_y + 15))
        
        hint_text = self.font.render("点击或按1-4选择答案，空格下一题", True, BLUE)
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, 500))

    def draw_game_over(self):
        screen.fill(BLACK)
        title_text = self.large_font.render("时间旅行结束！", True, GOLD)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 200))
        score_text = self.large_font.render(f"最终分数: {self.score}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 280))
        restart_text = self.font.render("按空格键再次出发", True, GREEN)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 360))

    def handle_click(self, pos):
        if self.game_over or self.answered:
            return
        for i in range(4):
            button_x = 150 + (i % 2) * 300
            button_y = 300 + (i // 2) * 70
            if button_x <= pos[0] <= button_x + 280 and button_y <= pos[1] <= button_y + 50:
                self.check_answer(i)
                return

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.game_over and event.key == pygame.K_SPACE:
                self.__init__()
                return
            if pygame.K_1 <= event.key <= pygame.K_4 and not self.answered:
                self.check_answer(event.key - pygame.K_1)
            elif event.key == pygame.K_SPACE and self.answered:
                self.next_question()

    def check_answer(self, selected):
        self.answered = True
        self.selected_option = selected
        if selected == self.current_question["correct"]:
            self.score += 10
            self.time_parts += 1
            if self.time_parts >= 10:
                self.game_over = True

game = TimeTravelGame()
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
