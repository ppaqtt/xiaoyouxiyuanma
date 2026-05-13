import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("放置挂机游戏")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)
big_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 24)

class IdleGame:
    def __init__(self):
        self.gold = 0
        self.total_gold = 0
        self.level = 1
        self.damage = 1
        self.health = 100
        self.max_health = 100
        self.armor = 0
        
        self.upgrades = {
            'damage': {'cost': 10, 'bonus': 1, 'name': '攻击'},
            'health': {'cost': 20, 'bonus': 10, 'name': '生命'},
            'armor': {'cost': 30, 'bonus': 1, 'name': '护甲'},
            'crit': {'cost': 50, 'bonus': 1, 'name': '暴击'},
        }
        
        self.stats = {
            'damage': 0,
            'health': 0,
            'armor': 0,
            'crit': 0,
        }
        
        self.enemies_killed = 0
        self.current_enemy = self.generate_enemy()
        self.enemy_damage_cooldown = 0
        self.auto_click_enabled = True
        
        self.achievements = []
        self.unlocked_items = []
        
        self.last_update = pygame.time.get_ticks()
    
    def generate_enemy(self):
        return {
            'name': random.choice(['史莱姆', '哥布林', '骷髅', '兽人', '恶龙']),
            'health': 10 + self.level * 5,
            'max_health': 10 + self.level * 5,
            'damage': 1 + self.level,
            'gold_reward': 5 + self.level,
            'color': random.choice([GREEN, RED, BLUE, PURPLE, ORANGE])
        }
    
    def click_damage(self):
        crit_chance = self.stats['crit'] * 0.01
        crit_mult = 2 if random.random() < crit_chance else 1
        damage = (self.damage + self.stats['damage']) * crit_mult
        self.current_enemy['health'] -= damage
        return crit_mult > 1
    
    def update(self):
        now = pygame.time.get_ticks()
        
        if self.enemy_damage_cooldown > 0:
            self.enemy_damage_cooldown -= 1
        
        if self.current_enemy['health'] <= 0:
            gold_reward = self.current_enemy['gold_reward']
            self.gold += gold_reward
            self.total_gold += gold_reward
            self.enemies_killed += 1
            self.current_enemy = self.generate_enemy()
            
            if self.enemies_killed % 10 == 0:
                self.level += 1
        
        if self.enemy_damage_cooldown == 0 and not self.auto_click_enabled:
            damage = self.current_enemy['damage']
            actual_damage = max(1, damage - self.stats['armor'])
            self.health -= actual_damage
            self.enemy_damage_cooldown = 60
        
        if self.health <= 0:
            self.health = self.max_health + self.stats['health']
            self.gold = max(0, self.gold - self.level * 10)
    
    def buy_upgrade(self, upgrade_type):
        upgrade = self.upgrades[upgrade_type]
        cost = upgrade['cost'] * (1 + self.stats[upgrade_type])
        
        if self.gold >= cost:
            self.gold -= cost
            self.stats[upgrade_type] += 1
            
            if upgrade_type == 'damage':
                self.damage += upgrade['bonus']
            elif upgrade_type == 'health':
                self.max_health += upgrade['bonus']
            elif upgrade_type == 'armor':
                self.armor += upgrade['bonus']
            
            return True
        return False
    
    def draw(self):
        screen.fill(BLACK)
        
        pygame.draw.rect(screen, (20, 20, 40), (0, 0, WIDTH // 2, HEIGHT))
        
        pygame.draw.rect(screen, (40, 40, 60), (0, 0, WIDTH // 2, HEIGHT // 3))
        
        pygame.draw.circle(screen, self.current_enemy['color'], 
                          (WIDTH // 4, HEIGHT // 6), 50)
        
        enemy_name = font.render(self.current_enemy['name'], True, WHITE)
        screen.blit(enemy_name, (WIDTH // 4 - enemy_name.get_width() // 2, HEIGHT // 3 + 20))
        
        enemy_health_ratio = self.current_enemy['health'] / self.current_enemy['max_health']
        pygame.draw.rect(screen, RED, (WIDTH // 8, HEIGHT // 2 - 20, WIDTH // 4, 20))
        pygame.draw.rect(screen, GREEN, 
                        (WIDTH // 8, HEIGHT // 2 - 20, int(WIDTH // 4 * enemy_health_ratio), 20))
        
        enemy_hp_text = font.render(f"{int(self.current_enemy['health'])}/{self.current_enemy['max_health']}", 
                                    True, WHITE)
        screen.blit(enemy_hp_text, (WIDTH // 8, HEIGHT // 2 + 5))
        
        click_area = (WIDTH // 8, HEIGHT // 3 - 50, WIDTH // 4, 150)
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            if (click_area[0] <= mx <= click_area[0] + click_area[2] and
                click_area[1] <= my <= click_area[1] + click_area[3]):
                crit = self.click_damage()
        
        player_info_x = WIDTH // 2 + 20
        pygame.draw.rect(screen, (20, 20, 40), (player_info_x - 10, 0, WIDTH // 2, HEIGHT))
        
        gold_text = big_font.render(f"💰 {self.gold}", True, YELLOW)
        screen.blit(gold_text, (player_info_x, 20))
        
        total_gold = font.render(f"总金币: {self.total_gold}", True, WHITE)
        screen.blit(total_gold, (player_info_x, 80))
        
        level_text = font.render(f"等级: {self.level}", True, GREEN)
        screen.blit(level_text, (player_info_x, 120))
        
        pygame.draw.rect(screen, RED, (player_info_x, 160, 200, 20))
        pygame.draw.rect(screen, GREEN, 
                        (player_info_x, 160, int(200 * self.health / self.max_health), 20))
        health_text = font.render(f"生命: {int(self.health)}/{self.max_health + self.stats['health']}", 
                                True, WHITE)
        screen.blit(health_text, (player_info_x, 185))
        
        pygame.draw.rect(screen, (40, 40, 60), (player_info_x - 10, 220, WIDTH // 2 - 20, 300))
        upgrades_title = font.render("升级:", True, WHITE)
        screen.blit(upgrades_title, (player_info_x, 230))
        
        y_offset = 270
        for upgrade_type, upgrade_data in self.upgrades.items():
            cost = upgrade_data['cost'] * (1 + self.stats[upgrade_type])
            can_afford = self.gold >= cost
            
            color = GREEN if can_afford else RED
            text = f"{upgrade_data['name']} +{upgrade_data['bonus']} (Lv.{self.stats[upgrade_type]}) - {cost}金币"
            upgrade_text = small_font.render(text, True, color)
            screen.blit(upgrade_text, (player_info_x, y_offset))
            
            if can_afford:
                hint = small_font.render(f"按{list(self.upgrades.keys()).index(upgrade_type) + 1}", 
                                       True, YELLOW)
                screen.blit(hint, (player_info_x + 280, y_offset))
            
            y_offset += 35
        
        stats_text = font.render(f"攻击: {self.damage + self.stats['damage']} | "
                                f"护甲: {self.armor + self.stats['armor']} | "
                                f"暴击: {self.stats['crit']}%", True, WHITE)
        screen.blit(stats_text, (player_info_x, y_offset + 20))
        
        kills_text = font.render(f"击杀: {self.enemies_killed}", True, WHITE)
        screen.blit(kills_text, (player_info_x, y_offset + 50))
        
        auto_text = font.render(f"自动攻击: {'ON' if self.auto_click_enabled else 'OFF'} (按A切换)", 
                               True, GREEN if self.auto_click_enabled else RED)
        screen.blit(auto_text, (10, HEIGHT - 30))

def idle_incremental():
    game = IdleGame()
    auto_attack_cooldown = 0
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game.buy_upgrade('damage')
                elif event.key == pygame.K_2:
                    game.buy_upgrade('health')
                elif event.key == pygame.K_3:
                    game.buy_upgrade('armor')
                elif event.key == pygame.K_4:
                    game.buy_upgrade('crit')
                elif event.key == pygame.K_a:
                    game.auto_click_enabled = not game.auto_click_enabled
        
        if game.auto_click_enabled:
            auto_attack_cooldown -= 1
            if auto_attack_cooldown <= 0:
                game.click_damage()
                auto_attack_cooldown = 10
        
        game.update()
        game.draw()
        
        instruction = small_font.render("1-4升级 | A自动攻击 | 点击怪物攻击", True, WHITE)
        screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    idle_incremental()
