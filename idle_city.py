import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("放置城市")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 235)
GRAY = (150, 150, 150)
GREEN = (50, 200, 50)
YELLOW = (255, 200, 50)

class IdleCity:
    def __init__(self):
        self.money = 500
        self.houses = 1
        self.shops = 0
        self.parks = 0
        self.population = 10
        self.font = pygame.font.Font(None, 32)
        self.clock = pygame.time.Clock()
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= 1000:
            self.money += self.population * 0.5 + self.shops * 10
            self.population = self.houses * 10 + self.parks * 5
            self.last_update = now

    def draw(self):
        screen.fill(BLUE)
        
        pygame.draw.rect(screen, GREEN, (0, 450, WIDTH, 150))
        
        for i in range(self.houses):
            x = 50 + (i % 8) * 80
            y = 350 - (i // 8) * 80
            pygame.draw.rect(screen, GRAY, (x, y, 60, 60))
            pygame.draw.polygon(screen, (100, 50, 50), [(x, y), (x+30, y-20), (x+60, y)])
        
        for i in range(self.shops):
            x = 600 + i * 60
            y = 400
            pygame.draw.rect(screen, YELLOW, (x, y, 40, 50))
            pygame.draw.circle(screen, BLACK, (x+20, y+25), 5)
        
        for i in range(self.parks):
            x = 100 + i * 150
            y = 500
            pygame.draw.circle(screen, GREEN, (x, y), 20)
        
        title_text = self.font.render("放置城市", True, BLACK)
        screen.blit(title_text, (350, 20))
        
        money_text = self.font.render(f"资金: {int(self.money)}", True, BLACK)
        screen.blit(money_text, (50, 70))
        
        pop_text = self.font.render(f"人口: {int(self.population)}", True, BLACK)
        screen.blit(pop_text, (50, 100))
        
        houses_text = self.font.render(f"住宅: {self.houses}", True, BLACK)
        screen.blit(houses_text, (50, 130))
        
        shops_text = self.font.render(f"商店: {self.shops}", True, BLACK)
        screen.blit(shops_text, (50, 160))
        
        parks_text = self.font.render(f"公园: {self.parks}", True, BLACK)
        screen.blit(parks_text, (50, 190))
        
        buy_house_text = self.font.render(f"建造住宅 (100资金)", True, BLACK)
        pygame.draw.rect(screen, (100, 150, 255), (50, 230, 200, 40))
        screen.blit(buy_house_text, (60, 240))
        
        buy_shop_text = self.font.render(f"建造商店 (200资金)", True, BLACK)
        pygame.draw.rect(screen, (100, 150, 255), (50, 290, 200, 40))
        screen.blit(buy_shop_text, (60, 300))
        
        buy_park_text = self.font.render(f"建造公园 (150资金)", True, BLACK)
        pygame.draw.rect(screen, (100, 150, 255), (50, 350, 200, 40))
        screen.blit(buy_park_text, (60, 360))

    def handle_click(self, pos):
        if 50 <= pos[0] <= 250 and 230 <= pos[1] <= 270:
            if self.money >= 100:
                self.money -= 100
                self.houses += 1
        elif 50 <= pos[0] <= 250 and 290 <= pos[1] <= 330:
            if self.money >= 200:
                self.money -= 200
                self.shops += 1
        elif 50 <= pos[0] <= 250 and 350 <= pos[1] <= 390:
            if self.money >= 150:
                self.money -= 150
                self.parks += 1

game = IdleCity()
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