import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("放置挖矿")

BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BROWN = (139, 90, 43)
GOLD = (255, 200, 50)
DIAMOND = (100, 255, 255)

class IdleMining:
    def __init__(self):
        self.money = 100
        self.pickaxes = 1
        self.miners = 0
        self.gold = 0
        self.diamonds = 0
        self.font = pygame.font.Font(None, 32)
        self.clock = pygame.time.Clock()
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= 1000:
            self.gold += self.pickaxes * (1 + self.miners * 0.4)
            if random.random() < 0.1 * self.miners:
                self.diamonds += 1
            self.last_update = now

    def draw(self):
        screen.fill(BROWN)
        
        for i in range(self.pickaxes):
            x = 50 + i * 80
            pygame.draw.polygon(screen, GRAY, [(x, 400), (x+20, 450), (x+40, 400)])
        
        title_text = self.font.render("放置挖矿", True, BLACK)
        screen.blit(title_text, (350, 20))
        
        money_text = self.font.render(f"金币: {int(self.money)}", True, BLACK)
        screen.blit(money_text, (50, 70))
        
        gold_text = self.font.render(f"黄金: {int(self.gold)}", True, GOLD)
        screen.blit(gold_text, (50, 100))
        
        diamond_text = self.font.render(f"钻石: {int(self.diamonds)}", True, DIAMOND)
        screen.blit(diamond_text, (50, 130))
        
        pickaxes_text = self.font.render(f"镐子: {self.pickaxes}", True, BLACK)
        screen.blit(pickaxes_text, (50, 160))
        
        miners_text = self.font.render(f"矿工: {self.miners}", True, BLACK)
        screen.blit(miners_text, (50, 190))
        
        buy_pickaxe_text = self.font.render(f"购买镐子 (150金币)", True, BLACK)
        pygame.draw.rect(screen, (100, 150, 255), (50, 230, 220, 40))
        screen.blit(buy_pickaxe_text, (60, 240))
        
        hire_miner_text = self.font.render(f"雇佣矿工 (100金币)", True, BLACK)
        pygame.draw.rect(screen, (100, 150, 255), (50, 290, 220, 40))
        screen.blit(hire_miner_text, (60, 300))
        
        sell_text = self.font.render(f"出售资源", True, BLACK)
        pygame.draw.rect(screen, (255, 150, 100), (50, 350, 220, 40))
        screen.blit(sell_text, (60, 360))

    def handle_click(self, pos):
        if 50 <= pos[0] <= 270 and 230 <= pos[1] <= 270:
            if self.money >= 150:
                self.money -= 150
                self.pickaxes += 1
        elif 50 <= pos[0] <= 270 and 290 <= pos[1] <= 330:
            if self.money >= 100:
                self.money -= 100
                self.miners += 1
        elif 50 <= pos[0] <= 270 and 350 <= pos[1] <= 390:
            self.money += int(self.gold) + int(self.diamonds) * 10
            self.gold = 0
            self.diamonds = 0

game = IdleMining()
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