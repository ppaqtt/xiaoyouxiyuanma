import pygame
import os
import random

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

WIDTH, HEIGHT = 800, 800
TILE_SIZE = 80

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
PURPLE = (150, 50, 200)
BROWN = (139, 69, 19)
LIGHT_BROWN = (210, 180, 140)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("大富翁桌游")
clock = pygame.time.Clock()
font = get_chinese_font(28)
big_font = get_chinese_font(50)

class Tile:
    def __init__(self, name, tile_type, price=0, rent=0):
        self.name = name
        self.tile_type = tile_type
        self.price = price
        self.rent = rent
        self.owner = None
        self.houses = 0

class Player:
    def __init__(self, name, color, is_ai=False):
        self.name = name
        self.color = color
        self.money = 1500
        self.position = 0
        self.is_ai = is_ai
        self.properties = []
        self.in_jail = False
        self.jail_turns = 0
    
    def can_afford(self, amount):
        return self.money >= amount

def create_board():
    tiles = [
        Tile("起点", "start", rent=200),
        Tile("北京", "property", 600, 50),
        Tile("机会", "chance"),
        Tile("上海", "property", 600, 50),
        Tile("广州", "property", 400, 30),
        Tile("税务局", "tax", rent=100),
        Tile("深圳", "property", 650, 55),
        Tile("成都", "property", 500, 40),
        Tile("武汉", "property", 500, 40),
        Tile("西安", "property", 400, 30),
        Tile("免费停车", "free_parking"),
        Tile("重庆", "property", 550, 45),
        Tile("天津", "property", 550, 45),
        Tile("机会", "chance"),
        Tile("南京", "property", 600, 50),
        Tile("杭州", "property", 700, 60),
        Tile("税务局", "tax", rent=150),
        Tile("苏州", "property", 500, 40),
        Tile("青岛", "property", 400, 30),
        Tile("厦门", "property", 450, 35),
    ]
    return tiles

def draw_board(tiles, players, current_player_idx):
    screen.fill(LIGHT_BROWN)
    
    for i, tile in enumerate(tiles):
        row = i // 5
        col = i % 5
        
        if row == 0:
            x, y = WIDTH - (col + 1) * TILE_SIZE, HEIGHT - TILE_SIZE
        elif row == 1:
            x, y = TILE_SIZE, HEIGHT - (col + 2) * TILE_SIZE
        elif row == 2:
            x, y = col * TILE_SIZE, TILE_SIZE
        else:
            x, y = WIDTH - TILE_SIZE, (row - 2) * TILE_SIZE
        
        if tile.tile_type == "property":
            color = RED if "京" in tile.name else (GREEN if "圳" in tile.name else BLUE) if "州" in tile.name else YELLOW
            if tile.owner:
                color = tile.owner.color
        elif tile.tile_type == "tax":
            color = RED
        elif tile.tile_type == "chance":
            color = PURPLE
        else:
            color = GREEN
        
        pygame.draw.rect(screen, color, (x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4))
        pygame.draw.rect(screen, BLACK, (x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4), 2)
        
        name_text = font.render(tile.name[:3], True, WHITE)
        screen.blit(name_text, (x + 5, y + 5))
        
        if tile.owner:
            owner_marker = font.render("★", True, tile.owner.color)
            screen.blit(owner_marker, (x + 30, y + 25))
    
    for i, player in enumerate(players):
        tile = tiles[player.position]
        row = tile_index // 5
        col = tile_index = player.position
        
        if row == 0:
            x = WIDTH - (col + 1) * TILE_SIZE + TILE_SIZE // 2 + (i - len(players) // 2) * 15
            y = HEIGHT - TILE_SIZE + TILE_SIZE // 2
        elif row == 1:
            x = TILE_SIZE + TILE_SIZE // 2 + (i - len(players) // 2) * 15
            y = HEIGHT - (col + 2) * TILE_SIZE + TILE_SIZE // 2
        elif row == 2:
            x = col * TILE_SIZE + TILE_SIZE // 2 + (i - len(players) // 2) * 15
            y = TILE_SIZE + TILE_SIZE // 2
        else:
            x = WIDTH - TILE_SIZE + TILE_SIZE // 2 + (i - len(players) // 2) * 15
            y = (row - 2) * TILE_SIZE + TILE_SIZE // 2
        
        pygame.draw.circle(screen, player.color, (int(x), int(y)), 12)
        pygame.draw.circle(screen, WHITE, (int(x), int(y)), 12, 2)
        
        num = font.render(str(i + 1), True, BLACK)
        screen.blit(num, (int(x) - 5, int(y) - 8))

