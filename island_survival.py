import pygame
import os
import random
import math
import sys
import time

pygame.init()



# 尝试使用中文字体
def get_chinese_font(size):
    """获取支持中文的字体"""
    font_names = [
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
        "/System/Library/Fonts/PingFang.ttc",  # macOS
    ]
    for font_name in font_names:
        if os.path.exists(font_name):
            try:
                return pygame.font.Font(font_name, size)
            except:
                continue
    return get_chinese_font(size)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (135, 206, 235)
SAND = (244, 164, 96)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('荒岛求生')
clock = pygame.time.Clock()

def generate_sound(frequency=440, duration=0.1, volume=0.3):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = bytearray()
    for s in range(n_samples):
        t = s / sample_rate
        value = int(volume * 127 * math.sin(2 * math.pi * frequency * t))
        buf.append(value + 128)
    sound = pygame.mixer.Sound(bytes(buf))
    return sound

collect_sound = generate_sound(523, 0.15)
craft_sound = generate_sound(659, 0.2)
eat_sound = generate_sound(784, 0.1)

RESOURCES = {
    'wood': {'color': BROWN, 'name': '木材'},
    'stone': {'color': GRAY, 'name': '石头'},
    'food': {'color': RED, 'name': '食物'},
    'water': {'color': BLUE, 'name': '水'}
}

RECIPES = {
    'axe': {'name': '斧头', 'cost': {'wood': 3, 'stone': 2}, 'effect': '采集效率+50%'},
    'pickaxe': {'name': '镐子', 'cost': {'wood': 2, 'stone': 3}, 'effect': '采集石头效率+100%'},
    'shelter': {'name': '庇护所', 'cost': {'wood': 10, 'stone': 5}, 'effect': '夜晚降温减少'},
    'spear': {'name': '长矛', 'cost': {'wood': 5, 'stone': 2}, 'effect': '可以打猎'},
    'water_bottle': {'name': '水瓶', 'cost': {'stone': 3}, 'effect': '储水+50'}
}

class Resource:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.amount = random.randint(1, 3)
    
    def draw(self, surface, offset_x, offset_y):
        rect = pygame.Rect(self.x * TILE_SIZE - offset_x, self.y * TILE_SIZE - offset_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, RESOURCES[self.type]['color'], rect)
        pygame.draw.rect(surface, BLACK, rect, 1)

class Player:
    def __init__(self):
        self.x = GRID_WIDTH // 2
        self.y = GRID_HEIGHT // 2
        self.health = 100
        self.hunger = 100
        self.thirst = 100
        self.inventory = {'wood': 0, 'stone': 0, 'food': 5, 'water': 5}
        self.crafted = []
        self.speed = 1
    
    def move(self, dx, dy):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        if 0 <= new_x < GRID_WIDTH * 2 and 0 <= new_y < GRID_HEIGHT * 2:
            self.x = new_x
            self.y = new_y
    
    def update_stats(self):
        self.hunger -= 0.02
        self.thirst -= 0.03
        if self.hunger <= 0 or self.thirst <= 0:
            self.health -= 0.1
        if self.hunger > 0 and self.thirst > 0 and self.health < 100:
            self.health += 0.01
        self.hunger = max(0, min(100, self.hunger))
        self.thirst = max(0, min(100, self.thirst))
        self.health = max(0, min(100, self.health))
    
    def eat(self):
        if self.inventory['food'] > 0:
            self.inventory['food'] -= 1
            self.hunger = min(100, self.hunger + 30)
            eat_sound.play()
    
    def drink(self):
        if self.inventory['water'] > 0:
            self.inventory['water'] -= 1
            self.thirst = min(100, self.thirst + 30)
            eat_sound.play()
    
    def draw(self, surface, offset_x, offset_y):
        rect = pygame.Rect(self.x * TILE_SIZE - offset_x, self.y * TILE_SIZE - offset_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, YELLOW, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)

