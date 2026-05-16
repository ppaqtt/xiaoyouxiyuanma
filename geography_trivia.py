import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("环球冒险知识问答")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
YELLOW = (255, 200, 50)
ORANGE = (255, 150, 50)

continents = [
    {
        "name": "亚洲",
        "color": (255, 200, 150),
        "questions": [
            {"q": "世界上最高的山峰是？", "a": ["喜马拉雅山", "乔戈里峰", "珠穆朗玛峰", "洛子峰"], "correct": 2},
            {"q": "世界上最大的沙漠是？", "a": ["撒哈拉沙漠", "阿拉伯沙漠", "戈壁", "塔克拉玛干"], "correct": 0},
            {"q": "世界上最大的国家是？", "a": ["中国", "美国", "俄罗斯", "加拿大"], "correct": 2},
            {"q": "世界上最长的河流是？", "a": ["亚马逊河", "尼罗河", "长江", "密西西比河"], "correct": 1},
        ]
    },
    {
        "name": "欧洲",
        "color": (200, 200, 255),
        "questions": [
            {"q": "欧洲最大的国家是？", "a": ["法国", "德国", "英国", "俄罗斯"], "correct": 3},
            {"q": "法国的首都是？", "a": ["伦敦", "巴黎", "罗马", "马德里"], "correct": 1},
            {"q": "意大利的首都是？", "a": ["米兰", "威尼斯", "罗马", "那不勒斯"], "correct": 2},
        ]
    },
    {
        "name": "非洲",
        "color": (200, 150, 100),
        "questions": [
            {"q": "非洲最大的国家是？", "a": ["埃及", "南非", "尼日利亚", "阿尔及利亚"], "correct": 3},
            {"q": "埃及的首都是？", "a": ["开罗", "亚历山大", "吉萨", "卢克索"], "correct": 0},
        ]
    },
    {
        "name": "美洲",
        "color": (150, 255, 200),
        "questions": [
            {"q": "美国的首都是？", "a": ["纽约", "洛杉矶", "华盛顿", "芝加哥"], "correct": 2},
            {"q": "巴西的首都是？", "a": ["里约热内卢", "圣保罗", "巴西利亚", "萨尔瓦多"], "correct": 2},
            {"q": "世界上最大的雨林是？", "a": ["亚马逊雨林", "刚果雨林", "东南亚雨林", "温带雨林"], "correct": 0},
        ]
    },
    {
        "name": "大洋洲",
        "color": (200, 255, 200),
        "questions": [
            {"q": "澳大利亚的首都是？", "a": ["悉尼", "墨尔本", "堪培拉", "布里斯班"], "correct": 2},
            {"q": "世界上最大的珊瑚礁是？", "a": ["大堡礁", "佛罗里达礁", "贝里斯礁", "新喀里多尼亚礁"], "correct": 0},
        ]
    }
]

class GeographyTrivia:
    def __init__(self):
        self.score = 0
        self.current_continent = 0
        self.question_index = 0
        self.current_question = None
        self.options = []
        self.lives = 3
        self.answered = False
        self.game_over = False
        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 48)
        self.next_question()

    def next_question(self):
        if self.question_index >= len(continents[self.current_continent]["questions"]):
            self.current_continent = (self.current_continent + 1) % len(continents)
            self.question_index = 0
        self.current_question = continents[self.current_continent]["questions"][self.question_index]
        self.options = self.current_question["a"]
        self.question_index += 1
        self.answered = False

    def draw(self):
        screen.fill(WHITE)
        
        if self.game_over:
            self.draw_game_over()
            return
        
        cont = continents[self.current_continent]
        pygame.draw.rect(screen, cont["color"], (100, 200, 600, 250))
        pygame.draw.rect(screen, (0, 0, 0), (100, 200, 600, 250), 3)
        
        title_text = self.large_font.render(f"环球冒险 - {cont['name']}", True, BLACK)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 30))
        
        score_text = self.font.render(f"分数: {self.score}", True, BLACK)
        screen.blit(score_text, (50, 20))
        
        lives_text = self.font.render(f"生命: {'❤' * self.lives}", True, RED)
        screen.blit(lives_text, (200, 20))
        
        question_text = self.font.render(self.current_question["q"], True, BLACK)
        screen.blit(question_text, (WIDTH//2 - question_text.get_width()//2, 240))
        
        for i, option in enumerate(self.options):
            button_x = 150 + (i % 2) * 300
            button_y = 300 + (i // 2) * 70
            color = (200, 200, 255) if not self.answered else (
                GREEN if i == self.current_question["correct"] else RED if i == self.selected_option else (200, 200, 255)
            )
            pygame.draw.rect(screen, color, (button_x, button_y, 280, 50), border_radius=10)
            pygame.draw.rect(screen, (50, 50, 50), (button_x, button_y, 280, 50), 3, border_radius=10)
            option_text = self.font.render(f"{i+1}. {option}", True, BLACK)
            screen.blit(option_text, (button_x + 20, button_y + 15))
        
        hint_text = self.font.render("点击选项或按1-4键回答，空格下一题", True, BLUE)
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, 500))

    def draw_game_over(self):
        screen.fill(BLACK)
        title_text = self.large_font.render("游戏结束！", True, YELLOW)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 200))
        score_text = self.large_font.render(f"最终分数: {self.score}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 280))
        restart_text = self.font.render("按空格键重新开始", True, GREEN)
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
        else:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True

game = GeographyTrivia()
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
