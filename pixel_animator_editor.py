import pygame
import sys
import os
import json

# 初始化Pygame
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

try:
    pygame.mixer.init()
    SOUND_ENABLED = True
except pygame.error:
    SOUND_ENABLED = False
    print("音频设备不可用，音效将被禁用")

# 配置参数
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
CANVAS_SIZE = 32  # 画布大小（像素）
PIXEL_SIZE = 16  # 每个像素的显示大小
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)

# 预设颜色面板
COLORS = [
    (0, 0, 0), (255, 255, 255), (128, 128, 128), (192, 192, 192),
    (255, 0, 0), (255, 128, 0), (255, 255, 0), (128, 255, 0),
    (0, 255, 0), (0, 255, 128), (0, 255, 255), (0, 128, 255),
    (0, 0, 255), (128, 0, 255), (255, 0, 255), (255, 0, 128),
    (139, 69, 19), (165, 42, 42), (210, 180, 140), (0, 100, 0)
]

class SoundSystem:
    """音效系统 - 使用bytearray生成音效"""
    def __init__(self):
        if not SOUND_ENABLED:
            return
        self.sample_rate = 44100
        self.channels = 2
        
    def generate_tone(self, frequency, duration, volume=0.3):
        """生成指定频率的音效"""
        if not SOUND_ENABLED:
            return None
        samples = int(self.sample_rate * duration)
        wave = bytearray()
        
        for i in range(samples):
            t = i / self.sample_rate
            value = int(volume * 32767 * (2 ** 0.5) * (
                0.5 * (1 - t/duration) * (
                    pygame.mixer.Sound._sine(t * frequency * 2 * 3.14159) +
                    0.5 * pygame.mixer.Sound._sine(t * frequency * 4 * 3.14159)
                )
            ))
            
            # 转换为16位立体声
            wave.extend(value.to_bytes(2, 'little', signed=True))
            wave.extend(value.to_bytes(2, 'little', signed=True))
        
        return pygame.mixer.Sound(wave)
    
    def play_click(self):
        """播放点击音效"""
        if not SOUND_ENABLED:
            return
        sound = self.generate_tone(800, 0.05)
        sound.play()
    
    def play_paint(self):
        """播放绘画音效"""
        if not SOUND_ENABLED:
            return
        sound = self.generate_tone(600, 0.02)
        sound.play()
    
    def play_delete(self):
        """播放删除音效"""
        if not SOUND_ENABLED:
            return
        sound = self.generate_tone(200, 0.1)
        sound.play()
    
    def play_add(self):
        """播放添加音效"""
        if not SOUND_ENABLED:
            return
        sound = self.generate_tone(523, 0.1)
        sound.play()
    
    def play_save(self):
        """播放保存音效"""
        if not SOUND_ENABLED:
            return
        sound = self.generate_tone(659, 0.1)
        sound.play()
        pygame.time.delay(50)
        sound2 = self.generate_tone(784, 0.1)
        sound2.play()

