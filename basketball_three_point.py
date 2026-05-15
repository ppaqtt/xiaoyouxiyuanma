import pygame
import sys
import math
import random
import struct

# 初始化pygame
pygame.init()
pygame.mixer.init()

# 游戏配置
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60
GRAVITY = 0.4
AIR_RESISTANCE = 0.99
BALL_RADIUS = 15
HOOP_RADIUS = 28
HOOP_HEIGHT = 300
HOOP_X = SCREEN_WIDTH - 150

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
BLUE = (30, 144, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

# 创建屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("篮球三分球挑战")

# 字体设置
font_large = pygame.font.Font(None, 64)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 32)
font_tiny = pygame.font.Font(None, 24)

# 游戏状态
class GameState:
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3

# 音效生成函数
def generate_sound(frequency, duration, sample_rate=44100, volume=0.5):
    samples = int(duration * sample_rate)
    sound_data = bytearray()
    
    for i in range(samples):
        t = i / sample_rate
        value = int((math.sin(2 * math.pi * frequency * t) * volume) * 32767)
        sound_data.extend(struct.pack('<h', value))
    
    sound = pygame.mixer.Sound(buffer=sound_data)
    return sound

# 预生成音效
pygame.mixer.set_num_channels(8)
swish_sound = generate_sound(800, 0.3)
bounce_sound = generate_sound(200, 0.15)
click_sound = generate_sound(1000, 0.05)
combo_sound = generate_sound(523, 0.2)  # C5
score_sound = generate_sound(659, 0.2)  # E5

