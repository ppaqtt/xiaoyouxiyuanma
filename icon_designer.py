import pygame
import sys
import os

# 初始化Pygame
pygame.init()

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("像素图标设计器")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)

# 预设颜色
COLORS = [
    (255, 0, 0),      # 红色
    (0, 255, 0),      # 绿色
    (0, 0, 255),      # 蓝色
    (255, 255, 0),    # 黄色
    (255, 0, 255),    # 品红
    (0, 255, 255),    # 青色
    (255, 128, 0),    # 橙色
    (128, 0, 255),    # 紫色
    (0, 128, 0),      # 深绿
    (128, 128, 128),  # 灰色
]

# 图标模板类型
TEMPLATE_TYPES = ["方形", "圆形", "圆角"]

# 图标风格类型
STYLE_TYPES = ["线性", "填充", "像素"]

# 音效系统 - 使用bytearray生成音效
class SoundSystem:
    def __init__(self):
        self.enabled = True
        try:
            pygame.mixer.init()
        except pygame.error:
            self.enabled = False
        
    def generate_sound(self, frequency=440, duration=0.1, volume=0.5):
        if not self.enabled:
            return None
        
        sample_rate = 44100
        samples = int(sample_rate * duration)
        sound_data = bytearray()
        
        for i in range(samples):
            t = i / sample_rate
            value = int(127 * (1 + (pygame.math.sin(2 * pygame.math.pi * frequency * t))))
            sound_data.append(value)
            sound_data.append(value)
        
        sound = pygame.mixer.Sound(sound_data)
        sound.set_volume(volume)
        return sound
    
    def play_click(self):
        if not self.enabled:
            return
        sound = self.generate_sound(880, 0.05)
        sound.play()
    
    def play_success(self):
        if not self.enabled:
            return
        sound = self.generate_sound(523, 0.1)
        sound.play()
        pygame.time.delay(100)
        sound = self.generate_sound(659, 0.1)
        sound.play()
    
    def play_error(self):
        if not self.enabled:
            return
        sound = self.generate_sound(200, 0.2)
        sound.play()

