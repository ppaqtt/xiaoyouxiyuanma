import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("放置农场")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)
BROWN = (139, 90, 43)
YELLOW = (255, 200, 50)

class IdleFarm:
    def __init__(self):
        self.money = 100
        self.farms = 1
        self.farmers = 0
        self.crops = 0
        self.font = pygame.font.Font(None, 32)
        self.clock = pygame.time.Clock()
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= 1000:
            self.crops += self.farms * (1 + self.farmers * 0.5)
            self.last_update = now

    def draw(self):
        screen.fill(GREEN)
        
        pygame.draw.rect(screen, BROWN, (100, 400, 600, 150))
        
        for i in range(self.farms):
            x = 200 + i * 100
            pygame.draw.rect(screen, YELLOW, (x, 450, 60, 40))
        
        title_text = self.font.render("放置农场", True, BLACK)
        screen.blit(title_text, (350, 20))
        
        money_text = self.font.render(f"金币: {int(self.money)}", True, BLACK)
        screen.blit(money_text, (50, 70))
        
        crops_text = self.font.render(f"作物: {int(self.crops)}", True, BLACK)
        screen.blit(crops_text, (50, 100))
        
        farms_text = self.font.render(f"农场: {self.farms}", True, BLACK)
        screen.blit(farms_text, (50, 130))
        
        farmers_text = self.font.render(f"农夫: {self.farmers}", True, BLACK)
        screen.blit(farmers_text, (50, 160))
        
        buy_farm_text = self.font.render(f"购买农场 (100金币)", True, BLACK)
        pygame.draw.rect(screen, (100, 150, 255), (50, 200, 200, 40))
        screen.blit(buy_farm_text, (60, 210))
        
        buy_farmer_text = self.font.render(f"雇佣农夫 (50金币)", True, BLACK)
        pygame.draw.rect(screen, (100, 150, 255), (50, 260, 200, 40))
        screen.blit(buy_farmer_text, (60, 270))
        
        sell_crops_text = self.font.render(f"出售作物 (1金币/个)", True, BLACK)
        pygame.draw.rect(screen, (255, 150, 100), (50, 320, 200, 40))
        screen.blit(sell_crops_text, (60, 330))

    def handle_click(self, pos):
        if 50 <= pos[0] <= 250 and 200 <= pos[1] <= 240:
            if self.money >= 100:
                self.money -= 100
                self.farms += 1
        elif 50 <= pos[0] <= 250 and 260 <= pos[1] <= 300:
            if self.money >= 50:
                self.money -= 50
                self.farmers += 1
        elif 50 <= pos[0] <= 250 and 320 <= pos[1] <= 360:
            self.money += int(self.crops)
            self.crops = 0

game = IdleFarm()
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