
import pygame
import os
import sys
import random
import math

# 初始化pygame
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
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 182, 193)
PURPLE = (147, 112, 219)
GOLD = (255, 215, 0)
BLUE = (135, 206, 235)
GREEN = (144, 238, 144)
RED = (255, 99, 71)
YELLOW = (255, 255, 0)

# 字体
FONT_SMALL = get_chinese_font(24)
FONT_MEDIUM = get_chinese_font(32)
FONT_LARGE = get_chinese_font(48)

# 创建屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('偶像养成计划')

# 音效系统
class SoundSystem:
    def __init__(self):
        self.audio_enabled = True
        try:
            pygame.mixer.init()
            self.sounds = {}
        except pygame.error:
            self.audio_enabled = False
            self.sounds = {}
    
    def generate_sound(self, frequency, duration, volume=0.5):
        if not self.audio_enabled:
            return None
        sample_rate = 44100
        samples = int(sample_rate * duration)
        arr = bytearray(samples * 2)
        
        for i in range(samples):
            t = float(i) / sample_rate
            value = int(math.sin(2 * math.pi * frequency * t) * 32767)
            arr[i * 2] = value & 0xFF
            arr[i * 2 + 1] = (value >> 8) & 0xFF
        
        sound = pygame.mixer.Sound(arr)
        sound.set_volume(volume)
        return sound
    
    def play_success(self):
        if not self.audio_enabled:
            return
        sound = self.generate_sound(523, 0.1)
        if sound:
            sound.play()
    
    def play_fail(self):
        if not self.audio_enabled:
            return
        sound = self.generate_sound(200, 0.2)
        if sound:
            sound.play()
    
    def play_levelup(self):
        if not self.audio_enabled:
            return
        sound1 = self.generate_sound(523, 0.1)
        sound2 = self.generate_sound(659, 0.1)
        sound3 = self.generate_sound(784, 0.15)
        if sound1:
            sound1.play()
            pygame.time.delay(100)
        if sound2:
            sound2.play()
            pygame.time.delay(100)
        if sound3:
            sound3.play()

