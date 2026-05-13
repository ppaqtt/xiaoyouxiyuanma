import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 900, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("即时战略对战")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
big_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 22)

class Unit:
    def __init__(self, x, y, unit_type, team):
        self.x = x
        self.y = y
        self.unit_type = unit_type
        self.team = team
        self.hp = 50 if unit_type == 'worker' else 100 if unit_type == 'soldier' else 150
        self.max_hp = self.hp
        self.attack = 5 if unit_type == 'worker' else 15 if unit_type == 'soldier' else 25
        self.speed = 2 if unit_type == 'worker' else 1.5 if unit_type == 'soldier' else 1
        self.attack_range = 30
        self.attack_cooldown = 0
        self.selected = False
        self.target = None
        self.color = BLUE if team == 'player' else RED
    
    def move_to(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 5:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
    
    def attack_target(self, target):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            return
        
        dist = ((self.x - target.x)**2 + (self.y - target.y)**2)**0.5
        if dist < self.attack_range:
            target.hp -= self.attack
            self.attack_cooldown = 30
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 15)
        
        if self.selected:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), 18, 3)
        
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, RED, (int(self.x) - 15, int(self.y) - 25, 30, 5))
        pygame.draw.rect(screen, GREEN, (int(self.x) - 15, int(self.y) - 25, int(30 * hp_ratio), 5))

