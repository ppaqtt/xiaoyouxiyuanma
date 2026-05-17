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

WIDTH, HEIGHT = 900, 700

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GRAY = (100, 100, 100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("飞行模拟器")
clock = pygame.time.Clock()
font = get_chinese_font(28)
big_font = get_chinese_font(50)

class Plane:
    def __init__(self):
        self.x = 200
        self.y = HEIGHT // 2
        self.speed = 0
        self.altitude = HEIGHT // 2
        self.fuel = 100
        self.angle = 0
    
    def update(self, keys):
        if keys[pygame.K_UP] and self.fuel > 0:
            self.speed = min(10, self.speed + 0.2)
            self.fuel -= 0.2
        elif keys[pygame.K_DOWN]:
            self.speed = max(-5, self.speed - 0.1)
        
        if keys[pygame.K_LEFT]:
            self.angle = max(-30, self.angle - 2)
        elif keys[pygame.K_RIGHT]:
            self.angle = min(30, self.angle + 2)
        else:
            self.angle *= 0.9
        
        self.y -= self.speed
        self.x += math.tan(math.radians(self.angle)) * 2
        
        self.y = max(50, min(HEIGHT - 100, self.y))
        self.x = max(50, min(WIDTH - 50, self.x))
    
    def draw(self):
        center = (int(self.x), int(self.y))
        
        rotated = pygame.Surface((60, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(rotated, WHITE, (0, 0, 60, 30))
        pygame.draw.ellipse(rotated, BLUE, (0, 5, 60, 20))
        
        rotated_plane = pygame.transform.rotate(rotated, -self.angle)
        screen.blit(rotated_plane, 
                   (self.x - rotated_plane.get_width() // 2,
                    self.y - rotated_plane.get_height() // 2))
        
        if self.speed > 2:
            flame_length = int(20 + self.speed * 3)
            points = [
                (self.x - 30, self.y),
                (self.x - 30 - flame_length, self.y - 5),
                (self.x - 30 - flame_length // 2, self.y),
                (self.x - 30 - flame_length, self.y + 5)
            ]
            pygame.draw.polygon(screen, RED, points)

class Obstacle:
    def __init__(self):
        self.x = WIDTH + 50
        self.y = random.randint(100, HEIGHT - 150)
        self.width = random.randint(50, 100)
        self.height = random.randint(80, 150)
    
    def update(self, speed):
        self.x -= speed
    
    def draw(self):
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2)
        pygame.draw.line(screen, GREEN, (self.x, self.y), (self.x + self.width, self.y + self.height), 2)
        pygame.draw.line(screen, GREEN, (self.x + self.width, self.y), (self.x, self.y + self.height), 2)

def flight_sim():
    plane = Plane()
    obstacles = []
    score = 0
    distance = 0
    game_over = False
    obstacle_timer = 0
    base_speed = 3
    
    while not game_over:
        screen.fill((135, 206, 235))
        
        for y in range(0, HEIGHT, 50):
            pygame.draw.line(screen, GREEN, (0, y), (WIDTH, y), 1)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        keys = pygame.key.get_pressed()
        plane.update(keys)
        
        obstacle_timer += 1
        if obstacle_timer > 60:
            if random.random() < 0.02:
                obstacles.append(Obstacle())
                obstacle_timer = 0
        
        current_speed = base_speed + distance // 1000
        
        for obs in obstacles[:]:
            obs.update(current_speed)
            obs.draw()
            
            if (plane.x + 30 > obs.x and plane.x - 30 < obs.x + obs.width and
                plane.y + 15 > obs.y and plane.y - 15 < obs.y + obs.height):
                game_over = True
            
            if obs.x < -100:
                obstacles.remove(obs)
                score += 100
        
        plane.draw()
        
        if plane.y <= 50 or plane.y >= HEIGHT - 100:
            game_over = True
        
        distance += current_speed
        score += int(current_speed)
        
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 60))
        
        speed_text = font.render(f"速度: {current_speed:.1f}", True, WHITE)
        altitude_text = font.render(f"高度: {int(plane.y)}", True, WHITE)
        fuel_text = font.render(f"燃料: {plane.fuel:.0f}%", True, GREEN if plane.fuel > 30 else RED)
        distance_text = font.render(f"距离: {distance}", True, WHITE)
        score_text = font.render(f"得分: {score}", True, YELLOW)
        
        screen.blit(speed_text, (10, 10))
        screen.blit(altitude_text, (150, 10))
        screen.blit(fuel_text, (300, 10))
        screen.blit(distance_text, (450, 10))
        screen.blit(score_text, (600, 10))
        
        inst = font.render("↑加速 ↓减速 ←→转向 | 燃料有限!", True, YELLOW)
        screen.blit(inst, (10, 40))
        
        fuel_bar_width = 150
        pygame.draw.rect(screen, GRAY, (WIDTH - fuel_bar_width - 10, 20, fuel_bar_width, 20))
        pygame.draw.rect(screen, GREEN if plane.fuel > 30 else RED, 
                        (WIDTH - fuel_bar_width - 10, 20, int(fuel_bar_width * plane.fuel / 100), 20))
        
        pygame.display.flip()
        clock.tick(60)
    
    screen.fill(BLACK)
    result = big_font.render("游戏结束!", True, RED)
    screen.blit(result, (WIDTH // 2 - 100, 100))
    
    final_score = font.render(f"最终得分: {score}", True, YELLOW)
    screen.blit(final_score, (WIDTH // 2 - 80, 200))
    
    final_distance = font.render(f"飞行距离: {distance}", True, WHITE)
    screen.blit(final_distance, (WIDTH // 2 - 80, 250))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    flight_sim()
