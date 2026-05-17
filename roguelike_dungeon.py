import pygame
import os
import random
import math

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

WIDTH, HEIGHT = 800, 600
TILE = 40
COLS = WIDTH // TILE
ROWS = HEIGHT // TILE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Roguelike地牢探险")

clock = pygame.time.Clock()
font = get_chinese_font(24)

class Entity:
    def __init__(self, x, y, char, color, hp=10, atk=2):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.hp = hp
        self.max_hp = hp
        self.atk = atk

class Dungeon:
    def __init__(self):
        self.rooms = []
        self.map_grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]
        self.entities = []
        self.player = None
        self.floor = 1
        self.messages = []
        self.generate()
    
    def generate(self):
        self.map_grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]
        self.entities = []
        self.rooms = []
        
        for _ in range(8 + self.floor):
            w = random.randint(4, 8)
            h = random.randint(4, 7)
            rx = random.randint(1, COLS - w - 1)
            ry = random.randint(1, ROWS - h - 1)
            
            overlap = False
            for room in self.rooms:
                if (rx < room[0] + room[2] + 1 and rx + w + 1 > room[0] and
                    ry < room[1] + room[3] + 1 and ry + h + 1 > room[1]):
                    overlap = True
                    break
            
            if not overlap:
                self.rooms.append((rx, ry, w, h))
                for y in range(ry, ry + h):
                    for x in range(rx, rx + w):
                        self.map_grid[y][x] = 0
        
        # 连接房间
        for i in range(len(self.rooms) - 1):
            r1 = self.rooms[i]
            r2 = self.rooms[i + 1]
            cx1, cy1 = r1[0] + r1[2] // 2, r1[1] + r1[3] // 2
            cx2, cy2 = r2[0] + r2[2] // 2, r2[1] + r2[3] // 2
            
            x = cx1
            while x != cx2:
                self.map_grid[cy1][x] = 0
                x += 1 if cx2 > cx1 else -1
            y = cy1
            while y != cy2:
                self.map_grid[y][cx2] = 0
                y += 1 if cy2 > cy1 else -1
        
        # 放置玩家
        if self.player is None:
            start_room = self.rooms[0]
            px = start_room[0] + start_room[2] // 2
            py = start_room[1] + start_room[3] // 2
            self.player = Entity(px, py, '@', YELLOW, hp=30, atk=5)
        else:
            start_room = self.rooms[0]
            self.player.x = start_room[0] + start_room[2] // 2
            self.player.y = start_room[1] + start_room[3] // 2
        
        # 放置敌人和物品
        for i, room in enumerate(self.rooms[1:], 1):
            cx = room[0] + room[2] // 2
            cy = room[1] + room[3] // 2
            
            if random.random() < 0.6:
                enemy_names = ['G', 'S', 'R', 'D']
                enemy_colors = [RED, GREEN, (200, 200, 0), PURPLE]
                idx = min(self.floor - 1, len(enemy_names) - 1)
                e = Entity(cx, cy, enemy_names[idx], enemy_colors[idx],
                          hp=5 + self.floor * 3, atk=2 + self.floor)
                self.entities.append(e)
            
            if random.random() < 0.4:
                item = Entity(cx + 1, cy, '!', BLUE, hp=0, atk=0)
                self.entities.append(item)
        
        # 楼梯
        if len(self.rooms) > 1:
            last = self.rooms[-1]
            sx = last[0] + last[2] // 2
            sy = last[1] + last[3] // 2
            stair = Entity(sx, sy, '>', WHITE, hp=0, atk=0)
            self.entities.append(stair)
    
    def move_player(self, dx, dy):
        nx, ny = self.player.x + dx, self.player.y + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS and self.map_grid[ny][nx] == 0:
            for e in self.entities[:]:
                if e.x == nx and e.y == ny:
                    if e.char == '>':
                        self.floor += 1
                        self.messages.append(f"进入第 {self.floor} 层!")
                        self.generate()
                        return
                    elif e.char == '!':
                        heal = 10 + self.floor * 2
                        self.player.hp = min(self.player.max_hp, self.player.hp + heal)
                        self.messages.append(f"获得药水! 恢复{heal}HP")
                        self.entities.remove(e)
                        self.player.x, self.player.y = nx, ny
                        return
                    else:
                        dmg = max(1, self.player.atk + random.randint(-1, 2))
                        e.hp -= dmg
                        self.messages.append(f"攻击{e.char}造成{dmg}伤害")
                        if e.hp <= 0:
                            self.messages.append(f"击败{e.char}!")
                            self.entities.remove(e)
                            self.player.x, self.player.y = nx, ny
                        else:
                            edmg = max(1, e.atk + random.randint(-1, 1))
                            self.player.hp -= edmg
                            self.messages.append(f"{e.char}反击造成{edmg}伤害")
                        return
            self.player.x, self.player.y = nx, ny
    
    def draw(self):
        screen.fill(BLACK)
        
        # 绘制地图
        for y in range(ROWS):
            for x in range(COLS):
                sx, sy = x * TILE, y * TILE
                if self.map_grid[y][x] == 1:
                    pygame.draw.rect(screen, DARK_GRAY, (sx, sy, TILE, TILE))
                else:
                    pygame.draw.rect(screen, (30, 30, 30), (sx, sy, TILE, TILE))
        
        # 绘制实体
        for e in self.entities:
            sx, sy = e.x * TILE, e.y * TILE
            text = font.render(e.char, True, e.color)
            screen.blit(text, (sx + TILE // 2 - text.get_width() // 2,
                              sy + TILE // 2 - text.get_height() // 2))
        
        # 绘制玩家
        sx, sy = self.player.x * TILE, self.player.y * TILE
        text = font.render(self.player.char, True, self.player.color)
        screen.blit(text, (sx + TILE // 2 - text.get_width() // 2,
                          sy + TILE // 2 - text.get_height() // 2))
        
        # UI
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 40))
        hp_text = font.render(f"HP: {self.player.hp}/{self.player.max_hp}  ATK: {self.player.atk}  层: {self.floor}", True, WHITE)
        screen.blit(hp_text, (10, 10))
        
        # 消息
        for i, msg in enumerate(self.messages[-3:]):
            msg_text = font.render(msg, True, GRAY)
            screen.blit(msg_text, (10, HEIGHT - 80 + i * 25))

def roguelike_dungeon():
    dungeon = Dungeon()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    dungeon.move_player(0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    dungeon.move_player(0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    dungeon.move_player(-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    dungeon.move_player(1, 0)
        
        if dungeon.player.hp <= 0:
            dungeon.draw()
            go_text = font.render(f"你死了! 到达第 {dungeon.floor} 层", True, RED)
            screen.blit(go_text, (WIDTH // 2 - 100, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            break
        
        dungeon.draw()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    roguelike_dungeon()