# 游戏数据
class IdolGame:
    def __init__(self):
        self.sound_system = SoundSystem()
        
        # 角色属性
        self.singing = 20      # 唱歌
        self.dancing = 20      # 跳舞
        self.beauty = 20       # 颜值
        self.popularity = 0    # 人气（粉丝数）
        
        # 状态
        self.day = 1
        self.energy = 100
        self.max_energy = 100
        self.fame = 0          # 知名度
        self.money = 1000
        
        # 游戏状态
        self.game_over = False
        self.game_won = False
        self.current_screen = 'main'  # main, training, event, performance, result
        
        # 事件日志
        self.logs = []
        
        # 随机事件列表
        self.events = [
            {"text": "在街上被星探发现！颜值+5", "effect": {"beauty": 5}},
            {"text": "参加公益活动，人气+100", "effect": {"popularity": 100}},
            {"text": "练习时受伤，体力-20", "effect": {"energy": -20}},
            {"text": "获得舞蹈大师指导，跳舞+8", "effect": {"dancing": 8}},
            {"text": "歌唱比赛获奖，唱歌+10", "effect": {"singing": 10}},
            {"text": "社交媒体爆火，粉丝+500", "effect": {"popularity": 500}},
            {"text": "感冒了，体力-30", "effect": {"energy": -30}},
            {"text": "时尚杂志拍摄，颜值+10", "effect": {"beauty": 10}},
            {"text": "粉丝见面会成功，人气+200", "effect": {"popularity": 200}},
            {"text": "新歌发布，唱歌+5，粉丝+300", "effect": {"singing": 5, "popularity": 300}},
        ]
    
    def add_log(self, text):
        self.logs.insert(0, text)
        if len(self.logs) > 5:
            self.logs.pop()
    
    def train_singing(self):
        if self.energy < 20:
            self.add_log("体力不足，无法训练！")
            self.sound_system.play_fail()
            return
        self.energy -= 20
        gain = random.randint(3, 7)
        self.singing += gain
        self.add_log(f"唱歌训练完成！唱歌+{gain}")
        self.sound_system.play_success()
    
    def train_dancing(self):
        if self.energy < 25:
            self.add_log("体力不足，无法训练！")
            self.sound_system.play_fail()
            return
        self.energy -= 25
        gain = random.randint(3, 7)
        self.dancing += gain
        self.add_log(f"舞蹈训练完成！跳舞+{gain}")
        self.sound_system.play_success()
    
    def train_fitness(self):
        if self.energy < 20:
            self.add_log("体力不足，无法训练！")
            self.sound_system.play_fail()
            return
        self.energy -= 20
        gain = random.randint(2, 6)
        self.beauty += gain
        self.add_log(f"健身完成！颜值+{gain}")
        self.sound_system.play_success()
    
    def rest(self):
        recover = random.randint(30, 50)
        self.energy = min(self.max_energy, self.energy + recover)
        self.add_log(f"休息恢复！体力+{recover}")
        self.sound_system.play_success()
    
    def perform(self):
        if self.energy < 30:
            self.add_log("体力不足，无法演出！")
            self.sound_system.play_fail()
            return
        
        self.energy -= 30
        
        # 计算演出效果
        total = self.singing + self.dancing + self.beauty
        base_fans = int(total * 2)
        bonus = random.randint(-50, 100)
        fans_gained = max(0, base_fans + bonus)
        
        self.popularity += fans_gained
        self.fame += 5
        
        if fans_gained > 100:
            self.add_log(f"演出大成功！粉丝+{fans_gained}")
            self.sound_system.play_levelup()
        else:
            self.add_log(f"演出完成！粉丝+{fans_gained}")
            self.sound_system.play_success()
    
    def check_game_end(self):
        if self.popularity >= 10000:
            self.game_won = True
            self.game_over = True
            return True
        if self.day > 30:
            if self.popularity >= 5000:
                self.game_won = True
            self.game_over = True
            return True
        return False
    
    def next_day(self):
        self.day += 1
        self.energy = self.max_energy
        
        # 每日随机事件
        if random.random() < 0.3:
            event = random.choice(self.events)
            self.add_log(f"【随机事件】{event['text']}")
            for attr, value in event['effect'].items():
                if attr == 'energy':
                    self.energy = max(0, min(self.max_energy, self.energy + value))
                elif attr == 'popularity':
                    self.popularity += value
                elif attr == 'singing':
                    self.singing += value
                elif attr == 'dancing':
                    self.dancing += value
                elif attr == 'beauty':
                    self.beauty += value
            self.sound_system.play_success()
        
        return self.check_game_end()

# UI组件
def draw_button(text, x, y, width, height, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, hover_color, (x, y, width, height))
        if click[0] == 1 and action:
            pygame.time.delay(200)
            action()
    else:
        pygame.draw.rect(screen, color, (x, y, width, height))
    
    text_surface = FONT_MEDIUM.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.center = (x + width/2, y + height/2)
    screen.blit(text_surface, text_rect)

def draw_stat_bar(x, y, width, height, value, max_value, label, color):
    # 绘制标签
    label_surface = FONT_SMALL.render(label, True, BLACK)
    screen.blit(label_surface, (x, y - 20))
    
    # 绘制背景
    pygame.draw.rect(screen, (200, 200, 200), (x, y, width, height))
    
    # 绘制进度
    fill_width = int(width * (value / max_value))
    pygame.draw.rect(screen, color, (x, y, fill_width, height))
    
    # 绘制数值
    value_surface = FONT_SMALL.render(f"{value}", True, BLACK)
    screen.blit(value_surface, (x + width + 10, y))

