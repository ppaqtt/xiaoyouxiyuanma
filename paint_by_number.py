import pygame
import os
import sys
import random
import math

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

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
PIXEL_SIZE = 20
CANVAS_SIZE = 25
CANVAS_PIXEL_WIDTH = CANVAS_SIZE * PIXEL_SIZE
CANVAS_PIXEL_HEIGHT = CANVAS_SIZE * PIXEL_SIZE

WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_GRAY = (240, 240, 240)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 50)
ORANGE = (255, 165, 50)
PURPLE = (150, 50, 200)
PINK = (255, 150, 200)
BROWN = (139, 69, 19)
CYAN = (50, 255, 255)

COLORS = [
    (255, 255, 255),
    (255, 100, 100),
    (100, 255, 100),
    (100, 100, 255),
    (255, 255, 100),
    (255, 150, 50),
    (150, 50, 200),
    (255, 150, 200),
    (150, 100, 50),
    (100, 200, 255),
    (200, 200, 200),
    (50, 150, 50)
]

PAINTINGS = [
    {
        "name": "小房子",
        "colors": 6,
        "data": [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,3,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,3,3,3,3,3,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,3,3,3,3,3,3,3,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,2,2,2,2,2,2,2,2,2,2,2,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,1,1,4,4,1,1,1,4,4,1,1,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,1,1,4,4,1,1,1,4,4,1,1,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,5,5,1,1,1,1,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,5,5,1,1,1,1,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,5,5,1,1,1,1,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,5,5,1,1,1,1,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ]
    },
    {
        "name": "太阳花",
        "colors": 5,
        "data": [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,3,3,3,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,3,3,3,3,3,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,3,3,3,3,3,3,3,3,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,3,3,3,3,3,3,3,3,3,3,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,3,3,3,3,3,2,2,2,3,3,3,3,0,0,0,0,0,0,0,0],
            [0,0,0,0,3,3,3,3,2,2,2,2,2,2,3,3,3,3,0,0,0,0,0,0,0],
            [0,0,0,0,3,3,3,2,2,2,2,2,2,2,2,3,3,3,0,0,0,0,0,0,0],
            [0,0,3,3,3,3,2,2,2,2,1,1,2,2,2,3,3,3,3,3,0,0,0,0,0],
            [0,0,3,3,3,3,2,2,2,1,1,1,1,2,2,3,3,3,3,3,0,0,0,0,0],
            [0,0,0,0,3,3,2,2,2,1,1,1,1,2,2,3,3,0,0,0,0,0,0,0,0],
            [0,0,0,0,3,3,2,2,2,2,1,1,2,2,2,3,3,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,3,3,3,2,2,2,2,2,3,3,3,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,3,3,3,2,2,2,3,3,3,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,4,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,5,5,0,0,4,4,4,4,4,0,0,5,5,0,0,0,0,0,0,0,0],
            [0,0,0,5,5,5,5,0,4,4,4,4,4,0,5,5,5,5,0,0,0,0,0,0,0],
            [0,0,5,5,5,5,5,5,4,4,4,4,4,5,5,5,5,5,5,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ]
    },
    {
        "name": "爱心",
        "colors": 4,
        "data": [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0],
            [0,0,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0],
            [0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ]
    },
    {
        "name": "小猫",
        "colors": 7,
        "data": [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0],
            [0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0],
            [0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0],
            [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
            [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
            [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
            [0,0,1,1,1,1,2,2,1,1,1,1,1,1,1,2,2,1,1,1,1,1,0,0,0],
            [0,0,1,1,1,1,2,2,1,1,1,1,1,1,1,2,2,1,1,1,1,1,0,0,0],
            [0,0,1,1,1,1,1,1,1,1,3,3,3,1,1,1,1,1,1,1,1,1,0,0,0],
            [0,0,1,1,1,1,1,1,1,1,3,3,3,1,1,1,1,1,1,1,1,1,0,0,0],
            [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
            [0,0,1,1,1,1,1,1,1,1,1,4,1,1,1,1,1,1,1,1,1,1,0,0,0],
            [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
            [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
            [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0],
            [0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0],
            [0,0,0,0,0,0,5,5,5,0,0,0,0,0,5,5,5,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,5,5,5,0,0,0,0,0,5,5,5,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,5,5,5,0,0,0,0,0,5,5,5,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ]
    }
]

def generate_sound(frequency, duration, volume=0.5):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    sound_buffer = bytearray()
    
    for i in range(n_samples):
        t = i / sample_rate
        value = int(volume * 32767 * math.sin(2 * math.pi * frequency * t))
        sound_buffer.append(value & 0xff)
        sound_buffer.append((value >> 8) & 0xff)
    
    return pygame.mixer.Sound(buffer=sound_buffer)

class PaintByNumber:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("数字油画 - Paint By Number")
        self.clock = pygame.time.Clock()
        self.font = get_chinese_font(28)
        self.large_font = get_chinese_font(48)
        
        self.click_sound = generate_sound(800, 0.1, 0.3)
        self.complete_sound = generate_sound(523, 0.15, 0.4)
        
        self.current_painting = 0
        self.selected_color = 1
        self.colored = []
        self.celebration = False
        self.celebration_particles = []
        self.celebration_time = 0
        
        self.load_painting()
        
        self.button_rects = {
            "prev": pygame.Rect(20, 620, 120, 40),
            "next": pygame.Rect(160, 620, 120, 40),
            "reset": pygame.Rect(300, 620, 120, 40)
        }
    
    def load_painting(self):
        painting = PAINTINGS[self.current_painting]
        self.colored = [[False for _ in range(CANVAS_SIZE)] for _ in range(CANVAS_SIZE)]
        self.selected_color = 1
        self.celebration = False
        self.celebration_particles = []
    
    def get_completion(self):
        painting = PAINTINGS[self.current_painting]
        total = 0
        colored = 0
        for y in range(CANVAS_SIZE):
            for x in range(CANVAS_SIZE):
                if painting["data"][y][x] != 0:
                    total += 1
                    if self.colored[y][x]:
                        colored += 1
        return colored, total
    
    def is_complete(self):
        colored, total = self.get_completion()
        return colored == total and total > 0
    
    def draw_pixel(self, surface, x, y, color, draw_number=True):
        painting = PAINTINGS[self.current_painting]
        rect = pygame.Rect(x, y, PIXEL_SIZE, PIXEL_SIZE)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, GRAY, rect, 1)
        
        if draw_number and not self.colored[y // PIXEL_SIZE][x // PIXEL_SIZE]:
            num = painting["data"][y // PIXEL_SIZE][x // PIXEL_SIZE]
            if num != 0:
                text = self.font.render(str(num), True, DARK_GRAY)
                text_rect = text.get_rect(center=(x + PIXEL_SIZE // 2, y + PIXEL_SIZE // 2))
                surface.blit(text, text_rect)
    
    def draw_canvas(self):
        canvas_x = 30
        canvas_y = 30
        painting = PAINTINGS[self.current_painting]
        
        for y in range(CANVAS_SIZE):
            for x in range(CANVAS_SIZE):
                px = canvas_x + x * PIXEL_SIZE
                py = canvas_y + y * PIXEL_SIZE
                num = painting["data"][y][x]
                
                if num == 0:
                    color = LIGHT_GRAY
                elif self.colored[y][x]:
                    color = COLORS[num]
                else:
                    color = WHITE
                
                self.draw_pixel(self.screen, px, py, color)
    
    def draw_color_palette(self):
        palette_x = 580
        palette_y = 30
        painting = PAINTINGS[self.current_painting]
        
        title = self.font.render("颜色选择", True, BLACK)
        self.screen.blit(title, (palette_x, palette_y))
        
        for i in range(1, painting["colors"] + 1):
            row = (i - 1) // 3
            col = (i - 1) % 3
            cx = palette_x + col * 60
            cy = palette_y + 40 + row * 60
            
            rect = pygame.Rect(cx, cy, 50, 50)
            pygame.draw.rect(self.screen, COLORS[i], rect)
            
            if i == self.selected_color:
                pygame.draw.rect(self.screen, BLACK, rect, 4)
            else:
                pygame.draw.rect(self.screen, GRAY, rect, 2)
            
            text = self.font.render(str(i), True, BLACK if COLORS[i][0] + COLORS[i][1] + COLORS[i][2] > 382 else WHITE)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
    
    def draw_ui(self):
        painting = PAINTINGS[self.current_painting]
        
        name_text = self.large_font.render(painting["name"], True, BLACK)
        self.screen.blit(name_text, (30, 560))
        
        colored, total = self.get_completion()
        percent = int((colored / total * 100) if total > 0 else 0)
        progress_text = self.font.render(f"完成度: {colored}/{total} ({percent}%)", True, BLUE)
        self.screen.blit(progress_text, (30, 590))
        
        for btn_name, rect in self.button_rects.items():
            pygame.draw.rect(self.screen, GRAY, rect, border_radius=5)
            pygame.draw.rect(self.screen, DARK_GRAY, rect, 2, border_radius=5)
            
            if btn_name == "prev":
                text = "上一幅"
            elif btn_name == "next":
                text = "下一幅"
            else:
                text = "重置"
            
            text_surf = self.font.render(text, True, BLACK)
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)
    
    def draw_celebration(self):
        if not self.celebration:
            return
        
        for particle in self.celebration_particles:
            pygame.draw.circle(self.screen, particle["color"], (int(particle["x"]), int(particle["y"])), particle["size"])
    
    def update_celebration(self):
        if not self.celebration:
            return
        
        self.celebration_time += 1
        
        if len(self.celebration_particles) < 100 and self.celebration_time % 5 == 0:
            for _ in range(5):
                self.celebration_particles.append({
                    "x": random.randint(0, SCREEN_WIDTH),
                    "y": SCREEN_HEIGHT + 10,
                    "vx": random.uniform(-3, 3),
                    "vy": random.uniform(-10, -5),
                    "size": random.randint(5, 15),
                    "color": random.choice(COLORS[1:])
                })
        
        for particle in self.celebration_particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += 0.3
        
        self.celebration_particles = [p for p in self.celebration_particles if p["y"] < SCREEN_HEIGHT + 50]
        
        if self.celebration_time > 180:
            self.celebration = False
            self.celebration_particles = []
            self.celebration_time = 0
    
    def handle_click(self, pos):
        x, y = pos
        
        for btn_name, rect in self.button_rects.items():
            if rect.collidepoint(pos):
                if btn_name == "prev":
                    self.current_painting = (self.current_painting - 1) % len(PAINTINGS)
                    self.load_painting()
                elif btn_name == "next":
                    self.current_painting = (self.current_painting + 1) % len(PAINTINGS)
                    self.load_painting()
                elif btn_name == "reset":
                    self.load_painting()
                return
        
        palette_x = 580
        palette_y = 70
        painting = PAINTINGS[self.current_painting]
        
        for i in range(1, painting["colors"] + 1):
            row = (i - 1) // 3
            col = (i - 1) % 3
            cx = palette_x + col * 60
            cy = palette_y + row * 60
            
            if cx <= x <= cx + 50 and cy <= y <= cy + 50:
                self.selected_color = i
                self.click_sound.play()
                return
        
        canvas_x = 30
        canvas_y = 30
        
        if canvas_x <= x <= canvas_x + CANVAS_PIXEL_WIDTH and canvas_y <= y <= canvas_y + CANVAS_PIXEL_HEIGHT:
            px = (x - canvas_x) // PIXEL_SIZE
            py = (y - canvas_y) // PIXEL_SIZE
            
            if 0 <= px < CANVAS_SIZE and 0 <= py < CANVAS_SIZE:
                painting = PAINTINGS[self.current_painting]
                num = painting["data"][py][px]
                
                if num != 0 and num == self.selected_color and not self.colored[py][px]:
                    self.colored[py][px] = True
                    self.click_sound.play()
                    
                    if self.is_complete():
                        self.celebration = True
                        self.celebration_time = 0
                        self.complete_sound.play()
    
    def run(self):
        running = True
        while running:
            self.screen.fill(WHITE)
            
            self.draw_canvas()
            self.draw_color_palette()
            self.draw_ui()
            self.update_celebration()
            self.draw_celebration()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PaintByNumber()
    game.run()
