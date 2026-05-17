import pygame
import os
import math
import random
import sys

# 初始化 pygame
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

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
LIGHT_GREEN = (50, 205, 50)
BROWN = (139, 69, 19)
BLUE = (0, 191, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

# 球的物理参数
FRICTION = 0.99
HOLE_RADIUS = 15
BALL_RADIUS = 8
MAX_POWER = 15
MIN_POWER = 2

# 音效生成函数
def generate_sound(frequency, duration, volume=0.5):
    sample_rate = 44100
    samples = int(sample_rate * duration)
    sound_data = []
    
    for i in range(samples):
        t = i / sample_rate
        value = math.sin(2 * math.pi * frequency * t) * volume
        sound_data.append(int(value * 32767))
    
    return pygame.mixer.Sound(pygame.sndarray.make_sound(bytearray([v & 0xFF for v in sound_data])))

# 创建音效
hit_sound = generate_sound(200, 0.1, 0.3)
roll_sound = generate_sound(100, 0.5, 0.1)
hole_sound = generate_sound(523, 0.3, 0.5)
click_sound = generate_sound(800, 0.05, 0.2)

# 关卡数据
levels = [
    {
        'name': '新手场',
        'terrain': [
            (0, 600, 800, 100, GREEN),
            (0, 400, 800, 200, LIGHT_GREEN)
        ],
        'slopes': [],
        'ball_pos': (100, 550),
        'hole_pos': (700, 550)
    },
    {
        'name': '缓坡挑战',
        'terrain': [
            (0, 600, 800, 100, GREEN),
            (0, 300, 800, 300, LIGHT_GREEN)
        ],
        'slopes': [
            {'start': (0, 500), 'end': (800, 350), 'angle': 0.1}
        ],
        'ball_pos': (100, 500),
        'hole_pos': (700, 380)
    },
    {
        'name': '沙丘地形',
        'terrain': [
            (0, 600, 800, 100, BROWN),
            (0, 400, 800, 200, LIGHT_GREEN)
        ],
        'slopes': [
            {'start': (0, 450), 'end': (400, 400), 'angle': 0.05},
            {'start': (400, 400), 'end': (800, 450), 'angle': -0.05}
        ],
        'ball_pos': (100, 480),
        'hole_pos': (700, 480)
    },
    {
        'name': '水域障碍',
        'terrain': [
            (0, 600, 800, 100, GREEN),
            (0, 350, 800, 250, LIGHT_GREEN),
            (350, 400, 100, 150, BLUE)
        ],
        'slopes': [],
        'ball_pos': (100, 550),
        'hole_pos': (700, 550)
    },
    {
        'name': '终极挑战',
        'terrain': [
            (0, 600, 800, 100, GREEN),
            (0, 250, 800, 350, LIGHT_GREEN),
            (300, 350, 200, 100, BROWN),
            (150, 500, 100, 50, BLUE)
        ],
        'slopes': [
            {'start': (0, 550), 'end': (300, 400), 'angle': 0.15},
            {'start': (500, 400), 'end': (800, 500), 'angle': -0.1}
        ],
        'ball_pos': (100, 580),
        'hole_pos': (700, 320)
    }
]

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = BALL_RADIUS
        self.is_moving = False
    
    def apply_force(self, angle, power):
        self.vx = math.cos(angle) * power
        self.vy = math.sin(angle) * power
        self.is_moving = True
        hit_sound.play()
    
    def update(self, slopes):
        if not self.is_moving:
            return
        
        # 应用摩擦力
        self.vx *= FRICTION
        self.vy *= FRICTION
        
        # 应用坡度影响
        for slope in slopes:
            dx = slope['end'][0] - slope['start'][0]
            dy = slope['end'][1] - slope['start'][1]
            if dx != 0:
                slope_angle = math.atan2(dy, dx)
                # 根据球的位置应用坡度加速度
                if slope['start'][0] < self.x < slope['end'][0]:
                    self.vy += math.sin(slope_angle) * 0.1
        
        # 更新位置
        self.x += self.vx
        self.y += self.vy
        
        # 检查速度是否足够小
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if speed < 0.1:
            self.vx = 0
            self.vy = 0
            self.is_moving = False
    
    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, GRAY, (int(self.x) - 3, int(self.y) - 3), self.radius - 3)
    
    def check_collision(self, obstacles):
        for obs in obstacles:
            ox, oy, ow, oh = obs[:4]
            if self.x + self.radius > ox and self.x - self.radius < ox + ow:
                if self.y + self.radius > oy and self.y - self.radius < oy + oh:
                    # 反弹
                    if abs(self.vx) > abs(self.vy):
                        self.vx *= -0.7
                    else:
                        self.vy *= -0.7
                    self.x = max(ox + self.radius, min(self.x, ox + ow - self.radius))
                    self.y = max(oy + self.radius, min(self.y, oy + oh - self.radius))

