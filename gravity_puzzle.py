import pygame
import os
import random

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

WIDTH, HEIGHT = 800, 600
GRID_SIZE = 40
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)
PURPLE = (128, 0, 128)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("重力反转解谜")
clock = pygame.time.Clock()
font = get_chinese_font(32)
big_font = get_chinese_font(50)
small_font = get_chinese_font(24)

LEVELS = [
    {
        "platforms": [
            (0, 14, 20, 1), (0, 0, 1, 15), (19, 0, 1, 15),
            (5, 10, 5, 1), (10, 6, 5, 1), (5, 3, 5, 1)
        ],
        "player_start": (2, 12),
        "exit_pos": (16, 2),
        "keys": 0
    },
    {
        "platforms": [
            (0, 14, 20, 1), (0, 0, 1, 15), (19, 0, 1, 15),
            (3, 11, 4, 1), (8, 8, 4, 1), (13, 5, 4, 1), (8, 2, 4, 1)
        ],
        "player_start": (2, 12),
        "exit_pos": (16, 2),
        "keys": 1
    },
    {
        "platforms": [
            (0, 14, 20, 1), (0, 0, 1, 15), (19, 0, 1, 15),
            (2, 11, 3, 1), (6, 8, 3, 1), (10, 5, 3, 1),
            (14, 8, 3, 1), (10, 2, 3, 1), (2, 5, 3, 1)
        ],
        "player_start": (2, 12),
        "exit_pos": (16, 2),
        "keys": 2
    }
]

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.vy = 0
        self.gravity = 1
        self.on_ground = False
        self.gravity_dir = 1
    
    def update(self, platforms, keys_collected):
        self.vy += 0.5 * self.gravity_dir
        
        if abs(self.vy) > 12:
            self.vy = 12 * self.gravity_dir
        
        next_y = self.y + self.vy
        
        for platform in platforms:
            px, py, pw, ph = platform
            px_world = px * GRID_SIZE
            py_world = py * GRID_SIZE
            pw_world = pw * GRID_SIZE
            ph_world = ph * GRID_SIZE
            
            if (self.x + self.radius > px_world and 
                self.x - self.radius < px_world + pw_world):
                if self.gravity_dir == 1:
                    if self.y + self.radius <= py_world and next_y + self.radius >= py_world:
                        self.y = py_world - self.radius
                        self.vy = 0
                        self.on_ground = True
                    elif self.y - self.radius >= py_world + ph_world and next_y - self.radius <= py_world + ph_world:
                        self.y = py_world + ph_world + self.radius
                        self.vy = 0
                else:
                    if self.y - self.radius >= py_world + ph_world and next_y - self.radius <= py_world + ph_world:
                        self.y = py_world + ph_world + self.radius
                        self.vy = 0
                        self.on_ground = True
                    elif self.y + self.radius <= py_world and next_y + self.radius >= py_world:
                        self.y = py_world - self.radius
                        self.vy = 0
            else:
                self.on_ground = False
        
        self.y = next_y
        
        if self.x - self.radius < 0:
            self.x = self.radius
        if self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
        if self.y - self.radius < 0:
            self.y = self.radius
        if self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius

class Key:
    def __init__(self, x, y):
        self.x = x * GRID_SIZE + GRID_SIZE // 2
        self.y = y * GRID_SIZE + GRID_SIZE // 2
        self.collected = False
    
    def draw(self):
        if not self.collected:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), 10)
            pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), 10, 2)

def gravity_puzzle():
    current_level = 0
    keys_collected = 0
    
    while current_level < len(LEVELS):
        level = LEVELS[current_level]
        player = Player(level["player_start"][0] * GRID_SIZE + GRID_SIZE // 2,
                       level["player_start"][1] * GRID_SIZE)
        
        keys = []
        for _ in range(level["keys"]):
            kx = random.randint(2, GRID_WIDTH - 3)
            ky = random.randint(2, GRID_HEIGHT - 3)
            keys.append(Key(kx, ky))
        
        exit_x = level["exit_pos"][0] * GRID_SIZE + GRID_SIZE // 2
        exit_y = level["exit_pos"][1] * GRID_SIZE + GRID_SIZE // 2
        
        running = True
        
        while running:
            screen.fill(BLACK)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                        if player.on_ground:
                            player.vy = -10 * player.gravity_dir
                            player.on_ground = False
                    elif event.key == pygame.K_g:
                        player.gravity_dir *= -1
                        player.vy = 0
                    elif event.key == pygame.K_r:
                        running = False
            
            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_a] and player.x > player.radius:
                player.x -= 5
            if keys_pressed[pygame.K_d] and player.x < WIDTH - player.radius:
                player.x += 5
            
            player.update(level["platforms"], keys_collected)
            
            for key in keys:
                if not key.collected:
                    dist = ((player.x - key.x)**2 + (player.y - key.y)**2)**0.5
                    if dist < player.radius + 10:
                        key.collected = True
                        keys_collected += 1
            
            for platform in level["platforms"]:
                px, py, pw, ph = platform
                pygame.draw.rect(screen, BROWN, 
                               (px * GRID_SIZE, py * GRID_SIZE, 
                                pw * GRID_SIZE, ph * GRID_SIZE))
            
            for key in keys:
                key.draw()
            
            pygame.draw.circle(screen, PURPLE, (int(exit_x), int(exit_y)), 15)
            
            gravity_color = GREEN if player.gravity_dir == 1 else BLUE
            pygame.draw.circle(screen, gravity_color, (int(player.x), int(player.y)), player.radius)
            pygame.draw.circle(screen, WHITE, (int(player.x), int(player.y)), player.radius, 2)
            
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 40))
            level_text = font.render(f"关卡 {current_level + 1}/{len(LEVELS)}", True, WHITE)
            screen.blit(level_text, (10, 10))
            
            keys_text = font.render(f"钥匙: {keys_collected}/{level['keys']}", True, YELLOW)
            screen.blit(keys_text, (200, 10))
            
            gravity_text = font.render(f"重力: {'↓' if player.gravity_dir == 1 else '↑'} (G切换)", True, 
                                    GREEN if player.gravity_dir == 1 else BLUE)
            screen.blit(gravity_text, (400, 10))
            
            inst = small_font.render("A/D移动 | W/空格跳跃 | G切换重力 | R重试", True, WHITE)
            screen.blit(inst, (WIDTH // 2 - inst.get_width() // 2, HEIGHT - 30))
            
            dist_to_exit = ((player.x - exit_x)**2 + (player.y - exit_y)**2)**0.5
            if dist_to_exit < player.radius + 15:
                running = False
                current_level += 1
            
            pygame.display.flip()
            clock.tick(60)
    
    screen.fill(BLACK)
    result = big_font.render("恭喜通关!", True, YELLOW)
    screen.blit(result, (WIDTH // 2 - 120, HEIGHT // 2 - 30))
    
    complete = font.render("你完成了所有关卡!", True, GREEN)
    screen.blit(complete, (WIDTH // 2 - 100, HEIGHT // 2 + 30))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    gravity_puzzle()
