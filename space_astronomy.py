import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("太空探索")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
PURPLE = (150, 50, 200)

planets = [
    {"name": "水星", "color": (180, 180, 180), "size": 12, "distance": 100, "info": "最小的行星"},
    {"name": "金星", "color": (255, 215, 0), "size": 18, "distance": 150, "info": "最热的行星"},
    {"name": "地球", "color": (0, 150, 255), "size": 20, "distance": 200, "info": "我们的家"},
    {"name": "火星", "color": (255, 100, 50), "size": 15, "distance": 260, "info": "红色星球"},
    {"name": "木星", "color": (200, 180, 100), "size": 35, "distance": 350, "info": "最大的行星"},
    {"name": "土星", "color": (255, 200, 100), "size": 32, "distance": 450, "info": "有美丽的光环"},
    {"name": "天王星", "color": (100, 200, 255), "size": 24, "distance": 520, "info": "倾斜旋转"},
    {"name": "海王星", "color": (50, 100, 255), "size": 23, "distance": 580, "info": "最远的行星"},
]

stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.random()) for _ in range(150)]

class SpaceGame:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.collected_planets = set()
        self.current_planet = None
        self.target_planet = None
        self.ship_x = WIDTH // 2
        self.ship_y = HEIGHT - 100
        self.ship_speed = 4
        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 48)
        self.select_target()

    def select_target(self):
        if len(self.collected_planets) >= len(planets):
            self.collected_planets.clear()
            self.level += 1
        available = [p for p in planets if p["name"] not in self.collected_planets]
        self.target_planet = random.choice(available) if available else random.choice(planets)

    def update(self):
        pass

    def draw(self):
        screen.fill(BLACK)
        
        for x, y, brightness in stars:
            pygame.draw.circle(screen, (int(200*brightness), int(200*brightness), int(255*brightness)), 
                              (int(x), int(y)), 1 if brightness < 0.5 else 2)
        
        pygame.draw.circle(screen, YELLOW, (WIDTH//2, HEIGHT//2), 40)
        pygame.draw.circle(screen, (255, 230, 0), (WIDTH//2, HEIGHT//2), 35)
        
        for planet in planets:
            x = WIDTH//2 + planet["distance"]
            y = HEIGHT//2 + random.randint(-40, 40)
            pygame.draw.circle(screen, planet["color"], (int(x), int(y)), planet["size"])
            if planet == self.target_planet:
                pygame.draw.circle(screen, WHITE, (int(x), int(y)), planet["size"] + 5, 2)
            
            if planet["name"] == "土星":
                pygame.draw.ellipse(screen, (200, 180, 150), (x - planet["size"]*1.5, y - planet["size"]*0.3, 
                                                        planet["size"]*3, planet["size"]*0.6), 2)
        
        pygame.draw.polygon(screen, WHITE, [
            (self.ship_x, self.ship_y - 20),
            (self.ship_x - 15, self.ship_y + 20),
            (self.ship_x + 15, self.ship_y + 20)
        ])
        
        title_text = self.large_font.render("太空探索", True, GREEN)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 10))
        
        level_text = self.font.render(f"关卡: {self.level}", True, WHITE)
        screen.blit(level_text, (50, 10))
        
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (50, 40))
        
        if self.target_planet:
            target_text = self.font.render(f"目标: {self.target_planet['name']}", True, YELLOW)
            screen.blit(target_text, (WIDTH//2 - target_text.get_width()//2, 550))
            info_text = self.font.render(self.target_planet["info"], True, BLUE)
            screen.blit(info_text, (WIDTH//2 - info_text.get_width()//2, 580))
        
        collected_text = self.font.render(f"已收集: {len(self.collected_planets)}/{len(planets)}", True, GREEN)
        screen.blit(collected_text, (600, 10))
        
        hint_text = self.font.render("方向键移动飞船，空格收集目标行星", True, WHITE)
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, 70))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] and self.ship_x > 50:
            self.ship_x -= self.ship_speed
        if keys[pygame.K_RIGHT] and self.ship_x < WIDTH - 50:
            self.ship_x += self.ship_speed
        if keys[pygame.K_UP] and self.ship_y > 50:
            self.ship_y -= self.ship_speed
        if keys[pygame.K_DOWN] and self.ship_y < HEIGHT - 50:
            self.ship_y += self.ship_speed

    def check_collision(self):
        for planet in planets:
            planet_x = WIDTH//2 + planet["distance"]
            planet_y = HEIGHT//2
            distance = ((self.ship_x - planet_x)**2 + (self.ship_y - planet_y)**2)**0.5
            if distance < planet["size"] + 25:
                if planet["name"] == self.target_planet["name"]:
                    self.score += 50 + self.level * 10
                    self.collected_planets.add(planet["name"])
                    self.select_target()
                    return

game = SpaceGame()
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game.check_collision()
    
    game.handle_input()
    game.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