# 主应用类
class IconDesigner:
    def __init__(self):
        self.sound_system = SoundSystem()
        self.current_template = 0  # 0: 方形, 1: 圆形, 2: 圆角
        self.current_style = 0     # 0: 线性, 1: 填充, 2: 像素
        self.current_color = COLORS[0]
        self.current_shadow_color = (0, 0, 0)
        self.draw_surface = pygame.Surface((200, 200))
        self.draw_surface.fill(WHITE)
        self.drawing = False
        self.last_pos = (0, 0)
        self.pixel_size = 4
        
        # UI元素位置
        self.template_buttons = []
        self.style_buttons = []
        self.color_buttons = []
        self.init_ui()
    
    def init_ui(self):
        # 模板按钮
        for i, template in enumerate(TEMPLATE_TYPES):
            self.template_buttons.append(pygame.Rect(50, 50 + i * 50, 100, 40))
        
        # 风格按钮
        for i, style in enumerate(STYLE_TYPES):
            self.style_buttons.append(pygame.Rect(200, 50 + i * 50, 100, 40))
        
        # 颜色按钮
        for i, color in enumerate(COLORS):
            x = 50 + (i % 5) * 40
            y = 200 + (i // 5) * 40
            self.color_buttons.append((color, pygame.Rect(x, y, 30, 30)))
    
    def draw_ui(self):
        # 绘制背景
        screen.fill(LIGHT_GRAY)
        
        # 绘制标题
        font = pygame.font.Font(None, 36)
        title = font.render("像素图标设计器", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))
        
        # 绘制模板选择
        font = pygame.font.Font(None, 24)
        template_label = font.render("选择模板:", True, BLACK)
        screen.blit(template_label, (50, 25))
        
        for i, rect in enumerate(self.template_buttons):
            color = GRAY if i == self.current_template else WHITE
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            text = font.render(TEMPLATE_TYPES[i], True, BLACK)
            screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))
        
        # 绘制风格选择
        style_label = font.render("选择风格:", True, BLACK)
        screen.blit(style_label, (200, 25))
        
        for i, rect in enumerate(self.style_buttons):
            color = GRAY if i == self.current_style else WHITE
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            text = font.render(STYLE_TYPES[i], True, BLACK)
            screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))
        
        # 绘制颜色选择
        color_label = font.render("选择颜色:", True, BLACK)
        screen.blit(color_label, (50, 175))
        
        for color, rect in self.color_buttons:
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            if color == self.current_color:
                pygame.draw.rect(screen, WHITE, rect, 3)
        
        # 绘制预览区域
        preview_label = font.render("预览:", True, BLACK)
        screen.blit(preview_label, (400, 25))
        
        # 根据模板绘制背景
        preview_rect = pygame.Rect(400, 50, 200, 200)
        pygame.draw.rect(screen, WHITE, preview_rect)
        pygame.draw.rect(screen, BLACK, preview_rect, 2)
        
        # 绘制模板背景
        template_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        template_surface.fill((0, 0, 0, 0))
        
        if self.current_template == 0:  # 方形
            pygame.draw.rect(template_surface, self.current_color, (20, 20, 160, 160), 0 if self.current_style == 1 else 3)
        elif self.current_template == 1:  # 圆形
            pygame.draw.circle(template_surface, self.current_color, (100, 100), 80, 0 if self.current_style == 1 else 3)
        elif self.current_template == 2:  # 圆角
            pygame.draw.rect(template_surface, self.current_color, (20, 20, 160, 160), 0 if self.current_style == 1 else 3, border_radius=20)
        
        screen.blit(template_surface, (400, 50))
        
        # 绘制绘制区域
        draw_label = font.render("绘制区域:", True, BLACK)
        screen.blit(draw_label, (400, 280))
        
        draw_rect = pygame.Rect(400, 310, 200, 200)
        pygame.draw.rect(screen, WHITE, draw_rect)
        pygame.draw.rect(screen, BLACK, draw_rect, 2)
        
        # 绘制像素网格
        for x in range(0, 200, self.pixel_size):
            pygame.draw.line(screen, LIGHT_GRAY, (400 + x, 310), (400 + x, 510))
        for y in range(0, 200, self.pixel_size):
            pygame.draw.line(screen, LIGHT_GRAY, (400, 310 + y), (600, 310 + y))
        
        # 绘制已绘制的内容
        screen.blit(self.draw_surface, (400, 310))
        
        # 绘制功能按钮
        export_button = pygame.Rect(650, 50, 100, 40)
        pygame.draw.rect(screen, (0, 200, 0), export_button)
        pygame.draw.rect(screen, BLACK, export_button, 2)
        export_text = font.render("导出PNG", True, BLACK)
        screen.blit(export_text, (export_button.centerx - export_text.get_width() // 2, export_button.centery - export_text.get_height() // 2))
        
        clear_button = pygame.Rect(650, 120, 100, 40)
        pygame.draw.rect(screen, (200, 0, 0), clear_button)
        pygame.draw.rect(screen, BLACK, clear_button, 2)
        clear_text = font.render("清除", True, BLACK)
        screen.blit(clear_text, (clear_button.centerx - clear_text.get_width() // 2, clear_button.centery - clear_text.get_height() // 2))
        
        # 绘制像素大小选择
        pixel_label = font.render(f"像素大小: {self.pixel_size}x{self.pixel_size}", True, BLACK)
        screen.blit(pixel_label, (50, 300))
        
        pixel_plus_button = pygame.Rect(50, 330, 40, 30)
        pygame.draw.rect(screen, WHITE, pixel_plus_button)
        pygame.draw.rect(screen, BLACK, pixel_plus_button, 2)
        plus_text = font.render("+", True, BLACK)
        screen.blit(plus_text, (pixel_plus_button.centerx - plus_text.get_width() // 2, pixel_plus_button.centery - plus_text.get_height() // 2))
        
        pixel_minus_button = pygame.Rect(100, 330, 40, 30)
        pygame.draw.rect(screen, WHITE, pixel_minus_button)
        pygame.draw.rect(screen, BLACK, pixel_minus_button, 2)
        minus_text = font.render("-", True, BLACK)
        screen.blit(minus_text, (pixel_minus_button.centerx - minus_text.get_width() // 2, pixel_minus_button.centery - minus_text.get_height() // 2))
        
        return export_button, clear_button, pixel_plus_button, pixel_minus_button
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # 检查模板按钮
                for i, rect in enumerate(self.template_buttons):
                    if rect.collidepoint(mouse_pos):
                        self.current_template = i
                        self.sound_system.play_click()
                        break
                
                # 检查风格按钮
                for i, rect in enumerate(self.style_buttons):
                    if rect.collidepoint(mouse_pos):
                        self.current_style = i
                        self.sound_system.play_click()
                        break
                
                # 检查颜色按钮
                for color, rect in self.color_buttons:
                    if rect.collidepoint(mouse_pos):
                        self.current_color = color
                        self.sound_system.play_click()
                        break
                
                # 检查导出按钮
                export_button, clear_button, pixel_plus_button, pixel_minus_button = self.draw_ui()
                if export_button.collidepoint(mouse_pos):
                    self.export_png()
                    self.sound_system.play_success()
                
                # 检查清除按钮
                if clear_button.collidepoint(mouse_pos):
                    self.draw_surface.fill(WHITE)
                    self.sound_system.play_click()
                
                # 检查像素大小按钮
                if pixel_plus_button.collidepoint(mouse_pos):
                    if self.pixel_size < 16:
                        self.pixel_size += 1
                        self.sound_system.play_click()
                
                if pixel_minus_button.collidepoint(mouse_pos):
                    if self.pixel_size > 1:
                        self.pixel_size -= 1
                        self.sound_system.play_click()
                
                # 检查绘制区域
                draw_rect = pygame.Rect(400, 310, 200, 200)
                if draw_rect.collidepoint(mouse_pos):
                    self.drawing = True
                    self.last_pos = (mouse_pos[0] - 400, mouse_pos[1] - 310)
            
            if event.type == pygame.MOUSEBUTTONUP:
                self.drawing = False
            
            if event.type == pygame.MOUSEMOTION and self.drawing:
                mouse_pos = pygame.mouse.get_pos()
                x = mouse_pos[0] - 400
                y = mouse_pos[1] - 310
                
                # 将坐标对齐到像素网格
                x = (x // self.pixel_size) * self.pixel_size
                y = (y // self.pixel_size) * self.pixel_size
                
                # 绘制直线
                dx = x - self.last_pos[0]
                dy = y - self.last_pos[1]
                steps = max(abs(dx), abs(dy))
                
                if steps > 0:
                    for i in range(steps + 1):
                        px = self.last_pos[0] + (dx * i) // steps
                        py = self.last_pos[1] + (dy * i) // steps
                        pygame.draw.rect(self.draw_surface, self.current_color, 
                                        (px, py, self.pixel_size, self.pixel_size))
                
                self.last_pos = (x, y)
    
    def export_png(self):
        # 创建最终图标
        final_icon = pygame.Surface((200, 200))
        final_icon.fill(WHITE)
        
        # 绘制模板
        if self.current_template == 0:
            pygame.draw.rect(final_icon, self.current_color, (20, 20, 160, 160), 0 if self.current_style == 1 else 3)
        elif self.current_template == 1:
            pygame.draw.circle(final_icon, self.current_color, (100, 100), 80, 0 if self.current_style == 1 else 3)
        elif self.current_template == 2:
            pygame.draw.rect(final_icon, self.current_color, (20, 20, 160, 160), 0 if self.current_style == 1 else 3, border_radius=20)
        
        # 添加绘制内容
        final_icon.blit(self.draw_surface, (0, 0))
        
        # 添加阴影效果
        shadow_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 30))
        final_icon.blit(shadow_surface, (5, 5))
        
        # 保存文件
        if not os.path.exists("icons"):
            os.makedirs("icons")
        
        filename = f"icons/icon_{pygame.time.get_ticks()}.png"
        pygame.image.save(final_icon, filename)
        print(f"图标已导出: {filename}")
    
    def run(self):
        while True:
            self.handle_events()
            self.draw_ui()
            pygame.display.flip()

if __name__ == "__main__":
    app = IconDesigner()
    app.run()