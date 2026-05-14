"""
冰上曲棍球赛车
玩家驾驶冰球在冰面上滑行竞速，利用冰面物理特性进行比赛
"""

import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("冰上曲棍球赛车")
clock = pygame.time.Clock()

ICE_BLUE = (200, 230, 255)
ICE_DARK = (150, 200, 230)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 80, 80)
BLUE = (80, 120, 255)
GREEN = (80, 200, 120)
YELLOW = (255, 230, 100)
PURPLE = (180, 100, 220)
CYAN = (100, 220, 220)
PINK = (255, 150, 200)

class Puck:
    """玩家控制的冰球"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 20
        self.friction = 0.985
        self.is_ball_mode = False
        self.ball_mode_timer = 0
        self.freeze_cooldown = 0
        self.freeze_active = False
        self.freeze_timer = 0
        self.energy = 0
        self.speed_trail = []
        
    def update(self):
        keys = pygame.key.get_pressed()
        
        if self.freeze_cooldown > 0:
            self.freeze_cooldown -= 1
        
        if self.freeze_active:
            self.freeze_timer -= 1
            if self.freeze_timer <= 0:
                self.freeze_active = False
        
        if self.ball_mode_timer > 0:
            self.ball_mode_timer -= 1
            if self.ball_mode_timer <= 0:
                self.is_ball_mode = False
        
        acceleration = 0.35 if not self.is_ball_mode else 0.5
        max_speed = 8 if not self.is_ball_mode else 12
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx -= acceleration
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx += acceleration
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vy -= acceleration
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy += acceleration
        
        drift = 0.92 if keys[pygame.K_LSHIFT] else 0.98
        self.vx *= drift
        self.vy *= drift
        
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > max_speed:
            self.vx = (self.vx / speed) * max_speed
            self.vy = (self.vy / speed) * max_speed
        
        self.vx *= self.friction
        self.vy *= self.friction
        
        self.x += self.vx
        self.y += self.vy
        
        if keys[pygame.K_e] and self.freeze_cooldown <= 0 and self.energy >= 30:
            self.activate_freeze()
        
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = abs(self.vx) * 0.5
        if self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx = -abs(self.vx) * 0.5
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = abs(self.vy) * 0.5
        if self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy = -abs(self.vy) * 0.5
        
        self.speed_trail.append((self.x, self.y))
        if len(self.speed_trail) > 15:
            self.speed_trail.pop(0)
    
    def activate_freeze(self):
        self.freeze_active = True
        self.freeze_timer = 60
        self.freeze_cooldown = 180
        self.energy -= 30
        play_sound('freeze')
    
    def draw(self):
        speed = math.sqrt(self.vx**2 + self.vy**2)
        
        for i, pos in enumerate(self.speed_trail[:-1]):
            alpha = int((i / len(self.speed_trail)) * 100)
            trail_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (*CYAN, alpha), (5, 5), 4)
            screen.blit(trail_surface, (pos[0] - 5, pos[1] - 5))
        
        if self.freeze_active:
            freeze_radius = 80 + math.sin(pygame.time.get_ticks() * 0.1) * 10
            freeze_surface = pygame.Surface((int(freeze_radius * 2), int(freeze_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(freeze_surface, (150, 220, 255, 80), (int(freeze_radius), int(freeze_radius)), int(freeze_radius))
            pygame.draw.circle(freeze_surface, (200, 240, 255, 150), (int(freeze_radius), int(freeze_radius)), int(freeze_radius), 3)
            screen.blit(freeze_surface, (int(self.x - freeze_radius), int(self.y - freeze_radius)))
        
        if self.is_ball_mode:
            pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), int(self.radius * 1.3))
            for i in range(8):
                angle = i * (math.pi / 4) + pygame.time.get_ticks() * 0.01
                bx = self.x + math.cos(angle) * self.radius * 1.5
                by = self.y + math.sin(angle) * self.radius * 1.5
                pygame.draw.circle(screen, WHITE, (int(bx), int(by)), 4)
        else:
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, WHITE, (int(self.x - 5), int(self.y - 5)), 6)
        
        if self.energy > 0:
            energy_bar_width = 40
            energy_bar_height = 6
            pygame.draw.rect(screen, (50, 50, 50), (self.x - energy_bar_width//2, self.y + self.radius + 10, energy_bar_width, energy_bar_height))
            pygame.draw.rect(screen, CYAN, (self.x - energy_bar_width//2, self.y + self.radius + 10, int(energy_bar_width * min(self.energy, 100) / 100), energy_bar_height))

class AI_Puck:
    """AI对手冰球"""
    def __init__(self, x, y, color, behavior='aggressive'):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 18
        self.color = color
        self.behavior = behavior
        self.target_x = x
        self.target_y = y
        self.speed = 5.5 + random.random() * 2
        self.frozen = 0
        self.friction = 0.985
    
    def update(self, player, checkpoints):
        if self.frozen > 0:
            self.frozen -= 1
            self.vx *= 0.9
            self.vy *= 0.9
        else:
            if player.freeze_active:
                dx = self.x - player.x
                dy = self.y - player.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist < 100:
                    self.speed *= 0.7
            
            target = random.choice(checkpoints) if checkpoints else (WIDTH//2, HEIGHT//2)
            if random.random() < 0.02:
                target = (random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50))
            
            dx = target[0] - self.x
            dy = target[1] - self.y
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist > 10:
                self.vx += (dx / dist) * 0.2
                self.vy += (dy / dist) * 0.2
            
            current_speed = math.sqrt(self.vx**2 + self.vy**2)
            if current_speed > self.speed:
                self.vx = (self.vx / current_speed) * self.speed
                self.vy = (self.vy / current_speed) * self.speed
        
        self.vx *= self.friction
        self.vy *= self.friction
        
        self.x += self.vx
        self.y += self.vy
        
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = abs(self.vx) * 0.5
        if self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx = -abs(self.vx) * 0.5
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = abs(self.vy) * 0.5
        if self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy = -abs(self.vy) * 0.5
    
    def draw(self):
        if self.frozen > 0:
            pygame.draw.circle(screen, (150, 200, 255), (int(self.x), int(self.y)), self.radius + 5)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            for i in range(4):
                angle = i * (math.pi / 2)
                sx = self.x + math.cos(angle) * (self.radius + 8)
                sy = self.y + math.sin(angle) * (self.radius + 8)
                pygame.draw.circle(screen, WHITE, (int(sx), int(sy)), 5)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, WHITE, (int(self.x - 4), int(self.y - 4)), 5)

class EnergyOrb:
    """能量球道具"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.collected = False
        self.anim_offset = random.random() * math.pi * 2
        self.pulse = 0
    
    def update(self):
        self.pulse += 0.1
    
    def draw(self):
        if self.collected:
            return
        
        y_offset = math.sin(self.pulse + self.anim_offset) * 5
        glow_radius = self.radius + 8 + math.sin(self.pulse * 2) * 3
        
        glow_surface = pygame.Surface((int(glow_radius * 2 + 10), int(glow_radius * 2 + 10)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 220, 100, 100), (int(glow_radius + 5), int(glow_radius + 5)), int(glow_radius))
        screen.blit(glow_surface, (int(self.x - glow_radius - 5), int(self.y + y_offset - glow_radius - 5)))
        
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y + int(y_offset))), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y + int(y_offset))), self.radius, 2)
        
        pygame.draw.circle(screen, (255, 255, 200), (int(self.x - 3), int(self.y + int(y_offset) - 3)), 4)

