import pygame
import os
import sys
import random
import math
import struct

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

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8
JUMP_FORCE = -15

# 难度设置
DIFFICULTIES = {
    '简单': {'rope_speed': 3, 'time_limit': 60, 'base_score': 10},
    '中等': {'rope_speed': 5, 'time_limit': 45, 'base_score': 15},
    '困难': {'rope_speed': 7, 'time_limit': 30, 'base_score': 20}
}

# 技能系统
SKILLS = {
    'slow_motion': {'name': '慢动作', 'duration': 3000, 'cooldown': 15000, 'effect': 0.5},
    'double_score': {'name': '双倍分数', 'duration': 5000, 'cooldown': 20000},
    'magnet': {'name': '磁铁', 'duration': 4000, 'cooldown': 18000}
}

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

class SoundGenerator:
    """使用bytearray生成音效"""
    def __init__(self):
        self.audio_enabled = True
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2)
        except pygame.error:
            self.audio_enabled = False
    
    def generate_sine_wave(self, frequency, duration, volume=0.3):
        if not self.audio_enabled:
            return None
        samples = int(44100 * duration)
        wave = []
        for i in range(samples):
            t = i / 44100
            value = int(volume * 32767 * math.sin(2 * math.pi * frequency * t))
            wave.extend(struct.pack('<h', value))
        sound_data = b''.join(wave)
        sound = pygame.mixer.Sound(sound_data)
        return sound
    
    def generate_jump_sound(self):
        return self.generate_sine_wave(400, 0.1)
    
    def generate_score_sound(self):
        return self.generate_sine_wave(600, 0.2)
    
    def generate_combo_sound(self):
        return self.generate_sine_wave(800, 0.15)
    
    def generate_fail_sound(self):
        return self.generate_sine_wave(200, 0.3)
    
    def generate_skill_sound(self):
        return self.generate_sine_wave(1000, 0.2)
    
    def play_sound(self, sound):
        if sound and self.audio_enabled:
            sound.play()

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.velocity_y = 0
        self.is_jumping = False
        self.rotation = 0
    
    def update(self):
        self.velocity_y += GRAVITY
        self.y += self.velocity_y
        
        if self.y >= SCREEN_HEIGHT - self.height - 10:
            self.y = SCREEN_HEIGHT - self.height - 10
            self.velocity_y = 0
            self.is_jumping = False
            self.rotation = 0
        
        if self.is_jumping:
            self.rotation += 5
    
    def jump(self):
        if not self.is_jumping:
            self.velocity_y = JUMP_FORCE
            self.is_jumping = True
    
    def draw(self, screen):
        # 绘制角色身体
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        # 绘制头部
        pygame.draw.circle(screen, YELLOW, (self.x + self.width // 2, self.y + 15), 12)
        # 绘制眼睛
        pygame.draw.circle(screen, BLACK, (self.x + self.width // 2 - 4, self.y + 13), 2)
        pygame.draw.circle(screen, BLACK, (self.x + self.width // 2 + 4, self.y + 13), 2)

class Rope:
    def __init__(self, center_x):
        self.center_x = center_x
        self.center_y = SCREEN_HEIGHT // 2
        self.radius = 150
        self.angle = 0
        self.speed = 3
        self.thickness = 8
    
    def update(self):
        self.angle += self.speed * 0.1
    
    def draw(self, screen):
        # 计算绳子两端位置
        x1 = self.center_x + self.radius * math.sin(self.angle)
        y1 = self.center_y - self.radius * math.cos(self.angle)
        x2 = self.center_x - self.radius * math.sin(self.angle)
        y2 = self.center_y + self.radius * math.cos(self.angle)
        
        # 绘制绳子
        pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), self.thickness)
        
        # 绘制手柄
        pygame.draw.circle(screen, RED, (x1, y1), 15)
        pygame.draw.circle(screen, RED, (x2, y2), 15)
    
    def get_rope_position(self, player_x):
        """获取绳子在玩家位置的y坐标"""
        dx = player_x - self.center_x
        if abs(dx) > self.radius:
            return None
        
        # 计算绳子在该x位置的两个可能y坐标
        dy = math.sqrt(self.radius ** 2 - dx ** 2)
        y1 = self.center_y - dy * math.cos(self.angle) - dx * math.sin(self.angle)
        y2 = self.center_y + dy * math.cos(self.angle) + dx * math.sin(self.angle)
        
        return y1, y2

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('跳绳挑战')
        self.clock = pygame.time.Clock()
        self.sound_gen = SoundGenerator()
        
        # 游戏状态
        self.game_state = 'menu'  # menu, playing, paused, gameover
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.time_left = 60
        self.difficulty = '简单'
        
        # 技能状态
        self.active_skill = None
        self.skill_end_time = 0
        self.skill_cooldowns = {skill: 0 for skill in SKILLS}
        
        # 游戏对象
        self.player = Player(SCREEN_WIDTH // 3, SCREEN_HEIGHT - 100)
        self.rope = Rope(SCREEN_WIDTH // 2)
        
        # 字体
        self.font = get_chinese_font(40)
        self.small_font = get_chinese_font(28)
        
        # 计时器
        self.timer_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.timer_event, 1000)
        
        # 粒子效果
        self.particles = []
        
    def reset_game(self):
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.time_left = DIFFICULTIES[self.difficulty]['time_limit']
        self.rope.speed = DIFFICULTIES[self.difficulty]['rope_speed']
        self.player = Player(SCREEN_WIDTH // 3, SCREEN_HEIGHT - 100)
        self.rope = Rope(SCREEN_WIDTH // 2)
        self.active_skill = None
        self.skill_end_time = 0
        self.skill_cooldowns = {skill: 0 for skill in SKILLS}
        self.particles = []
        
    def create_particle(self, x, y, color):
        for _ in range(5):
            self.particles.append({
                'x': x,
                'y': y,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'color': color,
                'life': 1.0
            })
    
    def update_particles(self):
        self.particles = [p for p in self.particles if p['life'] > 0]
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 0.02
    
    def draw_particles(self, screen):
        for p in self.particles:
            alpha = int(p['life'] * 255)
            color = (*p['color'], alpha)
            pygame.draw.circle(screen, color, (int(p['x']), int(p['y'])), int(p['life'] * 8))
    
    def check_collision(self):
        player_center_x = self.player.x + self.player.width // 2
        player_center_y = self.player.y + self.player.height // 2
        
        rope_positions = self.rope.get_rope_position(player_center_x)
        if rope_positions is None:
            return False
        
        y1, y2 = rope_positions
        
        # 检查玩家是否碰到绳子
        rope_threshold = 20
        player_top = self.player.y
        player_bottom = self.player.y + self.player.height
        
        # 检查上半部分绳子
        if abs(y1 - player_bottom) < rope_threshold and y1 < self.rope.center_y:
            return True
        # 检查下半部分绳子
        if abs(y2 - player_top) < rope_threshold and y2 > self.rope.center_y:
            return True
        
        return False
    
    def draw_menu(self):
        self.screen.fill(WHITE)
        
        title_text = self.font.render('跳绳挑战', True, BLACK)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        
        y_offset = 220
        for i, diff in enumerate(DIFFICULTIES.keys()):
            color = RED if self.difficulty == diff else BLACK
            text = self.font.render(diff, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            
            # 难度说明
            desc = self.small_font.render(
                f"时间: {DIFFICULTIES[diff]['time_limit']}秒 | 速度: {DIFFICULTIES[diff]['rope_speed']}", 
                True, BLACK
            )
            self.screen.blit(desc, (SCREEN_WIDTH // 2 - desc.get_width() // 2, y_offset + 35))
            
            y_offset += 80
        
        start_text = self.font.render('按空格键开始', True, GREEN)
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 500))
        
        hint_text = self.small_font.render('使用 WASD 或 方向键 选择难度', True, BLACK)
        self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, 550))
    
    def draw_game(self):
        # 背景
        self.screen.fill((200, 255, 200))
        
        # 绘制地面
        pygame.draw.rect(self.screen, (139, 90, 43), (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))
        
        # 绘制绳子
        self.rope.draw(self.screen)
        
        # 绘制玩家
        self.player.draw(self.screen)
        
        # 绘制粒子
        self.draw_particles(self.screen)
        
        # 绘制UI
        # 分数
        score_text = self.font.render(f'分数: {self.score}', True, BLACK)
        self.screen.blit(score_text, (20, 20))
        
        # 连击
        combo_text = self.font.render(f'连击: {self.combo}', True, ORANGE if self.combo > 5 else BLACK)
        self.screen.blit(combo_text, (20, 60))
        
        # 时间
        time_color = RED if self.time_left <= 10 else BLACK
        time_text = self.font.render(f'时间: {self.time_left}s', True, time_color)
        self.screen.blit(time_text, (SCREEN_WIDTH - 200, 20))
        
        # 技能栏
        skill_y = SCREEN_HEIGHT - 80
        for i, (skill_id, skill) in enumerate(SKILLS.items()):
            x = 50 + i * 180
            now = pygame.time.get_ticks()
            
            if self.active_skill == skill_id:
                remaining = max(0, (self.skill_end_time - now) // 1000)
                pygame.draw.rect(self.screen, GREEN, (x, skill_y, 150, 40))
                text = self.small_font.render(f'{skill["name"]} ({remaining}s)', True, WHITE)
            elif now < self.skill_cooldowns[skill_id]:
                cooldown = (self.skill_cooldowns[skill_id] - now) // 1000
                pygame.draw.rect(self.screen, (100, 100, 100), (x, skill_y, 150, 40))
                text = self.small_font.render(f'冷却 {cooldown}s', True, WHITE)
            else:
                pygame.draw.rect(self.screen, BLUE, (x, skill_y, 150, 40))
                text = self.small_font.render(f'[{i+1}] {skill["name"]}', True, WHITE)
            
            self.screen.blit(text, (x + 5, skill_y + 5))
        
        # 慢动作效果
        if self.active_skill == 'slow_motion':
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(50)
            overlay.fill(BLUE)
            self.screen.blit(overlay, (0, 0))
    
    def draw_gameover(self):
        self.screen.fill(WHITE)
        
        gameover_text = self.font.render('游戏结束', True, RED)
        self.screen.blit(gameover_text, (SCREEN_WIDTH // 2 - gameover_text.get_width() // 2, 100))
        
        score_text = self.font.render(f'最终分数: {self.score}', True, BLACK)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 200))
        
        max_combo_text = self.font.render(f'最高连击: {self.max_combo}', True, ORANGE)
        self.screen.blit(max_combo_text, (SCREEN_WIDTH // 2 - max_combo_text.get_width() // 2, 260))
        
        difficulty_text = self.font.render(f'难度: {self.difficulty}', True, BLUE)
        self.screen.blit(difficulty_text, (SCREEN_WIDTH // 2 - difficulty_text.get_width() // 2, 320))
        
        restart_text = self.font.render('按 R 键重新开始', True, GREEN)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 420))
        
        menu_text = self.font.render('按 ESC 返回菜单', True, BLACK)
        self.screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, 480))
    
    def use_skill(self, skill_id):
        now = pygame.time.get_ticks()
        if self.active_skill is None and now >= self.skill_cooldowns[skill_id]:
            self.active_skill = skill_id
            self.skill_end_time = now + SKILLS[skill_id]['duration']
            self.skill_cooldowns[skill_id] = now + SKILLS[skill_id]['cooldown']
            self.sound_gen.play_sound(self.sound_gen.generate_skill_sound())
            self.create_particle(self.player.x + self.player.width // 2, 
                               self.player.y + self.player.height // 2, PURPLE)
    
    def run(self):
        while True:
            current_time = pygame.time.get_ticks()
            
            # 处理技能结束
            if self.active_skill and current_time >= self.skill_end_time:
                self.active_skill = None
            
            # 慢动作效果
            time_scale = 0.5 if self.active_skill == 'slow_motion' else 1.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == self.timer_event and self.game_state == 'playing':
                    self.time_left -= 1
                    if self.time_left <= 0:
                        self.game_state = 'gameover'
                
                if event.type == pygame.KEYDOWN:
                    if self.game_state == 'menu':
                        if event.key == pygame.K_SPACE:
                            self.reset_game()
                            self.game_state = 'playing'
                        elif event.key in (pygame.K_w, pygame.K_UP):
                            difficulties = list(DIFFICULTIES.keys())
                            idx = difficulties.index(self.difficulty)
                            self.difficulty = difficulties[(idx - 1) % len(difficulties)]
                        elif event.key in (pygame.K_s, pygame.K_DOWN):
                            difficulties = list(DIFFICULTIES.keys())
                            idx = difficulties.index(self.difficulty)
                            self.difficulty = difficulties[(idx + 1) % len(difficulties)]
                    
                    elif self.game_state == 'playing':
                        if event.key == pygame.K_SPACE:
                            self.player.jump()
                            self.sound_gen.play_sound(self.sound_gen.generate_jump_sound())
                        
                        # 技能按键
                        if event.key == pygame.K_1:
                            self.use_skill('slow_motion')
                        elif event.key == pygame.K_2:
                            self.use_skill('double_score')
                        elif event.key == pygame.K_3:
                            self.use_skill('magnet')
                    
                    elif self.game_state == 'gameover':
                        if event.key == pygame.K_r:
                            self.reset_game()
                            self.game_state = 'playing'
                        elif event.key == pygame.K_ESCAPE:
                            self.game_state = 'menu'
            
            if self.game_state == 'playing':
                # 更新游戏对象
                self.player.update()
                self.rope.update()
                
                # 检查碰撞
                if self.check_collision():
                    # 检查是否成功跳过
                    if self.player.is_jumping:
                        # 成功跳过
                        base_score = DIFFICULTIES[self.difficulty]['base_score']
                        combo_multiplier = 1 + self.combo * 0.1
                        
                        if self.active_skill == 'double_score':
                            points = int(base_score * combo_multiplier * 2)
                        else:
                            points = int(base_score * combo_multiplier)
                        
                        self.score += points
                        self.combo += 1
                        self.max_combo = max(self.max_combo, self.combo)
                        
                        self.sound_gen.play_sound(self.sound_gen.generate_score_sound())
                        self.create_particle(self.player.x + self.player.width // 2, 
                                           self.player.y, GREEN)
                        
                        # 连击奖励
                        if self.combo >= 10:
                            self.sound_gen.play_sound(self.sound_gen.generate_combo_sound())
                    else:
                        # 失败
                        self.combo = 0
                        self.sound_gen.play_sound(self.sound_gen.generate_fail_sound())
                        self.create_particle(self.player.x + self.player.width // 2, 
                                           self.player.y + self.player.height // 2, RED)
                
                self.update_particles()
            
            # 绘制
            if self.game_state == 'menu':
                self.draw_menu()
            elif self.game_state == 'playing':
                self.draw_game()
            elif self.game_state == 'gameover':
                self.draw_gameover()
            
            pygame.display.flip()
            self.clock.tick(FPS * time_scale)

if __name__ == '__main__':
    game = Game()
    game.run()