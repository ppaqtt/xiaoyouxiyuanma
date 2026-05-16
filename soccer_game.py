import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("热血足球")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 150, 50)
RED = (200, 50, 50)
BLUE = (50, 100, 200)
YELLOW = (255, 200, 0)
PURPLE = (138, 43, 226)
ORANGE = (255, 140, 0)

class SoccerGame:
    def __init__(self):
        self.player_x = 100
        self.player_y = 300
        self.ball_x = 400
        self.ball_y = 300
        self.ball_vx = 0
        self.ball_vy = 0
        self.goals_player = 0
        self.goals_ai = 0
        self.game_time = 90
        self.timer = 0
        self.kick_power = 0
        self.kicking = False
        self.ai_x = 700
        self.ai_y = 300
        self.game_over = False
        self.winner = None
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 48)
        self.particles = []
        
        self.level = 1
        self.exp = 0
        self.coins = 0
        
        self.difficulty = 1
        self.difficulties = ["简单", "普通", "困难", "专家"]
        
        self.mode = "friendly"
        self.league_teams = [
            {"name": "红狮队", "color": RED, "wins": 0, "losses": 0},
            {"name": "蓝鹰队", "color": BLUE, "wins": 0, "losses": 0},
            {"name": "绿龙队", "color": GREEN, "wins": 0, "losses": 0},
            {"name": "金虎队", "color": YELLOW, "wins": 0, "losses": 0},
            {"name": "紫豹队", "color": PURPLE, "wins": 0, "losses": 0}
        ]
        self.current_opponent = 0
        self.league_points = 0
        self.league_matches = 0
        
        self.powerups = []
        self.active_powerup = None
        
        self.player_stamina = 100
        self.special_shoot_ready = False
    
    def draw(self):
        screen.fill(GREEN)
        
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 40))
        pygame.draw.line(screen, WHITE, (400, 0), (400, 600), 3)
        pygame.draw.circle(screen, WHITE, (400, 300), 80, 3)
        pygame.draw.circle(screen, WHITE, (400, 300), 8)
        pygame.draw.rect(screen, WHITE, (0, 100, 15, 200))
        pygame.draw.rect(screen, WHITE, (785, 100, 15, 200))
        pygame.draw.line(screen, WHITE, (0, 200), (100, 200), 3)
        pygame.draw.line(screen, WHITE, (700, 200), (800, 200), 3)
        
        opponent_color = self.league_teams[self.current_opponent]["color"]
        
        pygame.draw.circle(screen, BLUE, (int(self.player_x), int(self.player_y)), 20)
        player_num = self.font.render("1", True, WHITE)
        screen.blit(player_num, (int(self.player_x) - 6, int(self.player_y) - 10))
        
        pygame.draw.circle(screen, opponent_color, (int(self.ai_x), int(self.ai_y)), 20)
        ai_num = self.font.render("2", True, WHITE)
        screen.blit(ai_num, (int(self.ai_x) - 6, int(self.ai_y) - 10))
        
        pygame.draw.circle(screen, YELLOW, (int(self.ball_x), int(self.ball_y)), 10)
        
        for powerup in self.powerups:
            if powerup['type'] == 'speed':
                pygame.draw.polygon(screen, PURPLE, [(powerup['x'], powerup['y'] - 12),
                                                     (powerup['x'] - 10, powerup['y'] + 8),
                                                     (powerup['x'] + 10, powerup['y'] + 8)])
            elif powerup['type'] == 'power':
                pygame.draw.polygon(screen, RED, [(powerup['x'], powerup['y'] - 12),
                                                  (powerup['x'] - 10, powerup['y'] + 8),
                                                  (powerup['x'] + 10, powerup['y'] + 8)])
            else:
                pygame.draw.circle(screen, GREEN, (int(powerup['x']), int(powerup['y'])), 10)
        
        for p in self.particles:
            pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), int(p['size']))
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
    
    def draw_hud(self):
        pygame.draw.rect(screen, (0, 0, 0, 180), (10, 50, 300, 100), border_radius=10)
        
        score_text = self.large_font.render(f"{self.goals_player} - {self.goals_ai}", True, WHITE)
        screen.blit(score_text, (20, 55))
        
        time_text = self.font.render(f"时间: {int(self.timer)}s", True, WHITE)
        screen.blit(time_text, (20, 110))
        
        team_text = self.font.render(f"对手: {self.league_teams[self.current_opponent]['name']}", True, WHITE)
        screen.blit(team_text, (180, 55))
        
        pygame.draw.rect(screen, (0, 0, 0, 180), (500, 50, 200, 80), border_radius=10)
        
        stamina_text = self.font.render(f"体力: {int(self.player_stamina)}", True, GREEN)
        screen.blit(stamina_text, (510, 60))
        
        pygame.draw.rect(screen, (100, 100, 100), (510, 90, 180, 15))
        pygame.draw.rect(screen, GREEN, (510, 90, self.player_stamina * 1.8, 15))
        
        if self.special_shoot_ready:
            ready_text = self.font.render("必杀! L", True, RED)
            screen.blit(ready_text, (550, 110))
        
        pygame.draw.rect(screen, (0, 0, 0, 180), (10, 10, 250, 40), border_radius=10)
        league_text = self.font.render(f"联赛积分: {self.league_points} | 场次: {self.league_matches}", True, YELLOW)
        screen.blit(league_text, (20, 20))
        
        diff_text = self.font.render(f"难度: {self.difficulties[self.difficulty]}", True, RED)
        screen.blit(diff_text, (700, 10))
    
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        if self.mode == "league":
            text = self.large_font.render(f"联赛结束! 积分: {self.league_points}", True, YELLOW)
        elif self.winner == "player":
            text = self.large_font.render("你赢了!", True, GREEN)
        elif self.winner == "ai":
            text = self.large_font.render("对手赢了!", True, RED)
        else:
            text = self.large_font.render("平局!", True, WHITE)
        
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 150))
        
        score_text = self.font.render(f"比分: {self.goals_player} - {self.goals_ai}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 220))
        
        stats_text = self.font.render(f"等级: {self.level} | 金币: {self.coins}", True, PURPLE)
        screen.blit(stats_text, (WIDTH//2 - stats_text.get_width()//2, 260))
        
        restart_text = self.font.render("按 R 重新开始 | D 难度 | M 模式", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 340))
    
    def spawn_powerup(self):
        powerup_types = ["speed", "power", "heal"]
        powerup = {
            "x": random.randint(100, 700),
            "y": random.randint(100, 500),
            "type": random.choice(powerup_types)
        }
        self.powerups.append(powerup)
    
    def update(self):
        if self.game_over:
            return
        
        self.timer += 1/60
        if self.timer >= self.game_time:
            self.end_match()
            return
        
        keys = pygame.key.get_pressed()
        
        stamina_cost = 0.1
        if keys[pygame.K_LEFT]:
            self.player_x = max(30, self.player_x - 5)
            self.player_stamina -= stamina_cost
        if keys[pygame.K_RIGHT]:
            self.player_x = min(770, self.player_x + 5)
            self.player_stamina -= stamina_cost
        if keys[pygame.K_UP]:
            self.player_y = max(50, self.player_y - 5)
            self.player_stamina -= stamina_cost
        if keys[pygame.K_DOWN]:
            self.player_y = min(550, self.player_y + 5)
            self.player_stamina -= stamina_cost
        
        if keys[pygame.K_SPACE] and not self.kicking:
            self.kicking = True
            self.kick_power = 0
        
        if self.kicking:
            self.kick_power = min(100, self.kick_power + 3)
            if not keys[pygame.K_SPACE]:
                dist = ((self.player_x - self.ball_x)**2 + (self.player_y - self.ball_y)**2)**0.5
                if dist < 50:
                    angle = (self.ball_y - self.player_y) / (dist + 0.1)
                    power = self.kick_power * (1.5 if self.active_powerup == "power" else 1)
                    self.ball_vx = power * 0.2
                    self.ball_vy = -angle * power * 0.15
                self.kicking = False
        
        if keys[pygame.K_l] and self.special_shoot_ready:
            dist = ((self.player_x - self.ball_x)**2 + (self.player_y - self.ball_y)**2)**0.5
            if dist < 50:
                self.ball_vx = 25
                self.ball_vy = -5
                self.special_shoot_ready = False
                self.player_stamina -= 30
        
        if abs(self.ball_x - self.player_x) < 30 and abs(self.ball_y - self.player_y) < 30:
            if not self.kicking:
                self.ball_x = self.player_x + 30
                self.ball_y = self.player_y
        
        if self.active_powerup == "speed":
            self.player_x += (5 if keys[pygame.K_RIGHT] else (-5 if keys[pygame.K_LEFT] else 0))
        
        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy
        self.ball_vx *= 0.98
        self.ball_vy *= 0.98
        
        if self.ball_y < 10 or self.ball_y > 590:
            self.ball_vy *= -0.8
        if self.ball_x < 10 or self.ball_x > 790:
            self.ball_vx *= -0.8
        
        if self.ball_x < 15 and 100 < self.ball_y < 300:
            self.goals_ai += 1
            self.reset_ball()
        if self.ball_x > 785 and 100 < self.ball_y < 300:
            self.goals_player += 1
            self.coins += 20
            self.reset_ball()
        
        target_x = self.ball_x - 50
        target_y = self.ball_y
        ai_speed = (3 + self.difficulty) * 0.5
        self.ai_x += (target_x - self.ai_x) * 0.03 * ai_speed
        self.ai_y += (target_y - self.ai_y) * 0.03 * ai_speed
        
        if abs(self.ai_x - self.ball_x) < 30 and abs(self.ai_y - self.ball_y) < 30:
            self.ball_x = self.ai_x - 30
        
        if random.random() < 0.005:
            self.spawn_powerup()
        
        for powerup in self.powerups[:]:
            dist = ((self.player_x - powerup['x'])**2 + (self.player_y - powerup['y'])**2)**0.5
            if dist < 40:
                if powerup['type'] == 'speed':
                    self.active_powerup = "speed"
                elif powerup['type'] == 'power':
                    self.active_powerup = "power"
                else:
                    self.player_stamina = min(100, self.player_stamina + 30)
                self.powerups.remove(powerup)
        
        for _ in range(2):
            self.particles.append({
                'x': self.ball_x + random.randint(-5, 5),
                'y': self.ball_y + random.randint(-5, 5),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1),
                'size': random.uniform(2, 4),
                'color': GREEN
            })
        
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['size'] *= 0.95
        
        self.particles = [p for p in self.particles if p['size'] > 0.5]
        
        if self.player_stamina >= 80 and not self.special_shoot_ready:
            self.special_shoot_ready = True
        
        self.player_stamina = max(0, self.player_stamina + 0.02)
        
        self.exp += 1
        if self.exp >= 100:
            self.level += 1
            self.exp -= 100
            self.coins += 50
    
    def end_match(self):
        if self.mode == "league":
            if self.goals_player > self.goals_ai:
                self.league_points += 3
            elif self.goals_player == self.goals_ai:
                self.league_points += 1
            
            self.league_matches += 1
            
            if self.current_opponent < len(self.league_teams) - 1:
                self.current_opponent += 1
                self.reset_ball()
                self.timer = 0
                self.goals_player = 0
                self.goals_ai = 0
            else:
                self.game_over = True
        else:
            self.game_over = True
            if self.goals_player > self.goals_ai:
                self.winner = "player"
            elif self.goals_ai > self.goals_player:
                self.winner = "ai"
            else:
                self.winner = "draw"
    
    def reset_ball(self):
        self.ball_x = 400
        self.ball_y = 300
        self.ball_vx = 0
        self.ball_vy = 0
        self.player_x = 100
        self.player_y = 300
        self.player_stamina = 100
        self.active_powerup = None
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.__init__()
            elif event.key == pygame.K_d:
                self.difficulty = (self.difficulty + 1) % 4
            elif event.key == pygame.K_m:
                self.mode = "league" if self.mode == "friendly" else "friendly"

game = SoccerGame()
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
