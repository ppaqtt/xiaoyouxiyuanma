import pygame
import os
import random
import math
import array
import wave

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

# 游戏设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_TIME = 60  # 游戏时间（秒）

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# 字体设置
font_large = get_chinese_font(72)
font_medium = get_chinese_font(48)
font_small = get_chinese_font(36)

# 音效生成函数
def generate_sound(frequency, duration, volume=0.5, sample_rate=44100):
    """生成音效"""
    samples = int(sample_rate * duration)
    sound_data = array.array('h', [0] * samples)
    
    for i in range(samples):
        t = i / sample_rate
        sound_data[i] = int(volume * 32767 * math.sin(2 * math.pi * frequency * t))
    
    sound = pygame.mixer.Sound(sound_data)
    return sound

# 创建音效
shoot_sound = generate_sound(200, 0.15, 0.3)
score_sound = generate_sound(523.25, 0.2, 0.3)  # C5
double_sound = generate_sound(659.25, 0.3, 0.3)  # E5
game_over_sound = generate_sound(330, 0.5, 0.3)

class Ball:
    """篮球类"""
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 100
        self.radius = 15
        self.vx = 0
        self.vy = 0
        self.launched = False
        self.reset()
    
    def reset(self):
        """重置篮球位置"""
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 100
        self.vx = 0
        self.vy = 0
        self.launched = False
    
    def launch(self, power):
        """投篮"""
        if not self.launched:
            angle = -math.pi / 4  # 45度向上
            self.vx = power * math.cos(angle)
            self.vy = -power * math.sin(angle)
            self.launched = True
            shoot_sound.play()
    
    def update(self):
        """更新篮球位置"""
        if self.launched:
            self.vy += 0.5  # 重力
            self.x += self.vx
            self.y += self.vy
            
            # 边界检测
            if self.x - self.radius < 0:
                self.x = self.radius
                self.vx *= -0.8
            if self.x + self.radius > SCREEN_WIDTH:
                self.x = SCREEN_WIDTH - self.radius
                self.vx *= -0.8
            if self.y + self.radius > SCREEN_HEIGHT:
                self.reset()
    
    def draw(self, screen):
        """绘制篮球"""
        pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.radius)
        # 篮球纹理
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        pygame.draw.line(screen, BLACK, (int(self.x - self.radius * 0.7), int(self.y)), 
                         (int(self.x + self.radius * 0.7), int(self.y)))
        pygame.draw.line(screen, BLACK, (int(self.x), int(self.y - self.radius * 0.7)), 
                         (int(self.x), int(self.y + self.radius * 0.7)))

class Hoop:
    """篮筐类"""
    def __init__(self, x, y, points, color):
        self.x = x
        self.y = y
        self.radius = 30
        self.points = points
        self.color = color
    
    def draw(self, screen):
        """绘制篮筐"""
        # 篮筐环
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius, 4)
        # 篮网
        for i in range(-25, 26, 10):
            pygame.draw.line(screen, WHITE, (self.x + i, self.y), 
                             (self.x + i * 0.8, self.y + 30))
        # 分值显示
        text = font_small.render(str(self.points), True, WHITE)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

class PowerBar:
    """力量条类"""
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 - 50
        self.y = SCREEN_HEIGHT - 50
        self.width = 100
        self.height = 10
        self.power = 0
        self.direction = 1  # 1=增加，-1=减少
    
    def update(self):
        """更新力量值"""
        self.power += self.direction * 2
        if self.power >= 100:
            self.power = 100
            self.direction = -1
        elif self.power <= 0:
            self.power = 0
            self.direction = 1
    
    def draw(self, screen):
        """绘制力量条"""
        # 背景
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        # 力量值
        if self.power < 33:
            color = GREEN
        elif self.power < 66:
            color = YELLOW
        else:
            color = RED
        pygame.draw.rect(screen, color, (self.x, self.y, self.width * self.power / 100, self.height))

class DoublePowerUp:
    """双倍分数道具"""
    def __init__(self):
        self.x = random.randint(100, SCREEN_WIDTH - 100)
        self.y = -50
        self.radius = 20
        self.active = False
        self.speed = 2
    
    def activate(self):
        """激活道具"""
        self.x = random.randint(100, SCREEN_WIDTH - 100)
        self.y = -50
        self.active = True
    
    def update(self):
        """更新道具位置"""
        if self.active:
            self.y += self.speed
            if self.y > SCREEN_HEIGHT:
                self.active = False
    
    def draw(self, screen):
        """绘制道具"""
        if self.active:
            pygame.draw.circle(screen, PURPLE, (self.x, self.y), self.radius)
            pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius, 2)
            text = font_small.render("2x", True, YELLOW)
            text_rect = text.get_rect(center=(self.x, self.y))
            screen.blit(text, text_rect)

