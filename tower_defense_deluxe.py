import pygame
import random

pygame.init()

WIDTH, HEIGHT = 900, 700

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
ORANGE = (255, 165, 0)
CYAN = (0, 200, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("塔防豪华版")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
big_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 22)

TOWERS = {
    'arrow': {'name': '箭塔', 'cost': 50, 'damage': 15, 'range': 120, 'color': BROWN, 'rate': 30, 'desc': '基础攻击'},
    'ice': {'name': '冰塔', 'cost': 80, 'damage': 10, 'range': 100, 'color': CYAN, 'rate': 40, 'desc': '减速敌人'},
    'fire': {'name': '火塔', 'cost': 120, 'damage': 25, 'range': 90, 'color': ORANGE, 'rate': 50, 'desc': '范围伤害'},
    'missile': {'name': '导弹塔', 'cost': 200, 'damage': 50, 'range': 200, 'color': RED, 'rate': 80, 'desc': '高伤害'},
    'heal': {'name': '治疗塔', 'cost': 100, 'damage': 0, 'range': 150, 'color': GREEN, 'rate': 60, 'desc': '治疗友军'},
    'slow': {'name': '陷阱', 'cost': 60, 'damage': 5, 'range': 60, 'color': PURPLE, 'rate': 20, 'desc': '持续减速'},
}

ENEMIES = {
    'basic': {'hp': 50, 'speed': 1.5, 'reward': 10, 'color': GREEN},
    'fast': {'hp': 30, 'speed': 3, 'reward': 15, 'color': YELLOW},
    'tank': {'hp': 150, 'speed': 0.8, 'reward': 30, 'color': RED},
    'boss': {'hp': 500, 'speed': 0.5, 'reward': 100, 'color': PURPLE},
}

class Tower:
    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.type = tower_type
        self.data = TOWERS[tower_type]
        self.cooldown = 0
        self.level = 1
    
    def update(self, enemies):
        if self.cooldown > 0:
            self.cooldown -= 1
            return
        
        target = None
        min_dist = self.data['range']
        
        for enemy in enemies:
            dist = ((self.x - enemy.x)**2 + (self.y - enemy.y)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                target = enemy
        
        if target:
            if self.type == 'heal':
                for e in enemies:
                    dist = ((self.x - e.x)**2 + (self.y - e.y)**2)**0.5
                    if dist < self.data['range']:
                        e.hp += 5
            elif self.type == 'slow':
                target.slow_timer = 60
            else:
                target.hp -= self.data['damage'] * self.level
            self.cooldown = self.data['rate']
    
    def draw(self):
        pygame.draw.circle(screen, self.data['color'], (int(self.x), int(self.y)), 20)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 20, 2)
        
        level_text = small_font.render(str(self.level), True, WHITE)
        screen.blit(level_text, (int(self.x) - 5, int(self.y) - 8))

class Enemy:
    def __init__(self, enemy_type, path):
        self.type = enemy_type
        self.data = ENEMIES[enemy_type]
        self.path = path
        self.path_index = 0
        self.x, self.y = path[0]
        self.hp = self.data['hp']
        self.max_hp = self.data['hp']
        self.slow_timer = 0
    
    def update(self):
        if self.slow_timer > 0:
            self.slow_timer -= 1
        
        speed_mult = 0.3 if self.slow_timer > 0 else 1
        
        if self.path_index < len(self.path) - 1:
            target = self.path[self.path_index + 1]
            dx = target[0] - self.x
            dy = target[1] - self.y
            dist = (dx**2 + dy**2)**0.5
            
            if dist < self.data['speed'] * speed_mult:
                self.path_index += 1
            else:
                self.x += (dx / dist) * self.data['speed'] * speed_mult
                self.y += (dy / dist) * self.data['speed'] * speed_mult
    
    def draw(self):
        color = PURPLE if self.slow_timer > 0 else self.data['color']
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 12)
        
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, RED, (int(self.x) - 15, int(self.y) - 25, 30, 5))
        pygame.draw.rect(screen, GREEN, (int(self.x) - 15, int(self.y) - 25, int(30 * hp_ratio), 5))