class Hole:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = HOLE_RADIUS
    
    def draw(self, screen):
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius + 3)
        pygame.draw.circle(screen, (50, 50, 50), (int(self.x), int(self.y)), self.radius)
    
    def check_hole_in(self, ball):
        dx = self.x - ball.x
        dy = self.y - ball.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        return distance < self.radius + ball.radius * 0.7

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('高尔夫推杆游戏')
        self.clock = pygame.time.Clock()
        self.font = get_chinese_font(36)
        self.small_font = get_chinese_font(24)
        
        self.current_level = 0
        self.strokes = 0
        self.best_scores = [999] * len(levels)
        
        self.reset_level()
        
        self.power = 0
        self.power_direction = 0
        self.is_charging = False
        self.show_power_bar = False
        
        self.game_state = 'playing'  # playing, charging, success, fail
    
    def reset_level(self):
        level = levels[self.current_level]
        self.ball = Ball(*level['ball_pos'])
        self.hole = Hole(*level['hole_pos'])
        self.strokes = 0
        self.game_state = 'playing'
        self.is_charging = False
        self.show_power_bar = False
    
    def next_level(self):
        if self.current_level < len(levels) - 1:
            self.current_level += 1
            self.reset_level()
        else:
            self.show_victory()
    
    def show_victory(self):
        self.game_state = 'victory'
    
    def draw_power_bar(self, mouse_pos):
        if not self.show_power_bar:
            return
        
        # 计算方向
        dx = mouse_pos[0] - self.ball.x
        dy = mouse_pos[1] - self.ball.y
        angle = math.atan2(dy, dx)
        
        # 绘制力度条背景
        bar_x = self.ball.x + math.cos(angle) * 30
        bar_y = self.ball.y + math.sin(angle) * 30
        
        # 力度条方向与推杆方向相反
        perp_angle = angle + math.pi / 2
        bar_length = 100
        bar_width = 10
        
        # 绘制背景
        bg_x1 = bar_x + math.cos(perp_angle) * bar_width / 2
        bg_y1 = bar_y + math.sin(perp_angle) * bar_width / 2
        bg_x2 = bar_x - math.cos(perp_angle) * bar_width / 2
        bg_y2 = bar_y - math.sin(perp_angle) * bar_width / 2
        bg_x3 = bg_x2 + math.cos(angle) * bar_length
        bg_y3 = bg_y2 + math.sin(angle) * bar_length
        bg_x4 = bg_x1 + math.cos(angle) * bar_length
        bg_y4 = bg_y1 + math.sin(angle) * bar_length
        
        pygame.draw.polygon(self.screen, GRAY, [(bg_x1, bg_y1), (bg_x2, bg_y2), (bg_x3, bg_y3), (bg_x4, bg_y4)])
        
        # 绘制力度
        power_length = (self.power / MAX_POWER) * bar_length
        pow_x1 = bar_x + math.cos(perp_angle) * bar_width / 2 * 0.8
        pow_y1 = bar_y + math.sin(perp_angle) * bar_width / 2 * 0.8
        pow_x2 = bar_x - math.cos(perp_angle) * bar_width / 2 * 0.8
        pow_y2 = bar_y - math.sin(perp_angle) * bar_width / 2 * 0.8
        pow_x3 = pow_x2 + math.cos(angle) * power_length
        pow_y3 = pow_y2 + math.sin(angle) * power_length
        pow_x4 = pow_x1 + math.cos(angle) * power_length
        pow_y4 = pow_y1 + math.sin(angle) * power_length
        
        # 根据力度改变颜色
        if self.power < MAX_POWER * 0.5:
            color = GREEN
        elif self.power < MAX_POWER * 0.8:
            color = YELLOW
        else:
            color = RED
        
        pygame.draw.polygon(self.screen, color, [(pow_x1, pow_y1), (pow_x2, pow_y2), (pow_x3, pow_y3), (pow_x4, pow_y4)])
    
    def draw_terrain(self):
        level = levels[self.current_level]
        for terrain in level['terrain']:
            x, y, w, h, color = terrain
            pygame.draw.rect(self.screen, color, (x, y, w, h))
    
    def draw(self):
        # 清空屏幕
        self.screen.fill(BLUE)
        
        # 绘制地形
        self.draw_terrain()
        
        # 绘制洞
        self.hole.draw(self.screen)
        
        # 绘制球
        self.ball.draw(self.screen)
        
        # 绘制力度条
        if self.show_power_bar:
            mouse_pos = pygame.mouse.get_pos()
            self.draw_power_bar(mouse_pos)
        
        # 绘制UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        # 关卡信息
        level_text = self.font.render(f'关卡 {self.current_level + 1}: {levels[self.current_level]["name"]}', True, WHITE)
        self.screen.blit(level_text, (10, 10))
        
        # 杆数
        strokes_text = self.font.render(f'杆数: {self.strokes}', True, WHITE)
        self.screen.blit(strokes_text, (10, 50))
        
        # 最佳成绩
        best_text = self.font.render(f'最佳: {self.best_scores[self.current_level]}杆', True, WHITE)
        self.screen.blit(best_text, (10, 90))
        
        # 操作提示
        hint_text = self.small_font.render('点击鼠标设定方向，按住蓄力，松开发球', True, WHITE)
        self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 30))
    
    def draw_victory(self):
        self.screen.fill(BLACK)
        
        title_text = self.font.render('🎉 恭喜通关！', True, YELLOW)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - 100, 100))
        
        total_strokes = sum(self.best_scores)
        for i, (level, score) in enumerate(zip(levels, self.best_scores)):
            level_text = self.small_font.render(f'{level["name"]}: {score}杆', True, WHITE)
            self.screen.blit(level_text, (SCREEN_WIDTH // 2 - 80, 200 + i * 30))
        
        total_text = self.font.render(f'总杆数: {total_strokes}', True, GREEN)
        self.screen.blit(total_text, (SCREEN_WIDTH // 2 - 80, 400))
        
        restart_text = self.small_font.render('按 R 键重新开始', True, WHITE)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 80, 500))
        
        pygame.display.flip()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if self.game_state == 'victory':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.current_level = 0
                        self.best_scores = [999] * len(levels)
                        self.reset_level()
                continue
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.ball.is_moving:
                    click_sound.play()
                    self.is_charging = True
                    self.show_power_bar = True
            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.is_charging:
                    self.is_charging = False
                    self.show_power_bar = False
                    
                    if self.power >= MIN_POWER:
                        mouse_pos = pygame.mouse.get_pos()
                        dx = mouse_pos[0] - self.ball.x
                        dy = mouse_pos[1] - self.ball.y
                        angle = math.atan2(dy, dx) + math.pi  # 反向击球
                        self.ball.apply_force(angle, self.power)
                        self.strokes += 1
                    
                    self.power = 0
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    self.reset_level()
    
    def update(self):
        if self.is_charging:
            self.power = min(self.power + 0.3, MAX_POWER)
        
        if self.ball.is_moving:
            self.ball.update(levels[self.current_level].get('slopes', []))
            
            # 检查边界
            if self.ball.x < self.ball.radius:
                self.ball.x = self.ball.radius
                self.ball.vx *= -0.5
            if self.ball.x > SCREEN_WIDTH - self.ball.radius:
                self.ball.x = SCREEN_WIDTH - self.ball.radius
                self.ball.vx *= -0.5
            if self.ball.y < self.ball.radius:
                self.ball.y = self.ball.radius
                self.ball.vy *= -0.5
            if self.ball.y > SCREEN_HEIGHT - self.ball.radius:
                self.ball.y = SCREEN_HEIGHT - self.ball.radius
                self.ball.vy *= -0.5
            
            # 检查障碍物碰撞
            obstacles = [t for t in levels[self.current_level]['terrain'] if t[4] == BLUE]
            self.ball.check_collision(obstacles)
            
            # 检查进洞
            if self.hole.check_hole_in(self.ball):
                hole_sound.play()
                if self.strokes < self.best_scores[self.current_level]:
                    self.best_scores[self.current_level] = self.strokes
                self.next_level()
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            
            if self.game_state == 'victory':
                self.draw_victory()
            else:
                self.draw()
            
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()