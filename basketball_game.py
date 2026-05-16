import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("街头篮球")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 140, 0)
RED = (200, 50, 50)
BLUE = (50, 100, 200)
GREEN = (50, 200, 50)
YELLOW = (255, 200, 0)
PURPLE = (138, 43, 226)

class BasketballGame:
    def __init__(self):
        self.player_x = 400
        self.player_y = 450
        self.ball_x = self.player_x
        self.ball_y = self.player_y - 30
        self.ball_velocity_x = 0
        self.ball_velocity_y = 0
        self.score = 0
        self.attempts = 0
        self.ball_in_hand = True
        self.power = 0
        self.angle = 45
        self.combo = 0
        self.opponent_score = 0
        self.game_over = False
        self.turn = "player"
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 48)
        self.hoop_x = 650
        self.hoop_y = 150
        
        self.level = 1
        self.exp = 0
        self.coins = 0
        
        self.difficulty = 1
        self.difficulties = ["简单", "普通", "困难", "专家"]
        
        self.unlocked_shots = ["basic"]
        self.shot_types = {
            "basic": {"name": "普通投篮", "bonus": 1.0, "unlock_level": 1},
            "layup": {"name": "上篮", "bonus": 1.2, "unlock_level": 2},
            "dunk": {"name": "扣篮", "bonus": 1.5, "unlock_level": 3},
            "three": {"name": "三分球", "bonus": 2.0, "unlock_level": 4},
            "fadeaway": {"name": "后仰跳投", "bonus": 1.8, "unlock_level": 5}
        }
        
        self.current_shot = "basic"
        
        self.training_mode = False
        self.training_challenges = [
            {"name": "连进5球", "target": 5, "reward": 50},
            {"name": "3分钟内得20分", "target": 20, "reward": 100},
            {"name": "命中率达到80%", "target": 80, "reward": 150}
        ]
        self.current_challenge = 0
        
        self.guard_position = 550
        self.guard_speed = 2
    
    def draw(self):
        screen.fill((135, 206, 235))
        
        pygame.draw.rect(screen, (139, 90, 43), (0, 520, WIDTH, 80))
        
        pygame.draw.rect(screen, (200, 200, 200), (620, 100, 80, 10))
        pygame.draw.rect(screen, (255, 255, 255), (640, 110, 40, 60))
        pygame.draw.ellipse(screen, ORANGE, (645, 170, 30, 60))
        
        pygame.draw.circle(screen, RED, (int(self.guard_position), 200), 25)
        
        pygame.draw.circle(screen, BLUE, (int(self.player_x), int(self.player_y)), 25)
        
        if self.current_shot in ["dunk", "layup"] and not self.ball_in_hand:
            pygame.draw.arc(screen, YELLOW, 
                          (self.ball_x - 30, self.ball_y - 30, 60, 60),
                          0, math.pi, 3)
        
        pygame.draw.circle(screen, ORANGE, (int(self.ball_x), int(self.ball_y)), 12)
        
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
    
    def draw_hud(self):
        pygame.draw.rect(screen, (0, 0, 0, 128), (10, 10, 300, 130), border_radius=10)
        
        score_text = self.font.render(f"得分: {self.score}/{self.attempts}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        if self.attempts > 0:
            percent = int(self.score / self.attempts * 100)
            percent_text = self.font.render(f"命中率: {percent}%", True, GREEN)
            screen.blit(percent_text, (20, 50))
        
        combo_text = self.font.render(f"连进: {self.combo}", True, ORANGE)
        screen.blit(combo_text, (20, 80))
        
        level_text = self.font.render(f"等级: {self.level}", True, PURPLE)
        screen.blit(level_text, (200, 20))
        
        coins_text = self.font.render(f"金币: {self.coins}", True, YELLOW)
        screen.blit(coins_text, (200, 50))
        
        shot_text = self.font.render(f"投篮: {self.shot_types[self.current_shot]['name']}", True, WHITE)
        screen.blit(shot_text, (200, 80))
        
        if not self.ball_in_hand:
            power_text = self.font.render(f"力度: {int(self.power)}%", True, RED)
            screen.blit(power_text, (600, 500))
            
            pygame.draw.rect(screen, (100, 100, 100), (580, 520, 150, 20))
            pygame.draw.rect(screen, GREEN, (580, 520, self.power * 1.5, 20))
        
        pygame.draw.rect(screen, (0, 0, 0, 128), (400, 10, 200, 40), border_radius=10)
        diff_text = self.font.render(f"难度: {self.difficulties[self.difficulty]}", True, RED)
        screen.blit(diff_text, (410, 20))
        
        controls = self.font.render("←→移动 ↑↓角度 Q切换投篮 空格蓄力", True, (150, 150, 150))
        screen.blit(controls, (250, 560))
    
    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        text = self.large_font.render("训练结束!", True, ORANGE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 150))
        
        score_text = self.font.render(f"最终得分: {self.score}/{self.attempts}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 220))
        
        level_text = self.font.render(f"等级: {self.level} | 金币: {self.coins}", True, PURPLE)
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, 260))
        
        percent = int(self.score / self.attempts * 100) if self.attempts > 0 else 0
        percent_text = self.font.render(f"命中率: {percent}%", True, GREEN)
        screen.blit(percent_text, (WIDTH//2 - percent_text.get_width()//2, 300))
        
        restart_text = self.font.render("按 R 重新开始 | D 难度 | Q 切换投篮", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 380))
    
    def unlock_shots(self):
        unlocked = []
        for shot, data in self.shot_types.items():
            if self.level >= data["unlock_level"] and shot not in self.unlocked_shots:
                self.unlocked_shots.append(shot)
                unlocked.append(data["name"])
        return unlocked
    
    def update(self):
        if self.game_over:
            return
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.player_x = max(50, self.player_x - 5)
        if keys[pygame.K_RIGHT]:
            self.player_x = min(750, self.player_x + 5)
        
        if self.guard_position > 200:
            self.guard_position -= self.guard_speed * (1 + self.difficulty * 0.3)
        
        if self.ball_in_hand:
            self.ball_x = self.player_x
            self.ball_y = self.player_y - 30
            
            if keys[pygame.K_UP]:
                self.angle = min(90, self.angle + 1)
            if keys[pygame.K_DOWN]:
                self.angle = max(10, self.angle - 1)
            
            if keys[pygame.K_q]:
                shots = [s for s in self.unlocked_shots]
                current_idx = shots.index(self.current_shot) if self.current_shot in shots else 0
                self.current_shot = shots[(current_idx + 1) % len(shots)]
            
            if keys[pygame.K_SPACE]:
                self.power = min(100, self.power + 2)
            elif self.power > 0:
                self.ball_in_hand = False
                angle_rad = math.radians(self.angle)
                bonus = self.shot_types[self.current_shot]["bonus"]
                
                distance_modifier = 1.0
                if self.current_shot == "three":
                    distance_modifier = 1.3
                
                self.ball_velocity_x = math.cos(angle_rad) * self.power * 0.15
                self.ball_velocity_y = -math.sin(angle_rad) * self.power * 0.15 * distance_modifier
                self.attempts += 1
        else:
            self.ball_x += self.ball_velocity_x
            self.ball_y += self.ball_velocity_y
            self.ball_velocity_y += 0.5
            
            guard_dist = abs(self.ball_x - self.guard_position)
            if guard_dist < 50 and self.ball_velocity_y < 0:
                self.ball_velocity_x += random.uniform(-2, 2)
                self.ball_velocity_y *= 0.8
            
            if 630 <= self.ball_x <= 690 and 170 <= self.ball_y <= 230:
                dist_to_hoop = abs(self.ball_x - self.hoop_x)
                if dist_to_hoop < 25 and self.ball_velocity_y > 0:
                    bonus = self.shot_types[self.current_shot]["bonus"]
                    self.score += int(2 * bonus)
                    self.combo += 1
                    self.coins += 5 * self.combo
                    
                    self.ball_in_hand = True
                    self.ball_x = self.player_x
                    self.ball_y = self.player_y - 30
                    self.power = 0
                    
                    self.guard_position = 550
            
            if self.ball_y > 550 or self.ball_x < 0 or self.ball_x > 800:
                self.combo = 0
                self.ball_in_hand = True
                self.ball_x = self.player_x
                self.ball_y = self.player_y - 30
                self.power = 0
                
                self.guard_position = 550
        
        self.exp += 1
        if self.exp >= 100:
            self.level += 1
            self.exp -= 100
            new_shots = self.unlock_shots()
        
        if self.attempts >= 20:
            self.game_over = True
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.__init__()

game = BasketballGame()
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
