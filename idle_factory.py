import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("生产线帝国")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 255)
ORANGE = (255, 150, 50)
GRAY = (100, 100, 100)
RED = (200, 50, 50)
GREEN = (50, 200, 50)

products = [
    {"name": "零件", "price": 5, "cost": 3, "time": 2, "color": GRAY},
    {"name": "工具", "price": 15, "cost": 10, "time": 4, "color": ORANGE},
    {"name": "玩具", "price": 30, "cost": 20, "time": 6, "color": RED},
    {"name": "汽车", "price": 100, "cost": 70, "time": 12, "color": BLUE},
    {"name": "计算机", "price": 200, "cost": 150, "time": 20, "color": GREEN},
]

class FactoryGame:
    def __init__(self):
        self.money = 100
        self.machines = []
        self.storage = {}
        self.upgrades = {"speed": 1, "quality": 1}
        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 48)
        self.selected_product = 0

    def update(self):
        for machine in self.machines:
            machine["time_left"] -= 0.016
            if machine["time_left"] <= 0:
                product_name = machine["product"]["name"]
                if product_name in self.storage:
                    self.storage[product_name] += 1
                else:
                    self.storage[product_name] = 1
                self.money += machine["product"]["price"] * (1 + 0.1 * self.upgrades["quality"])
                machine["time_left"] = machine["product"]["time"] / self.upgrades["speed"]

    def draw(self):
        screen.fill((220, 220, 255))
        
        pygame.draw.rect(screen, (150, 180, 220), (0, 0, 800, 80))
        title_text = self.large_font.render("生产线帝国", True, BLACK)
        screen.blit(title_text, (280, 20))
        
        money_text = self.font.render(f"资金: ¥{int(self.money)}", True, BLACK)
        screen.blit(money_text, (30, 90))
        
        storage_y = 130
        storage_text = self.font.render("仓库:", True, BLACK)
        screen.blit(storage_text, (30, storage_y))
        storage_y += 30
        for product, count in self.storage.items():
            text = self.font.render(f"{product}: {count}", True, (80, 80, 80))
            screen.blit(text, (40, storage_y))
            storage_y += 25
        
        for i, machine in enumerate(self.machines):
            x = 100 + (i % 4) * 150
            y = 200 + (i // 4) * 120
            pygame.draw.rect(screen, machine["product"]["color"], (x, y, 130, 100), border_radius=5)
            pygame.draw.rect(screen, BLACK, (x, y, 130, 100), 2, border_radius=5)
            
            name = self.font.render(machine["product"]["name"], True, WHITE)
            screen.blit(name, (x+10, y+10))
            
            progress = max(0, 100 - (machine["time_left"] / (machine["product"]["time"]/self.upgrades["speed"]) * 100))
            pygame.draw.rect(screen, (200, 200, 200), (x+10, y+50, 110, 15))
            pygame.draw.rect(screen, GREEN, (x+10, y+50, 110 * progress / 100, 15))
            
            income_text = self.font.render(f"¥{int(machine['product']['price'])}/次", True, WHITE)
            screen.blit(income_text, (x+20, y+70))
        
        pygame.draw.rect(screen, (240, 240, 240), (550, 150, 230, 400), border_radius=10)
        pygame.draw.rect(screen, BLACK, (550, 150, 230, 400), 2, border_radius=10)
        
        shop_title = self.font.render("机器商店", True, BLACK)
        screen.blit(shop_title, (610, 165))
        
        for i, product in enumerate(products):
            cost = product["cost"] + len(self.machines) * 10
            button_y = 200 + i * 45
            color = (200, 220, 255) if self.money >= cost else (200, 200, 200)
            pygame.draw.rect(screen, color, (560, button_y, 210, 40), border_radius=3)
            pygame.draw.rect(screen, BLACK, (560, button_y, 210, 40), 2, border_radius=3)
            product_name = self.font.render(f"{product['name']}", True, BLACK)
            screen.blit(product_name, (570, button_y+5))
            price_text = self.font.render(f"¥{int(cost)}", True, (100, 100, 100))
            screen.blit(price_text, (670, button_y+5))
        
        upgrade_speed_cost = 100 * self.upgrades["speed"]
        upgrade_quality_cost = 150 * self.upgrades["quality"]
        
        speed_btn_y = 430
        speed_color = (200, 255, 200) if self.money >= upgrade_speed_cost else (200, 200, 200)
        pygame.draw.rect(screen, speed_color, (560, speed_btn_y, 210, 35), border_radius=3)
        pygame.draw.rect(screen, BLACK, (560, speed_btn_y, 210, 35), 2, border_radius=3)
        speed_text = self.font.render(f"速度 Lv{self.upgrades['speed']} ¥{upgrade_speed_cost}", True, BLACK)
        screen.blit(speed_text, (570, speed_btn_y+3))
        
        quality_btn_y = 475
        quality_color = (200, 255, 200) if self.money >= upgrade_quality_cost else (200, 200, 200)
        pygame.draw.rect(screen, quality_color, (560, quality_btn_y, 210, 35), border_radius=3)
        pygame.draw.rect(screen, BLACK, (560, quality_btn_y, 210, 35), 2, border_radius=3)
        quality_text = self.font.render(f"质量 Lv{self.upgrades['quality']} ¥{upgrade_quality_cost}", True, BLACK)
        screen.blit(quality_text, (570, quality_btn_y+3))
        
        hint_text = self.font.render("点击商店购买机器或升级，右键移除机器", True, BLUE)
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, 550))

    def handle_click(self, pos, button):
        if button == 1:
            for i, product in enumerate(products):
                cost = product["cost"] + len(self.machines) * 10
                if 560 <= pos[0] <= 770 and 200 + i*45 <= pos[1] <= 240 + i*45:
                    if len(self.machines) < 12 and self.money >= cost:
                        self.money -= cost
                        self.machines.append({
                            "product": product,
                            "time_left": product["time"] / self.upgrades["speed"],
                        })
                    return
            
            speed_cost = 100 * self.upgrades["speed"]
            if 560 <= pos[0] <= 770 and 430 <= pos[1] <= 465:
                if self.money >= speed_cost:
                    self.money -= speed_cost
                    self.upgrades["speed"] += 1
            
            quality_cost = 150 * self.upgrades["quality"]
            if 560 <= pos[0] <= 770 and 475 <= pos[1] <= 510:
                if self.money >= quality_cost:
                    self.money -= quality_cost
                    self.upgrades["quality"] += 1
        
        elif button == 3:
            for i in range(len(self.machines)):
                x = 100 + (i % 4) * 150
                y = 200 + (i // 4) * 120
                if x <= pos[0] <= x+130 and y <= pos[1] <= y+100:
                    refund = int(self.machines[i]["product"]["cost"] * 0.5)
                    self.money += refund
                    del self.machines[i]
                    break

game = FactoryGame()
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            game.handle_click(pygame.mouse.get_pos(), event.button)
    
    game.update()
    game.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
