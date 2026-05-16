import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("街头滑板")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 200)
ORANGE = (255, 165, 0)
PURPLE = (138, 43, 226)
YELLOW = (255, 200, 0)

class SkateboardGame:
    def __init__(self):
        self.player_x = 400
        self.player_y = 300
        self.velocity_x = 0
        self.velocity_y = 0
        self.rotation = 0
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.tricks = []
        self.ramps = []
        self.grinds = []
        self.particles = []
        self.game_over = False
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 48)
        
        self.level = 1
        self.exp = 0
        self.style_points = 0
        
        self.unlocked_moves = ["ollie", "kickflip", "heelflip"]
        self.move_descriptions = {
            "ollie": {"name": "Ollie", "points": 10, "keys": "空格"},
            "kickflip": {"name": "Kickflip", "points": 20, "keys": "上"},
            "heelflip": {"name": "Heelflip", "points": 20, "keys": "下"},
            "pop_shuvit": {"name": "Pop Shuvit", "points": 25, "keys": "左"},
            "fs_180": {"name": "FS 180", "points": 30, "keys": "右"},
            "hardflip": {"name": "Hardflip", "points": 50, "keys": "上+左"},
            "360_flip": {"name": "360 Flip", "points": 60, "keys": "下+右"},
            "laser_flip": {"name": "Laser Flip", "points": 75, "keys": "上+右"}
        }
        
        self.difficulty = 1
        self.difficulties = ["简单", "普通", "困难", "专家"]
        
        self.mode = "freestyle"
        self.achievements = []
        
        self.obstacles = []
        self.collectibles = []
        
        for i in range(5):
            self.ramps.append({
                'x': 100 + i * 180,
                'y': 450 + random.randint(-50, 50),
                'width': 120,
                'height': 40
            })
        
        for _ in range(3):
            self.spawn_obstacle()
    
    def spawn_obstacle(self):
        obstacle_types = ["barrier", "cone", "rail"]
        obstacle_type = random.choice(obstacle_types)
        self.obstacles.append({
            'x': random.randint(100, 700),
            'y': random.randint(200, 450),
            'type': obstacle_type,
            'size': random.uniform(0.8, 1.2)
        })
    
    def spawn_collectible(self):
        collectible_types = ["coin", "star", "boost"]
        col_type = random.choice(collectible_types)
        self.collectibles.append({
            'x': random.randint(100, 700),
            'y': random.randint(100, 400),
            'type': col_type
        })
    
    def draw(self):
        screen.fill((135, 206, 235))
        
        pygame.draw.rect(screen, (139, 90, 43), (0, 500, WIDTH, 100))
        pygame.draw.line(screen, WHITE, (0, 500), (WIDTH, 500), 3)
        
        for ramp in self.ramps:
            color = (100, 100, 100) if ramp['y'] > 400 else (150, 150, 150)
            pygame.draw.polygon(screen, color, [
                (ramp['x'], ramp['y'] + ramp['height']),
                (ramp['x'] + ramp['width'], ramp['y'] + ramp['height']),
                (ramp['x'] + ramp['width']//2, ramp['y'])
            ])
        
        for obs in self.obstacles:
            if obs['type'] == 'barrier':
                pygame.draw.rect(screen, RED, (obs['x'] - 20, obs['y'] - 10, 40, 20))
            elif obs['type'] == 'cone':
                pygame.draw.polygon(screen, ORANGE, [(obs['x'], obs['y'] - 15), 
                                                     (obs['x'] - 10, obs['y']), 
                                                     (obs['x'] + 10, obs['y'])])
            else:
                pygame.draw.line(screen, GRAY if 'GRAY' in dir() else (128, 128, 128), 
                               (obs['x'] - 25, obs['y']), (obs['x'] + 25, obs['y']), 5)
        
        for col in self.collectibles:
            if col['type'] == 'coin':
                pygame.draw.circle(screen, YELLOW, (int(col['x']), int(col['y'])), 10)
            elif col['type'] == 'star':
                for i in range(5):
                    angle = i * 72 + pygame.time.get_ticks() * 0.005
                    star_x = col['x'] + math.cos(angle) * 12
                    star_y = col['y'] + math.sin(angle) * 12
                    pygame.draw.circle(screen, YELLOW, (int(star_x), int(star_y)), 4)
            else:
                pygame.draw.polygon(screen, GREEN, [(col['x'], col['y'] - 12),
                                                   (col['x'] - 10, col['y'] + 8),
                                                   (col['x'] + 10, col['y'] + 8)])
        
        board_surface = pygame.Surface((60, 15), pygame.SRCALPHA)
        pygame.draw.rect(board_surface, (139, 69, 19), (0, 0, 60, 12), border_radius=3)
        rotated_board = pygame.transform.rotate(board_surface, self.rotation)
        rect = rotated_board.get_rect(center=(self.player_x, self.player_y))
        screen.blit(rotated_board, rect)
        
        pygame.draw.circle(screen, BLUE, (int(self.player_x), int(self.player_y)), 25)
        
        for p in self.particles:
            pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), int(p['size']))
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
    
    def draw_hud(self):
        pygame.draw.rect(screen, (0, 0, 0, 128), (10, 10, 220, 120), border_radius=10)
        
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        combo_text = self.font.render(f"连击: {self.combo}x", True, ORANGE)
        screen.blit(combo_text, (20, 50))
        
        style_text = self.font.render(f"风格: {self.style_points}", True, PURPLE)
        screen.blit(style_text, (20, 80))
        
        level_text = self.font.render(f"等级: {self.level}", True, GREEN)
        screen.blit(level_text, (130, 20))
        
        exp_text = self.font.render(f"经验: {self.exp}", True, (200, 200, 100))
        screen.blit(exp_text, (130, 50))
        
        diff_text = self.font.render(f"难度: {self.difficulties[self.difficulty]}", True, RED)
        screen.blit(diff_text, (130, 80))
        
        controls_text = self.font.render("←→移动 空格:Ollie 上:翻转 下:转圈", True, (150, 150, 150))
        screen.blit(controls_text, (180, 560))
        
        if self.tricks:
            trick_text = self.font.render(f"动作: {', '.join(self.tricks[-3:])}", True, YELLOW)
            screen.blit(trick_text, (400, 10))
    
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        text = self.large_font.render("游戏结束!", True, BLUE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 150))
        
        score_text = self.font.render(f"最终分数: {self.score}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 220))
        
        max_combo_text = self.font.render(f"最高连击: {self.max_combo}x", True, ORANGE)
        screen.blit(max_combo_text, (WIDTH//2 - max_combo_text.get_width()//2, 260))
        
        level_text = self.font.render(f"达到等级: {self.level}", True, GREEN)
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, 300))
        
        unlock_text = self.font.render(f"已解锁动作: {len(self.unlocked_moves)}", True, PURPLE)
        screen.blit(unlock_text, (WIDTH//2 - unlock_text.get_width()//2, 340))
        
        restart_text = self.font.render("按 R 重新开始 | D 难度 | U 解锁", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 400))
    
    def perform_trick(self, trick_name):
        if trick_name in self.unlocked_moves or self.level >= 3:
            points = self.move_descriptions[trick_name]["points"] * (1 + self.difficulty * 0.5)
            self.score += int(points)
            self.style_points += int(points * 0.5)
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            self.tricks.append(self.move_descriptions[trick_name]["name"])
            
            for _ in range(15):
                self.particles.append({
                    'x': self.player_x + random.randint(-30, 30),
                    'y': self.player_y + random.randint(-30, 30),
                    'vx': random.uniform(-3, 3),
                    'vy': random.uniform(-3, 3),
                    'size': random.uniform(3, 6),
                    'color': random.choice([YELLOW, ORANGE, PURPLE])
                })
            
            return True
        return False
    
    def unlock_move(self):
        moves_by_level = {
            2: "pop_shuvit",
            4: "fs_180",
            6: "hardflip",
            8: "360_flip",
            10: "laser_flip"
        }
        
        unlocked = []
        for lvl, move in moves_by_level.items():
            if self.level >= lvl and move not in self.unlocked_moves:
                self.unlocked_moves.append(move)
                unlocked.append(self.move_descriptions[move]["name"])
        
        return unlocked
    
    def update(self):
        if self.game_over:
            return
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.velocity_x -= 0.5
        if keys[pygame.K_RIGHT]:
            self.velocity_x += 0.5
        
        if keys[pygame.K_SPACE] and self.player_y > 200:
            self.velocity_y = -15
            self.perform_trick("ollie")
        
        if keys[pygame.K_UP]:
            self.rotation = (self.rotation + 10) % 360
            if self.rotation % 90 == 0:
                self.perform_trick("kickflip")
        
        if keys[pygame.K_DOWN]:
            self.rotation = (self.rotation - 10) % 360
            if self.rotation % 90 == 0:
                self.perform_trick("heelflip")
        
        if keys[pygame.K_a] and self.level >= 2:
            self.perform_trick("pop_shuvit")
        if keys[pygame.K_d] and self.level >= 4:
            self.perform_trick("fs_180")
        
        self.velocity_x *= 0.98
        self.velocity_y += 0.8
        
        self.player_x += self.velocity_x
        self.player_y += self.velocity_y
        
        self.player_x = max(30, min(WIDTH - 30, self.player_x))
        
        if self.player_y > 450:
            self.player_y = 450
            self.velocity_y = 0
            if abs(self.velocity_x) > 1:
                for _ in range(3):
                    self.particles.append({
                        'x': self.player_x + random.randint(-20, 20),
                        'y': self.player_y + 20,
                        'vx': random.uniform(-2, 2),
                        'vy': random.uniform(-3, 0),
                        'size': random.uniform(2, 4),
                        'color': (200, 200, 200)
                    })
        
        if abs(self.velocity_x) < 0.1 and self.combo > 0:
            self.combo = 0
        
        for col in self.collectibles[:]:
            dist = math.hypot(self.player_x - col['x'], self.player_y - col['y'])
            if dist < 40:
                if col['type'] == 'coin':
                    self.score += 10
                elif col['type'] == 'star':
                    self.style_points += 50
                else:
                    self.velocity_x *= 1.5
                self.collectibles.remove(col)
        
        for obs in self.obstacles:
            dist = math.hypot(self.player_x - obs['x'], self.player_y - obs['y'])
            if dist < 30 * obs['size']:
                if self.level < 3:
                    self.game_over = True
        
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1
            p['size'] *= 0.95
        
        self.particles = [p for p in self.particles if p['size'] > 0.5]
        
        if self.player_y < 100:
            self.game_over = True
        
        self.exp += 1
        if self.exp >= 100:
            self.level += 1
            self.exp -= 100
            new_moves = self.unlock_move()
            if new_moves:
                pass
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.__init__()
            elif event.key == pygame.K_d:
                self.difficulty = (self.difficulty + 1) % 4
            elif event.key == pygame.K_u:
                pass

game = SkateboardGame()
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
