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

WIDTH, HEIGHT = 800, 600

BLACK = (10, 10, 30)
WHITE = (240, 240, 255)
PURPLE = (180, 100, 255)
BLUE = (80, 180, 255)
GOLD = (255, 210, 80)
RED = (255, 80, 80)
GRAY = (60, 60, 100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("星际引力弹弓")
clock = pygame.time.Clock()
font = get_chinese_font(28)
big_font = get_chinese_font(50)
small_font = get_chinese_font(20)

class Planet:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = radius * 10
    
    def draw(self):
        gradient = int(255 * 0.3)
        for i in range(5, -1, -1):
            pygame.draw.circle(screen, (50 + gradient * i, 60 + gradient * i, 150), 
                             (int(self.x), int(self.y)), int(self.radius + i * 8), 2)
        pygame.draw.circle(screen, PURPLE, (int(self.x), int(self.y)), int(self.radius))
        pygame.draw.circle(screen, (200, 150, 255), (int(self.x), int(self.y)), int(self.radius * 0.7))
        pygame.draw.circle(screen, (220, 180, 255), (int(self.x), int(self.y)), int(self.radius * 0.3))

class Rocket:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT // 2
        self.vx = 2.5
        self.vy = 0
        self.angle = 0
        self.fuel = 100
        self.max_fuel = 100
        self.alive = True
        self.invincible = 0
    
    def update(self, keys, planets):
        if self.invincible > 0:
            self.invincible -= 1
        
        self.angle = math.atan2(self.vy, self.vx)
        
        for planet in planets:
            dx = planet.x - self.x
            dy = planet.y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > planet.radius + 15:
                force = planet.mass / (dist**2)
                self.vx += (dx / dist) * force * 0.01
                self.vy += (dy / dist) * force * 0.01
        
        if keys[pygame.K_LEFT] and self.fuel > 0:
            self.vx -= 0.15
            self.vy += 0
            self.fuel -= 0.3
        if keys[pygame.K_RIGHT] and self.fuel > 0:
            self.vx += 0.15
            self.fuel -= 0.3
        if keys[pygame.K_UP] and self.fuel > 0:
            self.vy -= 0.15
            self.fuel -= 0.3
        if keys[pygame.K_DOWN] and self.fuel > 0:
            self.vy += 0.15
            self.fuel -= 0.3
        
        speed = math.sqrt(self.vx**2 + self.vy**2)
        max_speed = 15
        if speed > max_speed:
            self.vx = (self.vx / speed) * max_speed
            self.vy = (self.vy / speed) * max_speed
        
        self.x += self.vx
        self.y += self.vy
    
    def draw(self):
        color = WHITE if self.invincible == 0 or (self.invincible // 3) % 2 == 0 else (200, 200, 200)
        
        points = [
            (self.x + 20 * math.cos(self.angle), self.y + 20 * math.sin(self.angle)),
            (self.x + 12 * math.cos(self.angle + 2.5), self.y + 12 * math.sin(self.angle + 2.5)),
            (self.x + 8 * math.cos(self.angle + math.pi), self.y + 8 * math.sin(self.angle + math.pi)),
            (self.x + 12 * math.cos(self.angle - 2.5), self.y + 12 * math.sin(self.angle - 2.5)),
        ]
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, BLUE, points, 2)
        
        flame_length = 15 + random.randint(0, 5)
        flame_points = [
            (self.x + 8 * math.cos(self.angle + math.pi), self.y + 8 * math.sin(self.angle + math.pi)),
            (self.x + flame_length * math.cos(self.angle + math.pi + 0.4), self.y + flame_length * math.sin(self.angle + math.pi + 0.4)),
            (self.x + (flame_length - 5) * math.cos(self.angle + math.pi), self.y + (flame_length - 5) * math.sin(self.angle + math.pi)),
            (self.x + flame_length * math.cos(self.angle + math.pi - 0.4), self.y + flame_length * math.sin(self.angle + math.pi - 0.4)),
        ]
        pygame.draw.polygon(screen, (255, 150, 0), flame_points)

class Mineral:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.pulse = 0
        self.collected = False
        self.value = random.randint(50, 150)
    
    def update(self, rocket):
        self.pulse += 0.08
        
        if rocket.alive and not self.collected:
            dx = rocket.x - self.x
            dy = rocket.y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist < rocket.radius + self.radius + 20:
                self.collected = True
                return self.value
        
        return 0
    
    def draw(self):
        if not self.collected:
            size = self.radius + math.sin(self.pulse) * 2
            pygame.draw.circle(screen, GOLD, (int(self.x), int(self.y)), int(size))
            pygame.draw.circle(screen, (255, 240, 150), (int(self.x), int(self.y)), int(size * 0.6))

class Waypoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 40
        self.reached = False
        self.pulse = 0
    
    def update(self, rocket):
        self.pulse += 0.05
        if rocket.alive and not self.reached:
            dx = rocket.x - self.x
            dy = rocket.y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist < rocket.radius + self.radius:
                self.reached = True
                rocket.fuel = min(rocket.max_fuel, rocket.fuel + 30)
                return 200
        return 0
    
    def draw(self):
        color = GREEN if self.reached else BLUE
        size = self.radius + math.sin(self.pulse) * 5
        
        pygame.draw.circle(screen, (*color, 50), (int(self.x), int(self.y)), int(size))
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(size * 0.5), 3)
        pygame.draw.circle(screen, (*color, 100), (int(self.x), int(self.y)), 8)

