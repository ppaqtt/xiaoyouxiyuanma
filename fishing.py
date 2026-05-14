import pygame
import random
import math
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
DEPTH_MAX = 2000

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY_BLUE = (135, 206, 250)
OCEAN_LIGHT = (0, 150, 255)
OCEAN_MEDIUM = (0, 80, 180)
OCEAN_DEEP = (0, 20, 80)
OCEAN_ABYSS = (0, 5, 30)
GOLD = (255, 215, 0)
RED = (255, 50, 50)
GREEN = (0, 200, 100)
PURPLE = (180, 100, 255)
ORANGE = (255, 140, 0)
PINK = (255, 100, 180)
CYAN = (0, 255, 255)
SILVER = (192, 192, 192)
PEARL_WHITE = (245, 245, 245)
DANGER_RED = (255, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("深海潜水钓鱼")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
title_font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 22)

SAFE_DEPTH = 800
CRITICAL_DEPTH = 1500

class SoundGenerator:
    def __init__(self):
        self.sample_rate = 22050
        self.sound_cache = {}

    def generate_sine_wave(self, frequency, duration, volume=0.3):
        samples = int(self.sample_rate * duration)
        audio_data = bytearray()
        for i in range(samples):
            t = i / self.sample_rate
            value = int(127 + 127 * volume * math.sin(2 * math.pi * frequency * t))
            audio_data.append(value)
        return pygame.mixer.Sound(buffer=audio_data)

    def generate_noise_burst(self, duration, volume=0.2):
        samples = int(self.sample_rate * duration)
        audio_data = bytearray()
        for i in range(samples):
            value = int(128 + 128 * volume * (random.random() * 2 - 1))
            audio_data.append(value)
        return pygame.mixer.Sound(buffer=audio_data)

    def generate_bubble_sound(self):
        if 'bubble' not in self.sound_cache:
            self.sound_cache['bubble'] = self.generate_sine_wave(800, 0.1, 0.15)
        return self.sound_cache['bubble']

    def generate_catch_sound(self):
        if 'catch' not in self.sound_cache:
            data = bytearray()
            for freq in [400, 600, 800]:
                samples = int(self.sample_rate * 0.1)
                for i in range(samples):
                    t = i / self.sample_rate
                    value = int(127 + 127 * 0.3 * math.sin(2 * math.pi * freq * t))
                    data.append(value)
            self.sound_cache['catch'] = pygame.mixer.Sound(buffer=data)
        return self.sound_cache['catch']

    def generate_damage_sound(self):
        if 'damage' not in self.sound_cache:
            self.sound_cache['damage'] = self.generate_noise_burst(0.15, 0.3)
        return self.sound_cache['damage']

    def generate_pearl_sound(self):
        if 'pearl' not in self.sound_cache:
            data = bytearray()
            for freq in [1000, 1200, 1500]:
                samples = int(self.sample_rate * 0.08)
                for i in range(samples):
                    t = i / self.sample_rate
                    value = int(127 + 127 * 0.25 * math.sin(2 * math.pi * freq * t))
                    data.append(value)
            self.sound_cache['pearl'] = pygame.mixer.Sound(buffer=data)
        return self.sound_cache['pearl']

    def generate_oxygen_warning(self):
        if 'oxygen_warning' not in self.sound_cache:
            data = bytearray()
            for _ in range(3):
                samples = int(self.sample_rate * 0.1)
                for i in range(samples):
                    t = i / self.sample_rate
                    value = int(127 + 127 * 0.3 * math.sin(2 * math.pi * 600 * t))
                    data.append(value)
                silence = int(self.sample_rate * 0.05)
                for _ in range(silence):
                    data.append(128)
            self.sound_cache['oxygen_warning'] = pygame.mixer.Sound(buffer=data)
        return self.sound_cache['oxygen_warning']

    def generate_cast_sound(self):
        if 'cast' not in self.sound_cache:
            self.sound_cache['cast'] = self.generate_sine_wave(200, 0.2, 0.25)
        return self.sound_cache['cast']

sound_gen = SoundGenerator()

