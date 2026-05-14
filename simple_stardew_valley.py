import pygame
import sys
import random
import math
from enum import Enum

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)
YELLOW = (255, 215, 0)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
SKY_BLUE = (135, 206, 235)
ORANGE = (255, 165, 0)

class CropState(Enum):
    EMPTY = 0
    SEEDED = 1
    GROWING = 2
    READY = 3

class SoundGenerator:
    @staticmethod
    def generate_plant_sound():
        sample_rate = 44100
        duration = 0.1
        num_samples = int(sample_rate * duration)
        sound_array = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            value = int(32767 * math.sin(2 * math.pi * 800 * t) * math.exp(-3 * t))
            sound_array.extend(value.to_bytes(2, byteorder='little', signed=True))
        return pygame.mixer.Sound(buffer=sound_array)
    
    @staticmethod
    def generate_water_sound():
        sample_rate = 44100
        duration = 0.2
        num_samples = int(sample_rate * duration)
        sound_array = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            value = int(32767 * (random.random() * 2 - 1) * math.exp(-5 * t))
            sound_array.extend(value.to_bytes(2, byteorder='little', signed=True))
        return pygame.mixer.Sound(buffer=sound_array)
    
    @staticmethod
    def generate_harvest_sound():
        sample_rate = 44100
        duration = 0.15
        num_samples = int(sample_rate * duration)
        sound_array = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            value = int(32767 * math.sin(2 * math.pi * 1200 * t) * math.exp(-4 * t))
            sound_array.extend(value.to_bytes(2, byteorder='little', signed=True))
        return pygame.mixer.Sound(buffer=sound_array)
    
    @staticmethod
    def generate_coin_sound():
        sample_rate = 44100
        duration = 0.2
        num_samples = int(sample_rate * duration)
        sound_array = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            value = int(32767 * (math.sin(2 * math.pi * 1500 * t) + math.sin(2 * math.pi * 2000 * t)) * math.exp(-3 * t))
            sound_array.extend(value.to_bytes(2, byteorder='little', signed=True))
        return pygame.mixer.Sound(buffer=sound_array)

