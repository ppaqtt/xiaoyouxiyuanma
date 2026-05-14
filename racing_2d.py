"""
涡轮漂移赛车 - 俯视角赛道赛车游戏
独特的漂移与涡轮加速系统
"""

import pygame
import sys
import math
import time
import struct
import random

pygame.init()

WIDTH, HEIGHT = 800, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("涡轮漂移赛车")
clock = pygame.time.Clock()

COLOR_BG = (20, 25, 35)
COLOR_TRACK = (50, 55, 65)
COLOR_TRACK_EDGE = (80, 85, 95)
COLOR_GRASS = (35, 80, 40)
COLOR_START_LINE = (255, 255, 255)
COLOR_CAR = (220, 50, 50)
COLOR_TURBO_BAR = (0, 200, 255)
COLOR_TURBO_ACTIVE = (255, 150, 0)
COLOR_TIRE_BAR = (80, 80, 80)
COLOR_TIRE_WARN = (200, 50, 50)
COLOR_LAP = (255, 215, 0)
COLOR_BEST_LAP = (100, 255, 100)

TRACK_CENTER_X = WIDTH // 2
TRACK_CENTER_Y = HEIGHT // 2 + 20
TRACK_RADIUS_X = 320
TRACK_RADIUS_Y = 220
TRACK_WIDTH = 100

CAR_LENGTH = 36
CAR_WIDTH = 18
CAR_MAX_SPEED = 6.5
CAR_ACCEL = 0.08
CAR_BRAKE = 0.12
CAR_TURN_SPEED = 2.8
DRIFT_TURN_BONUS = 1.6

TURBO_MAX = 100
TURBO_GAIN_RATE = 1.2
TURBO_DECAY_RATE = 0.4
TURBO_BOOST_MULT = 1.8
TURBO_BOOST_DURATION = 40

TIRE_MAX = 100
TIRE_DRIFT_RATE = 0.5
TIRE_RECOVER_RATE = 0.15
TIRE_SPEED_PENALTY = 0.7

pygame.mixer.init(frequency=22050, size=-8, channels=1, buffer=512)
sound_engine = None
sound_drift = None
sound_turbo = None
sound_lap = None


def generate_engine_sound():
    global sound_engine
    sample_rate = 22050
    duration = 0.15
    samples = int(sample_rate * duration)
    data = bytearray()
    for i in range(samples):
        t = i / sample_rate
        freq = 80 + (i % 200) * 0.5
        wave = math.sin(2 * math.pi * freq * t)
        wave += math.sin(2 * math.pi * freq * 2 * t) * 0.3
        wave += math.sin(2 * math.pi * freq * 0.5 * t) * 0.2
        value = int(wave * 4000)
        data.extend(struct.pack('h', max(-32768, min(32767, value))))
    sound_engine = pygame.mixer.Sound(buffer=bytes(data))


def generate_drift_sound():
    global sound_drift
    sample_rate = 22050
    duration = 0.3
    samples = int(sample_rate * duration)
    data = bytearray()
    for i in range(samples):
        t = i / sample_rate
        noise = random.uniform(-1, 1)
        rumble = math.sin(2 * math.pi * 60 * t) * 0.5
        envelope = 1.0 - (i / samples) * 0.6
        wave = (noise * 0.6 + rumble) * envelope
        value = int(wave * 5000)
        data.extend(struct.pack('h', max(-32768, min(32767, value))))
    sound_drift = pygame.mixer.Sound(buffer=bytes(data))


def generate_turbo_sound():
    global sound_turbo
    sample_rate = 22050
    duration = 0.5
    samples = int(sample_rate * duration)
    data = bytearray()
    for i in range(samples):
        t = i / sample_rate
        freq = 150 + i * 2
        wave1 = math.sin(2 * math.pi * freq * t)
        wave2 = math.sin(2 * math.pi * freq * 1.5 * t) * 0.5
        noise = random.uniform(-0.3, 0.3)
        envelope = (1.0 - (i / samples) * 0.5) if i > samples * 0.3 else 1.0
        wave = (wave1 + wave2 + noise) * envelope
        value = int(wave * 6000)
        data.extend(struct.pack('h', max(-32768, min(32767, value))))
    sound_turbo = pygame.mixer.Sound(buffer=bytes(data))


