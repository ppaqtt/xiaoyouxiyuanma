import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("太空侵略者")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 60
        self.width = 50
        self.height = 30
        self.speed = 5
    
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed
    
    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLUE, (self.x + 15, self.y - 15, 20, 20))

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 8
        self.radius = 4
    
    def move(self):
        self.y -= self.speed
    
    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.direction = 1
        self.speed = 1
        self.drop_amount = 30
    
    def move(self):
        self.x += self.direction * self.speed
        if self.x <= 0 or self.x >= WIDTH - self.width:
            self.direction *= -1
            self.y += self.drop_amount
    
    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(screen, WHITE, (self.x + 10, self.y + 10), 5)
        pygame.draw.circle(screen, WHITE, (self.x + 30, self.y + 10), 5)

class EnemyBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.radius = 5
    
    def move(self):
        self.y += self.speed
    
    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)

def space_invaders():
    player = Player()
    bullets = []
    enemies = []
    enemy_bullets = []
    score = 0
    lives = 3
    game_over = False
    
    for row in range(3):
        for col in range(8):
            enemy = Enemy(50 + col * 90, 50 + row * 60)
            enemies.append(enemy)
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append(Bullet(player.x + player.width // 2, player.y))
        
        keys = pygame.key.get_pressed()
        player.move(keys)
        
        for bullet in bullets[:]:
            bullet.move()
            if bullet.y < 0:
                bullets.remove(bullet)
        
        for enemy in enemies[:]:
            enemy.move()
            if enemy.y > HEIGHT - 100:
                game_over = True
                break
        
        if random.randint(1, 60) == 1 and enemies:
            enemy = random.choice(enemies)
            enemy_bullets.append(EnemyBullet(enemy.x + enemy.width // 2, enemy.y + enemy.height))
        
        for bullet in enemy_bullets[:]:
            bullet.move()
            if bullet.y > HEIGHT:
                enemy_bullets.remove(bullet)
        
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if (enemy.x < bullet.x < enemy.x + enemy.width and
                    enemy.y < bullet.y < enemy.y + enemy.height):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 100
                    break
        
        for bullet in enemy_bullets[:]:
            if (player.x < bullet.x < player.x + player.width and
                player.y < bullet.y < player.y + player.height):
                enemy_bullets.remove(bullet)
                lives -= 1
                if lives == 0:
                    game_over = True
        
        if not enemies:
            for row in range(3):
                for col in range(8):
                    enemy = Enemy(50 + col * 90, 50 + row * 60)
                    enemy.speed += 0.2
                    enemies.append(enemy)
        
        player.draw()
        for bullet in bullets:
            bullet.draw()
        for enemy in enemies:
            enemy.draw()
        for bullet in enemy_bullets:
            bullet.draw()
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        lives_text = font.render(f"生命: {lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 100, 10))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    result_text = font.render(f"游戏结束! 最终得分: {score}", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - 150, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    space_invaders()