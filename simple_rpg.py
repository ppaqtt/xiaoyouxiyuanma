import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 200)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("简单RPG")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 20
        self.speed = 4
        self.health = 100
        self.max_health = 100
        self.level = 1
        self.xp = 0
        self.xp_to_next = 100
        self.attack = 10
        self.defense = 5
    
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > self.radius:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.radius:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > self.radius:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.radius:
            self.y += self.speed
    
    def level_up(self):
        self.level += 1
        self.xp -= self.xp_to_next
        self.xp_to_next = int(self.xp_to_next * 1.5)
        self.max_health += 20
        self.health = self.max_health
        self.attack += 5
        self.defense += 3
    
    def draw(self):
        pygame.draw.circle(screen, BLUE, (self.x, self.y), self.radius)

class Enemy:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.radius = 15
        self.health = 50 + random.randint(0, 30)
        self.max_health = self.health
        self.attack = 5 + random.randint(0, 10)
        self.xp_reward = 20 + random.randint(0, 20)
        self.color = RED
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x - 20, self.y - 30, 40, 5))
        pygame.draw.rect(screen, GREEN, (self.x - 20, self.y - 30, 40 * health_ratio, 5))

class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.radius = 10
        self.type = item_type
        self.color = YELLOW if item_type == 'health' else GREEN
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

def simple_rpg():
    player = Player()
    enemies = []
    items = []
    message = ""
    message_timer = 0
    game_over = False
    
    for _ in range(5):
        enemies.append(Enemy())
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for enemy in enemies[:]:
                        distance = ((player.x - enemy.x)**2 + (player.y - enemy.y)**2)**0.5
                        if distance < 80:
                            damage = max(1, player.attack)
                            enemy.health -= damage
                            message = f"造成 {damage} 伤害!"
                            message_timer = 60
                            if enemy.health <= 0:
                                player.xp += enemy.xp_reward
                                if player.xp >= player.xp_to_next:
                                    player.level_up()
                                    message = "升级了!"
                                    message_timer = 120
                                enemies.remove(enemy)
                                enemies.append(Enemy())
                                if random.randint(1, 3) == 1:
                                    items.append(Item(enemy.x, enemy.y, random.choice(['health', 'xp'])))
                            else:
                                damage_taken = max(1, enemy.attack - player.defense)
                                player.health -= damage_taken
                                if player.health <= 0:
                                    game_over = True
                            break
        
        keys = pygame.key.get_pressed()
        player.move(keys)
        
        for item in items[:]:
            distance = ((player.x - item.x)**2 + (player.y - item.y)**2)**0.5
            if distance < 30:
                if item.type == 'health':
                    player.health = min(player.max_health, player.health + 30)
                    message = "获得治疗!"
                else:
                    player.xp += 30
                    message = "获得经验!"
                message_timer = 60
                items.remove(item)
        
        for enemy in enemies:
            enemy.draw()
        
        for item in items:
            item.draw()
        
        player.draw()
        
        if message_timer > 0:
            message_timer -= 1
            if message:
                msg_text = font.render(message, True, YELLOW)
                screen.blit(msg_text, (WIDTH//2 - msg_text.get_width()//2, 50))
        
        pygame.draw.rect(screen, BLACK, (10, 10, 200, 25))
        pygame.draw.rect(screen, RED, (10, 10, 200, 25))
        pygame.draw.rect(screen, GREEN, (10, 10, 200 * (player.health / player.max_health), 25))
        
        pygame.draw.rect(screen, BLACK, (10, 40, 200, 25))
        pygame.draw.rect(screen, (100, 0, 100), (10, 40, 200, 25))
        pygame.draw.rect(screen, (200, 0, 200), (10, 40, 200 * (player.xp / player.xp_to_next), 25))
        
        stats_text = font.render(f"等级: {player.level} 攻击: {player.attack} 防御: {player.defense}", True, WHITE)
        screen.blit(stats_text, (10, 70))
        
        instruction_text = font.render("方向键移动 | 空格攻击", True, WHITE)
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, HEIGHT - 30))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    result_text = font.render(f"游戏结束! 最终等级: {player.level}", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - 150, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    simple_rpg()