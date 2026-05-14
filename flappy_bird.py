"""
星际跳跃者 - 太空冒险游戏
控制火箭在陨石带中跳跃穿越，收集燃料躲避障碍
"""

import pygame
import random
import math
import struct

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 69, 0)
BLUE = (0, 191, 255)
DARK_BLUE = (25, 25, 112)
GRAY = (128, 128, 128)
GREEN = (50, 205, 50)
PURPLE = (138, 43, 226)
CYAN = (0, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("星际跳跃者 - Space Jumper")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 32)
font_small = pygame.font.Font(None, 24)


def generate_wav_data(sample_rate, duration_seconds, frequency, wave_type='sine', volume=0.3):
    """使用bytearray生成WAV音频数据"""
    num_samples = int(sample_rate * duration_seconds)
    samples = bytearray()

    for i in range(num_samples):
        t = i / sample_rate
        sample = 0

        if wave_type == 'sine':
            sample = math.sin(2 * math.pi * frequency * t)
        elif wave_type == 'square':
            sample = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
        elif wave_type == 'sawtooth':
            sample = 2 * (frequency * t - math.floor(0.5 + frequency * t))
        elif wave_type == 'noise':
            sample = random.uniform(-1, 1)

        sample = int(sample * volume * 32767)
        packed = struct.pack('<h', max(-32768, min(32767, sample)))
        samples.extend(packed)

    return samples


