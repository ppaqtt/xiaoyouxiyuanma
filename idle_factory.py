import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("放置工厂")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (50, 100, 200)
ORANGE = (255, 150, 50)

class IdleFactory:
    def __init__(self):
        self.money = 100
        self.machines = 1
        self.workers = 0
        self.products = 0
        self.font = pygame.font.Font(None, 32)
        self.clock = pygame.time.Clock()
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= 1000:
            self.products += self.machines * (1 + self.workers * 0.3)
            self.last_update = now

    def draw(self):
        screen.fill(GRAY)
        
        for i in range(self.machines):
            x = 100 + i * 120
            pygame.draw.rect(screen, BLUE, (x, 350, 80, 80))
            pygame.draw.rect(screen, ORANGE, (x + 20, 370, 40, 40))
        
        title_text = self.font.render("放置工厂", True, BLACK)
        screen.blit(title_text, (350, 20))
        
        money_text = self.font.render(f"资金: {int(self.money)}", True, BLACK)
        screen.blit(money_text, (50, 70))
        
        products_text = self.font.render(f"产品: {int(self.products)}", True, BLACK)
        screen.blit(products_text, (50, 100))
        
        machines_text = self.font.render(f"机器: {self.machines}", True, BLACK)
        screen.blit(machines_text, (50, 130))
        
        workers_text = self.font.render(f"工人: {self.workers}", True, BLACK)
        screen.blit(workers_text, (50, 160))
        
        buy_machine_text = self.font.render(f"购买机器 (150资金)", True, BLACK)
        pygame.draw.rect(screen, (100, 200, 100), (50, 200, 220, 40))
        screen.blit(buy_machine_text, (60, 210))
        
        hire_worker_text = self.font.render(f"雇佣工人 (80资金)", True, BLACK)
        pygame.draw.rect(screen, (100, 200, 100), (50, 260, 220, 40))
        screen.blit(hire_worker_text, (60, 270))
        
        sell_product_text = self.font.render(f"出售产品 (2资金/个)", True, BLACK)
        pygame.draw.rect(screen, (255, 100, 100), (50, 320, 220, 40))
        screen.blit(sell_product_text, (60, 330))

    def handle_click(self, pos):
        if 50 <= pos[0] <= 270 and 200 <= pos[1] <= 240:
            if self.money >= 150:
                self.money -= 150
                self.machines += 1
        elif 50 <= pos[0] <= 270 and 260 <= pos[1] <= 300:
            if self.money >= 80:
                self.money -= 80
                self.workers += 1
        elif 50 <= pos[0] <= 270 and 320 <= pos[1] <= 360:
            self.money += int(self.products) * 2
            self.products = 0

game = IdleFactory()
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