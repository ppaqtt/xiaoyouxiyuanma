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
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_BLUE = (173, 216, 230)

# 设置屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("简化银河恶魔城")
clock = pygame.time.Clock()

# 字体
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# 房间地图定义 (0=空, 1=平台, 2=门, 3=钥匙, 4=收集物, 5=升级, 6=敌人)
ROOMS = {
    0: {  # 起始房间
        'name': '起始大厅',
        'tiles': [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,1,1,0,0,1,1,1,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        'doors': [{'x': 18, 'y': 1, 'to_room': 1, 'to_x': 1, 'to_y': 12, 'key_required': False}],
        'keys': [{'x': 10, 'y': 8}],
        'collectibles': [{'x': 5, 'y': 3, 'type': 'health'}, {'x': 14, 'y': 3, 'type': 'coin'}],
        'upgrades': [],
        'enemies': [{'x': 12, 'y': 12, 'type': 'slime'}]
    },
    1: {  # 房间1
        'name': '长廊',
        'tiles': [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        'doors': [
            {'x': 0, 'y': 12, 'to_room': 0, 'to_x': 17, 'to_y': 1, 'key_required': False},
            {'x': 18, 'y': 1, 'to_room': 2, 'to_x': 1, 'to_y': 12, 'key_required': True}
        ],
        'keys': [{'x': 3, 'y': 3}],
        'collectibles': [{'x': 10, 'y': 6, 'type': 'coin'}, {'x': 16, 'y': 3, 'type': 'health'}],
        'upgrades': [{'x': 15, 'y': 12, 'type': 'double_jump'}],
        'enemies': [{'x': 5, 'y': 12, 'type': 'slime'}, {'x': 13, 'y': 12, 'type': 'bat'}]
    },
    2: {  # 房间2 - 需要钥匙
        'name': '宝藏室',
        'tiles': [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ],
        'doors': [{'x': 0, 'y': 12, 'to_room': 1, 'to_x': 17, 'to_y': 1, 'key_required': False}],
        'keys': [],
        'collectibles': [{'x': 5, 'y': 12, 'type': 'coin'}, {'x': 8, 'y': 3, 'type': 'health'}, 
                        {'x': 11, 'y': 3, 'type': 'coin'}, {'x': 14, 'y': 12, 'type': 'coin'}],
        'upgrades': [{'x': 10, 'y': 12, 'type': 'health_boost'}],
        'enemies': [{'x': 10, 'y': 3, 'type': 'boss'}]
    }
}

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 40
        self.vx = 0
        self.vy = 0
        self.speed = 5
        self.jump_power = -15
        self.gravity = 0.8
        self.on_ground = False
        self.health = 100
        self.max_health = 100
        self.keys = 0
        self.coins = 0
        self.can_double_jump = False
        self.has_double_jumped = False
        self.invincible = 0
        self.facing_right = True

    def update(self, tiles):
        # 应用重力
        self.vy += self.gravity
        if self.vy > 15:
            self.vy = 15

        # 水平移动
        self.x += self.vx

        # 水平碰撞检测
        self.check_collision(tiles, 'horizontal')

        # 垂直移动
        self.y += self.vy

        # 垂直碰撞检测
        self.on_ground = False
        self.check_collision(tiles, 'vertical')

        # 更新无敌时间
        if self.invincible > 0:
            self.invincible -= 1

        # 重置二段跳
        if self.on_ground:
            self.has_double_jumped = False

        # 更新朝向
        if self.vx > 0:
            self.facing_right = True
        elif self.vx < 0:
            self.facing_right = False

    def check_collision(self, tiles, direction):
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        for y, row in enumerate(tiles):
            for x, tile in enumerate(row):
                if tile == 1:
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if player_rect.colliderect(tile_rect):
                        if direction == 'horizontal':
                            if self.vx > 0:
                                self.x = tile_rect.left - self.width
                            elif self.vx < 0:
                                self.x = tile_rect.right
                        else:
                            if self.vy > 0:
                                self.y = tile_rect.top - self.height
                                self.on_ground = True
                                self.vy = 0
                            elif self.vy < 0:
                                self.y = tile_rect.bottom
                                self.vy = 0

    def jump(self):
        if self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False
        elif self.can_double_jump and not self.has_double_jumped:
            self.vy = self.jump_power * 0.9
            self.has_double_jumped = True

    def take_damage(self, amount):
        if self.invincible <= 0:
            self.health -= amount
            self.invincible = 60
            if self.health < 0:
                self.health = 0

    def draw(self, surface):
        if self.invincible > 0 and self.invincible % 4 < 2:
            return
        color = BLUE
        if self.facing_right:
            pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))
            pygame.draw.circle(surface, WHITE, (int(self.x + self.width - 8), int(self.y + 12)), 4)
        else:
            pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))
            pygame.draw.circle(surface, WHITE, (int(self.x + 8), int(self.y + 12)), 4)

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = 30
        self.height = 30
        self.type = enemy_type
        self.vx = 2 if enemy_type == 'slime' else 3
        self.direction = 1
        self.health = 50 if enemy_type == 'boss' else 20
        self.max_health = self.health
        self.anim_timer = 0

    def update(self, tiles):
        self.anim_timer += 1
        
        if self.type == 'slime':
            self.x += self.vx * self.direction
        elif self.type == 'bat':
            self.x += self.vx * self.direction
            self.y += math.sin(self.anim_timer * 0.1) * 0.5
        elif self.type == 'boss':
            self.x += self.vx * 0.5 * self.direction

        # 简单的碰撞检测和方向反转
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for y, row in enumerate(tiles):
            for x, tile in enumerate(row):
                if tile == 1:
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if player_rect.colliderect(tile_rect):
                        self.direction *= -1
                        break

    def draw(self, surface):
        if self.type == 'slime':
            pygame.draw.ellipse(surface, GREEN, (self.x, self.y + 5, self.width, self.height - 5))
        elif self.type == 'bat':
            pygame.draw.ellipse(surface, PURPLE, (self.x, self.y, self.width, self.height))
        elif self.type == 'boss':
            pygame.draw.rect(surface, RED, (self.x, self.y, self.width + 20, self.height + 20))
            pygame.draw.rect(surface, ORANGE, (self.x + 5, self.y + 5, 10, 10))
            pygame.draw.rect(surface, ORANGE, (self.x + 35, self.y + 5, 10, 10))

        # 血条
        if self.health < self.max_health:
            pygame.draw.rect(surface, RED, (self.x, self.y - 10, self.width, 5))
            pygame.draw.rect(surface, GREEN, (self.x, self.y - 10, self.width * (self.health / self.max_health), 5))

