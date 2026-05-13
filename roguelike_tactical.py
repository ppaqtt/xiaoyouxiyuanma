
import pygame
import random
import sys

# 初始化Pygame
pygame.init()

# 窗口设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("回合制战术 - 地牢探索")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 200)
GRAY = (120, 120, 120)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (180, 180, 180)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
LIGHT_BLUE = (100, 200, 255)
BROWN = (139, 69, 19)

# 字体
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# 网格设置
TILE_SIZE = 40
GRID_WIDTH = 16
GRID_HEIGHT = 12

# 职业定义
CLASSES = {
    "warrior": {
        "name": "战士",
        "max_hp": 100,
        "damage": 15,
        "range": 1,
        "move_range": 3,
        "color": RED,
        "desc": "高血量近战"
    },
    "archer": {
        "name": "弓箭手",
        "max_hp": 70,
        "damage": 12,
        "range": 3,
        "move_range": 4,
        "color": GREEN,
        "desc": "远程攻击"
    },
    "mage": {
        "name": "法师",
        "max_hp": 60,
        "damage": 20,
        "range": 2,
        "move_range": 2,
        "color": PURPLE,
        "desc": "高伤害"
    }
}

# 玩家类
class Player:
    def __init__(self, class_type, x, y):
        self.class_type = class_type
        stats = CLASSES[class_type]
        self.name = stats["name"]
        self.max_hp = stats["max_hp"]
        self.hp = self.max_hp
        self.damage = stats["damage"]
        self.range = stats["range"]
        self.move_range = stats["move_range"]
        self.color = stats["color"]
        self.x = x
        self.y = y
        self.acted = False
        self.moved = False

# 敌人类
class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        
        if enemy_type == "goblin":
            self.max_hp = 30
            self.hp = 30
            self.damage = 8
            self.range = 1
            self.move_range = 2
            self.color = GREEN
        elif enemy_type == "skeleton":
            self.max_hp = 40
            self.hp = 40
            self.damage = 10
            self.range = 1
            self.move_range = 2
            self.color = GRAY
        elif enemy_type == "orc":
            self.max_hp = 60
            self.hp = 60
            self.damage = 15
            self.range = 1
            self.move_range = 1
            self.color = BROWN
        
        self.acted = False

# 道具类
class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.item_type = item_type
        if item_type == "health":
            self.color = GREEN
            self.name = "治疗药水"
        elif item_type == "damage":
            self.color = RED
            self.name = "力量卷轴"
        elif item_type == "maxhp":
            self.color = PURPLE
            self.name = "生命宝石"

