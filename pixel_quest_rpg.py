import pygame
import random
import sys

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 40

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 100)
PURPLE = (200, 100, 200)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
GRASS_GREEN = (34, 139, 34)
SKY_BLUE = (135, 206, 235)

# 设置屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("像素冒险RPG")
clock = pygame.time.Clock()

# 字体
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 48)

# 物品定义
ITEMS = {
    'wooden_sword': {'name': '木剑', 'type': 'weapon', 'attack': 5, 'price': 50},
    'iron_sword': {'name': '铁剑', 'type': 'weapon', 'attack': 15, 'price': 150},
    'gold_sword': {'name': '金剑', 'type': 'weapon', 'attack': 30, 'price': 400},
    'leather_armor': {'name': '皮甲', 'type': 'armor', 'defense': 5, 'price': 40},
    'iron_armor': {'name': '铁甲', 'type': 'armor', 'defense': 15, 'price': 120},
    'gold_armor': {'name': '金甲', 'type': 'armor', 'defense': 30, 'price': 350},
    'health_potion': {'name': '生命药水', 'type': 'consumable', 'heal': 30, 'price': 20},
    'big_health_potion': {'name': '大生命药水', 'type': 'consumable', 'heal': 80, 'price': 60}
}

# 敌人定义
ENEMIES = {
    'slime': {'name': '史莱姆', 'hp': 30, 'attack': 5, 'exp': 10, 'gold': 5},
    'goblin': {'name': '哥布林', 'hp': 50, 'attack': 10, 'exp': 20, 'gold': 15},
    'orc': {'name': '兽人', 'hp': 100, 'attack': 20, 'exp': 40, 'gold': 30},
    'dragon': {'name': '小龙', 'hp': 200, 'attack': 35, 'exp': 80, 'gold': 60},
    'boss': {'name': '魔王', 'hp': 500, 'attack': 50, 'exp': 300, 'gold': 200}
}

# 地图
MAP = [
    ['G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G'],
    ['G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G'],
    ['G','G','G','T','T','T','T','T','G','G','G','G','T','T','T','T','G','G','G','G'],
    ['G','G','G','T','G','G','G','T','G','G','G','G','T','G','G','T','G','G','G','G'],
    ['G','G','G','T','G','S','G','T','G','G','G','G','T','G','G','T','G','G','G','G'],
    ['G','G','G','T','G','G','G','T','T','T','T','T','T','G','G','T','G','G','G','G'],
    ['G','G','G','T','T','T','T','T','G','G','G','G','G','G','G','T','G','G','G','G'],
    ['G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','T','G','G','G','G'],
    ['G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','T','G','G','G','G'],
    ['G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','T','T','T','G','G'],
    ['G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','T','G','G'],
    ['G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','T','G','G'],
    ['G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','T','G','G'],
    ['G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G'],
    ['G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G','G']
]