class Item:
    def __init__(self, x, y, item_type):
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = 20
        self.height = 20
        self.type = item_type
        self.collected = False
        self.anim_timer = 0

    def update(self):
        self.anim_timer += 1

    def draw(self, surface):
        if self.collected:
            return
        y_offset = math.sin(self.anim_timer * 0.1) * 3
        if self.type == 'health':
            pygame.draw.rect(surface, RED, (self.x, self.y + y_offset, self.width, self.height))
            pygame.draw.rect(surface, WHITE, (self.x + 8, self.y + y_offset, 4, 20))
            pygame.draw.rect(surface, WHITE, (self.x, self.y + 8 + y_offset, 20, 4))
        elif self.type == 'coin':
            pygame.draw.circle(surface, YELLOW, (int(self.x + 10), int(self.y + 10 + y_offset)), 10)
        elif self.type == 'double_jump':
            pygame.draw.rect(surface, PURPLE, (self.x, self.y + y_offset, self.width, self.height))
        elif self.type == 'health_boost':
            pygame.draw.rect(surface, ORANGE, (self.x, self.y + y_offset, self.width, self.height))

class Key:
    def __init__(self, x, y):
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = 20
        self.height = 20
        self.collected = False
        self.anim_timer = 0

    def update(self):
        self.anim_timer += 1

    def draw(self, surface):
        if self.collected:
            return
        y_offset = math.sin(self.anim_timer * 0.1) * 3
        pygame.draw.rect(surface, YELLOW, (self.x, self.y + y_offset, self.width, self.height))
        pygame.draw.circle(surface, BLACK, (int(self.x + 15), int(self.y + 10 + y_offset)), 4)

class Door:
    def __init__(self, door_data):
        self.x = door_data['x'] * TILE_SIZE
        self.y = door_data['y'] * TILE_SIZE
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.to_room = door_data['to_room']
        self.to_x = door_data['to_x'] * TILE_SIZE
        self.to_y = door_data['to_y'] * TILE_SIZE
        self.key_required = door_data['key_required']

    def draw(self, surface):
        color = GRAY if self.key_required else LIGHT_BLUE
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))
        if self.key_required:
            pygame.draw.rect(surface, YELLOW, (self.x + 15, self.y + 10, 10, 20))

