import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
TILE_SIZE = 32

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
BLUE = (0, 100, 200)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
RED = (200, 0, 0)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (144, 238, 144)
WATER = (64, 164, 223)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("沙盒建造者")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

BLOCKS = {
    'grass': GREEN,
    'dirt': BROWN,
    'stone': GRAY,
    'wood': (160, 82, 45),
    'water': WATER,
    'sand': (238, 214, 175),
    'brick': (178, 34, 34),
    'snow': (240, 248, 255),
}

BLOCK_NAMES = list(BLOCKS.keys())

class SandboxWorld:
    def __init__(self):
        self.grid_x = WIDTH // TILE_SIZE
        self.grid_y = HEIGHT // TILE_SIZE
        self.world = [[None for _ in range(self.grid_x)] for _ in range(self.grid_y)]
        self.current_block = 'grass'
        self.camera_x = 0
        self.camera_y = 0
        self.generate_terrain()
    
    def generate_terrain(self):
        for y in range(self.grid_y):
            for x in range(self.grid_x):
                if y >= self.grid_y - 3:
                    self.world[y][x] = 'stone'
                elif y >= self.grid_y - 6:
                    self.world[y][x] = 'dirt'
                elif y >= self.grid_y - 7:
                    self.world[y][x] = 'grass'
    
    def place_block(self, mx, my):
        gx = (mx + self.camera_x) // TILE_SIZE
        gy = (my + self.camera_y) // TILE_SIZE
        if 0 <= gx < self.grid_x and 0 <= gy < self.grid_y:
            self.world[gy][gx] = self.current_block
    
    def remove_block(self, mx, my):
        gx = (mx + self.camera_x) // TILE_SIZE
        gy = (my + self.camera_y) // TILE_SIZE
        if 0 <= gx < self.grid_x and 0 <= gy < self.grid_y:
            self.world[gy][gx] = None
    
    def draw(self):
        screen.fill((135, 206, 235))
        for y in range(self.grid_y):
            for x in range(self.grid_x):
                block = self.world[y][x]
                if block:
                    sx = x * TILE_SIZE - self.camera_x
                    sy = y * TILE_SIZE - self.camera_y
                    pygame.draw.rect(screen, BLOCKS[block], (sx, sy, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(screen, BLACK, (sx, sy, TILE_SIZE, TILE_SIZE), 1)

def sandbox_builder():
    world = SandboxWorld()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    world.place_block(*event.pos)
                elif event.button == 3:
                    world.remove_block(*event.pos)
            elif event.type == pygame.MOUSEWHEEL:
                idx = BLOCK_NAMES.index(world.current_block)
                idx = (idx + event.y) % len(BLOCK_NAMES)
                world.current_block = BLOCK_NAMES[idx]
            elif event.type == pygame.KEYDOWN:
                for i, name in enumerate(BLOCK_NAMES):
                    if event.key == pygame.K_1 + i and i < 9:
                        world.current_block = name
                        break
                if event.key == pygame.K_c:
                    world = SandboxWorld()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            world.camera_x = max(0, world.camera_x - 5)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            world.camera_x = min(world.grid_x * TILE_SIZE - WIDTH, world.camera_x + 5)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            world.camera_y = max(0, world.camera_y - 5)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            world.camera_y = min(world.grid_y * TILE_SIZE - HEIGHT, world.camera_y + 5)
        
        world.draw()
        
        # UI面板
        pygame.draw.rect(screen, (0, 0, 0, 180), (0, 0, WIDTH, 50))
        for i, name in enumerate(BLOCK_NAMES):
            x = 10 + i * 55
            color = BLOCKS[name]
            pygame.draw.rect(screen, color, (x, 5, 40, 30))
            if name == world.current_block:
                pygame.draw.rect(screen, WHITE, (x, 5, 40, 30), 3)
            num_text = font.render(str(i + 1), True, WHITE)
            screen.blit(num_text, (x + 15, 8))
        
        current_text = font.render(f"当前: {world.current_block} | 左键放置 右键删除 滚轮切换 C重置", True, WHITE)
        screen.blit(current_text, (10, 35))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    sandbox_builder()
