"""
音乐生成器 - 点击网格创作音乐
操作说明：
- 点击网格格子来添加/移除音符
- 点击"播放"按钮播放旋律
- 点击"停止"按钮停止播放
- 点击"清除"按钮清除所有音符
- 不同行代表不同音高，不同列代表不同时间
"""

import pygame
import math
import sys

# 初始化pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

# 窗口设置
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("音乐生成器 - Music Generator")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BG_COLOR = (30, 30, 50)

# 音符颜色（彩虹渐变）
NOTE_COLORS = [
    (255, 80, 80),    # C - 红
    (255, 140, 60),   # D - 橙
    (255, 220, 60),   # E - 黄
    (80, 220, 80),    # F - 绿
    (60, 180, 255),   # G - 蓝
    (100, 100, 255),  # A - 靛
    (200, 80, 255),   # B - 紫
    (255, 120, 200),  # C5 - 粉
]

# 音符名称（从低到高）
NOTE_NAMES = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]

# 网格设置
ROWS = 8       # 音高数量
COLS = 16      # 时间步数
GRID_LEFT = 80
GRID_TOP = 80
CELL_W = 52
CELL_H = 52
GRID_W = COLS * CELL_W
GRID_H = ROWS * CELL_H

# 生成音符频率
def note_freq(name):
    """根据音符名称返回频率"""
    freqs = {
        "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23,
        "G4": 392.00, "A4": 440.00, "B4": 493.88, "C5": 523.25
    }
    return freqs[name]

# 音效缓存（延迟生成）
_sounds_cache = {}

def get_tone(frequency, volume=0.5):
    """获取或生成音效（延迟加载，避免启动时卡顿）"""
    key = (frequency, volume)
    if key not in _sounds_cache:
        _sounds_cache[key] = _generate_tone(frequency, 0.1, volume)
    return _sounds_cache[key]

def _generate_tone(frequency, duration=0.1, volume=0.5):
    """生成正弦波音效"""
    sample_rate = 22050  # 降低采样率加速生成
    n_samples = int(sample_rate * duration)
    buf = bytearray(n_samples * 2)
    phase = 0.0
    phase_step = 2 * math.pi * frequency / sample_rate
    for i in range(n_samples):
        val = math.sin(phase) * 0.7
        phase += phase_step
        # 简单淡出
        if i > n_samples * 3 // 4:
            val *= (n_samples - i) / (n_samples // 4)
        sample = int(val * volume * 32767)
        sample = max(-32768, min(32767, sample))
        buf[i * 2] = sample & 0xFF
        buf[i * 2 + 1] = (sample >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))

# 网格状态：grid[row][col] = True/False
grid = [[False] * COLS for _ in range(ROWS)]

# 播放状态
playing = False
play_col = 0
play_timer = 0
play_speed = 300  # 毫秒每步

# 按钮类
class Button:
    def __init__(self, x, y, w, h, text, color, hover_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.SysFont("simhei", 20)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=8)
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# 创建按钮
btn_play = Button(GRID_LEFT, GRID_TOP + GRID_H + 30, 100, 45, "播放", (40, 160, 80), (60, 200, 100))
btn_stop = Button(GRID_LEFT + 120, GRID_TOP + GRID_H + 30, 100, 45, "停止", (180, 60, 60), (220, 80, 80))
btn_clear = Button(GRID_LEFT + 240, GRID_TOP + GRID_H + 30, 100, 45, "清除", (60, 60, 180), (80, 80, 220))
btn_speed_up = Button(GRID_LEFT + 380, GRID_TOP + GRID_H + 30, 100, 45, "加速", (160, 120, 40), (200, 150, 60))
btn_speed_down = Button(GRID_LEFT + 500, GRID_TOP + GRID_H + 30, 100, 45, "减速", (160, 120, 40), (200, 150, 60))

buttons = [btn_play, btn_stop, btn_clear, btn_speed_up, btn_speed_down]

# 字体
font_note = pygame.font.SysFont("simhei", 18)
font_title = pygame.font.SysFont("simhei", 32)
font_info = pygame.font.SysFont("simhei", 16)

