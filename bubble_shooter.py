import pygame
import random
import math
import struct
import io

pygame.init()

WIDTH, HEIGHT = 800, 600
GRID_TOP = 80
BUBBLE_RADIUS = 18
BUBBLE_DIAMETER = BUBBLE_RADIUS * 2
COLS = 15
ROWS = 12

RED = (255, 60, 60)
GREEN = (60, 255, 120)
BLUE = (60, 120, 255)
YELLOW = (255, 220, 60)
PURPLE = (180, 60, 255)
ORANGE = (255, 150, 60)

BOMB_COLOR = (30, 30, 30)
LIGHTNING_COLOR = (200, 200, 255)

BUBBLE_COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("魔法泡泡消除")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 32)
font_small = pygame.font.Font(None, 24)

class SoundGenerator:
    def __init__(self):
        self.sample_rate = 22050
        self.enabled = True

    def generate_shoot_sound(self):
        if not self.enabled:
            return None
        duration = 0.08
        samples = int(self.sample_rate * duration)
        data = bytearray()
        for i in range(samples):
            t = i / self.sample_rate
            freq = 600 + (800 - 600) * (i / samples)
            wave = math.sin(2 * math.pi * freq * t)
            envelope = 1.0 - (i / samples)
            value = int(wave * envelope * 150)
            data.append(128 + value)
        return self._create_sound(data)

    def generate_match_sound(self):
        if not self.enabled:
            return None
        duration = 0.15
        samples = int(self.sample_rate * duration)
        data = bytearray()
        for i in range(samples):
            t = i / self.sample_rate
            freq = 523 + (784 - 523) * (i / samples)
            wave = math.sin(2 * math.pi * freq * t)
            envelope = 1.0 - (i / samples) * 0.5
            value = int(wave * envelope * 200)
            data.append(128 + value)
        return self._create_sound(data)

    def generate_combo_sound(self):
        if not self.enabled:
            return None
        duration = 0.25
        samples = int(self.sample_rate * duration)
        data = bytearray()
        for i in range(samples):
            t = i / self.sample_rate
            freq = 400
            wave = math.sin(2 * math.pi * freq * t)
            wave += math.sin(2 * math.pi * freq * 1.5 * t) * 0.5
            wave += math.sin(2 * math.pi * freq * 2 * t) * 0.3
            envelope = math.exp(-t * 8)
            value = int(wave * envelope * 180)
            data.append(128 + value)
        return self._create_sound(data)

    def generate_bomb_sound(self):
        if not self.enabled:
            return None
        duration = 0.4
        samples = int(self.sample_rate * duration)
        data = bytearray()
        for i in range(samples):
            t = i / self.sample_rate
            wave = math.sin(2 * math.pi * 80 * t)
            wave += math.sin(2 * math.pi * 60 * t) * 0.5
            noise = random.uniform(-1, 1) * 0.3
            envelope = math.exp(-t * 5)
            value = int((wave + noise) * envelope * 220)
            data.append(128 + value)
        return self._create_sound(data)

    def generate_lightning_sound(self):
        if not self.enabled:
            return None
        duration = 0.3
        samples = int(self.sample_rate * duration)
        data = bytearray()
        for i in range(samples):
            t = i / self.sample_rate
            freq = 2000 * math.exp(-t * 3)
            wave = math.sin(2 * math.pi * freq * t)
            wave += random.uniform(-1, 1) * 0.2
            envelope = math.exp(-t * 6)
            value = int(wave * envelope * 180)
            data.append(128 + value)
        return self._create_sound(data)

    def generate_ultimate_sound(self):
        if not self.enabled:
            return None
        duration = 1.0
        samples = int(self.sample_rate * duration)
        data = bytearray()
        for i in range(samples):
            t = i / self.sample_rate
            wave = 0
            for harmonic in range(1, 6):
                wave += math.sin(2 * math.pi * 200 * harmonic * t) / harmonic
            envelope = math.sin(math.pi * t / duration)
            envelope *= math.exp(-t * 2)
            value = int(wave * envelope * 180)
            data.append(128 + value)
        return self._create_sound(data)

    def generate_invasion_sound(self):
        if not self.enabled:
            return None
        duration = 0.5
        samples = int(self.sample_rate * duration)
        data = bytearray()
        for i in range(samples):
            t = i / self.sample_rate
            freq = 150 + (300 - 150) * (i / samples)
            wave = math.sin(2 * math.pi * freq * t)
            wave += math.sin(2 * math.pi * freq * 0.5 * t) * 0.5
            envelope = 1.0 - (i / samples) * 0.3
            value = int(wave * envelope * 150)
            data.append(128 + value)
        return self._create_sound(data)

    def generate_drop_sound(self):
        if not self.enabled:
            return None
        duration = 0.2
        samples = int(self.sample_rate * duration)
        data = bytearray()
        for i in range(samples):
            t = i / self.sample_rate
            freq = 800 * math.exp(-t * 10)
            wave = math.sin(2 * math.pi * freq * t)
            envelope = math.exp(-t * 12)
            value = int(wave * envelope * 160)
            data.append(128 + value)
        return self._create_sound(data)

    def _create_sound(self, data):
        try:
            sound = pygame.mixer.Sound(buffer=bytes(data))
            sound.set_volume(0.3)
            return sound
        except:
            return None