def draw_ui(current_player, tiles):
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 60))
    
    info = f"{current_player.name} - ${current_player.money} - 位置: {tiles[current_player.position].name}"
    text = font.render(info, True, WHITE)
    screen.blit(text, (10, 20))
    
    dice_text = font.render("按空格掷骰子", True, YELLOW)
    screen.blit(dice_text, (WIDTH - 150, 20))

def monopoly_style():
    tiles = create_board()
    
    player = Player("玩家", BLUE, is_ai=False)
    ai = Player("电脑", RED, is_ai=True)
    players = [player, ai]
    current_idx = 0
    game_over = False
    dice_value = 0
    waiting_for_roll = True
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and waiting_for_roll and not players[current_idx].is_ai:
                    dice_value = random.randint(1, 6)
                    players[current_idx].position = (players[current_idx].position + dice_value) % len(tiles)
                    waiting_for_roll = False
        
        if players[current_idx].is_ai and waiting_for_roll:
            pygame.time.wait(500)
            dice_value = random.randint(1, 6)
            players[current_idx].position = (players[current_idx].position + dice_value) % len(tiles)
            waiting_for_roll = False
            pygame.time.wait(300)
        
        if not waiting_for_roll:
            current_tile = tiles[players[current_idx].position]
            current_p = players[current_idx]
            
            if current_tile.tile_type == "property":
                if current_tile.owner is None and current_p.can_afford(current_tile.price):
                    if current_p.is_ai:
                        current_p.money -= current_tile.price
                        current_tile.owner = current_p
                        current_p.properties.append(current_tile)
                    else:
                        buy_text = font.render(f"购买 {current_tile.name}? (${current_tile.price}) 按Y购买, N跳过", True, YELLOW)
                        screen.blit(buy_text, (WIDTH // 2 - 200, HEIGHT // 2))
                        pygame.display.flip()
                        
                        waiting = True
                        while waiting:
                            for ev in pygame.event.get():
                                if ev.type == pygame.QUIT:
                                    return
                                elif ev.type == pygame.KEYDOWN:
                                    if ev.key == pygame.K_y:
                                        current_p.money -= current_tile.price
                                        current_tile.owner = current_p
                                        current_p.properties.append(current_tile)
                                        waiting = False
                                    elif ev.key == pygame.K_n:
                                        waiting = False
                elif current_tile.owner and current_tile.owner != current_p:
                    rent = current_tile.rent * (1 + current_tile.houses * 0.5)
                    current_p.money -= rent
                    current_tile.owner.money += rent
            
            elif current_tile.tile_type == "tax":
                current_p.money -= current_tile.tax if hasattr(current_tile, 'tax') else 100
            
            elif current_tile.tile_type == "start":
                current_p.money += 200
            
            elif current_tile.tile_type == "chance":
                chance = random.choice([-50, 50, -100, 100, 0])
                current_p.money += chance
            
            if current_p.money < 0:
                if current_p.is_ai:
                    game_over = True
            
            current_idx = (current_idx + 1) % len(players)
            waiting_for_roll = True
        
        draw_board(tiles, players, current_idx)
        draw_ui(players[current_idx], tiles)
        
        for i, p in enumerate(players):
            score = font.render(f"{p.name}: ${p.money}", True, p.color)
            screen.blit(score, (10, 70 + i * 30))
        
        if waiting_for_roll and not players[current_idx].is_ai:
            dice_text = font.render(f"骰子: {dice_value}" if dice_value > 0 else "按空格掷骰子", True, WHITE)
            screen.blit(dice_text, (WIDTH // 2 - 50, HEIGHT // 2))
        
        pygame.display.flip()
        clock.tick(30)
    
    screen.fill(BLACK)
    if not players[0].is_ai and players[0].money > 0:
        result = big_font.render("你赢了!", True, GREEN)
    else:
        result = big_font.render("电脑赢了!", True, RED)
    screen.blit(result, (WIDTH // 2 - 100, HEIGHT // 2))
    
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    monopoly_style()
