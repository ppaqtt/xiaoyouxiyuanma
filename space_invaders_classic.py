import pygame
import random
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("太空侵略者 Space Invaders")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 - 25
        self.y = SCREEN_HEIGHT - 60
        self.width = 50
        self.height = 40
        self.speed = 5
        self.bullets = []
        self.last_shot = 0
        self.shoot_delay = 300

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
        
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot > self.shoot_delay:
                self.bullets.append(Bullet(self.x + self.width // 2 - 2, self.y))
                self.last_shot = current_time
        
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < 0:
                self.bullets.remove(bullet)

    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, WHITE, (self.x + 10, self.y - 10, 30, 10))
        for bullet in self.bullets:
            bullet.draw(surface)

class Bullet:
    def __init__(self, x, y, speed=-8):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 10
        self.speed = speed

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, YELLOW, (self.x, self.y, self.width, self.height))

class Alien:
    def __init__(self, x, y, alien_type):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.type = alien_type
        self.frame = 0

    def draw(self, surface):
        colors = [RED, GREEN, YELLOW, PURPLE, CYAN]
        color = colors[self.type % len(colors)]
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(surface, BLACK, (self.x + 10, self.y + 10), 5)
        pygame.draw.circle(surface, BLACK, (self.x + 30, self.y + 10), 5)

