import pygame
import random
import math
import struct

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

COLORS = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'gray': (64, 64, 64),
    'red': (255, 60, 60),
    'blue': (60, 120, 255),
    'yellow': (255, 220, 60),
    'green': (60, 220, 100),
    'cyan': (60, 220, 220),
    'purple': (180, 60, 255),
    'orange': (255, 150, 50),
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("碰碰车乱斗")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
font_large = pygame.font.Font(None, 56)
font_small = pygame.font.Font(None, 22)

def generate_sound(sound_type, duration_ms=200, sample_rate=22050):
    num_samples = int(sample_rate * duration_ms / 1000)
    audio_data = bytearray()
    
    if sound_type == 'collision':
        freq = 150
        for i in range(num_samples):
            t = i / sample_rate
            wave = math.sin(2 * math.pi * freq * t * (1 + 3 * math.exp(-t * 25)))
            envelope = math.exp(-t * 15)
            sample = int(16000 * wave * envelope)
            audio_data.extend(struct.pack('<h', max(-32768, min(32767, sample))))
    
    elif sound_type == 'energy_charge':
        freq = 400
        for i in range(num_samples):
            t = i / sample_rate
            wave = math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(4 * math.pi * freq * t)
            envelope = 0.3 + 0.7 * (i / num_samples)
            sample = int(12000 * wave * envelope)
            audio_data.extend(struct.pack('<h', max(-32768, min(32767, sample))))
    
    elif sound_type == 'lightning':
        for i in range(num_samples):
            t = i / sample_rate
            noise = random.uniform(-1, 1)
            freq_sweep = 800 * math.exp(-t * 8) + 200
            wave = math.sin(2 * math.pi * freq_sweep * t) + 0.5 * noise
            envelope = math.exp(-t * 10)
            sample = int(20000 * wave * envelope)
            audio_data.extend(struct.pack('<h', max(-32768, min(32767, sample))))
    
    elif sound_type == 'powerup':
        freq_start, freq_end = 300, 900
        for i in range(num_samples):
            t = i / sample_rate
            progress = i / num_samples
            freq = freq_start + (freq_end - freq_start) * progress
            wave = math.sin(2 * math.pi * freq * t)
            envelope = math.sin(math.pi * progress)
            sample = int(14000 * wave * envelope)
            audio_data.extend(struct.pack('<h', max(-32768, min(32767, sample))))
    
    elif sound_type == 'shield':
        freq = 600
        for i in range(num_samples):
            t = i / sample_rate
            wave = math.sin(2 * math.pi * freq * t) * math.sin(8 * math.pi * freq * t)
            envelope = math.exp(-t * 8)
            sample = int(10000 * wave * envelope)
            audio_data.extend(struct.pack('<h', max(-32768, min(32767, sample))))
    
    elif sound_type == 'game_over':
        freq = 440
        for i in range(num_samples):
            t = i / sample_rate
            if i < num_samples // 3:
                wave = math.sin(2 * math.pi * freq * t)
            elif i < 2 * num_samples // 3:
                wave = math.sin(2 * math.pi * (freq * 0.75) * t)
            else:
                wave = math.sin(2 * math.pi * (freq * 0.5) * t)
            envelope = math.exp(-t * 3)
            sample = int(16000 * wave * envelope)
            audio_data.extend(struct.pack('<h', max(-32768, min(32767, sample))))
    
    elif sound_type == 'victory':
        notes = [523, 659, 784, 1047]
        note_duration = num_samples // len(notes)
        for i in range(num_samples):
            t = i % note_duration
            note_idx = i // note_duration
            freq = notes[min(note_idx, len(notes) - 1)]
            wave = math.sin(2 * math.pi * freq * t / sample_rate)
            envelope = 1.0 if t < note_duration * 0.7 else (note_duration - t) / (note_duration * 0.3)
            sample = int(14000 * wave * envelope)
            audio_data.extend(struct.pack('<h', max(-32768, min(32767, sample))))
    
    elif sound_type == 'countdown':
        freq = 880
        for i in range(num_samples):
            t = i / sample_rate
            wave = math.sin(2 * math.pi * freq * t)
            envelope = math.sin(math.pi * t / (duration_ms / 1000))
            sample = int(12000 * wave * envelope)
            audio_data.extend(struct.pack('<h', max(-32768, min(32767, sample))))
    
    return bytes(audio_data)