class PixelAnimator:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("像素动画编辑器")
        
        self.clock = pygame.time.Clock()
        self.sound_system = SoundSystem()
        
        # 画布属性
        self.canvas = [[BLACK for _ in range(CANVAS_SIZE)] for _ in range(CANVAS_SIZE)]
        self.frames = [self.copy_canvas()]
        self.current_frame = 0
        self.onion_skin = True
        
        # 颜色选择
        self.selected_color = BLACK
        self.color_panel_x = SCREEN_WIDTH - 80
        self.color_panel_y = 50
        
        # 播放控制
        self.is_playing = False
        self.play_speed = 10  # 帧间隔（毫秒）
        self.last_frame_time = 0
        
        # UI按钮
        self.button_font = get_chinese_font(20)
        self.small_font = get_chinese_font(16)
        
        # 按钮位置
        self.buttons = {
            'prev_frame': (10, 10, 60, 30),
            'next_frame': (80, 10, 60, 30),
            'add_frame': (150, 10, 60, 30),
            'del_frame': (220, 10, 60, 30),
            'play': (290, 10, 60, 30),
            'save': (360, 10, 60, 30),
            'load': (430, 10, 60, 30),
            'onion_skin': (500, 10, 80, 30),
        }
        
        # 速度滑块
        self.speed_slider = (600, 10, 150, 30)
        self.speed_handle = 100  # 初始位置（百分比）
    
    def copy_canvas(self):
        """复制当前画布"""
        return [[self.canvas[y][x] for x in range(CANVAS_SIZE)] for y in range(CANVAS_SIZE)]
    
    def clear_canvas(self):
        """清空画布"""
        self.canvas = [[BLACK for _ in range(CANVAS_SIZE)] for _ in range(CANVAS_SIZE)]
    
    def draw_pixel(self, x, y, color):
        """绘制像素"""
        if 0 <= x < CANVAS_SIZE and 0 <= y < CANVAS_SIZE:
            self.canvas[y][x] = color
    
    def get_canvas_pos(self, mouse_x, mouse_y):
        """获取鼠标在画布上的位置"""
        canvas_x = mouse_x - 50
        canvas_y = mouse_y - 60
        
        if canvas_x < 0 or canvas_y < 0:
            return None
        
        pixel_x = canvas_x // PIXEL_SIZE
        pixel_y = canvas_y // PIXEL_SIZE
        
        if pixel_x >= CANVAS_SIZE or pixel_y >= CANVAS_SIZE:
            return None
        
        return (pixel_x, pixel_y)
    
    def draw_ui(self):
        """绘制UI界面"""
        # 背景
        self.screen.fill(LIGHT_GRAY)
        
        # 画布区域背景
        pygame.draw.rect(self.screen, DARK_GRAY, (45, 55, CANVAS_SIZE * PIXEL_SIZE + 10, CANVAS_SIZE * PIXEL_SIZE + 10))
        
        # 绘制画布
        for y in range(CANVAS_SIZE):
            for x in range(CANVAS_SIZE):
                pygame.draw.rect(self.screen, self.canvas[y][x], 
                    (50 + x * PIXEL_SIZE, 60 + y * PIXEL_SIZE, PIXEL_SIZE - 1, PIXEL_SIZE - 1))
        
        # 洋葱皮效果 - 显示上一帧
        if self.onion_skin and self.current_frame > 0 and len(self.frames) > 1:
            prev_frame = self.frames[self.current_frame - 1]
            for y in range(CANVAS_SIZE):
                for x in range(CANVAS_SIZE):
                    color = prev_frame[y][x]
                    if color != BLACK:
                        # 创建半透明颜色
                        alpha_color = (color[0], color[1], color[2], 64)
                        surface = pygame.Surface((PIXEL_SIZE - 1, PIXEL_SIZE - 1), pygame.SRCALPHA)
                        surface.fill(alpha_color)
                        self.screen.blit(surface, (50 + x * PIXEL_SIZE, 60 + y * PIXEL_SIZE))
        
        # 绘制网格线
        for i in range(CANVAS_SIZE + 1):
            pygame.draw.line(self.screen, GRAY, 
                (50 + i * PIXEL_SIZE, 60), 
                (50 + i * PIXEL_SIZE, 60 + CANVAS_SIZE * PIXEL_SIZE))
            pygame.draw.line(self.screen, GRAY, 
                (50, 60 + i * PIXEL_SIZE), 
                (50 + CANVAS_SIZE * PIXEL_SIZE, 60 + i * PIXEL_SIZE))
        
        # 绘制按钮
        button_texts = {
            'prev_frame': '上一帧',
            'next_frame': '下一帧',
            'add_frame': '添加帧',
            'del_frame': '删除帧',
            'play': '播放' if not self.is_playing else '暂停',
            'save': '保存',
            'load': '加载',
            'onion_skin': '洋葱皮' if self.onion_skin else '关闭洋葱皮',
        }
        
        for btn_name, (x, y, w, h) in self.buttons.items():
            color = DARK_GRAY if btn_name == 'del_frame' else GRAY
            pygame.draw.rect(self.screen, color, (x, y, w, h))
            pygame.draw.rect(self.screen, BLACK, (x, y, w, h), 2)
            
            text = self.button_font.render(button_texts[btn_name], True, WHITE)
            text_rect = text.get_rect(center=(x + w//2, y + h//2))
            self.screen.blit(text, text_rect)
        
        # 绘制速度控制
        pygame.draw.rect(self.screen, GRAY, self.speed_slider)
        pygame.draw.rect(self.screen, BLACK, self.speed_slider, 2)
        
        # 滑块手柄
        handle_x = self.speed_slider[0] + int(self.speed_handle / 100 * self.speed_slider[2])
        pygame.draw.rect(self.screen, BLACK, (handle_x - 5, self.speed_slider[1], 10, self.speed_slider[3]))
        
        # 速度文字
        speed_text = self.small_font.render(f'速度: {20 - self.play_speed // 5}', True, BLACK)
        self.screen.blit(speed_text, (self.speed_slider[0], self.speed_slider[1] + 35))
        
        # 绘制颜色面板
        pygame.draw.rect(self.screen, DARK_GRAY, (self.color_panel_x, self.color_panel_y - 10, 70, 220))
        pygame.draw.rect(self.screen, BLACK, (self.color_panel_x, self.color_panel_y - 10, 70, 220), 2)
        
        for i, color in enumerate(COLORS):
            x = self.color_panel_x + 5 + (i % 4) * 16
            y = self.color_panel_y + (i // 4) * 16
            
            pygame.draw.rect(self.screen, color, (x, y, 14, 14))
            pygame.draw.rect(self.screen, BLACK, (x, y, 14, 14), 1)
            
            # 选中的颜色用白框标记
            if color == self.selected_color:
                pygame.draw.rect(self.screen, WHITE, (x - 1, y - 1, 16, 16), 2)
        
        # 显示当前帧信息
        frame_info = self.button_font.render(f'帧 {self.current_frame + 1} / {len(self.frames)}', True, BLACK)
        self.screen.blit(frame_info, (10, 50))
        
        # 显示操作提示
        tips = [
            '左键绘画 | 右键擦除',
            '滚轮调整速度',
        ]
        for i, tip in enumerate(tips):
            text = self.small_font.render(tip, True, BLACK)
            self.screen.blit(text, (10, SCREEN_HEIGHT - 30 + i * 18))
    
    def handle_mouse_click(self, x, y, button):
        """处理鼠标点击"""
        # 检查颜色面板点击
        if self.color_panel_x <= x <= self.color_panel_x + 70:
            if self.color_panel_y <= y <= self.color_panel_y + 200:
                col = (x - self.color_panel_x - 5) // 16
                row = (y - self.color_panel_y) // 16
                index = row * 4 + col
                
                if 0 <= index < len(COLORS):
                    self.selected_color = COLORS[index]
                    self.sound_system.play_click()
                    return
        
        # 检查按钮点击
        for btn_name, (btn_x, btn_y, btn_w, btn_h) in self.buttons.items():
            if btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h:
                self.handle_button_click(btn_name)
                return
        
        # 检查速度滑块
        slider_x, slider_y, slider_w, slider_h = self.speed_slider
        if slider_x <= x <= slider_x + slider_w and slider_y <= y <= slider_y + slider_h:
            self.speed_handle = ((x - slider_x) / slider_w) * 100
            self.play_speed = int((100 - self.speed_handle) / 100 * 15) + 5
            return
        
        # 检查画布点击
        pos = self.get_canvas_pos(x, y)
        if pos:
            pixel_x, pixel_y = pos
            if button == 1:  # 左键绘画
                self.draw_pixel(pixel_x, pixel_y, self.selected_color)
                self.sound_system.play_paint()
            elif button == 3:  # 右键擦除
                self.draw_pixel(pixel_x, pixel_y, BLACK)
                self.sound_system.play_paint()
    
    def handle_button_click(self, btn_name):
        """处理按钮点击"""
        if btn_name == 'prev_frame':
            if self.current_frame > 0:
                self.save_current_frame()
                self.current_frame -= 1
                self.load_current_frame()
                self.sound_system.play_click()
        
        elif btn_name == 'next_frame':
            if self.current_frame < len(self.frames) - 1:
                self.save_current_frame()
                self.current_frame += 1
                self.load_current_frame()
                self.sound_system.play_click()
        
        elif btn_name == 'add_frame':
            self.save_current_frame()
            self.frames.append(self.copy_canvas())
            self.current_frame = len(self.frames) - 1
            self.sound_system.play_add()
        
        elif btn_name == 'del_frame':
            if len(self.frames) > 1:
                self.frames.pop(self.current_frame)
                if self.current_frame >= len(self.frames):
                    self.current_frame = len(self.frames) - 1
                self.load_current_frame()
                self.sound_system.play_delete()
        
        elif btn_name == 'play':
            self.is_playing = not self.is_playing
            self.sound_system.play_click()
        
        elif btn_name == 'save':
            self.save_animation()
        
        elif btn_name == 'load':
            self.load_animation()
        
        elif btn_name == 'onion_skin':
            self.onion_skin = not self.onion_skin
            self.sound_system.play_click()
    
    def save_current_frame(self):
        """保存当前画布到当前帧"""
        self.frames[self.current_frame] = self.copy_canvas()
    
    def load_current_frame(self):
        """加载当前帧到画布"""
        frame = self.frames[self.current_frame]
        for y in range(CANVAS_SIZE):
            for x in range(CANVAS_SIZE):
                self.canvas[y][x] = frame[y][x]
    
    def save_animation(self):
        """保存动画到文件"""
        try:
            data = {
                'canvas_size': CANVAS_SIZE,
                'frames': []
            }
            
            for frame in self.frames:
                frame_data = []
                for row in frame:
                    row_data = [[c[0], c[1], c[2]] for c in row]
                    frame_data.append(row_data)
                data['frames'].append(frame_data)
            
            with open('pixel_animation.json', 'w') as f:
                json.dump(data, f)
            
            self.sound_system.play_save()
            print('动画已保存到 pixel_animation.json')
        except Exception as e:
            print(f'保存失败: {e}')
    
    def load_animation(self):
        """从文件加载动画"""
        try:
            with open('pixel_animation.json', 'r') as f:
                data = json.load(f)
            
            self.frames = []
            for frame_data in data['frames']:
                frame = []
                for row_data in frame_data:
                    row = [(c[0], c[1], c[2]) for c in row_data]
                    frame.append(row)
                self.frames.append(frame)
            
            self.current_frame = 0
            self.load_current_frame()
            self.sound_system.play_save()
            print('动画已加载')
        except Exception as e:
            print(f'加载失败: {e}')
    
    def run(self):
        """主循环"""
        running = True
        
        while running:
            self.clock.tick(FPS)
            current_time = pygame.time.get_ticks()
            
            # 自动播放动画
            if self.is_playing and current_time - self.last_frame_time >= self.play_speed * 100:
                self.save_current_frame()
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.load_current_frame()
                self.last_frame_time = current_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos[0], event.pos[1], event.button)
                
                elif event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[0]:
                        pos = self.get_canvas_pos(event.pos[0], event.pos[1])
                        if pos:
                            self.draw_pixel(pos[0], pos[1], self.selected_color)
                    elif pygame.mouse.get_pressed()[2]:
                        pos = self.get_canvas_pos(event.pos[0], event.pos[1])
                        if pos:
                            self.draw_pixel(pos[0], pos[1], BLACK)
                
                elif event.type == pygame.MOUSEWHEEL:
                    # 滚轮调整速度
                    self.speed_handle = max(0, min(100, self.speed_handle + event.y * 10))
                    self.play_speed = int((100 - self.speed_handle) / 100 * 15) + 5
            
            self.draw_ui()
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    app = PixelAnimator()
    app.run()