class Bubble:
    def __init__(self, grid_row, grid_col, color, bubble_type="normal"):
        self.grid_row = grid_row
        self.grid_col = grid_col
        self.color = color
        self.bubble_type = bubble_type
        self.radius = BUBBLE_RADIUS
        self.x, self.y = self.grid_to_pixel(grid_row, grid_col)
        self.target_x = self.x
        self.target_y = self.y
        self.vx = 0
        self.vy = 0
        self.active = True
        self.connected = False
        self.anim_offset = 0
        self.pulse_time = random.uniform(0, math.pi * 2)

    def grid_to_pixel(self, row, col):
        offset = BUBBLE_RADIUS if row % 2 == 1 else 0
        x = col * BUBBLE_DIAMETER + BUBBLE_RADIUS + offset + 5
        y = row * (BUBBLE_DIAMETER - 4) + GRID_TOP + BUBBLE_RADIUS
        return x, y

    def update_position(self):
        self.x, self.y = self.grid_to_pixel(self.grid_row, self.grid_col)

    def draw(self, surface):
        if not self.active:
            return
        pulse = math.sin(self.pulse_time) * 2 if self.bubble_type != "normal" else 0
        draw_radius = self.radius + pulse

        if self.bubble_type == "bomb":
            pygame.draw.circle(surface, BOMB_COLOR, (int(self.x), int(self.y)), draw_radius)
            pygame.draw.circle(surface, (80, 80, 80), (int(self.x), int(self.y)), draw_radius, 3)
            font_tiny = pygame.font.Font(None, 20)
            text = font_tiny.render("💣", True, (255, 255, 255))
            text_rect = text.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(text, text_rect)
        elif self.bubble_type == "lightning":
            pygame.draw.circle(surface, LIGHTNING_COLOR, (int(self.x), int(self.y)), draw_radius)
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), draw_radius, 2)
            font_tiny = pygame.font.Font(None, 20)
            text = font_tiny.render("⚡", True, (255, 255, 0))
            text_rect = text.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(text, text_rect)
        else:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), draw_radius)
            highlight_pos = (int(self.x - draw_radius * 0.3), int(self.y - draw_radius * 0.3))
            pygame.draw.circle(surface, (255, 255, 255, 100), highlight_pos, int(draw_radius * 0.25))
            pygame.draw.circle(surface, (max(0, self.color[0] - 40), max(0, self.color[1] - 40), max(0, self.color[2] - 40)),
                             (int(self.x), int(self.y)), draw_radius, 2)

