import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("放置英雄")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)

class IdleHeroes:
    def __init__(self):
        self.gold = 100
        self.heroes = 1
        self.level = 1
        self.exp = 0
        self.monsters_killed = 0
        self.font = pygame.font.Font(None, 32)
        self.clock = pygame.time.Clock()
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= 1000:
            self.monsters_killed += self.heroes * self.level
            self.exp += self.monsters_killed
            self.gold += self.monsters_killed * 2
            
            if self.exp >= self.level * 100:
                self.level += 1
                self.exp = 0
            
            self.last_update = now

    def draw(self):
        screen.fill(BLACK)
        
        for i in range(self.heroes):
            x = 100 + i * 100
            pygame.draw.rect(screen, BLUE, (x, 450, 60, 80))
            pygame.draw.polygon(screen, RED, [(x+30, 460), (x+20, 480), (x+40, 480)])
        
        title_text = self.font.render("放置英雄", True, WHITE)
        screen.blit(title_text, (350, 20))
        
        gold_text = self.font.render(f"金币: {int(self.gold)}", True, GREEN)
        screen.blit(gold_text, (50, 70))
        
        level_text = self.font.render(f"等级: {self.level}", True, BLUE)
        screen.blit(level_text, (50, 100))
        
        exp_text = self.font.render(f"经验: {int(self.exp)}/{self.level * 100}", True, WHITE)
        screen.blit(exp_text, (50, 130))
        
        heroes_text = self.font.render(f"英雄: {self.heroes}", True, WHITE)
        screen.blit(heroes_text, (50, 160))
        
        monsters_text = self.font.render(f"击杀怪物: {self.monsters_killed}", True, RED)
        screen.blit(monsters_text, (50, 190))
        
        buy_hero_text = self.font.render(f"召唤英雄 (200金币)", True, BLACK)
        pygame.draw.rect(screen, GREEN, (50, 230, 200, 40))
        screen.blit(buy_hero_text, (60, 240))
        
        upgrade_text = self.font.render(f"升级英雄 (150金币)", True, BLACK)
        pygame.draw.rect(screen, BLUE, (50, 290, 200, 40))
        screen.blit(upgrade_text, (60, 300))

    def handle_click(self, pos):
        if 50 <= pos[0] <= 250 and 230 <= pos[1] <= 270:
            if self.gold >= 200:
                self.gold -= 200
                self.heroes += 1
        elif 50 <= pos[0] <= 250 and 290 <= pos[1] <= 330:
            if self.gold >= 150:
                self.gold -= 150
                self.level += 1

game = IdleHeroes()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            game.handle_click(pygame.mouse.get_pos())
    
    game.update()
    game.draw()
    pygame.display.flip()
    game.clock.tick(60)

pygame.quit()