class Asteroid:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1) * 0.5
        self.vy = random.uniform(-1, 1) * 0.5
        self.radius = size
        self.angle = random.random() * math.pi * 2
        self.rot_speed = random.uniform(-0.05, 0.05)
        self.verts = self.generate_verts()
    
    def generate_verts(self):
        verts = []
        num = random.randint(6, 10)
        for i in range(num):
            a = i / num * math.pi * 2
            r = self.radius + random.randint(-3, 5)
            verts.append((math.cos(a) * r, math.sin(a) * r))
        return verts
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.angle += self.rot_speed
        
        if self.x < -100: self.x = WIDTH + 100
        if self.x > WIDTH + 100: self.x = -100
        if self.y < -100: self.y = HEIGHT + 100
        if self.y > HEIGHT + 100: self.y = -100
    
    def check_collision(self, rocket):
        dx = rocket.x - self.x
        dy = rocket.y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        return dist < rocket.radius + self.radius - 5
    
    def draw(self):
        transformed = []
        for vx, vy in self.verts:
            rx = vx * math.cos(self.angle) - vy * math.sin(self.angle)
            ry = vx * math.sin(self.angle) + vy * math.cos(self.angle)
            transformed.append((self.x + rx, self.y + ry))
        
        pygame.draw.polygon(screen, GRAY, transformed)
        pygame.draw.polygon(screen, (80, 80, 120), transformed, 2)

def gravity_slingshot_game():
    rocket = Rocket()
    planets = []
    minerals = []
    waypoints = []
    asteroids = []
    
    planets.append(Planet(WIDTH // 2, HEIGHT // 2, 60))
    planets.append(Planet(WIDTH // 4, HEIGHT // 3, 35))
    planets.append(Planet(WIDTH * 3 // 4, HEIGHT * 2 // 3, 45))
    
    waypoints.append(Waypoint(WIDTH - 80, HEIGHT // 2))
    
    for _ in range(5):
        mx = random.randint(100, WIDTH-100)
        my = random.randint(100, HEIGHT-100)
        minerals.append(Mineral(mx, my))
    
    for _ in range(8):
        ax = random.randint(80, WIDTH-80)
        ay = random.randint(80, HEIGHT-80)
        valid = True
        for p in planets:
            d = math.sqrt((ax - p.x)**2 + (ay - p.y)**2)
            if d < p.radius + 60:
                valid = False
        if valid:
            asteroids.append(Asteroid(ax, ay, random.randint(12, 22)))
    
    score = 0
    game_over = False
    won = False
    
    while not game_over:
        screen.fill(BLACK)
        
        for i in range(50):
            sx = (i * 137 + 50) % WIDTH
            sy = (i * 89 + 30) % HEIGHT
            pygame.draw.circle(screen, (80, 80, 120, 30), (sx, sy), 1)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        keys = pygame.key.get_pressed()
        
        if rocket.alive:
            rocket.update(keys, planets)
            
            for waypoint in waypoints:
                wp_score = waypoint.update(rocket)
                if wp_score > 0:
                    score += wp_score
                    if all(w.reached for w in waypoints):
                        won = True
            
            for mineral in minerals:
                min_score = mineral.update(rocket)
                if min_score > 0:
                    score += min_score
            
            for asteroid in asteroids:
                asteroid.update()
                if asteroid.check_collision(rocket) and rocket.invincible == 0:
                    rocket.alive = False
                    game_over = True
            
            for planet in planets:
                dx = rocket.x - planet.x
                dy = rocket.y - planet.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist < planet.radius + rocket.radius and rocket.invincible == 0:
                    rocket.alive = False
                    game_over = True
            
            if rocket.x < -50 or rocket.x > WIDTH + 50 or rocket.y < -50 or rocket.y > HEIGHT + 50:
                rocket.alive = False
                game_over = True
        
        for planet in planets:
            planet.draw()
        
        for asteroid in asteroids:
            asteroid.draw()
        
        for mineral in minerals:
            mineral.draw()
        
        for waypoint in waypoints:
            waypoint.draw()
        
        if rocket.alive:
            rocket.draw()
        
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 60))
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        fuel_text = font.render(f"燃料: {int(rocket.fuel)}%", True, BLUE)
        screen.blit(fuel_text, (180, 10))
        pygame.draw.rect(screen, GRAY, (180, 35, 120, 15))
        pygame.draw.rect(screen, BLUE, (180, 35, int(120 * rocket.fuel / rocket.max_fuel), 15))
        
        wp_text = font.render(f"导航点: {'✓' if waypoints[0].reached else '○'}", True, GREEN)
        screen.blit(wp_text, (WIDTH - 200, 10))
        
        inst_text = small_font.render("方向键加速 | 利用行星引力 | 到达导航点", True, WHITE)
        screen.blit(inst_text, (WIDTH // 2 - inst_text.get_width() // 2, 40))
        
        if won:
            game_over = True
        
        pygame.display.flip()
        clock.tick(60)
    
    screen.fill(BLACK)
    if won:
        end_text = big_font.render("任务完成!", True, GREEN)
    else:
        end_text = big_font.render("任务失败", True, RED)
    screen.blit(end_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
    
    final_score = font.render(f"最终得分: {score}", True, WHITE)
    screen.blit(final_score, (WIDTH // 2 - 80, HEIGHT // 2 + 20))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    gravity_slingshot_game()
