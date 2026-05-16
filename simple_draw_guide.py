import pygame
import sys
import os
import math
from pygame.locals import *

# 初始化 pygame
pygame.init()

# 初始化音频 mixer
try:
    pygame.mixer.init()
    sound_enabled = True
except pygame.error:
    sound_enabled = False

# 音效生成函数
def generate_sound(frequency, duration, sample_rate=44100, volume=0.5):
    if not sound_enabled:
        return None
    samples = int(sample_rate * duration)
    sound_data = bytearray()
    for i in range(samples):
        t = i / sample_rate
        value = int(128 + 127 * math.sin(2 * math.pi * frequency * t))
        sound_data.append(value)
        sound_data.append(value)
    sound = pygame.mixer.Sound(sound_data)
    sound.set_volume(volume)
    return sound

# 创建音效
click_sound = generate_sound(800, 0.1)
success_sound = generate_sound(600, 0.2)
complete_sound = generate_sound(523, 0.15)
complete_sound2 = generate_sound(659, 0.15)
complete_sound3 = generate_sound(784, 0.2)

# 空音效播放函数
def play_sound(sound):
    if sound and sound_enabled:
        try:
            sound.play()
        except pygame.error:
            pass

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)

COLORS = [BLACK, RED, GREEN, BLUE, YELLOW, ORANGE, PINK, PURPLE, BROWN, GRAY]
COLOR_NAMES = ["黑色", "红色", "绿色", "蓝色", "黄色", "橙色", "粉色", "紫色", "棕色", "灰色"]