class Game:
    def __init__(self):
        self.player = Player(2 * TILE_SIZE, 10 * TILE_SIZE)
        self.current_room = 0
        self.room = ROOMS[self.current_room]
        self.enemies = []
        self.items = []
        self.keys = []
        self.doors = []
        self.load_room()
        self.game_over = False
        self.win = False

    def load_room(self):
        self.room = ROOMS[self.current_room]
        self.enemies = []
        self.items = []
        self.keys = []
        self.doors = []

        for enemy_data in self.room['enemies']:
            self.enemies.append(Enemy(enemy_data['x'], enemy_data['y'], enemy_data['type']))
        
        for item_data in self.room['collectibles']:
            self.items.append(Item(item_data['x'], item_data['y'], item_data['type']))
        
        for upgrade_data in self.room['upgrades']:
            self.items.append(Item(upgrade_data['x'], upgrade_data['y'], upgrade_data['type']))
        
        for key_data in self.room['keys']:
            self.keys.append(Key(key_data['x'], key_data['y']))
        
        for door_data in self.room['doors']:
            self.doors.append(Door(door_data))

    def change_room(self, door):
        self.current_room = door.to_room
        self.player.x = door.to_x
        self.player.y = door.to_y
        self.load_room()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        self.player.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vx = -self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vx = self.player.speed

    def handle_keydown(self, event):
        if event.key == pygame.K_SPACE or event.key == pygame.K_UP or event.key == pygame.K_w:
            self.player.jump()

    def update(self):
        if self.game_over or self.win:
            return

        self.player.update(self.room['tiles'])
        
        for enemy in self.enemies:
            enemy.update(self.room['tiles'])
            player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            
            if player_rect.colliderect(enemy_rect):
                if self.player.vy > 0 and self.player.y + self.player.height - 10 < enemy.y + enemy.height / 2:
                    enemy.health -= 25
                    self.player.vy = -10
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                else:
                    self.player.take_damage(20)

        for item in self.items:
            item.update()
            if not item.collected:
                player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
                item_rect = pygame.Rect(item.x, item.y, item.width, item.height)
                if player_rect.colliderect(item_rect):
                    item.collected = True
                    if item.type == 'health':
                        self.player.health = min(self.player.health + 30, self.player.max_health)
                    elif item.type == 'coin':
                        self.player.coins += 10
                    elif item.type == 'double_jump':
                        self.player.can_double_jump = True
                    elif item.type == 'health_boost':
                        self.player.max_health += 50
                        self.player.health += 50

        for key in self.keys:
            key.update()
            if not key.collected:
                player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
                key_rect = pygame.Rect(key.x, key.y, key.width, key.height)
                if player_rect.colliderect(key_rect):
                    key.collected = True
                    self.player.keys += 1

        for door in self.doors:
            player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
            door_rect = pygame.Rect(door.x, door.y, door.width, door.height)
            if player_rect.colliderect(door_rect):
                if door.key_required and self.player.keys > 0:
                    self.player.keys -= 1
                    self.change_room(door)
                elif not door.key_required:
                    self.change_room(door)

        if self.player.health <= 0:
            self.game_over = True

        # 简单的胜利条件 - 击败boss
        if self.current_room == 2 and len(self.enemies) == 0 and self.win == False:
            self.win = True

    def draw(self):
        screen.fill(DARK_GRAY)
        
        # 绘制瓷砖
        for y, row in enumerate(self.room['tiles']):
            for x, tile in enumerate(row):
                if tile == 1:
                    pygame.draw.rect(screen, GRAY, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(screen, DARK_GRAY, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)
        
        # 绘制门
        for door in self.doors:
            door.draw(screen)
        
        # 绘制钥匙
        for key in self.keys:
            key.draw(screen)
        
        # 绘制物品
        for item in self.items:
            item.draw(screen)
        
        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(screen)
        
        # 绘制玩家
        self.player.draw(screen)
        
        # UI
        self.draw_ui()
        
        if self.game_over:
            game_over_text = font.render("游戏结束! R键重新开始", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
        
        if self.win:
            win_text = font.render("恭喜通关! R键重新开始", True, GREEN)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))

    def draw_ui(self):
        # 生命值
        health_text = small_font.render(f"生命: {self.player.health}/{self.player.max_health}", True, WHITE)
        screen.blit(health_text, (10, 10))
        
        # 钥匙
        key_text = small_font.render(f"钥匙: {self.player.keys}", True, YELLOW)
        screen.blit(key_text, (10, 40))
        
        # 金币
        coin_text = small_font.render(f"金币: {self.player.coins}", True, YELLOW)
        screen.blit(coin_text, (10, 70))
        
        # 房间名称
        room_text = small_font.render(f"区域: {self.room['name']}", True, WHITE)
        screen.blit(room_text, (SCREEN_WIDTH - 150, 10))
        
        # 能力
        if self.player.can_double_jump:
            ability_text = small_font.render("二段跳: 已获得", True, PURPLE)
            screen.blit(ability_text, (10, 100))

    def reset(self):
        self.player = Player(2 * TILE_SIZE, 10 * TILE_SIZE)
        self.current_room = 0
        self.load_room()
        self.game_over = False
        self.win = False

import math

def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.reset()
                else:
                    game.handle_keydown(event)
        
        game.handle_input()
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