class ProjectileBubble:
    def __init__(self, x, y, color, angle):
        self.x = x
        self.y = y
        self.color = color
        self.bubble_type = "normal"
        self.radius = BUBBLE_RADIUS
        self.vx = math.cos(angle) * 12
        self.vy = math.sin(angle) * 12
        self.active = True
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y, self.color))
        if len(self.trail) > 8:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        if self.x <= self.radius or self.x >= WIDTH - self.radius:
            self.vx *= -1
            self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        if self.y <= GRID_TOP + self.radius:
            self.active = False

    def draw(self, surface):
        for i, (tx, ty, tc) in enumerate(self.trail):
            alpha = int(100 * (i / len(self.trail)))
            trail_radius = int(self.radius * (i / len(self.trail)) * 0.7)
            if trail_radius > 0:
                temp_surf = pygame.Surface((trail_radius * 2 + 2, trail_radius * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, (*tc, alpha), (trail_radius + 1, trail_radius + 1), trail_radius)
                surface.blit(temp_surf, (int(tx) - trail_radius - 1, int(ty) - trail_radius - 1))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x - self.radius * 0.3), int(self.y - self.radius * 0.3)),
                          int(self.radius * 0.25))

class ParticleEffect:
    def __init__(self, x, y, color, particle_type="normal"):
        self.x = x
        self.y = y
        self.color = color
        self.particle_type = particle_type
        self.lifetime = 30
        self.max_lifetime = 30
        self.particles = []
        count = 12 if particle_type == "normal" else 20
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.uniform(3, 6),
                'life': self.lifetime
            })

    def update(self):
        self.lifetime -= 1
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1
            p['life'] -= 1
            p['size'] *= 0.95
        self.particles = [p for p in self.particles if p['life'] > 0]

    def draw(self, surface):
        for p in self.particles:
            alpha = int(255 * (p['life'] / self.max_lifetime))
            temp_surf = pygame.Surface((int(p['size'] * 2 + 2), int(p['size'] * 2 + 2)), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*self.color, alpha), (int(p['size'] + 1), int(p['size'] + 1)), int(p['size']))
            surface.blit(temp_surf, (int(p['x'] - p['size'] - 1), int(p['y'] - p['size'] - 1)))

    def is_dead(self):
        return self.lifetime <= 0 or len(self.particles) == 0

