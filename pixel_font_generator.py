import pygame
import sys
import os

# 初始化Pygame
pygame.init()

# 配置参数
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 8
CELL_SIZE = 40
COLORS = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'gray': (128, 128, 128),
    'light_gray': (200, 200, 200),
    'blue': (50, 100, 200),
    'green': (50, 200, 100),
    'red': (200, 50, 50),
}

# 字符集
CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

class SoundSystem:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
        self.sounds = {}
    
    def generate_sound(self, freq=440, duration=0.1, volume=0.5):
        sample_rate = 44100
        samples = int(sample_rate * duration)
        sound_data = bytearray()
        
        for i in range(samples):
            t = i / sample_rate
            value = int(32767 * volume * (pygame.math.sin(2 * pygame.math.pi * freq * t)))
            sound_data.extend(value.to_bytes(2, 'little', signed=True))
            sound_data.extend(value.to_bytes(2, 'little', signed=True))
        
        sound = pygame.mixer.Sound(sound_data)
        return sound
    
    def play_click(self):
        sound = self.generate_sound(800, 0.05, 0.3)
        sound.play()
    
    def play_success(self):
        sound = self.generate_sound(523, 0.1, 0.3)
        pygame.time.delay(100)
        sound2 = self.generate_sound(659, 0.1, 0.3)
        sound2.play()
    
    def play_error(self):
        sound = self.generate_sound(200, 0.2, 0.3)
        sound.play()

