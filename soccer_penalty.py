import pygame
import os
import sys
import math
import random
import struct

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
GREEN = (34, 139, 34)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# 创建屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("足球点球大战")

# 时钟
clock = pygame.time.Clock()

# 音效生成器
class SoundGenerator:
    def __init__(self):
        self.sample_rate = 44100
        self.audio_enabled = True
        try:
            pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=2)
        except pygame.error:
            self.audio_enabled = False
    
    def generate_sine_wave(self, frequency, duration, volume=0.5):
        if not self.audio_enabled:
            return None
        samples = int(self.sample_rate * duration)
        wave = bytearray()
        for i in range(samples):
            t = i / self.sample_rate
            value = int(32767 * volume * math.sin(2 * math.pi * frequency * t))
            wave.extend(struct.pack('<h', value))
            wave.extend(struct.pack('<h', value))
        return pygame.mixer.Sound(wave)
    
    def generate_kick_sound(self):
        return self.generate_sine_wave(150, 0.15, 0.8)
    
    def generate_goal_sound(self):
        return self.generate_sine_wave(523, 0.3, 0.5)
    
    def generate_save_sound(self):
        return self.generate_sine_wave(200, 0.2, 0.6)
    
    def generate_miss_sound(self):
        return self.generate_sine_wave(100, 0.4, 0.4)
    
    def generate_power_up_sound(self):
        return self.generate_sine_wave(440, 0.1, 0.3)

# 游戏状态
class GameState:
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3

class SoccerBall:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x = SCREEN_WIDTH // 2 - 300
        self.y = SCREEN_HEIGHT // 2
        self.vx = 0
        self.vy = 0
        self.radius = 15
        self.in_air = False
        self.color = (255, 255, 255)
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        # 足球花纹
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius - 5, 1)
        pygame.draw.line(surface, BLACK, (int(self.x) - self.radius + 3, int(self.y)), (int(self.x) + self.radius - 3, int(self.y)))
        pygame.draw.line(surface, BLACK, (int(self.x), int(self.y) - self.radius + 3), (int(self.x), int(self.y) + self.radius - 3))
    
    def update(self):
        if self.in_air:
            self.x += self.vx
            self.y += self.vy
            self.vy += 0.2  # 重力
            # 摩擦力
            self.vx *= 0.995

