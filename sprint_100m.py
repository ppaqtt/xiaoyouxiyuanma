import pygame
import sys
import random
import math

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 500
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# 跑道颜色
TRACK_COLORS = [
    (100, 100, 100),
    (80, 80, 80),
]

# 玩家颜色
PLAYER_COLORS = [
    (255, 0, 0),
    (0, 0, 255),
    (0, 255, 0),
    (255, 255, 0),
    (255, 165, 0),
]

# 创建屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("100米短跑")

# 创建时钟对象
clock = pygame.time.Clock()

# 音效生成函数
def generate_sound(frequency, duration, volume=0.1):
    sample_rate = 44100
    samples = int(sample_rate * duration)
    sound_data = bytearray()
    
    for i in range(samples):
        t = i / sample_rate
        value = int(127 * volume * (math.sin(2 * math.pi * frequency * t)))
        sound_data.append(value + 128)
    
    sound = pygame.mixer.Sound(sound_data)
    return sound

# 生成游戏音效
start_sound = generate_sound(800, 0.3)
beep_sound = generate_sound(1000, 0.2)
race_sound = generate_sound(200, 0.1)
win_sound = generate_sound(523, 0.2)
error_sound = generate_sound(200, 0.3)

class Player:
    def __init__(self, name, color, lane):
        self.name = name
        self.color = color
        self.lane = lane
        self.x = 50
        self.y = 80 + lane * 80
        self.width = 40
        self.height = 60
        self.speed = 0
        self.max_speed = 8
        self.acceleration = 0.3
        self.last_key = None
        self.state = 'ready'  # ready, set, racing, finished
        self.start_time = 0
        self.end_time = 0
        self.reaction_time = 0
        self.has_started = False
        self.finished = False
    
    def reset(self):
        self.x = 50
        self.speed = 0
        self.last_key = None
        self.state = 'ready'
        self.start_time = 0
        self.end_time = 0
        self.reaction_time = 0
        self.has_started = False
        self.finished = False
    
    def update(self, key_pressed, current_time):
        if self.state == 'ready' or self.state == 'set':
            if key_pressed and self.state == 'ready':
                self.state = 'false_start'
                return
            
        if self.state == 'racing':
            if key_pressed and not self.has_started:
                self.has_started = True
                self.start_time = current_time
                self.reaction_time = current_time - game.start_signal_time
            
            if self.has_started and not self.finished:
                if key_pressed:
                    if key_pressed != self.last_key:
                        self.speed = min(self.speed + self.acceleration, self.max_speed)
                        self.last_key = key_pressed
                    else:
                        self.speed = max(self.speed - 0.2, 0)
                
                self.x += self.speed
                
                if self.x >= SCREEN_WIDTH - 50:
                    self.x = SCREEN_WIDTH - 50
                    self.finished = True
                    self.end_time = current_time
    
    def draw(self):
        # 绘制运动员
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # 绘制头部
        pygame.draw.circle(screen, (255, 200, 150), (self.x + self.width//2, self.y + 15), 12)
        # 绘制跑道线
        pygame.draw.line(screen, WHITE, (self.x + self.width, self.y), 
                        (self.x + self.width, self.y + self.height), 2)

class Game:
    def __init__(self):
        self.players = []
        self.game_state = 'menu'  # menu, choosing_players, ready, set, go, racing, finished
        self.start_signal_time = 0
        self.winners = []
        self.best_record = float('inf')
        self.selected_players = 1
        self.keys_pressed = {}
        
        # 初始化玩家
        for i in range(4):
            self.players.append(Player(f"玩家{i+1}", PLAYER_COLORS[i], i))
    
    def reset_game(self):
        for player in self.players:
            player.reset()
        self.winners = []
        self.game_state = 'ready'
    
    def draw_track(self):
        # 绘制跑道
        for lane in range(5):
            y = 60 + lane * 80
            color = TRACK_COLORS[lane % 2]
            pygame.draw.rect(screen, color, (0, y, SCREEN_WIDTH, 70))
        
        # 绘制起跑线
        pygame.draw.line(screen, WHITE, (50, 60), (50, 460), 3)
        pygame.draw.line(screen, WHITE, (53, 60), (53, 460), 2)
        
        # 绘制终点线
        pygame.draw.line(screen, RED, (SCREEN_WIDTH - 50, 60), (SCREEN_WIDTH - 50, 460), 3)
        for i in range(0, 70, 10):
            pygame.draw.line(screen, RED, (SCREEN_WIDTH - 55, 60 + i), 
                           (SCREEN_WIDTH - 45, 60 + i), 3)
        
        # 绘制跑道数字
        font = pygame.font.Font(None, 24)
        for lane in range(4):
            text = font.render(f"{lane + 1}", True, WHITE)
            screen.blit(text, (20, 85 + lane * 80))
    
    def draw_menu(self):
        screen.fill(BLACK)
        
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 24)
        
        title = font_large.render("100米短跑", True, RED)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
        
        # 玩家选择
        players_text = font_medium.render(f"玩家数量: {self.selected_players}", True, WHITE)
        screen.blit(players_text, (SCREEN_WIDTH//2 - players_text.get_width()//2, 200))
        
        plus_button = pygame.Rect(SCREEN_WIDTH//2 + 100, 195, 50, 40)
        minus_button = pygame.Rect(SCREEN_WIDTH//2 - 150, 195, 50, 40)
        
        pygame.draw.rect(screen, BLUE, plus_button)
        pygame.draw.rect(screen, BLUE, minus_button)
        
        plus_text = font_large.render("+", True, WHITE)
        minus_text = font_large.render("-", True, WHITE)
        screen.blit(plus_text, (SCREEN_WIDTH//2 + 115, 185))
        screen.blit(minus_text, (SCREEN_WIDTH//2 - 130, 185))
        
        start_button = pygame.Rect(SCREEN_WIDTH//2 - 100, 300, 200, 60)
        pygame.draw.rect(screen, GREEN, start_button)
        start_text = font_medium.render("开始比赛", True, BLACK)
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 315))
        
        instructions = [
            "游戏说明:",
            "1. 使用 ← → 箭头键交替按键加速",
            "2. 在 'GO!' 出现后开始按键",
            "3. 过早按键会被判犯规",
            "4. 保持按键节奏获得最高速度",
            "5. 冲过终点线完成比赛"
        ]
        
        y = 400
        for line in instructions:
            text = font_small.render(line, True, (150, 150, 150))
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y))
            y += 25
        
        return {'plus': plus_button, 'minus': minus_button, 'start': start_button}
    
    def draw_ready_set_go(self):
        self.draw_track()
        
        font_large = pygame.font.Font(None, 96)
        font_medium = pygame.font.Font(None, 36)
        
        if self.game_state == 'ready':
            text = font_large.render("准备...", True, YELLOW)
        elif self.game_state == 'set':
            text = font_large.render("各就各位...", True, ORANGE)
        elif self.game_state == 'go':
            text = font_large.render("GO!", True, GREEN)
        
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        for i, player in enumerate(self.players[:self.selected_players]):
            player.draw()
            if player.state == 'false_start':
                false_text = font_medium.render("犯规!", True, RED)
                screen.blit(false_text, (player.x, player.y - 30))
    
    def draw_racing(self):
        self.draw_track()
        
        font_small = pygame.font.Font(None, 24)
        
        for i, player in enumerate(self.players[:self.selected_players]):
            player.draw()
            
            # 显示速度条
            speed_bar_width = 50
            speed_bar_height = 6
            speed_ratio = player.speed / player.max_speed
            pygame.draw.rect(screen, (50, 50, 50), (player.x, player.y - 20, speed_bar_width, speed_bar_height))
            pygame.draw.rect(screen, GREEN, (player.x, player.y - 20, speed_bar_width * speed_ratio, speed_bar_height))
            
            # 显示反应时间（如果已起跑）
            if player.has_started and not player.finished:
                time = font_small.render(f"{player.reaction_time:.2f}s", True, WHITE)
                screen.blit(time, (player.x, player.y - 40))
    
    def draw_finished(self):
        self.draw_track()
        
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 24)
        
        # 绘制结果面板
        panel_width = 400
        panel_height = 300
        panel_x = SCREEN_WIDTH//2 - panel_width//2
        panel_y = SCREEN_HEIGHT//2 - panel_height//2
        
        pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 3)
        
        title = font_large.render("比赛结果", True, GREEN)
        screen.blit(title, (panel_x + panel_width//2 - title.get_width()//2, panel_y + 20))
        
        # 排序玩家按完成时间
        sorted_players = sorted(self.players[:self.selected_players], key=lambda p: p.end_time if p.finished else float('inf'))
        
        y = panel_y + 70
        for rank, player in enumerate(sorted_players, 1):
            if player.finished:
                time = (player.end_time - player.start_time) / 1000
                reaction = player.reaction_time / 1000
                
                if rank == 1:
                    color = YELLOW
                elif rank == 2:
                    color = (192, 192, 192)
                elif rank == 3:
                    color = (210, 105, 30)
                else:
                    color = WHITE
                
                rank_text = font_medium.render(f"{rank}. {player.name}", True, color)
                time_text = font_medium.render(f"{time:.3f}s", True, WHITE)
                reaction_text = font_small.render(f"反应: {reaction:.2f}s", True, (150, 150, 150))
                
                screen.blit(rank_text, (panel_x + 20, y))
                screen.blit(time_text, (panel_x + panel_width - 120, y))
                screen.blit(reaction_text, (panel_x + 20, y + 30))
                
                # 更新最佳记录
                if rank == 1 and time < self.best_record:
                    self.best_record = time
                
                y += 50
        
        # 显示最佳记录
        if self.best_record != float('inf'):
            record_text = font_small.render(f"最佳记录: {self.best_record:.3f}s", True, GREEN)
            screen.blit(record_text, (panel_x + panel_width//2 - record_text.get_width()//2, panel_y + panel_height - 40))
        
        # 绘制返回按钮
        restart_button = pygame.Rect(panel_x + panel_width//2 - 80, panel_y + panel_height - 80, 160, 40)
        pygame.draw.rect(screen, BLUE, restart_button)
        restart_text = font_medium.render("再玩一次", True, WHITE)
        screen.blit(restart_text, (panel_x + panel_width//2 - restart_text.get_width()//2, panel_y + panel_height - 75))
        
        return restart_button
    
    def run(self):
        while True:
            current_time = pygame.time.get_ticks()
            screen.fill(BLACK)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.game_state == 'menu':
                        buttons = self.draw_menu()
                        if buttons['plus'].collidepoint(mouse_pos):
                            self.selected_players = min(self.selected_players + 1, 4)
                        elif buttons['minus'].collidepoint(mouse_pos):
                            self.selected_players = max(self.selected_players - 1, 1)
                        elif buttons['start'].collidepoint(mouse_pos):
                            self.reset_game()
                            beep_sound.play()
                    
                    elif self.game_state == 'finished':
                        restart_button = self.draw_finished()
                        if restart_button.collidepoint(mouse_pos):
                            self.game_state = 'menu'
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        self.keys_pressed[event.key] = current_time
                        
                        if self.game_state == 'racing':
                            race_sound.play()
                
                if event.type == pygame.KEYUP:
                    if event.key in self.keys_pressed:
                        del self.keys_pressed[event.key]
            
            # 游戏状态管理
            if self.game_state == 'ready':
                if current_time - self.start_signal_time > 1000:
                    self.game_state = 'set'
                    beep_sound.play()
            
            elif self.game_state == 'set':
                if current_time - self.start_signal_time > 2500:
                    self.game_state = 'go'
                    start_sound.play()
                    self.start_signal_time = current_time
                    self.game_state = 'racing'
            
            elif self.game_state == 'racing':
                # 检查是否所有玩家都完成
                finished_count = sum(1 for p in self.players[:self.selected_players] if p.finished)
                if finished_count == self.selected_players:
                    self.game_state = 'finished'
                    win_sound.play()
            
            # 更新玩家
            for i, player in enumerate(self.players[:self.selected_players]):
                if self.game_state == 'racing':
                    key_pressed = None
                    if pygame.K_LEFT in self.keys_pressed:
                        key_pressed = 'left'
                    elif pygame.K_RIGHT in self.keys_pressed:
                        key_pressed = 'right'
                    player.update(key_pressed, current_time)
            
            # 绘制
            if self.game_state == 'menu':
                self.draw_menu()
            elif self.game_state in ['ready', 'set', 'go']:
                self.draw_ready_set_go()
            elif self.game_state == 'racing':
                self.draw_racing()
            elif self.game_state == 'finished':
                self.draw_finished()
            
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