class IceHockeyRacing:
    """冰上曲棍球赛车游戏主类"""
    def __init__(self):
        self.player = Puck(WIDTH // 2, HEIGHT - 100)
        self.ai_opponents = [
            AI_Puck(150, 150, BLUE, 'aggressive'),
            AI_Puck(WIDTH - 150, 150, GREEN, 'defensive'),
            AI_Puck(WIDTH // 2, 100, PURPLE, 'balanced')
        ]
        self.energy_orbs = []
        self.checkpoints = [
            (100, 100), (WIDTH - 100, 100),
            (100, HEIGHT // 2), (WIDTH - 100, HEIGHT // 2),
            (WIDTH // 2, HEIGHT // 2)
        ]
        self.phase = 'menu'
        self.score = 0
        self.lap = 0
        self.position = 1
        self.game_time = 0
        self.finish_line_y = HEIGHT - 50
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.snowflakes = []
        for _ in range(50):
            self.snowflakes.append({
                'x': random.random() * WIDTH,
                'y': random.random() * HEIGHT,
                'size': random.random() * 3 + 1,
                'speed': random.random() * 1 + 0.5
            })
    
    def spawn_energy_orb(self):
        if len(self.energy_orbs) < 5 and random.random() < 0.02:
            x = random.randint(50, WIDTH - 50)
            y = random.randint(50, HEIGHT - 50)
            too_close = any(math.sqrt((x - orb.x)**2 + (y - orb.y)**2) < 100 for orb in self.energy_orbs)
            if not too_close:
                self.energy_orbs.append(EnergyOrb(x, y))
    
    def update(self):
        if self.phase != 'playing':
            return
        
        self.game_time += 1
        
        self.player.update()
        
        for ai in self.ai_opponents:
            ai.update(self.player, self.checkpoints)
            dx = self.player.x - ai.x
            dy = self.player.y - ai.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < self.player.radius + ai.radius:
                overlap = self.player.radius + ai.radius - dist
                if dist > 0:
                    nx, ny = dx / dist, dy / dist
                    self.player.x += nx * overlap * 0.5
                    self.player.y += ny * overlap * 0.5
                    ai.x -= nx * overlap * 0.5
                    ai.y -= ny * overlap * 0.5
        
        for orb in self.energy_orbs:
            orb.update()
            if not orb.collected:
                dx = self.player.x - orb.x
                dy = self.player.y - orb.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < self.player.radius + orb.radius:
                    orb.collected = True
                    self.player.energy = min(100, self.player.energy + 25)
                    play_sound('collect')
        
        if self.player.y < 100:
            self.lap += 1
            self.score += 100
            play_sound('checkpoint')
        
        player_progress = self.game_time + (HEIGHT - self.player.y)
        positions = [(p, player_progress)]
        for i, ai in enumerate(self.ai_opponents):
            ai_progress = self.game_time + (HEIGHT - ai.y)
            positions.append((ai, ai_progress))
        
        positions.sort(key=lambda x: x[1], reverse=True)
        self.position = next((i + 1 for i, (obj, _) in enumerate(positions) if obj is self.player), 4)
        
        if random.random() < 0.1:
            self.player.energy = min(100, self.player.energy + 0.5)
        
        self.spawn_energy_orb()
        
        for snow in self.snowflakes:
            snow['y'] += snow['speed']
            snow['x'] += math.sin(snow['y'] * 0.02) * 0.5
            if snow['y'] > HEIGHT:
                snow['y'] = -10
                snow['x'] = random.random() * WIDTH
    
    def draw(self):
        self.draw_ice_surface()
        
        if self.phase == 'menu':
            self.draw_menu()
        elif self.phase == 'playing':
            self.draw_game()
        elif self.phase == 'paused':
            self.draw_game()
            self.draw_pause_overlay()
        
        pygame.display.flip()
    
    def draw_ice_surface(self):
        screen.fill(ICE_BLUE)
        
        for y in range(0, HEIGHT, 40):
            alpha = 30 + int(math.sin(y * 0.1) * 20)
            scratch_surface = pygame.Surface((WIDTH, 3), pygame.SRCALPHA)
            scratch_surface.fill((255, 255, 255, alpha))
            screen.blit(scratch_surface, (0, y))
        
        for x in range(0, WIDTH, 50):
            for snow in self.snowflakes:
                if int(snow['x']) == x or int(snow['x']) == x + 25:
                    pygame.draw.circle(screen, (255, 255, 255, 150), (int(snow['x']), int(snow['y'])), int(snow['size']))
        
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 5))
        pygame.draw.rect(screen, WHITE, (0, 0, 5, HEIGHT))
        pygame.draw.rect(screen, WHITE, (WIDTH - 5, 0, 5, HEIGHT))
        pygame.draw.rect(screen, WHITE, (0, HEIGHT - 5, WIDTH, 5))
        
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        pygame.draw.circle(screen, (180, 210, 240), (center_x, center_y), 60, 3)
        pygame.draw.circle(screen, (180, 210, 240), (center_x, center_y), 5)
        
        pygame.draw.rect(screen, PINK, (0, self.finish_line_y - 10, WIDTH, 20))
        for x in range(0, WIDTH, 20):
            pygame.draw.rect(screen, WHITE, (x, self.finish_line_y - 10, 10, 20))
    
    def draw_menu(self):
        title = self.font_large.render("冰上曲棍球赛车", True, CYAN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        
        subtitle = self.font_small.render("Ice Puck Racing", True, WHITE)
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 110))
        
        instructions = [
            "【操作说明】",
            "方向键/WASD - 移动冰球",
            "SHIFT - 漂移加速",
            "E - 释放冰冻光环 (需要30能量)",
            "空格 - 冰球形态 (更快的速度)",
            "",
            "【游戏目标】",
            "到达屏幕顶部完成一圈获得积分",
            "收集能量球为冰冻技能充能",
            "",
            "按 SPACE 开始游戏!"
        ]
        
        y = 160
        for line in instructions:
            color = YELLOW if line.startswith("【") else WHITE
            text = self.font_small.render(line, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 28
        
        demo_puck = Puck(WIDTH // 2, 520)
        demo_puck.draw()
    
    def draw_game(self):
        for orb in self.energy_orbs:
            orb.draw()
        
        for ai in self.ai_opponents:
            ai.draw()
        
        self.player.draw()
        
        pygame.draw.rect(screen, (20, 40, 60, 200), (10, 10, 200, 120), border_radius=10)
        
        pos_colors = {1: YELLOW, 2: WHITE, 3: PURPLE, 4: RED}
        pos_text = self.font_medium.render(f"第 {self.position} 名", True, pos_colors.get(self.position, WHITE))
        screen.blit(pos_text, (20, 20))
        
        score_text = self.font_small.render(f"得分: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 55))
        
        lap_text = self.font_small.render(f"已跑: {self.lap} 圈", True, WHITE)
        screen.blit(lap_text, (20, 80))
        
        energy_color = CYAN if self.player.energy >= 30 else (100, 100, 100)
        energy_text = self.font_small.render(f"能量: {int(self.player.energy)}%", True, energy_color)
        screen.blit(energy_text, (20, 105))
        
        pygame.draw.rect(screen, (20, 40, 60, 200), (WIDTH - 160, 10, 150, 50), border_radius=10)
        time_text = self.font_medium.render(f"{self.game_time // 60}s", True, WHITE)
        screen.blit(time_text, (WIDTH - 150, 25))
        
        if self.player.ball_mode_timer > 0:
            ball_text = self.font_small.render(f"冰球形态: {self.player.ball_mode_timer // 60 + 1}s", True, CYAN)
            pygame.draw.rect(screen, (20, 40, 60, 200), (WIDTH // 2 - 80, 10, 160, 30), border_radius=10)
            screen.blit(ball_text, (WIDTH // 2 - ball_text.get_width() // 2, 18))
        
        if self.player.freeze_cooldown > 0:
            cooldown_text = self.font_small.render(f"冷却: {self.player.freeze_cooldown // 60 + 1}s", True, (150, 150, 150))
            pygame.draw.rect(screen, (20, 40, 60, 200), (10, HEIGHT - 40, 120, 30), border_radius=10)
            screen.blit(cooldown_text, (20, HEIGHT - 35))
    
    def draw_pause_overlay(self):
        pause_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pause_surface.fill((0, 0, 0, 150))
        screen.blit(pause_surface, (0, 0))
        
        pause_text = self.font_large.render("游戏暂停", True, WHITE)
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))
        
        hint_text = self.font_medium.render("按 ESC 继续", True, WHITE)
        screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 + 20))
    
    def handle_key(self, key):
        if self.phase == 'menu':
            if key == pygame.K_SPACE:
                self.phase = 'playing'
                self.reset_game()
        
        elif self.phase == 'playing':
            if key == pygame.K_ESCAPE:
                self.phase = 'paused'
            elif key == pygame.K_SPACE:
                if self.player.energy >= 15:
                    self.player.is_ball_mode = True
                    self.player.ball_mode_timer = 180
                    self.player.energy -= 15
                    play_sound('transform')
        
        elif self.phase == 'paused':
            if key == pygame.K_ESCAPE:
                self.phase = 'playing'
    
    def reset_game(self):
        self.player = Puck(WIDTH // 2, HEIGHT - 100)
        self.ai_opponents = [
            AI_Puck(150, 150, BLUE, 'aggressive'),
            AI_Puck(WIDTH - 150, 150, GREEN, 'defensive'),
            AI_Puck(WIDTH // 2, 100, PURPLE, 'balanced')
        ]
        self.energy_orbs = []
        self.score = 0
        self.lap = 0
        self.game_time = 0

def generate_sound_data(frequency, duration_ms, sample_rate=22050, wave_type='sine'):
    """生成音效数据"""
    num_samples = int(sample_rate * duration_ms / 1000)
    sound_data = bytearray()
    
    for i in range(num_samples):
        t = i / sample_rate
        sample = 0
        
        if wave_type == 'sine':
            sample = math.sin(2 * math.pi * frequency * t)
        elif wave_type == 'square':
            sample = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
        elif wave_type == 'sawtooth':
            sample = 2 * (frequency * t % 1) - 1
        elif wave_type == 'noise':
            sample = random.random() * 2 - 1
        
        envelope = 1.0
        attack = int(0.01 * sample_rate)
        release = int(0.1 * sample_rate)
        
        if i < attack:
            envelope = i / attack
        elif i > num_samples - release:
            envelope = (num_samples - i) / release
        
        sample = int(sample * envelope * 16000)
        sample = max(-32768, min(32767, sample))
        
        sound_data.extend(sample.to_bytes(2, byteorder='little', signed=True))
    
    return bytes(sound_data)

def play_sound(sound_type):
    """播放指定类型的音效"""
    try:
        if not pygame.mixer.get_init():
            return
            
        sound_effects = {
            'collect': lambda: (800, 100, 'sine'),
            'freeze': lambda: (400, 300, 'sine'),
            'checkpoint': lambda: (600, 150, 'square'),
            'transform': lambda: (500, 80, 'sawtooth')
        }
        
        if sound_type in sound_effects:
            freq, dur, wave = sound_effects[sound_type]()
            sound_data = generate_sound_data(freq, dur, wave_type=wave)
            sound = pygame.mixer.Sound(buffer=sound_data)
            sound.set_volume(0.3)
            sound.play()
    except:
        pass

def main():
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        sound_enabled = True
    except:
        sound_enabled = False
    
    game = IceHockeyRacing()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.phase == 'playing':
                        game.phase = 'paused'
                    elif game.phase == 'paused':
                        game.phase = 'playing'
                    elif game.phase == 'menu':
                        running = False
                elif event.key == pygame.K_SPACE:
                    game.handle_key(event.key)
                else:
                    game.handle_key(event.key)
        
        game.update()
        game.draw()
        clock.tick(60)
    
    if sound_enabled:
        pygame.mixer.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