def create_wav_header(data_size, sample_rate=22050, num_channels=1, bits_per_sample=16):
    """创建WAV文件头"""
    header = bytearray()
    header.extend(b'RIFF')
    header.extend(struct.pack('<I', 36 + data_size))
    header.extend(b'WAVE')
    header.extend(b'fmt ')
    header.extend(struct.pack('<I', 16))
    header.extend(struct.pack('<H', 1))
    header.extend(struct.pack('<H', num_channels))
    header.extend(struct.pack('<I', sample_rate))
    header.extend(struct.pack('<I', sample_rate * num_channels * bits_per_sample // 8))
    header.extend(struct.pack('<H', num_channels * bits_per_sample // 8))
    header.extend(struct.pack('<H', bits_per_sample))
    header.extend(b'data')
    header.extend(struct.pack('<I', data_size))
    return header


def generate_sound_effect(sound_type, sample_rate=22050):
    """生成各种游戏音效"""
    if sound_type == 'thrust':
        data = generate_wav_data(sample_rate, 0.15, 150, 'sawtooth', 0.2)
        noise = generate_wav_data(sample_rate, 0.15, 80, 'noise', 0.15)
        combined = bytearray()
        for i in range(len(data)):
            val = data[i] + noise[i] - 128
            combined.append(max(0, min(255, val + 128)))
        return bytes(combined)
    elif sound_type == 'collect_fuel':
        data1 = generate_wav_data(sample_rate, 0.1, 523, 'sine', 0.25)
        data2 = generate_wav_data(sample_rate, 0.15, 784, 'sine', 0.25)
        return bytes(data1 + data2)
    elif sound_type == 'collision':
        return generate_wav_data(sample_rate, 0.3, 100, 'sawtooth', 0.35)
    elif sound_type == 'score':
        return generate_wav_data(sample_rate, 0.08, 880, 'sine', 0.2)
    elif sound_type == 'gravity':
        return generate_wav_data(sample_rate, 0.2, 200, 'sine', 0.1)
    return b''


def create_sound_object(wav_data):
    """将WAV数据转换为pygame声音对象"""
    import io
    header = create_wav_header(len(wav_data))
    full_wav = bytes(header) + wav_data
    return pygame.mixer.Sound(buffer=full_wav)


class Rocket:
    """火箭类 - 玩家控制的飞船"""

    def __init__(self):
        self.x = 150
        self.y = HEIGHT // 2
        self.width = 40
        self.height = 50
        self.velocity_y = 0
        self.gravity = 0.25
        self.thrust_power = -0.6
        self.max_velocity = 12
        self.fuel = 100
        self.max_fuel = 100
        self.fuel_consumption = 0.4
        self.fuel_recovery = 0.08
        self.thrusting = False
        self.alive = True
        self.invincible_time = 0
        self.flame_size = 0

    def apply_thrust(self):
        """应用引擎推力"""
        if self.fuel > 0 and self.alive:
            self.velocity_y += self.thrust_power
            self.fuel -= self.fuel_consumption
            self.fuel = max(0, self.fuel)
            self.thrusting = True
            self.flame_size = random.uniform(15, 25)
            return True
        return False

    def apply_gravity(self, planets):
        """应用行星引力"""
        for planet in planets:
            dx = planet.x - self.x
            dy = planet.y - self.y
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < planet.gravity_range and distance > 0:
                force = planet.gravity_strength / (distance * 0.1)
                self.velocity_y += (dy / distance) * force

    def update(self, planets):
        """更新火箭状态"""
        if not self.alive:
            return

        self.apply_gravity(planets)

        if self.thrusting:
            self.velocity_y += self.gravity * 0.3
        else:
            self.velocity_y += self.gravity

        self.velocity_y = max(-self.max_velocity, min(self.max_velocity, self.velocity_y))
        self.y += self.velocity_y

        if self.y < 0:
            self.y = 0
            self.velocity_y = 0
        elif self.y > HEIGHT - self.height:
            self.y = HEIGHT - self.height
            self.velocity_y = 0

        self.thrusting = False
        self.flame_size *= 0.9

        if self.invincible_time > 0:
            self.invincible_time -= 1

    def draw(self):
        """绘制火箭"""
        if not self.alive:
            return

        if self.invincible_time > 0 and int(self.invincible_time / 5) % 2 == 0:
            return

        center_x = self.x
        center_y = self.y + self.height // 2

        if self.thrusting:
            flame_height = self.flame_size
            pygame.draw.polygon(screen, ORANGE, [
                (center_x - 10, center_y + 20),
                (center_x + 10, center_y + 20),
                (center_x, center_y + 20 + flame_height)
            ])
            pygame.draw.polygon(screen, YELLOW, [
                (center_x - 5, center_y + 20),
                (center_x + 5, center_y + 20),
                (center_x, center_y + 20 + flame_height * 0.6)
            ])

        pygame.draw.ellipse(screen, WHITE, (center_x - 15, center_y - 20, 30, 40))
        pygame.draw.ellipse(screen, RED, (center_x - 15, center_y - 15, 30, 30))

        nose_x, nose_y = center_x, center_y - 25
        pygame.draw.circle(screen, GRAY, (int(nose_x), int(nose_y)), 8)

        window_x = center_x
        window_y = center_y - 5
        pygame.draw.circle(screen, BLUE, (int(window_x), int(window_y)), 6)

        pygame.draw.rect(screen, RED, (center_x - 18, center_y + 10, 8, 15))
        pygame.draw.rect(screen, RED, (center_x + 10, center_y + 10, 8, 15))

    def get_rect(self):
        """获取火箭碰撞矩形"""
        return pygame.Rect(
            self.x - 15,
            self.y + 10,
            30,
            40
        )


class Meteor:
    """陨石类 - 需要躲避的障碍物"""

    def __init__(self, x=None):
        self.x = x if x else WIDTH + random.randint(50, 200)
        self.y = random.randint(50, HEIGHT - 50)
        self.radius = random.randint(20, 45)
        self.speed = random.uniform(2, 5)
        self.rotation = 0
        self.rotation_speed = random.uniform(-0.03, 0.03)
        self.vertices = []
        self.generate_shape()

    def generate_shape(self):
        """生成不规则陨石形状"""
        num_points = random.randint(7, 12)
        for i in range(num_points):
            angle = (2 * math.pi / num_points) * i
            distance = self.radius * random.uniform(0.7, 1.0)
            x = self.x + math.cos(angle) * distance
            y = self.y + math.sin(angle) * distance
            self.vertices.append((x, y))

    def update(self):
        """更新陨石位置"""
        self.x -= self.speed
        self.rotation += self.rotation_speed

        for i, vertex in enumerate(self.vertices):
            dx = vertex[0] - self.x
            dy = vertex[1] - self.y
            new_x = self.x + dx * math.cos(self.rotation_speed) - dy * math.sin(self.rotation_speed)
            new_y = self.y + dx * math.sin(self.rotation_speed) + dy * math.cos(self.rotation_speed)
            self.vertices[i] = (new_x, new_y)

    def draw(self):
        """绘制陨石"""
        if len(self.vertices) >= 3:
            pygame.draw.polygon(screen, GRAY, self.vertices)
            pygame.draw.polygon(screen, DARK_BLUE, self.vertices, 2)

            for i in range(3):
                crater_x = self.x + random.uniform(-self.radius * 0.4, self.radius * 0.4)
                crater_y = self.y + random.uniform(-self.radius * 0.4, self.radius * 0.4)
                pygame.draw.circle(screen, DARK_BLUE, (int(crater_x), int(crater_y)), random.randint(3, 8))

    def get_rect(self):
        """获取陨石碰撞矩形"""
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def is_off_screen(self):
        """检查是否移出屏幕"""
        return self.x < -self.radius * 2


class Fuel:
    """燃料补给类"""

    def __init__(self):
        self.x = WIDTH + random.randint(100, 300)
        self.y = random.randint(80, HEIGHT - 80)
        self.radius = 15
        self.speed = 3
        self.pulse = 0
        self.collected = False

    def update(self):
        """更新燃料位置"""
        self.x -= self.speed
        self.pulse += 0.1

    def draw(self):
        """绘制燃料罐"""
        if self.collected:
            return

        pulse_radius = self.radius + math.sin(self.pulse) * 3

        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), int(pulse_radius + 8), 2)
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), int(pulse_radius))

        pygame.draw.rect(screen, GREEN, (int(self.x) - 6, int(self.y) - 22, 12, 10))
        pygame.draw.rect(screen, GREEN, (int(self.x) - 8, int(self.y) - 15, 16, 20))

        font_fuel = pygame.font.Font(None, 18)
        fuel_text = font_fuel.render("F", True, WHITE)
        screen.blit(fuel_text, (int(self.x) - 4, int(self.y) - 8))

    def get_rect(self):
        """获取燃料碰撞矩形"""
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def is_off_screen(self):
        """检查是否移出屏幕"""
        return self.x < -50