def draw_main_screen(game):
    screen.fill(PINK)
    
    # 标题
    title_surface = FONT_LARGE.render('偶像养成计划', True, PURPLE)
    screen.blit(title_surface, (SCREEN_WIDTH//2 - title_surface.get_width()//2, 50))
    
    # 状态面板
    pygame.draw.rect(screen, WHITE, (50, 150, 300, 350), border_radius=10)
    
    # 头像区域
    pygame.draw.circle(screen, BLUE, (200, 220), 60)
    pygame.draw.circle(screen, WHITE, (200, 220), 56)
    star_surface = FONT_LARGE.render('★', True, GOLD)
    screen.blit(star_surface, (185, 205))
    
    # 状态信息
    info_y = 300
    screen.blit(FONT_MEDIUM.render(f"第 {game.day} 天", True, BLACK), (80, info_y))
    screen.blit(FONT_MEDIUM.render(f"粉丝: {game.popularity}", True, BLACK), (80, info_y + 30))
    screen.blit(FONT_MEDIUM.render(f"知名度: {game.fame}", True, BLACK), (80, info_y + 60))
    screen.blit(FONT_MEDIUM.render(f"体力: {game.energy}/{game.max_energy}", True, BLACK), (80, info_y + 90))
    
    # 属性面板
    pygame.draw.rect(screen, WHITE, (400, 150, 350, 350), border_radius=10)
    
    y_offset = 180
    draw_stat_bar(430, y_offset, 280, 25, game.singing, 100, "唱歌", RED)
    draw_stat_bar(430, y_offset + 40, 280, 25, game.dancing, 100, "跳舞", BLUE)
    draw_stat_bar(430, y_offset + 80, 280, 25, game.beauty, 100, "颜值", PURPLE)
    draw_stat_bar(430, y_offset + 120, 280, 25, game.popularity, 10000, "人气", GOLD)
    
    # 操作按钮
    btn_y = 520
    draw_button("唱歌训练", 50, btn_y, 150, 40, GREEN, (100, 200, 100), game.train_singing)
    draw_button("舞蹈训练", 220, btn_y, 150, 40, BLUE, (100, 150, 200), game.train_dancing)
    draw_button("健身", 390, btn_y, 150, 40, PURPLE, (150, 100, 200), game.train_fitness)
    draw_button("休息", 560, btn_y, 150, 40, YELLOW, (200, 200, 100), game.rest)
    draw_button("演出", 730, btn_y, 150, 40, RED, (200, 100, 100), game.perform)
    
    # 事件日志
    pygame.draw.rect(screen, WHITE, (50, 520, 350, 60), border_radius=5)
    for i, log in enumerate(game.logs):
        log_surface = FONT_SMALL.render(log, True, BLACK)
        screen.blit(log_surface, (60, 530 + i * 18))
    
    # 结束当天
    draw_button("结束当天", 620, 520, 130, 40, GOLD, (200, 180, 50), game.next_day)

def draw_game_over_screen(game):
    screen.fill(PURPLE)
    
    if game.game_won:
        title_surface = FONT_LARGE.render('恭喜成为超级偶像！', True, GOLD)
        msg = f"用了 {game.day} 天，获得了 {game.popularity} 名粉丝！"
    else:
        title_surface = FONT_LARGE.render('游戏结束', True, WHITE)
        if game.popularity >= 5000:
            msg = f"虽然时间到了，但你已是人气偶像！粉丝: {game.popularity}"
        else:
            msg = f"继续努力吧！当前粉丝: {game.popularity}"
    
    screen.blit(title_surface, (SCREEN_WIDTH//2 - title_surface.get_width()//2, 200))
    
    msg_surface = FONT_MEDIUM.render(msg, True, WHITE)
    screen.blit(msg_surface, (SCREEN_WIDTH//2 - msg_surface.get_width()//2, 300))
    
    draw_button("重新开始", SCREEN_WIDTH//2 - 75, 400, 150, 50, PINK, WHITE, lambda: reset_game())

def reset_game():
    global game
    game = IdolGame()

# 主游戏循环
game = IdolGame()
clock = pygame.time.Clock()

running = True
while running:
    clock.tick(FPS)
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    if game.game_over:
        draw_game_over_screen(game)
    else:
        draw_main_screen(game)
    
    pygame.display.flip()

pygame.quit()
sys.exit()
