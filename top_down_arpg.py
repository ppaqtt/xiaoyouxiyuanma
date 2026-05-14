import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 900, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
PURPLE = (128, 0, 128)
GRAY = (100, 100, 100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("俯视角ARPG")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
big_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 20)

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed = 4
        self.radius = 15
        self.hp = 100
        self.max_hp = 100
        self.attack = 10
        self.attack_range = 50
        self.attack_cooldown = 0
        self.invincible = 0
        self.level = 1
        self.exp = 0
        self.exp_to_level = 50
        
        self.weapon = {"name": "新手剑", "damage": 10}
        self.armor = {"name": "布衣", "defense": 2}
    
    def update(self, keys, mouse_pos):
        if keys[pygame.K_w] and self.y > 20:
            self.y -= self.speed
        if keys[pygame.K_s] and self.y < HEIGHT - 20:
            self.y += self.speed
        if keys[pygame.K_a] and self.x > 20:
            self.x -= self.speed
        if keys[pygame.K_d] and self.x < WIDTH - 20:
            self.x += self.speed
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.invincible > 0:
            self.invincible -= 1
    
    def attack_enemy(self, enemies):
        if self.attack_cooldown == 0:
            self.attack_cooldown = 20
            for enemy in enemies[:]:
                dist = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
                if dist < self.attack_range + enemy.radius:
                    damage = self.weapon["damage"] + self.attack
                    enemy.hp -= damage
                    return enemy, damage
        return None, 0
    
    def level_up(self):
        if self.exp >= self.exp_to_level:
            self.level += 1
            self.exp -= self.exp_to_level
            self.exp_to_level = int(self.exp_to_level * 1.5)
            self.max_hp += 20
            self.hp = self.max_hp
            self.attack += 3
            return True
        return False
    
    def draw(self):
        color = YELLOW if self.invincible == 0 or (self.invincible // 5) % 2 == 0 else GRAY
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 20)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 20, 2)
        
        pygame.draw.rect(screen, RED, (int(self.x) - 25, int(self.y) - 40, 50, 8))
        pygame.draw.rect(screen, GREEN, (int(self.x) - 25, int(self.y) - 40, int(50 * self.hp / self.max_hp), 8))

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.radius = 15
        self.speed = 1.5
        
        if enemy_type == "slime":
            self.hp = 20
            self.max_hp = 20
            self.damage = 5
            self.exp_reward = 10
            self.color = GREEN
        elif enemy_type == "skeleton":
            self.hp = 35
            self.max_hp = 35
            self.damage = 8
            self.exp_reward = 20
            self.color = WHITE
        elif enemy_type == "demon":
            self.hp = 60
            self.max_hp = 60
            self.damage = 15
            self.exp_reward = 40
            self.color = RED
        else:
            self.hp = 30
            self.max_hp = 30
            self.damage = 10
            self.exp_reward = 15
            self.color = PURPLE
    
    def update(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        
        pygame.draw.rect(screen, RED, (int(self.x) - 15, int(self.y) - 30, 30, 5))
        pygame.draw.rect(screen, GREEN, 
                        (int(self.x) - 15, int(self.y) - 30, int(30 * self.hp / self.max_hp), 5))

class Drop:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.radius = 8
    
    def draw(self):
        if self.item_type == "health":
            pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        elif self.item_type == "weapon":
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
        elif self.item_type == "armor":
            pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.radius)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 30
        self.color = color
        self.radius = random.randint(2, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.radius *= 0.95
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), max(1, int(self.radius)))

