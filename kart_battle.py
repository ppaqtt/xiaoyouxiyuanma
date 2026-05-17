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

# 游戏配置
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
clock = pygame.time.Clock()

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# 道具类型
ITEM_TYPES = {
    'speed': {'color': YELLOW, 'name': '加速', 'symbol': '⚡'},
    'missile': {'color': RED, 'name': '导弹', 'symbol': '🚀'},
    'shield': {'color': CYAN, 'name': '护盾', 'symbol': '🛡️'},
    'mine': {'color': PURPLE, 'name': '地雷', 'symbol': '💣'}
}

# 音效生成
def generate_sound(frequency, duration, volume=0.5, sample_rate=44100):
    samples = int(sample_rate * duration)
    sound_data = bytearray()
    
    for i in range(samples):
        t = i / sample_rate
        value = int(volume * 32767 * math.sin(2 * math.pi * frequency * t))
        sound_data.extend(struct.pack('<h', value))
    
    return pygame.mixer.Sound(sound_data)

# 预生成音效
class SoundManager:
    def __init__(self):
        self.item_pickup = generate_sound(880, 0.2)
        self.speed_boost = generate_sound(1200, 0.5, 0.3)
        self.missile_fire = generate_sound(440, 0.3)
        self.missile_hit = generate_sound(220, 0.4, 0.4)
        self.shield_activate = generate_sound(660, 0.3, 0.3)
        self.mine_place = generate_sound(330, 0.2, 0.3)
        self.mine_explode = generate_sound(165, 0.5, 0.5)
        self.game_start = generate_sound(523, 0.3)
        self.game_over = generate_sound(392, 0.5)
        self.lap_complete = generate_sound(659, 0.3)
    
    def play(self, sound_name):
        if hasattr(self, sound_name):
            getattr(self, sound_name).play()

# 赛道类
class Track:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.checkpoints = []
        self.item_spawn_points = []
        self.start_points = []
        
    def generate_track(self):
        self.checkpoints = []
        self.item_spawn_points = []
        self.start_points = []
        
        if self.name == '森林赛道':
            # 森林赛道 - 环形路线
            cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
            r = 250
            for i in range(8):
                angle = i * (math.pi / 4)
                self.checkpoints.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
            
            for i in range(6):
                angle = i * (math.pi / 3)
                self.item_spawn_points.append((cx + (r - 80) * math.cos(angle), cy + (r - 80) * math.sin(angle)))
            
            self.start_points = [(cx - 50, cy - r), (cx + 50, cy - r)]
            
        elif self.name == '沙漠赛道':
            # 沙漠赛道 - 直线加弯道
            self.checkpoints = [
                (100, 400), (300, 200), (600, 150), 
                (900, 200), (1100, 400), (900, 600),
                (600, 650), (300, 600)
            ]
            self.item_spawn_points = [
                (200, 300), (450, 175), (750, 175),
                (1000, 500), (750, 625), (450, 625), (200, 500)
            ]
            self.start_points = [(100, 380), (100, 420)]
            
        elif self.name == '城市赛道':
            # 城市赛道 - 矩形路线
            self.checkpoints = [
                (150, 150), (1050, 150), (1050, 650),
                (150, 650), (350, 350), (850, 350)
            ]
            self.item_spawn_points = [
                (350, 150), (650, 150), (950, 150),
                (1050, 350), (1050, 550), (850, 650),
                (550, 650), (250, 650), (150, 450), (150, 250)
            ]
            self.start_points = [(150, 130), (150, 170)]

# 道具类
class Item:
    def __init__(self, x, y, item_type=None):
        self.x = x
        self.y = y
        self.item_type = item_type if item_type else random.choice(list(ITEM_TYPES.keys()))
        self.radius = 15
        self.pulse = 0
        self.active = True
        
    def update(self):
        self.pulse = (self.pulse + 0.1) % (2 * math.pi)
        
    def draw(self, screen):
        scale = 1 + math.sin(self.pulse) * 0.1
        color = ITEM_TYPES[self.item_type]['color']
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.radius * scale))
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), int(self.radius * scale), 2)
        
        font = get_chinese_font(20)
        text = font.render(ITEM_TYPES[self.item_type]['symbol'], True, BLACK)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