class Goalkeeper:
    def __init__(self):
        self.width = 40
        self.height = 80
        self.x = SCREEN_WIDTH // 2 + 200
        self.y = SCREEN_HEIGHT // 2
        self.speed = 5
        self.target_y = self.y
        self.jumping = False
        self.jump_speed = 0
        self.color = BLUE
    
    def draw(self, surface):
        # 身体
        pygame.draw.rect(surface, self.color, (self.x - self.width // 2, self.y - self.height // 2, self.width, self.height))
        # 头
        pygame.draw.circle(surface, (255, 204, 153), (self.x, self.y - self.height // 2 - 15), 15)
        # 手套
        pygame.draw.rect(surface, ORANGE, (self.x - self.width // 2 - 10, self.y - 20, 12, 30))
        pygame.draw.rect(surface, ORANGE, (self.x + self.width // 2 - 2, self.y - 20, 12, 30))
    
    def update(self, difficulty):
        speed = self.speed + difficulty * 0.5
        
        if abs(self.y - self.target_y) > 5:
            if self.y < self.target_y:
                self.y += speed
            else:
                self.y -= speed
        
        if self.jumping:
            self.y += self.jump_speed
            self.jump_speed += 0.4
            if self.jump_speed > 0:
                self.jumping = False
    
    def jump(self, direction):
        if not self.jumping:
            self.jump_speed = -12 * direction
            self.jumping = True

class Goal:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 + 250
        self.y = SCREEN_HEIGHT // 2
        self.width = 20
        self.height = 180
        self.top = self.y - self.height // 2
        self.bottom = self.y + self.height // 2
    
    def draw(self, surface):
        # 球门柱
        pygame.draw.rect(surface, WHITE, (self.x - self.width // 2, self.top, self.width, self.height))
        # 横梁
        pygame.draw.rect(surface, WHITE, (self.x - 60, self.top - 10, 120, 10))
        # 球网
        for i in range(0, self.height, 20):
            pygame.draw.line(surface, (200, 200, 200), (self.x - 50, self.top + i), (self.x + 50, self.top + i))

class PowerBar:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 - 300
        self.y = SCREEN_HEIGHT // 2 + 80
        self.width = 150
        self.height = 15
        self.power = 0
        self.max_power = 100
        self.increasing = False
    
    def draw(self, surface):
        # 背景
        pygame.draw.rect(surface, BLACK, (self.x, self.y, self.width, self.height), 2)
        # 力度条
        fill_width = (self.power / self.max_power) * self.width
        if self.power < 33:
            color = GREEN
        elif self.power < 66:
            color = YELLOW
        else:
            color = RED
        pygame.draw.rect(surface, color, (self.x, self.y, fill_width, self.height))
        # 标签
        font = get_chinese_font(20)
        text = font.render(f"力度: {int(self.power)}%", True, BLACK)
        surface.blit(text, (self.x, self.y + 20))
    
    def update(self):
        if self.increasing:
            self.power = (self.power + 2) % (self.max_power + 1)

class Game:
    def __init__(self):
        self.sound_gen = SoundGenerator()
        self.ball = SoccerBall()
        self.goalkeeper = Goalkeeper()
        self.goal = Goal()
        self.power_bar = PowerBar()
        self.game_state = GameState.MENU
        self.score = 0
        self.level = 1
        self.consecutive_goals = 0
        self.max_consecutive = 0
        self.total_shots = 0
        self.goals = 0
        self.target_angle = 0
        self.show_trajectory = False
        self.trajectory_points = []
        
        # 音效缓存
        self.kick_sound = self.sound_gen.generate_kick_sound()
        self.goal_sound = self.sound_gen.generate_goal_sound()
        self.save_sound = self.sound_gen.generate_save_sound()
        self.miss_sound = self.sound_gen.generate_miss_sound()
        self.power_up_sound = self.sound_gen.generate_power_up_sound()
    
    def play_sound(self, sound):
        if sound is not None:
            sound.play()
    
    def draw_menu(self):
        screen.fill(GREEN)
        
        # 标题
        font = get_chinese_font(64)
        text = font.render("足球点球大战", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(text, text_rect)
        
        # 副标题
        font = get_chinese_font(32)
        text = font.render("鼠标瞄准 - 按住蓄力 - 松开发射", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 250))
        screen.blit(text, text_rect)
        
        # 开始按钮
        button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 350, 200, 50)
        pygame.draw.rect(screen, BLUE, button_rect)
        font = get_chinese_font(36)
        text = font.render("开始游戏", True, WHITE)
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)
        
        # 操作说明
        font = get_chinese_font(24)
        text = font.render("操作说明:", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - 80, 450))
        text = font.render("1. 移动鼠标瞄准球门", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - 80, 480))
        text = font.render("2. 按住鼠标左键蓄力", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - 80, 510))
        text = font.render("3. 松开鼠标射门", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - 80, 540))
        
        return button_rect
    
    def draw_game_over(self):
        screen.fill(GREEN)
        
        font = get_chinese_font(64)
        text = font.render("游戏结束", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(text, text_rect)
        
        font = get_chinese_font(32)
        text = font.render(f"最终得分: {self.score}", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 250))
        screen.blit(text, text_rect)
        
        text = font.render(f"总射门次数: {self.total_shots}", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        screen.blit(text, text_rect)
        
        text = font.render(f"进球数: {self.goals}", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        screen.blit(text, text_rect)
        
        text = font.render(f"最高连续进球: {self.max_consecutive}", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        screen.blit(text, text_rect)
        
        button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 480, 200, 50)
        pygame.draw.rect(screen, BLUE, button_rect)
        font = get_chinese_font(36)
        text = font.render("重新开始", True, WHITE)
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)
        
        return button_rect
    
    def draw_game(self):
        # 场地背景
        screen.fill(GREEN)
        
        # 场地线条
        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 2)
        pygame.draw.circle(screen, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 80, 2)
        
        # 球门
        self.goal.draw(screen)
        
        # 守门员
        self.goalkeeper.draw(screen)
        
        # 足球
        self.ball.draw(screen)
        
        # 力度条
        self.power_bar.draw(screen)
        
        # 瞄准线和轨迹
        if self.show_trajectory:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # 瞄准线
            pygame.draw.line(screen, YELLOW, (self.ball.x, self.ball.y), (mouse_x, mouse_y), 2)
            # 预测轨迹
            for i, point in enumerate(self.trajectory_points):
                alpha = 255 - (i * 255 // len(self.trajectory_points))
                pygame.draw.circle(screen, (255, 255, 0, alpha), (int(point[0]), int(point[1])), 3)
        
        # 分数和关卡显示
        font = get_chinese_font(32)
        text = font.render(f"得分: {self.score}", True, WHITE)
        screen.blit(text, (20, 20))
        
        text = font.render(f"关卡: {self.level}", True, WHITE)
        screen.blit(text, (20, 50))
        
        text = font.render(f"连续: {self.consecutive_goals}", True, WHITE)
        screen.blit(text, (20, 80))
        
        text = font.render(f"难度: {'简单' if self.level <= 2 else '中等' if self.level <= 4 else '困难'}", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH - 150, 20))
    
    def calculate_trajectory(self, power, angle):
        points = []
        x, y = self.ball.x, self.ball.y
        vx = math.cos(angle) * power * 0.5
        vy = math.sin(angle) * power * 0.5
        
        for _ in range(50):
            points.append((x, y))
            x += vx
            y += vy
            vy += 0.2
            vx *= 0.995
        
        return points
    
    def handle_shot(self):
        self.total_shots += 1
        power = self.power_bar.power / 100 * 15
        angle = self.target_angle
        
        self.ball.vx = math.cos(angle) * power
        self.ball.vy = math.sin(angle) * power
        self.ball.in_air = True
        
        self.play_sound(self.kick_sound)
        
        # 守门员AI
        self.predict_and_save(power, angle)
    
    def predict_and_save(self, power, angle):
        # 预测球的落点
        predict_x = self.ball.x + math.cos(angle) * power * 15
        predict_y = self.ball.y + math.sin(angle) * power * 15
        
        # 考虑重力影响
        time_to_goal = (self.goal.x - self.ball.x) / (math.cos(angle) * power) if math.cos(angle) * power != 0 else 2
        predict_y += 0.5 * 0.2 * time_to_goal * time_to_goal
        
        # 守门员反应
        reaction_time = random.uniform(0.3, 0.6 - self.level * 0.05)
        pygame.time.set_timer(pygame.USEREVENT, int(reaction_time * 1000))
        
        self.goalkeeper.target_y = predict_y
        
        # 高球时跳跃
        if predict_y < self.goal.top + 30 or predict_y > self.goal.bottom - 30:
            direction = -1 if predict_y < SCREEN_HEIGHT // 2 else 1
            self.goalkeeper.jump(direction)
    
    def check_goal(self):
        ball_x = self.ball.x
        ball_y = self.ball.y
        
        # 检查是否进球
        if (self.goal.x - self.goal.width // 2 <= ball_x <= self.goal.x + self.goal.width // 2 and
            self.goal.top <= ball_y <= self.goal.bottom):
            return True
        
        # 检查是否被守门员扑到
        keeper_left = self.goalkeeper.x - self.goalkeeper.width // 2 - 10
        keeper_right = self.goalkeeper.x + self.goalkeeper.width // 2 + 10
        keeper_top = self.goalkeeper.y - self.goalkeeper.height // 2
        keeper_bottom = self.goalkeeper.y + self.goalkeeper.height // 2
        
        if (keeper_left <= ball_x <= keeper_right and
            keeper_top <= ball_y <= keeper_bottom):
            return False
        
        # 检查是否出界
        if ball_x > SCREEN_WIDTH + 50 or ball_y < -50 or ball_y > SCREEN_HEIGHT + 50:
            return False
        
        return None
    
    def update_level(self):
        if self.total_shots > 0 and self.total_shots % 5 == 0:
            self.level = min(self.level + 1, 6)
            self.play_sound(self.power_up_sound)
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state == GameState.MENU:
                        button_rect = self.draw_menu()
                        if button_rect.collidepoint(event.pos):
                            self.__init__()
                            self.game_state = GameState.PLAYING
                    elif self.game_state == GameState.GAME_OVER:
                        button_rect = self.draw_game_over()
                        if button_rect.collidepoint(event.pos):
                            self.__init__()
                            self.game_state = GameState.PLAYING
                    elif self.game_state == GameState.PLAYING and not self.ball.in_air:
                        self.power_bar.increasing = True
                
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.game_state == GameState.PLAYING and not self.ball.in_air and self.power_bar.power > 0:
                        self.handle_shot()
                        self.power_bar.increasing = False
                        self.show_trajectory = False
                
                if event.type == pygame.MOUSEMOTION:
                    if self.game_state == GameState.PLAYING and not self.ball.in_air:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        self.target_angle = math.atan2(mouse_y - self.ball.y, mouse_x - self.ball.x)
                        self.show_trajectory = True
                        self.trajectory_points = self.calculate_trajectory(self.power_bar.power / 100 * 15, self.target_angle)
            
            if self.game_state == GameState.MENU:
                self.draw_menu()
            
            elif self.game_state == GameState.GAME_OVER:
                self.draw_game_over()
            
            elif self.game_state == GameState.PLAYING:
                # 更新游戏对象
                self.power_bar.update()
                self.goalkeeper.update(self.level)
                
                if self.ball.in_air:
                    self.ball.update()
                    
                    result = self.check_goal()
                    if result is not None:
                        if result:
                            self.goals += 1
                            self.consecutive_goals += 1
                            self.max_consecutive = max(self.max_consecutive, self.consecutive_goals)
                            # 基础分 + 连续奖励
                            base_score = 100
                            bonus = self.consecutive_goals * 20
                            self.score += base_score + bonus
                            self.play_sound(self.goal_sound)
                        else:
                            self.consecutive_goals = 0
                            if self.ball.x < self.goal.x:
                                self.play_sound(self.save_sound)
                            else:
                                self.play_sound(self.miss_sound)
                        
                        # 重置球
                        self.ball.reset()
                        self.power_bar.power = 0
                        self.update_level()
                        
                        # 检查游戏结束条件
                        if self.total_shots >= 10:
                            self.game_state = GameState.GAME_OVER
                
                self.draw_game()
            
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