def tower_defense_deluxe():
    money = 200
    lives = 20
    score = 0
    wave = 0
    max_waves = 20
    
    towers = []
    enemies = []
    selected_tower = 'arrow'
    spawn_timer = 0
    enemies_to_spawn = []
    
    path = [(0, 350), (200, 350), (200, 200), (400, 200), (400, 500), (600, 500), (600, 350), (900, 350)]
    
    running = True
    
    while running and lives > 0 and wave < max_waves:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if my < 600:
                    can_place = True
                    for t in towers:
                        if ((t.x - mx)**2 + (t.y - my)**2)**0.5 < 40:
                            can_place = False
                            break
                    
                    if can_place and money >= TOWERS[selected_tower]['cost']:
                        towers.append(Tower(mx, my, selected_tower))
                        money -= TOWERS[selected_tower]['cost']
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_tower = 'arrow'
                elif event.key == pygame.K_2:
                    selected_tower = 'ice'
                elif event.key == pygame.K_3:
                    selected_tower = 'fire'
                elif event.key == pygame.K_4:
                    selected_tower = 'missile'
                elif event.key == pygame.K_5:
                    selected_tower = 'heal'
                elif event.key == pygame.K_6:
                    selected_tower = 'slow'
                elif event.key == pygame.K_SPACE and not enemies_to_spawn:
                    wave += 1
                    for _ in range(5 + wave * 2):
                        if random.random() < 0.1 and wave > 3:
                            enemies_to_spawn.append('boss')
                        elif random.random() < 0.3:
                            enemies_to_spawn.append('fast')
                        elif random.random() < 0.2 and wave > 5:
                            enemies_to_spawn.append('tank')
                        else:
                            enemies_to_spawn.append('basic')
        
        if enemies_to_spawn:
            spawn_timer -= 1
            if spawn_timer <= 0:
                enemies.append(Enemy(enemies_to_spawn.pop(0), path))
                spawn_timer = 30
        
        pygame.draw.lines(screen, (50, 50, 50), False, path, 20)
        
        for enemy in enemies[:]:
            enemy.update()
            enemy.draw()
            
            if enemy.hp <= 0:
                money += enemy.data['reward']
                score += enemy.data['reward']
                enemies.remove(enemy)
            
            if enemy.path_index >= len(enemy.path) - 1:
                lives -= 1
                enemies.remove(enemy)
        
        for tower in towers:
            tower.update(enemies)
            tower.draw()
        
        pygame.draw.rect(screen, BLACK, (0, 600, WIDTH, 100))
        
        money_text = font.render(f"金币: {money}", True, YELLOW)
        screen.blit(money_text, (10, 610))
        
        lives_text = font.render(f"生命: {lives}", True, RED)
        screen.blit(lives_text, (150, 610))
        
        wave_text = font.render(f"波次: {wave}/{max_waves}", True, WHITE)
        screen.blit(wave_text, (300, 610))
        
        score_text = font.render(f"得分: {score}", True, GREEN)
        screen.blit(score_text, (450, 610))
        
        for i, (tower_type, tower_data) in enumerate(TOWERS.items()):
            key = i + 1
            color = GREEN if money >= tower_data['cost'] else RED
            text = f"{key}. {tower_data['name']} (${tower_data['cost']})"
            t = small_font.render(text, True, color)
            screen.blit(t, (10 + (i % 3) * 200, 640 + (i // 3) * 25))
        
        selected_data = TOWERS[selected_tower]
        sel_text = font.render(f"选择: {selected_data['name']} - {selected_data['desc']}", True, GREEN)
        screen.blit(sel_text, (10, 680))
        
        if not enemies_to_spawn and wave < max_waves:
            start_text = font.render("按空格开始下一波", True, YELLOW)
            screen.blit(start_text, (WIDTH // 2 - 80, 620))
        
        pygame.display.flip()
        clock.tick(60)
    
    screen.fill(BLACK)
    
    if lives > 0:
        result = big_font.render("恭喜胜利!", True, GREEN)
    else:
        result = big_font.render("游戏结束!", True, RED)
    
    screen.blit(result, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
    
    final_score = font.render(f"最终得分: {score}", True, YELLOW)
    screen.blit(final_score, (WIDTH // 2 - 80, HEIGHT // 2 + 20))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    tower_defense_deluxe()
