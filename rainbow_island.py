"""
彩虹岛冒险
收集宝石、躲避障碍的跑酷冒险游戏
"""

import pygame
import os
import random
import sys
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

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("彩虹岛冒险 🌈")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (50, 50, 50)

RAINBOW_COLORS = [
    (255, 80, 80),
    (255, 160, 80),
    (255, 220, 80),
    (100, 220, 100),
    (80, 180, 255),
    (120, 120, 255),
    (200, 100, 255)
]

GAME_COLORS = {
    "sky": (135, 206, 250),
    "ground": (139, 90, 43),
    "grass": (34, 139, 34),
    "water": (30, 144, 255),
    "lava": (255, 69, 0),
    "cloud": (255, 255, 255),
    "rainbow": RAINBOW_COLORS
}

class Player:
    def __init__(self):
        self.x = 150
        self.y = HEIGHT - 150
        self.base_y = HEIGHT - 150
        self.vy = 0
        self.size = 40
        self.on_ground = True
        self.jumping = False
        self.anim_frame = 0
        self.direction = 1
        self.invincible = 0
        self.trail = []
        
    def jump(self):
        if self.on_ground:
            self.vy = -18
            self.jumping = True
            self.on_ground = False
    
    def update(self, platforms):
        gravity = 0.8
        self.vy += gravity
        self.y += self.vy
        
        self.on_ground = False
        for plat in platforms:
            if plat.type != "cloud" and self.vy > 0:
                if self.x + self.size // 2 > plat.x and self.x - self.size // 2 < plat.x + plat.width:
                    if self.y + self.size // 2 >= plat.y and self.y + self.size // 2 <= plat.y + 20:
                        self.y = plat.y - self.size // 2
                        self.vy = 0
                        self.on_ground = True
                        self.jumping = False
        
        if self.y > HEIGHT:
            return False
        
        if self.invincible > 0:
            self.invincible -= 1
        
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        self.anim_frame = (self.anim_frame + 0.2) % 4
        return True
    
    def draw(self):
        if self.invincible > 0 and self.invincible % 4 < 2:
            return
        
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)) * 0.3)
            size = int(self.size * (i / len(self.trail)))
            rainbow_idx = (pygame.time.get_ticks() // 100) % 7
            color = RAINBOW_COLORS[rainbow_idx]
            pygame.draw.circle(screen, color, (tx, ty - size // 4), size // 4)
        
        rainbow_idx = (pygame.time.get_ticks() // 100) % 7
        
        body_color = RAINBOW_COLORS[rainbow_idx]
        
        pygame.draw.ellipse(screen, body_color, (self.x - self.size//2, self.y - self.size//2, 
                                                  self.size, self.size * 0.8))
        
        eye_x = self.x + 5 * self.direction
        pygame.draw.circle(screen, WHITE, (eye_x, self.y - 8), 8)
        pygame.draw.circle(screen, BLACK, (eye_x + 2 * self.direction, self.y - 8), 4)
        
        if self.jumping:
            pygame.draw.polygon(screen, body_color,
                               [(self.x - 15, self.y - 10), (self.x - 25, self.y - 30),
                                (self.x - 10, self.y - 20)])

class Platform:
    def __init__(self, x, y, width, plat_type="ground"):
        self.x = x
        self.y = y
        self.width = width
        self.height = 20
        self.type = plat_type
        self.anim_offset = random.randint(0, 100)
        
    def update(self, speed):
        self.x -= speed
        
    def draw(self):
        if self.type == "ground":
            pygame.draw.rect(screen, GAME_COLORS["grass"], (self.x, self.y, self.width, 10))
            pygame.draw.rect(screen, GAME_COLORS["ground"], (self.x, self.y + 10, self.width, self.height - 10))
            
            for i in range(0, self.width, 30):
                tree_x = self.x + i + 15
                if tree_x < self.x + self.width:
                    pygame.draw.rect(screen, (101, 67, 33), (tree_x, self.y - 25, 8, 25))
                    pygame.draw.circle(screen, (0, 200, 0), (tree_x + 4, self.y - 35), 15)
                    
        elif self.type == "cloud":
            alpha = int(180 + 50 * math.sin(pygame.time.get_ticks() / 500 + self.anim_offset))
            cloud_color = (255, 255, 255, alpha)
            
            pygame.draw.circle(screen, (255, 255, 255), (self.x + 20, self.y + 10), 20)
            pygame.draw.circle(screen, (255, 255, 255), (self.x + 40, self.y + 15), 25)
            pygame.draw.circle(screen, (255, 255, 255), (self.x + 60, self.y + 10), 20)
            
        elif self.type == "rainbow":
            for i, color in enumerate(RAINBOW_COLORS):
                y_offset = i * 8
                pygame.draw.arc(screen, color, 
                               (self.x - 50, self.y - 60 + y_offset, 100, 120),
                               0, math.pi, 6)
        
        elif self.type == "water":
            pygame.draw.rect(screen, GAME_COLORS["water"], (self.x, self.y, self.width, self.height))
            wave_offset = math.sin(pygame.time.get_ticks() / 200 + self.anim_offset) * 3
            for i in range(0, self.width, 20):
                pygame.draw.arc(screen, (100, 180, 255), 
                              (self.x + i, self.y - 5 + wave_offset, 15, 10),
                              0, math.pi, 2)
                              
        elif self.type == "lava":
            pygame.draw.rect(screen, GAME_COLORS["lava"], (self.x, self.y, self.width, self.height))
            glow = int(150 + 50 * math.sin(pygame.time.get_ticks() / 100 + self.anim_offset))
            pygame.draw.rect(screen, (255, glow, 0), (self.x, self.y, self.width, 5))

class Gem:
    def __init__(self, x, y, gem_type="normal"):
        self.x = x
        self.y = y
        self.size = 20
        self.type = gem_type
        self.collected = False
        self.anim_offset = random.random() * math.pi * 2
        
        self.colors = {
            "red": (255, 50, 50),
            "blue": (50, 150, 255),
            "green": (50, 255, 100),
            "purple": (200, 50, 255),
            "rainbow": None
        }
    
    def update(self, speed):
        self.x -= speed
        
    def draw(self):
        if self.collected:
            return
        
        wobble = math.sin(pygame.time.get_ticks() / 200 + self.anim_offset) * 5
        y = self.y + wobble
        
        if self.type == "rainbow":
            rainbow_idx = (pygame.time.get_ticks() // 100) % 7
            color = RAINBOW_COLORS[rainbow_idx]
        elif self.type == "normal":
            color = (255, 215, 0)
        else:
            color = self.colors.get(self.type, (255, 215, 0))
        
        glow_size = self.size + 10 + 5 * math.sin(pygame.time.get_ticks() / 150 + self.anim_offset)
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        glow_alpha = int(100 + 50 * math.sin(pygame.time.get_ticks() / 200 + self.anim_offset))
        pygame.draw.circle(glow_surface, (*color, glow_alpha), (int(glow_size), int(glow_size)), int(glow_size))
        screen.blit(glow_surface, (self.x - glow_size, y - glow_size))
        
        points = [
            (self.x, y - self.size),
            (self.x + self.size * 0.7, y - self.size * 0.3),
            (self.x + self.size * 0.7, y + self.size * 0.3),
            (self.x, y + self.size),
            (self.x - self.size * 0.7, y + self.size * 0.3),
            (self.x - self.size * 0.7, y - self.size * 0.3)
        ]
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, WHITE, points, 2)
        
        inner = [
            (self.x, y - self.size * 0.4),
            (self.x + self.size * 0.3, y),
            (self.x, y + self.size * 0.2),
            (self.x - self.size * 0.3, y)
        ]
        pygame.draw.polygon(screen, (255, 255, 255, 150), inner)

class Obstacle:
    def __init__(self, x, y, obstacle_type="spike"):
        self.x = x
        self.y = y
        self.type = obstacle_type
        self.width = 40
        self.height = 40
        
    def update(self, speed):
        self.x -= speed
        
    def draw(self):
        if self.type == "spike":
            for i in range(3):
                spike_x = self.x + i * 15
                points = [(spike_x, self.y + self.height), 
                         (spike_x + 7, self.y),
                         (spike_x + 14, self.y + self.height)]
                pygame.draw.polygon(screen, GRAY, points)
                pygame.draw.polygon(screen, WHITE, points, 1)
                
        elif self.type == "saw":
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            rotation = pygame.time.get_ticks() / 50
            
            for i in range(8):
                angle = rotation + i * (math.pi / 4)
                x1 = center_x + math.cos(angle) * 5
                y1 = center_y + math.sin(angle) * 5
                x2 = center_x + math.cos(angle) * 20
                y2 = center_y + math.sin(angle) * 20
                pygame.draw.line(screen, (150, 150, 150), (x1, y1), (x2, y2), 3)
            
            pygame.draw.circle(screen, DARK_GRAY, (center_x, center_y), 8)
            
        elif self.type == "bird":
            bird_y = self.y + math.sin(pygame.time.get_ticks() / 200) * 10
            wing_offset = math.sin(pygame.time.get_ticks() / 100) * 10
            
            pygame.draw.ellipse(screen, (50, 50, 50), (self.x, bird_y, 30, 20))
            pygame.draw.circle(screen, (50, 50, 50), (self.x + 25, bird_y + 8), 6)
            pygame.draw.polygon(screen, (255, 200, 0), 
                               [(self.x + 28, bird_y + 6), (self.x + 35, bird_y + 8), (self.x + 28, bird_y + 10)])
            
            pygame.draw.line(screen, (50, 50, 50), (self.x + 10, bird_y + 5), (self.x + 5, bird_y - wing_offset), 2)
            pygame.draw.line(screen, (50, 50, 50), (self.x + 20, bird_y + 5), (self.x + 15, bird_y - wing_offset), 2)

class Game:
    def __init__(self):
        self.reset()
        self.font = get_chinese_font(36)
        self.font_large = get_chinese_font(72)
        self.font_small = get_chinese_font(28)
        
    def reset(self):
        self.player = Player()
        self.platforms = []
        self.gems = []
        self.obstacles = []
        self.score = 0
        self.distance = 0
        self.speed = 5
        self.game_over = False
        self.paused = False
        self.phase = "menu"
        self.background_offset = 0
        self.spawn_timer = 0
        self.gem_spawn_timer = 0
        
        self.create_initial_world()
    
    def create_initial_world(self):
        for i in range(8):
            self.platforms.append(Platform(i * 150, HEIGHT - 50, 150, "ground"))
        
        self.platforms.append(Platform(400, HEIGHT - 180, 100, "cloud"))
        self.platforms.append(Platform(700, HEIGHT - 220, 100, "cloud"))
        
    def spawn_elements(self):
        self.spawn_timer += 1
        self.gem_spawn_timer += 1
        
        if self.spawn_timer > 60:
            self.spawn_timer = 0
            
            rand = random.random()
            last_plat = None
            for p in self.platforms:
                if p.x + p.width > WIDTH - 100:
                    last_plat = p
            
            if rand < 0.4 and last_plat:
                new_y = max(100, min(HEIGHT - 150, last_plat.y + random.randint(-100, 50)))
                self.platforms.append(Platform(WIDTH + 50, new_y, random.randint(80, 150), "ground"))
                
            elif rand < 0.6:
                self.platforms.append(Platform(WIDTH + 50, HEIGHT - 150, 100, "cloud"))
                
            elif rand < 0.75:
                obstacle_type = random.choice(["spike", "spike", "saw", "bird"])
                if last_plat and last_plat.type == "ground":
                    y = last_plat.y - 40
                else:
                    y = HEIGHT - 100
                self.obstacles.append(Obstacle(WIDTH + 50, y, obstacle_type))
                
            elif rand < 0.85:
                self.platforms.append(Platform(WIDTH + 50, HEIGHT - 400, 200, "rainbow"))
                
            elif rand < 0.92:
                self.platforms.append(Platform(WIDTH + 50, HEIGHT - 50, 100, "water"))
                
            elif rand < 0.98:
                self.platforms.append(Platform(WIDTH + 50, HEIGHT - 50, 150, "lava"))
        
        if self.gem_spawn_timer > 40:
            self.gem_spawn_timer = 0
            gem_type = random.choice(["normal", "normal", "red", "blue", "green", "purple", "rainbow"])
            y = HEIGHT - 250 - random.randint(0, 200)
            self.gems.append(Gem(WIDTH + 30, y, gem_type))
    
    def update(self):
        if self.phase != "playing" or self.game_over or self.paused:
            return
        
        self.speed = 5 + self.distance // 1000
        self.distance += self.speed // 10
        self.score = self.distance // 10
        
        for platform in self.platforms:
            platform.update(self.speed)
        for gem in self.gems:
            gem.update(self.speed)
        for obstacle in self.obstacles:
            obstacle.update(self.speed)
        
        self.platforms = [p for p in self.platforms if p.x + p.width > -50]
        self.gems = [g for g in self.gems if g.x > -50 and not g.collected]
        self.obstacles = [o for o in self.obstacles if o.x + o.width > -50]
        
        if not self.player.update(self.platforms):
            self.game_over = True
        
        for gem in self.gems:
            if not gem.collected:
                dx = self.player.x - gem.x
                dy = self.player.y - gem.y
                if abs(dx) < 35 and abs(dy) < 35:
                    gem.collected = True
                    if gem.type == "rainbow":
                        self.score += 50
                    elif gem.type in ["red", "blue", "green", "purple"]:
                        self.score += 20
                    else:
                        self.score += 10
        
        for obstacle in self.obstacles:
            if self.player.invincible == 0:
                dx = abs(self.player.x - (obstacle.x + obstacle.width // 2))
                dy = abs(self.player.y - (obstacle.y + obstacle.height // 2))
                
                if obstacle.type == "bird":
                    bird_y = obstacle.y + math.sin(pygame.time.get_ticks() / 200) * 10
                    dy = abs(self.player.y - bird_y)
                
                if dx < 25 and dy < 25:
                    self.game_over = True
        
        self.spawn_elements()
        
        self.background_offset = (self.background_offset + self.speed * 0.5) % WIDTH
    
    def draw_background(self):
        sky_gradient = []
        for i in range(HEIGHT):
            t = i / HEIGHT
            r = int(135 + (255 - 135) * t * 0.3)
            g = int(206 + (200 - 206) * t * 0.3)
            b = int(250 + (180 - 250) * t * 0.3)
            sky_gradient.append((r, g, b))
        
        for i, color in enumerate(sky_gradient):
            pygame.draw.line(screen, color, (0, i), (WIDTH, i))
        
        for i in range(3):
            x = ((i * 400 - self.background_offset * 0.3) % (WIDTH + 200)) - 100
            y = 80 + i * 30
            size = 60 + i * 20
            
            pygame.draw.ellipse(screen, (255, 255, 255, 150), (x, y, size * 2, size))
            pygame.draw.ellipse(screen, (255, 255, 255, 150), (x + 30, y - 20, size * 1.5, size * 0.8))
    
    def draw(self):
        self.draw_background()
        
        for platform in self.platforms:
            platform.draw()
        
        for gem in self.gems:
            gem.draw()
        
        for obstacle in self.obstacles:
            obstacle.draw()
        
        self.player.draw()
        
        if self.phase == "menu":
            self.draw_menu()
        elif self.game_over:
            self.draw_game_over()
        
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        pygame.draw.rect(screen, (0, 0, 0, 128), (10, 10, 150, 40), border_radius=8)
        screen.blit(score_text, (20, 18))
        
        dist_text = self.font_small.render(f"距离: {self.distance}m", True, WHITE)
        pygame.draw.rect(screen, (0, 0, 0, 128), (10, 55, 150, 35), border_radius=8)
        screen.blit(dist_text, (20, 60))
        
        speed_text = self.font_small.render(f"速度: {self.speed}x", True, WHITE)
        pygame.draw.rect(screen, (0, 0, 0, 128), (10, 95, 130, 35), border_radius=8)
        screen.blit(speed_text, (20, 100))
        
        controls = self.font_small.render("空格-跳跃 | P-暂停 | ESC-菜单", True, WHITE)
        screen.blit(controls, (WIDTH - controls.get_width() - 20, HEIGHT - 40))
        
        pygame.display.flip()
    
    def draw_menu(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        for i, color in enumerate(RAINBOW_COLORS):
            y = 150 + i * 15
            pygame.draw.rect(screen, color, (WIDTH//2 - 200 + i * 10, y, 400 - i * 20, 15))
        
        title = self.font_large.render("🌈 彩虹岛冒险 🌈", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        
        instructions = [
            "收集宝石获得分数!",
            "躲避尖刺和障碍物",
            "在云朵平台上跳跃",
            "寻找彩虹桥获得额外奖励",
            "",
            "按 空格键 开始冒险"
        ]
        
        y = 350
        for line in instructions:
            text = self.font.render(line, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y))
            y += 45
    
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        game_over_text = self.font_large.render("游戏结束!", True, RAINBOW_COLORS[0])
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, 200))
        
        score_text = self.font.render(f"最终分数: {self.score}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 300))
        
        dist_text = self.font.render(f"行驶距离: {self.distance}m", True, WHITE)
        screen.blit(dist_text, (WIDTH//2 - dist_text.get_width()//2, 350))
        
        restart_text = self.font.render("按 R 重新开始 | ESC 返回主菜单", True, RAINBOW_COLORS[3])
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 450))
    
    def handle_key(self, key):
        if key == pygame.K_SPACE:
            if self.phase == "menu":
                self.phase = "playing"
            elif self.phase == "playing" and not self.game_over:
                self.player.jump()
        elif key == pygame.K_p and self.phase == "playing":
            self.paused = not self.paused
        elif key == pygame.K_r and self.game_over:
            self.reset()
            self.phase = "playing"
        elif key == pygame.K_ESCAPE:
            if self.game_over or self.phase == "playing":
                self.reset()
                self.phase = "menu"

def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.paused:
                        game.paused = False
                    else:
                        running = False
                else:
                    game.handle_key(event.key)
        
        game.update()
        game.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
