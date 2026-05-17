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

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("密室逃脱")
clock = pygame.time.Clock()
font = get_chinese_font(28)
big_font = get_chinese_font(50)
small_font = get_chinese_font(22)

class Item:
    def __init__(self, name, description, icon):
        self.name = name
        self.description = description
        self.icon = icon
        self.collected = False

class Puzzle:
    def __init__(self, name, solution, hint):
        self.name = name
        self.solution = solution
        self.hint = hint
        self.solved = False

class Room:
    def __init__(self, name, description, items, puzzles, exits):
        self.name = name
        self.description = description
        self.items = items
        self.puzzles = puzzles
        self.exits = exits

class EscapeGame:
    def __init__(self):
        self.rooms = {
            "start": Room("起始房间", "你醒来发现自己在 一个昏暗的房间里。门被锁住了。",
                         [Item("钥匙", "一把生锈的钥匙", "🔑")],
                         [Puzzle("检查门", "钥匙", "门需要钥匙才能打开")],
                         {"north": "hallway"}),
            
            "hallway": Room("走廊", "一条长长的走廊，两侧有几幅画。",
                           [Item("画", "一幅奇怪的画", "🖼️")],
                           [Puzzle("移动画", "画", "画后面似乎有东西")],
                           {"south": "start", "north": "study", "east": "kitchen"}),
            
            "study": Room("书房", "一个充满书籍的房间，书架上落满灰尘。",
                         [Item("日记", "一本旧日记", "📔")],
                         [Puzzle("读日记", "日记", "日记里提到了密码")],
                         {"south": "hallway", "east": "library"}),
            
            "library": Room("图书馆", "巨大的书架占据了整面墙。",
                            [Item("密码本", "记录着密码的本子: 1234", "📕")],
                            [Puzzle("输入密码", "1234", "需要4位密码")],
                            {"west": "study"}),
            
            "kitchen": Room("厨房", "厨房里有一把刀和一些食材。",
                            [Item("锤子", "可以用来敲东西", "🔨")],
                            [Puzzle("敲地板", "锤子", "地板下面有空洞")],
                            {"west": "hallway", "north": "secret"}),
            
            "secret": Room("秘密房间", "你发现了隐藏的房间!",
                          [Item("钥匙卡", "打开最终门的钥匙卡", "💳")],
                          [],
                          {"south": "kitchen", "north": "exit"}),
            
            "exit": Room("出口", "这就是出口! 你自由了!",
                        [],
                        [Puzzle("使用钥匙卡", "钥匙卡", "需要钥匙卡才能离开")],
                        {}),
        }
        
        self.current_room = "start"
        self.inventory = []
        self.clues = []
        self.time_limit = 300
        self.start_time = pygame.time.get_ticks()
        self.game_over = False
        self.won = False
    
    def get_time_remaining(self):
        elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
        return max(0, self.time_limit - elapsed)
    
    def move_to(self, direction):
        room = self.rooms[self.current_room]
        if direction in room.exits:
            next_room = room.exits[direction]
            
            if next_room == "exit" and "钥匙卡" not in self.inventory:
                return "门被锁住了，需要钥匙卡!"
            
            if next_room == "secret":
                if "锤子" in self.inventory and "secret_found" not in self.clues:
                    self.clues.append("secret_found")
                    self.current_room = next_room
                    return "你用锤子敲开了隐藏的入口!"
                elif "secret_found" not in self.clues:
                    return "这里似乎有隐藏的东西..."
            
            self.current_room = next_room
            return f"你进入了{self.rooms[next_room].name}"
        return "你不能往那个方向走"
    
    def take_item(self, item_name):
        room = self.rooms[self.current_room]
        for item in room.items:
            if item.name == item_name and not item.collected:
                item.collected = True
                self.inventory.append(item_name)
                return f"你拿起了{item.icon} {item.name}"
        return "你找不到这个东西"
    
    def use_item(self, item_name):
        if item_name not in self.inventory:
            return "你没有这个东西"
        
        room = self.rooms[self.current_room]
        
        if item_name == "钥匙" and self.current_room == "start":
            if "门" in [p.name for p in room.puzzles]:
                self.won = True
                return "你用钥匙打开了门! 逃出去了!"
        
        if item_name == "钥匙卡" and self.current_room == "exit":
            self.won = True
            self.game_over = True
            return "你成功了! 自由了!"
        
        return f"现在不能使用{item_name}"
    
    def interact(self, target):
        room = self.rooms[self.current_room]
        
        if target == "画" and self.current_room == "hallway":
            if "secret_found" not in self.clues:
                self.clues.append("secret_found")
                return "画后面有一个暗格，里面有提示!"
        
        for puzzle in room.puzzles:
            if puzzle.name == target:
                if puzzle.name == "输入密码":
                    return "需要输入4位密码"
                elif puzzle.name == "使用钥匙卡" and "钥匙卡" in self.inventory:
                    self.won = True
                    self.game_over = True
                    return "你使用了钥匙卡! 成功了!"
        
        return f"你不能与{target}互动"

