import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
TILE = 40
COLS = WIDTH // TILE
ROWS = HEIGHT // TILE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
LIGHT_BROWN = (210, 180, 140)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("农场模拟器")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

CROPS = {
    'wheat': {'grow_time': 180, 'color': (255, 215, 0), 'seed_cost': 5, 'sell_price': 15},
    'carrot': {'grow_time': 240, 'color': (255, 140, 0), 'seed_cost': 8, 'sell_price': 25},
    'tomato': {'grow_time': 300, 'color': (255, 99, 71), 'seed_cost': 10, 'sell_price': 35},
    'corn': {'grow_time': 360, 'color': (255, 255, 100), 'seed_cost': 12, 'sell_price': 45},
}

CROP_NAMES = list(CROPS.keys())

class FarmGame:
    def __init__(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.money = 100
        self.current_crop = 'wheat'
        self.day = 1
        self.message = ""
        self.msg_timer = 0
        
        # 初始化草地
        for y in range(ROWS):
            for x in range(COLS):
                self.grid[y][x] = {'type': 'grass'}
    
    def plant(self, mx, my):
        gx, gy = mx // TILE, my // TILE
        if 0 <= gx < COLS and 0 <= gy < ROWS:
            crop_info = CROPS[self.current_crop]
            if self.grid[gy][gx]['type'] == 'grass' and self.money >= crop_info['seed_cost']:
                self.money -= crop_info['seed_cost']
                self.grid[gy][gx] = {
                    'type': 'crop',
                    'crop': self.current_crop,
                    'growth': 0,
                    'max_growth': crop_info['grow_time']
                }
                self.message = f"种下了{self.current_crop}! (-{crop_info['seed_cost']}金币)"
                self.msg_timer = 90
    
    def harvest(self, mx, my):
        gx, gy = mx // TILE, my // TILE
        if 0 <= gx < COLS and 0 <= gy < ROWS:
            cell = self.grid[gy][gx]
            if cell['type'] == 'crop' and cell['growth'] >= cell['max_growth']:
                crop_info = CROPS[cell['crop']]
                self.money += crop_info['sell_price']
                self.grid[gy][gx] = {'type': 'grass'}
                self.message = f"收获了{cell['crop']}! (+{crop_info['sell_price']}金币)"
                self.msg_timer = 90
    
    def water(self, mx, my):
        gx, gy = mx // TILE, my // TILE
        if 0 <= gx < COLS and 0 <= gy < ROWS:
            cell = self.grid[gy][gx]
            if cell['type'] == 'crop' and cell['growth'] < cell['max_growth']:
                cell['growth'] = min(cell['max_growth'], cell['growth'] + 30)
                self.message = "浇水加速生长!"
                self.msg_timer = 60
    
    def update(self):
        for y in range(ROWS):
            for x in range(COLS):
                cell = self.grid[y][x]
                if cell['type'] == 'crop' and cell['growth'] < cell['max_growth']:
                    cell['growth'] += 1
    
    def draw(self):
        screen.fill((135, 206, 235))
        
        for y in range(ROWS):
            for x in range(COLS):
                cell = self.grid[y][x]
                sx, sy = x * TILE, y * TILE
                
                if cell['type'] == 'grass':
                    color = GREEN if (x + y) % 2 == 0 else DARK_GREEN
                    pygame.draw.rect(screen, color, (sx, sy, TILE, TILE))
                elif cell['type'] == 'crop':
                    pygame.draw.rect(screen, BROWN, (sx, sy, TILE, TILE))
                    crop_info = CROPS[cell['crop']]
                    ratio = cell['growth'] / cell['max_growth']
                    h = int(TILE * 0.8 * ratio)
                    if h > 0:
                        pygame.draw.rect(screen, crop_info['color'], 
                                       (sx + 8, sy + TILE - h - 2, TILE - 16, h))
                    if ratio >= 1.0:
                        pygame.draw.circle(screen, YELLOW, (sx + TILE // 2, sy + 5), 4)
                
                pygame.draw.rect(screen, (0, 0, 0, 50), (sx, sy, TILE, TILE), 1)
        
        # UI
        pygame.draw.rect(screen, (0, 0, 0), (0, HEIGHT - 60, WIDTH, 60))
        money_text = font.render(f"金币: {self.money}", True, YELLOW)
        day_text = font.render(f"天数: {self.day}", True, WHITE)
        crop_text = font.render(f"当前: {self.current_crop}", True, CROPS[self.current_crop]['color'])
        screen.blit(money_text, (10, HEIGHT - 55))
        screen.blit(day_text, (150, HEIGHT - 55))
        screen.blit(crop_text, (280, HEIGHT - 55))
        
        inst = font.render("左键种植 | 右键收获 | 中键浇水 | 1-4切换作物", True, WHITE)
        screen.blit(inst, (10, HEIGHT - 30))
        
        if self.msg_timer > 0:
            self.msg_timer -= 1
            msg = font.render(self.message, True, WHITE)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 10))

def farm_simulator():
    game = FarmGame()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.plant(*event.pos)
                elif event.button == 3:
                    game.harvest(*event.pos)
                elif event.button == 2:
                    game.water(*event.pos)
            elif event.type == pygame.KEYDOWN:
                for i, name in enumerate(CROP_NAMES):
                    if event.key == pygame.K_1 + i:
                        game.current_crop = name
        
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    farm_simulator()