class Player:
    def __init__(self):
        self.x = 5 * TILE_SIZE
        self.y = 4 * TILE_SIZE
        self.width = 30
        self.height = 40
        self.speed = 4
        self.hp = 100
        self.max_hp = 100
        self.level = 1
        self.exp = 0
        self.exp_to_next = 50
        self.gold = 100
        self.attack = 10
        self.defense = 0
        self.weapon = None
        self.armor = None
        self.inventory = {'health_potion': 3, 'big_health_potion': 0}
        self.facing = 'down'
        self.walk_frame = 0

    def move(self, dx, dy, game):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        # 碰撞检测
        if dx != 0:
            self.facing = 'right' if dx > 0 else 'left'
        if dy != 0:
            self.facing = 'down' if dy > 0 else 'up'

        if self.can_move_to(new_x, self.y, game):
            self.x = new_x
        if self.can_move_to(self.x, new_y, game):
            self.y = new_y

        self.walk_frame += 0.1

    def can_move_to(self, x, y, game):
        # 边界检查
        if x < 0 or x > SCREEN_WIDTH - self.width or y < 0 or y > SCREEN_HEIGHT - self.height:
            return False
        # 地图碰撞检查
        tile_x = int(x / TILE_SIZE)
        tile_y = int(y / TILE_SIZE)
        tile_x2 = int((x + self.width - 1) / TILE_SIZE)
        tile_y2 = int((y + self.height - 1) / TILE_SIZE)
        
        for ty in range(tile_y, tile_y2 + 1):
            for tx in range(tile_x, tile_x2 + 1):
                if ty >= 0 and ty < len(MAP) and tx >= 0 and tx < len(MAP[0]):
                    if MAP[ty][tx] == 'T':
                        return False
        return True

    def get_total_attack(self):
        base = self.attack + self.level * 2
        if self.weapon:
            base += ITEMS[self.weapon]['attack']
        return base

    def get_total_defense(self):
        base = self.defense + self.level
        if self.armor:
            base += ITEMS[self.armor]['defense']
        return base

    def gain_exp(self, amount):
        self.exp += amount
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level_up()

    def level_up(self):
        self.level += 1
        self.exp_to_next = int(self.exp_to_next * 1.5)
        self.max_hp += 20
        self.hp = self.max_hp
        self.attack += 3

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def equip(self, item_key):
        item = ITEMS[item_key]
        if item['type'] == 'weapon':
            self.weapon = item_key
        elif item['type'] == 'armor':
            self.armor = item_key

    def use_potion(self, potion_type):
        if self.inventory.get(potion_type, 0) > 0:
            self.inventory[potion_type] -= 1
            self.heal(ITEMS[potion_type]['heal'])
            return True
        return False

    def draw(self, surface):
        x = self.x
        y = self.y
        
        # 身体
        pygame.draw.rect(surface, BLUE, (x + 5, y + 10, 20, 25))
        # 头
        pygame.draw.circle(surface, YELLOW, (int(x + 15), int(y + 8)), 10)
        
        # 眼睛
        eye_offset = 0
        if self.facing == 'left':
            eye_offset = -3
        elif self.facing == 'right':
            eye_offset = 3
        pygame.draw.circle(surface, BLACK, (int(x + 12 + eye_offset), int(y + 6)), 2)
        pygame.draw.circle(surface, BLACK, (int(x + 18 + eye_offset), int(y + 6)), 2)

class Enemy:
    def __init__(self, enemy_type, x, y):
        self.type = enemy_type
        self.data = ENEMIES[enemy_type]
        self.x = x
        self.y = y
        self.width = 35
        self.height = 35
        self.hp = self.data['hp']
        self.max_hp = self.data['hp']
        self.attack = self.data['attack']
        self.exp = self.data['exp']
        self.gold = self.data['gold']
        self.alive = True

    def draw(self, surface):
        x = self.x
        y = self.y
        if self.type == 'slime':
            pygame.draw.ellipse(surface, GREEN, (x, y + 10, self.width, self.height - 10))
        elif self.type == 'goblin':
            pygame.draw.rect(surface, ORANGE, (x + 5, y + 5, self.width - 10, self.height - 5))
            pygame.draw.circle(surface, ORANGE, (int(x + self.width/2), int(y + 5)), 12)
        elif self.type == 'orc':
            pygame.draw.rect(surface, GREEN, (x, y, self.width, self.height))
            pygame.draw.rect(surface, WHITE, (x + 5, y + 10, 10, 10))
            pygame.draw.rect(surface, WHITE, (x + 20, y + 10, 10, 10))
        elif self.type == 'dragon':
            pygame.draw.ellipse(surface, RED, (x, y, self.width, self.height))
            pygame.draw.polygon(surface, ORANGE, [(x + 10, y), (x + 5, y - 15), (x + 20, y)])
            pygame.draw.polygon(surface, ORANGE, [(x + 25, y), (x + 30, y - 15), (x + 20, y)])
        elif self.type == 'boss':
            pygame.draw.rect(surface, PURPLE, (x - 10, y - 10, self.width + 20, self.height + 20))
            pygame.draw.rect(surface, RED, (x, y, self.width, self.height))

        # 血条
        pygame.draw.rect(surface, BLACK, (x, y - 10, self.width, 6))
        pygame.draw.rect(surface, RED, (x + 1, y - 9, (self.width - 2) * (self.hp / self.max_hp), 4))