# 生成关卡
def generate_level(level):
    grid = [[1 for _ in range(GRID_WIDTH) for _ in range(GRID_HEIGHT)]
    
    for x in range(1, GRID_WIDTH-1):
        for y in range(1, GRID_HEIGHT-1):
            if random.random() < 0.7:
                grid[y][x] = 0
    
    grid[1][1] = 0
    grid[GRID_HEIGHT-2][GRID_WIDTH-2] = 0
    
    enemies = []
    num_enemies = 2 + level
    enemy_types = ["goblin", "skeleton", "orc"]
    for _ in range(num_enemies):
        ex, ey = random.randint(3, GRID_WIDTH-3), random.randint(3, GRID_HEIGHT-3)
        while grid[ey][ex] == 0:
            enemies.append(Enemy(ex, ey, random.choice(enemy_types)))
            break
    
    items = []
    num_items = random.randint(1, 2)
    item_types = ["health", "damage", "maxhp"]
    for _ in range(num_items):
        ix, iy = random.randint(2, GRID_WIDTH-2), random.randint(2, GRID_HEIGHT-2)
        while grid[iy][ix] == 0:
            items.append(Item(ix, iy, random.choice(item_types)))
            break
    
    return grid, enemies, items

# 游戏状态
class GameState:
    def __init__(self):
        self.state = "class_select"
        self.player = None
        self.level = 1
        self.grid = []
        self.enemies = []
        self.items = []
        self.turn = "player"
        self.message = ""
        self.selected_player = None
        self.action_mode = "move"
        self.highlighted = []
        self.game_over = False
    
    def start_level(self):
        self.grid, self.enemies, self.items = generate_level(self.level)
        if self.player:
            self.player.x = 1
            self.player.y = 1
            self.player.acted = False
            self.player.moved = False
        self.turn = "player"
    
    def reset(self):
        self.__init__()

game = GameState()

# 辅助函数
def get_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

def draw_grid(surface, grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            color = DARK_GRAY if grid[y][x] == 1 else LIGHT_GRAY
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)

def draw_highlighted(surface, highlighted, color):
    for (x, y) in highlighted:
        rect = (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        s.fill((*color, 100))
        surface.blit(s, (x*TILE_SIZE, y*TILE_SIZE))

def draw_player(surface, player):
    rect = (player.x * TILE_SIZE + 5, player.y * TILE_SIZE + 5, 
            TILE_SIZE - 10, TILE_SIZE - 10)
    pygame.draw.ellipse(surface, player.color, rect)
    hp_ratio = player.hp / player.max_hp
    pygame.draw.rect(surface, DARK_GRAY, (player.x*TILE_SIZE, player.y*TILE_SIZE - 8, TILE_SIZE, 6))
    pygame.draw.rect(surface, GREEN, (player.x*TILE_SIZE, player.y*TILE_SIZE - 8, TILE_SIZE*hp_ratio, 6))

def draw_enemy(surface, enemy):
    rect = (enemy.x * TILE_SIZE + 5, enemy.y * TILE_SIZE + 5, 
            TILE_SIZE - 10, TILE_SIZE - 10)
    pygame.draw.ellipse(surface, enemy.color, rect)
    hp_ratio = enemy.hp / enemy.max_hp
    pygame.draw.rect(surface, DARK_GRAY, (enemy.x*TILE_SIZE, enemy.y*TILE_SIZE - 8, TILE_SIZE, 6))
    pygame.draw.rect(surface, RED, (enemy.x*TILE_SIZE, enemy.y*TILE_SIZE - 8, TILE_SIZE*hp_ratio, 6))

def draw_item(surface, item):
    rect = (item.x * TILE_SIZE + 10, item.y * TILE_SIZE + 10, 20, 20)
    pygame.draw.rect(surface, item.color, rect)

# 主循环
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            gx = mx // TILE_SIZE
            gy = my // TILE_SIZE
            
            if game.state == "class_select":
                if 200 &lt; mx &lt; 350 and 300 &lt; my &lt; 400:
                    game.player = Player("warrior", 1, 1)
                    game.state = "playing"
                    game.start_level()
                    game.message = "选择你的回合"
                elif 325 &lt; mx &lt; 475 and 300 &lt; my &lt; 400:
                    game.player = Player("archer", 1, 1)
                    game.state = "playing"
                    game.start_level()
                    game.message = "选择你的回合"
                elif 450 &lt; mx &lt; 600 and 300 &lt; my &lt; 400:
                    game.player = Player("mage", 1, 1)
                    game.state = "playing"
                    game.start_level()
                    game.message = "选择你的回合"
            
            elif game.state == "playing" and game.turn == "player" and not game.game_over:
                if gx &lt; GRID_WIDTH and gy &lt; GRID_HEIGHT:
                    if (gx, gy) in game.highlighted:
                        if game.action_mode == "move":
                            game.player.x = gx
                            game.player.y = gy
                            game.player.moved = True
                            game.highlighted = []
                            game.action_mode = "attack"
                            game.message = "选择攻击目标"
                        elif game.action_mode == "attack":
                            for enemy in game.enemies[:]:
                                if enemy.x == gx and enemy.y == gy:
                                    enemy.hp -= game.player.damage
                                    if enemy.hp &lt;= 0:
                                        game.enemies.remove(enemy)
                                        game.message = "击杀敌人！"
                                    else:
                                        game.message = f"造成 {game.player.damage} 点伤害"
                                    game.player.acted = True
                                    game.highlighted = []
                                    break
                        
                        for item in game.items[:]:
                            if item.x == gx and item.y == gy:
                                if item.item_type == "health":
                                    game.player.hp = min(game.player.hp + 30, game.player.max_hp)
                                    game.message = "恢复 30 HP"
                                elif item.item_type == "damage":
                                    game.player.damage += 5
                                    game.message = "伤害 +5"
                                elif item.item_type == "maxhp":
                                    game.player.max_hp += 20
                                    game.player.hp += 20
                                    game.message = "最大生命 +20"
                                game.items.remove(item)
                    
                    if game.player.x == gx and game.player.y == gy and not (game.player.acted and game.player.moved):
                        if not game.player.moved:
                            game.action_mode = "move"
                            game.highlighted = []
                            for x in range(GRID_WIDTH):
                                for y in range(GRID_HEIGHT):
                                    if get_distance(game.player.x, game.player.y, x, y) &lt;= game.player.move_range and game.grid[y][x] == 0:
                                        game.highlighted.append((x, y))
                            game.message = "选择移动位置"
                        elif not game.player.acted:
                            game.action_mode = "attack"
                            game.highlighted = []
                            for enemy in game.enemies:
                                if get_distance(game.player.x, game.player.y, enemy.x, enemy.y) &lt;= game.player.range:
                                    game.highlighted.append((enemy.x, enemy.y))
                            for item in game.items:
                                if get_distance(game.player.x, game.player.y, item.x, item.y) &lt;= game.player.range:
                                    game.highlighted.append((item.x, item.y))
                            game.message = "选择攻击/拾取目标"
                    
                    if game.player.x == gx and game.player.y == gy and game.player.acted and game.player.moved:
                        game.turn = "enemy"
                        game.message = "敌人回合"
        
        if event.type == pygame.KEYDOWN:
            if game.state == "playing" and game.turn == "player":
                if event.key == pygame.K_SPACE:
                    if game.player.acted and game.player.moved:
                        game.turn = "enemy"
                        game.message = "敌人回合"
                    else:
                        game.player.acted = True
                        game.player.moved = True
                        game.highlighted = []
                        game.message = "结束回合"
                elif event.key == pygame.K_ESCAPE:
                    game.highlighted = []
                    game.message = ""
    
    if game.state == "class_select":
        title = font_large.render("选择职业", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        warrior_rects = [(200, 300, 150, 100), (325, 300, 150, 100), (450, 300, 150, 100)]
        for i, (class_id, stats) in enumerate(CLASSES.items()):
            pygame.draw.rect(screen, stats["color"], warrior_rects[i])
            name = font_small.render(stats["name"], True, WHITE)
            screen.blit(name, (warrior_rects[i][0] + 40, warrior_rects[i][1] + 30))
            desc = font_small.render(stats["desc"], True, LIGHT_GRAY)
            screen.blit(desc, (warrior_rects[i][0] + 20, warrior_rects[i][1] + 60))
    
    elif game.state == "playing":
        if game.turn == "enemy" and not game.game_over:
            for enemy in game.enemies:
                dist = get_distance(enemy.x, enemy.y, game.player.x, game.player.y)
                if dist &lt;= enemy.range:
                    game.player.hp -= enemy.damage
                    game.message = f"受到 {enemy.damage} 点伤害"
                else:
                    dx = 1 if game.player.x &gt; enemy.x else -1
                    dy = 1 if game.player.y &gt; enemy.y else -1
                    for _ in range(enemy.move_range):
                        nx, ny = enemy.x + dx, enemy.y
                        if 0 &lt;= nx &lt; GRID_WIDTH and game.grid[ny][nx] == 0:
                            enemy.x = nx
                        else:
                            ny = enemy.y + dy
                            if 0 &lt;= ny &lt; GRID_HEIGHT and game.grid[ny][enemy.x] == 0:
                                enemy.y = ny
            
            if game.player.hp &lt;= 0:
                game.game_over = True
                game.state = "gameover"
            elif len(game.enemies) == 0:
                game.level += 1
                if game.level &gt; 5:
                    game.state = "victory"
                else:
                    game.start_level()
                    game.message = "进入第 {} 层".format(game.level)
            else:
                game.turn = "player"
                game.player.acted = False
                game.player.moved = False
        
        draw_grid(screen, game.grid)
        
        if game.highlighted:
            color = BLUE if game.action_mode == "move" else RED
            draw_highlighted(screen, game.highlighted, color)
        
        for item in game.items:
            draw_item(screen, item)
        
        for enemy in game.enemies:
            draw_enemy(screen, enemy)
        
        if game.player:
            draw_player(screen, game.player)
        
        ui_x = GRID_WIDTH * TILE_SIZE
        pygame.draw.rect(screen, DARK_GRAY, (ui_x, 0, WIDTH - ui_x, HEIGHT))
        if game.player:
            name = font_medium.render(game.player.name, True, WHITE)
            screen.blit(name, (ui_x + 20, 20))
            hp = font_small.render(f"HP: {game.player.hp}/{game.player.max_hp}", True, GREEN)
            screen.blit(hp, (ui_x + 20, 60))
            dmg = font_small.render(f"伤害: {game.player.damage}", True, RED)
            screen.blit(dmg, (ui_x + 20, 90))
            level = font_small.render(f"层数: {game.level}", True, GOLD)
            screen.blit(level, (ui_x + 20, 120))
        
        msg = font_small.render(game.message, True, WHITE)
        screen.blit(msg, (20, HEIGHT - 40))
        
        instr = font_small.render("点击角色开始行动", True, GRAY)
        screen.blit(instr, (20, HEIGHT - 70))
    
    elif game.state == "gameover":
        title = font_large.render("游戏结束", True, RED)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        level_text = font_medium.render(f"到达第 {game.level} 层", True, WHITE)
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, 280))
        restart = font_medium.render("点击重新开始", True, GOLD)
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 350))
        if pygame.mouse.get_pressed()[0]:
            game.reset()
    
    elif game.state == "victory":
        title = font_large.render("胜利！", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        victory_text = font_medium.render("你征服了地牢！", True, WHITE)
        screen.blit(victory_text, (WIDTH//2 - victory_text.get_width()//2, 280))
        restart = font_medium.render("点击再来一局", True, GOLD)
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 350))
        if pygame.mouse.get_pressed()[0]:
            game.reset()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
