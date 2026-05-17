import pygame
import os
import random
import math

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

WIDTH, HEIGHT = 800, 700

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 200, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("时间控制解谜")
clock = pygame.time.Clock()
font = get_chinese_font(28)
big_font = get_chinese_font(50)
small_font = get_chinese_font(22)

class Entity:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.start_x = x
        self.start_y = y
        self.history = []
        self.radius = 15
        self.goal_x = 700
        self.goal_y = 350
    
    def move(self, dx, dy):
        self.history.append((self.x, self.y))
        self.x += dx
        self.y += dy
    
    def undo(self):
        if self.history:
            self.x, self.y = self.history.pop()
    
    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.history = []
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)

class Level:
    def __init__(self, num):
        self.num = num
        
        if num == 1:
            self.player = Entity(100, 350, GREEN)
            self.obstacles = [(400, 300, 50, 200)]
            self.description = "绕过障碍物到达终点"
        elif num == 2:
            self.player = Entity(100, 350, GREEN)
            self.player2 = Entity(100, 450, BLUE)
            self.obstacles = [(300, 250, 50, 200), (500, 250, 50, 200)]
            self.description = "两个角色同时到达"
        elif num == 3:
            self.player = Entity(100, 300, GREEN)
            self.player2 = Entity(100, 400, BLUE)
            self.obstacles = [(300, 200, 50, 150), (400, 350, 50, 150), (500, 200, 50, 150)]
            self.description = "配合通过障碍"
        elif num == 4:
            self.player = Entity(100, 350, GREEN)
            self.player2 = Entity(100, 300, BLUE)
            self.switches = [(250, 350), (550, 350)]
            self.doors = [(400, 250, 50, 30)]
            self.obstacles = []
            self.description = "踩开关打开门"
        else:
            self.player = Entity(100, 350, GREEN)
            self.obstacles = [(250, 200, 30, 300), (400, 200, 30, 300), (550, 200, 30, 300)]
            self.description = "最终挑战"

class TimeGame:
    def __init__(self):
        self.current_level = 1
        self.max_levels = 5
        self.recording = True
        self.playback = False
        self.playback_frame = 0
        self.time_factor = 1
        self.game_state = "playing"

def time_manipulation():
    game = TimeGame()
    
    while game.current_level <= game.max_levels:
        level = Level(game.current_level)
        
        if not hasattr(level, 'player2'):
            level.player2 = None
        if not hasattr(level, 'switches'):
            level.switches = []
        if not hasattr(level, 'doors'):
            level.doors = []
        
        running = True
        
        while running:
            screen.fill(BLACK)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        game.current_level = game.max_levels + 1
                    elif event.key == pygame.K_r:
                        level.player.reset()
                        if level.player2:
                            level.player2.reset()
                        game.recording = True
                        game.playback = False
                    elif event.key == pygame.K_u:
                        level.player.undo()
                        if level.player2:
                            level.player2.undo()
                    elif event.key == pygame.K_w:
                        level.player.move(0, -10)
                    elif event.key == pygame.K_s:
                        level.player.move(0, 10)
                    elif event.key == pygame.K_a:
                        level.player.move(-10, 0)
                    elif event.key == pygame.K_d:
                        level.player.move(10, 0)
                    elif event.key == pygame.K_i:
                        if level.player2:
                            level.player2.move(0, -10)
                    elif event.key == pygame.K_k:
                        if level.player2:
                            level.player2.move(0, 10)
                    elif event.key == pygame.K_j:
                        if level.player2:
                            level.player2.move(-10, 0)
                    elif event.key == pygame.K_l:
                        if level.player2:
                            level.player2.move(10, 0)
                    elif event.key == pygame.K_1:
                        game.time_factor = -1
                    elif event.key == pygame.K_2:
                        game.time_factor = 0
                    elif event.key == pygame.K_3:
                        game.time_factor = 1
                    elif event.key == pygame.K_4:
                        game.time_factor = 3
            
            for obs in level.obstacles:
                pygame.draw.rect(screen, RED, obs)
            
            for switch in level.switches:
                pygame.draw.circle(screen, YELLOW, switch, 20)
            
            for door in level.doors:
                pygame.draw.rect(screen, PURPLE, door)
            
            goal = pygame.Rect(level.player.goal_x - 30, level.player.goal_y - 30, 60, 60)
            pygame.draw.rect(screen, GREEN, goal, 3)
            
            if level.player:
                level.player.draw()
            if level.player2:
                level.player2.draw()
            
            if level.player and not level.player2:
                dist = ((level.player.x - level.player.goal_x)**2 + (level.player.y - level.player.goal_y)**2)**0.5
                if dist < 30:
                    running = False
                    game.current_level += 1
            
            elif level.player and level.player2:
                d1 = ((level.player.x - level.player.goal_x)**2 + (level.player.y - level.player.goal_y)**2)**0.5
                d2 = ((level.player2.x - level.player2.goal_x)**2 + (level.player2.y - level.player2.goal_y)**2)**0.5
                if d1 < 30 and d2 < 30:
                    running = False
                    game.current_level += 1
            
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 60))
            
            level_text = font.render(f"关卡 {game.current_level}/{game.max_levels}", True, YELLOW)
            screen.blit(level_text, (10, 20))
            
            desc = small_font.render(level.description, True, WHITE)
            screen.blit(desc, (200, 20))
            
            time_text = font.render(f"时间: {game.time_factor}x (1.倒带 2.暂停 3.正常 4.快进)", True, 
                                 GREEN if game.time_factor > 0 else RED if game.time_factor < 0 else WHITE)
            screen.blit(time_text, (500, 20))
            
            instructions = small_font.render("WASD移动 | U撤销 | R重置 | 1-4时间控制", True, WHITE)
            screen.blit(instructions, (10, HEIGHT - 30))
            
            pygame.display.flip()
            clock.tick(60)
    
    screen.fill(BLACK)
    result = big_font.render("恭喜通关!", True, YELLOW)
    screen.blit(result, (WIDTH // 2 - 100, HEIGHT // 2 - 30))
    complete = font.render("你掌握了时间的力量!", True, GREEN)
    screen.blit(complete, (WIDTH // 2 - 100, HEIGHT // 2 + 30))
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    time_manipulation()
