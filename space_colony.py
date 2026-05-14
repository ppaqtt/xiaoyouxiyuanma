import pygame
import random
import math
import sys

pygame.init()
try:
    pygame.mixer.init()
    sound_enabled = True
except:
    sound_enabled = False

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
GRID_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = (SCREEN_HEIGHT - 150) // GRID_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
BLUE = (50, 100, 200)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
YELLOW = (200, 200, 50)
PURPLE = (150, 50, 200)
CYAN = (50, 200, 200)
ORANGE = (255, 150, 50)
SPACE_BLUE = (10, 15, 30)
STAR_COLOR = (200, 200, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("太空殖民地建造者")
clock = pygame.time.Clock()

def generate_sound(frequency, duration, volume=0.3):
    if not sound_enabled:
        return None
    try:
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = bytearray()
        max_sample = 2**15 - 1
        for s in range(n_samples):
            t = s / sample_rate
            value = int(volume * max_sample * math.sin(2 * math.pi * frequency * t))
            buf.append(value & 0xff)
            buf.append((value >> 8) & 0xff)
        sound = pygame.mixer.Sound(buffer=buf)
        return sound
    except:
        return None

def play_sound(sound):
    if sound and sound_enabled:
        try:
            sound.play()
        except:
            pass

BUILD_SOUND = generate_sound(440, 0.1)
DESTROY_SOUND = generate_sound(220, 0.15)
CLICK_SOUND = generate_sound(660, 0.05)

RESOURCES = {
    'energy': 100,
    'minerals': 100,
    'food': 100,
    'population': 0
}

RESOURCE_COLORS = {
    'energy': YELLOW,
    'minerals': GRAY,
    'food': GREEN,
    'population': BLUE
}

RESOURCE_NAMES = {
    'energy': '能量',
    'minerals': '矿石',
    'food': '食物',
    'population': '人口'
}

BUILDINGS = {
    'power_station': {
        'name': '发电站',
        'cost': {'minerals': 50},
        'production': {'energy': 5},
        'consumption': {},
        'color': YELLOW,
        'description': '产生能量'
    },
    'mine': {
        'name': '矿场',
        'cost': {'energy': 30},
        'production': {'minerals': 3},
        'consumption': {'energy': 1},
        'color': GRAY,
        'description': '消耗能量，产出矿石'
    },
    'greenhouse': {
        'name': '温室',
        'cost': {'minerals': 40, 'energy': 20},
        'production': {'food': 4},
        'consumption': {'energy': 1},
        'color': GREEN,
        'description': '消耗能量，产出食物'
    },
    'house': {
        'name': '住宅',
        'cost': {'minerals': 60},
        'production': {'population': 2},
        'consumption': {'food': 1, 'energy': 1},
        'color': BLUE,
        'description': '消耗食物和能量，增加人口上限'
    }
}

grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
selected_building = None
build_mode = True

stars = []
for _ in range(200):
    stars.append((random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT - 150), random.uniform(0.3, 1.0)))

class Building:
    def __init__(self, type_, x, y):
        self.type = type_
        self.x = x
        self.y = y
        self.data = BUILDINGS[type_]
        self.animation_time = 0
    
    def update(self, dt):
        self.animation_time += dt
    
    def draw(self, surface):
        rect = pygame.Rect(self.x * GRID_SIZE, self.y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, self.data['color'], rect)
        pygame.draw.rect(surface, WHITE, rect, 2)
        
        cx = self.x * GRID_SIZE + GRID_SIZE // 2
        cy = self.y * GRID_SIZE + GRID_SIZE // 2
        
        if self.type == 'power_station':
            for i in range(3):
                offset = math.sin(self.animation_time * 5 + i) * 3
                pygame.draw.circle(surface, (255, 255, 200), (cx + offset, cy + offset), 4)
        elif self.type == 'mine':
            for i in range(3):
                y_offset = (self.animation_time * 20 + i * 10) % 30 - 15
                pygame.draw.rect(surface, (80, 80, 80), (cx - 5 + i * 5, cy - 10 + y_offset, 3, 10))
        elif self.type == 'greenhouse':
            for i in range(3):
                leaf_y = cy - 5 + math.sin(self.animation_time * 3 + i) * 2
                pygame.draw.ellipse(surface, (0, 150, 0), (cx - 8 + i * 8, leaf_y, 6, 10))
        elif self.type == 'house':
            pygame.draw.polygon(surface, (0, 0, 150), [(cx, cy - 15), (cx - 15, cy + 5), (cx + 15, cy + 5)])

def draw_stars(surface):
    for x, y, brightness in stars:
        color = (int(STAR_COLOR[0] * brightness), int(STAR_COLOR[1] * brightness), int(STAR_COLOR[2] * brightness))
        pygame.draw.circle(surface, color, (x, y), 1)

def draw_grid(surface):
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(surface, (30, 30, 50), (x, 0), (x, SCREEN_HEIGHT - 150))
    for y in range(0, SCREEN_HEIGHT - 150, GRID_SIZE):
        pygame.draw.line(surface, (30, 30, 50), (0, y), (SCREEN_WIDTH, y))

def draw_buildings(surface):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x]:
                grid[y][x].draw(surface)

