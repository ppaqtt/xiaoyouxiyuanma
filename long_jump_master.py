
import pygame
import sys
import math
import random
import array

# 初始化pygame
pygame.init()

# 尝试初始化音效，如果失败则禁用音效
try:
    pygame.mixer.init()
    sound_enabled = True
except pygame.error:
    sound_enabled = False

# 游戏常量
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
GROUND_HEIGHT = 100
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60

# 颜色定义
WHITE = (255, 255, 255)
BLUE = (135, 206, 235)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# 关卡目标（米）
LEVEL_TARGETS = [5, 8, 12, 15, 20, 25, 30, 35, 40, 50]

# 创建屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("跳远大师")

# 字体设置
font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 28)

# 空音效类（用于无音频设备时）
class DummySound:
    def play(self):
        pass

# 音效生成函数
def generate_sound(frequency, duration, volume=0.5):
    if not sound_enabled:
        return DummySound()
    sample_rate = 44100
    samples = int(sample_rate * duration)
    wave = array.array('h', [0] * samples)
    for i in range(samples):
        t = i / sample_rate
        wave[i] = int(32767 * volume * math.sin(2 * math.pi * frequency * t))
    sound = pygame.mixer.Sound(wave)
    return sound

# 生成音效
run_sound = generate_sound(800, 0.1, 0.3)
jump_sound = generate_sound(400, 0.3, 0.5)
land_sound = generate_sound(200, 0.2, 0.4)
success_sound = generate_sound(600, 0.5, 0.5)
fail_sound = generate_sound(150, 0.3, 0.4)