# 主循环
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # 检查按钮点击
            if btn_play.is_clicked(pos):
                playing = True
                play_col = 0
                play_timer = pygame.time.get_ticks()
            elif btn_stop.is_clicked(pos):
                playing = False
                play_col = 0
            elif btn_clear.is_clicked(pos):
                grid = [[False] * COLS for _ in range(ROWS)]
                playing = False
                play_col = 0
            elif btn_speed_up.is_clicked(pos):
                play_speed = max(100, play_speed - 50)
            elif btn_speed_down.is_clicked(pos):
                play_speed = min(800, play_speed + 50)

            # 检查网格点击
            grid_rect = pygame.Rect(GRID_LEFT, GRID_TOP, GRID_W, GRID_H)
            if grid_rect.collidepoint(pos):
                col = (pos[0] - GRID_LEFT) // CELL_W
                row = (pos[1] - GRID_TOP) // CELL_H
                if 0 <= row < ROWS and 0 <= col < COLS:
                    grid[row][col] = not grid[row][col]
                    # 点击时播放预览音
                    if grid[row][col]:
                        get_tone(note_freq(NOTE_NAMES[row])).play()

    # 播放逻辑
    if playing:
        current_time = pygame.time.get_ticks()
        if current_time - play_timer >= play_speed:
            # 播放当前列的所有音符
            for row in range(ROWS):
                if grid[row][play_col]:
                    get_tone(note_freq(NOTE_NAMES[row])).play()
            play_col = (play_col + 1) % COLS
            play_timer = current_time

    # 绘制
    screen.fill(BG_COLOR)

    # 标题
    title = font_title.render("音乐生成器", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 15))

    # 操作说明
    info = font_info.render("点击网格添加音符 | 播放/停止/清除控制旋律 | 加速/减速调整节奏", True, GRAY)
    screen.blit(info, (WIDTH // 2 - info.get_width() // 2, 55))

    # 绘制网格
    for row in range(ROWS):
        for col in range(COLS):
            x = GRID_LEFT + col * CELL_W
            y = GRID_TOP + row * CELL_H
            rect = pygame.Rect(x, y, CELL_W - 2, CELL_H - 2)

            if grid[row][col]:
                # 激活的格子用对应颜色
                color = NOTE_COLORS[row]
                pygame.draw.rect(screen, color, rect, border_radius=4)
                # 播放时当前列高亮
                if playing and col == play_col:
                    pygame.draw.rect(screen, WHITE, rect, 3, border_radius=4)
            else:
                # 未激活的格子
                pygame.draw.rect(screen, (50, 50, 70), rect, border_radius=4)
                pygame.draw.rect(screen, (70, 70, 90), rect, 1, border_radius=4)

    # 播放指示线
    if playing:
        line_x = GRID_LEFT + play_col * CELL_W + CELL_W // 2
        pygame.draw.line(screen, (255, 255, 100), (line_x, GRID_TOP - 5), (line_x, GRID_TOP + GRID_H + 5), 3)

    # 绘制音高标签
    for row in range(ROWS):
        label = font_note.render(NOTE_NAMES[row], True, NOTE_COLORS[row])
        screen.blit(label, (GRID_LEFT - 50, GRID_TOP + row * CELL_H + CELL_H // 2 - label.get_height() // 2))

    # 绘制时间步标签
    for col in range(COLS):
        label = font_info.render(str(col + 1), True, GRAY)
        screen.blit(label, (GRID_LEFT + col * CELL_W + CELL_W // 2 - label.get_width() // 2, GRID_TOP - 22))

    # 绘制按钮
    for btn in buttons:
        btn.draw(screen)

    # 显示速度信息
    speed_text = font_info.render(f"速度: {60000 // play_speed} BPM", True, WHITE)
    screen.blit(speed_text, (GRID_LEFT + 640, GRID_TOP + GRID_H + 40))

    # 播放状态
    if playing:
        status = font_info.render("正在播放...", True, (100, 255, 100))
    else:
        status = font_info.render("已停止", True, GRAY)
    screen.blit(status, (GRID_LEFT + 640, GRID_TOP + GRID_H + 15))

    pygame.display.flip()

pygame.quit()
sys.exit()