def escape_room():
    game = EscapeGame()
    
    while not game.game_over:
        screen.fill(BLACK)
        
        time_left = game.get_time_remaining()
        if time_left <= 0:
            game.game_over = True
            break
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.game_over = True
                elif event.key == pygame.K_w or event.key == pygame.K_UP:
                    msg = game.move_to("north")
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    msg = game.move_to("south")
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    msg = game.move_to("west")
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    msg = game.move_to("east")
                elif event.key == pygame.K_t:
                    if game.inventory:
                        item = game.inventory[-1]
                        msg = game.use_item(item)
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                    idx = event.key - 49
                    room = game.rooms[game.current_room]
                    available_items = [item for item in room.items if not item.collected]
                    if idx < len(available_items):
                        msg = game.take_item(available_items[idx].name)
                elif event.key == pygame.K_i:
                    msg = f"背包: {', '.join(game.inventory) if game.inventory else '空'}"
        
        room = game.rooms[game.current_room]
        
        pygame.draw.rect(screen, (20, 20, 40), (0, 0, WIDTH, 60))
        
        time_color = GREEN if time_left > 60 else YELLOW if time_left > 30 else RED
        time_text = font.render(f"剩余时间: {time_left}秒", True, time_color)
        screen.blit(time_text, (10, 20))
        
        room_name = font.render(f"位置: {room.name}", True, YELLOW)
        screen.blit(room_name, (250, 20))
        
        pygame.draw.rect(screen, (30, 30, 50), (0, 60, WIDTH, 150))
        
        desc_lines = []
        words = room.description.split()
        line = ""
        for word in words:
            if len(line + word) < 50:
                line += word + " "
            else:
                desc_lines.append(line)
                line = word + " "
        desc_lines.append(line)
        
        for i, line in enumerate(desc_lines[:3]):
            text = small_font.render(line, True, WHITE)
            screen.blit(text, (10, 70 + i * 25))
        
        available_items = [item for item in room.items if not item.collected]
        if available_items:
            items_text = small_font.render(f"可拾取: " + ", ".join([f"{i+1}.{item.name}" for i, item in enumerate(available_items)]), True, GREEN)
            screen.blit(items_text, (10, 180))
        
        pygame.draw.rect(screen, (40, 40, 60), (0, 220, WIDTH, 100))
        
        inventory_text = font.render(f"背包: {', '.join(game.inventory) if game.inventory else '(空)'}", True, YELLOW)
        screen.blit(inventory_text, (10, 230))
        
        if game.clues:
            clues_text = small_font.render(f"线索: {', '.join(game.clues)}", True, PURPLE)
            screen.blit(clues_text, (10, 270))
        
        exits = room.exits.keys()
        exits_text = font.render(f"出口: {', '.join([k for k in exits])}", True, WHITE)
        screen.blit(exits_text, (10, 300))
        
        pygame.draw.rect(screen, (50, 50, 70), (0, 330, WIDTH, 270))
        
        inst = small_font.render("WASD移动 | 1-5拾取物品 | T使用物品 | I查看背包 | ESC退出", True, WHITE)
        screen.blit(inst, (10, 340))
        
        if game.current_room == "exit":
            exit_msg = big_font.render("这是出口! 使用钥匙卡离开!", True, GREEN)
            screen.blit(exit_msg, (WIDTH // 2 - 200, 400))
        
        pygame.display.flip()
        clock.tick(60)
    
    screen.fill(BLACK)
    
    if game.won:
        result = big_font.render("恭喜逃脱成功!", True, GREEN)
        time_taken = 300 - game.get_time_remaining()
        stats = font.render(f"用时: {time_taken}秒", True, YELLOW)
    else:
        result = big_font.render("游戏结束!", True, RED)
        stats = font.render("时间耗尽了", True, WHITE)
    
    screen.blit(result, (WIDTH // 2 - 150, HEIGHT // 2 - 50))
    screen.blit(stats, (WIDTH // 2 - 80, HEIGHT // 2 + 20))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    escape_room()
