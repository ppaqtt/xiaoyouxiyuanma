import pygame
import sys
import pickle
import os

# 初始化pygame
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

# 游戏常量
WIDTH, HEIGHT = 900, 650
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("视觉小说 - 校园物语")
FONT = get_chinese_font(28)
TITLE_FONT = get_chinese_font(48)
CHOICE_FONT = get_chinese_font(32)

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (20, 30, 60)
LIGHT_BLUE = (100, 150, 200)
PINK = (255, 150, 180)
YELLOW = (255, 220, 100)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
TRANSPARENT_BLACK = (0, 0, 0, 180)

# 背景颜色/图案
BACKGROUNDS = {
    "school_gate": (150, 200, 255),
    "classroom": (240, 240, 220),
    "rooftop": (135, 206, 235),
    "park": (144, 238, 144),
    "cafe": (210, 180, 140),
    "home": (200, 180, 200)
}

# 角色立绘（用简单图形表示）
class CharacterSprite:
    def __init__(self, name, color, x):
        self.name = name
        self.color = color
        self.x = x
        self.y = 100
        self.width = 150
        self.height = 300
        self.visible = False
        self.expression = "normal"  # normal, happy, sad, angry

    def draw(self, surface):
        if not self.visible:
            return
        
        # 身体
        pygame.draw.rect(surface, self.color, (self.x, self.y + 100, self.width, self.height - 100), 0, 10)
        # 头
        pygame.draw.circle(surface, (255, 220, 200), (self.x + self.width//2, self.y + 60), 50)
        # 眼睛
        eye_y = self.y + 50
        if self.expression == "happy":
            pygame.draw.circle(surface, BLACK, (self.x + self.width//2 - 20, eye_y), 5)
            pygame.draw.circle(surface, BLACK, (self.x + self.width//2 + 20, eye_y), 5)
            pygame.draw.arc(surface, BLACK, (self.x + self.width//2 - 15, eye_y + 15, 30, 20), 3.14, 0, 3)
        elif self.expression == "sad":
            pygame.draw.line(surface, BLACK, (self.x + self.width//2 - 25, eye_y - 5), (self.x + self.width//2 - 15, eye_y + 5), 3)
            pygame.draw.line(surface, BLACK, (self.x + self.width//2 + 25, eye_y - 5), (self.x + self.width//2 + 15, eye_y + 5), 3)
            pygame.draw.arc(surface, BLACK, (self.x + self.width//2 - 15, eye_y + 20, 30, 20), 0, 3.14, 3)
        elif self.expression == "angry":
            pygame.draw.line(surface, BLACK, (self.x + self.width//2 - 25, eye_y + 5), (self.x + self.width//2 - 15, eye_y - 5), 3)
            pygame.draw.line(surface, BLACK, (self.x + self.width//2 + 25, eye_y + 5), (self.x + self.width//2 + 15, eye_y - 5), 3)
            pygame.draw.line(surface, BLACK, (self.x + self.width//2 - 15, eye_y + 25), (self.x + self.width//2 + 15, eye_y + 25), 3)
        else:
            pygame.draw.circle(surface, BLACK, (self.x + self.width//2 - 20, eye_y), 5)
            pygame.draw.circle(surface, BLACK, (self.x + self.width//2 + 20, eye_y), 5)
            pygame.draw.line(surface, BLACK, (self.x + self.width//2 - 15, eye_y + 25), (self.x + self.width//2 + 15, eye_y + 25), 3)
        
        # 名字标签
        name_surf = FONT.render(self.name, True, WHITE)
        pygame.draw.rect(surface, DARK_GRAY, (self.x, self.y - 30, self.width, 30), 0, 5)
        surface.blit(name_surf, (self.x + (self.width - name_surf.get_width())//2, self.y - 25))

# 创建角色
characters = {
    "sakura": CharacterSprite("小樱", (255, 182, 193), 100),
    "kenji": CharacterSprite("健二", (135, 206, 250), 650),
    "teacher": CharacterSprite("老师", (200, 200, 200), 375)
}

# 对话脚本
SCRIPT = [
    {"type": "scene", "bg": "school_gate", "text": "新的一天开始了，你站在学校门口..."},
    {"type": "scene", "bg": "school_gate", "char": "sakura", "char_pos": "left", "expression": "normal", "text": "小樱：早上好！你今天看起来精神不错呢！"},
    {"type": "choice", "text": "你会怎么回答？", "choices": [
        {"text": "早上好！今天天气真好", "next": 3},
        {"text": "嗯，还好吧", "next": 4}
    ]},
    {"type": "scene", "bg": "school_gate", "char": "sakura", "expression": "happy", "text": "小樱：是呀！一起去教室吧！", "flag": "sakura_happy", "value": True, "next": 5},
    {"type": "scene", "bg": "school_gate", "char": "sakura", "expression": "sad", "text": "小樱：这样啊...那我先去教室了...", "flag": "sakura_happy", "value": False, "next": 5},
    {"type": "scene", "bg": "classroom", "char": "sakura", "char_pos": "left", "char2": "kenji", "char2_pos": "right", "text": "教室里，健二正在和同学聊天。"},
    {"type": "scene", "bg": "classroom", "char": "kenji", "expression": "normal", "text": "健二：喂！听说今天有数学考试！"},
    {"type": "choice", "text": "你的反应是？", "choices": [
        {"text": "什么？我还没复习！", "next": 8},
        {"text": "没关系，我准备好了", "next": 9}
    ]},
    {"type": "scene", "bg": "classroom", "char": "kenji", "expression": "happy", "text": "健二：哈哈，我也是！一起加油吧！", "flag": "kenji_friend", "value": True, "next": 10},
    {"type": "scene", "bg": "classroom", "char": "kenji", "expression": "angry", "text": "健二：你这家伙，总是这么自信！", "flag": "kenji_friend", "value": False, "next": 10},
    {"type": "scene", "bg": "classroom", "char": "teacher", "expression": "normal", "text": "老师：好了，安静！考试开始了。"},
    {"type": "scene", "bg": "rooftop", "text": "午休时间，你来到了屋顶...", "clear_chars": True},
    {"type": "choice", "text": "你想做什么？", "choices": [
        {"text": "吃午饭", "next": 13},
        {"text": "四处看看", "next": 14},
        {"text": "保存游戏", "next": "save"}
    ]},
    {"type": "scene", "bg": "rooftop", "text": "你拿出了美味的便当，今天的午餐真不错！", "flag": "ate_lunch", "value": True, "next": 15},
    {"type": "scene", "bg": "rooftop", "char": "sakura", "char_pos": "left", "text": "小樱：咦，你也在这儿！", "next": 15},
    {"type": "scene", "bg": "park", "text": "放学后，你来到了公园...", "clear_chars": True},
    {"type": "scene", "bg": "park", "char": "sakura", "char_pos": "left", "expression": "happy", "text": "小樱：今天谢谢你陪我聊天！", "check_flag": "sakura_happy", "next": 18},
    {"type": "scene", "bg": "park", "char": "sakura", "char_pos": "left", "expression": "sad", "text": "小樱：那个...希望明天能和你多说说话...", "check_flag": "!sakura_happy", "next": 19},
    {"type": "scene", "bg": "park", "text": "小樱开心地回家了。今天真是美好的一天！", "clear_chars": True, "next": 20},
    {"type": "scene", "bg": "park", "text": "你决定明天要更主动一些。", "clear_chars": True, "next": 20},
    {"type": "ending", "text": "—— 第一章 结束 ——\n\n感谢游玩！"}
]

class VisualNovel:
    def __init__(self):
        self.script_index = 0
        self.flags = {}
        self.saves = {}
        self.save_file = "vn_save.pkl"
        self.current_bg = "school_gate"
        self.dialog_text = ""
        self.showing_choices = False
        self.current_choices = []
        self.selected_choice = 0
        self.text_complete = False
        self.text_timer = 0
        self.displayed_text = ""
        self.load_saves()

    def load_saves(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'rb') as f:
                    self.saves = pickle.load(f)
            except:
                self.saves = {}

    def save_game(self):
        self.saves["quick_save"] = {
            "script_index": self.script_index,
            "flags": self.flags.copy()
        }
        with open(self.save_file, 'wb') as f:
            pickle.dump(self.saves, f)
        return True

    def load_game(self):
        if "quick_save" in self.saves:
            data = self.saves["quick_save"]
            self.script_index = data["script_index"]
            self.flags = data["flags"].copy()
            return True
        return False

    def process_script(self):
        if self.script_index >= len(SCRIPT):
            return
        
        step = SCRIPT[self.script_index]
        
        if step["type"] == "scene":
            if "check_flag" in step:
                flag = step["check_flag"]
                invert = flag.startswith("!")
                if invert:
                    flag = flag[1:]
                if (invert and self.flags.get(flag, False)) or (not invert and not self.flags.get(flag, False)):
                    self.script_index += 1
                    self.process_script()
                    return
            
            if "bg" in step:
                self.current_bg = step["bg"]
            
            if "clear_chars" in step:
                for char in characters.values():
                    char.visible = False
            
            if "char" in step:
                char = characters[step["char"]]
                char.visible = True
                if "char_pos" in step:
                    if step["char_pos"] == "left":
                        char.x = 100
                    elif step["char_pos"] == "right":
                        char.x = 650
                if "expression" in step:
                    char.expression = step["expression"]
            
            if "char2" in step:
                char = characters[step["char2"]]
                char.visible = True
                if "char2_pos" in step:
                    if step["char2_pos"] == "left":
                        char.x = 100
                    elif step["char2_pos"] == "right":
                        char.x = 650
            
            if "flag" in step:
                self.flags[step["flag"]] = step["value"]
            
            self.dialog_text = step["text"]
            self.displayed_text = ""
            self.text_complete = False
            self.text_timer = 0
            self.showing_choices = False
        
        elif step["type"] == "choice":
            if step.get("next") == "save":
                self.save_game()
                self.script_index += 1
                self.process_script()
                return
            
            self.showing_choices = True
            self.current_choices = step["choices"]
            self.dialog_text = step["text"]
            self.displayed_text = self.dialog_text
            self.text_complete = True
            self.selected_choice = 0
        
        elif step["type"] == "ending":
            self.dialog_text = step["text"]
            self.displayed_text = ""
            self.text_complete = False
            self.text_timer = 0
            self.showing_choices = False

    def advance(self):
        if self.showing_choices:
            choice = self.current_choices[self.selected_choice]
            if isinstance(choice["next"], int):
                self.script_index = choice["next"]
            else:
                self.script_index += 1
            self.showing_choices = False
            self.process_script()
        else:
            if not self.text_complete:
                self.displayed_text = self.dialog_text
                self.text_complete = True
            else:
                self.script_index += 1
                if self.script_index < len(SCRIPT):
                    self.process_script()

    def update_text(self):
        if not self.text_complete and self.dialog_text:
            self.text_timer += 1
            if self.text_timer >= 3:
                self.text_timer = 0
                if len(self.displayed_text) < len(self.dialog_text):
                    self.displayed_text += self.dialog_text[len(self.displayed_text)]
                else:
                    self.text_complete = True

    def draw_background(self, surface, bg_name):
        color = BACKGROUNDS.get(bg_name, DARK_BLUE)
        surface.fill(color)
        
        if bg_name == "school_gate":
            pygame.draw.rect(surface, (180, 180, 180), (0, 450, WIDTH, 200))
            pygame.draw.rect(surface, (200, 150, 100), (300, 150, 300, 300), 0, 5)
            pygame.draw.rect(surface, (100, 80, 60), (400, 300, 100, 150))
        elif bg_name == "classroom":
            pygame.draw.rect(surface, (150, 150, 150), (0, 450, WIDTH, 200))
            for i in range(5):
                pygame.draw.rect(surface, (200, 150, 100), (100 + i * 150, 350, 100, 80))
            pygame.draw.rect(surface, (100, 150, 200), (50, 100, 200, 120))
        elif bg_name == "rooftop":
            pygame.draw.rect(surface, (150, 150, 150), (0, 400, WIDTH, 250))
            pygame.draw.rect(surface, (100, 100, 100), (0, 380, WIDTH, 40))
        elif bg_name == "park":
            pygame.draw.rect(surface, (100, 180, 100), (0, 450, WIDTH, 200))
            pygame.draw.circle(surface, (100, 80, 50), (200, 350), 40)
            pygame.draw.rect(surface, (80, 60, 30), (190, 350, 20, 100))
            pygame.draw.circle(surface, (100, 80, 50), (700, 350), 40)
            pygame.draw.rect(surface, (80, 60, 30), (690, 350, 20, 100))

    def draw_dialog_box(self, surface):
        box_rect = pygame.Rect(50, 480, WIDTH - 100, 150)
        s = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        surface.blit(s, box_rect.topleft)
        pygame.draw.rect(surface, LIGHT_BLUE, box_rect, 3, 5)

        lines = self.wrap_text(self.displayed_text, box_rect.width - 40)
        y_offset = box_rect.y + 20
        for line in lines:
            text_surf = FONT.render(line, True, WHITE)
            surface.blit(text_surf, (box_rect.x + 20, y_offset))
            y_offset += 35

        if self.text_complete and not self.showing_choices and self.script_index < len(SCRIPT):
            indicator_y = box_rect.y + box_rect.height - 20
            pygame.draw.polygon(surface, YELLOW, [
                (WIDTH//2 - 10, indicator_y - 5),
                (WIDTH//2 + 10, indicator_y - 5),
                (WIDTH//2, indicator_y + 5)
            ])

    def draw_choices(self, surface):
        if not self.showing_choices:
            return
        
        start_y = 150
        for i, choice in enumerate(self.current_choices):
            rect = pygame.Rect(150, start_y + i * 70, WIDTH - 300, 60)
            color = YELLOW if i == self.selected_choice else DARK_GRAY
            pygame.draw.rect(surface, color, rect, 0, 10)
            pygame.draw.rect(surface, WHITE, rect, 2, 10)
            
            text_surf = CHOICE_FONT.render(choice["text"], True, WHITE if i == self.selected_choice else GRAY)
            text_rect = text_surf.get_rect(center=rect.center)
            surface.blit(text_surf, text_rect)

    def draw_menu(self, surface):
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        surface.blit(s, (0, 0))
        
        title = TITLE_FONT.render("校园物语", True, YELLOW)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        menu_items = ["开始游戏", "读取存档", "退出"]
        for i, item in enumerate(menu_items):
            rect = pygame.Rect(WIDTH//2 - 150, 250 + i * 80, 300, 60)
            pygame.draw.rect(surface, DARK_GRAY, rect, 0, 10)
            pygame.draw.rect(surface, WHITE, rect, 2, 10)
            text = CHOICE_FONT.render(item, True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)
        
        return menu_items

    def wrap_text(self, text, max_width):
        words = text.split('\n')
        lines = []
        for paragraph in words:
            current_line = ""
            for char in paragraph:
                test_line = current_line + char
                if FONT.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = char
            if current_line:
                lines.append(current_line)
        return lines

    def run(self):
        clock = pygame.time.Clock()
        state = "menu"
        menu_choice = 0
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if state == "menu":
                        if event.key == pygame.K_UP:
                            menu_choice = (menu_choice - 1) % 3
                        elif event.key == pygame.K_DOWN:
                            menu_choice = (menu_choice + 1) % 3
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            if menu_choice == 0:
                                state = "game"
                                self.script_index = 0
                                self.flags = {}
                                self.process_script()
                            elif menu_choice == 1:
                                if self.load_game():
                                    state = "game"
                                    self.process_script()
                            elif menu_choice == 2:
                                running = False
                    
                    elif state == "game":
                        if event.key == pygame.K_ESCAPE:
                            state = "menu"
                        elif self.showing_choices:
                            if event.key == pygame.K_UP:
                                self.selected_choice = (self.selected_choice - 1) % len(self.current_choices)
                            elif event.key == pygame.K_DOWN:
                                self.selected_choice = (self.selected_choice + 1) % len(self.current_choices)
                            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                                self.advance()
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            self.advance()
                        elif event.key == pygame.K_s:
                            self.save_game()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if state == "menu":
                            mx, my = pygame.mouse.get_pos()
                            for i in range(3):
                                rect = pygame.Rect(WIDTH//2 - 150, 250 + i * 80, 300, 60)
                                if rect.collidepoint(mx, my):
                                    if i == 0:
                                        state = "game"
                                        self.script_index = 0
                                        self.flags = {}
                                        self.process_script()
                                    elif i == 1:
                                        if self.load_game():
                                            state = "game"
                                            self.process_script()
                                    elif i == 2:
                                        running = False
                                    break
                        elif state == "game":
                            self.advance()
            
            if state == "menu":
                SCREEN.fill(DARK_BLUE)
                self.draw_menu(SCREEN)
            else:
                self.update_text()
                self.draw_background(SCREEN, self.current_bg)
                for char in characters.values():
                    char.draw(SCREEN)
                self.draw_dialog_box(SCREEN)
                self.draw_choices(SCREEN)
            
            pygame.display.flip()
            clock.tick(30)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = VisualNovel()
    game.run()