class UFO:
    def __init__(self):
        self.x = -60
        self.y = 50
        self.width = 60
        self.height = 30
        self.speed = 2
        self.active = False
        self.timer = 0

    def update(self):
        self.timer += 1
        if not self.active and random.random() < 0.005:
            self.active = True
            self.x = -60
        if self.active:
            self.x += self.speed
            if self.x > SCREEN_WIDTH + 60:
                self.active = False

    def draw(self, surface):
        if self.active:
            pygame.draw.ellipse(surface, CYAN, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(surface, WHITE, (self.x + 10, self.y + 5, 40, 10))

class Bunker:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 60
        self.health = 100

    def draw(self, surface):
        if self.health > 0:
            pygame.draw.rect(surface, GREEN, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(surface, BLACK, (self.x + 10, self.y, 20, 30))
            pygame.draw.rect(surface, BLACK, (self.x + 50, self.y, 20, 30))

class Game:
    def __init__(self):
        self.state = 'menu'
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.lives = 3
        self.load_high_score()
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.aliens = self.create_aliens()
        self.alien_bullets = []
        self.alien_direction = 1
        self.alien_speed = 1
        self.ufo = UFO()
        self.bunkers = [
            Bunker(100, SCREEN_HEIGHT - 150),
            Bunker(300, SCREEN_HEIGHT - 150),
            Bunker(500, SCREEN_HEIGHT - 150),
            Bunker(700, SCREEN_HEIGHT - 150)
        ]
        self.alien_timer = 0

    def create_aliens(self):
        aliens = []
        for row in range(5):
            for col in range(11):
                x = 100 + col * 60
                y = 50 + row * 50
                aliens.append(Alien(x, y, row))
        return aliens

    def load_high_score(self):
        try:
            with open('si_highscore.txt', 'r') as f:
                self.high_score = int(f.read())
        except:
            self.high_score = 0

    def save_high_score(self):
        with open('si_highscore.txt', 'w') as f:
            f.write(str(self.high_score))

    def update_aliens(self):
        self.alien_timer += 1
        move_interval = max(10, 30 - self.level * 2)
        if self.alien_timer >= move_interval:
            self.alien_timer = 0
            move_down = False
            for alien in self.aliens:
                alien.x += self.alien_speed * self.alien_direction
                if alien.x <= 0 or alien.x + alien.width >= SCREEN_WIDTH:
                    move_down = True
            
            if move_down:
                self.alien_direction *= -1
                for alien in self.aliens:
                    alien.y += 20

            if random.random() < 0.02 and self.aliens:
                shooter = random.choice(self.aliens)
                self.alien_bullets.append(Bullet(shooter.x + shooter.width // 2 - 2, shooter.y + shooter.height, 5))

        for bullet in self.alien_bullets[:]:
            bullet.update()
            if bullet.y > SCREEN_HEIGHT:
                self.alien_bullets.remove(bullet)

    def check_collisions(self):
        for bullet in self.player.bullets[:]:
            for alien in self.aliens[:]:
                if (bullet.x < alien.x + alien.width and
                    bullet.x + bullet.width > alien.x and
                    bullet.y < alien.y + alien.height and
                    bullet.y + bullet.height > alien.y):
                    self.aliens.remove(alien)
                    self.player.bullets.remove(bullet)
                    self.score += (50 + alien.type * 10)
                    break
        
        for bullet in self.player.bullets[:]:
            if self.ufo.active:
                if (bullet.x < self.ufo.x + self.ufo.width and
                    bullet.x + bullet.width > self.ufo.x and
                    bullet.y < self.ufo.y + self.ufo.height and
                    bullet.y + bullet.height > self.ufo.y):
                    self.ufo.active = False
                    self.player.bullets.remove(bullet)
                    self.score += 200
                    break
        
        for bullet in self.alien_bullets[:]:
            if (bullet.x < self.player.x + self.player.width and
                bullet.x + bullet.width > self.player.x and
                bullet.y < self.player.y + self.player.height and
                bullet.y + bullet.height > self.player.y):
                self.alien_bullets.remove(bullet)
                self.lives -= 1
                if self.lives <= 0:
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
                    self.state = 'gameover'
        
        for bullet in self.alien_bullets[:]:
            for bunker in self.bunkers:
                if bunker.health > 0:
                    if (bullet.x < bunker.x + bunker.width and
                        bullet.x + bullet.width > bunker.x and
                        bullet.y < bunker.y + bunker.height and
                        bullet.y + bullet.height > bunker.y):
                        bunker.health -= 25
                        self.alien_bullets.remove(bullet)
                        break
        
        for alien in self.aliens:
            if (alien.x < self.player.x + self.player.width and
                alien.x + alien.width > self.player.x and
                alien.y < self.player.y + self.player.height and
                alien.y + alien.height > self.player.y):
                self.lives = 0
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                self.state = 'gameover'

        if not self.aliens:
            self.level += 1
            self.alien_speed = min(3, 1 + self.level * 0.2)
            self.aliens = self.create_aliens()

    def draw_menu(self):
        screen.fill(BLACK)
        font = pygame.font.Font(None, 72)
        title = font.render("太空侵略者 SPACE INVADERS", True, GREEN)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        font = pygame.font.Font(None, 36)
        instructions = [
            "操作说明：",
            "WASD / 方向键 - 移动",
            "W / 空格 / 上 - 射击",
            "",
            "游戏规则：",
            "消灭所有外星人，躲避子弹！",
            "",
            "按空格键开始游戏"
        ]
        y_pos = 200
        for line in instructions:
            text = font.render(line, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 40

        high_score_text = font.render(f"最高分: {self.high_score}", True, WHITE)
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, 500))

    def draw_game(self):
        screen.fill(BLACK)
        
        for bunker in self.bunkers:
            bunker.draw(screen)
        
        for alien in self.aliens:
            alien.draw(screen)
        
        self.ufo.draw(screen)
        self.player.draw(screen)
        
        for bullet in self.alien_bullets:
            bullet.draw(screen)
        
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"分数: {self.score}", True, WHITE)
        lives_text = font.render(f"生命: {self.lives}", True, WHITE)
        level_text = font.render(f"关卡: {self.level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (200, 10))
        screen.blit(level_text, (380, 10))

    def draw_gameover(self):
        screen.fill(BLACK)
        font = pygame.font.Font(None, 72)
        gameover_text = font.render("游戏结束", True, RED)
        screen.blit(gameover_text, (SCREEN_WIDTH // 2 - gameover_text.get_width() // 2, 150))
        
        font = pygame.font.Font(None, 48)
        score_text = font.render(f"得分: {self.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))
        
        font = pygame.font.Font(None, 36)
        restart_text = font.render("按空格键重新开始", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 400))

def main():
    clock = pygame.time.Clock()
    game = Game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.state == 'menu':
                        game.state = 'playing'
                    elif game.state == 'gameover':
                        game.reset_game()
                        game.state = 'playing'

        if game.state == 'menu':
            game.draw_menu()
        elif game.state == 'gameover':
            game.draw_gameover()
        elif game.state == 'playing':
            game.player.update()
            game.update_aliens()
            game.ufo.update()
            game.check_collisions()
            game.draw_game()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