class Shop:
    def __init__(self):
        self.items = ['wooden_sword', 'iron_sword', 'gold_sword', 'leather_armor', 'iron_armor', 'gold_armor', 'health_potion', 'big_health_potion']
        self.selected = 0

    def draw(self, surface, player):
        # 背景
        pygame.draw.rect(surface, DARK_GRAY, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100))
        pygame.draw.rect(surface, GRAY, (60, 60, SCREEN_WIDTH - 120, SCREEN_HEIGHT - 120))
        
        title = title_font.render("商店", True, YELLOW)
        surface.blit(title, (SCREEN_WIDTH // 2 - 50, 70))
        
        gold_text = small_font.render(f"金币: {player.gold}", True, YELLOW)
        surface.blit(gold_text, (70, 110))
        
        # 物品列表
        y_pos = 150
        for i, item_key in enumerate(self.items):
            item = ITEMS[item_key]
            color = WHITE
            if i == self.selected:
                color = YELLOW
                pygame.draw.rect(surface, YELLOW, (65, y_pos - 5, SCREEN_WIDTH - 130, 30), 2)
            
            name_text = small_font.render(item['name'], True, color)
            price_text = small_font.render(f"{item['price']}金币", True, color)
            
            if item['type'] == 'weapon':
                stat_text = small_font.render(f"攻击+{item['attack']}", True, color)
            elif item['type'] == 'armor':
                stat_text = small_font.render(f"防御+{item['defense']}", True, color)
            else:
                stat_text = small_font.render(f"回复{item['heal']}HP", True, color)
            
            surface.blit(name_text, (80, y_pos))
            surface.blit(stat_text, (250, y_pos))
            surface.blit(price_text, (SCREEN_WIDTH - 150, y_pos))
            y_pos += 35
        
        hint = small_font.render("按空格购买, 按E退出", True, WHITE)
        surface.blit(hint, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80))

    def move_selection(self, d):
        self.selected = max(0, min(len(self.items) - 1, self.selected + d))

    def buy(self, player):
        item_key = self.items[self.selected]
        item = ITEMS[item_key]
        if player.gold >= item['price']:
            player.gold -= item['price']
            if item['type'] == 'consumable':
                player.inventory[item_key] = player.inventory.get(item_key, 0) + 1
            else:
                player.equip(item_key)
            return True
        return False

class InventoryScreen:
    def __init__(self):
        self.selected = 0

    def draw(self, surface, player):
        pygame.draw.rect(surface, DARK_GRAY, (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100))
        pygame.draw.rect(surface, GRAY, (60, 60, SCREEN_WIDTH - 120, SCREEN_HEIGHT - 120))
        
        title = title_font.render("装备/物品", True, YELLOW)
        surface.blit(title, (SCREEN_WIDTH // 2 - 80, 70))
        
        # 装备
        y_pos = 120
        weapon_name = "无"
        if player.weapon:
            weapon_name = ITEMS[player.weapon]['name']
        armor_name = "无"
        if player.armor:
            armor_name = ITEMS[player.armor]['name']
        
        pygame.draw.rect(surface, BROWN, (70, y_pos, SCREEN_WIDTH - 140, 80))
        weapon_text = small_font.render(f"武器: {weapon_name}", True, WHITE)
        armor_text = small_font.render(f"护甲: {armor_name}", True, WHITE)
        surface.blit(weapon_text, (90, y_pos + 15))
        surface.blit(armor_text, (90, y_pos + 45))
        
        # 属性
        y_pos = 220
        stats = [
            f"等级: {player.level}",
            f"HP: {player.hp}/{player.max_hp}",
            f"攻击: {player.get_total_attack()}",
            f"防御: {player.get_total_defense()}",
            f"经验: {player.exp}/{player.exp_to_next}"
        ]
        for stat in stats:
            text = small_font.render(stat, True, WHITE)
            surface.blit(text, (90, y_pos))
            y_pos += 30
        
        # 物品
        y_pos = 220
        pygame.draw.rect(surface, BROWN, (350, y_pos - 10, SCREEN_WIDTH - 420, 150))
        potions = [('health_potion', '生命药水'), ('big_health_potion', '大生命药水')]
        
        for i, (potion_key, potion_name) in enumerate(potions):
            count = player.inventory.get(potion_key, 0)
            text = small_font.render(f"{potion_name}: {count}", True, WHITE)
            if i == self.selected:
                pygame.draw.rect(surface, YELLOW, (360, y_pos + i*35, SCREEN_WIDTH - 440, 30), 2)
            surface.blit(text, (370, y_pos + i*35))
        
        hint = small_font.render("按空格使用药水, 按E退出", True, WHITE)
        surface.blit(hint, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 80))

    def move_selection(self, d):
        self.selected = max(0, min(1, self.selected + d))

    def use_item(self, player):
        potions = ['health_potion', 'big_health_potion']
        return player.use_potion(potions[self.selected])

class Battle:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.state = 'player_turn'  # player_turn, enemy_turn, player_won, enemy_won
        self.log = []
        self.add_log(f"遭遇了 {enemy.data['name']}!")
        self.selected_action = 0
        self.actions = ['攻击', '使用物品', '逃跑']

    def add_log(self, text):
        self.log.append(text)
        if len(self.log) > 5:
            self.log.pop(0)

    def player_attack(self):
        damage = max(1, self.player.get_total_attack() - random.randint(0, 5))
        self.enemy.hp -= damage
        self.add_log(f"你造成了 {damage} 点伤害!")
        
        if self.enemy.hp <= 0:
            self.state = 'player_won'
            self.add_log(f"击败了 {self.enemy.data['name']}!")
            self.add_log(f"获得 {self.enemy.exp} 经验和 {self.enemy.gold} 金币!")
        else:
            self.state = 'enemy_turn'

    def enemy_attack(self):
        damage = max(1, self.enemy.attack - self.player.get_total_defense())
        self.player.hp -= damage
        self.add_log(f"{self.enemy.data['name']} 造成了 {damage} 点伤害!")
        
        if self.player.hp <= 0:
            self.state = 'enemy_won'
            self.add_log("你被击败了...")
        else:
            self.state = 'player_turn'

    def try_escape(self):
        if random.random() < 0.5:
            self.add_log("逃跑成功!")
            return True
        else:
            self.add_log("逃跑失败!")
            self.state = 'enemy_turn'
            return False

    def use_potion(self, potion_type):
        if self.player.use_potion(potion_type):
            item = ITEMS[potion_type]
            self.add_log(f"使用了 {item['name']}, 恢复了 {item['heal']} HP!")
            self.state = 'enemy_turn'
            return True
        return False

    def draw(self, surface):
        # 背景
        surface.fill(BROWN)
        
        # 敌人
        enemy_x = SCREEN_WIDTH // 2 - 50
        enemy_y = 100
        self.enemy.x = enemy_x
        self.enemy.y = enemy_y
        self.enemy.width = 100
        self.enemy.height = 100
        self.enemy.draw(surface)
        
        enemy_name = small_font.render(self.enemy.data['name'], True, WHITE)
        surface.blit(enemy_name, (enemy_x + 20, enemy_y - 30))
        
        # 玩家
        player_x = 100
        player_y = 300
        pygame.draw.rect(surface, BLUE, (player_x, player_y, 60, 80))
        pygame.draw.circle(surface, YELLOW, (player_x + 30, player_y + 15), 20)
        
        # 血条
        pygame.draw.rect(surface, BLACK, (player_x - 20, player_y - 30, 100, 20))
        pygame.draw.rect(surface, RED, (player_x - 18, player_y - 28, 96 * (self.player.hp / self.player.max_hp), 16))
        hp_text = small_font.render(f"{self.player.hp}/{self.player.max_hp}", True, WHITE)
        surface.blit(hp_text, (player_x, player_y - 25))
        
        # 战斗日志
        log_y = 450
        pygame.draw.rect(surface, DARK_GRAY, (20, log_y - 10, SCREEN_WIDTH - 40, 140))
        for i, log_text in enumerate(self.log):
            text = small_font.render(log_text, True, WHITE)
            surface.blit(text, (40, log_y + i*25))
        
        # 操作菜单
        if self.state == 'player_turn':
            menu_x = SCREEN_WIDTH - 220
            menu_y = 300
            pygame.draw.rect(surface, GRAY, (menu_x, menu_y, 200, 120))
            for i, action in enumerate(self.actions):
                color = YELLOW if i == self.selected_action else WHITE
                text = small_font.render(action, True, color)
                surface.blit(text, (menu_x + 20, menu_y + 20 + i*35))

class Game:
    def __init__(self):
        self.player = Player()
        self.enemies = []
        self.shop = Shop()
        self.inventory_screen = InventoryScreen()
        self.battle = None
        self.state = 'game'  # game, shop, inventory, battle
        self.spawn_timer = 0
        self.game_over = False
        self.victory = False

        # 初始敌人
        self.spawn_enemies()

    def spawn_enemies(self):
        self.enemies = []
        # 史莱姆区域
        for _ in range(3):
            x = random.randint(8 * TILE_SIZE, 12 * TILE_SIZE)
            y = random.randint(2 * TILE_SIZE, 8 * TILE_SIZE)
            self.enemies.append(Enemy('slime', x, y))
        # 哥布林区域
        for _ in range(2):
            x = random.randint(1 * TILE_SIZE, 4 * TILE_SIZE)
            y = random.randint(8 * TILE_SIZE, 13 * TILE_SIZE)
            self.enemies.append(Enemy('goblin', x, y))
        # 兽人区域
        for _ in range(2):
            x = random.randint(13 * TILE_SIZE, 18 * TILE_SIZE)
            y = random.randint(9 * TILE_SIZE, 13 * TILE_SIZE)
            self.enemies.append(Enemy('orc', x, y))
        # 龙
        self.enemies.append(Enemy('dragon', 15 * TILE_SIZE, 12 * TILE_SIZE))
        # Boss
        self.enemies.append(Enemy('boss', 17 * TILE_SIZE, 13 * TILE_SIZE))

    def update(self):
        if self.game_over or self.victory:
            return

        if self.state == 'game':
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            
            if dx != 0 or dy != 0:
                self.player.move(dx, dy, self)

            # 商店碰撞
            shop_x = 5 * TILE_SIZE
            shop_y = 4 * TILE_SIZE
            if (abs(self.player.x - shop_x) < TILE_SIZE and 
                abs(self.player.y - shop_y) < TILE_SIZE):
                pass  # 商店区域

            # 敌人碰撞
            for enemy in self.enemies[:]:
                if enemy.alive:
                    player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                    if player_rect.colliderect(enemy_rect):
                        self.start_battle(enemy)

        elif self.state == 'battle' and self.battle:
            pass

    def start_battle(self, enemy):
        self.battle = Battle(self.player, enemy)
        self.state = 'battle'

    def handle_key(self, event):
        if event.key == pygame.K_r and (self.game_over or self.victory):
            self.__init__()
            return

        if self.state == 'game':
            if event.key == pygame.K_e:
                tile_x = int(self.player.x / TILE_SIZE)
                tile_y = int(self.player.y / TILE_SIZE)
                if tile_x == 5 and tile_y == 4:
                    self.state = 'shop'
                else:
                    self.state = 'inventory'
        elif self.state == 'shop':
            if event.key == pygame.K_e:
                self.state = 'game'
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.shop.move_selection(-1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.shop.move_selection(1)
            elif event.key == pygame.K_SPACE:
                self.shop.buy(self.player)
        elif self.state == 'inventory':
            if event.key == pygame.K_e:
                self.state = 'game'
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.inventory_screen.move_selection(-1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.inventory_screen.move_selection(1)
            elif event.key == pygame.K_SPACE:
                self.inventory_screen.use_item(self.player)
        elif self.state == 'battle' and self.battle:
            if self.battle.state == 'player_turn':
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.battle.selected_action = max(0, self.battle.selected_action - 1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.battle.selected_action = min(2, self.battle.selected_action + 1)
                elif event.key == pygame.K_SPACE:
                    if self.battle.selected_action == 0:
                        self.battle.player_attack()
                    elif self.battle.selected_action == 1:
                        # 简单使用小药水
                        if not self.battle.use_potion('health_potion'):
                            self.battle.use_potion('big_health_potion')
                    elif self.battle.selected_action == 2:
                        if self.battle.try_escape():
                            self.state = 'game'
                            self.battle = None
            elif self.battle.state == 'enemy_turn':
                if event.key == pygame.K_SPACE:
                    self.battle.enemy_attack()
            elif self.battle.state == 'player_won':
                if event.key == pygame.K_SPACE:
                    self.player.gain_exp(self.battle.enemy.exp)
                    self.player.gold += self.battle.enemy.gold
                    if self.battle.enemy in self.enemies:
                        if self.battle.enemy.type == 'boss':
                            self.victory = True
                        self.enemies.remove(self.battle.enemy)
                    self.state = 'game'
                    self.battle = None
            elif self.battle.state == 'enemy_won':
                if event.key == pygame.K_SPACE:
                    self.game_over = True
                    self.state = 'game'

    def draw(self):
        if self.state == 'game' or self.state == 'battle':
            self.draw_map()
            
            if self.state == 'game':
                for enemy in self.enemies:
                    if enemy.alive:
                        enemy.draw(screen)
                self.player.draw(screen)
                self.draw_ui()
                
                if self.game_over:
                    text = title_font.render("游戏结束! R键重玩", True, RED)
                    screen.blit(text, (SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2))
                elif self.victory:
                    text = title_font.render("恭喜通关! R键重玩", True, YELLOW)
                    screen.blit(text, (SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2))
            else:
                self.battle.draw(screen)
        elif self.state == 'shop':
            self.shop.draw(screen, self.player)
        elif self.state == 'inventory':
            self.inventory_screen.draw(screen, self.player)

    def draw_map(self):
        screen.fill(SKY_BLUE)
        for y, row in enumerate(MAP):
            for x, tile in enumerate(row):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile == 'G':
                    pygame.draw.rect(screen, GRASS_GREEN, rect)
                    pygame.draw.rect(screen, (20, 100, 20), rect, 1)
                elif tile == 'T':
                    pygame.draw.rect(screen, GRAY, rect)
                elif tile == 'S':
                    pygame.draw.rect(screen, BROWN, rect)
                    pygame.draw.rect(screen, (100, 50, 0), rect, 3)

    def draw_ui(self):
        # HP
        pygame.draw.rect(screen, BLACK, (10, 10, 204, 24))
        pygame.draw.rect(screen, RED, (12, 12, 200 * (self.player.hp / self.player.max_hp), 20))
        hp_text = small_font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, WHITE)
        screen.blit(hp_text, (20, 12))
        
        # 等级
        level_text = small_font.render(f"等级: {self.player.level}", True, WHITE)
        screen.blit(level_text, (10, 45))
        
        # 经验
        exp_text = small_font.render(f"经验: {self.player.exp}/{self.player.exp_to_next}", True, WHITE)
        screen.blit(exp_text, (10, 70))
        
        # 金币
        gold_text = small_font.render(f"金币: {self.player.gold}", True, YELLOW)
        screen.blit(gold_text, (10, 95))
        
        # 提示
        hint1 = small_font.render("移动: 方向键/WASD", True, WHITE)
        hint2 = small_font.render("商店/E键: 物品栏", True, WHITE)
        screen.blit(hint1, (SCREEN_WIDTH - 220, 10))
        screen.blit(hint2, (SCREEN_WIDTH - 220, 35))

def main():
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                game.handle_key(event)

        game.update()
        game.draw()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
