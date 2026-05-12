import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("坦克大战")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)

class Tank:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.color = color
        self.angle = 0
        self.speed = 3
    
    def rotate(self, direction):
        self.angle = (self.angle + direction * 5) % 360
    
    def move_forward(self):
        rad = -self.angle * 3.14159 / 180
        self.x += self.speed * -1 * (1 if -90 <= self.angle % 360 <= 90 else -1)
    
    def draw(self):
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(surface, self.color, (0, 0, self.width, self.height))
        rotated = pygame.transform.rotate(surface, self.angle)
        screen.blit(rotated, (self.x - rotated.get_width()//2, self.y - rotated.get_height()//2))

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        self.radius = 5
    
    def move(self):
        rad = -self.angle * 3.14159 / 180
        self.x += self.speed * (-1 if -90 <= self.angle % 360 <= 90 else 1)
        self.y += self.speed * (-1 if 0 <= self.angle % 360 <= 180 else 1)
    
    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
    
    def is_off_screen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

def tank_battle():
    player = Tank(WIDTH//2, HEIGHT - 100, GREEN)
    enemies = [Tank(random.randint(100, WIDTH-100), 100, RED) for _ in range(3)]
    
    player_bullets = []
    enemy_bullets = []
    
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
                    player_bullets.append(Bullet(player.x, player.y, player.angle))
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.rotate(-1)
        if keys[pygame.K_RIGHT]:
            player.rotate(1)
        if keys[pygame.K_UP]:
            player.move_forward()
        
        if random.randint(1, 60) == 1:
            for enemy in enemies:
                if random.randint(0, 1):
                    enemy_bullets.append(Bullet(enemy.x, enemy.y, enemy.angle))
        
        for bullet in player_bullets:
            bullet.move()
            if bullet.is_off_screen():
                player_bullets.remove(bullet)
            else:
                for enemy in enemies:
                    if (bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2 < 900:
                        enemies.remove(enemy)
                        player_bullets.remove(bullet)
                        score += 100
                        break
        
        for bullet in enemy_bullets:
            bullet.move()
            if bullet.is_off_screen():
                enemy_bullets.remove(bullet)
            else:
                if (bullet.x - player.x)**2 + (bullet.y - player.y)**2 < 900:
                    lives -= 1
                    enemy_bullets.remove(bullet)
                    if lives == 0:
                        game_over = True
        
        if len(enemies) == 0:
            enemies = [Tank(random.randint(100, WIDTH-100), 100, RED) for _ in range(3)]
        
        for enemy in enemies:
            enemy.x += random.choice([-2, 2])
            if enemy.x < 50:
                enemy.x = 50
            if enemy.x > WIDTH - 50:
                enemy.x = WIDTH - 50
        
        pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, 10))
        pygame.draw.rect(screen, GRAY, (0, HEIGHT - 10, WIDTH, 10))
        pygame.draw.rect(screen, GRAY, (0, 0, 10, HEIGHT))
        pygame.draw.rect(screen, GRAY, (WIDTH - 10, 0, 10, HEIGHT))
        
        player.draw()
        for enemy in enemies:
            enemy.draw()
        
        for bullet in player_bullets:
            bullet.draw()
        for bullet in enemy_bullets:
            bullet.draw()
        
        score_text = font.render(f"分数: {score}", True, WHITE)
        lives_text = font.render(f"生命: {lives}", True, WHITE)
        screen.blit(score_text, (10, 20))
        screen.blit(lives_text, (10, 50))
        
        controls_text = font.render("←→转向 | ↑前进 | 空格射击", True, WHITE)
        screen.blit(controls_text, (WIDTH - 250, 10))
        
        pygame.display.update()
        clock.tick(30)
    
    screen.fill(RED)
    game_over_text = font.render(f"游戏结束! 得分: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    tank_battle()