class PixelFontGenerator:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('像素字体生成器')
        
        self.sound_system = SoundSystem()
        
        # 初始化字体数据
        self.font_data = {}
        for char in CHARS:
            self.font_data[char] = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        self.current_char = 'A'
        self.selected_color = COLORS['white']
        self.is_eraser = False
        self.is_drawing = False
        
        # UI元素位置
        self.grid_x = 50
        self.grid_y = 50
        self.char_select_x = 50
        self.char_select_y = 420
        self.preview_x = 450
        self.preview_y = 50
        self.export_button = (650, 520, 120, 40)
        
        # 加载默认字体
        self.load_default_font()
    
    def load_default_font(self):
        default_fonts = {
            'A': [[0,1,1,1,1,1,0,0],
                  [1,0,0,0,0,0,1,0],
                  [1,0,0,0,0,0,1,0],
                  [1,0,0,0,0,0,1,0],
                  [1,1,1,1,1,1,1,0],
                  [1,0,0,0,0,0,1,0],
                  [1,0,0,0,0,0,1,0],
                  [1,0,0,0,0,0,1,0]],
            'B': [[1,1,1,1,1,0,0,0],
                  [1,0,0,0,0,1,0,0],
                  [1,0,0,0,0,1,0,0],
                  [1,1,1,1,1,0,0,0],
                  [1,0,0,0,0,1,0,0],
                  [1,0,0,0,0,1,0,0],
                  [1,0,0,0,0,1,0,0],
                  [1,1,1,1,1,0,0,0]],
            'C': [[0,1,1,1,1,1,0,0],
                  [1,0,0,0,0,0,1,0],
                  [1,0,0,0,0,0,0,0],
                  [1,0,0,0,0,0,0,0],
                  [1,0,0,0,0,0,0,0],
                  [1,0,0,0,0,0,0,0],
                  [1,0,0,0,0,0,1,0],
                  [0,1,1,1,1,1,0,0]],
        }
        
        for char, data in default_fonts.items():
            if char in self.font_data:
                self.font_data[char] = [row[:] for row in data]
    
    def draw_grid(self):
        grid = self.font_data[self.current_char]
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(
                    self.grid_x + x * CELL_SIZE,
                    self.grid_y + y * CELL_SIZE,
                    CELL_SIZE - 1,
                    CELL_SIZE - 1
                )
                color = COLORS['white'] if grid[y][x] else COLORS['black']
                pygame.draw.rect(self.screen, color, rect)
    
    def draw_char_selector(self):
        pygame.draw.rect(self.screen, COLORS['gray'], 
                        (self.char_select_x - 5, self.char_select_y - 5, 350, 50), 2)
        
        for i, char in enumerate(CHARS):
            x = self.char_select_x + i * 28
            y = self.char_select_y
            rect = pygame.Rect(x, y, 24, 24)
            
            if char == self.current_char:
                pygame.draw.rect(self.screen, COLORS['blue'], rect)
            
            pygame.draw.rect(self.screen, COLORS['white'], rect, 1)
            
            # 绘制字符预览
            font_data = self.font_data[char]
            for fy in range(4):
                for fx in range(4):
                    if font_data[fy * 2][fx * 2] or font_data[fy * 2][fx * 2 + 1] or \
                       font_data[fy * 2 + 1][fx * 2] or font_data[fy * 2 + 1][fx * 2 + 1]:
                        dot_rect = pygame.Rect(x + fx * 5 + 2, y + fy * 5 + 2, 4, 4)
                        pygame.draw.rect(self.screen, COLORS['white'], dot_rect)
    
    def draw_preview(self):
        pygame.draw.rect(self.screen, COLORS['gray'], 
                        (self.preview_x - 5, self.preview_y - 5, 300, 250), 2)
        
        # 标题
        font = pygame.font.Font(None, 24)
        text = font.render('字体预览', True, COLORS['white'])
        self.screen.blit(text, (self.preview_x, self.preview_y))
        
        # 当前字符放大预览
        char_preview_y = self.preview_y + 40
        grid = self.font_data[self.current_char]
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if grid[y][x]:
                    rect = pygame.Rect(
                        self.preview_x + x * 15,
                        char_preview_y + y * 15,
                        14, 14
                    )
                    pygame.draw.rect(self.screen, COLORS['white'], rect)
        
        # 所有字符预览
        all_chars_y = self.preview_y + 170
        for i, char in enumerate(CHARS):
            x = self.preview_x + (i % 13) * 22
            y = all_chars_y + (i // 13) * 18
            
            font_data = self.font_data[char]
            for fy in range(4):
                for fx in range(4):
                    if font_data[fy * 2][fx * 2] or font_data[fy * 2][fx * 2 + 1] or \
                       font_data[fy * 2 + 1][fx * 2] or font_data[fy * 2 + 1][fx * 2 + 1]:
                        dot_rect = pygame.Rect(x + fx * 3 + 1, y + fy * 3 + 1, 2, 2)
                        pygame.draw.rect(self.screen, COLORS['light_gray'], dot_rect)
    
    def draw_ui(self):
        # 清除屏幕
        self.screen.fill(COLORS['black'])
        
        # 绘制网格
        self.draw_grid()
        
        # 绘制字符选择器
        self.draw_char_selector()
        
        # 绘制预览
        self.draw_preview()
        
        # 绘制按钮
        pygame.draw.rect(self.screen, COLORS['green'], self.export_button)
        font = pygame.font.Font(None, 24)
        text = font.render('导出字体', True, COLORS['black'])
        text_rect = text.get_rect(center=(self.export_button[0] + self.export_button[2]//2, 
                                          self.export_button[1] + self.export_button[3]//2))
        self.screen.blit(text, text_rect)
        
        # 绘制当前字符显示
        font = pygame.font.Font(None, 36)
        text = font.render(f'当前字符: {self.current_char}', True, COLORS['white'])
        self.screen.blit(text, (50, 380))
        
        # 绘制提示
        font = pygame.font.Font(None, 18)
        text = font.render('左键绘制 | 右键擦除 | 点击字符选择', True, COLORS['gray'])
        self.screen.blit(text, (50, 520))
        
        pygame.display.flip()
    
    def handle_mouse_click(self, pos, button):
        x, y = pos
        
        # 检查网格点击
        if (self.grid_x <= x <= self.grid_x + GRID_SIZE * CELL_SIZE and
            self.grid_y <= y <= self.grid_y + GRID_SIZE * CELL_SIZE):
            grid_x = (x - self.grid_x) // CELL_SIZE
            grid_y = (y - self.grid_y) // CELL_SIZE
            
            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                if button == pygame.BUTTON_LEFT:
                    self.font_data[self.current_char][grid_y][grid_x] = 1
                    self.sound_system.play_click()
                elif button == pygame.BUTTON_RIGHT:
                    self.font_data[self.current_char][grid_y][grid_x] = 0
                    self.sound_system.play_click()
        
        # 检查字符选择器点击
        elif (self.char_select_x <= x <= self.char_select_x + 350 and
              self.char_select_y <= y <= self.char_select_y + 24):
            index = (x - self.char_select_x) // 28
            if 0 <= index < len(CHARS):
                self.current_char = CHARS[index]
                self.sound_system.play_click()
        
        # 检查导出按钮点击
        elif (self.export_button[0] <= x <= self.export_button[0] + self.export_button[2] and
              self.export_button[1] <= y <= self.export_button[1] + self.export_button[3]):
            self.export_font()
    
    def handle_mouse_drag(self, pos):
        x, y = pos
        
        if (self.grid_x <= x <= self.grid_x + GRID_SIZE * CELL_SIZE and
            self.grid_y <= y <= self.grid_y + GRID_SIZE * CELL_SIZE):
            grid_x = (x - self.grid_x) // CELL_SIZE
            grid_y = (y - self.grid_y) // CELL_SIZE
            
            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                if pygame.mouse.get_pressed()[0]:
                    self.font_data[self.current_char][grid_y][grid_x] = 1
                elif pygame.mouse.get_pressed()[2]:
                    self.font_data[self.current_char][grid_y][grid_x] = 0
    
    def export_font(self):
        output = "PIXEL_FONT = {\n"
        for char in CHARS:
            output += f"    '{char}': [\n"
            for row in self.font_data[char]:
                output += f"        {row},\n"
            output += "    ],\n"
        output += "}\n"
        
        # 保存到文件
        with open('pixel_font_data.py', 'w', encoding='utf-8') as f:
            f.write(output)
        
        self.sound_system.play_success()
        print("字体数据已导出到 pixel_font_data.py")
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos, event.button)
                    self.is_drawing = True
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.is_drawing = False
                
                elif event.type == pygame.MOUSEMOTION:
                    if self.is_drawing:
                        self.handle_mouse_drag(event.pos)
            
            self.draw_ui()
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    generator = PixelFontGenerator()
    generator.run()
