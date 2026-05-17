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
pygame.display.set_caption("数学大冒险")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
YELLOW = (255, 200, 50)
PURPLE = (150, 50, 200)

class MathPuzzle:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.hp = 100
        self.expression = ""
        self.answer = 0
        self.choices = []
        self.time_left = 10
        self.max_time = 10
        self.font = get_chinese_font(32)
        self.large_font = get_chinese_font(48)
        self.hero_x = WIDTH // 2
        self.hero_y = 500
        self.enemies = []
        self.spawn_timer = 0
        self.next_problem()

    def next_problem(self):
        self.time_left = self.max_time
        self.max_time = max(5, 10 - self.level // 2)
        difficulty = min(self.level, 10)
        
        ops = ["+", "-", "*", "×", "/"]
        op = random.choice(ops[:min(difficulty)])
        
        if op == "+":
            a = random.randint(1, 20 + difficulty * 5)
            b = random.randint(1, 20 + difficulty * 5)
            self.answer = a + b
        elif op == "-":
            a = random.randint(10, 30 + difficulty * 5)
            b = random.randint(1, a)
            self.answer = a - b
        elif op == "*" or op == "×":
            a = random.randint(1, difficulty + 4)
            b = random.randint(1, difficulty + 4)
            self.answer = a * b
        elif op == "/":
            b = random.randint(2, 10)
            self.answer = random.randint(1, 10)
            a = b * self.answer
        
        op_display = "×" if op == "*" else op
        
        self.expression = f"{a} {op_display} {b} = ?"
        
        self.choices = [self.answer]
        while len(self.choices) < 4:
            offset = random.randint(-10, 10)
            if self.answer + offset not in self.choices and self.answer + offset >= 0:
                self.choices.append(self.answer + offset)
        random.shuffle(self.choices)

    def update(self):
        pass

    def draw(self):
        screen.fill(WHITE)
        
        pygame.draw.rect(screen, (100, 200, 100), (0, 400, WIDTH, 200))
        
        pygame.draw.rect(screen, BLUE, (self.hero_x - 20, self.hero_y - 30, 40, 60))
        pygame.draw.circle(screen, (255, 200, 100), (self.hero_x, self.hero_y - 45), 15)
        
        title_text = self.large_font.render("数学大冒险", True, BLACK)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 10))
        
        level_text = self.font.render(f"关卡: {self.level}", True, BLACK)
        screen.blit(level_text, (50, 10))
        
        score_text = self.font.render(f"分数: {self.score}", True, BLACK)
        screen.blit(score_text, (200, 10))
        
        hp_text = self.font.render(f"HP: {self.hp}", True, RED if self.hp < 30 else GREEN)
        screen.blit(hp_text, (650, 10))
        
        pygame.draw.rect(screen, (200, 200, 200), (100, 60, 600, 40))
        pygame.draw.rect(screen, GREEN, (100, 60, 600 * (self.hp/100), 40))
        
        pygame.draw.rect(screen, (240, 240, 240), (200, 120, 400, 120), border_radius=10)
        pygame.draw.rect(screen, BLACK, (200, 120, 400, 120), 3, border_radius=10)
        expr_text = self.large_font.render(self.expression, True, BLACK)
        screen.blit(expr_text, (WIDTH//2 - expr_text.get_width()//2, 155))
        
        time_text = self.font.render(f"剩余: {int(self.time_left)}", True, RED if self.time_left < 3 else BLACK)
        screen.blit(time_text, (650, 60))
        
        for i, choice in enumerate(self.choices):
            button_x = 100 + i * 175
            pygame.draw.rect(screen, (200, 220, 255), (button_x, 260, 150, 60), border_radius=10)
            pygame.draw.rect(screen, BLACK, (button_x, 260, 150, 60), 3, border_radius=10)
            choice_text = self.font.render(str(choice), True, BLACK)
            screen.blit(choice_text, (button_x + 75 - choice_text.get_width()//2, 280))
        
        hint_text = self.font.render("点击或按1-4选择答案", True, PURPLE)
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, 350))

    def handle_click(self, pos):
        for i in range(4):
            button_x = 100 + i * 175
            if button_x <= pos[0] <= button_x + 150 and 260 <= pos[1] <= 320:
                if self.choices[i] == self.answer:
                    self.score += 10 * self.level
                    self.next_problem()
                    if self.score > self.level * 50:
                        self.level += 1
                else:
                    self.hp -= 20
                    if self.hp <= 0:
                        self.__init__()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and pygame.K_1 <= event.key <= pygame.K_4:
            i = event.key - pygame.K_1
            if self.choices[i] == self.answer:
                self.score += 10 * self.level
                self.next_problem()
                if self.score > self.level * 50:
                    self.level += 1
            else:
                self.hp -= 20
                if self.hp <= 0:
                    self.__init__()

game = MathPuzzle()
clock = pygame.time.Clock()
last_time = pygame.time.get_ticks()
running = True

while running:
    current_time = pygame.time.get_ticks()
    if current_time - last_time >= 1000:
        game.time_left -= 1
        last_time = current_time
        if game.time_left <= 0:
            game.hp -= 10
            game.next_problem()
            if game.hp <= 0:
                game.__init__()
    
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
