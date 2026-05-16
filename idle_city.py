import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("梦想城市")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 235)
GRAY = (150, 150, 150)
GREEN = (50, 200, 50)
YELLOW = (255, 200, 50)
PURPLE = (150, 50, 200)

buildings = [
    {"name": "住宅", "cost": 50, "income": 5, "workers": 0, "max_pop": 10, "color": (100, 150, 200)},
    {"name": "商店", "cost": 100, "income": 15, "workers": 3, "max_pop": 0, "color": (200, 150, 100)},
    {"name": "工厂", "cost": 200, "income": 30, "workers": 8, "max_pop": 0, "color": (180, 180, 180)},
    {"name": "公园", "cost": 80, "income": 0, "workers": 1, "max_pop": 0, "color": GREEN},
    {"name": "办公楼", "cost": 300, "income": 50, "workers": 15, "max_pop": 0, "color": (200, 200, 220)},
]

class CityGame:
    def __init__(self):
        self.money = 200
        self.population = 10
        self.city = [[None for _ in range(5)] for _ in range(5)]
        self.happiness = 75
        self.hour = 0
        self.selected_building = 0
        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 48)

    def update(self):
        total_income = 0
        total_workers_needed = 0
        total_pop = 0
        
        for row in self.city:
            for building in row:
                if building:
                    b = buildings[building["type"]]
                    total_income += b["income"]
                    total_workers_needed += b["workers"]
                    total_pop += b["max_pop"]
        
        workers = min(self.population, total_workers_needed)
        efficiency = workers / total_workers_needed if total_workers_needed > 0 else 1
        
        self.money += total_income * efficiency / 60
        self.happiness = max(20, min(100, 75 + len([b for row in self.city for b in row if b and b["type"] == 3]) * 5))
        self.hour = (self.hour + 0.01) % 24

    def draw(self):
        sky_color = BLUE if 6 < self.hour < 18 else (30, 30, 70)
        screen.fill(sky_color)
        
        pygame.draw.rect(screen, (80, 150, 80), (0, 380, 800, 220))
        
        for i in range(5):
            for j in range(5):
                x = 80 + j * 130
                y = 150 + i * 70
                building = self.city[i][j]
                if building:
                    b = buildings[building["type"]]
                    pygame.draw.rect(screen, b["color"], (x, y, 120, 65), border_radius=5)
                    pygame.draw.rect(screen, BLACK, (x, y, 120, 65), 2, border_radius=5)
                    name_text = self.font.render(b["name"], True, WHITE)
                    screen.blit(name_text, (x+15, y+20))
                else:
                    pygame.draw.rect(screen, (200, 240, 200), (x, y, 120, 65), border_radius=5)
                    pygame.draw.rect(screen, BLACK, (x, y, 120, 65), 2, border_radius=5)
                    hint = self.font.render("空地", True, (150, 150, 150))
                    screen.blit(hint, (x+35, y+20))
        
        pygame.draw.rect(screen, (240, 240, 240), (0, 0, 800, 100))
        pygame.draw.rect(screen, BLACK, (0, 0, 800, 100), 2)
        
        title_text = self.large_font.render("梦想城市", True, BLACK)
        screen.blit(title_text, (320, 30))
        
        money_text = self.font.render(f"资金: ¥{int(self.money)}", True, BLACK)
        screen.blit(money_text, (30, 35))
        
        pop_text = self.font.render(f"人口: {int(self.population)}", True, BLACK)
        screen.blit(pop_text, (200, 35))
        
        happy_text = self.font.render(f"幸福度: {int(self.happiness)}%", True, GREEN if self.happiness > 70 else YELLOW if self.happiness > 50 else RED)
        screen.blit(happy_text, (360, 35))
        
        time_text = self.font.render(f"时间: {int(self.hour)}:00", True, BLACK)
        screen.blit(time_text, (540, 35))
        
        pygame.draw.rect(screen, (240, 240, 240), (600, 110, 180, 450), border_radius=10)
        pygame.draw.rect(screen, BLACK, (600, 110, 180, 450), 2, border_radius=10)
        
        shop_title = self.font.render("建筑商店", True, BLACK)
        screen.blit(shop_title, (640, 125))
        
        for i, b in enumerate(buildings):
            button_y = 160 + i * 60
            color = (200, 220, 255) if self.money >= b["cost"] else (200, 200, 200)
            pygame.draw.rect(screen, color, (610, button_y, 160, 55), border_radius=3)
            pygame.draw.rect(screen, BLACK, (610, button_y, 160, 55), 2, border_radius=3)
            b_name = self.font.render(b["name"], True, BLACK)
            screen.blit(b_name, (620, button_y+5))
            b_cost = self.font.render(f"¥{b['cost']}", True, PURPLE)
            screen.blit(b_cost, (620, button_y+25))
        
        hint_text = self.font.render("点击商店选择建筑，再点击空地建造", True, BLUE)
        screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, 560))

    def handle_click(self, pos):
        for i in range(5):
            for j in range(5):
                x = 80 + j * 130
                y = 150 + i * 70
                if x <= pos[0] <= x+120 and y <= pos[1] <= y+65:
                    if self.city[i][j] is None:
                        b = buildings[self.selected_building]
                        if self.money >= b["cost"]:
                            self.money -= b["cost"]
                            self.city[i][j] = {"type": self.selected_building, "level": 1}
                            if b["max_pop"] > 0:
                                self.population += b["max_pop"]
        
        for i in range(len(buildings)):
            button_y = 160 + i * 60
            if 610 <= pos[0] <= 770 and button_y <= pos[1] <= button_y+55:
                self.selected_building = i

game = CityGame()
clock = pygame.time.Clock()
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
    clock.tick(60)

pygame.quit()