class Building:
    def __init__(self, x, y, building_type, team):
        self.x = x
        self.y = y
        self.type = building_type
        self.team = team
        self.hp = 200 if building_type == 'base' else 100 if building_type == 'barracks' else 50
        self.max_hp = self.hp
        self.color = BLUE if team == 'player' else RED
    
    def draw(self):
        size = 60 if self.type == 'base' else 40
        pygame.draw.rect(screen, self.color, 
                       (int(self.x - size // 2), int(self.y - size // 2), size, size))
        pygame.draw.rect(screen, WHITE, 
                       (int(self.x - size // 2), int(self.y - size // 2), size, size), 2)
        
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, RED, (int(self.x - 25), int(self.y - size // 2 - 10), 50, 5))
        pygame.draw.rect(screen, GREEN, (int(self.x - 25), int(self.y - size // 2 - 10), int(50 * hp_ratio), 5))

class RTSGame:
    def __init__(self):
        self.player_units = [
            Unit(100, 300, 'worker', 'player'),
            Unit(120, 320, 'worker', 'player'),
            Unit(80, 280, 'soldier', 'player'),
            Unit(100, 260, 'soldier', 'player'),
        ]
        self.player_buildings = [
            Building(100, 400, 'base', 'player'),
            Building(100, 480, 'barracks', 'player'),
        ]
        
        self.ai_units = [
            Unit(800, 300, 'worker', 'ai'),
            Unit(780, 320, 'worker', 'ai'),
            Unit(820, 280, 'soldier', 'ai'),
            Unit(800, 260, 'soldier', 'ai'),
        ]
        self.ai_buildings = [
            Building(800, 400, 'base', 'ai'),
            Building(800, 480, 'barracks', 'ai'),
        ]
        
        self.player_gold = 200
        self.ai_gold = 200
        
        self.selected_units = []
        self.ai_timer = 0

def rts_battle():
    game = RTSGame()
    game_over = False
    winner = None
    start_positions = {'player': (100, 300), 'ai': (800, 300)}
    
    while not game_over:
        screen.fill((50, 100, 50))
        
        for y in range(0, HEIGHT, 40):
            for x in range(0, WIDTH, 40):
                if (x + y) % 80 == 0:
                    pygame.draw.rect(screen, (40, 80, 40), (x, y, 40, 40))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if event.button == 1:
                    clicked = False
                    for unit in game.player_units:
                        if ((unit.x - mx)**2 + (unit.y - my)**2)**0.5 < 20:
                            unit.selected = True
                            if unit not in game.selected_units:
                                game.selected_units.append(unit)
                            clicked = True
                    
                    if not clicked:
                        for unit in game.selected_units:
                            unit.selected = False
                        game.selected_units = []
                        
                        for unit in game.player_units:
                            dist = ((unit.x - mx)**2 + (unit.y - my)**2)**0.5
                            if dist > 50:
                                for u in game.selected_units:
                                    u.target = (mx, my)
                
                elif event.button == 3:
                    mx, my = event.pos
                    for unit in game.selected_units:
                        unit.target = (mx, my)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    if game.player_gold >= 50:
                        spawn_pos = start_positions['player']
                        game.player_units.append(Unit(spawn_pos[0] + 30, spawn_pos[1], 'worker', 'player'))
                        game.player_gold -= 50
                elif event.key == pygame.K_2:
                    if game.player_gold >= 100:
                        spawn_pos = start_positions['player']
                        game.player_units.append(Unit(spawn_pos[0] + 30, spawn_pos[1], 'soldier', 'player'))
                        game.player_gold -= 100
        
        for unit in game.player_units:
            if unit.target:
                unit.move_to(unit.target[0], unit.target[1])
                if ((unit.x - unit.target[0])**2 + (unit.y - unit.target[1])**2)**0.5 < 10:
                    unit.target = None
            
            for enemy in game.ai_units:
                dist = ((unit.x - enemy.x)**2 + (unit.y - enemy.y)**2)**0.5
                if dist < unit.attack_range * 1.5:
                    unit.attack_target(enemy)
        
        for unit in game.ai_units:
            if unit.target:
                unit.move_to(unit.target[0], unit.target[1])
                if ((unit.x - unit.target[0])**2 + (unit.y - unit.target[1])**2)**0.5 < 10:
                    unit.target = None
            
            for enemy in game.player_units:
                dist = ((unit.x - enemy.x)**2 + (unit.y - enemy.y)**2)**0.5
                if dist < unit.attack_range * 1.5:
                    unit.attack_target(enemy)
        
        for building in game.player_buildings:
            for enemy in game.ai_units:
                dist = ((building.x - enemy.x)**2 + (building.y - enemy.y)**2)**0.5
                if dist < 50:
                    if building.attack_cooldown > 0:
                        building.attack_cooldown -= 1
                    else:
                        enemy.hp -= 10
                        building.attack_cooldown = 60
        
        for building in game.ai_buildings:
            for enemy in game.player_units:
                dist = ((building.x - enemy.x)**2 + (building.y - enemy.y)**2)**0.5
                if dist < 50:
                    if building.attack_cooldown > 0:
                        building.attack_cooldown -= 1
                    else:
                        enemy.hp -= 10
                        building.attack_cooldown = 60
        
        game.player_units = [u for u in game.player_units if u.hp > 0]
        game.ai_units = [u for u in game.ai_units if u.hp > 0]
        
        if not game.player_buildings or not any(u.team == 'player' for u in game.player_units):
            game_over = True
            winner = "AI"
        elif not game.ai_buildings or not any(u.team == 'ai' for u in game.ai_units):
            game_over = True
            winner = "玩家"
        
        game.ai_timer += 1
        if game.ai_timer > 120:
            game.ai_timer = 0
            game.ai_gold += 10
            
            if game.ai_gold >= 100 and len([u for u in game.ai_units if u.unit_type == 'soldier']) < 5:
                spawn_pos = start_positions['ai']
                game.ai_units.append(Unit(spawn_pos[0] - 30, spawn_pos[1], 'soldier', 'ai'))
                game.ai_gold -= 100
            
            target = random.choice(game.player_units) if game.player_units else None
            if target:
                for unit in game.ai_units[:3]:
                    unit.target = (target.x, target.y)
        
        for building in game.player_buildings:
            building.draw()
        for building in game.ai_buildings:
            building.draw()
        
        for unit in game.player_units:
            unit.draw()
        for unit in game.ai_units:
            unit.draw()
        
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 50))
        
        gold_text = font.render(f"金币: {game.player_gold}", True, YELLOW)
        screen.blit(gold_text, (10, 15))
        
        units_text = font.render(f"单位: {len(game.player_units)}", True, WHITE)
        screen.blit(units_text, (200, 15))
        
        inst = small_font.render("1.训练工人(50) | 2.训练士兵(100) | 左键选择 | 右键移动攻击", True, WHITE)
        screen.blit(inst, (WIDTH // 2 - 200, 15))
        
        pygame.display.flip()
        clock.tick(60)
    
    screen.fill(BLACK)
    result = big_font.render(f"{winner}获胜!", True, GREEN if winner == "玩家" else RED)
    screen.blit(result, (WIDTH // 2 - 100, HEIGHT // 2 - 30))
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    rts_battle()
