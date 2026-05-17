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

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("僵尸生存")

clock = pygame.time.Clock()
font = get_chinese_font(30)

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 20
        self.speed = 4
        self.health = 100
        self.max_health = 100
        self.ammo = 30
        self.max_ammo = 30
        self.score = 0
    
    def move(self, keys):
        if keys[pygame.K_w] and self.y > self.radius:
            self.y -= self.speed
        if keys[pygame.K_s] and self.y < HEIGHT - self.radius:
            self.y += self.speed
        if keys[pygame.K_a] and self.x > self.radius:
            self.x -= self.speed
        if keys[pygame.K_d] and self.x < WIDTH - self.radius:
            self.x += self.speed
    
    def draw(self):
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)

class Zombie:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.speed = 1.5
        self.health = 50
        self.max_health = 50
    
    def chase(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
    
    def draw(self):
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), self.radius)
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x - 15, self.y - 30, 30, 5))
        pygame.draw.rect(screen, GREEN, (self.x - 15, self.y - 30, 30 * health_ratio, 5))

class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.speed = 12
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        self.vx = (dx / distance) * self.speed
        self.vy = (dy / distance) * self.speed
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
    
    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), 5)

class Pickup:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.radius = 10
        self.type = type
        self.color = YELLOW if type == 'ammo' else GREEN
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

def zombie_survival():
    player = Player()
    zombies = []
    bullets = []
    pickups = []
    
    game_over = False
    round_number = 1
    
    def spawn_zombie():
        side = random.randint(0, 3)
        if side == 0:
            x = random.randint(0, WIDTH)
            y = -30
        elif side == 1:
            x = WIDTH + 30
            y = random.randint(0, HEIGHT)
        elif side == 2:
            x = random.randint(0, WIDTH)
            y = HEIGHT + 30
        else:
            x = -30
            y = random.randint(0, HEIGHT)
        zombies.append(Zombie(x, y))
    
    for _ in range(3):
        spawn_zombie()
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and player.ammo > 0:
                    mouse_x, mouse_y = event.pos
                    bullets.append(Bullet(player.x, player.y, mouse_x, mouse_y))
                    player.ammo -= 1
        
        keys = pygame.key.get_pressed()
        player.move(keys)
        
        for zombie in zombies:
            zombie.chase(player)
        
        for bullet in bullets[:]:
            bullet.update()
            if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
                bullets.remove(bullet)
        
        for bullet in bullets[:]:
            for zombie in zombies[:]:
                distance = math.sqrt((bullet.x - zombie.x)**2 + (bullet.y - zombie.y)**2)
                if distance < zombie.radius + 5:
                    zombie.health -= 25
                    if bullet in bullets:
                        bullets.remove(bullet)
                    if zombie.health <= 0:
                        zombies.remove(zombie)
                        player.score += 10
                        if random.randint(1, 3) == 1:
                            pickups.append(Pickup(zombie.x, zombie.y, random.choice(['ammo', 'health'])))
                    break
        
        for zombie in zombies:
            distance = math.sqrt((player.x - zombie.x)**2 + (player.y - zombie.y)**2)
            if distance < player.radius + zombie.radius:
                player.health -= 0.5
        
        for pickup in pickups[:]:
            distance = math.sqrt((player.x - pickup.x)**2 + (player.y - pickup.y)**2)
            if distance < player.radius + pickup.radius:
                if pickup.type == 'ammo':
                    player.ammo = min(player.max_ammo, player.ammo + 10)
                else:
                    player.health = min(player.max_health, player.health + 25)
                pickups.remove(pickup)
        
        if len(zombies) == 0:
            round_number += 1
            for _ in range(3 + round_number * 2):
                spawn_zombie()
        
        if random.randint(1, 120) == 1:
            spawn_zombie()
        
        if player.health <= 0:
            game_over = True
        
        for pickup in pickups:
            pickup.draw()
        for zombie in zombies:
            zombie.draw()
        for bullet in bullets:
            bullet.draw()
        player.draw()
        
        health_text = font.render(f"生命: {int(player.health)}", True, RED)
        ammo_text = font.render(f"弹药: {player.ammo}", True, YELLOW)
        score_text = font.render(f"得分: {player.score}", True, WHITE)
        round_text = font.render(f"回合: {round_number}", True, WHITE)
        
        screen.blit(health_text, (10, 10))
        screen.blit(ammo_text, (10, 50))
        screen.blit(score_text, (10, 90))
        screen.blit(round_text, (WIDTH - 100, 10))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    result_text = font.render(f"游戏结束! 最终得分: {player.score}", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - 150, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    zombie_survival()