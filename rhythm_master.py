import pygame
import os
import random
import math
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

pygame.mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (80, 80, 80)
DARK_GRAY = (30, 30, 30)
RED = (220, 60, 60)
ORANGE = (255, 140, 50)
YELLOW = (255, 220, 50)
GREEN = (50, 200, 100)
BLUE = (60, 140, 255)
PURPLE = (180, 80, 220)
CYAN = (50, 220, 220)

PIECE_COLORS = [RED, BLUE, GREEN, YELLOW, PURPLE]
PIECE_NAMES = ['Do', 'Re', 'Mi', 'Fa', 'Sol']
PIECE_KEYS = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k, pygame.K_SPACE]

GRID_COLS = 10
GRID_ROWS = 18
CELL_SIZE = 28
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 40
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE

TEMPLATE_WIDTH = 4
TEMPLATE_HEIGHT = 4

TEMPLATES = [
    [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[1, 0, 0, 0], [1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[0, 1, 0, 0], [1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[1, 1, 1, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[1, 1, 1, 0], [0, 0, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[1, 1, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[0, 1, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[1, 0, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[0, 0, 1, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[1, 1, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0]],
    [[1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 0, 0]],
    [[0, 1, 1, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]],
    [[1, 1, 1, 1], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("音乐方块消消乐")
clock = pygame.time.Clock()

font_large = get_chinese_font(56)
font_medium = get_chinese_font(40)
font_small = get_chinese_font(28)
font_tiny = get_chinese_font(22)

class SoundGenerator:
    @staticmethod
    def generate_tone(frequency, duration, volume=0.4):
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        buffer = bytearray(num_samples * 2)
        for i in range(num_samples):
            t = i / sample_rate
            envelope = 1.0
            if i < num_samples * 0.01:
                envelope = i / (num_samples * 0.01)
            elif i > num_samples * 0.7:
                envelope = (num_samples - i) / (num_samples * 0.3)
            value = int(32767 * volume * envelope * math.sin(2 * math.pi * frequency * t))
            value = max(-32768, min(32767, value))
            buffer[i * 2] = value & 0xff
            buffer[i * 2 + 1] = (value >> 8) & 0xff
        return pygame.mixer.Sound(buffer)

    @staticmethod
    def generate_clear_sound(duration=0.5):
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        buffer = bytearray(num_samples * 2)
        for i in range(num_samples):
            t = i / sample_rate
            envelope = 1.0 - (i / num_samples)
            freq = 400 + (i / num_samples) * 800
            value = int(16383 * envelope * (
                math.sin(2 * math.pi * freq * t) +
                math.sin(2 * math.pi * freq * 1.5 * t) * 0.5 +
                math.sin(2 * math.pi * freq * 2 * t) * 0.25
            ))
            value = max(-32768, min(32767, value))
            buffer[i * 2] = value & 0xff
            buffer[i * 2 + 1] = (value >> 8) & 0xff
        return pygame.mixer.Sound(buffer)

    @staticmethod
    def generate_gameover_sound(duration=1.0):
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        buffer = bytearray(num_samples * 2)
        for i in range(num_samples):
            t = i / sample_rate
            envelope = 1.0 - (i / num_samples)
            freq = 200 - (i / num_samples) * 150
            value = int(20000 * envelope * math.sin(2 * math.pi * freq * t))
            value = max(-32768, min(32767, value))
            buffer[i * 2] = value & 0xff
            buffer[i * 2 + 1] = (value >> 8) & 0xff
        return pygame.mixer.Sound(buffer)

PIECE_FREQUENCIES = [262, 294, 330, 349, 392]

sounds = {}
for i, freq in enumerate(PIECE_FREQUENCIES):
    sounds[i] = SoundGenerator.generate_tone(freq, 0.15)
sounds['clear'] = SoundGenerator.generate_clear_sound()
sounds['gameover'] = SoundGenerator.generate_gameover_sound()
sounds['move'] = SoundGenerator.generate_tone(200, 0.05, 0.1)
sounds['rotate'] = SoundGenerator.generate_tone(300, 0.05, 0.1)
sounds['drop'] = SoundGenerator.generate_tone(150, 0.1, 0.2)
sounds['lock'] = SoundGenerator.generate_tone(100, 0.1, 0.3)

class Piece:
    def __init__(self, template_index, piece_type):
        self.template = [row[:] for row in TEMPLATES[template_index]]
        self.piece_type = piece_type
        self.color = PIECE_COLORS[piece_type]
        self.name = PIECE_NAMES[piece_type]
        self.rotation = 0
        self.col = GRID_COLS // 2 - 2
        self.row = 0

    def rotate_clockwise(self):
        size = len(self.template)
        rotated = [[self.template[size - 1 - j][i] for j in range(size)] for i in range(size)]
        self.template = rotated
        self.rotation = (self.rotation + 1) % 4

    def rotate_counter_clockwise(self):
        size = len(self.template)
        rotated = [[self.template[j][size - 1 - i] for j in range(size)] for i in range(size)]
        self.template = rotated
        self.rotation = (self.rotation - 1) % 4

    def get_cells(self):
        cells = []
        for r, row in enumerate(self.template):
            for c, val in enumerate(row):
                if val:
                    cells.append((r, c))
        return cells

    def get_absolute_cells(self):
        cells = []
        for r, row in enumerate(self.template):
            for c, val in enumerate(row):
                if val:
                    cells.append((self.row + r, self.col + c))
        return cells

class Game:
    def __init__(self):
        self.state = 'menu'
        self.grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.grid_note_types = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.current_piece = None
        self.next_piece_type = 0
        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = 0
        self.max_combo = 0
        self.total_clears = 0
        self.perfect_clears = 0
        self.waiting_piece = None
        self.waiting_row = 0
        self.waiting_timer = 0
        self.waiting_max_time = 120
        self.game_over = False
        self.drop_timer = 0
        self.drop_interval = 800
        self.lock_delay = 0
        self.lock_delay_max = 500
        self.particles = []
        self.floating_texts = []
        self.last_fall_time = 0
        self.soft_drop = False
        self.cascade_count = 0
        self.screen_shake = 0
        self.init_new_piece()

    def init_new_piece(self):
        self.current_piece = Piece(random.randint(0, len(TEMPLATES) - 1), self.next_piece_type)
        self.next_piece_type = random.randint(0, len(PIECE_COLORS) - 1)
        self.lock_delay = 0

    def is_valid_position(self, piece, col_offset=0, row_offset=0):
        for r, row in enumerate(piece.template):
            for c, val in enumerate(row):
                if val:
                    new_row = piece.row + r + row_offset
                    new_col = piece.col + c + col_offset
                    if new_col < 0 or new_col >= GRID_COLS:
                        return False
                    if new_row >= GRID_ROWS:
                        return False
                    if new_row >= 0 and self.grid[new_row][new_col] is not None:
                        return False
        return True

    def lock_piece(self):
        piece = self.current_piece
        locked = False
        for r, row in enumerate(piece.template):
            for c, val in enumerate(row):
                if val:
                    grid_row = piece.row + r
                    grid_col = piece.col + c
                    if grid_row >= 0 and grid_row < GRID_ROWS and grid_col >= 0 and grid_col < GRID_COLS:
                        self.grid[grid_row][grid_col] = piece.color
                        self.grid_note_types[grid_row][grid_col] = piece.piece_type
                        locked = True
        if locked:
            sounds['lock'].play()
            self.waiting_piece = self.find_complete_row_piece()
            if self.waiting_piece:
                self.waiting_row = self.waiting_piece['row']
                self.waiting_timer = 0
                self.state = 'waiting'
            else:
                self.check_game_over()
                if not self.game_over:
                    self.init_new_piece()

    def find_complete_row_piece(self):
        for row_idx in range(GRID_ROWS):
            complete = True
            for col_idx in range(GRID_COLS):
                if self.grid[row_idx][col_idx] is None:
                    complete = False
                    break
            if complete:
                note_types = [self.grid_note_types[row_idx][c] for c in range(GRID_COLS)]
                return {'row': row_idx, 'note_types': note_types, 'colors': [self.grid[row_idx][c] for c in range(GRID_COLS)]}
        return None

    def check_game_over(self):
        for c in range(GRID_COLS):
            if self.grid[0][c] is not None:
                self.game_over = True
                self.state = 'gameover'
                sounds['gameover'].play()
                return

    def move_piece(self, direction):
        if self.current_piece and self.state == 'playing':
            if direction == 'left' and self.is_valid_position(self.current_piece, col_offset=-1):
                self.current_piece.col -= 1
                sounds['move'].play()
            elif direction == 'right' and self.is_valid_position(self.current_piece, col_offset=1):
                self.current_piece.col += 1
                sounds['move'].play()

    def rotate_piece(self, direction):
        if self.current_piece and self.state == 'playing':
            original_template = [row[:] for row in self.current_piece.template]
            original_rotation = self.current_piece.rotation
            if direction == 'clockwise':
                self.current_piece.rotate_clockwise()
            else:
                self.current_piece.rotate_counter_clockwise()
            if not self.is_valid_position(self.current_piece):
                for offset in [-1, 1, -2, 2]:
                    if self.is_valid_position(self.current_piece, col_offset=offset):
                        self.current_piece.col += offset
                        break
                else:
                    self.current_piece.template = original_template
                    self.current_piece.rotation = original_rotation
            else:
                sounds['rotate'].play()

    def drop_piece(self):
        if self.current_piece and self.state == 'playing':
            while self.is_valid_position(self.current_piece, row_offset=1):
                self.current_piece.row += 1
            sounds['drop'].play()
            self.lock_piece()

    def hard_drop(self):
        if self.current_piece and self.state == 'playing':
            drop_distance = 0
            while self.is_valid_position(self.current_piece, row_offset=1):
                self.current_piece.row += 1
                drop_distance += 1
            self.score += drop_distance * 2
            sounds['drop'].play()
            self.lock_piece()

    def play_note(self, note_type):
        if note_type < len(sounds):
            sounds[note_type].play()

    def process_waiting_input(self, key_index):
        if self.state == 'waiting' and self.waiting_piece:
            correct_note = self.waiting_piece['note_types'][self.waiting_row]
            if key_index == correct_note:
                self.waiting_timer += 20
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)
                self.score += 100 * self.combo
                self.add_floating_text(f"+{100 * self.combo}", GREEN, GRID_OFFSET_X + GRID_WIDTH // 2, GRID_OFFSET_Y + self.waiting_row * CELL_SIZE)
                self.play_note(key_index)
                if self.waiting_timer >= self.waiting_max_time:
                    self.clear_line(self.waiting_row)
            else:
                self.combo = 0
                self.screen_shake = 10
                self.add_floating_text("错误!", RED, GRID_OFFSET_X + GRID_WIDTH // 2, GRID_OFFSET_Y + self.waiting_row * CELL_SIZE)

    def clear_line(self, row):
        self.cascade_count = 0
        self.clear_row_recursive(row)

    def clear_row_recursive(self, row):
        self.cascade_count += 1
        for c in range(GRID_COLS):
            color = self.grid[row][c]
            if color:
                self.spawn_particles(GRID_OFFSET_X + c * CELL_SIZE + CELL_SIZE // 2,
                                    GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2,
                                    color)
        sounds['clear'].play()
        for c in range(GRID_COLS):
            self.grid[row][c] = None
            self.grid_note_types[row][c] = None
        self.lines += 1
        self.total_clears += 1
        self.score += 1000 * self.cascade_count
        self.level = min(20, self.lines // 10 + 1)
        self.drop_interval = max(100, 800 - (self.level - 1) * 35)
        self.add_floating_text(f"消除! x{self.cascade_count}", YELLOW, GRID_OFFSET_X + GRID_WIDTH // 2, GRID_OFFSET_Y + row * CELL_SIZE)
        for r in range(row, 0, -1):
            self.grid[r] = self.grid[r - 1][:]
            self.grid_note_types[r] = self.grid_note_types[r - 1][:]
        self.grid[0] = [None for _ in range(GRID_COLS)]
        self.grid_note_types[0] = [None for _ in range(GRID_COLS)]
        self.waiting_piece = self.find_complete_row_piece()
        if self.waiting_piece:
            self.waiting_row = self.waiting_piece['row']
            self.waiting_timer = 0
        else:
            self.state = 'playing'
            self.check_game_over()
            if not self.game_over:
                self.init_new_piece()

    def spawn_particles(self, x, y, color):
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append({
                'x': x, 'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': color,
                'life': 30
            })

    def add_floating_text(self, text, color, x, y):
        self.floating_texts.append({
            'text': text,
            'color': color,
            'x': x,
            'y': y,
            'life': 60,
            'vy': -2
        })

    def update(self):
        current_time = pygame.time.get_ticks()
        if self.state == 'playing' and self.current_piece and not self.game_over:
            if self.soft_drop:
                fall_interval = self.drop_interval // 10
            else:
                fall_interval = self.drop_interval
            if current_time - self.last_fall_time > fall_interval:
                if self.is_valid_position(self.current_piece, row_offset=1):
                    self.current_piece.row += 1
                    if self.soft_drop:
                        self.score += 1
                else:
                    self.lock_delay += fall_interval
                    if self.lock_delay >= self.lock_delay_max:
                        self.lock_piece()
                self.last_fall_time = current_time
        if self.state == 'waiting':
            self.waiting_timer += 1
            if self.waiting_timer >= self.waiting_max_time:
                self.clear_line(self.waiting_row)
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.2
            p['life'] -= 1
        self.particles = [p for p in self.particles if p['life'] > 0]
        for t in self.floating_texts:
            t['y'] += t['vy']
            t['life'] -= 1
        self.floating_texts = [t for t in self.floating_texts if t['life'] > 0]
        if self.screen_shake > 0:
            self.screen_shake -= 1

    def draw(self):
        offset_x = 0
        offset_y = 0
        if self.screen_shake > 0:
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-3, 3)
        screen.fill(BLACK)
        if self.state == 'menu':
            self.draw_menu()
        elif self.state in ['playing', 'waiting']:
            self.draw_game(offset_x, offset_y)
        elif self.state == 'gameover':
            self.draw_gameover()

    def draw_menu(self):
        title = font_large.render("音乐方块消消乐", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        screen.blit(title, title_rect)
        subtitle = font_small.render("方块消除 + 音乐记忆", True, GRAY)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 170))
        screen.blit(subtitle, subtitle_rect)
        pygame.draw.rect(screen, DARK_GRAY, (100, 220, SCREEN_WIDTH - 200, 280))
        pygame.draw.rect(screen, CYAN, (100, 220, SCREEN_WIDTH - 200, 280), 3)
        instructions = [
            "【游戏说明】",
            "",
            "方块下落时，按正确按键演奏音符",
            "整行填满后，在时间窗口内正确演奏可消除",
            "错误按键或超时，方块将堆积",
            "堆积到顶部则游戏结束",
            "",
            "【操作说明】",
            "← → 移动方块",
            "↑ 旋转方块",
            "↓ 加速下落",
            "空格 快速落地",
            "D F J K 空格 - 演奏音符 Do Re Mi Fa Sol",
        ]
        for i, line in enumerate(instructions):
            color = YELLOW if i == 0 else WHITE if i == 1 or i == 7 else GRAY
            text = font_small.render(line, True, color)
            screen.blit(text, (130, 240 + i * 22))
        start_text = font_medium.render("按 Enter 开始游戏", True, GREEN)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, 530))
        screen.blit(start_text, start_rect)

    def draw_game(self, offset_x=0, offset_y=0):
        pygame.draw.rect(screen, DARK_GRAY, (GRID_OFFSET_X - 2 + offset_x, GRID_OFFSET_Y - 2 + offset_y, GRID_WIDTH + 4, GRID_HEIGHT + 4))
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                x = GRID_OFFSET_X + c * CELL_SIZE + offset_x
                y = GRID_OFFSET_Y + r * CELL_SIZE + offset_y
                pygame.draw.rect(screen, GRAY, (x, y, CELL_SIZE - 1, CELL_SIZE - 1), 1)
                if self.grid[r][c] is not None:
                    color = self.grid[r][c]
                    note_type = self.grid_note_types[r][c]
                    pygame.draw.rect(screen, color, (x + 1, y + 1, CELL_SIZE - 3, CELL_SIZE - 3))
                    pygame.draw.rect(screen, WHITE, (x + 1, y + 1, CELL_SIZE - 3, CELL_SIZE - 3), 1)
                    self.draw_note_label(x + CELL_SIZE // 2, y + CELL_SIZE // 2, note_type, 10)
        if self.state == 'waiting' and self.waiting_piece:
            progress = self.waiting_timer / self.waiting_max_time
            y = GRID_OFFSET_Y + self.waiting_row * CELL_SIZE
            pygame.draw.rect(screen, (50, 50, 50), (GRID_OFFSET_X, y, GRID_WIDTH, CELL_SIZE))
            bar_width = int(GRID_WIDTH * (1 - progress))
            bar_color = GREEN if progress < 0.5 else (YELLOW if progress < 0.8 else RED)
            pygame.draw.rect(screen, bar_color, (GRID_OFFSET_X, y + CELL_SIZE - 6, bar_width, 4))
            for c in range(GRID_COLS):
                x = GRID_OFFSET_X + c * CELL_SIZE
                color = self.waiting_piece['colors'][c]
                note_type = self.waiting_piece['note_types'][c]
                pygame.draw.rect(screen, color, (x + 1, y + 1, CELL_SIZE - 3, CELL_SIZE - 3))
                pygame.draw.rect(screen, WHITE, (x + 1, y + 1, CELL_SIZE - 3, CELL_SIZE - 3), 2)
                self.draw_note_label(x + CELL_SIZE // 2, y + CELL_SIZE // 2, note_type, 10)
        if self.current_piece and self.state == 'playing':
            cells = self.current_piece.get_cells()
            ghost_row = self.current_piece.row
            while True:
                valid = True
                for r, c in cells:
                    new_row = ghost_row + 1 + r
                    new_col = self.current_piece.col + c
                    if new_row >= GRID_ROWS or (new_row >= 0 and self.grid[new_row][new_col] is not None):
                        valid = False
                        break
                if valid:
                    ghost_row += 1
                else:
                    break
            for r, c in cells:
                x = GRID_OFFSET_X + (self.current_piece.col + c) * CELL_SIZE + offset_x
                y = GRID_OFFSET_Y + (ghost_row + r) * CELL_SIZE + offset_y
                pygame.draw.rect(screen, (30, 30, 30), (x + 2, y + 2, CELL_SIZE - 5, CELL_SIZE - 5), 1)
            for r, c in cells:
                x = GRID_OFFSET_X + (self.current_piece.col + c) * CELL_SIZE + offset_x
                y = GRID_OFFSET_Y + (self.current_piece.row + r) * CELL_SIZE + offset_y
                pygame.draw.rect(screen, self.current_piece.color, (x + 1, y + 1, CELL_SIZE - 3, CELL_SIZE - 3))
                pygame.draw.rect(screen, WHITE, (x + 1, y + 1, CELL_SIZE - 3, CELL_SIZE - 3), 2)
                self.draw_note_label(x + CELL_SIZE // 2, y + CELL_SIZE // 2, self.current_piece.piece_type, 11)
        for p in self.particles:
            alpha = int(255 * p['life'] / 30)
            color = (*p['color'][:3], alpha) if len(p['color']) == 4 else p['color']
            pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), 3)
        for t in self.floating_texts:
            alpha = int(255 * t['life'] / 60)
            text = font_small.render(t['text'], True, t['color'])
            text.set_alpha(alpha)
            screen.blit(text, (t['x'] - text.get_width() // 2, t['y']))
        self.draw_side_panel(offset_x, offset_y)
        if self.state == 'waiting' and self.waiting_piece:
            hint = font_small.render("按 D F J K 空格 演奏正确音符!", True, YELLOW)
            screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 10))

    def draw_note_label(self, x, y, note_type, size):
        font = get_chinese_font(size)
        text = font.render(PIECE_NAMES[note_type], True, WHITE)
        rect = text.get_rect(center=(x, y))
        screen.blit(text, rect)

    def draw_side_panel(self, offset_x=0, offset_y=0):
        panel_x = GRID_OFFSET_X + GRID_WIDTH + 30
        next_x = panel_x + 20
        next_y = GRID_OFFSET_Y + 50
        label = font_small.render("NEXT", True, GRAY)
        screen.blit(label, (next_x + 30, next_y - 30))
        pygame.draw.rect(screen, DARK_GRAY, (next_x, next_y, 100, 100), 2)
        for r, row in enumerate(TEMPLATES[0]):
            for c, val in enumerate(row):
                if val:
                    color = PIECE_COLORS[self.next_piece_type]
                    pygame.draw.rect(screen, color, (next_x + 15 + c * 20, next_y + 15 + r * 20, 18, 18))
        score_label = font_small.render("分数", True, GRAY)
        screen.blit(score_label, (panel_x, GRID_OFFSET_Y + 200))
        score_text = font_medium.render(str(self.score), True, WHITE)
        screen.blit(score_text, (panel_x, GRID_OFFSET_Y + 225))
        lines_label = font_small.render("消除行数", True, GRAY)
        screen.blit(lines_label, (panel_x, GRID_OFFSET_Y + 280))
        lines_text = font_medium.render(str(self.lines), True, WHITE)
        screen.blit(lines_text, (panel_x, GRID_OFFSET_Y + 305))
        level_label = font_small.render("等级", True, GRAY)
        screen.blit(level_label, (panel_x, GRID_OFFSET_Y + 360))
        level_text = font_medium.render(str(self.level), True, YELLOW)
        screen.blit(level_text, (panel_x, GRID_OFFSET_Y + 385))
        combo_label = font_small.render("连击", True, GRAY)
        screen.blit(combo_label, (panel_x, GRID_OFFSET_Y + 440))
        combo_text = font_medium.render(f"{self.combo}x", True, CYAN if self.combo > 0 else GRAY)
        screen.blit(combo_text, (panel_x, GRID_OFFSET_Y + 465))
        key_panel_x = GRID_OFFSET_X
        key_panel_y = GRID_OFFSET_Y + GRID_HEIGHT + 20
        pygame.draw.rect(screen, DARK_GRAY, (key_panel_x, key_panel_y, GRID_WIDTH, 50))
        pygame.draw.rect(screen, GRAY, (key_panel_x, key_panel_y, GRID_WIDTH, 50), 2)
        for i, (color, name, key) in enumerate(zip(PIECE_COLORS, PIECE_NAMES, PIECE_NAMES)):
            x = key_panel_x + i * (GRID_WIDTH // 5) + GRID_WIDTH // 10
            y = key_panel_y + 25
            pygame.draw.rect(screen, color, (x - 15, y - 15, 30, 30))
            pygame.draw.rect(screen, WHITE, (x - 15, y - 15, 30, 30), 2)
            key_labels = ['D', 'F', 'J', 'K', '空格']
            text = font_tiny.render(key_labels[i], True, BLACK)
            rect = text.get_rect(center=(x, y))
            screen.blit(text, rect)

    def draw_gameover(self):
        self.draw_game()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        title = font_large.render("游戏结束", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title, title_rect)
        stats = [
            (f"最终分数: {self.score}", WHITE),
            (f"消除行数: {self.lines}", WHITE),
            (f"最高连击: {self.max_combo}", CYAN),
            (f"等级: {self.level}", YELLOW),
        ]
        for i, (text, color) in enumerate(stats):
            stat_text = font_medium.render(text, True, color)
            rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, 250 + i * 50))
            screen.blit(stat_text, rect)
        restart = font_small.render("按 Enter 重新开始", True, GREEN)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, 500))
        screen.blit(restart, restart_rect)
        menu = font_small.render("按 ESC 返回菜单", True, GRAY)
        menu_rect = menu.get_rect(center=(SCREEN_WIDTH // 2, 540))
        screen.blit(menu, menu_rect)

    def start_game(self):
        self.grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.grid_note_types = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = 0
        self.max_combo = 0
        self.total_clears = 0
        self.game_over = False
        self.drop_interval = 800
        self.current_piece = None
        self.waiting_piece = None
        self.particles = []
        self.floating_texts = []
        self.screen_shake = 0
        self.next_piece_type = random.randint(0, len(PIECE_COLORS) - 1)
        self.init_new_piece()
        self.state = 'playing'
        self.last_fall_time = pygame.time.get_ticks()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == 'menu':
                if event.key == pygame.K_RETURN:
                    self.start_game()
            elif self.state == 'playing':
                if event.key == pygame.K_LEFT:
                    self.move_piece('left')
                elif event.key == pygame.K_RIGHT:
                    self.move_piece('right')
                elif event.key == pygame.K_UP:
                    self.rotate_piece('clockwise')
                elif event.key == pygame.K_z:
                    self.rotate_piece('counter_clockwise')
                elif event.key == pygame.K_DOWN:
                    self.soft_drop = True
                elif event.key == pygame.K_SPACE:
                    self.hard_drop()
                elif event.key in PIECE_KEYS:
                    self.process_waiting_input(PIECE_KEYS.index(event.key))
            elif self.state == 'waiting':
                if event.key in PIECE_KEYS:
                    self.process_waiting_input(PIECE_KEYS.index(event.key))
            elif self.state == 'gameover':
                if event.key == pygame.K_RETURN:
                    self.start_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = 'menu'
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                self.soft_drop = False

def main():
    game = Game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_input(event)
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