# 模板数据 - 简笔画分步教程
TEMPLATES = {
    "小猫": {
        "steps": [
            {"text": "第一步：画一个圆形作为小猫的头", "draw": [(200, 150), (200, 150, 80, 0, 360)]},
            {"text": "第二步：画两个三角形耳朵", "draw": [(150, 100), (170, 140), (130, 130), (190, 110), (170, 140), (150, 130)]},
            {"text": "第三步：画小猫的眼睛", "draw": [(170, 140, 15, 0, 360), (230, 140, 15, 0, 360), (173, 140, 5, 0, 360), (233, 140, 5, 0, 360)]},
            {"text": "第四步：画小猫的鼻子和嘴巴", "draw": [(200, 165), (200, 180), (190, 170), (200, 165), (210, 170)]},
            {"text": "第五步：画小猫的胡须", "draw": [(140, 155), (165, 160), (140, 165), (165, 165), (140, 175), (165, 170), (235, 160), (260, 155), (235, 165), (260, 165), (235, 170), (260, 175)]},
            {"text": "第六步：画小猫的身体", "draw": [(200, 230), (200, 230, 70, 0, 360)]},
            {"text": "第七步：画小猫的腿和尾巴", "draw": [(150, 280), (140, 320), (160, 320), (250, 280), (240, 320), (260, 320), (270, 210), (320, 180), (330, 160)]}
        ],
        "color_hints": [{"area": [(170, 140), (170, 140, 15, 0, 360)], "color": YELLOW}]
    },
    "花朵": {
        "steps": [
            {"text": "第一步：画花朵的茎", "draw": [(200, 350), (200, 200)]},
            {"text": "第二步：画左边的叶子", "draw": [(200, 280), (150, 300), (160, 270)]},
            {"text": "第三步：画右边的叶子", "draw": [(200, 280), (250, 300), (240, 270)]},
            {"text": "第四步：画花瓣的中心", "draw": [(200, 160), (200, 160, 25, 0, 360)]},
            {"text": "第五步：画第一层花瓣", "draw": [(200, 135), (200, 135, 20, 0, 360), (220, 150), (220, 150, 20, 0, 360), (200, 185), (200, 185, 20, 0, 360), (180, 150), (180, 150, 20, 0, 360)]},
            {"text": "第六步：画第二层花瓣", "draw": [(215, 125), (215, 125, 15, 0, 360), (185, 125), (185, 125, 15, 0, 360), (225, 170), (225, 170, 15, 0, 360), (175, 170), (175, 170, 15, 0, 360)]}
        ],
        "color_hints": [{"area": [(200, 160), (200, 160, 25, 0, 360)], "color": YELLOW}]
    },
    "汽车": {
        "steps": [
            {"text": "第一步：画汽车的车身", "draw": [(150, 200), (350, 200), (340, 260), (160, 260)]},
            {"text": "第二步：画汽车的车顶", "draw": [(180, 200), (320, 200), (310, 240), (190, 240)]},
            {"text": "第三步：画前车轮", "draw": [(220, 260), (220, 260, 25, 0, 360)]},
            {"text": "第四步：画后车轮", "draw": [(300, 260), (300, 260, 25, 0, 360)]},
            {"text": "第五步：画车窗", "draw": [(200, 210), (300, 210), (295, 235), (205, 235)]},
            {"text": "第六步：画车灯", "draw": [(340, 230), (350, 225), (350, 245)]}
        ],
        "color_hints": []
    },
    "太阳": {
        "steps": [
            {"text": "第一步：画太阳的脸", "draw": [(200, 200), (200, 200, 60, 0, 360)]},
            {"text": "第二步：画太阳的眼睛", "draw": [(180, 190, 8, 0, 360), (220, 190, 8, 0, 360), (183, 190, 3, 0, 360), (223, 190, 3, 0, 360)]},
            {"text": "第三步：画太阳的微笑", "draw": [(170, 220), (180, 230), (200, 235), (220, 230), (230, 220)]},
            {"text": "第四步：画太阳的光芒", "draw": [(200, 80), (200, 120), (200, 280), (200, 320), (80, 200), (120, 200), (280, 200), (320, 200), (127, 127), (145, 145), (255, 255), (233, 233), (127, 273), (145, 255), (255, 145), (233, 165)]}
        ],
        "color_hints": [{"area": [(200, 200), (200, 200, 60, 0, 360)], "color": YELLOW}]
    },
    "房子": {
        "steps": [
            {"text": "第一步：画房子的墙", "draw": [(150, 300), (350, 300), (350, 150), (150, 150)]},
            {"text": "第二步：画房子的屋顶", "draw": [(130, 170), (250, 80), (370, 170)]},
            {"text": "第三步：画房子的门", "draw": [(220, 300), (220, 220), (280, 220), (280, 300)]},
            {"text": "第四步：画门把手", "draw": [(270, 260), (270, 260, 5, 0, 360)]},
            {"text": "第五步：画左窗户", "draw": [(170, 180), (210, 180), (210, 220), (170, 220), (190, 180), (190, 220), (170, 200), (210, 200)]},
            {"text": "第六步：画右窗户", "draw": [(290, 180), (330, 180), (330, 220), (290, 220), (310, 180), (310, 220), (290, 200), (330, 200)]}
        ],
        "color_hints": []
    },
    "小鸟": {
        "steps": [
            {"text": "第一步：画小鸟的身体", "draw": [(200, 200), (200, 200, 50, 0, 360)]},
            {"text": "第二步：画小鸟的头", "draw": [(170, 160), (170, 160, 35, 0, 360)]},
            {"text": "第三步：画小鸟的嘴巴", "draw": [(145, 165), (130, 160), (130, 170)]},
            {"text": "第四步：画小鸟的眼睛", "draw": [(160, 155, 6, 0, 360), (162, 155, 2, 0, 360)]},
            {"text": "第五步：画小鸟的翅膀", "draw": [(210, 190), (250, 180), (240, 210)]},
            {"text": "第六步：画小鸟的尾巴", "draw": [(250, 200), (290, 180), (280, 200), (290, 220)]},
            {"text": "第七步：画小鸟的脚", "draw": [(185, 245), (175, 265), (185, 260), (185, 245), (195, 265), (185, 260)]}
        ],
        "color_hints": []
    }
}

