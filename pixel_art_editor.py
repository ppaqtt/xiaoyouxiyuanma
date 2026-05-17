import pygame
import sys
import os
import struct
from pygame.locals import *


class PixelArtEditor:
    def __init__(self):
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

self.SCREEN_WIDTH = 1000
        self.SCREEN_HEIGHT = 700
        self.GRID_SIZE = 16
        self.PIXEL_SIZE = 30
        self.CANVAS_WIDTH = self.GRID_SIZE * self.PIXEL_SIZE
        self.CANVAS_HEIGHT = self.GRID_SIZE * self.PIXEL_SIZE
        
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption('像素艺术编辑器')
        
        self.clock = pygame.time.Clock()
        self.font = get_chinese_font(24)
        self.title_font = get_chinese_font(32)
        
        self.canvas = [[(255, 255, 255) for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        
        self.current_color = (0, 0, 0)
        self.brush_size = 1
        self.show_grid = True
        self.drawing = False
        self.erasing = False
        
        self.colors = [
            (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0),
            (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255),
            (128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 0),
            (128, 0, 128), (0, 128, 128), (128, 128, 128), (192, 192, 192),
            (255, 128, 0), (128, 255, 0), (0, 255, 128), (128, 0, 255),
            (255, 0, 128), (0, 128, 255), (255, 192, 128), (192, 255, 128)
        ]
        
        self.sounds = self.create_sounds()
        
        self.buttons = []
        self.setup_ui()
        
    def create_sounds(self):
        sounds = {}
        
        def generate_square_wave(frequency, duration, volume=0.3):
            sample_rate = 44100
            n_samples = int(sample_rate * duration)
            buf = bytearray()
            amplitude = int(32767 * volume)
            
            for i in range(n_samples):
                t = i / sample_rate
                value = amplitude if int(t * frequency * 2) % 2 == 0 else -amplitude
                buf.extend(struct.pack('<h', value))
            
            return pygame.mixer.Sound(buffer=buf)
        
        sounds['click'] = generate_square_wave(800, 0.05, 0.2)
        sounds['draw'] = generate_square_wave(400, 0.02, 0.1)
        sounds['erase'] = generate_square_wave(200, 0.02, 0.1)
        sounds['save'] = generate_square_wave(600, 0.1, 0.3)
        sounds['load'] = generate_square_wave(500, 0.1, 0.3)
        
        return sounds
    
    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def setup_ui(self):
        button_y = 620
        button_width = 120
        button_height = 40
        spacing = 10
        
        buttons_info = [
            ('清除画布', self.clear_canvas),
            ('保存图片', self.save_image),
            ('加载图片', self.load_image),
            ('切换网格', self.toggle_grid),
            ('画笔+', self.increase_brush),
            ('画笔-', self.decrease_brush)
        ]
        
        for i, (text, action) in enumerate(buttons_info):
            x = 20 + i * (button_width + spacing)
            self.buttons.append({
                'x': x,
                'y': button_y,
                'width': button_width,
                'height': button_height,
                'text': text,
                'action': action,
                'hover': False
            })
    
    def draw_text(self, text, x, y, color=(0, 0, 0), font=None):
        if font is None:
            font = self.font
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
    
    def draw_button(self, button):
        color = (200, 200, 200) if button['hover'] else (180, 180, 180)
        border_color = (100, 100, 100)
        pygame.draw.rect(self.screen, color, (button['x'], button['y'], button['width'], button['height']))
        pygame.draw.rect(self.screen, border_color, (button['x'], button['y'], button['width'], button['height']), 2)
        
        text_surface = self.font.render(button['text'], True, (0, 0, 0))
        text_x = button['x'] + (button['width'] - text_surface.get_width()) // 2
        text_y = button['y'] + (button['height'] - text_surface.get_height()) // 2
        self.screen.blit(text_surface, (text_x, text_y))
    
    def draw_color_palette(self):
        palette_x = self.CANVAS_WIDTH + 30
        palette_y = 30
        
        self.draw_text('颜色选择', palette_x, palette_y - 25, (50, 50, 50), self.title_font)
        
        color_size = 30
        spacing = 5
        cols = 4
        
        for i, color in enumerate(self.colors):
            col = i % cols
            row = i // cols
            x = palette_x + col * (color_size + spacing)
            y = palette_y + row * (color_size + spacing)
            
            pygame.draw.rect(self.screen, color, (x, y, color_size, color_size))
            pygame.draw.rect(self.screen, (100, 100, 100), (x, y, color_size, color_size), 1)
            
            if color == self.current_color:
                pygame.draw.rect(self.screen, (0, 0, 0), (x - 2, y - 2, color_size + 4, color_size + 4), 2)
    
    def draw_canvas(self):
        canvas_x = 20
        canvas_y = 20
        
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                rect_x = canvas_x + x * self.PIXEL_SIZE
                rect_y = canvas_y + y * self.PIXEL_SIZE
                pygame.draw.rect(self.screen, self.canvas[y][x], (rect_x, rect_y, self.PIXEL_SIZE, self.PIXEL_SIZE))
        
        if self.show_grid:
            for x in range(self.GRID_SIZE + 1):
                line_x = canvas_x + x * self.PIXEL_SIZE
                pygame.draw.line(self.screen, (200, 200, 200), (line_x, canvas_y), (line_x, canvas_y + self.CANVAS_HEIGHT))
            
            for y in range(self.GRID_SIZE + 1):
                line_y = canvas_y + y * self.PIXEL_SIZE
                pygame.draw.line(self.screen, (200, 200, 200), (canvas_x, line_y), (canvas_x + self.CANVAS_WIDTH, line_y))
        
        pygame.draw.rect(self.screen, (100, 100, 100), (canvas_x - 2, canvas_y - 2, self.CANVAS_WIDTH + 4, self.CANVAS_HEIGHT + 4), 2)
    
    def draw_info(self):
        info_x = self.CANVAS_WIDTH + 30
        info_y = 200
        
        self.draw_text(f'画笔大小: {self.brush_size}', info_x, info_y, (50, 50, 50))
        self.draw_text(f'当前颜色:', info_x, info_y + 30, (50, 50, 50))
        pygame.draw.rect(self.screen, self.current_color, (info_x, info_y + 55, 50, 30))
        pygame.draw.rect(self.screen, (100, 100, 100), (info_x, info_y + 55, 50, 30), 2)
    
    def get_canvas_pos(self, mouse_x, mouse_y):
        canvas_x = 20
        canvas_y = 20
        
        if (canvas_x <= mouse_x < canvas_x + self.CANVAS_WIDTH and
            canvas_y <= mouse_y < canvas_y + self.CANVAS_HEIGHT):
            grid_x = (mouse_x - canvas_x) // self.PIXEL_SIZE
            grid_y = (mouse_y - canvas_y) // self.PIXEL_SIZE
            return grid_x, grid_y
        return None, None
    
    def get_color_palette_pos(self, mouse_x, mouse_y):
        palette_x = self.CANVAS_WIDTH + 30
        palette_y = 30
        
        color_size = 30
        spacing = 5
        cols = 4
        
        for i, color in enumerate(self.colors):
            col = i % cols
            row = i // cols
            x = palette_x + col * (color_size + spacing)
            y = palette_y + row * (color_size + spacing)
            
            if x <= mouse_x < x + color_size and y <= mouse_y < y + color_size:
                return color
        return None
    
    def paint_pixel(self, x, y, color):
        for dy in range(self.brush_size):
            for dx in range(self.brush_size):
                nx = x + dx
                ny = y + dy
                if 0 <= nx < self.GRID_SIZE and 0 <= ny < self.GRID_SIZE:
                    self.canvas[ny][nx] = color
    
    def clear_canvas(self):
        self.play_sound('click')
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                self.canvas[y][x] = (255, 255, 255)
    
    def toggle_grid(self):
        self.play_sound('click')
        self.show_grid = not self.show_grid
    
    def increase_brush(self):
        self.play_sound('click')
        if self.brush_size < 5:
            self.brush_size += 1
    
    def decrease_brush(self):
        self.play_sound('click')
        if self.brush_size > 1:
            self.brush_size -= 1
    
    def save_image(self):
        self.play_sound('save')
        surface = pygame.Surface((self.GRID_SIZE, self.GRID_SIZE))
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                surface.set_at((x, y), self.canvas[y][x])
        
        filename = 'pixel_art.png'
        pygame.image.save(surface, filename)
        print(f'图片已保存为: {filename}')
    
    def load_image(self):
        self.play_sound('load')
        filename = 'pixel_art.png'
        if os.path.exists(filename):
            try:
                image = pygame.image.load(filename)
                image = pygame.transform.scale(image, (self.GRID_SIZE, self.GRID_SIZE))
                
                for y in range(self.GRID_SIZE):
                    for x in range(self.GRID_SIZE):
                        self.canvas[y][x] = image.get_at((x, y))[:3]
                print(f'图片已加载: {filename}')
            except:
                print('加载图片失败')
        else:
            print('未找到图片文件')
    
    def handle_mouse_down(self, pos, button):
        x, y = pos
        
        if button == 1:
            grid_x, grid_y = self.get_canvas_pos(x, y)
            if grid_x is not None:
                self.drawing = True
                self.paint_pixel(grid_x, grid_y, self.current_color)
                self.play_sound('draw')
            
            color = self.get_color_palette_pos(x, y)
            if color is not None:
                self.current_color = color
                self.play_sound('click')
            
            for btn in self.buttons:
                if (btn['x'] <= x < btn['x'] + btn['width'] and
                    btn['y'] <= y < btn['y'] + btn['height']):
                    btn['action']()
        
        elif button == 3:
            grid_x, grid_y = self.get_canvas_pos(x, y)
            if grid_x is not None:
                self.erasing = True
                self.paint_pixel(grid_x, grid_y, (255, 255, 255))
                self.play_sound('erase')
    
    def handle_mouse_up(self, pos, button):
        if button == 1:
            self.drawing = False
        elif button == 3:
            self.erasing = False
    
    def handle_mouse_motion(self, pos):
        x, y = pos
        
        for btn in self.buttons:
            btn['hover'] = (btn['x'] <= x < btn['x'] + btn['width'] and
                           btn['y'] <= y < btn['y'] + btn['height'])
        
        if self.drawing:
            grid_x, grid_y = self.get_canvas_pos(x, y)
            if grid_x is not None:
                self.paint_pixel(grid_x, grid_y, self.current_color)
        
        elif self.erasing:
            grid_x, grid_y = self.get_canvas_pos(x, y)
            if grid_x is not None:
                self.paint_pixel(grid_x, grid_y, (255, 255, 255))
    
    def run(self):
        running = True
        while running:
            self.screen.fill((240, 240, 240))
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    self.handle_mouse_down(event.pos, event.button)
                elif event.type == MOUSEBUTTONUP:
                    self.handle_mouse_up(event.pos, event.button)
                elif event.type == MOUSEMOTION:
                    self.handle_mouse_motion(event.pos)
            
            self.draw_canvas()
            self.draw_color_palette()
            self.draw_info()
            
            for btn in self.buttons:
                self.draw_button(btn)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    editor = PixelArtEditor()
    editor.run()