class SoundManager:
    def __init__(self):
        self.sounds = {}
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.enabled = True
        except:
            self.enabled = False
        self._generate_sounds()
    
    def _generate_sounds(self):
        if not self.enabled:
            return
        self.sounds['collision'] = generate_sound('collision', 150)
        self.sounds['energy_charge'] = generate_sound('energy_charge', 300)
        self.sounds['lightning'] = generate_sound('lightning', 400)
        self.sounds['powerup'] = generate_sound('powerup', 350)
        self.sounds['shield'] = generate_sound('shield', 250)
        self.sounds['game_over'] = generate_sound('game_over', 800)
        self.sounds['victory'] = generate_sound('victory', 700)
        self.sounds['countdown'] = generate_sound('countdown', 200)
    
    def play(self, sound_name):
        if not self.enabled or sound_name not in self.sounds:
            return
        try:
            sound = pygame.mixer.Sound(self.sounds[sound_name])
            sound.set_volume(0.5)
            sound.play()
        except:
            pass

class Player:
    def __init__(self, x, y, color, name, controls):
        self.x = x
        self.y = y
        self.radius = 28
        self.color = color
        self.name = name
        self.controls = controls
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 4.5
        self.health = 100
        self.max_health = 100
        self.energy = 0
        self.max_energy = 100
        self.has_shield = False
        self.shield_timer = 0
        self.boost_timer = 0
        self.invincible_timer = 0
        self.knockback_x = 0.0
        self.knockback_y = 0.0
        self.angle = 0.0
        self.lightning_effects = []
    
    def handle_input(self, keys):
        ax, ay = 0, 0
        speed = self.speed * (1.4 if self.boost_timer > 0 else 1.0)
        
        if keys[self.controls['up']]:
            ay = -speed
        if keys[self.controls['down']]:
            ay = speed
        if keys[self.controls['left']]:
            ax = -speed
        if keys[self.controls['right']]:
            ax = speed
        
        friction = 0.88
        self.vx = self.vx * friction + ax * 0.35
        self.vy = self.vy * friction + ay * 0.35
        
        if ax != 0 or ay != 0:
            self.angle = math.atan2(ay, ax)
        
        if keys[self.controls['skill']] and self.energy >= self.max_energy:
            return True
        return False
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        margin = 40
        self.x = max(margin, min(WIDTH - margin, self.x))
        self.y = max(margin + 60, min(HEIGHT - margin - 30, self.y))
        
        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.has_shield = False
        
        if self.boost_timer > 0:
            self.boost_timer -= 1
        
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        
        self.lightning_effects = [e for e in self.lightning_effects if e['life'] > 0]
        for e in self.lightning_effects:
            e['life'] -= 1
    
    def draw(self, surface):
        flicker = (pygame.time.get_ticks() // 80) % 2 == 0
        
        if self.invincible_timer > 0 and flicker:
            return
        
        if self.has_shield:
            shield_color = (100, 200, 255, 100)
            for r in range(3):
                offset = r * 5
                pygame.draw.circle(surface, (60, 180, 255), (int(self.x), int(self.y)), self.radius + 10 + offset, 2)
        
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        
        highlight_pos = (int(self.x - self.radius * 0.3), int(self.y - self.radius * 0.3))
        pygame.draw.circle(surface, (255, 255, 255), highlight_pos, 8)
        
        eye_offset = 12
        eye_radius = 5
        ex1 = int(self.x + math.cos(self.angle) * eye_offset + math.cos(self.angle + 1.57) * 6)
        ey1 = int(self.y + math.sin(self.angle) * eye_offset + math.sin(self.angle + 1.57) * 6)
        ex2 = int(self.x + math.cos(self.angle) * eye_offset - math.cos(self.angle + 1.57) * 6)
        ey2 = int(self.y + math.sin(self.angle) * eye_offset - math.sin(self.angle + 1.57) * 6)
        pygame.draw.circle(surface, COLORS['black'], (ex1, ey1), eye_radius)
        pygame.draw.circle(surface, COLORS['black'], (ex2, ey2), eye_radius)
        pygame.draw.circle(surface, COLORS['white'], (ex1 + 1, ey1 - 1), 2)
        pygame.draw.circle(surface, COLORS['white'], (ex2 + 1, ey2 - 1), 2)
        
        if self.boost_timer > 0:
            for i in range(3):
                bx = int(self.x - math.cos(self.angle) * (self.radius + 5 + i * 8))
                by = int(self.y - math.sin(self.angle) * (self.radius + 5 + i * 8))
                alpha = 255 - i * 70
                pygame.draw.circle(surface, (255, 150, 50), (bx, by), 6 - i, 0)
        
        for effect in self.lightning_effects:
            alpha = int(255 * effect['life'] / effect['max_life'])
            points = effect['points']
            if len(points) >= 2:
                pygame.draw.lines(surface, (200, 220, 255), False, points, 2)
    
    def take_damage(self, amount, from_x, from_y):
        if self.invincible_timer > 0:
            return False
        
        if self.has_shield:
            self.shield_timer = max(self.shield_timer - 20, 0)
            if self.shield_timer <= 0:
                self.has_shield = False
            return False
        
        self.health = max(0, self.health - amount)
        self.invincible_timer = 30
        return True
    
    def apply_knockback(self, from_x, from_y, force=12.0):
        dx = self.x - from_x
        dy = self.y - from_y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            self.vx += (dx / dist) * force
            self.vy += (dy / dist) * force
            self.invincible_timer = max(self.invincible_timer, 15)
    
    def fire_lightning(self, target):
        self.energy = 0
        self.invincible_timer = 20
        points = []
        x, y = self.x, self.y
        while abs(x - target.x) > 10 or abs(y - target.y) > 10:
            points.append((int(x), int(y)))
            x += (target.x - x) * 0.15 + random.uniform(-20, 20)
            y += (target.y - y) * 0.15 + random.uniform(-20, 20)
        points.append((int(target.x), int(target.y)))
        
        self.lightning_effects.append({'points': points, 'life': 20, 'max_life': 20})
        target.lightning_effects.append({'points': points, 'life': 20, 'max_life': 20})
        
        target.take_damage(25, self.x, self.y)
        target.apply_knockback(self.x, self.y, 18.0)
        
        return True


class PowerUp:
    TYPES = ['shield', 'speed', 'repair']
    
    def __init__(self, x, y, ptype=None):
        self.x = x
        self.y = y
        self.ptype = ptype if ptype else random.choice(self.TYPES)
        self.radius = 15
        self.lifetime = 600
        self.age = 0
        self.bob_offset = random.uniform(0, math.pi * 2)
        
        if self.ptype == 'shield':
            self.color = COLORS['cyan']
            self.symbol = '护'
        elif self.ptype == 'speed':
            self.color = COLORS['orange']
            self.symbol = '速'
        else:
            self.color = COLORS['green']
            self.symbol = '回'
    
    def update(self):
        self.age += 1
        return self.age < self.lifetime
    
    def draw(self, surface):
        bob = math.sin(self.age * 0.08 + self.bob_offset) * 4
        y_pos = self.y + bob
        
        pulse = 1.0 + 0.15 * math.sin(self.age * 0.15)
        r = int(self.radius * pulse)
        
        glow_alpha = 80 + 40 * math.sin(self.age * 0.1)
        for i in range(3):
            glow_r = r + (3 - i) * 5
            alpha_surf = pygame.Surface((glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surf, (*self.color, glow_alpha // (i + 1)), (glow_r + 2, glow_r + 2), glow_r)
            surface.blit(alpha_surf, (int(self.x - glow_r - 2), int(y_pos - glow_r - 2)))
        
        pygame.draw.circle(surface, self.color, (int(self.x), int(y_pos)), r)
        pygame.draw.circle(surface, COLORS['white'], (int(self.x), int(y_pos)), r, 2)
        
        text_surf = font_small.render(self.symbol, True, COLORS['white'])
        text_rect = text_surf.get_rect(center=(int(self.x), int(y_pos) + 1))
        surface.blit(text_surf, text_rect)
    
    def apply(self, player):
        if self.ptype == 'shield':
            player.has_shield = True
            player.shield_timer = 360
            return 'shield'
        elif self.ptype == 'speed':
            player.boost_timer = 180
            return 'speed'
        else:
            player.health = min(player.max_health, player.health + 30)
            return 'repair'
    
    def check_collision(self, player):
        dx = self.x - player.x
        dy = self.y - player.y
        dist = math.sqrt(dx * dx + dy * dy)
        return dist < self.radius + player.radius


class LightningEffect:
    def __init__(self, x1, y1, x2, y2):
        self.points = self._generate_bolt(x1, y1, x2, y2)
        self.life = 15
        self.max_life = 15
    
    def _generate_bolt(self, x1, y1, x2, y2):
        points = [(x1, y1)]
        steps = max(8, int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / 15))
        
        for i in range(1, steps):
            t = i / steps
            x = x1 + (x2 - x1) * t + random.uniform(-15, 15)
            y = y1 + (y2 - y1) * t + random.uniform(-15, 15)
            points.append((x, y))
        
        points.append((x2, y2))
        return points
    
    def draw(self, surface):
        alpha = int(255 * self.life / self.max_life)
        if alpha <= 0:
            return
        
        alpha_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        for i in range(len(self.points) - 1):
            t = i / len(self.points)
            color = (100 + int(155 * (1 - t)), 150 + int(105 * t), 255)
            pygame.draw.line(alpha_surf, (*color, alpha), self.points[i], self.points[i + 1], 3)
        
        pygame.draw.line(alpha_surf, (255, 255, 255, alpha), self.points[0], self.points[-1], 1)
        
        for pt in self.points[1:-1]:
            pygame.draw.circle(alpha_surf, (*color, alpha), pt, 3)
        
        surface.blit(alpha_surf, (0, 0))
    
    def update(self):
        self.life -= 1
        return self.life > 0


class GameArena:
    def __init__(self):
        self.background_color = (20, 30, 50)
        self.arena_rect = pygame.Rect(30, 80, WIDTH - 60, HEIGHT - 110)
        self.particles = []
        self.arena_border_glow = 0
    
    def draw(self, surface):
        surface.fill(self.background_color)
        
        for y in range(80, HEIGHT - 30, 40):
            offset = (pygame.time.get_ticks() // 30) % 40
            alpha = 40 if (y // 40) % 2 == 0 else 30
            line_surf = pygame.Surface((WIDTH - 80, 2), pygame.SRCALPHA)
            line_surf.fill((60, 80, 120, alpha))
            surface.blit(line_surf, (40, y + offset))
        
        border_color = (60, 80, 160)
        pygame.draw.rect(surface, border_color, self.arena_rect, 3)
        
        inner_color = (25, 35, 55)
        pygame.draw.rect(surface, inner_color, self.arena_rect.inflate(-6, -6))
        
        corner_size = 15
        corners = [
            (self.arena_rect.left, self.arena_rect.top),
            (self.arena_rect.right - corner_size, self.arena_rect.top),
            (self.arena_rect.left, self.arena_rect.bottom - corner_size),
            (self.arena_rect.right - corner_size, self.arena_rect.bottom - corner_size),
        ]
        for cx, cy in corners:
            pygame.draw.rect(surface, (80, 120, 200), (cx, cy, corner_size, corner_size), 2)
        
        pygame.draw.rect(surface, (20, 30, 50), (35, 85, WIDTH - 70, HEIGHT - 120))
        
        self.particles = [p for p in self.particles if p['life'] > 0]
        for p in self.particles:
            alpha = int(255 * p['life'] / p['max_life'])
            color = (*p['color'], alpha)
            pos = (int(p['x']), int(p['y']))
            pygame.draw.circle(surface, color, pos, p['size'])
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
    
    def spawn_particles(self, x, y, color, count=8, speed=3):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(1, speed)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * spd,
                'vy': math.sin(angle) * spd,
                'color': color,
                'size': random.randint(2, 5),
                'life': random.randint(15, 30),
                'max_life': 30,
            })
    
    def is_in_arena(self, x, y, radius):
        return (self.arena_rect.left + radius < x < self.arena_rect.right - radius and
                self.arena_rect.top + radius < y < self.arena_rect.bottom - radius)


def draw_hud(surface, player1, player2, powerups):
    hud_bg = pygame.Surface((WIDTH, 55), pygame.SRCALPHA)
    hud_bg.fill((0, 0, 0, 180))
    surface.blit(hud_bg, (0, 0))
    
    pygame.draw.line(surface, (60, 80, 120), (0, 55), (WIDTH, 55), 1)
    
    p1_bar_x, p1_bar_y = 100, 15
    p1_health_ratio = player1.health / player1.max_health
    p1_energy_ratio = player1.energy / player1.max_energy
    
    pygame.draw.rect(surface, (40, 40, 60), (p1_bar_x, p1_bar_y, 200, 12))
    health_color = (220, 60, 60) if p1_health_ratio < 0.3 else (60, 220, 100)
    pygame.draw.rect(surface, health_color, (p1_bar_x, p1_bar_y, int(200 * p1_health_ratio), 12))
    pygame.draw.rect(surface, COLORS['white'], (p1_bar_x, p1_bar_y, 200, 12), 1)
    
    pygame.draw.rect(surface, (40, 40, 60), (p1_bar_x, p1_bar_y + 15, 200, 8))
    energy_color = (255, 200, 50) if player1.energy >= player1.max_energy else (50, 150, 255)
    pygame.draw.rect(surface, energy_color, (p1_bar_x, p1_bar_y + 15, int(200 * p1_energy_ratio), 8))
    pygame.draw.rect(surface, COLORS['white'], (p1_bar_x, p1_bar_y + 15, 200, 8), 1)
    
    name_surf = font.render("玩家1 [WASD]", True, player1.color)
    surface.blit(name_surf, (10, p1_bar_y))
    
    shield_indicator = "甲" if player1.has_shield else ""
    boost_indicator = "火" if player1.boost_timer > 0 else ""
    indicators1 = shield_indicator + boost_indicator
    if indicators1:
        ind_surf = font_small.render(indicators1, True, COLORS['yellow'])
        surface.blit(ind_surf, (p1_bar_x + 205, p1_bar_y + 3))
    
    ready_text = ""
    if player1.energy >= player1.max_energy:
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
        color = (255, 100 + int(155 * pulse), 50)
        ready_text = " [闪电就绪! Q]"
    if ready_text:
        ready_surf = font_small.render(ready_text, True, (255, 200, 50))
        surface.blit(ready_surf, (p1_bar_x, p1_bar_y + 26))
    
    p2_bar_x = WIDTH - 300
    p2_health_ratio = player2.health / player2.max_health
    p2_energy_ratio = player2.energy / player2.max_energy
    
    pygame.draw.rect(surface, (40, 40, 60), (p2_bar_x, p1_bar_y, 200, 12))
    health_color = (220, 60, 60) if p2_health_ratio < 0.3 else (60, 220, 100)
    pygame.draw.rect(surface, health_color, (p2_bar_x + 200 * (1 - p2_health_ratio), p1_bar_y, int(200 * p2_health_ratio), 12))
    pygame.draw.rect(surface, COLORS['white'], (p2_bar_x, p1_bar_y, 200, 12), 1)
    
    pygame.draw.rect(surface, (40, 40, 60), (p2_bar_x, p1_bar_y + 15, 200, 8))
    energy_color = (255, 200, 50) if player2.energy >= player2.max_energy else (50, 150, 255)
    pygame.draw.rect(surface, energy_color, (p2_bar_x + 200 * (1 - p2_energy_ratio), p1_bar_y + 15, int(200 * p2_energy_ratio), 8))
    pygame.draw.rect(surface, COLORS['white'], (p2_bar_x, p1_bar_y + 15, 200, 8), 1)
    
    name_surf = font.render("玩家2 [方向键]", True, player2.color)
    surface.blit(name_surf, (WIDTH - name_surf.get_width() - 10, p1_bar_y))
    
    shield_indicator = "甲" if player2.has_shield else ""
    boost_indicator = "火" if player2.boost_timer > 0 else ""
    indicators2 = shield_indicator + boost_indicator
    if indicators2:
        ind_surf = font_small.render(indicators2, True, COLORS['yellow'])
        surface.blit(ind_surf, (p2_bar_x - 25, p1_bar_y + 3))
    
    ready_text = ""
    if player2.energy >= player2.max_energy:
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
        color = (255, 100 + int(155 * pulse), 50)
        ready_text = "[闪电就绪! /]"
    if ready_text:
        ready_surf = font_small.render(ready_text, True, (255, 200, 50))
        surface.blit(ready_surf, (p2_bar_x + 200 - ready_surf.get_width(), p1_bar_y + 26))
    
    center_text = font_small.render("碰碰车乱斗", True, (100, 120, 180))
    surface.blit(center_text, (WIDTH // 2 - center_text.get_width() // 2, 5))
    
    tip_text = font_small.render("撞! 充能! Q/——释放闪电!", True, (80, 80, 100))
    surface.blit(tip_text, (WIDTH // 2 - tip_text.get_width() // 2, 35))
    
    if len(powerups) > 0:
        count_surf = font_small.render(f"道具: {len(powerups)}", True, (150, 130, 80))
        surface.blit(count_surf, (WIDTH // 2 - count_surf.get_width() // 2, p1_bar_y))


def show_start_screen():
    sounds = SoundManager()
    
    title_font = pygame.font.Font(None, 72)
    subtitle_font = pygame.font.Font(None, 36)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return sounds
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return None
        
        screen.fill((10, 15, 30))
        
        for i in range(20):
            x = (pygame.time.get_ticks() * 0.3 + i * 100) % (WIDTH + 200) - 100
            y = 100 + math.sin(i * 0.5 + pygame.time.get_ticks() * 0.002) * 30
            size = 5 + math.sin(i * 0.3) * 3
            alpha = 60 + int(40 * math.sin(i * 0.2))
            glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (100, 150, 255, alpha), (size * 2, size * 2), size)
            screen.blit(glow_surf, (int(x - size * 2), int(y - size * 2)))
        
        title = title_font.render("碰碰车乱斗", True, (100, 180, 255))
        title_rect = title.get_rect(center=(WIDTH // 2, 180))
        screen.blit(title, title_rect)
        
        glow_surf = pygame.Surface((title.get_width() + 20, title.get_height() + 20), pygame.SRCALPHA)
        glow_title = title_font.render("碰碰车乱斗", True, (60, 120, 200))
        glow_surf.blit(glow_title, (10, 10))
        for _ in range(3):
            glow_surf.blit(glow_title, (10, 10))
        screen.blit(glow_surf, (title_rect.x - 10, title_rect.y - 10))
        
        subtitle1 = subtitle_font.render("双人碰碰车对战", True, (200, 200, 200))
        screen.blit(subtitle1, (WIDTH // 2 - subtitle1.get_width() // 2, 240))
        
        instructions = [
            ("玩家1", "WASD 移动 | Q 闪电攻击", COLORS['green']),
            ("玩家2", "方向键 移动 | / 闪电攻击", COLORS['blue']),
        ]
        
        y_pos = 320
        for title_text, desc, color in instructions:
            pygame.draw.rect(screen, (30, 40, 60), (WIDTH // 2 - 220, y_pos - 5, 440, 35), border_radius=8)
            t1 = font.render(title_text, True, color)
            t2 = font_small.render(desc, True, (160, 160, 180))
            screen.blit(t1, (WIDTH // 2 - 210, y_pos))
            screen.blit(t2, (WIDTH // 2 + 50, y_pos + 4))
            y_pos += 45
        
        rules = [
            "碰撞造成伤害并充能",
            "能量满后按Q或/释放闪电攻击",
            "拾取道具: 护盾、加速、回血",
        ]
        
        y_pos = 450
        for rule in rules:
            r_surf = font_small.render(rule, True, (120, 120, 140))
            screen.blit(r_surf, (WIDTH // 2 - r_surf.get_width() // 2, y_pos))
            y_pos += 25
        
        pulse = 0.7 + 0.3 * math.sin(pygame.time.get_ticks() * 0.005)
        start_text = font.render(f"[ 按空格键开始 ]", True, (150 + int(105 * pulse), 150 + int(105 * pulse), 200))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 530))
        
        pygame.display.update()
        clock.tick(60)


def show_game_over_screen(winner, sounds):
    screen.fill((10, 15, 30))
    
    for i in range(30):
        x = (pygame.time.get_ticks() * 0.5 + i * 80) % (WIDTH + 160) - 80
        y = 50 + math.sin(i * 0.7 + pygame.time.get_ticks() * 0.003) * 20
        size = 3 + math.sin(i * 0.4) * 2
        alpha = 40 + int(30 * math.sin(i * 0.3))
        glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (200, 200, 255, alpha), (size * 2, size * 2), size)
        screen.blit(glow_surf, (int(x - size * 2), int(y - size * 2)))
    
    if sounds:
        sounds.play('game_over')
    
    pygame.time.wait(500)
    
    title = font_large.render("游戏结束", True, (255, 100, 100))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
    
    if winner:
        winner_text = font.render(f"胜者: {winner}", True, (255, 220, 60))
        screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, 240))
        
        if sounds:
            sounds.play('victory')
    else:
        tie_text = font.render("平局!", True, (200, 200, 200))
        screen.blit(tie_text, (WIDTH // 2 - tie_text.get_width() // 2, 240))
    
    prompt_text = font.render("按空格键重新开始  ESC退出", True, (120, 120, 150))
    screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, 350))
    
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    return False
        clock.tick(30)


def main():
    sounds = show_start_screen()
    if sounds is None:
        return
    
    player1 = Player(200, HEIGHT // 2, COLORS['green'], "玩家1",
                   {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d, 'skill': pygame.K_q})
    
    player2 = Player(WIDTH - 200, HEIGHT // 2, COLORS['blue'], "玩家2",
                   {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'skill': pygame.K_KP_DIVIDE})
    
    arena = GameArena()
    powerups = []
    lightning_effects = []
    
    powerup_spawn_timer = 0
    game_time = 0
    last_collision_time = 0
    
    running = True
    while running:
        game_time += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
        
        keys = pygame.key.get_pressed()
        
        p1_fires = player1.handle_input(keys)
        p2_fires = player2.handle_input(keys)
        
        if p1_fires:
            sounds.play('lightning')
            lightning_effects.append(LightningEffect(player1.x, player1.y, player2.x, player2.y))
            player1.fire_lightning(player2)
            arena.spawn_particles(player2.x, player2.y, (150, 180, 255), 15, 5)
        
        if p2_fires:
            sounds.play('lightning')
            lightning_effects.append(LightningEffect(player2.x, player2.y, player1.x, player1.y))
            player2.fire_lightning(player1)
            arena.spawn_particles(player1.x, player1.y, (150, 180, 255), 15, 5)
        
        player1.update()
        player2.update()
        
        dx = player2.x - player1.x
        dy = player2.y - player1.y
        dist = math.sqrt(dx * dx + dy * dy)
        min_dist = player1.radius + player2.radius
        
        if dist < min_dist and dist > 0:
            if game_time - last_collision_time > 15:
                last_collision_time = game_time
                
                overlap = min_dist - dist
                nx, ny = dx / dist, dy / dist
                
                player1.x -= nx * overlap * 0.5
                player1.y -= ny * overlap * 0.5
                player2.x += nx * overlap * 0.5
                player2.y += ny * overlap * 0.5
                
                rel_vx = player1.vx - player2.vx
                rel_vy = player1.vy - player2.vy
                rel_dot = rel_vx * nx + rel_vy * ny
                
                if rel_dot > 0:
                    player1.vx -= nx * rel_dot * 0.8
                    player1.vy -= ny * rel_dot * 0.8
                    player2.vx += nx * rel_dot * 0.8
                    player2.vy += ny * rel_dot * 0.8
                
                damage = 8
                
                if player1.take_damage(damage, player2.x, player2.y):
                    player1.apply_knockback(player2.x, player2.y, 8)
                    arena.spawn_particles(player1.x, player1.y, COLORS['red'], 6)
                
                if player2.take_damage(damage, player1.x, player1.y):
                    player2.apply_knockback(player1.x, player1.y, 8)
                    arena.spawn_particles(player2.x, player2.y, COLORS['red'], 6)
                
                energy_gain = 15
                player1.energy = min(player1.max_energy, player1.energy + energy_gain)
                player2.energy = min(player2.max_energy, player2.energy + energy_gain)
                
                if player1.energy >= player1.max_energy:
                    sounds.play('energy_charge')
                if player2.energy >= player2.max_energy:
                    sounds.play('energy_charge')
                
                sounds.play('collision')
        
        powerup_spawn_timer += 1
        if powerup_spawn_timer >= 300 and len(powerups) < 3:
            powerup_spawn_timer = 0
            px = random.randint(100, WIDTH - 100)
            py = random.randint(150, HEIGHT - 100)
            powerups.append(PowerUp(px, py))
        
        powerups = [p for p in powerups if p.update()]
        
        for powerup in powerups[:]:
            if powerup.check_collision(player1):
                result = powerup.apply(player1)
                if result == 'shield':
                    sounds.play('shield')
                else:
                    sounds.play('powerup')
                arena.spawn_particles(player1.x, player1.y, powerup.color, 10, 4)
                powerups.remove(powerup)
            elif powerup.check_collision(player2):
                result = powerup.apply(player2)
                if result == 'shield':
                    sounds.play('shield')
                else:
                    sounds.play('powerup')
                arena.spawn_particles(player2.x, player2.y, powerup.color, 10, 4)
                powerups.remove(powerup)
        
        lightning_effects = [e for e in lightning_effects if e.update()]
        
        arena.draw(screen)
        
        for powerup in powerups:
            powerup.draw(screen)
        
        player1.draw(screen)
        player2.draw(screen)
        
        for effect in lightning_effects:
            effect.draw(screen)
        
        draw_hud(screen, player1, player2, powerups)
        
        pygame.display.update()
        clock.tick(FPS)
        
        if player1.health <= 0 or player2.health <= 0:
            winner = None
            if player1.health > 0:
                winner = "玩家1 获胜!"
            elif player2.health > 0:
                winner = "玩家2 获胜!"
            else:
                winner = None
            
            if sounds:
                sounds.play('game_over')
            
            restart = show_game_over_screen(winner, sounds)
            if restart:
                player1 = Player(200, HEIGHT // 2, COLORS['green'], "玩家1",
                               {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d, 'skill': pygame.K_q})
                player2 = Player(WIDTH - 200, HEIGHT // 2, COLORS['blue'], "玩家2",
                               {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'skill': pygame.K_KP_DIVIDE})
                powerups = []
                lightning_effects = []
                powerup_spawn_timer = 0
                game_time = 0
            else:
                pygame.quit()
                return

if __name__ == "__main__":
    main()
