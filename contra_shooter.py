#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
魂斗罗风格射击 - 横版动作射击游戏
经典横版射击，消灭敌人
"""

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

WIDTH, HEIGHT = 900, 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 100)
RED = (255, 50, 50)
BLUE = (0, 100, 200)
YELLOW = (255, 200, 0)
PURPLE = (150, 50, 200)
ORANGE = (255, 150, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("魂斗罗风格射击 - 横版动作")
clock = pygame.time.Clock()
font_large = get_chinese_font(50)
font_medium = get_chinese_font(36)
font_small = get_chinese_font(24)

class Player:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT // 2
        self.width = 40
        self.height = 30
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.shoot_cooldown = 0
        self.weapon_level = 1
        self.invincible = 0
        self.jumping = False
        self.jump_velocity = 0
        self.on_ground = True
    
    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed
        
        if keys[pygame.K_UP] and self.on_ground:
            self.jumping = True
            self.jump_velocity = -15
            self.on_ground = False
        
        if self.jumping:
            self.y += self.jump_velocity
            self.jump_velocity += 0.8
            
            if self.y > HEIGHT - 100:
                self.y = HEIGHT - 100
                self.jumping = False
                self.on_ground = True
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        if self.invincible > 0:
            self.invincible -= 1
    
    def shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 10
            return Bullet(self.x + self.width, self.y + self.height // 2, self.weapon_level)
        return None
    
    def draw(self):
        color = YELLOW if self.invincible == 0 or (self.invincible // 5) % 2 == 0 else BLACK
        
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height), 3)
        
        pygame.draw.polygon(screen, BLUE, [
            (self.x + self.width, self.y + self.height // 2),
            (self.x + self.width + 15, self.y + self.height // 2 - 10),
            (self.x + self.width + 15, self.y + self.height // 2 + 10)
        ])

class Enemy:
    def __init__(self, enemy_type, x, y):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.speed = 2
        
        if enemy_type == "soldier":
            self.health = 20
            self.width = 30
            self.height = 30
            self.color = RED
            self.points = 100
        elif enemy_type == "turret":
            self.health = 50
            self.width = 40
            self.height = 40
            self.color = PURPLE
            self.points = 200
        elif enemy_type == "jet":
            self.health = 30
            self.width = 35
            self.height = 25
            self.color = ORANGE
            self.speed = 3
            self.points = 150
        else:
            self.health = 10
            self.width = 25
            self.height = 25
            self.color = GREEN
            self.points = 50
    
    def update(self, player_y):
        self.x -= self.speed
        
        if self.type == "soldier":
            if random.random() < 0.02:
                return Bullet(self.x, self.y + self.height // 2, 0, left=False)
        elif self.type == "turret":
            if random.random() < 0.03:
                return Bullet(self.x, self.y + self.height // 2, 0, left=False)
        elif self.type == "jet":
            dy = player_y - self.y
            self.y += dy * 0.02
        
        return None
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), self.width, self.height))
        pygame.draw.rect(screen, BLACK, (int(self.x), int(self.y), self.width, self.height), 2)

class Bullet:
    def __init__(self, x, y, level, left=True):
        self.x = x
        self.y = y
        self.speed = 10 if left else -5
        self.level = level
        self.width = 20 if left else 15
        self.height = 6
    
    def update(self):
        self.x += self.speed
    
    def draw(self):
        if self.level == 0:
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 5)
        else:
            pygame.draw.ellipse(screen, YELLOW, (int(self.x), int(self.y), self.width, self.height))

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(["health", "weapon", "speed"])
        self.width = 25
        self.height = 25
    
    def update(self):
        self.x -= 1
    
    def draw(self):
        colors = {"health": GREEN, "weapon": YELLOW, "speed": BLUE}
        pygame.draw.circle(screen, colors[self.type], (int(self.x), int(self.y)), 12)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 12, 2)

class ContraGame:
    def __init__(self):
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.enemy_bullets = []
        self.powerups = []
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_over = False
        self.won = False
        self.spawn_timer = 0
        self.background_x = 0
    
    def spawn_enemy(self):
        enemy_types = ["soldier", "soldier", "jet"]
        if self.level > 2:
            enemy_types.append("turret")
        
        enemy_type = random.choice(enemy_types)
        x = WIDTH + 50
        y = random.randint(100, HEIGHT - 150)
        
        self.enemies.append(Enemy(enemy_type, x, y))
    
    def update(self):
        if self.game_over or self.won:
            return
        
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        
        if keys[pygame.K_SPACE]:
            bullet = self.player.shoot()
            if bullet:
                if bullet.speed > 0:
                    self.bullets.append(bullet)
        
        self.spawn_timer += 1
        if self.spawn_timer > max(30, 80 - self.level * 5):
            self.spawn_timer = 0
            if random.random() < 0.7:
                self.spawn_enemy()
        
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.x > WIDTH:
                self.bullets.remove(bullet)
        
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.x < 0 or bullet.x > WIDTH:
                self.enemy_bullets.remove(bullet)
        
        for enemy in self.enemies[:]:
            bullet = enemy.update(self.player.y)
            if bullet:
                self.enemy_bullets.append(bullet)
            
            if enemy.x < -50:
                self.enemies.remove(enemy)
                continue
            
            for bullet in self.bullets[:]:
                if (enemy.x < bullet.x < enemy.x + enemy.width and
                    enemy.y < bullet.y < enemy.y + enemy.height):
                    enemy.health -= 10 * bullet.level
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += enemy.points
                        
                        if random.random() < 0.2:
                            self.powerups.append(PowerUp(enemy.x, enemy.y))
        
        for bullet in self.enemy_bullets[:]:
            if (self.player.x < bullet.x < self.player.x + self.player.width and
                self.player.y < bullet.y < self.player.y + self.player.height):
                if self.player.invincible == 0:
                    self.player.health -= 20
                    self.player.invincible = 60
                    self.enemy_bullets.remove(bullet)
        
        for enemy in self.enemies:
            if (self.player.x < enemy.x + enemy.width and
                self.player.x + self.player.width > enemy.x and
                self.player.y < enemy.y + enemy.height and
                self.player.y + self.player.height > enemy.y):
                if self.player.invincible == 0:
                    self.player.health -= 30
                    self.player.invincible = 60
        
        for powerup in self.powerups[:]:
            powerup.update()
            
            if (self.player.x < powerup.x < self.player.x + self.player.width and
                self.player.y < powerup.y < self.player.y + self.player.height):
                if powerup.type == "health":
                    self.player.health = min(self.player.max_health, self.player.health + 30)
                elif powerup.type == "weapon":
                    self.player.weapon_level = min(5, self.player.weapon_level + 1)
                elif powerup.type == "speed":
                    self.player.speed += 1
                self.powerups.remove(powerup)
            elif powerup.x < -50:
                self.powerups.remove(powerup)
        
        if self.player.health <= 0:
            self.lives -= 1
            if self.lives > 0:
                self.player.health = self.player.max_health
                self.player.invincible = 120
                self.enemies.clear()
                self.enemy_bullets.clear()
            else:
                self.game_over = True
        
        if self.score >= 5000 * self.level:
            self.level += 1
            self.player.max_health += 20
            self.player.health = self.player.max_health
        
        if self.level > 5:
            self.won = True
        
        self.background_x -= 2

def contra_game():
    game = ContraGame()
    
    while True:
        if game.game_over or game.won:
            screen.fill(BLACK)
            
            if game.won:
                result = font_large.render("🎉 恭喜通关!", True, YELLOW)
                screen.blit(result, (WIDTH // 2 - 150, HEIGHT // 2 - 50))
            else:
                result = font_large.render("💀 游戏结束", True, RED)
                screen.blit(result, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
            
            score_text = font_medium.render(f"最终得分: {game.score}", True, WHITE)
            screen.blit(score_text, (WIDTH // 2 - 100, HEIGHT // 2 + 20))
            
            level_text = font_medium.render(f"到达关卡: {game.level}", True, WHITE)
            screen.blit(level_text, (WIDTH // 2 - 80, HEIGHT // 2 + 60))
            
            restart = font_small.render("按 R 重新开始", True, GREEN)
            screen.blit(restart, (WIDTH // 2 - 60, HEIGHT // 2 + 120))
            
            pygame.display.flip()
            
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            game = ContraGame()
                            waiting = False
        
        game.update()
        
        screen.fill((100, 150, 200))
        
        for i in range(0, WIDTH, 100):
            pygame.draw.rect(screen, (139, 119, 101), (i + game.background_x % 100, HEIGHT - 100, 100, 100))
        
        pygame.draw.rect(screen, (34, 139, 34), (0, HEIGHT - 100, WIDTH, 100))
        
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 50))
        
        score_text = font_medium.render(f"得分: {game.score}", True, YELLOW)
        screen.blit(score_text, (10, 10))
        
        health_ratio = game.player.health / game.player.max_health
        pygame.draw.rect(screen, RED, (150, 10, 200, 30))
        pygame.draw.rect(screen, GREEN, (150, 10, int(200 * health_ratio), 30))
        health_text = font_small.render(f"生命: {int(game.player.health)}/{game.player.max_health}", True, WHITE)
        screen.blit(health_text, (360, 15))
        
        lives_text = font_medium.render(f"生命数: {game.lives}", True, RED)
        screen.blit(lives_text, (500, 10))
        
        level_text = font_medium.render(f"关卡: {game.level}", True, WHITE)
        screen.blit(level_text, (700, 10))
        
        weapon_text = font_small.render(f"武器: Lv.{game.player.weapon_level}", True, YELLOW)
        screen.blit(weapon_text, (150, 45))
        
        game.player.draw()
        
        for enemy in game.enemies:
            enemy.draw()
        
        for bullet in game.bullets:
            bullet.draw()
        
        for bullet in game.enemy_bullets:
            bullet.draw()
        
        for powerup in game.powerups:
            powerup.draw()
        
        controls = font_small.render("←→移动 | ↑跳跃 | 空格射击 | R重新开始", True, WHITE)
        screen.blit(controls, (WIDTH // 2 - 150, HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

if __name__ == "__main__":
    contra_game()