class BasketballGame:
    def __init__(self):
        self.reset_game()
        self.state = GameState.MENU
        
    def reset_game(self):
        # 球的位置
        self.ball_x = 150
        self.ball_y = SCREEN_HEIGHT - 200
        self.ball_vx = 0
        self.ball_vy = 0
        self.is_flying = False
        
        # 投篮线
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        
        # 计分
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.shots_made = 0
        self.total_shots = 0
        
        # 计时器
        self.time_left = 60
        self.last_time_update = pygame.time.get_ticks()
        
        # 投篮位置
        self.current_position = "三分线"
        self.position_scores = {"三分线": 3, "底线": 4, "弧顶": 3, "45度角": 3}
        
        # 空心入网
        self.swish = False
        
    def draw_background(self):
        # 天空背景
        gradient = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            color = (int(135 + 120 * ratio), int(206 + 49 * ratio), int(235 + 20 * ratio))
            for x in range(SCREEN_WIDTH):
                gradient.set_at((x, y), color)
        screen.blit(gradient, (0, 0))
        
        # 篮球场地面
        pygame.draw.rect(screen, (34, 139, 34), (0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150))
        
        # 三分线
        pygame.draw.circle(screen, BROWN, (HOOP_X, SCREEN_HEIGHT - 150), 625, 5)
        
        # 罚球线
        pygame.draw.line(screen, BROWN, (HOOP_X - 420, SCREEN_HEIGHT - 150), 
                         (HOOP_X + 420, SCREEN_HEIGHT - 150), 5)
        
        # 篮筐支柱
        pygame.draw.rect(screen, BROWN, (HOOP_X - 8, SCREEN_HEIGHT - 150, 16, -HOOP_HEIGHT))
        
        # 篮板
        pygame.draw.rect(screen, WHITE, (HOOP_X - 80, SCREEN_HEIGHT - 150 - HOOP_HEIGHT - 50, 160, 110))
        pygame.draw.rect(screen, BLACK, (HOOP_X - 80, SCREEN_HEIGHT - 150 - HOOP_HEIGHT - 50, 160, 110), 3)
        
        # 篮筐
        pygame.draw.circle(screen, ORANGE, (HOOP_X, SCREEN_HEIGHT - 150 - HOOP_HEIGHT), HOOP_RADIUS, 5)
        
        # 篮网
        for i in range(12):
            angle = i * 30
            x1 = HOOP_X + HOOP_RADIUS * math.cos(math.radians(angle))
            y1 = SCREEN_HEIGHT - 150 - HOOP_HEIGHT
            x2 = HOOP_X + (HOOP_RADIUS - 10) * math.cos(math.radians(angle + 15))
            y2 = SCREEN_HEIGHT - 150 - HOOP_HEIGHT + 30
            pygame.draw.line(screen, WHITE, (x1, y1), (x2, y2), 2)
        
        # 地面线条
        pygame.draw.line(screen, BROWN, (0, SCREEN_HEIGHT - 150), (SCREEN_WIDTH, SCREEN_HEIGHT - 150), 5)
        
    def draw_ball(self):
        # 篮球主体
        pygame.draw.circle(screen, ORANGE, (int(self.ball_x), int(self.ball_y)), BALL_RADIUS)
        
        # 篮球线条
        pygame.draw.circle(screen, BLACK, (int(self.ball_x), int(self.ball_y)), BALL_RADIUS, 2)
        
        # 纵向线条
        for i in range(4):
            angle = (i * 90) + 45
            x1 = self.ball_x + BALL_RADIUS * math.cos(math.radians(angle))
            y1 = self.ball_y + BALL_RADIUS * math.sin(math.radians(angle))
            x2 = self.ball_x - BALL_RADIUS * math.cos(math.radians(angle))
            y2 = self.ball_y - BALL_RADIUS * math.sin(math.radians(angle))
            pygame.draw.line(screen, BLACK, (int(x1), int(y1)), (int(x2), int(y2)), 2)
        
        # 横向线条
        pygame.draw.arc(screen, BLACK, 
                       (self.ball_x - BALL_RADIUS, self.ball_y - BALL_RADIUS, 
                        BALL_RADIUS * 2, BALL_RADIUS * 2), 0, math.pi, 2)
        pygame.draw.arc(screen, BLACK, 
                       (self.ball_x - BALL_RADIUS, self.ball_y - BALL_RADIUS, 
                        BALL_RADIUS * 2, BALL_RADIUS * 2), math.pi, 2 * math.pi, 2)
    
    def draw_power_line(self):
        if self.is_dragging:
            # 力度线
            dx = self.drag_start_x - pygame.mouse.get_pos()[0]
            dy = self.drag_start_y - pygame.mouse.get_pos()[1]
            length = min(math.sqrt(dx * dx + dy * dy), 200)
            
            # 角度指示
            angle = math.atan2(dy, dx)
            end_x = self.ball_x + length * math.cos(angle)
            end_y = self.ball_y + length * math.sin(angle)
            
            # 绘制力度线
            pygame.draw.line(screen, RED, (self.ball_x, self.ball_y), 
                           (int(end_x), int(end_y)), 4)
            
            # 力度箭头
            arrow_size = 15
            arrow_angle = angle + math.pi
            arrow_x1 = end_x + arrow_size * math.cos(arrow_angle + math.pi / 6)
            arrow_y1 = end_y + arrow_size * math.sin(arrow_angle + math.pi / 6)
            arrow_x2 = end_x + arrow_size * math.cos(arrow_angle - math.pi / 6)
            arrow_y2 = end_y + arrow_size * math.sin(arrow_angle - math.pi / 6)
            pygame.draw.polygon(screen, RED, [(end_x, end_y), (int(arrow_x1), int(arrow_y1)), 
                                             (int(arrow_x2), int(arrow_y2))])
            
            # 力度百分比显示
            power = int((length / 200) * 100)
            power_text = font_small.render(f"力度: {power}%", True, RED)
            screen.blit(power_text, (self.ball_x + 30, self.ball_y - 50))
    
    def draw_ui(self):
        # 分数显示
        score_text = font_large.render(f"{self.score}", True, WHITE)
        screen.blit(score_text, (50, 30))
        
        # 连击显示
        if self.combo > 1:
            combo_text = font_medium.render(f"连击 x{self.combo}", True, YELLOW)
            screen.blit(combo_text, (50, 100))
            
            # 连击进度条
            progress = (self.combo % 5) / 5
            pygame.draw.rect(screen, GRAY, (50, 150, 200, 20))
            pygame.draw.rect(screen, YELLOW, (50, 150, 200 * progress, 20))
        
        # 时间显示
        time_color = GREEN if self.time_left > 10 else RED
        time_text = font_large.render(f"{self.time_left}s", True, time_color)
        screen.blit(time_text, (SCREEN_WIDTH - 150, 30))
        
        # 当前位置
        position_text = font_small.render(f"当前位置: {self.current_position}", True, WHITE)
        screen.blit(position_text, (SCREEN_WIDTH - 300, 100))
        
        # 命中率
        if self.total_shots > 0:
            accuracy = int((self.shots_made / self.total_shots) * 100)
            accuracy_text = font_small.render(f"命中率: {accuracy}%", True, WHITE)
            screen.blit(accuracy_text, (50, 180))
        
        # 空心入网提示
        if self.swish:
            swish_text = font_medium.render("空心入网! +5分", True, GREEN)
            screen.blit(swish_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
            self.swish = False
    
    def draw_menu(self):
        screen.fill(BLUE)
        
        # 标题
        title_text = font_large.render("篮球三分球挑战", True, ORANGE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - 200, 150))
        
        # 篮球图标
        pygame.draw.circle(screen, ORANGE, (SCREEN_WIDTH // 2, 350), 80)
        pygame.draw.circle(screen, BLACK, (SCREEN_WIDTH // 2, 350), 80, 4)
        
        # 开始按钮
        start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 500, 200, 60)
        pygame.draw.rect(screen, GREEN, start_button)
        start_text = font_medium.render("开始游戏", True, WHITE)
        screen.blit(start_text, (SCREEN_WIDTH // 2 - 80, 510))
        
        # 操作说明
        instructions = [
            "操作说明:",
            "1. 按住鼠标左键拖动调整投篮角度和力度",
            "2. 松开鼠标投篮",
            "3. 空心入网获得额外5分",
            "4. 连续命中获得连击奖励",
            "5. 在60秒内获得最高分"
        ]
        
        y_pos = 600
        for line in instructions:
            text = font_tiny.render(line, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - 250, y_pos))
            y_pos += 25
        
        return start_button
    
    def draw_game_over(self):
        # 半透明遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # 游戏结束文字
        game_over_text = font_large.render("游戏结束", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, 200))
        
        # 最终得分
        final_score_text = font_large.render(f"最终得分: {self.score}", True, ORANGE)
        screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 180, 300))
        
        # 统计信息
        stats = [
            f"命中次数: {self.shots_made}",
            f"投篮次数: {self.total_shots}",
            f"最高连击: {self.max_combo}",
            f"命中率: {int((self.shots_made / max(self.total_shots, 1)) * 100)}%"
        ]
        
        y_pos = 400
        for stat in stats:
            text = font_medium.render(stat, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - 150, y_pos))
            y_pos += 50
        
        # 重新开始按钮
        restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 550, 200, 60)
        pygame.draw.rect(screen, GREEN, restart_button)
        restart_text = font_medium.render("再玩一次", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 80, 560))
        
        return restart_button
    
    def update_ball(self):
        if self.is_flying:
            # 应用重力
            self.ball_vy += GRAVITY
            
            # 应用空气阻力
            self.ball_vx *= AIR_RESISTANCE
            self.ball_vy *= AIR_RESISTANCE
            
            # 更新位置
            self.ball_x += self.ball_vx
            self.ball_y += self.ball_vy
            
            # 检测球是否进入篮筐
            hoop_center_y = SCREEN_HEIGHT - 150 - HOOP_HEIGHT
            dist_to_hoop = math.sqrt((self.ball_x - HOOP_X) ** 2 + (self.ball_y - hoop_center_y) ** 2)
            
            # 检测进球
            if (HOOP_RADIUS - BALL_RADIUS - 5 < dist_to_hoop < HOOP_RADIUS + BALL_RADIUS + 5 and
                abs(self.ball_y - hoop_center_y) < BALL_RADIUS + 10):
                
                # 判断是否空心入网（球速较慢且角度合适）
                ball_speed = math.sqrt(self.ball_vx ** 2 + self.ball_vy ** 2)
                if ball_speed < 8:
                    self.swish = True
                    points = self.position_scores[self.current_position] + 5
                    swish_sound.play()
                else:
                    points = self.position_scores[self.current_position]
                    bounce_sound.play()
                
                # 连击奖励
                self.combo += 1
                if self.combo > self.max_combo:
                    self.max_combo = self.combo
                
                if self.combo >= 3:
                    points *= (1 + (self.combo - 2) * 0.2)
                    combo_sound.play()
                
                self.score += int(points)
                self.shots_made += 1
                self.total_shots += 1
                score_sound.play()
                
                # 重置球位置
                self.reset_ball_position()
                
            # 检测球落地
            elif self.ball_y > SCREEN_HEIGHT - 150 - BALL_RADIUS:
                bounce_sound.play()
                self.total_shots += 1
                self.combo = 0
                self.reset_ball_position()
            
            # 检测球飞出屏幕
            elif self.ball_x < -50 or self.ball_x > SCREEN_WIDTH + 50 or self.ball_y > SCREEN_HEIGHT + 50:
                self.total_shots += 1
                self.combo = 0
                self.reset_ball_position()
    
    def reset_ball_position(self):
        self.is_flying = False
        # 随机选择投篮位置
        positions = ["三分线", "底线", "弧顶", "45度角"]
        self.current_position = random.choice(positions)
        
        # 根据位置设置球的初始位置
        if self.current_position == "底线":
            self.ball_x = random.choice([100, SCREEN_WIDTH - 250])
            self.ball_y = SCREEN_HEIGHT - 200
        elif self.current_position == "弧顶":
            self.ball_x = SCREEN_WIDTH // 2 - 300
            self.ball_y = SCREEN_HEIGHT - 200
        elif self.current_position == "45度角":
            self.ball_x = SCREEN_WIDTH // 2 - 150
            self.ball_y = SCREEN_HEIGHT - 180
        else:  # 三分线
            self.ball_x = random.randint(100, SCREEN_WIDTH - 400)
            self.ball_y = SCREEN_HEIGHT - 200
    
    def update_timer(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_time_update >= 1000:
            self.time_left -= 1
            self.last_time_update = current_time
            if self.time_left <= 0:
                self.state = GameState.GAME_OVER
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if self.state == GameState.MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    start_button = self.draw_menu()  # 只是获取按钮区域
                    if start_button.collidepoint(mouse_pos):
                        click_sound.play()
                        self.reset_game()
                        self.state = GameState.PLAYING
            
            elif self.state == GameState.PLAYING:
                if event.type == pygame.MOUSEBUTTONDOWN and not self.is_flying:
                    self.is_dragging = True
                    self.drag_start_x, self.drag_start_y = pygame.mouse.get_pos()
                
                elif event.type == pygame.MOUSEBUTTONUP and self.is_dragging:
                    self.is_dragging = False
                    
                    dx = self.drag_start_x - pygame.mouse.get_pos()[0]
                    dy = self.drag_start_y - pygame.mouse.get_pos()[1]
                    length = min(math.sqrt(dx * dx + dy * dy), 200)
                    
                    if length > 10:
                        angle = math.atan2(dy, dx)
                        power = length / 200
                        
                        # 设置球的初速度
                        self.ball_vx = math.cos(angle) * power * 15
                        self.ball_vy = math.sin(angle) * power * 15
                        self.is_flying = True
            
            elif self.state == GameState.GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    restart_button = self.draw_game_over()  # 只是获取按钮区域
                    if restart_button.collidepoint(mouse_pos):
                        click_sound.play()
                        self.reset_game()
                        self.state = GameState.PLAYING
    
    def run(self):
        clock = pygame.time.Clock()
        
        while True:
            self.handle_events()
            
            if self.state == GameState.MENU:
                start_button = self.draw_menu()
            
            elif self.state == GameState.PLAYING:
                self.draw_background()
                self.draw_ball()
                self.draw_power_line()
                self.draw_ui()
                self.update_ball()
                self.update_timer()
            
            elif self.state == GameState.GAME_OVER:
                self.draw_background()
                self.draw_ball()
                restart_button = self.draw_game_over()
            
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    game = BasketballGame()
    game.run()