class FloatingText:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.lifetime = 60
        self.max_lifetime = 60

    def update(self):
        self.y -= 1
        self.lifetime -= 1

    def draw(self, surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        text_surf = font_medium.render(self.text, True, self.color)
        temp_surf = pygame.Surface((text_surf.get_width() + 10, text_surf.get_height() + 10), pygame.SRCALPHA)
        temp_surf.blit(text_surf, (5, 5))
        pygame.draw.rect(temp_surf, (*self.color, alpha // 3), temp_surf.get_rect(), 2)
        surface.blit(temp_surf, (int(self.x - text_surf.get_width() // 2 - 5), int(self.y)))

    def is_dead(self):
        return self.lifetime <= 0

class Game:
    def __init__(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.projectile = None
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.energy = 0
        self.max_energy = 100
        self.wave = 1
        self.wave_timer = 0
        self.invasion_active = False
        self.invasion_progress = 0
        self.ultimate_ready = False
        self.ultimate_active = False
        self.ultimate_timer = 0
        self.particles = []
        self.floating_texts = []
        self.sounds = SoundGenerator()
        self.shoot_sound = self.sounds.generate_shoot_sound()
        self.match_sound = self.sounds.generate_match_sound()
        self.combo_sound = self.sounds.generate_combo_sound()
        self.bomb_sound = self.sounds.generate_bomb_sound()
        self.lightning_sound = self.sounds.generate_lightning_sound()
        self.ultimate_sound = self.sounds.generate_ultimate_sound()
        self.invasion_sound = self.sounds.generate_invasion_sound()
        self.drop_sound = self.sounds.generate_drop_sound()
        self.current_color = random.choice(BUBBLE_COLORS)
        self.next_color = self._generate_next_color()
        self.special_chance = 0.08
        self.game_over = False
        self.start_screen = True
        self.aim_angle = -math.pi / 2
        self.mouse_x = WIDTH // 2
        self.mouse_y = HEIGHT // 2
        self.player_x = WIDTH // 2
        self.player_y = HEIGHT - 60
        self._init_grid()

    def _generate_next_color(self):
        if random.random() < self.special_chance:
            if random.random() < 0.5:
                return "bomb"
            else:
                return "lightning"
        return random.choice(BUBBLE_COLORS)

    def _init_grid(self):
        for row in range(4):
            for col in range(COLS):
                if col < COLS:
                    color = random.choice(BUBBLE_COLORS)
                    self.grid[row][col] = Bubble(row, col, color)

    def get_valid_next_color(self):
        colors_in_grid = set()
        for row in self.grid:
            for bubble in row:
                if bubble and bubble.active and bubble.bubble_type == "normal":
                    colors_in_grid.add(bubble.color)
        if colors_in_grid:
            return random.choice(list(colors_in_grid))
        return random.choice(BUBBLE_COLORS)

    def color_shift(self, projectile_color):
        target_color = self.get_valid_next_color()
        if isinstance(projectile_color, str):
            return target_color
        return target_color

    def get_neighbors(self, row, col):
        neighbors = []
        directions = [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)]
        if row % 2 == 1:
            directions = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                neighbors.append((nr, nc))
        return neighbors

    def find_floating_bubbles(self):
        connected = set()
        queue = []
        for col in range(COLS):
            if self.grid[0][col] and self.grid[0][col].active:
                queue.append((0, col))
                connected.add((0, col))
        while queue:
            row, col = queue.pop(0)
            for nr, nc in self.get_neighbors(row, col):
                if (nr, nc) not in connected and self.grid[nr][nc] and self.grid[nr][nc].active:
                    connected.add((nr, nc))
                    queue.append((nr, nc))
        floating = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.grid[row][col] and self.grid[row][col].active and (row, col) not in connected:
                    floating.append((row, col))
        return floating

    def remove_bubbles(self, bubbles_to_remove):
        score_gain = 0
        for row, col in bubbles_to_remove:
            bubble = self.grid[row][col]
            if bubble and bubble.active:
                if bubble.bubble_type == "bomb":
                    if self.bomb_sound:
                        self.bomb_sound.play()
                    cross = [(row, col)]
                    for dr in range(-3, 4):
                        if 0 <= row + dr < ROWS:
                            cross.append((row + dr, col))
                    for dc in range(-3, 4):
                        if 0 <= col + dc < COLS:
                            cross.append((row, col + dc))
                    for r, c in cross:
                        if self.grid[r][c] and self.grid[r][c].active:
                            self.particles.append(ParticleEffect(self.grid[r][c].x, self.grid[r][c].y, (255, 100, 50), "explosion"))
                            self.grid[r][c].active = False
                            score_gain += 15
                    self.energy = min(self.max_energy, self.energy + 8)
                elif bubble.bubble_type == "lightning":
                    if self.lightning_sound:
                        self.lightning_sound.play()
                    color = bubble.color
                    chain = []
                    for r in range(ROWS):
                        for c in range(COLS):
                            if self.grid[r][c] and self.grid[r][c].active and self.grid[r][c].color == color:
                                chain.append((r, c))
                    for r, c in chain:
                        self.particles.append(ParticleEffect(self.grid[r][c].x, self.grid[r][c].y, (150, 150, 255), "lightning"))
                        self.grid[r][c].active = False
                        score_gain += 12
                    self.energy = min(self.max_energy, self.energy + 5)
                else:
                    self.particles.append(ParticleEffect(bubble.x, bubble.y, bubble.color))
                    score_gain += 10
                    self.energy = min(self.max_energy, self.energy + 2)
        return score_gain

    def drop_floating_bubbles(self):
        floating = self.find_floating_bubbles()
        score_gain = 0
        for row, col in floating:
            bubble = self.grid[row][col]
            if bubble and bubble.active:
                self.particles.append(ParticleEffect(bubble.x, bubble.y, bubble.color, "drop"))
                bubble.active = False
                score_gain += 20
                if self.drop_sound:
                    self.drop_sound.play()
        return score_gain

    def trigger_ultimate(self):
        if self.energy >= self.max_energy and not self.ultimate_active:
            self.ultimate_active = True
            self.ultimate_timer = 60
            self.energy = 0
            self.ultimate_ready = False
            if self.ultimate_sound:
                self.ultimate_sound.play()
            score_gain = 0
            for row in range(ROWS):
                for col in range(COLS):
                    if self.grid[row][col] and self.grid[row][col].active:
                        self.particles.append(ParticleEffect(self.grid[row][col].x, self.grid[row][col].y, (255, 255, 100), "ultimate"))
                        self.grid[row][col].active = False
                        score_gain += 5
            self.score += score_gain
            self.floating_texts.append(FloatingText(WIDTH // 2, HEIGHT // 2, f"全屏消除! +{score_gain}", (255, 255, 0)))

    def spawn_wave(self):
        self.wave += 1
        self.wave_timer = 300
        if self.invasion_sound:
            self.invasion_sound.play()
        new_row = []
        for col in range(COLS):
            if random.random() < 0.7:
                color = random.choice(BUBBLE_COLORS)
                new_row.append(Bubble(0, col, color))
            else:
                new_row.append(None)
        for row in range(ROWS - 1, 0, -1):
            self.grid[row] = self.grid[row - 1][:]
            for col in range(COLS):
                if self.grid[row][col]:
                    self.grid[row][col].grid_row = row
                    self.grid[row][col].update_position()
        self.grid[0] = new_row
        for col in range(COLS):
            if self.grid[0][col]:
                self.grid[0][col].grid_row = 0
                self.grid[0][col].update_position()

    def shoot(self):
        if self.projectile is None:
            color = self.current_color
            special_type = "normal"
            if isinstance(color, str):
                if color == "bomb":
                    special_type = "bomb"
                    color = self.get_valid_next_color()
                elif color == "lightning":
                    special_type = "lightning"
                    color = self.get_valid_next_color()
            self.projectile = ProjectileBubble(self.player_x, self.player_y, color, self.aim_angle)
            self.projectile.bubble_type = special_type
            if self.shoot_sound:
                self.shoot_sound.play()
            self.current_color = self.next_color
            self.next_color = self._generate_next_color()

    def check_collision(self, projectile):
        for row in range(ROWS):
            for col in range(COLS):
                bubble = self.grid[row][col]
                if bubble and bubble.active:
                    dx = projectile.x - bubble.x
                    dy = projectile.y - bubble.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < BUBBLE_RADIUS * 1.8:
                        return (row, col)
        if projectile.y <= GRID_TOP + BUBBLE_RADIUS:
            return (0, int(projectile.x // BUBBLE_DIAMETER))
        return None

    def find_empty_spot(self, row, col):
        if 0 <= row < ROWS and 0 <= col < COLS and self.grid[row][col] is None:
            return (row, col)
        neighbors = self.get_neighbors(row, col) if row < ROWS else [(0, c) for c in range(COLS) if self.grid[0][c] is None]
        for nr, nc in sorted(neighbors, key=lambda x: abs(x[0] - row) + abs(x[1] - col)):
            if 0 <= nr < ROWS and 0 <= nc < COLS and self.grid[nr][nc] is None:
                return (nr, nc)
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] is None:
                    return (r, c)
        return None

    def process_match(self, row, col, color):
        matched = []
        stack = [(row, col)]
        visited = set()
        while stack:
            r, c = stack.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            if 0 <= r < ROWS and 0 <= c < COLS:
                bubble = self.grid[r][c]
                if bubble and bubble.active and bubble.bubble_type == "normal" and bubble.color == color:
                    matched.append((r, c))
                    stack.extend(self.get_neighbors(r, c))
        if len(matched) >= 3:
            return matched
        return []

    def handle_projectile_landed(self, row, col):
        color = self.projectile.color
        special_type = self.projectile.bubble_type
        new_bubble = Bubble(row, col, color, special_type)
        self.grid[row][col] = new_bubble
        self.projectile = None
        matched = self.process_match(row, col, color)
        score_gain = 0
        if matched:
            if self.match_sound:
                self.match_sound.play()
            score_gain = self.remove_bubbles(matched)
            self.combo += 1
            self.combo_timer = 120
            combo_multiplier = min(self.combo, 5)
            score_gain *= combo_multiplier
            self.score += score_gain
            if self.combo >= 2:
                if self.combo_sound:
                    self.combo_sound.play()
                self.floating_texts.append(FloatingText(new_bubble.x, new_bubble.y, f"连击 x{self.combo}!", (255, 200, 50)))
            drop_score = self.drop_floating_bubbles()
            self.score += drop_score
            self.current_color = self.color_shift(color)
        else:
            self.combo = 0
            self.current_color = self.color_shift(color)
        if self.energy >= self.max_energy:
            self.ultimate_ready = True

    def update(self):
        if self.start_screen:
            return
        if self.game_over:
            return
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0
        if self.ultimate_active:
            self.ultimate_timer -= 1
            if self.ultimate_timer <= 0:
                self.ultimate_active = False
        self.wave_timer -= 1
        if self.wave_timer <= 0 and not self.invasion_active:
            self.spawn_wave()
        if self.projectile:
            self.projectile.update()
            if not self.projectile.active:
                collision = self.check_collision(self.projectile)
                if collision:
                    row, col = collision
                    if 0 <= row < ROWS and 0 <= col < COLS:
                        spot = self.find_empty_spot(row, col)
                        if spot:
                            self.handle_projectile_landed(spot[0], spot[1])
                else:
                    self.projectile = None
            elif self.projectile.y <= GRID_TOP + BUBBLE_RADIUS:
                collision = self.check_collision(self.projectile)
                if collision:
                    row, col = collision
                    spot = self.find_empty_spot(row, col)
                    if spot:
                        self.handle_projectile_landed(spot[0], spot[1])
                else:
                    for c in range(COLS):
                        if self.grid[0][c] is None:
                            self.handle_projectile_landed(0, c)
                            break
        for row in range(ROWS):
            for col in range(COLS):
                bubble = self.grid[row][col]
                if bubble:
                    bubble.pulse_time += 0.05
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if not p.is_dead()]
        for text in self.floating_texts:
            text.update()
        self.floating_texts = [t for t in self.floating_texts if not t.is_dead()]
        self._check_game_over()

    def _check_game_over(self):
        for col in range(COLS):
            if self.grid[ROWS - 1][col] and self.grid[ROWS - 1][col].active:
                self.game_over = True
                return

    def draw_background(self):
        screen.fill((10, 10, 30))
        for i in range(0, WIDTH, 40):
            alpha = int(20 + (i % 80) / 80 * 15)
            temp_surf = pygame.Surface((2, HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(temp_surf, (40, 40, 80, alpha), (1, 0), (1, HEIGHT))
            screen.blit(temp_surf, (i, 0))
        for i in range(GRID_TOP, HEIGHT, 30):
            alpha = int(15 + ((i - GRID_TOP) % 60) / 60 * 10)
            temp_surf = pygame.Surface((WIDTH, 1), pygame.SRCALPHA)
            pygame.draw.line(temp_surf, (30, 30, 60, alpha), (0, 0), (WIDTH, 0))
            screen.blit(temp_surf, (0, i))
        pygame.draw.line(screen, (80, 80, 150), (0, GRID_TOP - 5), (WIDTH, GRID_TOP - 5), 3)

    def draw_energy_bar(self):
        bar_width = 200
        bar_height = 20
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = HEIGHT - 35
        pygame.draw.rect(screen, (40, 40, 60), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), border_radius=5)
        pygame.draw.rect(screen, (20, 20, 40), (bar_x, bar_y, bar_width, bar_height), border_radius=4)
        fill_width = int((self.energy / self.max_energy) * bar_width)
        if fill_width > 0:
            gradient_surf = pygame.Surface((fill_width, bar_height), pygame.SRCALPHA)
            for i in range(fill_width):
                ratio = i / bar_width
                color = (int(100 + 155 * ratio), int(200 - 100 * ratio), int(255 * (1 - ratio)), 200)
                pygame.draw.line(gradient_surf, color, (i, 0), (i, bar_height))
            screen.blit(gradient_surf, (bar_x, bar_y))
        if self.ultimate_ready:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 30
            glow_surf = pygame.Surface((bar_width + 20, bar_height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (255, 200, 50, int(50 + pulse)), glow_surf.get_rect(), border_radius=8)
            screen.blit(glow_surf, (bar_x - 10, bar_y - 10))
        pygame.draw.rect(screen, (100, 100, 200), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=4)
        label = "能量条 [空格]释放大招!" if self.ultimate_ready else "能量条"
        label_surf = font_small.render(label, True, (200, 200, 255) if self.ultimate_ready else (150, 150, 200))
        screen.blit(label_surf, (bar_x + bar_width // 2 - label_surf.get_width() // 2, bar_y - 20))

    def draw_player(self):
        pygame.draw.circle(screen, (60, 60, 100), (self.player_x, self.player_y + 10), 35)
        if isinstance(self.current_color, str):
            display_color = (150, 150, 150)
        else:
            display_color = self.current_color
        pygame.draw.circle(screen, display_color, (self.player_x, self.player_y), BUBBLE_RADIUS + 2)
        pygame.draw.circle(screen, (255, 255, 255), (self.player_x - 5, self.player_y - 5), 5)
        dx = self.mouse_x - self.player_x
        dy = self.mouse_y - self.player_y
        angle = math.atan2(dy, dx)
        end_x = self.player_x + math.cos(angle) * 80
        end_y = self.player_y + math.sin(angle) * 80
        pygame.draw.line(screen, (100, 100, 150), (self.player_x, self.player_y), (end_x, end_y), 3)
        pygame.draw.circle(screen, (150, 150, 200), (int(end_x), int(end_y)), 6)

    def draw_next_bubble(self):
        preview_x = WIDTH - 70
        preview_y = HEIGHT - 60
        pygame.draw.circle(screen, (50, 50, 80), (preview_x, preview_y), 32)
        pygame.draw.circle(screen, (30, 30, 60), (preview_x, preview_y), 30, 2)
        if isinstance(self.next_color, str):
            if self.next_color == "bomb":
                pygame.draw.circle(screen, BOMB_COLOR, (preview_x, preview_y), BUBBLE_RADIUS)
                font_tiny = pygame.font.Font(None, 18)
                text = font_tiny.render("💣", True, (255, 255, 255))
                text_rect = text.get_rect(center=(preview_x, preview_y))
                screen.blit(text, text_rect)
            elif self.next_color == "lightning":
                pygame.draw.circle(screen, LIGHTNING_COLOR, (preview_x, preview_y), BUBBLE_RADIUS)
                font_tiny = pygame.font.Font(None, 18)
                text = font_tiny.render("⚡", True, (255, 255, 0))
                text_rect = text.get_rect(center=(preview_x, preview_y))
                screen.blit(text, text_rect)
        else:
            pygame.draw.circle(screen, self.next_color, (preview_x, preview_y), BUBBLE_RADIUS)
        label = font_small.render("下一个", True, (150, 150, 200))
        screen.blit(label, (preview_x - label.get_width() // 2, preview_y - 50))

    def draw_hud(self):
        score_text = font_medium.render(f"分数: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 15))
        wave_text = font_medium.render(f"波次: {self.wave}", True, (200, 200, 255))
        screen.blit(wave_text, (20, 45))
        if self.combo > 1:
            combo_text = font_large.render(f"连击 x{self.combo}", True, (255, 200, 50))
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 5
            combo_rect = combo_text.get_rect(center=(WIDTH // 2, 40))
            screen.blit(combo_text, (combo_rect.x, combo_rect.y - pulse))
        color_name = "特殊" if isinstance(self.current_color, str) else "普通"
        color_text = font_small.render(f"当前: {color_name}", True, (180, 180, 220))
        screen.blit(color_text, (WIDTH - 120, 15))

    def draw_ultimate_effect(self):
        if self.ultimate_active:
            progress = 1 - (self.ultimate_timer / 60)
            for i in range(5):
                alpha = int(100 * (1 - progress) * math.sin(progress * math.pi * 10 + i))
                if alpha > 0:
                    offset = i * 20 - 40
                    line_y = GRID_TOP + offset + int(progress * (HEIGHT - GRID_TOP))
                    if 0 <= line_y < HEIGHT:
                        temp_surf = pygame.Surface((WIDTH, 3), pygame.SRCALPHA)
                        pygame.draw.line(temp_surf, (255, 255, 100, alpha), (0, 1), (WIDTH, 1))
                        screen.blit(temp_surf, (0, line_y))

    def draw_start_screen(self):
        screen.fill((10, 10, 40))
        title = font_large.render("魔法泡泡消除", True, (255, 220, 100))
        title_rect = title.get_rect(center=(WIDTH // 2, 150))
        screen.blit(title, title_rect)
        instructions = [
            "🎯 玩法说明",
            "",
            "• 射击泡泡攻击入侵的怪物泡泡",
            "• 3个以上同色泡泡相连即可消除",
            "• 泡泡染色: 射击的泡泡颜色会改变",
            "• 连击: 连续消除获得分数加成",
            "• 炸弹泡泡: 十字范围消除",
            "• 闪电泡泡: 消除所有同色泡泡",
            "• 能量条满了按空格释放全屏大招",
            "",
            "🖱️ 点击鼠标左键射击",
            "",
            "按任意键开始游戏..."
        ]
        for i, line in enumerate(instructions):
            color = (200, 200, 255) if i == 0 else (180, 180, 220)
            text = font_small.render(line, True, color)
            text_rect = text.get_rect(center=(WIDTH // 2, 250 + i * 30))
            screen.blit(text, text_rect)
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 50
        start_text = font_medium.render("按任意键开始游戏...", True, (150 + pulse, 150 + pulse, 255))
        start_rect = start_text.get_rect(center=(WIDTH // 2, 550))
        screen.blit(start_text, start_rect)

    def draw_game_over_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 180), overlay.get_rect())
        screen.blit(overlay, (0, 0))
        game_over_text = font_large.render("游戏结束", True, (255, 80, 80))
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(game_over_text, game_over_rect)
        score_text = font_medium.render(f"最终得分: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        screen.blit(score_text, score_rect)
        wave_text = font_medium.render(f"到达波次: {self.wave}", True, (200, 200, 255))
        wave_rect = wave_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(wave_text, wave_rect)
        restart_text = font_small.render("按 R 键重新开始", True, (150, 150, 200))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        screen.blit(restart_text, restart_rect)

    def draw(self):
        if self.start_screen:
            self.draw_start_screen()
            pygame.display.update()
            return
        self.draw_background()
        for row in range(ROWS):
            for col in range(COLS):
                bubble = self.grid[row][col]
                if bubble and bubble.active:
                    bubble.draw(screen)
        if self.projectile:
            self.projectile.draw(screen)
        for particle in self.particles:
            particle.draw(screen)
        for text in self.floating_texts:
            text.draw(screen)
        self.draw_player()
        self.draw_next_bubble()
        self.draw_energy_bar()
        self.draw_hud()
        self.draw_ultimate_effect()
        if self.game_over:
            self.draw_game_over_screen()
        pygame.display.update()

    def handle_event(self, event):
        if self.start_screen:
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                self.start_screen = False
            return
        if self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.__init__()
            return
        if event.type == pygame.MOUSEMOTION:
            self.mouse_x, self.mouse_y = event.pos
            dx = self.mouse_x - self.player_x
            dy = self.mouse_y - self.player_y
            self.aim_angle = math.atan2(dy, dx)
            self.aim_angle = max(-math.pi + 0.1, min(-0.1, self.aim_angle))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.shoot()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and self.ultimate_ready:
                self.trigger_ultimate()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_event(event)
            self.update()
            self.draw()
            clock.tick(60)
        pygame.quit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