class Game:
    def __init__(self):
        self.player = Player()
        self.resources = []
        self.day_time = 0
        self.crafting_open = False
        self.generate_resources()
    
    def generate_resources(self):
        for _ in range(50):
            x = random.randint(0, GRID_WIDTH * 2 - 1)
            y = random.randint(0, GRID_HEIGHT * 2 - 1)
            type = random.choice(['wood', 'stone', 'food', 'water'])
            self.resources.append(Resource(x, y, type))
    
    def collect_resource(self):
        collect_amount = 1
        if 'axe' in self.player.crafted:
            collect_amount += 0.5
        if 'pickaxe' in self.player.crafted:
            collect_amount += 1
        
        for resource in self.resources[:]:
            if abs(resource.x - self.player.x) < 1.5 and abs(resource.y - self.player.y) < 1.5:
                self.player.inventory[resource.type] += int(collect_amount)
                self.resources.remove(resource)
                collect_sound.play()
                if random.random() < 0.3:
                    x = random.randint(0, GRID_WIDTH * 2 - 1)
                    y = random.randint(0, GRID_HEIGHT * 2 - 1)
                    type = random.choice(['wood', 'stone', 'food', 'water'])
                    self.resources.append(Resource(x, y, type))
                break
    
    def craft(self, item):
        recipe = RECIPES[item]
        can_craft = True
        for resource, amount in recipe['cost'].items():
            if self.player.inventory[resource] < amount:
                can_craft = False
                break
        
        if can_craft and item not in self.player.crafted:
            for resource, amount in recipe['cost'].items():
                self.player.inventory[resource] -= amount
            self.player.crafted.append(item)
            craft_sound.play()
    
    def update(self):
        self.player.update_stats()
        self.day_time = (self.day_time + 0.05) % 100
    
    def get_sky_color(self):
        if self.day_time < 25:
            return LIGHT_BLUE
        elif self.day_time < 50:
            r = int(135 - (self.day_time - 25) * 5)
            g = int(206 - (self.day_time - 25) * 4)
            b = int(235 - (self.day_time - 25) * 3)
            return (max(0, r), max(0, g), max(0, b))
        elif self.day_time < 75:
            return (10, 10, 30)
        else:
            r = int(10 + (self.day_time - 75) * 5)
            g = int(10 + (self.day_time - 75) * 7)
            b = int(30 + (self.day_time - 75) * 8)
            return (min(135, r), min(206, g), min(235, b))
    
    def draw(self):
        sky_color = self.get_sky_color()
        screen.fill(sky_color)
        
        offset_x = (self.player.x - GRID_WIDTH // 2) * TILE_SIZE
        offset_y = (self.player.y - GRID_HEIGHT // 2) * TILE_SIZE
        
        for x in range(-1, GRID_WIDTH + 2):
            for y in range(-1, GRID_HEIGHT + 2):
                world_x = x + int(offset_x // TILE_SIZE)
                world_y = y + int(offset_y // TILE_SIZE)
                dist_from_center = math.sqrt((world_x - GRID_WIDTH) ** 2 + (world_y - GRID_HEIGHT) ** 2)
                if dist_from_center < 15:
                    color = SAND if dist_from_center > 12 else GREEN
                else:
                    color = BLUE
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)
        
        for resource in self.resources:
            if (offset_x - TILE_SIZE <= resource.x * TILE_SIZE < offset_x + SCREEN_WIDTH + TILE_SIZE and
                offset_y - TILE_SIZE <= resource.y * TILE_SIZE < offset_y + SCREEN_HEIGHT + TILE_SIZE):
                resource.draw(screen, offset_x, offset_y)
        
        self.player.draw(screen, offset_x, offset_y)
        
        self.draw_ui()
        
        if self.crafting_open:
            self.draw_crafting_menu()
    
    def draw_ui(self):
        font = get_chinese_font(24)
        
        y_offset = 10
        stats = [
            ('生命值', self.player.health, RED),
            ('饥饿度', self.player.hunger, ORANGE),
            ('口渴度', self.player.thirst, BLUE)
        ]
        for name, value, color in stats:
            text = font.render(f'{name}: {int(value)}', True, BLACK)
            screen.blit(text, (10, y_offset))
            bar_rect = pygame.Rect(10, y_offset + 20, 150, 15)
            pygame.draw.rect(screen, GRAY, bar_rect)
            fill_rect = pygame.Rect(10, y_offset + 20, int(150 * value / 100), 15)
            pygame.draw.rect(screen, color, fill_rect)
            pygame.draw.rect(screen, BLACK, bar_rect, 1)
            y_offset += 45
        
        y_offset = 10
        for resource, amount in self.player.inventory.items():
            text = font.render(f'{RESOURCES[resource]["name"]}: {amount}', True, BLACK)
            screen.blit(text, (SCREEN_WIDTH - 150, y_offset))
            y_offset += 25
        
        if self.player.crafted:
            text = font.render('已制造:', True, BLACK)
            screen.blit(text, (SCREEN_WIDTH - 150, y_offset))
            y_offset += 25
            for item in self.player.crafted:
                text = font.render(f'- {RECIPES[item]["name"]}', True, BLACK)
                screen.blit(text, (SCREEN_WIDTH - 150, y_offset))
                y_offset += 20
        
        controls = [
            'WASD - 移动',
            'E - 收集资源',
            'C - 制造菜单',
            '1 - 吃食物',
            '2 - 喝水'
        ]
        for i, control in enumerate(controls):
            text = font.render(control, True, BLACK)
            screen.blit(text, (10, SCREEN_HEIGHT - 120 + i * 20))
    
    def draw_crafting_menu(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        font = get_chinese_font(36)
        title = font.render('制造菜单 (按C关闭)', True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        font = get_chinese_font(28)
        y_offset = 120
        for i, (item_key, recipe) in enumerate(RECIPES.items()):
            can_craft = True
            cost_text = []
            for resource, amount in recipe['cost'].items():
                has = self.player.inventory[resource] >= amount
                if not has:
                    can_craft = False
                cost_text.append(f'{RESOURCES[resource]["name"]}: {self.player.inventory[resource]}/{amount}')
            
            color = GREEN if can_craft and item_key not in self.player.crafted else RED
            if item_key in self.player.crafted:
                color = GRAY
            
            item_text = font.render(f'{i+1}. {recipe["name"]}', True, color)
            screen.blit(item_text, (100, y_offset))
            
            cost_str = ' | '.join(cost_text)
            cost_text_surf = font.render(cost_str, True, WHITE)
            screen.blit(cost_text_surf, (300, y_offset))
            
            effect_text = font.render(f'效果: {recipe["effect"]}', True, WHITE)
            screen.blit(effect_text, (550, y_offset))
            
            y_offset += 50

def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    game.crafting_open = not game.crafting_open
                elif event.key == pygame.K_e and not game.crafting_open:
                    game.collect_resource()
                elif event.key == pygame.K_1 and not game.crafting_open:
                    game.player.eat()
                elif event.key == pygame.K_2 and not game.crafting_open:
                    game.player.drink()
                elif game.crafting_open:
                    keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]
                    items = list(RECIPES.keys())
                    for i, key in enumerate(keys):
                        if event.key == key and i < len(items):
                            game.craft(items[i])
        
        if not game.crafting_open:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_w]:
                dy = -0.1
            if keys[pygame.K_s]:
                dy = 0.1
            if keys[pygame.K_a]:
                dx = -0.1
            if keys[pygame.K_d]:
                dx = 0.1
            game.player.move(dx, dy)
        
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(60)
        
        if game.player.health <= 0:
            game_over_font = get_chinese_font(72)
            game_over_text = game_over_font.render('游戏结束!', True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 36))
            pygame.display.flip()
            time.sleep(3)
            running = False
    
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()