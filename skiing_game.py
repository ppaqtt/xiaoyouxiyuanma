import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("滑雪大冒险")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (100, 150, 255)
PURPLE = (138, 43, 226)
ORANGE = (255, 140, 0)
SKY_BLUE = (135, 206, 250)
GRAY = (128, 128, 128)

class SkiGame:
    def __init__(self):
        self.player_x = 400
        self.player_y = 100
        self.player_angle = 0
        self.speed = 5
        self.score = 0
        self.distance = 0
        self.obstacles = []
        self.particles = []
        self.collectibles = []
        self.game_over = False
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 48)
        
        self.difficulty = 1
        self.difficulty_names = ["简单", "普通", "困难", "极限"]
        self.weather = "sunny"
        self.weather_names = ["晴天", "多云", "雪天", "暴风雪"]
        
        self.level = 1
        self.exp = 0
        self.skill_points = 0
        
        self.skills = {
            "speed_boost": {"level": 0, "max": 3, "name": "加速", "cost": 2},
            "shield": {"level": 0, "max": 2, "name": "护盾", "cost": 3},
            "magnet": {"level": 0, "max": 1, "name": "磁铁", "cost": 4}
        }
        
        self.shield_active = False
        self.shield_timer = 0
        
        self.unlocked_costumes = ["default"]
        self.current_costume = "default"
        self.costume_colors = {
            "default": BLUE,
            "pro": RED,
            "legendary": GOLD if 'GOLD' in dir() else ORANGE,
            "ninja": PURPLE
        }
        
        self.mode = "adventure"
        self.time_trial_best = {}
        
        for _ in range(5):
            self.spawn_obstacle()
        for _ in range(3):
            self.spawn_collectible()
    
    def spawn_obstacle(self):
        obstacle_types = [
            ('tree', '树木', 0.4),
            ('rock', '岩石', 0.3),
            ('iceberg', '冰山', 0.2),
            ('snowman', '雪人', 0.1)
        ]
        
        types = [t[0] for t in obstacle_types]
        weights = [t[2] for t in obstacle_types]
        obstacle_type = random.choices(types, weights=weights)[0]
        
        x = random.randint(100, 700)
        y = HEIGHT + random.randint(50, 200)
        speed_mult = 1 + self.difficulty * 0.3
        
        self.obstacles.append({
            'x': x, 'y': y, 'type': obstacle_type,
            'speed': random.uniform(3, 6) * speed_mult,
            'size': random.uniform(0.8, 1.2)
        })
    
    def spawn_collectible(self):
        collectible_types = [
            ('coin', '金币', 10, 0.5),
            ('gem', '宝石', 50, 0.3),
            ('star', '星星', 100, 0.2)
        ]
        
        types = [t[0] for t in collectible_types]
        weights = [t[3] for t in collectible_types]
        col_type = random.choices(types, weights=weights)[0]
        
        x = random.randint(100, 700)
        y = HEIGHT + random.randint(100, 300)
        
        self.collectibles.append({
            'x': x, 'y': y, 'type': col_type,
            'speed': 5 + self.difficulty * 0.5
        })
    
    def draw(self):
        weather_colors = {
            "sunny": SKY_BLUE,
            "cloudy": (150, 150, 170),
            "snowy": (200, 210, 220),
            "blizzard": (180, 190, 200)
        }
        screen.fill(weather_colors.get(self.weather, SKY_BLUE))
        
        for i in range(20):
            y = (i * 50 + self.distance * 3) % (HEIGHT + 200) - 100
            line_color = WHITE if self.weather in ["snowy", "blizzard"] else (220, 220, 230)
            pygame.draw.line(screen, line_color, (0, y), (WIDTH, y), 2)
        
        for obs in self.obstacles:
            size = obs['size']
            if obs['type'] == 'tree':
                pygame.draw.rect(screen, (101, 67, 33), (obs['x'] - 8*size, obs['y'] - 20*size, 16*size, 25*size))
                pygame.draw.circle(screen, GREEN, (int(obs['x']), int(obs['y'] - 30*size)), int(20*size))
            elif obs['type'] == 'rock':
                pygame.draw.polygon(screen, GRAY, [(obs['x'], obs['y'] - 15*size), 
                                                   (obs['x'] - 20*size, obs['y']), 
                                                   (obs['x'] + 20*size, obs['y'])])
            elif obs['type'] == 'iceberg':
                pygame.draw.polygon(screen, (200, 230, 255), [(obs['x'], obs['y'] - 25*size),
                                                              (obs['x'] - 15*size, obs['y']),
                                                              (obs['x'] + 15*size, obs['y'])])
            else:
                pygame.draw.circle(screen, WHITE, (int(obs['x']), int(obs['y'] - 15*size)), int(15*size))
                pygame.draw.circle(screen, WHITE, (int(obs['x']), int(obs['y'] - 35*size)), int(10*size))
        
        for col in self.collectibles:
            if col['type'] == 'coin':
                pygame.draw.circle(screen, GOLD if 'GOLD' in dir() else ORANGE, (int(col['x']), int(col['y'])), 10)
                pygame.draw.circle(screen, WHITE, (int(col['x']), int(col['y'])), 5)
            elif col['type'] == 'gem':
                pygame.draw.polygon(screen, PURPLE, [(col['x'], col['y'] - 12),
                                                     (col['x'] - 10, col['y'] + 8),
                                                     (col['x'] + 10, col['y'] + 8)])
            else:
                for i in range(5):
                    angle = i * 72 + self.distance * 5
                    star_x = col['x'] + math.cos(math.radians(angle)) * 12
                    star_y = col['y'] + math.sin(math.radians(angle)) * 12
                    pygame.draw.circle(screen, GOLD if 'GOLD' in dir() else ORANGE, (int(star_x), int(star_y)), 4)
        
        color = self.costume_colors.get(self.current_costume, BLUE)
        pygame.draw.circle(screen, color, (int(self.player_x), int(self.player_y)), 15)
        
        if self.shield_active:
            pygame.draw.circle(screen, (100, 200, 255), (int(self.player_x), int(self.player_y)), 25, 3)
        
        for p in self.particles:
            pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), int(p['size']))
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
    
    def draw_hud(self):
        pygame.draw.rect(screen, (0, 0, 0, 128), (10, 10, 250, 120), border_radius=10)
        
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        dist_text = self.font.render(f"距离: {self.distance}m", True, WHITE)
        screen.blit(dist_text, (20, 50))
        
        level_text = self.font.render(f"等级: {self.level}", True, GREEN)
        screen.blit(level_text, (20, 80))
        
        exp_text = self.font.render(f"经验: {self.exp}/100", True, (200, 200, 100))
        screen.blit(exp_text, (150, 80))
        
        difficulty_text = self.font.render(f"难度: {self.difficulty_names[self.difficulty]}", True, ORANGE)
        screen.blit(difficulty_text, (150, 20))
        
        weather_text = self.font.render(f"天气: {self.weather_names[['sunny','cloudy','snowy','blizzard'].index(self.weather)]}", True, WHITE)
        screen.blit(weather_text, (150, 50))
        
        controls = self.font.render("←→移动 空格加速 R重开 S技能", True, (150, 150, 150))
        screen.blit(controls, (200, 570))
        
        pygame.draw.rect(screen, (0, 0, 0, 180), (550, 10, 150, 50), border_radius=10)
        skill_text = self.font.render(f"技能点: {self.skill_points}", True, PURPLE)
        screen.blit(skill_text, (560, 25))
    
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        text = self.large_font.render("滑雪结束!", True, BLUE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 150))
        
        score_text = self.font.render(f"最终分数: {self.score}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 220))
        
        level_text = self.font.render(f"达到等级: {self.level}", True, GREEN)
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, 260))
        
        new_skills = self.font.render(f"获得技能点: {self.skill_points}", True, PURPLE)
        screen.blit(new_skills, (WIDTH//2 - new_skills.get_width()//2, 300))
        
        restart_text = self.font.render("按 R 重新开始 | D 难度选择 | T 换装", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 380))
    
    def upgrade_skill(self, skill_name):
        skill = self.skills[skill_name]
        if self.skill_points >= skill["cost"] and skill["level"] < skill["max"]:
            self.skill_points -= skill["cost"]
            skill["level"] += 1
            return True
        return False
    
    def use_skill(self, skill_name):
        skill = self.skills[skill_name]
        if skill["level"] > 0:
            if skill_name == "speed_boost":
                self.speed_boost_active = True
                self.speed_boost_timer = 180
            elif skill_name == "shield":
                self.shield_active = True
                self.shield_timer = 300
            elif skill_name == "magnet":
                self.magnet_active = True
                self.magnet_timer = 300
            return True
        return False
    
    def update(self):
        if self.game_over:
            return
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.player_x -= 8
            self.particles.append({'x': self.player_x + 15, 'y': self.player_y + 10, 'vx': 3, 'vy': -2, 'size': 3, 'color': WHITE})
        if keys[pygame.K_RIGHT]:
            self.player_x += 8
            self.particles.append({'x': self.player_x - 15, 'y': self.player_y + 10, 'vx': -3, 'vy': -2, 'size': 3, 'color': WHITE})
        
        self.player_x = max(30, min(WIDTH - 30, self.player_x))
        
        weather_speed_mult = 1.0
        if self.weather == "cloudy":
            weather_speed_mult = 0.9
        elif self.weather == "snowy":
            weather_speed_mult = 0.8
        elif self.weather == "blizzard":
            weather_speed_mult = 0.6
        
        self.distance += int(1 * weather_speed_mult)
        
        for obs in self.obstacles:
            obs['y'] -= obs['speed'] * weather_speed_mult
        
        self.obstacles = [o for o in self.obstacles if o['y'] > -50]
        
        while len(self.obstacles) < 6 + self.difficulty * 2:
            self.spawn_obstacle()
        
        for col in self.collectibles:
            col['y'] -= col['speed']
        
        self.collectibles = [c for c in self.collectibles if c['y'] > -50]
        
        while len(self.collectibles) < 3:
            self.spawn_collectible()
        
        for col in self.collectibles[:]:
            dist = math.hypot(self.player_x - col['x'], self.player_y - col['y'])
            if dist < 35:
                points = 10 if col['type'] == 'coin' else (50 if col['type'] == 'gem' else 100)
                self.score += points
                self.collectibles.remove(col)
        
        if self.skills["magnet"]["level"] > 0:
            for col in self.collectibles:
                dist = math.hypot(self.player_x - col['x'], self.player_y - col['y'])
                if dist < 150:
                    col['x'] += (self.player_x - col['x']) * 0.05
                    col['y'] += (self.player_y - col['y']) * 0.05
        
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['size'] *= 0.95
        
        self.particles = [p for p in self.particles if p['size'] > 0.5]
        
        for obs in self.obstacles:
            dist = math.hypot(self.player_x - obs['x'], self.player_y - obs['y'])
            if dist < 30 * obs['size']:
                if not self.shield_active:
                    self.game_over = True
                else:
                    self.shield_timer -= 30
        
        if self.shield_timer <= 0:
            self.shield_active = False
        
        if self.distance % 500 == 0 and self.distance > 0:
            self.exp += 10
            if self.exp >= 100:
                self.level += 1
                self.exp -= 100
                self.skill_points += 1
        
        if self.distance % 1000 == 0 and self.distance > 0:
            weathers = ["sunny", "cloudy", "snowy", "blizzard"]
            current_idx = weathers.index(self.weather) if self.weather in weathers else 0
            if current_idx < len(weathers) - 1:
                self.weather = weathers[current_idx + 1]
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.__init__()
            elif event.key == pygame.K_s and not self.game_over:
                self.use_skill("speed_boost")
            elif event.key == pygame.K_d and self.game_over:
                self.difficulty = (self.difficulty + 1) % 4
            elif event.key == pygame.K_t and self.game_over:
                costumes = ["default", "pro", "legendary", "ninja"]
                current_idx = costumes.index(self.current_costume) if self.current_costume in costumes else 0
                self.current_costume = costumes[(current_idx + 1) % len(costumes)]
            elif event.key == pygame.K_1 and self.game_over:
                self.upgrade_skill("speed_boost")
            elif event.key == pygame.K_2 and self.game_over:
                self.upgrade_skill("shield")
            elif event.key == pygame.K_3 and self.game_over:
                self.upgrade_skill("magnet")

game = SkiGame()
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.handle_input(event)
    
    game.update()
    game.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