class Planet:
    """行星类 - 产生引力场"""

    def __init__(self):
        self.x = WIDTH + random.randint(300, 600)
        self.y = random.randint(100, HEIGHT - 100)
        self.radius = random.randint(40, 70)
        self.gravity_range = self.radius * 4
        self.gravity_strength = random.uniform(0.1, 0.25)
        self.rotation = 0
        self.speed = 1.5

        colors = [PURPLE, BLUE, ORANGE, RED]
        self.color = random.choice(colors)
        self.has_ring = random.choice([True, False])

    def update(self):
        """更新行星位置"""
        self.x -= self.speed
        self.rotation += 0.005

    def draw(self):
        """绘制行星及其引力场"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.gravity_range), 1)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.gravity_range * 0.7), 1)

        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        highlight_x = int(self.x - self.radius * 0.3)
        highlight_y = int(self.y - self.radius * 0.3)
        pygame.draw.circle(screen, WHITE, (highlight_x, highlight_y), self.radius // 4)

        if self.has_ring:
            ellipse_rect = pygame.Rect(
                int(self.x - self.radius * 1.5),
                int(self.y - self.radius * 0.3),
                int(self.radius * 3),
                int(self.radius * 0.6)
            )
            pygame.draw.ellipse(screen, GRAY, ellipse_rect, 2)

    def is_off_screen(self):
        """检查是否移出屏幕"""
        return self.x < -self.gravity_range


class Star:
    """背景星星"""

    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(0.5, 2)
        self.brightness = random.randint(100, 255)
        self.twinkle_speed = random.uniform(0.02, 0.08)
        self.twinkle_phase = random.uniform(0, 2 * math.pi)

    def draw(self):
        """绘制星星"""
        self.twinkle_phase += self.twinkle_speed
        current_brightness = int(self.brightness * (0.5 + 0.5 * math.sin(self.twinkle_phase)))
        color = (current_brightness, current_brightness, min(255, current_brightness + 50))
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.size))


class Game:
    """游戏主类"""

    def __init__(self):
        self.rocket = Rocket()
        self.meteors = []
        self.fuels = []
        self.planets = []
        self.stars = [Star() for _ in range(100)]
        self.score = 0
        self.distance = 0
        self.game_over = False
        self.game_started = False
        self.frame_count = 0
        self.sounds = {}

        self.load_sounds()

    def load_sounds(self):
        """加载游戏音效"""
        try:
            self.sounds['thrust'] = create_sound_object(generate_sound_effect('thrust'))
            self.sounds['collect_fuel'] = create_sound_object(generate_sound_effect('collect_fuel'))
            self.sounds['collision'] = create_sound_object(generate_sound_effect('collision'))
            self.sounds['score'] = create_sound_object(generate_sound_effect('score'))
            self.sounds['gravity'] = create_sound_object(generate_sound_effect('gravity'))
        except Exception:
            pass

    def play_sound(self, sound_name):
        """播放音效"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except Exception:
                pass

    def spawn_objects(self):
        """生成游戏物体"""
        if self.frame_count % 60 == 0:
            if random.random() < 0.4:
                self.meteors.append(Meteor())

        if self.frame_count % 90 == 0:
            if random.random() < 0.5:
                self.fuels.append(Fuel())

        if self.frame_count % 180 == 0:
            if random.random() < 0.3 and len(self.planets) < 2:
                self.planets.append(Planet())

    def check_collisions(self):
        """检测碰撞"""
        rocket_rect = self.rocket.get_rect()

        for meteor in self.meteors:
            if self.rocket.invincible_time <= 0:
                meteor_rect = meteor.get_rect()
                if rocket_rect.colliderect(meteor_rect):
                    if math.sqrt((self.rocket.x - meteor.x) ** 2 +
                                 (self.rocket.y + 30 - meteor.y) ** 2) < self.rocket.width // 2 + meteor.radius * 0.7:
                        self.rocket.alive = False
                        self.play_sound('collision')
                        return True

        for fuel in self.fuels:
            if not fuel.collected:
                fuel_rect = fuel.get_rect()
                if rocket_rect.colliderect(fuel_rect):
                    if math.sqrt((self.rocket.x - fuel.x) ** 2 +
                                 (self.rocket.y + 30 - fuel.y) ** 2) < self.rocket.width // 2 + fuel.radius:
                        fuel.collected = True
                        self.rocket.fuel = min(self.rocket.max_fuel, self.rocket.fuel + 30)
                        self.score += 5
                        self.play_sound('collect_fuel')

        return False

    def update_score(self):
        """更新分数"""
        for meteor in self.meteors:
            if hasattr(meteor, 'scored'):
                continue
            if meteor.x + meteor.radius < self.rocket.x - 20:
                meteor.scored = True
                self.score += 10
                self.play_sound('score')

    def draw_hud(self):
        """绘制游戏界面HUD"""
        score_text = font_medium.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 20))

        fuel_bar_width = 150
        fuel_bar_height = 20
        fuel_x, fuel_y = 20, 55

        pygame.draw.rect(screen, GRAY, (fuel_x, fuel_y, fuel_bar_width, fuel_bar_height), 2)
        fuel_fill_width = int((self.rocket.fuel / self.rocket.max_fuel) * (fuel_bar_width - 4))
        fuel_color = GREEN if self.rocket.fuel > 30 else RED
        pygame.draw.rect(screen, fuel_color, (fuel_x + 2, fuel_y + 2, fuel_fill_width, fuel_bar_height - 4))

        fuel_text = font_small.render(f"燃料: {int(self.rocket.fuel)}%", True, WHITE)
        screen.blit(fuel_text, (fuel_x + fuel_bar_width + 10, fuel_y))

        controls_text = font_small.render("SPACE: 引擎喷射 | 躲避陨石 | 收集燃料", True, GRAY)
        screen.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, HEIGHT - 30))

    def draw_background(self):
        """绘制太空背景"""
        screen.fill(BLACK)

        for star in self.stars:
            star.draw()

        nebula_x = (self.frame_count * 0.2) % (WIDTH + 200) - 100
        for i in range(3):
            x = (nebula_x + i * 300) % (WIDTH + 200) - 100
            pygame.draw.circle(screen, (50, 0, 80), (int(x), 150 + i * 100), 80, 1)

    def draw_start_screen(self):
        """绘制开始界面"""
        self.draw_background()

        title = font_large.render("星际跳跃者", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

        subtitle = font_medium.render("SPACE JUMPER", True, CYAN)
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 200))

        instructions = [
            "操作说明:",
            "按住 SPACE 键 - 喷射引擎向上",
            "松开 - 火箭下落",
            "",
            "目标:",
            "- 躲避陨石障碍",
            "- 收集绿色燃料补给",
            "- 利用行星引力省燃料",
            "- 穿越陨石 +10分",
            "- 收集燃料 +5分",
            "",
            "按 SPACE 开始游戏"
        ]

        for i, line in enumerate(instructions):
            text = font_small.render(line, True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 280 + i * 28))

    def draw_game_over_screen(self):
        """绘制游戏结束界面"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        game_over_text = font_large.render("游戏结束!", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 180))

        score_text = font_medium.render(f"最终得分: {self.score}", True, YELLOW)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 260))

        restart_text = font_small.render("按 SPACE 重新开始", True, WHITE)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 340))

    def update(self):
        """更新游戏逻辑"""
        if self.game_over:
            return

        self.frame_count += 1
        self.distance += 2

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if self.rocket.apply_thrust():
                if self.frame_count % 3 == 0:
                    self.play_sound('thrust')

        self.rocket.update(self.planets)
        self.spawn_objects()

        for meteor in self.meteors:
            meteor.update()
        self.meteors = [m for m in self.meteors if not m.is_off_screen()]

        for fuel in self.fuels:
            fuel.update()
        self.fuels = [f for f in self.fuels if not f.is_off_screen() and not f.collected]

        for planet in self.planets:
            planet.update()
            if self.frame_count % 30 == 0:
                self.play_sound('gravity')
        self.planets = [p for p in self.planets if not p.is_off_screen()]

        if self.check_collisions():
            self.game_over = True

        self.update_score()

    def draw(self):
        """绘制游戏画面"""
        self.draw_background()

        for planet in self.planets:
            planet.draw()

        for meteor in self.meteors:
            meteor.draw()

        for fuel in self.fuels:
            fuel.draw()

        self.rocket.draw()
        self.draw_hud()

        if self.game_over:
            self.draw_game_over_screen()

    def run(self):
        """游戏主循环"""
        running = True
        playing_thrust = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        if not self.game_started:
                            self.game_started = True
                        elif self.game_over:
                            self.__init__()

            if not self.game_started:
                self.draw_start_screen()
            else:
                self.update()
                self.draw()

            pygame.display.update()
            clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