# 地雷类
class Mine:
    def __init__(self, x, y, owner):
        self.x = x
        self.y = y
        self.owner = owner
        self.radius = 12
        self.timer = 180  # 3秒后自动消失
        self.active = True
        
    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.active = False
        
    def draw(self, screen):
        pygame.draw.circle(screen, PURPLE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        font = get_chinese_font(16)
        text = font.render('💣', True, BLACK)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

# 导弹类
class Missile:
    def __init__(self, x, y, angle, owner):
        self.x = x
        self.y = y
        self.angle = angle
        self.owner = owner
        self.speed = 12
        self.radius = 10
        self.active = True
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        if self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT:
            self.active = False
            
    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        
        # 导弹尾焰
        tail_x = self.x - math.cos(self.angle) * 15
        tail_y = self.y - math.sin(self.angle) * 15
        pygame.draw.circle(screen, ORANGE, (int(tail_x), int(tail_y)), 8)
        pygame.draw.circle(screen, YELLOW, (int(tail_x), int(tail_y)), 4)

# 卡丁车类
class Kart:
    def __init__(self, x, y, color, player_num, is_ai=False):
        self.x = x
        self.y = y
        self.color = color
        self.player_num = player_num
        self.is_ai = is_ai
        
        self.angle = -math.pi / 2  # 向上
        self.speed = 0
        self.max_speed = 8
        self.acceleration = 0.3
        self.deceleration = 0.15
        self.turn_speed = 0.05
        
        self.item = None
        self.shield_active = False
        self.shield_timer = 0
        self.speed_boost_active = False
        self.speed_boost_timer = 0
        
        self.current_checkpoint = 0
        self.laps = 0
        self.total_laps = 3
        
        self.rect = pygame.Rect(x - 20, y - 20, 40, 40)
        
        # AI相关
        self.ai_target_checkpoint = 0
        self.ai_random_time = 0
        
    def update(self, keys=None, track=None, other_karts=None):
        if not self.is_ai:
            # 玩家控制
            if keys[pygame.K_UP]:
                self.speed = min(self.speed + self.acceleration, self.max_speed)
            elif keys[pygame.K_DOWN]:
                self.speed = max(self.speed - self.acceleration, -self.max_speed / 2)
            else:
                if self.speed > 0:
                    self.speed = max(self.speed - self.deceleration, 0)
                elif self.speed < 0:
                    self.speed = min(self.speed + self.deceleration, 0)
            
            if keys[pygame.K_LEFT] and self.speed != 0:
                self.angle -= self.turn_speed * (self.speed / self.max_speed)
            if keys[pygame.K_RIGHT] and self.speed != 0:
                self.angle += self.turn_speed * (self.speed / self.max_speed)
        else:
            # AI控制
            self.ai_update(track, other_karts)
        
        # 应用加速效果
        actual_speed = self.speed
        if self.speed_boost_active:
            actual_speed *= 1.8
            self.speed_boost_timer -= 1
            if self.speed_boost_timer <= 0:
                self.speed_boost_active = False
        
        # 更新位置
        self.x += math.cos(self.angle) * actual_speed
        self.y += math.sin(self.angle) * actual_speed
        
        # 更新护盾
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
        
        # 边界限制
        self.x = max(20, min(self.x, SCREEN_WIDTH - 20))
        self.y = max(20, min(self.y, SCREEN_HEIGHT - 20))
        
        # 更新碰撞盒
        self.rect.center = (self.x, self.y)
        
    def ai_update(self, track, other_karts):
        if track and track.checkpoints:
            # AI目标选择
            target_x, target_y = track.checkpoints[self.ai_target_checkpoint]
            
            # 计算到目标的方向
            dx = target_x - self.x
            dy = target_y - self.y
            target_angle = math.atan2(dy, dx)
            
            # 转向目标
            angle_diff = target_angle - self.angle
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            if abs(angle_diff) > 0.1:
                self.angle += angle_diff * 0.03
            
            # 加速向目标前进
            self.speed = min(self.speed + self.acceleration * 0.5, self.max_speed * 0.8)
            
            # 随机改变行为
            self.ai_random_time -= 1
            if self.ai_random_time <= 0:
                self.ai_random_time = random.randint(120, 300)
                # 随机使用道具
                if self.item and random.random() < 0.3:
                    self.use_item(other_karts)
            
            # 检查是否到达 checkpoint
            dist_to_checkpoint = math.hypot(dx, dy)
            if dist_to_checkpoint < 50:
                self.ai_target_checkpoint = (self.ai_target_checkpoint + 1) % len(track.checkpoints)
    
    def use_item(self, other_karts):
        if not self.item:
            return
        
        if self.item == 'speed':
            self.speed_boost_active = True
            self.speed_boost_timer = 180  # 3秒
            self.item = None
            return True
            
        elif self.item == 'shield':
            self.shield_active = True
            self.shield_timer = 240  # 4秒
            self.item = None
            return True
            
        elif self.item == 'mine':
            # 在当前位置放置地雷
            return 'place_mine'
            
        elif self.item == 'missile':
            # 发射导弹
            if other_karts:
                # 找到最近的对手
                nearest_kart = None
                min_dist = float('inf')
                for kart in other_karts:
                    if kart != self and not kart.is_ai:
                        dist = math.hypot(kart.x - self.x, kart.y - self.y)
                        if dist < min_dist:
                            min_dist = dist
                            nearest_kart = kart
                
                if nearest_kart:
                    angle_to_target = math.atan2(nearest_kart.y - self.y, nearest_kart.x - self.x)
                    self.item = None
                    return ('missile', angle_to_target)
            return None
        
        return False
    
    def draw(self, screen):
        # 绘制卡丁车主体
        pygame.draw.polygon(screen, self.color, [
            (self.x, self.y - 20),
            (self.x - 15, self.y + 15),
            (self.x + 15, self.y + 15)
        ])
        
        # 绘制轮子
        pygame.draw.circle(screen, BLACK, (self.x - 10, self.y + 12), 6)
        pygame.draw.circle(screen, BLACK, (self.x + 10, self.y + 12), 6)
        
        # 绘制护盾
        if self.shield_active:
            pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), 35, 3)
            pygame.draw.circle(screen, (0, 255, 255, 50), (int(self.x), int(self.y)), 35)
        
        # 绘制加速效果
        if self.speed_boost_active:
            for i in range(3):
                offset = i * 8
                tail_x = self.x - math.cos(self.angle) * (25 + offset)
                tail_y = self.y - math.sin(self.angle) * (25 + offset)
                pygame.draw.circle(screen, YELLOW, (int(tail_x), int(tail_y)), 6 - i)
        
        # 绘制玩家编号
        font = get_chinese_font(20)
        text = font.render(str(self.player_num), True, WHITE)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