class Crop:
    def __init__(self):
        self.state = CropState.EMPTY
        self.watered = False
        self.growth_stage = 0
        self.max_growth = 3
        self.type = None

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("简易星露谷 - 像素农场")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 36)

        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_speed = 3

        self.money = 100
        self.day = 1
        self.hour = 6
        self.minute = 0
        self.time_speed = 0.5

        self.grid_size = 8
        self.grid_offset_x = (SCREEN_WIDTH - self.grid_size * TILE_SIZE) // 2
        self.grid_offset_y = 150
        self.farm_grid = [[Crop() for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        self.selected_seed = 0
        self.seed_types = ["萝卜", "白菜", "土豆"]
        self.seed_prices = [10, 20, 15]
        self.sell_prices = [30, 50, 40]

        self.sounds = {
            'plant': SoundGenerator.generate_plant_sound(),
            'water': SoundGenerator.generate_water_sound(),
            'harvest': SoundGenerator.generate_harvest_sound(),
            'coin': SoundGenerator.generate_coin_sound()
        }

        self.inventory = {crop: 0 for crop in self.seed_types}

    def draw_sky(self):
        hour_total = self.hour + self.minute / 60
        
        if 6 <= hour_total < 8:
            ratio = (hour_total - 6) / 2
            r = int(255 * (1 - ratio) + 135 * ratio)
            g = int(140 * (1 - ratio) + 206 * ratio)
            b = int(200 * (1 - ratio) + 235 * ratio)
        elif 8 <= hour_total < 18:
            r, g, b = 135, 206, 235
        elif 18 <= hour_total < 20:
            ratio = (hour_total - 18) / 2
            r = int(135 * (1 - ratio) + 50 * ratio)
            g = int(206 * (1 - ratio) + 30 * ratio)
            b = int(235 * (1 - ratio) + 80 * ratio)
        else:
            r, g, b = 50, 30, 80
        
        self.screen.fill((r, g, b))

    def draw_player(self):
        pygame.draw.rect(self.screen, BLUE, (self.player_x - 12, self.player_y - 16, 24, 32))
        pygame.draw.rect(self.screen, (255, 220, 180), (self.player_x - 8, self.player_y - 24, 16, 16))
        pygame.draw.circle(self.screen, BLACK, (self.player_x - 4, self.player_y - 18), 2)
        pygame.draw.circle(self.screen, BLACK, (self.player_x + 4, self.player_y - 18), 2)

    def draw_farm(self):
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                tile_x = self.grid_offset_x + x * TILE_SIZE
                tile_y = self.grid_offset_y + y * TILE_SIZE
                crop = self.farm_grid[y][x]

                pygame.draw.rect(self.screen, DARK_BROWN, (tile_x, tile_y, TILE_SIZE - 1, TILE_SIZE - 1))
                
                if crop.state != CropState.EMPTY:
                    if crop.watered:
                        pygame.draw.rect(self.screen, (60, 40, 20), (tile_x + 2, tile_y + 2, TILE_SIZE - 5, TILE_SIZE - 5))
                
                if crop.state == CropState.SEEDED:
                    pygame.draw.circle(self.screen, (50, 50, 50), (tile_x + TILE_SIZE // 2, tile_y + TILE_SIZE // 2), 3)
                elif crop.state == CropState.GROWING:
                    height = 8 + crop.growth_stage * 6
                    color = GREEN if crop.growth_stage < 2 else LIGHT_GREEN
                    pygame.draw.rect(self.screen, color, (tile_x + TILE_SIZE // 2 - 4, tile_y + TILE_SIZE - height - 4, 8, height))
                elif crop.state == CropState.READY:
                    pygame.draw.rect(self.screen, LIGHT_GREEN, (tile_x + TILE_SIZE // 2 - 4, tile_y + 8, 8, 20))
                    if crop.type == "萝卜":
                        pygame.draw.circle(self.screen, RED, (tile_x + TILE_SIZE // 2, tile_y + 12), 8)
                    elif crop.type == "白菜":
                        pygame.draw.circle(self.screen, LIGHT_GREEN, (tile_x + TILE_SIZE // 2, tile_y + 12), 10)
                    elif crop.type == "土豆":
                        pygame.draw.circle(self.screen, YELLOW, (tile_x + TILE_SIZE // 2, tile_y + 12), 7)

    def draw_ui(self):
        pygame.draw.rect(self.screen, (0, 0, 0, 180), (0, 0, SCREEN_WIDTH, 100))
        pygame.draw.rect(self.screen, (0, 0, 0, 180), (0, SCREEN_HEIGHT - 80, SCREEN_WIDTH, 80))

        time_text = f"第 {self.day} 天  {self.hour:02d}:{self.minute:02d}"
        time_surf = self.font.render(time_text, True, WHITE)
        self.screen.blit(time_surf, (20, 20))

        money_text = f"金币: {self.money}"
        money_surf = self.font.render(money_text, True, YELLOW)
        self.screen.blit(money_surf, (200, 20))

        seed_text = f"当前种子: {self.seed_types[self.selected_seed]} (价格: {self.seed_prices[self.selected_seed]})"
        seed_surf = self.font.render(seed_text, True, WHITE)
        self.screen.blit(seed_surf, (20, 50))

        hint_text1 = "WASD/方向键移动  |  空格交互  |  Q/E切换种子"
        hint_text2 = "1-3买种子  |  点击商店图标卖菜"
        hint_surf1 = self.font.render(hint_text1, True, WHITE)
        hint_surf2 = self.font.render(hint_text2, True, WHITE)
        self.screen.blit(hint_surf1, (20, SCREEN_HEIGHT - 60))
        self.screen.blit(hint_surf2, (20, SCREEN_HEIGHT - 35))

        inv_x = 400
        inv_y = 20
        for i, crop in enumerate(self.seed_types):
            inv_text = f"{crop}: {self.inventory[crop]}"
            inv_surf = self.font.render(inv_text, True, WHITE)
            self.screen.blit(inv_surf, (inv_x, inv_y + i * 20))

        shop_rect = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 60)
        pygame.draw.rect(self.screen, ORANGE, shop_rect)
        shop_text = self.font.render("商店", True, BLACK)
        self.screen.blit(shop_text, (shop_rect.centerx - 20, shop_rect.centery - 8))
        self.shop_rect = shop_rect

    def update_time(self):
        self.minute += self.time_speed
        if self.minute >= 60:
            self.minute = 0
            self.hour += 1
            if self.hour >= 24:
                self.hour = 0
                self.day += 1
                self.new_day()

    def new_day(self):
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                crop = self.farm_grid[y][x]
                crop.watered = False
                if crop.state == CropState.GROWING and crop.growth_stage < crop.max_growth:
                    crop.growth_stage += 1
                    if crop.growth_stage >= crop.max_growth:
                        crop.state = CropState.READY

    def get_grid_pos(self):
        grid_x = int((self.player_x - self.grid_offset_x) // TILE_SIZE)
        grid_y = int((self.player_y - self.grid_offset_y) // TILE_SIZE)
        return grid_x, grid_y

    def interact(self):
        grid_x, grid_y = self.get_grid_pos()
        if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
            crop = self.farm_grid[grid_y][grid_x]
            
            if crop.state == CropState.EMPTY:
                if self.money >= self.seed_prices[self.selected_seed]:
                    self.money -= self.seed_prices[self.selected_seed]
                    crop.type = self.seed_types[self.selected_seed]
                    crop.state = CropState.SEEDED
                    crop.growth_stage = 0
                    crop.watered = False
                    self.sounds['plant'].play()
            elif crop.state == CropState.SEEDED or crop.state == CropState.GROWING:
                if not crop.watered:
                    crop.watered = True
                    if crop.state == CropState.SEEDED:
                        crop.state = CropState.GROWING
                    self.sounds['water'].play()
            elif crop.state == CropState.READY:
                self.inventory[crop.type] += 1
                crop.state = CropState.EMPTY
                crop.type = None
                crop.watered = False
                crop.growth_stage = 0
                self.sounds['harvest'].play()

    def sell_crops(self):
        total = 0
        for i, crop in enumerate(self.seed_types):
            if self.inventory[crop] > 0:
                total += self.inventory[crop] * self.sell_prices[i]
                self.inventory[crop] = 0
        if total > 0:
            self.money += total
            self.sounds['coin'].play()
            return total
        return 0

    def buy_seed(self, index):
        if self.money >= self.seed_prices[index]:
            self.money -= self.seed_prices[index]
            self.inventory[self.seed_types[index]] += 1
            self.sounds['coin'].play()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.player_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.player_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.player_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.player_speed

        self.player_x = max(20, min(SCREEN_WIDTH - 20, self.player_x + dx))
        self.player_y = max(120, min(SCREEN_HEIGHT - 100, self.player_y + dy))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    self.interact()
                elif event.key == pygame.K_q:
                    self.selected_seed = (self.selected_seed - 1) % len(self.seed_types)
                elif event.key == pygame.K_e:
                    self.selected_seed = (self.selected_seed + 1) % len(self.seed_types)
                elif event.key == pygame.K_1:
                    self.buy_seed(0)
                elif event.key == pygame.K_2:
                    self.buy_seed(1)
                elif event.key == pygame.K_3:
                    self.buy_seed(2)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if hasattr(self, 'shop_rect') and self.shop_rect.collidepoint(event.pos):
                        earned = self.sell_crops()
                        if earned > 0:
                            print(f"卖出作物获得 {earned} 金币!")

    def run(self):
        while True:
            self.handle_input()
            self.update_time()
            
            self.draw_sky()
            self.draw_farm()
            self.draw_player()
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