class Game:
    """游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("篮球街机")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.score = 0
        self.time_left = GAME_TIME
        self.double_points = False
        self.double_timer = 0
        
        # 创建游戏对象
        self.ball = Ball()
        self.power_bar = PowerBar()
        
        # 创建多个篮筐（不同分值）
        self.hoops = [
            Hoop(SCREEN_WIDTH // 2, 150, 10, ORANGE),      # 中间主篮筐
            Hoop(200, 200, 15, BLUE),                        # 左侧篮筐
            Hoop(600, 200, 15, BLUE),                        # 右侧篮筐
            Hoop(150, 280, 20, RED),                         # 左下方篮筐
            Hoop(650, 280, 20, RED),                         # 右下方篮筐
            Hoop(SCREEN_WIDTH // 2, 320, 25, PURPLE),        # 底部篮筐
        ]
        
        self.double_powerup = DoublePowerUp()
        
        # 计时器
        self.last_time = pygame.time.get_ticks()
        self.powerup_timer = 0
        
    def check_collision(self):
        """检测碰撞"""
        for hoop in self.hoops:
            distance = math.sqrt((self.ball.x - hoop.x) ** 2 + (self.ball.y - hoop.y) ** 2)
            if distance < self.ball.radius + hoop.radius - 10:
                # 计算得分倍数
                multiplier = 2 if self.double_points else 1
                self.score += hoop.points * multiplier
                score_sound.play()
                
                # 显示得分动画
                self.show_score_popup(hoop.x, hoop.y, hoop.points * multiplier)
                self.ball.reset()
                return True
        return False
    
    def check_powerup_collision(self):
        """检测道具碰撞"""
        if self.double_powerup.active:
            distance = math.sqrt((self.ball.x - self.double_powerup.x) ** 2 + 
                                (self.ball.y - self.double_powerup.y) ** 2)
            if distance < self.ball.radius + self.double_powerup.radius:
                self.double_points = True
                self.double_timer = 5  # 5秒双倍时间
                self.double_powerup.active = False
                double_sound.play()
    
    def show_score_popup(self, x, y, points):
        """显示得分弹窗"""
        popup = font_medium.render(f"+{points}", True, YELLOW)
        self.screen.blit(popup, (x - 30, y - 60))
        pygame.display.flip()
        pygame.time.delay(200)
    
    def run(self):
        """游戏主循环"""
        while self.running:
            current_time = pygame.time.get_ticks()
            
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if not self.game_over:
                            power = self.power_bar.power / 10  # 转换为投篮力度
                            self.ball.launch(power)
                    if event.key == pygame.K_r:
                        self.__init__()
            
            if not self.game_over:
                # 更新时间
                if current_time - self.last_time >= 1000:
                    self.time_left -= 1
                    self.last_time = current_time
                    
                    # 更新双倍时间
                    if self.double_points:
                        self.double_timer -= 1
                        if self.double_timer <= 0:
                            self.double_points = False
                
                # 更新道具计时器
                self.powerup_timer += 1
                if self.powerup_timer >= 300 and not self.double_powerup.active:  # 每5秒出现一次
                    self.double_powerup.activate()
                    self.powerup_timer = 0
                
                # 更新游戏对象
                self.power_bar.update()
                self.ball.update()
                self.double_powerup.update()
                
                # 检测碰撞
                self.check_collision()
                self.check_powerup_collision()
                
                # 游戏结束判断
                if self.time_left <= 0:
                    self.game_over = True
                    game_over_sound.play()
            
            # 绘制
            self.draw()
            
            # 控制帧率
            self.clock.tick(FPS)
        
        pygame.quit()
    
    def draw(self):
        """绘制游戏界面"""
        # 背景
        self.screen.fill(BLACK)
        
        # 绘制篮筐
        for hoop in self.hoops:
            hoop.draw(self.screen)
        
        # 绘制道具
        self.double_powerup.draw(self.screen)
        
        # 绘制篮球
        self.ball.draw(self.screen)
        
        # 绘制力量条
        self.power_bar.draw(self.screen)
        
        # 绘制UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """绘制UI元素"""
        # 分数
        score_text = font_medium.render(f"得分: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))
        
        # 时间
        time_text = font_medium.render(f"时间: {self.time_left}", True, WHITE)
        self.screen.blit(time_text, (SCREEN_WIDTH - 180, 20))
        
        # 双倍状态
        if self.double_points:
            double_text = font_small.render(f"双倍得分! ({self.double_timer}s)", True, YELLOW)
            self.screen.blit(double_text, (SCREEN_WIDTH // 2 - 80, 20))
        
        # 游戏结束画面
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            title = font_large.render("游戏结束", True, RED)
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(title, title_rect)
            
            final_score = font_medium.render(f"最终得分: {self.score}", True, YELLOW)
            score_rect = final_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(final_score, score_rect)
            
            restart_text = font_small.render("按 R 重新开始", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
            self.screen.blit(restart_text, restart_rect)

if __name__ == "__main__":
    game = Game()
    game.run()
