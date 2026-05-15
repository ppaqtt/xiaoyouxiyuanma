import pygame
import sys
import math
import time

# 初始化Pygame
pygame.init()

# 游戏配置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
GRAY = (128, 128, 128)

# 格子颜色映射
CELL_COLORS = [RED, BLUE, GREEN, YELLOW, ORANGE, PURPLE, CYAN, PINK, GRAY]

# 关卡配置
LEVELS = [
    {"name": "初级", "sequence": [1, 2, 3, 4, 5, 6, 7, 8, 9], "time_limit": 60},
    {"name": "中级", "sequence": [1, 3, 5, 7, 9, 2, 4, 6, 8], "time_limit": 45},
    {"name": "高级", "sequence": [5, 3, 7, 1, 9, 2, 8, 4, 6], "time_limit": 30},
    {"name": "专家", "sequence": [9, 7, 5, 3, 1, 2, 4, 6, 8], "time_limit": 25},
    {"name": "大师", "sequence": [1, 9, 2, 8, 3, 7, 4, 6, 5], "time_limit": 20}
]

class SoundManager:
    """音效管理器 - 使用bytearray生成音效"""
    
    def __init__(self):
        self.sample_rate = 44100
        pygame.mixer.set_init(self.sample_rate, -16, 2, 4096)
    
    def generate_tone(self, frequency, duration, volume=0.5):
        """生成单音音效"""
        samples = int(self.sample_rate * duration)
        arr = bytearray(samples * 2)
        for i in range(samples):
            t = i / self.sample_rate
            value = int(volume * 32767 * math.sin(2 * math.pi * frequency * t))
            arr[2*i] = value & 0xff
            arr[2*i+1] = (value >> 8) & 0xff
        
        sound = pygame.mixer.Sound(arr)
        return sound
    
    def play_jump_sound(self):
        """跳跃音效"""
        sound = self.generate_tone(440, 0.1)
        sound.play()
    
    def play_correct_sound(self):
        """正确跳跃音效"""
        sound = self.generate_tone(523, 0.15)
        sound.play()
    
    def play_wrong_sound(self):
        """错误跳跃音效"""
        sound = self.generate_tone(200, 0.3)
        sound.play()
    
    def play_win_sound(self):
        """胜利音效"""
        frequencies = [523, 659, 784, 1047]
        for freq in frequencies:
            sound = self.generate_tone(freq, 0.2)
            sound.play()
            pygame.time.delay(200)
    
    def play_level_sound(self):
        """关卡切换音效"""
        frequencies = [440, 554, 659, 880]
        for freq in frequencies:
            sound = self.generate_tone(freq, 0.15)
            sound.play()
            pygame.time.delay(150)

class HopscotchGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("跳房子游戏")
        
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        
        self.reset_game()
    
    def reset_game(self):
        """重置游戏状态"""
        self.current_level = 0
        self.current_position = 0  # 0表示起点
        self.current_step = 0
        self.game_state = "menu"  # menu, playing, paused, win, lose
        self.start_time = 0
        self.elapsed_time = 0
        self.best_times = [0] * len(LEVELS)
    
    def draw_grid(self):
        """绘制跳房子格子"""
        # 格子布局 - 3行3列
        cell_size = 100
        margin = 40
        start_x = (SCREEN_WIDTH - 3 * cell_size - 2 * margin) // 2
        start_y = 150
        
        for i in range(3):
            for j in range(3):
                cell_num = i * 3 + j + 1
                x = start_x + j * (cell_size + margin)
                y = start_y + i * (cell_size + margin)
                
                # 绘制格子背景
                color = CELL_COLORS[cell_num - 1]
                pygame.draw.rect(self.screen, color, (x, y, cell_size, cell_size))
                
                # 绘制格子边框
                pygame.draw.rect(self.screen, BLACK, (x, y, cell_size, cell_size), 3)
                
                # 绘制数字
                font = pygame.font.Font(None, 64)
                text = font.render(str(cell_num), True, WHITE)
                text_rect = text.get_rect(center=(x + cell_size//2, y + cell_size//2))
                self.screen.blit(text, text_rect)
        
        # 绘制起点
        start_color = BLUE
        pygame.draw.rect(self.screen, start_color, (start_x + cell_size + margin - 50, start_y + 3 * (cell_size + margin) + 20, 100, 60))
        pygame.draw.rect(self.screen, BLACK, (start_x + cell_size + margin - 50, start_y + 3 * (cell_size + margin) + 20, 100, 60), 3)
        
        font = pygame.font.Font(None, 36)
        text = font.render("起点", True, WHITE)
        text_rect = text.get_rect(center=(start_x + cell_size + margin, start_y + 3 * (cell_size + margin) + 50))
        self.screen.blit(text, text_rect)
    
    def draw_player(self):
        """绘制玩家位置"""
        cell_size = 100
        margin = 40
        start_x = (SCREEN_WIDTH - 3 * cell_size - 2 * margin) // 2
        start_y = 150
        
        if self.current_position == 0:
            # 在起点
            x = start_x + cell_size + margin
            y = start_y + 3 * (cell_size + margin) + 50
        else:
            # 在格子上
            row = (self.current_position - 1) // 3
            col = (self.current_position - 1) % 3
            x = start_x + col * (cell_size + margin) + cell_size // 2
            y = start_y + row * (cell_size + margin) + cell_size // 2
        
        # 绘制玩家（黄色圆圈）
        pygame.draw.circle(self.screen, YELLOW, (x, y), 25)
        pygame.draw.circle(self.screen, BLACK, (x, y), 25, 3)
    
    def draw_hud(self):
        """绘制游戏界面信息"""
        font = pygame.font.Font(None, 36)
        
        # 当前关卡
        level_info = LEVELS[self.current_level]
        text = font.render(f"关卡: {level_info['name']}", True, BLACK)
        self.screen.blit(text, (20, 20))
        
        # 当前进度
        progress = font.render(f"进度: {self.current_step + 1}/{len(level_info['sequence'])}", True, BLACK)
        self.screen.blit(progress, (20, 60))
        
        # 计时器
        time_left = max(0, level_info['time_limit'] - self.elapsed_time)
        time_color = GREEN if time_left > 10 else RED
        time_text = font.render(f"时间: {int(time_left)}秒", True, time_color)
        self.screen.blit(time_text, (SCREEN_WIDTH - 180, 20))
        
        # 最佳时间
        if self.best_times[self.current_level] > 0:
            best_text = font.render(f"最佳: {self.best_times[self.current_level]:.1f}秒", True, BLUE)
            self.screen.blit(best_text, (SCREEN_WIDTH - 200, 60))
    
    def draw_menu(self):
        """绘制主菜单"""
        self.screen.fill(WHITE)
        
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
        # 标题
        title = font_large.render("跳房子游戏", True, BLUE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        # 游戏说明
        instructions = [
            "游戏规则：",
            "1. 使用数字键盘1-9控制跳跃位置",
            "2. 按顺序跳到正确的格子",
            "3. 踩错格子需要重新开始",
            "4. 在规定时间内完成所有格子获胜",
            "",
            "选择关卡开始游戏："
        ]
        
        y = 200
        for line in instructions:
            text = font_small.render(line, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y))
            self.screen.blit(text, text_rect)
            y += 40
        
        # 关卡选择按钮
        y = 380
        for i, level in enumerate(LEVELS):
            button_x = SCREEN_WIDTH // 2 - 150
            button_y = y + i * 60
            
            # 按钮背景
            pygame.draw.rect(self.screen, CELL_COLORS[i], (button_x, button_y, 300, 50))
            pygame.draw.rect(self.screen, BLACK, (button_x, button_y, 300, 50), 3)
            
            # 按钮文字
            text = font_medium.render(f"{i+1}. {level['name']} - {level['time_limit']}秒", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, button_y + 25))
            self.screen.blit(text, text_rect)
    
    def draw_win_screen(self):
        """绘制胜利界面"""
        self.screen.fill(GREEN)
        
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
        # 胜利文字
        title = font_large.render("恭喜过关！", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title, title_rect)
        
        # 用时信息
        time_text = font_medium.render(f"完成时间: {self.elapsed_time:.1f}秒", True, WHITE)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        self.screen.blit(time_text, time_rect)
        
        # 下一关提示
        if self.current_level < len(LEVELS) - 1:
            next_level = LEVELS[self.current_level + 1]
            next_text = font_small.render(f"下一关: {next_level['name']}", True, WHITE)
            next_rect = next_text.get_rect(center=(SCREEN_WIDTH//2, 330))
            self.screen.blit(next_text, next_rect)
            
            continue_text = font_small.render("按 Enter 进入下一关", True, YELLOW)
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, 400))
            self.screen.blit(continue_text, continue_rect)
        else:
            complete_text = font_medium.render("🎉 恭喜通关所有关卡！", True, YELLOW)
            complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, 330))
            self.screen.blit(complete_text, complete_rect)
        
        # 返回菜单
        menu_text = font_small.render("按 M 返回主菜单", True, WHITE)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH//2, 480))
        self.screen.blit(menu_text, menu_rect)
    
    def draw_lose_screen(self):
        """绘制失败界面"""
        self.screen.fill(RED)
        
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
        # 失败文字
        title = font_large.render("游戏失败", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(title, title_rect)
        
        # 失败原因
        level_info = LEVELS[self.current_level]
        time_left = level_info['time_limit'] - self.elapsed_time
        if time_left <= 0:
            reason = font_medium.render("时间用完了！", True, WHITE)
        else:
            reason = font_medium.render("踩错格子了！", True, WHITE)
        
        reason_rect = reason.get_rect(center=(SCREEN_WIDTH//2, 300))
        self.screen.blit(reason, reason_rect)
        
        # 重试提示
        retry_text = font_small.render("按 R 重新开始本关", True, YELLOW)
        retry_rect = retry_text.get_rect(center=(SCREEN_WIDTH//2, 400))
        self.screen.blit(retry_text, retry_rect)
        
        # 返回菜单
        menu_text = font_small.render("按 M 返回主菜单", True, WHITE)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH//2, 470))
        self.screen.blit(menu_text, menu_rect)
    
    def start_level(self, level_index):
        """开始指定关卡"""
        self.current_level = level_index
        self.current_position = 0
        self.current_step = 0
        self.game_state = "playing"
        self.start_time = time.time()
        self.elapsed_time = 0
        self.sound_manager.play_level_sound()
    
    def jump_to(self, target):
        """跳跃到指定格子"""
        level_info = LEVELS[self.current_level]
        
        if self.current_step < len(level_info['sequence']):
            correct_target = level_info['sequence'][self.current_step]
            
            if target == correct_target:
                # 跳对了
                self.current_position = target
                self.current_step += 1
                self.sound_manager.play_correct_sound()
                
                if self.current_step >= len(level_info['sequence']):
                    # 完成关卡
                    self.game_state = "win"
                    self.sound_manager.play_win_sound()
                    # 更新最佳时间
                    if self.best_times[self.current_level] == 0 or self.elapsed_time < self.best_times[self.current_level]:
                        self.best_times[self.current_level] = self.elapsed_time
            else:
                # 跳错了
                self.sound_manager.play_wrong_sound()
                self.game_state = "lose"
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.game_state == "menu":
                    # 菜单界面 - 数字键选择关卡
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                        level_index = event.key - pygame.K_1
                        if level_index < len(LEVELS):
                            self.start_level(level_index)
                
                elif self.game_state == "playing":
                    # 游戏中 - 数字键控制跳跃
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                                    pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                        target = event.key - pygame.K_0
                        self.sound_manager.play_jump_sound()
                        self.jump_to(target)
                
                elif self.game_state == "win":
                    # 胜利界面
                    if event.key == pygame.K_RETURN:
                        if self.current_level < len(LEVELS) - 1:
                            self.start_level(self.current_level + 1)
                    elif event.key == pygame.K_m:
                        self.reset_game()
                
                elif self.game_state == "lose":
                    # 失败界面
                    if event.key == pygame.K_r:
                        self.start_level(self.current_level)
                    elif event.key == pygame.K_m:
                        self.reset_game()
    
    def update(self):
        """更新游戏状态"""
        if self.game_state == "playing":
            self.elapsed_time = time.time() - self.start_time
            
            # 检查时间是否用完
            if self.elapsed_time >= LEVELS[self.current_level]['time_limit']:
                self.game_state = "lose"
                self.sound_manager.play_wrong_sound()
    
    def render(self):
        """渲染游戏画面"""
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "playing":
            self.screen.fill(WHITE)
            self.draw_grid()
            self.draw_player()
            self.draw_hud()
        elif self.game_state == "win":
            self.draw_win_screen()
        elif self.game_state == "lose":
            self.draw_lose_screen()
        
        pygame.display.flip()
    
    def run(self):
        """游戏主循环"""
        while True:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = HopscotchGame()
    game.run()
