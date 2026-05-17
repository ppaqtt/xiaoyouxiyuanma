"""
侦探推理小说
一个经典的侦探推理游戏，找出凶手！
"""

import pygame
import os
import sys
import random

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

WIDTH, HEIGHT = 950, 680
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("侦探推理小说")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (40, 40, 40)
BLUE = (0, 100, 200)
GREEN = (0, 180, 100)
RED = (200, 50, 50)
PURPLE = (150, 50, 200)
BROWN = (139, 69, 19)

class Suspect:
    def __init__(self, name, color, description):
        self.name = name
        self.color = color
        self.description = description
        self.motives = []
        self.testimonies = []

class Clue:
    def __init__(self, name, description, hint):
        self.name = name
        self.description = description
        self.hint = hint
        self.found = False

class DetectiveGame:
    def __init__(self):
        self.phase = "menu"
        self.clues = []
        self.suspects = []
        self.interviewed = []
        self.found_clues = 0
        self.true_murderer = ""
        self.current_location = 0
        self.font_large = get_chinese_font(64)
        self.font_medium = get_chinese_font(32)
        self.font_small = get_chinese_font(26)
        self.locations = ["客厅", "书房", "花园", "厨房"]
        self.init_game()
    
    def init_game(self):
        self.suspects = [
            Suspect("管家", BROWN, "忠诚地服务了家族30年"),
            Suspect("女继承人", BLUE, "死者的女儿，生活奢侈"),
            Suspect("医生", GREEN, "死者的私人医生"),
            Suspect("厨师", RED, "在大宅工作了10年")
        ]
        
        self.suspects[0].motives = ["被死者威胁要解雇", "发现自己被欺骗多年"]
        self.suspects[1].motives = ["欠了大量赌债", "遗嘱即将被修改"]
        self.suspects[2].motives = ["医疗事故被死者发现", "被死者勒索"]
        self.suspects[3].motives = ["与死者有感情纠葛", "工资被长期拖欠"]
        
        self.suspects[0].testimonies = [
            "昨晚我一直在整理账目，直到11点才休息",
            "我听到书房有奇怪的声音，但没太在意"
        ]
        self.suspects[1].testimonies = [
            "我和朋友在外面吃饭，10点左右回来的",
            "父亲最近对我总是发脾气"
        ]
        self.suspects[2].testimonies = [
            "我下午来看过死者，他当时还很健康",
            "死者最近压力很大，睡眠不好"
        ]
        self.suspects[3].testimonies = [
            "我8点就做完晚饭回房间了",
            "死者最近胃口一直不好"
        ]
        
        self.clues = [
            Clue("沾血的小刀", "厨房的一把小刀上有血迹", "指向厨师或管家"),
            Clue("撕碎的遗嘱", "在书房发现了被撕碎的遗嘱草稿", "指向女继承人"),
            Clue("神秘的药方", "在花园发现了一瓶未标签的药", "指向医生"),
            Clue("沾泥的鞋", "在客厅门口发现了沾泥的鞋子", "可能是外来者"),
            Clue("破旧的日记", "管家房间的日记记录了怨恨", "指向管家")
        ]
        
        self.true_murderer = random.choice([s.name for s in self.suspects])
    
    def draw(self):
        screen.fill(DARK_GRAY)
        
        if self.phase == "menu":
            self.draw_menu()
        elif self.phase == "game":
            self.draw_game()
        elif self.phase == "guess":
            self.draw_guess()
        elif self.phase == "result":
            self.draw_result()
        
        pygame.display.flip()
    
    def draw_menu(self):
        title = self.font_large.render("侦探推理小说", True, PURPLE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        
        desc_lines = [
            "富商在豪宅中离奇死亡...",
            "你是一位著名的侦探，",
            "现在需要通过寻找线索和审问嫌疑人，",
            "找出真正的凶手！",
            "",
            "按 空格键 开始调查"
        ]
        
        y = 200
        for line in desc_lines:
            text = self.font_medium.render(line, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 40
    
    def draw_game(self):
        # 状态栏
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 70))
        status = f"找到线索: {self.found_clues}/{len(self.clues)}  已审问: {len(self.interviewed)}"
        text = self.font_medium.render(status, True, WHITE)
        screen.blit(text, (30, 20))
        
        location_text = f"当前位置: {self.locations[self.current_location]}"
        text = self.font_small.render(location_text, True, BLUE)
        screen.blit(text, (WIDTH - text.get_width() - 30, 25))
        
        # 位置按钮
        button_y = 100
        for i, loc in enumerate(self.locations):
            btn_rect = pygame.Rect(50 + i * 220, button_y, 200, 50)
            pygame.draw.rect(screen, DARK_GRAY if i == self.current_location else GRAY, 
                           btn_rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, btn_rect, 2, border_radius=8)
            text = self.font_medium.render(loc, True, WHITE)
            screen.blit(text, (btn_rect.x + 60, btn_rect.y + 10))
        
        # 线索区域
        clue_y = 180
        clue_text = self.font_medium.render("现场线索:", True, BLUE)
        screen.blit(clue_text, (50, clue_y))
        
        for i, clue in enumerate(self.clues):
            btn_rect = pygame.Rect(50, clue_y + 40 + i * 50, 400, 40)
            if clue.found:
                pygame.draw.rect(screen, GREEN, btn_rect, border_radius=5)
                text = f"{clue.name}: {clue.description}"
                color = BLACK
            else:
                pygame.draw.rect(screen, GRAY, btn_rect, border_radius=5)
                text = "??? (需要仔细调查)"
                color = DARK_GRAY
            text_surface = self.font_small.render(text, True, color)
            screen.blit(text_surface, (btn_rect.x + 10, btn_rect.y + 8))
        
        # 嫌疑人区域
        sus_text = self.font_medium.render("嫌疑人:", True, BLUE)
        screen.blit(sus_text, (500, clue_y))
        
        for i, sus in enumerate(self.suspects):
            btn_rect = pygame.Rect(500, clue_y + 40 + i * 60, 400, 50)
            if sus.name in self.interviewed:
                pygame.draw.rect(screen, GREEN, btn_rect, border_radius=5)
            else:
                pygame.draw.rect(screen, sus.color, btn_rect, border_radius=5)
            text = f"{sus.name}: {sus.description}"
            text_surface = self.font_small.render(text, True, WHITE)
            screen.blit(text_surface, (btn_rect.x + 10, btn_rect.y + 12))
        
        # 猜测按钮
        guess_btn = pygame.Rect(WIDTH - 150, HEIGHT - 60, 130, 45)
        pygame.draw.rect(screen, RED, guess_btn, border_radius=10)
        text = self.font_medium.render("指认凶手", True, WHITE)
        screen.blit(text, (guess_btn.x + 15, guess_btn.y + 10))
    
    def draw_guess(self):
        title = self.font_large.render("指认凶手", True, RED)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        desc = self.font_medium.render("根据收集到的线索，选择你认为的凶手", True, WHITE)
        screen.blit(desc, (WIDTH//2 - desc.get_width()//2, 130))
        
        y = 220
        for i, sus in enumerate(self.suspects):
            btn_rect = pygame.Rect(WIDTH//2 - 180, y, 360, 70)
            pygame.draw.rect(screen, sus.color, btn_rect, border_radius=10)
            text = self.font_medium.render(sus.name, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y + 20))
            y += 90
        
        back_btn = pygame.Rect(WIDTH//2 - 70, y + 20, 140, 45)
        pygame.draw.rect(screen, GRAY, back_btn, border_radius=8)
        text = self.font_medium.render("继续调查", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, y + 28))
    
    def draw_result(self):
        if self.phase == "result":
            if self.true_murderer == "":
                return
            
            if self.true_murderer in [s.name for s in self.suspects]:
                title_text = "案件告破！" if self.phase == "result" else "..."
                color = GREEN
            else:
                title_text = "凶手逃脱了..."
                color = RED
            
            title = self.font_large.render(title_text, True, color)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
            
            result_text = f"真正的凶手是: {self.true_murderer}!"
            text = self.font_medium.render(result_text, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 280))
            
            restart_text = self.font_medium.render("按 R 键重新开始", True, BLUE)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 450))
    
    def handle_click(self, pos):
        if self.phase == "menu":
            return
        elif self.phase == "game":
            self.handle_game_click(pos)
        elif self.phase == "guess":
            self.handle_guess_click(pos)
    
    def handle_game_click(self, pos):
        # 位置按钮
        button_y = 100
        for i, _ in enumerate(self.locations):
            btn_rect = pygame.Rect(50 + i * 220, button_y, 200, 50)
            if btn_rect.collidepoint(pos):
                self.current_location = i
                if random.random() < 0.6 and self.found_clues < len(self.clues):
                    for clue in self.clues:
                        if not clue.found:
                            clue.found = True
                            self.found_clues += 1
                            break
                return
        
        # 嫌疑人按钮
        clue_y = 180
        for i, sus in enumerate(self.suspects):
            btn_rect = pygame.Rect(500, clue_y + 40 + i * 60, 400, 50)
            if btn_rect.collidepoint(pos) and sus.name not in self.interviewed:
                self.interviewed.append(sus.name)
                return
        
        # 指认凶手按钮
        guess_btn = pygame.Rect(WIDTH - 150, HEIGHT - 60, 130, 45)
        if guess_btn.collidepoint(pos):
            self.phase = "guess"
    
    def handle_guess_click(self, pos):
        y = 220
        for i, sus in enumerate(self.suspects):
            btn_rect = pygame.Rect(WIDTH//2 - 180, y, 360, 70)
            if btn_rect.collidepoint(pos):
                if sus.name == self.true_murderer:
                    self.phase = "result"
                else:
                    self.phase = "result"
                return
            y += 90
        
        back_btn = pygame.Rect(WIDTH//2 - 70, y + 20, 140, 45)
        if back_btn.collidepoint(pos):
            self.phase = "game"
    
    def handle_key(self, key):
        if key == pygame.K_SPACE and self.phase == "menu":
            self.phase = "game"
        elif key == pygame.K_r and self.phase == "result":
            self.__init__()
        elif key == pygame.K_ESCAPE:
            if self.phase == "guess":
                self.phase = "game"

def main():
    game = DetectiveGame()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                game.handle_key(event.key)
        
        game.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