def generate_lap_sound():
    global sound_lap
    sample_rate = 22050
    duration = 0.6
    samples = int(sample_rate * duration)
    data = bytearray()
    notes = [523, 659, 784, 1047]
    note_duration = samples // len(notes)
    for i in range(samples):
        t = i / sample_rate
        note_idx = min(i // note_duration, len(notes) - 1)
        freq = notes[note_idx]
        attack = min(1.0, i / (sample_rate * 0.02))
        decay = max(0.0, 1.0 - (i % note_duration) / (note_duration * 0.7))
        wave = math.sin(2 * math.pi * freq * t)
        wave = wave * attack * decay
        value = int(wave * 8000)
        data.extend(struct.pack('h', max(-32768, min(32767, value))))
    sound_lap = pygame.mixer.Sound(buffer=bytes(data))


generate_engine_sound()
generate_drift_sound()
generate_turbo_sound()
generate_lap_sound()

engine_channel = pygame.mixer.Channel(0)
drift_channel = pygame.mixer.Channel(1)
effect_channel = pygame.mixer.Channel(2)


class PlayerCar:
    def __init__(self):
        self.x = TRACK_CENTER_X
        self.y = TRACK_CENTER_Y + TRACK_RADIUS_Y
        self.angle = -90
        self.speed = 0
        self.angular_vel = 0
        self.drifting = False
        self.turbo = 0
        self.turbo_active = False
        self.turbo_timer = 0
        self.tire_wear = TIRE_MAX
        self.lap_count = 0
        self.lap_start_time = 0
        self.current_lap_time = 0
        self.best_lap_time = float('inf')
        self.last_checkpoint = 0
        self.finished_first_lap = False
        self.drift_particles = []
        self.turbo_particles = []
        self.drift_sound_playing = False

    def reset(self):
        self.x = TRACK_CENTER_X
        self.y = TRACK_CENTER_Y + TRACK_RADIUS_Y
        self.angle = -90
        self.speed = 0
        self.angular_vel = 0
        self.drifting = False
        self.turbo = 0
        self.turbo_active = False
        self.turbo_timer = 0
        self.tire_wear = TIRE_MAX
        self.lap_count = 0
        self.lap_start_time = time.time()
        self.current_lap_time = 0
        self.last_checkpoint = 0
        self.finished_first_lap = False
        self.drift_particles = []
        self.turbo_particles = []
        self.drift_sound_playing = False

    def get_track_angle(self):
        dx = self.x - TRACK_CENTER_X
        dy = self.y - TRACK_CENTER_Y
        return math.atan2(dy, dx)

    def get_track_curvature(self):
        angle = self.get_track_angle()
        return abs(math.sin(angle * 2))

    def is_on_track(self):
        dx = (self.x - TRACK_CENTER_X) / TRACK_RADIUS_X
        dy = (self.y - TRACK_CENTER_Y) / TRACK_RADIUS_Y
        dist = math.sqrt(dx * dx + dy * dy)
        inner_edge = 1 - TRACK_WIDTH / 2 / min(TRACK_RADIUS_X, TRACK_RADIUS_Y)
        outer_edge = 1 + TRACK_WIDTH / 2 / min(TRACK_RADIUS_X, TRACK_RADIUS_Y)
        return inner_edge < dist < outer_edge

    def update(self, keys):
        self.drifting = keys[pygame.K_SPACE]

        turn_amount = CAR_TURN_SPEED
        if self.drifting:
            turn_amount *= DRIFT_TURN_BONUS

        if keys[pygame.K_LEFT]:
            self.angle -= turn_amount
        if keys[pygame.K_RIGHT]:
            self.angle += turn_amount

        if keys[pygame.K_UP]:
            tire_factor = self.tire_wear / TIRE_MAX if self.tire_wear < TIRE_MAX else 1.0
            base_accel = CAR_ACCEL * tire_factor
            if self.turbo_active:
                base_accel *= TURBO_BOOST_MULT
            self.speed += base_accel
        elif keys[pygame.K_DOWN]:
            self.speed -= CAR_BRAKE
        else:
            self.speed *= 0.97

        max_speed = CAR_MAX_SPEED
        if self.turbo_active:
            max_speed *= TURBO_BOOST_MULT
        elif self.tire_wear < 30:
            max_speed *= TIRE_SPEED_PENALTY

        self.speed = max(0, min(max_speed, self.speed))

        if self.speed > 1 and self.drifting:
            self.turbo = min(TURBO_MAX, self.turbo + TURBO_GAIN_RATE)
            self.tire_wear = max(0, self.tire_wear - TIRE_DRIFT_RATE)

            if random.random() < 0.4:
                self.drift_particles.append({
                    'x': self.x - math.cos(math.radians(self.angle)) * 15,
                    'y': self.y + math.sin(math.radians(self.angle)) * 15,
                    'vx': random.uniform(-2, 2),
                    'vy': random.uniform(-2, 2),
                    'life': 30,
                    'size': random.randint(3, 6)
                })

            if not self.drift_sound_playing and sound_drift:
                drift_channel.play(sound_drift, loops=-1)
                self.drift_sound_playing = True
        else:
            if self.drift_sound_playing:
                drift_channel.stop()
                self.drift_sound_playing = False

        if not self.drifting and self.turbo > 20:
            curvature = self.get_track_curvature()
            if curvature < 0.3 and self.speed > 3:
                self.turbo_active = True
                self.turbo_timer = TURBO_BOOST_DURATION
                if sound_turbo:
                    effect_channel.play(sound_turbo)
                for _ in range(15):
                    self.turbo_particles.append({
                        'x': self.x,
                        'y': self.y,
                        'vx': -math.cos(math.radians(self.angle)) * random.uniform(3, 6),
                        'vy': math.sin(math.radians(self.angle)) * random.uniform(3, 6),
                        'life': 20,
                        'size': random.randint(4, 8)
                    })

        if self.turbo_active:
            self.turbo_timer -= 1
            self.turbo = max(0, self.turbo - 2)
            if self.turbo_timer <= 0:
                self.turbo_active = False
                self.turbo = max(0, self.turbo - TURBO_GAIN_RATE * 2)

        if not self.drifting:
            self.tire_wear = min(TIRE_MAX, self.tire_wear + TIRE_RECOVER_RATE)

        rad = math.radians(self.angle)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed

        margin = 50
        self.x = max(margin, min(WIDTH - margin, self.x))
        self.y = max(margin, min(HEIGHT - margin, self.y))

        self.update_lap_progress()

        for p in self.drift_particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            p['size'] *= 0.95
        self.drift_particles = [p for p in self.drift_particles if p['life'] > 0]

        for p in self.turbo_particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
        self.turbo_particles = [p for p in self.turbo_particles if p['life'] > 0]

    def update_lap_progress(self):
        track_angle = self.get_track_angle()
        checkpoint = int((track_angle + math.pi) / (2 * math.pi) * 100) % 100

        if self.last_checkpoint > 90 and checkpoint < 10:
            self.lap_count += 1
            self.current_lap_time = time.time() - self.lap_start_time

            if self.finished_first_lap and self.current_lap_time < self.best_lap_time:
                self.best_lap_time = self.current_lap_time
                if sound_lap:
                    effect_channel.play(sound_lap)

            self.lap_start_time = time.time()
            self.finished_first_lap = True

        self.last_checkpoint = checkpoint

    def draw(self):
        for p in self.drift_particles:
            alpha = int(200 * p['life'] / 30)
            size = int(p['size'])
            if size > 0:
                pygame.draw.circle(screen, (180, 180, 180), (int(p['x']), int(p['y'])), size)

        for p in self.turbo_particles:
            colors = [(255, 200, 50), (255, 150, 0), (255, 100, 0)]
            color = colors[min(p['life'] // 7, 2)]
            pygame.draw.circle(screen, color, (int(p['x']), int(p['y'])), int(p['size']))

        if self.turbo_active:
            glow_radius = 30 + math.sin(time.time() * 20) * 5
            glow_surf = pygame.Surface((glow_radius * 2 + 10, glow_radius * 2 + 10), pygame.SRCALPHA)
            for r in range(int(glow_radius), 0, -3):
                alpha = int(50 * (1 - r / glow_radius))
                pygame.draw.circle(glow_surf, (*COLOR_TURBO_ACTIVE, alpha), (glow_radius + 5, glow_radius + 5), r)
            screen.blit(glow_surf, (self.x - glow_radius - 5, self.y - glow_radius - 5))

        car_surf = pygame.Surface((CAR_LENGTH + 10, CAR_WIDTH + 10), pygame.SRCALPHA)
        car_center = (CAR_LENGTH // 2 + 5, CAR_WIDTH // 2 + 5)

        pygame.draw.rect(car_surf, (40, 40, 50), (3, 0, CAR_LENGTH - 6, CAR_WIDTH), border_radius=4)
        pygame.draw.rect(car_surf, COLOR_CAR, (0, 0, CAR_LENGTH, CAR_WIDTH), border_radius=6)

        if self.drifting:
            pygame.draw.rect(car_surf, (255, 220, 50), (CAR_LENGTH - 12, 3, 9, CAR_WIDTH - 6), border_radius=2)
        if self.turbo_active:
            for i in range(3):
                offset = int(math.sin(time.time() * 15 + i) * 2)
                pygame.draw.circle(car_surf, (255, 150, 0), (CAR_LENGTH - 3 + offset, CAR_WIDTH // 2), 4 - i)

        window = pygame.Surface((CAR_LENGTH - 16, CAR_WIDTH - 8), pygame.SRCALPHA)
        pygame.draw.rect(window, (100, 150, 200, 180), window.get_rect(), border_radius=3)
        car_surf.blit(window, (10, 4))

        rotated = pygame.transform.rotate(car_surf, -self.angle)
        rot_rect = rotated.get_rect(center=(self.x, self.y))
        screen.blit(rotated, rot_rect)


def draw_track():
    pygame.draw.rect(screen, COLOR_GRASS, (0, 0, WIDTH, HEIGHT))

    track_points = []
    for i in range(72):
        angle = i * 5 * math.pi / 180
        x = TRACK_CENTER_X + math.cos(angle) * TRACK_RADIUS_X
        y = TRACK_CENTER_Y + math.sin(angle) * TRACK_RADIUS_Y
        track_points.append((x, y))

    outer_points = []
    inner_points = []
    for i in range(72):
        angle = i * 5 * math.pi / 180
        outer_x = TRACK_CENTER_X + math.cos(angle) * (TRACK_RADIUS_X + TRACK_WIDTH / 2)
        outer_y = TRACK_CENTER_Y + math.sin(angle) * (TRACK_RADIUS_Y + TRACK_WIDTH / 2)
        outer_points.append((outer_x, outer_y))
        inner_x = TRACK_CENTER_X + math.cos(angle) * (TRACK_RADIUS_X - TRACK_WIDTH / 2)
        inner_y = TRACK_CENTER_Y + math.sin(angle) * (TRACK_RADIUS_Y - TRACK_WIDTH / 2)
        inner_points.append((inner_x, inner_y))

    pygame.draw.polygon(screen, COLOR_TRACK, outer_points)
    pygame.draw.polygon(screen, COLOR_GRASS, inner_points)

    pygame.draw.polygon(screen, COLOR_TRACK_EDGE, outer_points, 4)
    pygame.draw.polygon(screen, COLOR_TRACK_EDGE, inner_points, 4)

    center_x = TRACK_CENTER_X
    center_y = TRACK_CENTER_Y - TRACK_RADIUS_Y
    pygame.draw.line(screen, COLOR_START_LINE, (center_x - 50, center_y), (center_x + 50, center_y), 4)

    for i in range(-3, 4):
        dash_x = center_x + i * 15
        pygame.draw.line(screen, COLOR_START_LINE, (dash_x, center_y - 40), (dash_x, center_y + 40), 2)

    curb_points = []
    for i in range(36):
        angle = -math.pi / 2 + i * 5 * math.pi / 180
        x = TRACK_CENTER_X + math.cos(angle) * (TRACK_RADIUS_X + TRACK_WIDTH / 2 + 8)
        y = TRACK_CENTER_Y + math.sin(angle) * (TRACK_RADIUS_Y + TRACK_WIDTH / 2 + 8)
        curb_points.append((x, y))
    for i in range(0, 36, 2):
        if i < len(curb_points):
            pygame.draw.circle(screen, (255, 0, 0), curb_points[i], 4)
    for i in range(1, 36, 2):
        if i < len(curb_points):
            pygame.draw.circle(screen, (255, 255, 255), curb_points[i], 4)


def draw_hud(player):
    font_large = pygame.font.Font(None, 42)
    font_medium = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 22)

    pygame.draw.rect(screen, (0, 0, 0, 180), (15, 15, 220, 130), border_radius=12)
    pygame.draw.rect(screen, (80, 80, 80), (15, 15, 220, 130), 2, border_radius=12)

    speed_val = int(player.speed * 25)
    speed_text = font_large.render(f"{speed_val} km/h", True, (255, 255, 255))
    screen.blit(speed_text, (25, 20))

    pygame.draw.rect(screen, (50, 50, 50), (25, 60, 180, 16), border_radius=4)
    turbo_width = int(180 * player.turbo / TURBO_MAX)
    turbo_color = COLOR_TURBO_ACTIVE if player.turbo_active else COLOR_TURBO_BAR
    pygame.draw.rect(screen, turbo_color, (25, 60, max(8, turbo_width), 16), border_radius=4)
    turbo_label = font_small.render("涡轮", True, (200, 200, 200))
    screen.blit(turbo_label, (25, 78))

    pygame.draw.rect(screen, (50, 50, 50), (25, 95, 180, 16), border_radius=4)
    tire_width = int(180 * player.tire_wear / TIRE_MAX)
    tire_color = COLOR_TIRE_WARN if player.tire_wear < 30 else COLOR_TIRE_BAR
    pygame.draw.rect(screen, tire_color, (25, 95, max(8, tire_width), 16), border_radius=4)
    tire_label = font_small.render("轮胎", True, (200, 200, 200))
    screen.blit(tire_label, (25, 113))

    pygame.draw.rect(screen, (0, 0, 0, 180), (WIDTH - 195, 15, 180, 100), border_radius=12)
    pygame.draw.rect(screen, (80, 80, 80), (WIDTH - 195, 15, 180, 100), 2, border_radius=12)

    lap_text = font_medium.render(f"圈数: {player.lap_count}", True, COLOR_LAP)
    screen.blit(lap_text, (WIDTH - 185, 20))

    if player.finished_first_lap:
        current = player.current_lap_time if player.finished_first_lap else 0
        current_text = font_small.render(f"本圈: {current:.2f}s", True, (255, 255, 255))
        screen.blit(current_text, (WIDTH - 185, 50))

        best_text = font_small.render(f"最佳: {player.best_lap_time:.2f}s", True, COLOR_BEST_LAP)
        screen.blit(best_text, (WIDTH - 185, 72))

    if player.turbo_active:
        boost_text = font_medium.render("涡轮加速!", True, COLOR_TURBO_ACTIVE)
        screen.blit(boost_text, (WIDTH - 185, 92))

    instructions_text = font_small.render("空格:漂移  ↑↓:加减  ←→:转向", True, (150, 150, 150))
    screen.blit(instructions_text, (WIDTH // 2 - instructions_text.get_width() // 2, HEIGHT - 25))


def draw_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 26)

    title = font_large.render("涡轮漂移赛车", True, (255, 200, 50))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

    subtitle = font_medium.render("Turbo Drift Racing", True, (200, 200, 200))
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 130))

    instructions = [
        "空格键 - 漂移（积累涡轮能量）",
        "↑ 键 - 加速",
        "↓ 键 - 减速/刹车",
        "← → 键 - 转向",
        "",
        "漂移时积累涡轮能量",
        "直道出口释放涡轮获得加速",
        "注意轮胎磨损，过度磨损速度下降",
        "",
        "按 空格键 开始游戏"
    ]

    y = 200
    for line in instructions:
        if line:
            text = font_small.render(line, True, (220, 220, 220))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
        y += 32


class RacingGame:
    def __init__(self):
        self.player = PlayerCar()
        self.phase = "menu"
        self.last_engine_play = 0

    def reset(self):
        self.player.reset()

    def update(self):
        if self.phase != "game":
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys)

        current_time = time.time()
        if current_time - self.last_engine_play > 0.15 and self.player.speed > 0.5:
            if sound_engine and not engine_channel.get_busy():
                vol = min(1.0, self.player.speed / CAR_MAX_SPEED)
                sound_engine.set_volume(vol * 0.3)
                engine_channel.play(sound_engine)
            self.last_engine_play = current_time

    def draw(self):
        draw_track()
        self.player.draw()
        draw_hud(self.player)

        if self.phase == "menu":
            draw_menu()

        pygame.display.flip()

    def handle_key(self, key):
        if self.phase == "menu":
            if key == pygame.K_SPACE:
                self.reset()
                self.phase = "game"
        elif self.phase == "game":
            pass


def main():
    game = RacingGame()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.phase == "game":
                        game.phase = "menu"
                    else:
                        running = False
                elif event.key == pygame.K_r and game.phase == "game":
                    game.reset()
                else:
                    game.handle_key(event.key)

        game.update()
        game.draw()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
