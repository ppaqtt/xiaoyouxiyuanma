#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动物园模拟器 - 模拟经营游戏
管理动物园,照顾动物
"""

import pygame
import random

pygame.init()

WIDTH, HEIGHT = 1000, 700

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 100)
RED = (255, 50, 50)
BLUE = (0, 100, 200)
YELLOW = (255, 200, 0)
GRAY = (200, 200, 200)
PURPLE = (150, 50, 200)
ORANGE = (255, 150, 0)
PINK = (255, 150, 200)
BROWN = (139, 69, 19)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("动物园模拟器 - 模拟经营")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 50)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

ANIMALS = [
    ("狮子", "🦁", 500, 20, 3),
    ("大象", "🐘", 800, 30, 4),
    ("熊猫", "🐼", 600, 25, 3),
    ("长颈鹿", "🦒", 450, 15, 2),
    ("企鹅", "🐧", 300, 10, 1),
    ("猴子", "🐵", 250, 8, 1),
    ("老虎", "🐯", 550, 22, 3),
    ("斑马", "🦓", 400, 12, 2),
]

class Animal:
    def __init__(self, animal_type):
        self.name = animal_type[0]
        self.emoji = animal_type[1]
        self.price = animal_type[2]
        self.happiness = 80
        self.hunger = 0
        self.cleanliness = 100
        self.health = 100
        self.age = random.randint(1, 10)
        self.visitors_attracted = self.price // 100
        self.x = 0
        self.y = 0

class ZooGame:
    def __init__(self):
        self.money = 10000
        self.day = 1
        self.reputation = 50
        self.animals = []
        self.visitors = 0
        self.ticket_price = 20
        self.food_stock = 100
        self.total_visitors = 0
        self.game_over = False
        self.enclosures = []
        
        for i in range(6):
            self.enclosures.append({
                "x": 250 + (i % 3) * 220,
                "y": 150 + (i // 3) * 250,
                "occupied": False,
                "animal": None
            })
    
    def buy_animal(self, idx):
        if idx < len(ANIMALS):
            animal_type = ANIMALS[idx]
            for enclosure in self.enclosures:
                if not enclosure["occupied"]:
                    if self.money >= animal_type[2]:
                        self.money -= animal_type[2]
                        animal = Animal(animal_type)
                        enclosure["occupied"] = True
                        enclosure["animal"] = animal
                        animal.x = enclosure["x"] + 60
                        animal.y = enclosure["y"] + 60
                        return True
        return False
    
    def feed_animals(self):
        if self.food_stock >= len(self.animals):
            self.food_stock -= len(self.animals)
            for enclosure in self.enclosures:
                if enclosure["animal"]:
                    enclosure["animal"].hunger = 0
                    enclosure["animal"].happiness += 10
        else:
            for enclosure in self.enclosures:
                if enclosure["animal"]:
                    enclosure["animal"].hunger += 10
                    enclosure["animal"].happiness -= 5
    
    def clean_enclosures(self):
        cost = 50
        if self.money >= cost:
            self.money -= cost
            for enclosure in self.enclosures:
                if enclosure["animal"]:
                    enclosure["animal"].cleanliness = 100
                    enclosure["animal"].happiness += 5
    
    def update(self):
        if self.money < -500:
            self.game_over = True
        
        visitors_today = 0
        for enclosure in self.enclosures:
            if enclosure["animal"]:
                animal = enclosure["animal"]
                
                animal.hunger += 1
                animal.cleanliness -= 1
                animal.happiness -= 1
                
                if animal.hunger > 50:
                    animal.happiness -= 2
                if animal.cleanliness < 30:
                    animal.happiness -= 3
                
                animal.happiness = max(0, min(100, animal.happiness))
                
                if animal.happiness > 70:
                    visitors_today += animal.visitors_attracted
                elif animal.happiness > 40:
                    visitors_today += animal.visitors_attracted // 2
        
        self.visitors = visitors_today
        self.money += self.visitors * self.ticket_price
        self.total_visitors += self.visitors
        
        self.reputation = min(100, self.reputation + 1)
        
        self.day += 1
        if self.day % 10 == 0:
            self.food_stock += 50

def zoo_sim():
    game = ZooGame()
    
    game.buy_animal(4)
    game.buy_animal(5)
    
    while not game.game_over:
        screen.fill((144, 238, 144))
        
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 80))
        
        title = font_large.render(f"动物园模拟器 - 第{game.day}天", True, BROWN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
        
        pygame.draw.rect(screen, (50, 50, 70), (0, 90, 220, HEIGHT - 90))
        
        info = [
            f"资金: {game.money}元",
            f"声望: {game.reputation}",
            f"今日游客: {game.visitors}人",
            f"总收入游客: {game.total_visitors}",
            f"食物库存: {game.food_stock}",
            f"票价: {game.ticket_price}元"
        ]
        
        for i, text in enumerate(info):
            t = font_small.render(text, True, WHITE)
            screen.blit(t, (10, 100 + i * 35))
        
        shop_title = font_small.render("购买动物:", True, YELLOW)
        screen.blit(shop_title, (10, 340))
        
        for i, animal in enumerate(ANIMALS):
            text = f"{i+1}. {animal[0]}: {animal[2]}元"
            t = font_small.render(text, True, GREEN if game.money >= animal[2] else RED)
            screen.blit(t, (10, 370 + i * 25))
        
        pygame.draw.rect(screen, WHITE, (10, 620, 200, 50), 2)
        actions = [
            "F - 喂食",
            "C - 清扫",
            "空格 - 下一天"
        ]
        for i, action in enumerate(actions):
            a = font_small.render(action, True, WHITE)
            screen.blit(a, (15, 625 + i * 15))
        
        pygame.draw.rect(screen, BROWN, (230, 100, 720, 550), 5)
        
        for i, enclosure in enumerate(game.enclosures):
            pygame.draw.rect(screen, (200, 180, 150), 
                           (enclosure["x"], enclosure["y"], 200, 200))
            pygame.draw.rect(screen, BROWN, 
                           (enclosure["x"], enclosure["y"], 200, 200), 2)
            
            if enclosure["animal"]:
                animal = enclosure["animal"]
                
                emoji_size = 60
                emoji_surf = font_large.render(animal.emoji, True, BLACK)
                screen.blit(emoji_surf, (enclosure["x"] + 70, enclosure["y"] + 40))
                
                name_text = font_small.render(animal.name, True, BLACK)
                screen.blit(name_text, (enclosure["x"] + 60, enclosure["y"] + 110))
                
                happiness_color = GREEN if animal.happiness > 60 else YELLOW if animal.happiness > 30 else RED
                happiness_text = font_small.render(f"开心:{int(animal.happiness)}%", True, happiness_color)
                screen.blit(happiness_text, (enclosure["x"] + 30, enclosure["y"] + 140))
                
                hunger_color = GREEN if animal.hunger < 30 else YELLOW if animal.hunger < 60 else RED
                hunger_text = font_small.render(f"饥饿:{int(animal.hunger)}", True, hunger_color)
                screen.blit(hunger_text, (enclosure["x"] + 30, enclosure["y"] + 160))
                
                pygame.draw.rect(screen, RED, (enclosure["x"] + 30, enclosure["y"] + 180, 140, 10))
                pygame.draw.rect(screen, GREEN, 
                               (enclosure["x"] + 30, enclosure["y"] + 180, 
                                int(140 * animal.cleanliness / 100), 10))
                
                clean_text = font_small.render("清洁", True, BLUE)
                screen.blit(clean_text, (enclosure["x"] + 130, enclosure["y"] + 175))
            else:
                empty = font_small.render("空地", True, GRAY)
                screen.blit(empty, (enclosure["x"] + 70, enclosure["y"] + 90))
                
                hint = font_small.render("按对应数字购买", True, GRAY)
                screen.blit(hint, (enclosure["x"] + 30, enclosure["y"] + 120))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    game.feed_animals()
                elif event.key == pygame.K_c:
                    game.clean_enclosures()
                elif event.key == pygame.K_SPACE:
                    game.update()
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                                 pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8]:
                    idx = event.key - 49
                    game.buy_animal(idx)
    
    screen.fill(BLACK)
    result = font_large.render("游戏结束!", True, RED)
    screen.blit(result, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
    
    stats = [
        f"存活天数: {game.day}天",
        f"总收入游客: {game.total_visitors}人",
        f"最终资金: {game.money}元",
        f"最终声望: {game.reputation}"
    ]
    
    for i, text in enumerate(stats):
        t = font_medium.render(text, True, WHITE)
        screen.blit(t, (WIDTH // 2 - 100, HEIGHT // 2 + i * 40))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    zoo_sim()