# 游戏主类
class KartBattleGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('卡丁车道具赛')
        
        self.sound_manager = SoundManager()
        self.tracks = [
            Track('森林赛道', 'forest'),
            Track('沙漠赛道', 'desert'),
            Track('城市赛道', 'city')
        ]
        
        self.current_track = 0
        self.game_mode = 'menu'  # menu, single, multi
        self.selected_track = 0
        
        self.karts = []
        self.items = []
        self.mines = []
        self.missiles = []
        
        self.winner = None
        self.countdown = 0
        
    def reset_game(self):
        track = self.tracks[self.current_track]
        track.generate_track()
        
        self.karts = []
        self.items = []
        self.mines = []
        self.missiles = []
        self.winner = None
        self.countdown = 3
        
        if self.game_mode == 'single':
            # 玩家 + AI
            self.karts.append(Kart(track.start_points[0][0], track.start_points[0][1], BLUE, 1, is_ai=False))
            self.karts.append(Kart(track.start_points[1][0], track.start_points[1][1], RED, 2, is_ai=True))
        else:
            # 双人模式
            self.karts.append(Kart(track.start_points[0][0], track.start_points[0][1], BLUE, 1, is_ai=False))
            self.karts.append(Kart(track.start_points[1][0], track.start_points[1][1], RED, 2, is_ai=False))
        
        # 生成道具
        for point in track.item_spawn_points:
            self.items.append(Item(point[0], point[1]))
        
        self.sound_manager.play('game_start')
    
    def handle_collisions(self):
        track = self.tracks[self.current_track]
        
        for kart in self.karts:
            # 检查道具拾取
            for item in self.items[:]:
                if item.active:
                    dist = math.hypot(kart.x - item.x, kart.y - item.y)
                    if dist < kart.rect.width / 2 + item.radius:
                        kart.item = item.item_type
                        item.active = False
                        self.items.remove(item)
                        self.sound_manager.play('item_pickup')
                        
                        # 补充新道具
                        if track.item_spawn_points:
                            spawn_point = random.choice(track.item_spawn_points)
                            self.items.append(Item(spawn_point[0], spawn_point[1]))
            
            # 检查地雷碰撞
            for mine in self.mines[:]:
                if mine.active and mine.owner != kart:
                    dist = math.hypot(kart.x - mine.x, kart.y - mine.y)
                    if dist < kart.rect.width / 2 + mine.radius:
                        # 地雷爆炸
                        mine.active = False
                        self.mines.remove(mine)
                        self.sound_manager.play('mine_explode')
                        
                        if kart.shield_active:
                            kart.shield_active = False
                            kart.shield_timer = 0
                        else:
                            kart.speed = -kart.max_speed / 2
                            kart.x -= math.cos(kart.angle) * 50
                            kart.y -= math.sin(kart.angle) * 50
            
            # 检查导弹碰撞
            for missile in self.missiles[:]:
                if missile.active and missile.owner != kart:
                    dist = math.hypot(kart.x - missile.x, kart.y - missile.y)
                    if dist < kart.rect.width / 2 + missile.radius:
                        missile.active = False
                        self.missiles.remove(missile)
                        self.sound_manager.play('missile_hit')
                        
                        if kart.shield_active:
                            kart.shield_active = False
                            kart.shield_timer = 0
                        else:
                            kart.speed = -kart.max_speed
                            kart.x -= math.cos(kart.angle) * 80
                            kart.y -= math.sin(kart.angle) * 80
            
            # 检查 checkpoint
            if track.checkpoints:
                checkpoint = track.checkpoints[kart.current_checkpoint]
                dist = math.hypot(kart.x - checkpoint[0], kart.y - checkpoint[1])
                if dist < 40:
                    kart.current_checkpoint = (kart.current_checkpoint + 1) % len(track.checkpoints)
                    if kart.current_checkpoint == 0:
                        kart.laps += 1
                        self.sound_manager.play('lap_complete')
                        
                        # 检查是否获胜
                        if kart.laps >= kart.total_laps:
                            self.winner = kart
                            self.sound_manager.play('game_over')
    
    def draw_track(self):
        track = self.tracks[self.current_track]
        screen = self.screen
        
        # 背景
        if track.name == '森林赛道':
            screen.fill(GREEN)
            # 绘制树木
            for i in range(20):
                tx = random.randint(0, SCREEN_WIDTH)
                ty = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.polygon(screen, (34, 139, 34), [
                    (tx, ty - 30), (tx - 15, ty), (tx + 15, ty)
                ])
                pygame.draw.rect(screen, (139, 90, 43), (tx - 5, ty, 10, 15))
                
        elif track.name == '沙漠赛道':
            screen.fill((244, 164, 96))
            # 绘制沙丘
            for i in range(15):
                sx = random.randint(0, SCREEN_WIDTH)
                sy = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.ellipse(screen, (210, 105, 30), (sx - 30, sy, 60, 25))
                
        elif track.name == '城市赛道':
            screen.fill((100, 100, 100))
            # 绘制建筑物
            for i in range(8):
                bx = random.randint(50, SCREEN_WIDTH - 50)
                by = random.randint(50, SCREEN_HEIGHT - 50)
                bw = random.randint(40, 80)
                bh = random.randint(60, 120)
                pygame.draw.rect(screen, (150, 150, 150), (bx, by - bh, bw, bh))
                for j in range(3):
                    for k in range(4):
                        pygame.draw.rect(screen, BLUE, (bx + 5 + j * 15, by - bh + 10 + k * 20, 10, 15))
        
        # 绘制赛道
        if track.checkpoints:
            pygame.draw.lines(screen, (100, 100, 100), True, track.checkpoints, 100)
            pygame.draw.lines(screen, WHITE, True, track.checkpoints, 5)
            
            # 绘制起点线
            start_idx = 0
            start_x, start_y = track.checkpoints[start_idx]
            next_x, next_y = track.checkpoints[(start_idx + 1) % len(track.checkpoints)]
            angle = math.atan2(next_y - start_y, next_x - start_x)
            
            perp_angle = angle + math.pi / 2
            for i in range(20):
                offset = (i - 10) * 8
                x1 = start_x + math.cos(perp_angle) * offset
                y1 = start_y + math.sin(perp_angle) * offset
                x2 = x1 + math.cos(angle) * 10
                y2 = y1 + math.sin(angle) * 10
                
                if i % 2 == 0:
                    pygame.draw.line(screen, WHITE, (x1, y1), (x2, y2), 3)
                else:
                    pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), 3)
        
        # 绘制 checkpoint 标记
        for i, (cx, cy) in enumerate(track.checkpoints):
            pygame.draw.circle(screen, YELLOW, (int(cx), int(cy)), 20)
            pygame.draw.circle(screen, BLACK, (int(cx), int(cy)), 15)
            font = get_chinese_font(20)
            text = font.render(str(i + 1), True, WHITE)
            text_rect = text.get_rect(center=(cx, cy))
            screen.blit(text, text_rect)
    
    def draw_ui(self):
        screen = self.screen
        font = get_chinese_font(28)
        
        # 显示玩家信息
        for i, kart in enumerate(self.karts):
            y_pos = 20 + i * 40
            
            # 玩家颜色标记
            pygame.draw.rect(screen, kart.color, (20, y_pos, 20, 20))
            
            # 玩家编号和圈数
            text = font.render(f'玩家 {kart.player_num}: {kart.laps}/{kart.total_laps} 圈', True, WHITE)
            screen.blit(text, (50, y_pos))
            
            # 道具显示
            if kart.item:
                item_info = ITEM_TYPES[kart.item]
                item_text = font.render(f'道具: {item_info["symbol"]} {item_info["name"]}', True, WHITE)
                screen.blit(item_text, (250, y_pos))
            
            # 状态效果
            status_text = ''
            if kart.shield_active:
                status_text += '🛡️'
            if kart.speed_boost_active:
                status_text += '⚡'
            if status_text:
                status = font.render(status_text, True, WHITE)
                screen.blit(status, (450, y_pos))
        
        # 赛道名称
        track_name = font.render(f'赛道: {self.tracks[self.current_track].name}', True, WHITE)
        screen.blit(track_name, (SCREEN_WIDTH - 200, 20))
        
        # 倒计时显示
        if self.countdown > 0:
            big_font = get_chinese_font(120)
            countdown_text = big_font.render(str(self.countdown), True, RED)
            text_rect = countdown_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(countdown_text, text_rect)
            
            ready_text = font.render('准备开始!', True, WHITE)
            ready_rect = ready_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            screen.blit(ready_text, ready_rect)
        
        # 获胜显示
        if self.winner:
            big_font = get_chinese_font(80)
            winner_text = big_font.render(f'🎉 玩家 {self.winner.player_num} 获胜!', True, YELLOW)
            text_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(winner_text, text_rect)
            
            small_font = get_chinese_font(36)
            restart_text = small_font.render('按 R 键重新开始，按 ESC 返回菜单', True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            screen.blit(restart_text, restart_rect)
    
    def show_main_menu(self):
        screen = self.screen
        screen.fill(BLACK)
        
        # 标题
        title_font = get_chinese_font(80)
        title = title_font.render('卡丁车道具赛', True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title, title_rect)
        
        # 菜单选项
        menu_font = get_chinese_font(48)
        options = ['单人模式', '双人模式', '选择赛道', '退出游戏']
        
        for i, option in enumerate(options):
            y_pos = 300 + i * 80
            text = menu_font.render(option, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            
            if i == self.menu_selected:
                pygame.draw.rect(screen, BLUE, (text_rect.left - 20, text_rect.top - 10, text_rect.width + 40, text_rect.height + 20))
                text = menu_font.render(option, True, YELLOW)
            
            screen.blit(text, text_rect)
        
        # 道具说明
        info_font = get_chinese_font(28)
        item_examples = [
            ('⚡ 加速', '提升速度'),
            ('🚀 导弹', '攻击对手'),
            ('🛡️ 护盾', '保护自己'),
            ('💣 地雷', '放置陷阱')
        ]
        
        for i, (symbol, desc) in enumerate(item_examples):
            x_pos = 100 + i * 250
            y_pos = SCREEN_HEIGHT - 100
            text = info_font.render(f'{symbol}: {desc}', True, WHITE)
            screen.blit(text, (x_pos, y_pos))
        
        pygame.display.flip()
    
    def show_track_select(self):
        screen = self.screen
        screen.fill(BLACK)
        
        title_font = get_chinese_font(60)
        title = title_font.render('选择赛道', True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)
        
        track_font = get_chinese_font(48)
        for i, track in enumerate(self.tracks):
            y_pos = 250 + i * 100
            text = track_font.render(track.name, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            
            if i == self.selected_track:
                pygame.draw.rect(screen, BLUE, (text_rect.left - 20, text_rect.top - 10, text_rect.width + 40, text_rect.height + 20))
                text = track_font.render(track.name, True, YELLOW)
            
            screen.blit(text, text_rect)
        
        back_font = get_chinese_font(36)
        back_text = back_font.render('按 ESC 返回', True, WHITE)
        screen.blit(back_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 50))
        
        pygame.display.flip()
    
    def run(self):
        self.menu_selected = 0
        keys_held = {pygame.K_UP: False, pygame.K_DOWN: False}
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if self.game_mode == 'menu':
                        if event.key == pygame.K_UP and not keys_held[pygame.K_UP]:
                            self.menu_selected = (self.menu_selected - 1) % 4
                            keys_held[pygame.K_UP] = True
                        if event.key == pygame.K_DOWN and not keys_held[pygame.K_DOWN]:
                            self.menu_selected = (self.menu_selected + 1) % 4
                            keys_held[pygame.K_DOWN] = True
                        if event.key == pygame.K_RETURN:
                            if self.menu_selected == 0:
                                self.game_mode = 'single'
                                self.current_track = self.selected_track
                                self.reset_game()
                            elif self.menu_selected == 1:
                                self.game_mode = 'multi'
                                self.current_track = self.selected_track
                                self.reset_game()
                            elif self.menu_selected == 2:
                                self.game_mode = 'track_select'
                            elif self.menu_selected == 3:
                                pygame.quit()
                                sys.exit()
                    
                    elif self.game_mode == 'track_select':
                        if event.key == pygame.K_ESCAPE:
                            self.game_mode = 'menu'
                        if event.key == pygame.K_UP:
                            self.selected_track = (self.selected_track - 1) % len(self.tracks)
                        if event.key == pygame.K_DOWN:
                            self.selected_track = (self.selected_track + 1) % len(self.tracks)
                        if event.key == pygame.K_RETURN:
                            self.game_mode = 'menu'
                    
                    elif self.game_mode in ['single', 'multi']:
                        if self.winner:
                            if event.key == pygame.K_r:
                                self.reset_game()
                            elif event.key == pygame.K_ESCAPE:
                                self.game_mode = 'menu'
                        else:
                            if event.key == pygame.K_SPACE:
                                for kart in self.karts:
                                    if not kart.is_ai:
                                        result = kart.use_item(self.karts)
                                        if result == 'place_mine':
                                            self.mines.append(Mine(kart.x, kart.y, kart))
                                            kart.item = None
                                            self.sound_manager.play('mine_place')
                                        elif isinstance(result, tuple) and result[0] == 'missile':
                                            self.missiles.append(Missile(kart.x, kart.y, result[1], kart))
                                            self.sound_manager.play('missile_fire')
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        keys_held[pygame.K_UP] = False
                    if event.key == pygame.K_DOWN:
                        keys_held[pygame.K_DOWN] = False
            
            if self.game_mode == 'menu':
                self.show_main_menu()
            elif self.game_mode == 'track_select':
                self.show_track_select()
            elif self.game_mode in ['single', 'multi']:
                # 游戏主循环
                keys = pygame.key.get_pressed()
                
                # 倒计时
                if self.countdown > 0:
                    self.countdown -= 1
                    if self.countdown == 0:
                        self.sound_manager.play('game_start')
                
                # 更新游戏状态
                if self.countdown == 0 and not self.winner:
                    # 更新卡丁车
                    for kart in self.karts:
                        if kart.player_num == 1 or (self.game_mode == 'multi' and kart.player_num == 2):
                            kart.update(keys=keys, track=self.tracks[self.current_track], other_karts=self.karts)
                        else:
                            kart.update(keys=None, track=self.tracks[self.current_track], other_karts=self.karts)
                    
                    # 更新道具
                    for item in self.items:
                        item.update()
                    
                    # 更新地雷
                    for mine in self.mines[:]:
                        mine.update()
                        if not mine.active:
                            self.mines.remove(mine)
                    
                    # 更新导弹
                    for missile in self.missiles[:]:
                        missile.update()
                        if not missile.active:
                            self.missiles.remove(missile)
                    
                    # 处理碰撞
                    self.handle_collisions()
                
                # 绘制
                self.draw_track()
                
                # 绘制道具
                for item in self.items:
                    if item.active:
                        item.draw(self.screen)
                
                # 绘制地雷
                for mine in self.mines:
                    if mine.active:
                        mine.draw(self.screen)
                
                # 绘制导弹
                for missile in self.missiles:
                    if missile.active:
                        missile.draw(self.screen)
                
                # 绘制卡丁车
                for kart in self.karts:
                    kart.draw(self.screen)
                
                # 绘制UI
                self.draw_ui()
                
                pygame.display.flip()
            
            clock.tick(FPS)

if __name__ == '__main__':
    game = KartBattleGame()
    game.run()