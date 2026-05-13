import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("太空射击游戏")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)

class Player:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.speed = 7
    
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height:
            self.y += self.speed
    
    def draw(self):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))

class Bullet:
    def __init__(self, x, y):
        self.width = 5
        self.height = 15
        self.x = x
        self.y = y
        self.speed = -10
    
    def move(self):
        self.y += self.speed
    
    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))

class Enemy:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.x = random.randint(0, WIDTH - self.width)
        self.y = -self.height
        self.speed = random.randint(2, 5)
    
    def move(self):
        self.y += self.speed
    
    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

def space_shooter():
    player = Player()
    bullets = []
    enemies = []
    score = 0
    lives = 3
    game_over = False
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append(Bullet(player.x + player.width // 2 - 2, player.y))
        
        keys = pygame.key.get_pressed()
        player.move(keys)
        
        if random.randint(1, 60) == 1:
            enemies.append(Enemy())
        
        bullets = [b for b in bullets if b.y > -20]
        for bullet in bullets:
            bullet.move()
        
        enemies = [e for e in enemies if e.y < HEIGHT]
        for enemy in enemies:
            enemy.move()
            if (enemy.x < player.x + player.width and
                enemy.x + enemy.width > player.x and
                enemy.y < player.y + player.height and
                enemy.y + enemy.height > player.y):
                lives -= 1
                enemies.remove(enemy)
                if lives == 0:
                    game_over = True
        
        bullets_to_remove = []
        enemies_to_remove = []
        for bullet in bullets:
            for enemy in enemies:
                if (bullet.x < enemy.x + enemy.width and
                    bullet.x + bullet.width > enemy.x and
                    bullet.y < enemy.y + enemy.height and
                    bullet.y + bullet.height > enemy.y):
                    if bullet not in bullets_to_remove:
                        bullets_to_remove.append(bullet)
                    if enemy not in enemies_to_remove:
                        enemies_to_remove.append(enemy)
                    score += 10
        
        for bullet in bullets_to_remove:
            if bullet in bullets:
                bullets.remove(bullet)
        for enemy in enemies_to_remove:
            if enemy in enemies:
                enemies.remove(enemy)
        
        player.draw()
        for bullet in bullets:
            bullet.draw()
        for enemy in enemies:
            enemy.draw()
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        lives_text = font.render(f"生命: {lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 80, 10))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    game_over_text = font.render(f"游戏结束! 最终得分: {score}", True, RED)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    space_shooter()