class Player:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT
        self.velocity_x = 0
        self.velocity_y = 0
        self.run_power = 0
        self.max_power = 100
        self.jump_angle = 45
        self.is_running = False
        self.is_jumping = False
        self.is_flying = False
        self.rotation = 0
        self.target_distance = 0
        self.state = 'ready'  # ready, running, jumping, flying, landed
    
    def start_run(self):
        self.is_running = True
        self.state = 'running'
        self.run_power = 0
    
    def update_run(self):
        if self.is_running and self.run_power < self.max_power:
            self.run_power += 1
            if self.run_power % 10 == 0:
                run_sound.play()
    
    def jump(self):
        self.is_running = False
        self.is_jumping = False
        self.is_flying = True
        self.state = 'flying'
        power = self.run_power / 100
        angle_rad = math.radians(self.jump_angle)
        self.velocity_x = power * 20
        self.velocity_y = -power * 15 * math.sin(angle_rad)
        jump_sound.play()
    
    def update_flying(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.5  # 重力
        self.rotation += 3
        
        # 检查是否落地
        if self.y >= SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT:
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT
            self.is_flying = False
            self.state = 'landed'
            self.target_distance = (self.x - 150) / 10  # 转换为米
            land_sound.play()
    
    def reset(self):
        self.x = 100
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - PLAYER_HEIGHT
        self.velocity_x = 0
        self.velocity_y = 0
        self.run_power = 0
        self.is_running = False
        self.is_jumping = False
        self.is_flying = False
        self.rotation = 0
        self.state = 'ready'
        self.target_distance = 0

class Game:
    def __init__(self):
        self.player = Player()
        self.level = 0
        self.score = 0
        self.best_score = 0
        self.game_over = False
        self.level_complete = False
        self.wind_speed = 0
        self.obstacles = []
        self.generate_wind()
    
    def generate_wind(self):
        self.wind_speed = random.randint(-3, 3)
    
    def generate_obstacles(self):
        self.obstacles = []
        if self.level >= 2:
            num_obstacles = min(self.level - 1, 3)
            for _ in range(num_obstacles):
                x = random.randint(300, 900)
                height = random.randint(30, 60)
                self.obstacles.append({'x': x, 'height': height})
    
    def start_level(self):
        self.player.reset()
        self.level_complete = False
        self.game_over = False
        self.generate_wind()
        self.generate_obstacles()
    
    def check_collision(self):
        for obs in self.obstacles:
            obs_rect = pygame.Rect(obs['x'], SCREEN_HEIGHT - GROUND_HEIGHT - obs['height'], 30, obs['height'])
            player_rect = pygame.Rect(self.player.x, self.player.y, PLAYER_WIDTH, PLAYER_HEIGHT)
            if player_rect.colliderect(obs_rect):
                return True
        return False
    
    def update(self):
        if self.player.state == 'running':
            self.player.update_run()
        elif self.player.state == 'flying':
            # 应用风力
            self.player.velocity_x += self.wind_speed * 0.05
            self.player.update_flying()
            
            # 检查障碍物碰撞
            if self.check_collision():
                self.player.state = 'landed'
                self.player.target_distance = max(0, (self.player.x - 150) / 10)
                land_sound.play()
        
        if self.player.state == 'landed':
            # 更新最高分
            if self.player.target_distance > self.best_score:
                self.best_score = self.player.target_distance
            
            # 检查是否完成关卡
            if self.player.target_distance >= LEVEL_TARGETS[self.level]:
                self.level_complete = True
                success_sound.play()
                self.score += int(self.player.target_distance * 10)
            else:
                self.game_over = True
                fail_sound.play()

    def draw(self):
        # 绘制背景
        screen.fill(BLUE)
        
        # 绘制云朵
        for i in range(5):
            x = (i * 250 + pygame.time.get_ticks() // 50) % (SCREEN_WIDTH + 100) - 50
            pygame.draw.ellipse(screen, WHITE, (x, 50 + i * 20, 60, 30))
            pygame.draw.ellipse(screen, WHITE, (x + 20, 40 + i * 20, 50, 40))
        
        # 绘制地面
        pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        
        # 绘制沙坑
        pygame.draw.rect(screen, BROWN, (150, SCREEN_HEIGHT - GROUND_HEIGHT + 10, 900, GROUND_HEIGHT - 20))
        
        # 绘制助跑区域
        pygame.draw.rect(screen, (200, 200, 200), (50, SCREEN_HEIGHT - GROUND_HEIGHT - 5, 100, 5))
        
        # 绘制起跳线
        pygame.draw.line(screen, RED, (150, SCREEN_HEIGHT - GROUND_HEIGHT), (150, SCREEN_HEIGHT - GROUND_HEIGHT - 30), 3)
        
        # 绘制距离标记
        for i in range(11):
            x = 150 + i * 90
            meters = i * 9
            pygame.draw.line(screen, WHITE, (x, SCREEN_HEIGHT - GROUND_HEIGHT), (x, SCREEN_HEIGHT - GROUND_HEIGHT + 5))
            text = small_font.render(f"{meters}m", True, WHITE)
            screen.blit(text, (x - 15, SCREEN_HEIGHT - GROUND_HEIGHT + 10))
        
        # 绘制障碍物
        for obs in self.obstacles:
            pygame.draw.rect(screen, BROWN, (obs['x'], SCREEN_HEIGHT - GROUND_HEIGHT - obs['height'], 30, obs['height']))
            pygame.draw.polygon(screen, RED, [
                (obs['x'], SCREEN_HEIGHT - GROUND_HEIGHT - obs['height']),
                (obs['x'] + 15, SCREEN_HEIGHT - GROUND_HEIGHT - obs['height'] - 15),
                (obs['x'] + 30, SCREEN_HEIGHT - GROUND_HEIGHT - obs['height'])
            ])
        
        # 绘制风力指示
        wind_text = small_font.render(f"风力: {self.wind_speed:+} m/s", True, WHITE)
        screen.blit(wind_text, (SCREEN_WIDTH - 150, 20))
        
        # 绘制玩家
        if self.player.is_flying:
            player_surface = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(player_surface, ORANGE, (0, 0, PLAYER_WIDTH, PLAYER_HEIGHT))
            pygame.draw.circle(player_surface, YELLOW, (PLAYER_WIDTH//2, 10), 10)
            rotated_surface = pygame.transform.rotate(player_surface, self.player.rotation)
            screen.blit(rotated_surface, (self.player.x, self.player.y))
        else:
            # 站立或跑步姿势
            pygame.draw.rect(screen, ORANGE, (self.player.x, self.player.y, PLAYER_WIDTH, PLAYER_HEIGHT))
            pygame.draw.circle(screen, YELLOW, (self.player.x + PLAYER_WIDTH//2, self.player.y + 12), 12)
        
        # 绘制力度条
        power_bar_width = 200
        power_bar_height = 20
        power_bar_x = SCREEN_WIDTH - 220
        power_bar_y = 60
        pygame.draw.rect(screen, (50, 50, 50), (power_bar_x, power_bar_y, power_bar_width, power_bar_height))
        power_fill = (self.player.run_power / self.player.max_power) * power_bar_width
        power_color = GREEN if power_fill < power_bar_width * 0.7 else YELLOW if power_fill < power_bar_width * 0.9 else RED
        pygame.draw.rect(screen, power_color, (power_bar_x, power_bar_y, power_fill, power_bar_height))
        power_text = small_font.render(f"力度: {self.player.run_power}%", True, WHITE)
        screen.blit(power_text, (power_bar_x, power_bar_y + 25))
        
        # 绘制角度条
        angle_bar_width = 200
        angle_bar_height = 15
        angle_bar_x = SCREEN_WIDTH - 220
        angle_bar_y = 120
        pygame.draw.rect(screen, (50, 50, 50), (angle_bar_x, angle_bar_y, angle_bar_width, angle_bar_height))
        angle_fill = (self.player.jump_angle / 90) * angle_bar_width
        pygame.draw.rect(screen, PURPLE, (angle_bar_x, angle_bar_y, angle_fill, angle_bar_height))
        angle_text = small_font.render(f"角度: {self.player.jump_angle}°", True, WHITE)
        screen.blit(angle_text, (power_bar_x, angle_bar_y + 20))
        
        # 绘制关卡信息
        level_text = font.render(f"关卡 {self.level + 1}", True, WHITE)
        screen.blit(level_text, (20, 20))
        
        # 绘制目标距离
        target_text = small_font.render(f"目标: {LEVEL_TARGETS[self.level]} 米", True, WHITE)
        screen.blit(target_text, (20, 65))
        
        # 绘制分数
        score_text = small_font.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 100))
        
        # 绘制最佳成绩
        best_text = small_font.render(f"最佳: {self.best_score:.1f}m", True, WHITE)
        screen.blit(best_text, (20, 135))
        
        # 绘制状态提示
        if self.player.state == 'ready':
            ready_text = font.render("按住空格键开始助跑", True, YELLOW)
            screen.blit(ready_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2))
            angle_hint = small_font.render("使用 ↑↓ 键调整跳跃角度", True, WHITE)
            screen.blit(angle_hint, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))
        elif self.player.state == 'running':
            run_text = font.render("松开空格键起跳!", True, ORANGE)
            screen.blit(run_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2))
        elif self.player.state == 'flying':
            fly_text = font.render(f"飞行中... {self.player.target_distance:.1f}米", True, WHITE)
            screen.blit(fly_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
        elif self.player.state == 'landed':
            distance_text = font.render(f"成绩: {self.player.target_distance:.1f} 米", True, YELLOW)
            screen.blit(distance_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 50))
            
            if self.level_complete:
                success_text = font.render("🎉 关卡通过! 🎉", True, GREEN)
                screen.blit(success_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
                next_text = small_font.render("按 Enter 键进入下一关", True, WHITE)
                screen.blit(next_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 50))
            else:
                fail_text = font.render("😢 未达到目标!", True, RED)
                screen.blit(fail_text, (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2))
                retry_text = small_font.render("按 Enter 键重试", True, WHITE)
                screen.blit(retry_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50))
                
                if self.level > 0:
                    giveup_text = small_font.render("按 Esc 键返回第一关", True, WHITE)
                    screen.blit(giveup_text, (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 80))

def main():
    game = Game()
    game.start_level()
    
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game.player.state == 'ready':
                    game.player.start_run()
                
                if event.key == pygame.K_UP and game.player.state == 'ready':
                    game.player.jump_angle = min(90, game.player.jump_angle + 5)
                
                if event.key == pygame.K_DOWN and game.player.state == 'ready':
                    game.player.jump_angle = max(15, game.player.jump_angle - 5)
                
                if event.key == pygame.K_RETURN:
                    if game.player.state == 'landed':
                        if game.level_complete:
                            if game.level < len(LEVEL_TARGETS) - 1:
                                game.level += 1
                                game.start_level()
                            else:
                                # 通关所有关卡
                                game.level = 0
                                game.score = 0
                                game.start_level()
                        else:
                            game.start_level()
                
                if event.key == pygame.K_ESCAPE:
                    if game.player.state == 'landed' and not game.level_complete:
                        game.level = 0
                        game.score = 0
                        game.start_level()
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and game.player.state == 'running':
                    game.player.jump()
        
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