def draw_ui(surface):
    ui_rect = pygame.Rect(0, SCREEN_HEIGHT - 150, SCREEN_WIDTH, 150)
    pygame.draw.rect(surface, DARK_GRAY, ui_rect)
    pygame.draw.line(surface, GRAY, (0, SCREEN_HEIGHT - 150), (SCREEN_WIDTH, SCREEN_HEIGHT - 150), 3)
    
    font = pygame.font.Font(None, 24)
    resource_x = 20
    resource_y = SCREEN_HEIGHT - 130
    for resource, value in RESOURCES.items():
        color = RESOURCE_COLORS[resource]
        name = RESOURCE_NAMES[resource]
        text = f"{name}: {int(value)}"
        text_surface = font.render(text, True, WHITE)
        pygame.draw.rect(surface, color, (resource_x - 5, resource_y - 2, 20, 20))
        pygame.draw.rect(surface, WHITE, (resource_x - 5, resource_y - 2, 20, 20), 2)
        surface.blit(text_surface, (resource_x + 25, resource_y))
        resource_y += 30
    
    building_x = 250
    building_y = SCREEN_HEIGHT - 140
    for type_, data in BUILDINGS.items():
        button_rect = pygame.Rect(building_x, building_y, 140, 60)
        pygame.draw.rect(surface, data['color'], button_rect)
        pygame.draw.rect(surface, WHITE, button_rect, 3)
        
        if selected_building == type_:
            pygame.draw.rect(surface, CYAN, button_rect, 5)
        
        name_surface = pygame.font.Font(None, 20).render(data['name'], True, BLACK)
        surface.blit(name_surface, (building_x + 10, building_y + 5))
        
        cost_y = building_y + 25
        for res, cost in data['cost'].items():
            cost_text = f"{RESOURCE_NAMES[res]}: {cost}"
            cost_surface = pygame.font.Font(None, 16).render(cost_text, True, BLACK)
            surface.blit(cost_surface, (building_x + 10, cost_y))
            cost_y += 15
        
        building_x += 160
    
    mode_text = "建造模式" if build_mode else "拆除模式"
    mode_surface = font.render(mode_text, True, GREEN if build_mode else RED)
    surface.blit(mode_surface, (950, SCREEN_HEIGHT - 130))
    
    instruction1 = font.render("点击选择建筑，再点击地图放置", True, LIGHT_GRAY)
    instruction2 = font.render("按 D 键切换拆除模式", True, LIGHT_GRAY)
    surface.blit(instruction1, (950, SCREEN_HEIGHT - 100))
    surface.blit(instruction2, (950, SCREEN_HEIGHT - 70))

def can_afford(cost):
    for resource, amount in cost.items():
        if RESOURCES[resource] < amount:
            return False
    return True

def place_building(x, y):
    if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
        return False
    if grid[y][x]:
        return False
    if not selected_building:
        return False
    if not can_afford(BUILDINGS[selected_building]['cost']):
        return False
    
    for resource, amount in BUILDINGS[selected_building]['cost'].items():
        RESOURCES[resource] -= amount
    
    grid[y][x] = Building(selected_building, x, y)
    play_sound(BUILD_SOUND)
    return True

def remove_building(x, y):
    if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
        return False
    if not grid[y][x]:
        return False
    
    building = grid[y][x]
    for resource, amount in BUILDINGS[building.type]['cost'].items():
        RESOURCES[resource] += amount // 2
    
    grid[y][x] = None
    play_sound(DESTROY_SOUND)
    return True

def update_resources(dt):
    production = {'energy': 0, 'minerals': 0, 'food': 0, 'population': 0}
    consumption = {'energy': 0, 'minerals': 0, 'food': 0, 'population': 0}
    
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x]:
                b = grid[y][x]
                for res, amount in b.data['production'].items():
                    production[res] += amount
                for res, amount in b.data['consumption'].items():
                    consumption[res] += amount
    
    for res in ['energy', 'minerals', 'food']:
        RESOURCES[res] += (production[res] - consumption[res]) * dt * 0.5
        RESOURCES[res] = max(0, RESOURCES[res])
    
    if RESOURCES['food'] > consumption['food'] + 5 and RESOURCES['energy'] > consumption['energy'] + 5:
        max_pop = production['population']
        if RESOURCES['population'] < max_pop:
            RESOURCES['population'] += dt * 0.1
    else:
        if RESOURCES['population'] > 0:
            RESOURCES['population'] -= dt * 0.05

def update_buildings(dt):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x]:
                grid[y][x].update(dt)

def main():
    global selected_building, build_mode
    running = True
    last_time = pygame.time.get_ticks()
    
    while running:
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_time) / 1000.0
        last_time = current_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                
                if y < SCREEN_HEIGHT - 150:
                    grid_x = x // GRID_SIZE
                    grid_y = y // GRID_SIZE
                    if build_mode:
                        place_building(grid_x, grid_y)
                    else:
                        remove_building(grid_x, grid_y)
                else:
                    building_x = 250
                    for type_ in BUILDINGS.keys():
                        button_rect = pygame.Rect(building_x, SCREEN_HEIGHT - 140, 140, 60)
                        if button_rect.collidepoint(x, y):
                            selected_building = type_
                            play_sound(CLICK_SOUND)
                            break
                        building_x += 160
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    build_mode = not build_mode
                    play_sound(CLICK_SOUND)
        
        update_resources(dt)
        update_buildings(dt)
        
        screen.fill(SPACE_BLUE)
        draw_stars(screen)
        draw_grid(screen)
        draw_buildings(screen)
        draw_ui(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