class DrawGuide:
    def __init__(self):
        self.screen_width = 450
        self.screen_height = 450
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("儿童简笔画教学")
        
        self.current_mode = "menu"  # menu, tutorial, free_draw
        self.current_template = None
        self.current_step = 0
        self.selected_color = BLACK
        self.brush_size = 3
        
        self.drawing = []
        self.guide_layer = []
        
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        self.clock = pygame.time.Clock()
        
    def draw_menu(self):
        self.screen.fill(WHITE)
        
        title_text = self.font.render("儿童简笔画教学", True, BLACK)
        title_rect = title_text.get_rect(center=(self.screen_width//2, 50))
        self.screen.blit(title_text, title_rect)
        
        y_pos = 120
        templates = list(TEMPLATES.keys())
        for i, template in enumerate(templates):
            button_rect = pygame.Rect(100, y_pos, 250, 40)
            pygame.draw.rect(self.screen, BLUE, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            
            text = self.font.render(f"{i+1}. {template}", True, WHITE)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            
            y_pos += 60
        
        free_draw_button = pygame.Rect(100, y_pos, 250, 40)
        pygame.draw.rect(self.screen, GREEN, free_draw_button)
        pygame.draw.rect(self.screen, BLACK, free_draw_button, 2)
        text = self.font.render("自由绘画", True, WHITE)
        text_rect = text.get_rect(center=free_draw_button.center)
        self.screen.blit(text, text_rect)
        
        pygame.display.flip()
        
    def draw_tutorial(self):
        self.screen.fill(WHITE)
        
        # 绘制已完成的步骤
        for i in range(self.current_step):
            for draw_info in TEMPLATES[self.current_template]["steps"][i]["draw"]:
                if len(draw_info) == 2:
                    pygame.draw.line(self.screen, BLACK, draw_info[0], draw_info[1], self.brush_size)
                elif len(draw_info) == 5:
                    pygame.draw.circle(self.screen, BLACK, draw_info[:2], draw_info[2], self.brush_size)
        
        # 绘制当前步骤的引导
        if self.current_step < len(TEMPLATES[self.current_template]["steps"]):
            current_step_data = TEMPLATES[self.current_template]["steps"][self.current_step]
            for draw_info in current_step_data["draw"]:
                if len(draw_info) == 2:
                    pygame.draw.line(self.screen, GRAY, draw_info[0], draw_info[1], self.brush_size)
                elif len(draw_info) == 5:
                    pygame.draw.circle(self.screen, GRAY, draw_info[:2], draw_info[2], self.brush_size)
        
        # 绘制用户已画的内容
        for stroke in self.drawing:
            for i in range(len(stroke)-1):
                pygame.draw.line(self.screen, stroke[0], stroke[1][i], stroke[1][i+1], stroke[2])
        
        # 显示步骤文字
        if self.current_step < len(TEMPLATES[self.current_template]["steps"]):
            step_text = self.font.render(current_step_data["text"], True, BLACK)
            text_rect = step_text.get_rect(center=(self.screen_width//2, 420))
            pygame.draw.rect(self.screen, WHITE, (50, 380, 350, 60))
            self.screen.blit(step_text, text_rect)
        
        # 进度条
        total_steps = len(TEMPLATES[self.current_template]["steps"])
        progress_width = (self.current_step / total_steps) * 400
        pygame.draw.rect(self.screen, GRAY, (25, 10, 400, 15))
        pygame.draw.rect(self.screen, GREEN, (25, 10, progress_width, 15))
        
        # 按钮
        prev_button = pygame.Rect(25, 350, 100, 30)
        pygame.draw.rect(self.screen, ORANGE, prev_button)
        text = self.small_font.render("上一步", True, WHITE)
        self.screen.blit(text, (prev_button.x + 20, prev_button.y + 5))
        
        next_button = pygame.Rect(325, 350, 100, 30)
        pygame.draw.rect(self.screen, BLUE, next_button)
        text = self.small_font.render("下一步", True, WHITE)
        self.screen.blit(text, (next_button.x + 20, next_button.y + 5))
        
        menu_button = pygame.Rect(175, 350, 100, 30)
        pygame.draw.rect(self.screen, RED, menu_button)
        text = self.small_font.render("返回菜单", True, WHITE)
        self.screen.blit(text, (menu_button.x + 15, menu_button.y + 5))
        
        pygame.display.flip()
        
    def draw_free_draw(self):
        self.screen.fill(WHITE)
        
        # 绘制用户已画的内容
        for stroke in self.drawing:
            for i in range(len(stroke[1])-1):
                pygame.draw.line(self.screen, stroke[0], stroke[1][i], stroke[1][i+1], stroke[2])
        
        # 颜色选择
        color_x = 25
        color_y = 400
        for i, color in enumerate(COLORS):
            pygame.draw.circle(self.screen, color, (color_x + i * 40, color_y), 15)
            pygame.draw.circle(self.screen, BLACK, (color_x + i * 40, color_y), 15, 2)
        
        # 当前颜色指示
        pygame.draw.circle(self.screen, self.selected_color, (25 + COLORS.index(self.selected_color) * 40, color_y), 20, 3)
        
        # 按钮
        clear_button = pygame.Rect(25, 350, 100, 30)
        pygame.draw.rect(self.screen, RED, clear_button)
        text = self.small_font.render("清空画布", True, WHITE)
        self.screen.blit(text, (clear_button.x + 10, clear_button.y + 5))
        
        save_button = pygame.Rect(175, 350, 100, 30)
        pygame.draw.rect(self.screen, GREEN, save_button)
        text = self.small_font.render("保存作品", True, WHITE)
        self.screen.blit(text, (save_button.x + 10, save_button.y + 5))
        
        menu_button = pygame.Rect(325, 350, 100, 30)
        pygame.draw.rect(self.screen, BLUE, menu_button)
        text = self.small_font.render("返回菜单", True, WHITE)
        self.screen.blit(text, (menu_button.x + 15, menu_button.y + 5))
        
        # 笔刷大小
        brush_text = self.small_font.render(f"笔刷大小: {self.brush_size}", True, BLACK)
        self.screen.blit(brush_text, (25, 320))
        
        pygame.display.flip()
        
    def handle_menu_click(self, pos):
        y_pos = 120
        templates = list(TEMPLATES.keys())
        for i, template in enumerate(templates):
            button_rect = pygame.Rect(100, y_pos, 250, 40)
            if button_rect.collidepoint(pos):
                play_sound(click_sound)
                self.current_template = template
                self.current_step = 0
                self.drawing = []
                self.current_mode = "tutorial"
                return
            y_pos += 60
        
        free_draw_button = pygame.Rect(100, y_pos, 250, 40)
        if free_draw_button.collidepoint(pos):
            play_sound(click_sound)
            self.current_mode = "free_draw"
            self.drawing = []
        
    def handle_tutorial_click(self, pos):
        prev_button = pygame.Rect(25, 350, 100, 30)
        next_button = pygame.Rect(325, 350, 100, 30)
        menu_button = pygame.Rect(175, 350, 100, 30)
        
        if prev_button.collidepoint(pos):
            play_sound(click_sound)
            if self.current_step > 0:
                self.current_step -= 1
                self.drawing = []
        elif next_button.collidepoint(pos):
            play_sound(click_sound)
            if self.current_step < len(TEMPLATES[self.current_template]["steps"]):
                self.current_step += 1
                self.drawing = []
                if self.current_step == len(TEMPLATES[self.current_template]["steps"]):
                    play_sound(complete_sound)
                    pygame.time.wait(150)
                    play_sound(complete_sound2)
                    pygame.time.wait(150)
                    play_sound(complete_sound3)
        elif menu_button.collidepoint(pos):
            play_sound(click_sound)
            self.current_mode = "menu"
        
    def handle_free_draw_click(self, pos):
        clear_button = pygame.Rect(25, 350, 100, 30)
        save_button = pygame.Rect(175, 350, 100, 30)
        menu_button = pygame.Rect(325, 350, 100, 30)
        
        if clear_button.collidepoint(pos):
            play_sound(click_sound)
            self.drawing = []
        elif save_button.collidepoint(pos):
            play_sound(success_sound)
            filename = f"drawing_{pygame.time.get_ticks()}.png"
            pygame.image.save(self.screen, filename)
            print(f"作品已保存为: {filename}")
        elif menu_button.collidepoint(pos):
            play_sound(click_sound)
            self.current_mode = "menu"
        
        # 检查颜色选择
        color_x = 25
        color_y = 400
        for i, color in enumerate(COLORS):
            if math.hypot(pos[0] - (color_x + i * 40), pos[1] - color_y) <= 15:
                play_sound(click_sound)
                self.selected_color = color
                break
        
    def run(self):
        drawing = False
        current_stroke = []
        
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    
                    if self.current_mode == "menu":
                        self.handle_menu_click(pos)
                    elif self.current_mode == "tutorial":
                        if pos[1] < 350:
                            drawing = True
                            current_stroke = [(pos[0], pos[1])]
                        else:
                            self.handle_tutorial_click(pos)
                    elif self.current_mode == "free_draw":
                        if pos[1] < 350:
                            drawing = True
                            current_stroke = [(pos[0], pos[1])]
                        else:
                            self.handle_free_draw_click(pos)
                            
                elif event.type == MOUSEMOTION:
                    if drawing:
                        current_stroke.append(pygame.mouse.get_pos())
                        
                elif event.type == MOUSEBUTTONUP:
                    if drawing and len(current_stroke) > 1:
                        self.drawing.append((self.selected_color, current_stroke, self.brush_size))
                    drawing = False
                    current_stroke = []
                    
                elif event.type == KEYDOWN:
                    if self.current_mode == "free_draw":
                        if event.key == K_PLUS or event.key == K_EQUALS:
                            self.brush_size = min(self.brush_size + 1, 10)
                        elif event.key == K_MINUS:
                            self.brush_size = max(self.brush_size - 1, 1)
            
            if self.current_mode == "menu":
                self.draw_menu()
            elif self.current_mode == "tutorial":
                self.draw_tutorial()
            elif self.current_mode == "free_draw":
                self.draw_free_draw()
            
            self.clock.tick(60)

if __name__ == "__main__":
    game = DrawGuide()
    game.run()
