import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
BLUE = (0, 0, 200)
RED = (200, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("接金币")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)

class Player:
    def __init__(self):
        self.width = 80
        self.height = 30
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 80
        self.speed = 7
    
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed
    
    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height), border_radius=5)

class Coin:
    def __init__(self):
        self.radius = 15
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = -self.radius
        self.speed = random.randint(3, 6)
    
    def move(self):
        self.y += self.speed
    
    def draw(self):
        pygame.draw.circle(screen, GOLD, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255, 230, 0), (int(self.x), int(self.y)), self.radius - 4)

class Bomb:
    def __init__(self):
        self.radius = 15
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = -self.radius
        self.speed = random.randint(2, 4)
    
    def move(self):
        self.y += self.speed
    
    def draw(self):
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius - 3)

def collect_coins():
    player = Player()
    coins = []
    bombs = []
    score = 0
    lives = 3
    game_over = False
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        keys = pygame.key.get_pressed()
        player.move(keys)
        
        if random.randint(1, 60) == 1:
            coins.append(Coin())
        
        if random.randint(1, 120) == 1:
            bombs.append(Bomb())
        
        for coin in coins[:]:
            coin.move()
            
            if coin.y > HEIGHT:
                coins.remove(coin)
                continue
            
            if (player.x < coin.x < player.x + player.width and
                player.y < coin.y < player.y + player.height):
                coins.remove(coin)
                score += 10
        
        for bomb in bombs[:]:
            bomb.move()
            
            if bomb.y > HEIGHT:
                bombs.remove(bomb)
                continue
            
            if (player.x < bomb.x < player.x + player.width and
                player.y < bomb.y < player.y + player.height):
                bombs.remove(bomb)
                lives -= 1
                if lives == 0:
                    game_over = True
        
        player.draw()
        for coin in coins:
            coin.draw()
        for bomb in bombs:
            bomb.draw()
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        lives_text = font.render(f"生命: {lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 120, 10))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    game_over_text = font.render(f"游戏结束! 得分: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    collect_coins()