class Diver:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = 0
        self.oxygen = 100
        self.health = 100
        self.gold = 0
        self.speed = 3
        self.hook_out = False
        self.hook_x = self.x
        self.hook_y = self.y
        self.hook_length = 0
        self.max_hook_length = 200
        self.catching_fish = None
        self.vertical_velocity = 0
        self.facing_right = True
        self.warning_played = False

    def update(self, keys):
        if self.y > 0:
            self.y -= self.speed * 0.5

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
            self.facing_right = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed * 0.7

        self.x = max(30, min(WIDTH - 30, self.x))
        self.y = max(0, min(DEPTH_MAX, self.y))

        depth_factor = 1 + (self.y / DEPTH_MAX) * 2
        self.oxygen -= 0.05 * depth_factor
        self.oxygen = max(0, self.oxygen)

        if self.y > CRITICAL_DEPTH:
            self.health -= 0.08 * depth_factor
            if not self.warning_played:
                sound_gen.generate_damage_sound().play()
                self.warning_played = True
        else:
            self.warning_played = False

        if self.oxygen < 20:
            sound_gen.generate_oxygen_warning().play()

        if self.hook_out and self.catching_fish is None:
            self.hook_length += 8
            self.hook_x = self.x + (50 if self.facing_right else -50)
            self.hook_y = self.y + self.hook_length

            if self.hook_length >= self.max_hook_length:
                self.hook_out = False
                self.hook_length = 0
                sound_gen.generate_cast_sound().play()

    def cast_hook(self):
        if not self.hook_out:
            self.hook_out = True
            self.hook_length = 0
            self.hook_x = self.x + (50 if self.facing_right else -50)
            self.hook_y = self.y + 20
            self.catching_fish = None
            sound_gen.generate_cast_sound().play()

    def pull_hook(self):
        self.hook_out = False
        self.hook_length = 0
        if self.catching_fish:
            self.gold += self.catching_fish.value
            self.catching_fish = None

    def draw(self, camera_y):
        screen_y = HEIGHT // 2 - camera_y + self.y

        alpha = max(0, min(255, 255 - int((self.y / DEPTH_MAX) * 100)))
        base_color = (min(255, OCEAN_LIGHT[0] + alpha // 4),
                      min(255, OCEAN_LIGHT[1] + alpha // 4),
                      min(255, OCEAN_LIGHT[2]))

        if self.hook_out:
            hook_start_x = self.x + (50 if self.facing_right else -50)
            hook_start_y = self.y + 20
            pygame.draw.line(screen, GOLD, (hook_start_x, hook_start_y - camera_y),
                           (self.hook_x, self.hook_y - camera_y), 2)

            hook_dir = 1 if self.facing_right else -1
            pygame.draw.circle(screen, GOLD,
                             (int(self.hook_x), int(self.hook_y - camera_y)), 6)

            pygame.draw.polygon(screen, GOLD, [
                (self.hook_x + 10 * hook_dir, self.hook_y - camera_y),
                (self.hook_x, self.hook_y - 8 - camera_y),
                (self.hook_x, self.hook_y + 8 - camera_y)
            ])

        if self.catching_fish:
            self.catching_fish.draw(screen, camera_y, self.hook_x, self.hook_y)

        body_rect = pygame.Rect(self.x - 15, screen_y - 20, 30, 35)
        pygame.draw.ellipse(screen, base_color, body_rect)
        pygame.draw.ellipse(screen, base_color, (self.x - 20, screen_y - 25, 40, 30))

        mask_x = self.x + (10 if self.facing_right else -10)
        pygame.draw.ellipse(screen, BLACK, (mask_x - 8, screen_y - 18, 16, 10))

        goggle_rim = pygame.Rect(mask_x - 6, screen_y - 16, 12, 6)
        pygame.draw.rect(screen, SILVER, goggle_rim, 1)

        tank_x = self.x + (-15 if self.facing_right else 5)
        pygame.draw.rect(screen, SILVER, (tank_x, screen_y - 15, 10, 25), border_radius=3)

        flipper_offset = 5 if self.facing_right else -25
        pygame.draw.ellipse(screen, BLACK, (self.x + flipper_offset, screen_y + 15, 20, 8))

        leg_offset = -8 if self.facing_right else 8
        pygame.draw.line(screen, base_color, (self.x + leg_offset, screen_y + 10),
                        (self.x + leg_offset - 5, screen_y + 25), 4)


class Fish:
    def __init__(self, depth, fish_type=None):
        self.x = random.randint(50, WIDTH - 50)
        self.y = depth + random.randint(-100, 100)
        self.base_y = self.y
        self.swim_timer = random.uniform(0, math.pi * 2)
        self.direction = random.choice([-1, 1])
        self.vertical_dir = random.choice([-1, 1])

        if fish_type is None:
            if depth < 300:
                self.type = random.choice(['small', 'small', 'medium'])
            elif depth < 700:
                self.type = random.choice(['small', 'medium', 'medium'])
            elif depth < 1200:
                self.type = random.choice(['medium', 'large', 'rare'])
            elif depth < 1700:
                self.type = random.choice(['large', 'rare', 'legendary'])
            else:
                self.type = random.choice(['rare', 'legendary', 'legendary'])
        else:
            self.type = fish_type

        type_configs = {
            'small': {'size': (15, 10), 'speed': 2, 'value': 5, 'color': CYAN, 'name': '小丑鱼'},
            'medium': {'size': (25, 15), 'speed': 1.5, 'value': 15, 'color': ORANGE, 'name': '神仙鱼'},
            'large': {'size': (40, 22), 'speed': 1, 'value': 40, 'color': PURPLE, 'name': '石斑鱼'},
            'rare': {'size': (35, 18), 'speed': 2.5, 'value': 80, 'color': PINK, 'name': '海马'},
            'legendary': {'size': (50, 28), 'speed': 0.8, 'value': 200, 'color': GOLD, 'name': '金龙鱼'}
        }

        config = type_configs[self.type]
        self.width, self.height = config['size']
        self.speed = config['speed']
        self.value = config['value']
        self.color = config['color']
        self.name = config['name']
        self.caught = False

    def update(self):
        self.swim_timer += 0.05
        self.x += self.speed * self.direction
        self.y = self.base_y + math.sin(self.swim_timer) * 15 + self.vertical_dir * 0.5

        if self.x < -50:
            self.x = WIDTH + 50
        elif self.x > WIDTH + 50:
            self.x = -50

        if self.swim_timer > math.pi * 4:
            self.direction *= -1
            self.swim_timer = 0

    def draw(self, camera_y, override_x=None, override_y=None):
        if override_x is not None:
            draw_x = override_x
            draw_y = override_y - camera_y
        else:
            draw_x = self.x
            draw_y = self.y - camera_y

        if self.type == 'legendary':
            glow_size = int(8 + 4 * math.sin(self.swim_timer * 2))
            glow_surf = pygame.Surface((self.width * 2 + glow_size * 2,
                                        self.height * 2 + glow_size * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (*self.color, 80),
                              (glow_size, glow_size, self.width * 2, self.height))
            screen.blit(glow_surf, (draw_x - self.width - glow_size,
                                   draw_y - self.height - glow_size))

        body_rect = pygame.Rect(draw_x - self.width // 2, draw_y - self.height // 2,
                               self.width, self.height)
        pygame.draw.ellipse(screen, self.color, body_rect)

        tail_x = draw_x + (self.width // 2 if self.direction > 0 else -self.width // 2)
        tail_points = [
            (tail_x, draw_y),
            (tail_x + 15 * self.direction, draw_y - self.height // 2),
            (tail_x + 15 * self.direction, draw_y + self.height // 2)
        ]
        pygame.draw.polygon(screen, self.color, tail_points)

        eye_x = draw_x + (-8 if self.direction > 0 else 8)
        pygame.draw.circle(screen, WHITE, (int(eye_x), int(draw_y - 2)), 4)
        pygame.draw.circle(screen, BLACK, (int(eye_x + (2 if self.direction > 0 else -2)), int(draw_y - 2)), 2)

        if self.type == 'rare':
            crown_y = draw_y - self.height // 2 - 8
            crown_points = [(draw_x - 8, crown_y + 8), (draw_x - 5, crown_y),
                           (draw_x, crown_y + 5), (draw_x + 5, crown_y),
                           (draw_x + 8, crown_y + 8)]
            pygame.draw.lines(screen, GOLD, False, crown_points, 2)

    def check_hook_collision(self, hook_x, hook_y):
        distance = math.sqrt((self.x - hook_x) ** 2 + (self.y - hook_y) ** 2)
        return distance < self.width // 2 + 20


class Pearl:
    def __init__(self, depth):
        self.x = random.randint(50, WIDTH - 50)
        self.y = depth + random.randint(50, 200)
        self.collected = False
        self.sparkle_timer = random.uniform(0, math.pi * 2)
        self.value = random.choice([10, 15, 25])

    def update(self):
        self.sparkle_timer += 0.1

    def draw(self, camera_y):
        if self.collected:
            return

        draw_x = self.x
        draw_y = self.y - camera_y

        shimmer = int(0.5 + 0.5 * math.sin(self.sparkle_timer))
        brightness = 200 + shimmer * 55

        base_color = (brightness, brightness, min(255, brightness + 20))

        for i in range(3):
            offset_x = math.cos(self.sparkle_timer + i * 2) * 3
            offset_y = math.sin(self.sparkle_timer + i * 2) * 3
            pygame.draw.circle(screen, WHITE,
                             (int(draw_x + offset_x), int(draw_y + offset_y)), 2)

        pygame.draw.circle(screen, base_color, (draw_x, draw_y), 8)
        pygame.draw.circle(screen, WHITE, (draw_x - 2, draw_y - 2), 3)

        shell_rect = pygame.Rect(draw_x - 12, draw_y + 6, 24, 10)
        pygame.draw.arc(screen, (180, 150, 120), shell_rect, 0, math.pi, 2)

    def check_collision(self, diver_x, diver_y):
        distance = math.sqrt((self.x - diver_x) ** 2 + (self.y - diver_y) ** 2)
        return distance < 40


class Bubble:
    def __init__(self, x, y):
        self.x = x + random.randint(-10, 10)
        self.y = y
        self.size = random.randint(3, 8)
        self.speed = random.uniform(1, 2)
        self.wobble = random.uniform(0, math.pi * 2)

    def update(self):
        self.y -= self.speed
        self.wobble += 0.1
        self.x += math.sin(self.wobble) * 0.5

    def draw(self, camera_y):
        draw_y = self.y - camera_y
        pygame.draw.circle(screen, (200, 230, 255), (int(self.x), int(draw_y)), self.size)
        pygame.draw.circle(screen, (255, 255, 255),
                         (int(self.x - self.size // 2), int(draw_y - self.size // 2)),
                         max(1, self.size // 3))


def get_depth_color(depth):
    if depth < 100:
        return OCEAN_LIGHT
    elif depth < 300:
        ratio = (depth - 100) / 200
        return (
            int(OCEAN_LIGHT[0] + (OCEAN_MEDIUM[0] - OCEAN_LIGHT[0]) * ratio),
            int(OCEAN_LIGHT[1] + (OCEAN_MEDIUM[1] - OCEAN_LIGHT[1]) * ratio),
            int(OCEAN_LIGHT[2] + (OCEAN_MEDIUM[2] - OCEAN_LIGHT[2]) * ratio)
        )
    elif depth < 700:
        ratio = (depth - 300) / 400
        return (
            int(OCEAN_MEDIUM[0] + (OCEAN_DEEP[0] - OCEAN_MEDIUM[0]) * ratio),
            int(OCEAN_MEDIUM[1] + (OCEAN_DEEP[1] - OCEAN_MEDIUM[1]) * ratio),
            int(OCEAN_MEDIUM[2] + (OCEAN_DEEP[2] - OCEAN_MEDIUM[2]) * ratio)
        )
    else:
        ratio = min(1, (depth - 700) / 500)
        return (
            int(OCEAN_DEEP[0] + (OCEAN_ABYSS[0] - OCEAN_DEEP[0]) * ratio),
            int(OCEAN_DEEP[1] + (OCEAN_ABYSS[1] - OCEAN_DEEP[1]) * ratio),
            int(OCEAN_DEEP[2] + (OCEAN_ABYSS[2] - OCEAN_DEEP[2]) * ratio)
        )


def draw_depth_background(camera_y):
    water_height = 60
    for y in range(HEIGHT):
        world_y = y + camera_y
        if world_y < 50:
            screen.set_at((0, y), SKY_BLUE)
        elif world_y < 100:
            blend_ratio = (world_y - 50) / 50
            color = tuple(int(SKY_BLUE[i] + (OCEAN_LIGHT[i] - SKY_BLUE[i]) * blend_ratio)
                         for i in range(3))
            screen.set_at((0, y), color)
        else:
            depth = world_y - 100
            color = get_depth_color(depth)
            screen.set_at((0, y), color)

    for x in range(1, WIDTH):
        world_y_base = camera_y + HEIGHT
        depth = max(0, world_y_base - 100)
        color = get_depth_color(depth)
        screen.set_at((x, HEIGHT - 1), color)
        for y in range(1, HEIGHT):
            world_y = y + camera_y
            if world_y >= 50 and world_y < 100:
                blend_ratio = (world_y - 50) / 50
                color = tuple(int(SKY_BLUE[i] + (OCEAN_LIGHT[i] - SKY_BLUE[i]) * blend_ratio)
                             for i in range(3))
            elif world_y >= 100:
                depth = world_y - 100
                color = get_depth_color(depth)
            screen.set_at((x, y), color)


def draw_seaweed(x, base_y, camera_y, height_range):
    draw_x = x
    for i, h in enumerate(height_range):
        draw_y = base_y + i * 8 - camera_y
        if 0 <= draw_y <= HEIGHT:
            offset = int(5 * math.sin(pygame.time.get_ticks() * 0.002 + x * 0.1 + i * 0.5))
            pygame.draw.line(screen, (34, 139, 34), (draw_x + offset, draw_y),
                           (draw_x + offset, draw_y - h % 20), 2)


def draw_rocks(x, base_y, camera_y):
    draw_x = x
    draw_y = base_y - camera_y
    if 0 <= draw_y <= HEIGHT:
        pygame.draw.ellipse(screen, (60, 60, 70), (draw_x - 15, draw_y - 10, 30, 20))
        pygame.draw.ellipse(screen, (50, 50, 60), (draw_x - 10, draw_y - 15, 20, 25))


def draw_surface():
    wave_height = 8
    for x in range(0, WIDTH, 20):
        wave_y = int(30 + wave_height * math.sin(x * 0.02 + pygame.time.get_ticks() * 0.003))
        pygame.draw.line(screen, WHITE, (x, wave_y), (x + 10, wave_y + 2), 2)

    sun_x, sun_y = WIDTH - 80, 50
    pygame.draw.circle(screen, GOLD, (sun_x, sun_y), 30)
    for i in range(8):
        angle = i * math.pi / 4 + pygame.time.get_ticks() * 0.001
        ray_x = sun_x + int(40 * math.cos(angle))
        ray_y = sun_y + int(40 * math.sin(angle))
        pygame.draw.line(screen, GOLD, (sun_x, sun_y), (ray_x, ray_y), 2)

    pygame.draw.rect(screen, OCEAN_LIGHT, (0, 25, WIDTH, 35))
    for x in range(0, WIDTH, 40):
        wave_offset = int(5 * math.sin(pygame.time.get_ticks() * 0.002 + x * 0.05))
        pygame.draw.arc(screen, WHITE, (x, 30 + wave_offset, 35, 15), 0, math.pi, 2)


def show_game_over(score, gold):
    screen.fill(BLACK)
    game_over_text = title_font.render("游戏结束!", True, RED)
    score_text = font.render(f"最终得分: {score}", True, WHITE)
    gold_text = font.render(f"收集金币: {gold}", True, GOLD)

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 80))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(gold_text, (WIDTH // 2 - gold_text.get_width() // 2, HEIGHT // 2 + 40))

    restart_text = small_font.render("按 R 键重新开始", True, WHITE)
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 100))

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    return True
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
    return False


def show_start_screen():
    screen.fill(OCEAN_DEEP)

    title = title_font.render("深海潜水钓鱼", True, GOLD)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    instructions = [
        "操作说明:",
        "方向键/WASD - 移动潜水员",
        "空格键 - 发射钓鱼竿",
        "",
        "氧气说明:",
        "- 越深氧气消耗越快",
        "- 氧气耗尽将失去生命",
        "",
        "深度说明:",
        f"- 安全深度: 0-{SAFE_DEPTH}米 (绿色)",
        f"- 危险深度: {SAFE_DEPTH}-{CRITICAL_DEPTH}米 (黄色)",
        f"- 致命深度: {CRITICAL_DEPTH}+米 (红色)",
        "",
        "鱼类价值:",
        "- 小丑鱼: 5金币",
        "- 神仙鱼: 15金币",
        "- 石斑鱼: 40金币",
        "- 海马(稀有): 80金币",
        "- 金龙鱼(传说): 200金币",
        "",
        "按空格键开始游戏"
    ]

    y_offset = 160
    for line in instructions:
        color = WHITE
        if "价值" in line or "传说" in line or "稀有" in line:
            color = GOLD
        elif "致命" in line:
            color = RED
        elif "危险" in line:
            color = ORANGE
        elif "安全" in line:
            color = GREEN
        text = small_font.render(line, True, color)
        screen.blit(text, (WIDTH // 2 - 150, y_offset))
        y_offset += 25

    for i in range(10):
        bubble_x = random.randint(50, WIDTH - 50)
        bubble_y = random.randint(100, HEIGHT - 50)
        bubble_size = random.randint(5, 15)
        alpha = random.randint(50, 150)
        surf = pygame.Surface((bubble_size * 2, bubble_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (200, 230, 255, alpha), (bubble_size, bubble_size), bubble_size)
        screen.blit(surf, (bubble_x - bubble_size, bubble_y - bubble_size))

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                    return True
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        clock.tick(30)


def main_game():
    diver = Diver()
    fishes = []
    pearls = []
    bubbles = []
    seaweed_positions = []
    rock_positions = []

    score = 0
    camera_y = 0
    fish_spawn_timer = 0
    pearl_spawn_timer = 0
    bubble_timer = 0
    game_running = True

    for x in range(100, WIDTH, 150):
        seaweed_positions.append((x, DEPTH_MAX - 50 + random.randint(-100, 100)))
    for x in range(50, WIDTH, 200):
        rock_positions.append((x, DEPTH_MAX - 30 + random.randint(-50, 50)))

    while game_running:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if diver.hook_out:
                        diver.pull_hook()
                        if diver.catching_fish:
                            sound_gen.generate_catch_sound().play()
                            score += diver.catching_fish.value
                    else:
                        diver.cast_hook()

        diver.update(keys)

        if diver.hook_out and diver.catching_fish is None:
            for fish in fishes:
                if fish.check_hook_collision(diver.hook_x, diver.hook_y):
                    diver.catching_fish = fish
                    diver.hook_length = math.sqrt((fish.x - diver.x) ** 2 +
                                                   (fish.y - diver.y) ** 2)
                    sound_gen.generate_catch_sound().play()
                    break

        if diver.catching_fish:
            diver.hook_x = diver.x + (50 if diver.facing_right else -50)
            diver.hook_y = diver.y + 20

        camera_y = diver.y - HEIGHT // 2

        fish_spawn_timer += 1
        if fish_spawn_timer > 60:
            fish_spawn_timer = 0
            new_fish_depth = diver.y + random.randint(-300, 300)
            new_fish_depth = max(50, min(DEPTH_MAX - 50, new_fish_depth))
            fishes.append(Fish(new_fish_depth))

        pearl_spawn_timer += 1
        if pearl_spawn_timer > 180:
            pearl_spawn_timer = 0
            pearl_depth = random.randint(100, DEPTH_MAX - 100)
            pearls.append(Pearl(pearl_depth))

        bubble_timer += 1
        if bubble_timer > 10:
            bubble_timer = 0
            bubbles.append(Bubble(diver.x, diver.y))

        for fish in fishes[:]:
            fish.update()
            if diver.catching_fish == fish:
                continue
            if fish.y < camera_y - 100 or fish.y > camera_y + HEIGHT + 100:
                fishes.remove(fish)

        for pearl in pearls[:]:
            pearl.update()
            if pearl.check_collision(diver.x, diver.y):
                diver.gold += pearl.value
                pearl.collected = True
                sound_gen.generate_pearl_sound().play()
                pearls.remove(pearl)
            elif pearl.y < camera_y - 50 or pearl.y > camera_y + HEIGHT + 50:
                pearls.remove(pearl)

        for bubble in bubbles[:]:
            bubble.update()
            if bubble.y < camera_y - 50:
                bubbles.remove(bubble)

        draw_depth_background(camera_y)

        draw_surface()

        for x, y in seaweed_positions:
            if camera_y - 100 < y < camera_y + HEIGHT + 100:
                draw_seaweed(x, y, camera_y, [random.randint(20, 40) for _ in range(3)])

        for x, y in rock_positions:
            if camera_y - 50 < y < camera_y + HEIGHT + 50:
                draw_rocks(x, y, camera_y)

        for pearl in pearls:
            if camera_y - 50 < pearl.y < camera_y + HEIGHT + 50:
                pearl.draw(camera_y)

        for fish in fishes:
            if camera_y - 50 < fish.y < camera_y + HEIGHT + 50:
                fish.draw(camera_y)

        for bubble in bubbles:
            if camera_y - 50 < bubble.y < camera_y + HEIGHT + 50:
                bubble.draw(camera_y)

        diver.draw(camera_y)

        panel_height = 60
        pygame.draw.rect(screen, (20, 20, 40), (0, HEIGHT - panel_height, WIDTH, panel_height))

        oxygen_bar_width = 150
        oxygen_ratio = diver.oxygen / 100
        oxygen_color = GREEN if oxygen_ratio > 0.3 else RED
        pygame.draw.rect(screen, (50, 50, 50), (20, HEIGHT - 40, oxygen_bar_width, 20))
        pygame.draw.rect(screen, oxygen_color,
                        (20, HEIGHT - 40, int(oxygen_bar_width * oxygen_ratio), 20))
        oxygen_text = font.render(f"氧气: {int(diver.oxygen)}%", True, WHITE)
        screen.blit(oxygen_text, (25, HEIGHT - 55))

        health_bar_width = 150
        health_ratio = diver.health / 100
        health_color = GREEN if health_ratio > 0.3 else RED
        pygame.draw.rect(screen, (50, 50, 50), (200, HEIGHT - 40, health_bar_width, 20))
        pygame.draw.rect(screen, health_color,
                        (200, HEIGHT - 40, int(health_bar_width * health_ratio), 20))
        health_text = font.render(f"生命: {int(diver.health)}%", True, WHITE)
        screen.blit(health_text, (205, HEIGHT - 55))

        gold_text = font.render(f"金币: {diver.gold}", True, GOLD)
        screen.blit(gold_text, (380, HEIGHT - 50))

        depth_text = font.render(f"深度: {diver.y}米", True, WHITE)
        screen.blit(depth_text, (500, HEIGHT - 50))

        if diver.y > CRITICAL_DEPTH:
            danger_text = font.render("警告: 危险深度!", True, DANGER_RED)
            screen.blit(danger_text, (WIDTH - 200, HEIGHT - 50))
        elif diver.y > SAFE_DEPTH:
            warning_text = font.render("注意: 超出安全深度", True, ORANGE)
            screen.blit(warning_text, (WIDTH - 220, HEIGHT - 50))

        score_text = font.render(f"得分: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH - 150, HEIGHT - 25))

        hook_hint = small_font.render("空格: 发射/收回钓鱼竿", True, WHITE)
        screen.blit(hook_hint, (20, HEIGHT - 20))

        pygame.display.update()
        clock.tick(60)

        if diver.oxygen <= 0:
            diver.health -= 0.5

        if diver.health <= 0:
            game_running = False

    return score, diver.gold


def main():
    while True:
        if not show_start_screen():
            break

        score, gold = main_game()

        if not show_game_over(score, gold):
            break


if __name__ == "__main__":
    main()