def top_down_arpg():
    player = Player()
    enemies = []
    drops = []
    particles = []
    score = 0
    wave = 1
    spawn_timer = 0
    game_over = False
    
    for _ in range(3):
        ex = random.randint(100, WIDTH - 100)
        ey = random.randint(100, HEIGHT - 100)
        enemies.append(Enemy(ex, ey, "slime"))
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    enemy, damage = player.attack_enemy(enemies)
                    if enemy:
                        for _ in range(5):
                            particles.append(Particle(enemy.x, enemy.y, YELLOW))
        
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        player.update(keys, mouse_pos)
        
        spawn_timer += 1
        if spawn_timer > 120 - wave * 5 and len(enemies) < 5 + wave:
            spawn_timer = 0
            ex = random.choice([random.randint(50, WIDTH - 50), 
                              random.choice([50, WIDTH - 50])])
            ey = random.choice([random.randint(50, HEIGHT - 50),
                              random.choice([50, HEIGHT - 50])])
            
            if wave >= 3 and random.random() < 0.2:
                enemy_type = "demon"
            elif wave >= 2 and random.random() < 0.4:
                enemy_type = "skeleton"
            else:
                enemy_type = "slime"
            
            enemies.append(Enemy(ex, ey, enemy_type))
        
        for enemy in enemies[:]:
            enemy.update(player)
            
            dist = math.sqrt((player.x - enemy.x)**2 + (player.y - enemy.y)**2)
            if dist < player.radius + enemy.radius and player.invincible == 0:
                player.hp -= enemy.damage
                player.invincible = 60
                for _ in range(8):
                    particles.append(Particle(player.x, player.y, RED))
            
            if enemy.hp <= 0:
                enemies.remove(enemy)
                score += enemy.exp_reward
                player.exp += enemy.exp_reward
                player.level_up()
                
                if random.random() < 0.3:
                    drops.append(Drop(enemy.x, enemy.y, "health"))
                elif random.random() < 0.1:
                    drops.append(Drop(enemy.x, enemy.y, "weapon"))
                elif random.random() < 0.1:
                    drops.append(Drop(enemy.x, enemy.y, "armor"))
        
        for drop in drops[:]:
            dist = math.sqrt((player.x - drop.x)**2 + (player.y - drop.y)**2)
            if dist < 30:
                if drop.item_type == "health":
                    player.hp = min(player.max_hp, player.hp + 20)
                elif drop.item_type == "weapon":
                    player.weapon["damage"] += 5
                elif drop.item_type == "armor":
                    player.armor["defense"] += 2
                drops.remove(drop)
        
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)
        
        player.draw()
        
        for enemy in enemies:
            enemy.draw()
        
        for drop in drops:
            drop.draw()
        
        for particle in particles:
            particle.draw()
        
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 70))
        
        score_text = font.render(f"得分: {score}", True, YELLOW)
        screen.blit(score_text, (10, 10))
        
        level_text = font.render(f"等级: {player.level}", True, GREEN)
        screen.blit(level_text, (150, 10))
        
        exp_ratio = player.exp / player.exp_to_level
        pygame.draw.rect(screen, GRAY, (150, 40, 150, 15))
        pygame.draw.rect(screen, BLUE, (150, 40, int(150 * exp_ratio), 15))
        
        wave_text = font.render(f"波次: {wave}", True, WHITE)
        screen.blit(wave_text, (10, 45))
        
        weapon_text = small_font.render(f"武器: {player.weapon['name']} (+{player.weapon['damage']})", True, YELLOW)
        screen.blit(weapon_text, (320, 10))
        
        armor_text = small_font.render(f"护甲: {player.armor['name']} (+{player.armor['defense']})", True, BLUE)
        screen.blit(armor_text, (320, 35))
        
        inst = small_font.render("WASD移动 | 鼠标左键攻击 | 收集掉落物", True, WHITE)
        screen.blit(inst, (WIDTH - 280, 50))
        
        if player.hp <= 0:
            game_over = True
        
        pygame.display.flip()
        clock.tick(60)
    
    screen.fill(BLACK)
    result = big_font.render("游戏结束!", True, RED)
    screen.blit(result, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
    
    final_score = font.render(f"最终得分: {score}", True, YELLOW)
    screen.blit(final_score, (WIDTH // 2 - 80, HEIGHT // 2 + 20))
    
    final_level = font.render(f"最终等级: {player.level}", True, GREEN)
    screen.blit(final_level, (WIDTH // 2 - 80, HEIGHT // 2 + 60))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    top_down_arpg()
