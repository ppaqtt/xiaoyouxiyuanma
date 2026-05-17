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

WIDTH, HEIGHT = 700, 600
GRID_SIZE = 50

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
ORANGE = (255, 165, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("推箱子变种")
clock = pygame.time.Clock()
font = get_chinese_font(28)
big_font = get_chinese_font(50)
small_font = get_chinese_font(22)

LEVELS = [
    {
        "map": [
            "########",
            "#      #",
            "# $ @  #",
            "#  .   #",
            "#      #",
            "########",
        ],
        "name": "第一关"
    },
    {
        "map": [
            "########",
            "#   #  #",
            "# $ $  #",
            "# #. . #",
            "#   @  #",
            "########",
        ],
        "name": "第二关"
    },
    {
        "map": [
            "  #####",
            "###   #",
            "#.$@$ #",
            "#.#.###",
            "#.  $ #",
            "##### #",
            "    # #",
            "    # #",
            "    ###",
        ],
        "name": "第三关"
    },
    {
        "map": [
            "##########",
            "#        #",
            "# $$ ##  #",
            "# $  $ # #",
            "# .. .# #",
            "# $  $   #",
            "#  ##$ $ #",
            "###    ###",
            "  # @  #",
            "  ######",
        ],
        "name": "第四关"
    },
]

class Sokoban:
    def __init__(self, level_data):
        self.parse_level(level_data)
        self.moves = 0
        self.history = []
        self.pushes = 0
    
    def parse_level(self, level_data):
        self.grid = []
        self.player_pos = None
        self.targets = []
        self.boxes = []
        
        for y, line in enumerate(level_data["map"]):
            row = []
            for x, char in enumerate(line):
                if char == "#":
                    row.append("#")
                elif char == ".":
                    row.append(".")
                    self.targets.append((x, y))
                elif char == "$":
                    row.append(" ")
                    self.boxes.append((x, y))
                elif char == "@":
                    row.append(" ")
                    self.player_pos = (x, y)
                elif char == "+":
                    row.append(".")
                    self.targets.append((x, y))
                    self.boxes.append((x, y))
                else:
                    row.append(" ")
            self.grid.append(row)
    
    def move(self, dx, dy):
        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy
        
        if self.grid[new_y][new_x] == "#":
            return False
        
        if (new_x, new_y) in self.boxes:
            box_new_x = new_x + dx
            box_new_y = new_y + dy
            
            if self.grid[box_new_y][box_new_x] == "#":
                return False
            if (box_new_x, box_new_y) in self.boxes:
                return False
            
            self.boxes.remove((new_x, new_y))
            self.boxes.append((box_new_x, box_new_y))
            self.pushes += 1
        
        self.history.append({
            'player': self.player_pos,
            'boxes': list(self.boxes)
        })
        
        self.player_pos = (new_x, new_y)
        self.moves += 1
        return True
    
    def undo(self):
        if self.history:
            state = self.history.pop()
            self.player_pos = state['player']
            self.boxes = state['boxes']
            self.moves = max(0, self.moves - 1)
    
    def check_win(self):
        return all(target in self.boxes for target in self.targets)
    
    def draw(self):
        screen.fill(BLACK)
        
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == "#":
                    pygame.draw.rect(screen, BROWN, 
                                   (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                elif cell == ".":
                    pygame.draw.rect(screen, (50, 50, 50),
                                   (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
                    pygame.draw.circle(screen, GREEN,
                                     (x * GRID_SIZE + GRID_SIZE // 2,
                                      y * GRID_SIZE + GRID_SIZE // 2),
                                     10)
        
        for box in self.boxes:
            if box in self.targets:
                pygame.draw.rect(screen, GREEN,
                               (box[0] * GRID_SIZE + 5, box[1] * GRID_SIZE + 5,
                                GRID_SIZE - 10, GRID_SIZE - 10))
            else:
                pygame.draw.rect(screen, ORANGE,
                               (box[0] * GRID_SIZE + 5, box[1] * GRID_SIZE + 5,
                                GRID_SIZE - 10, GRID_SIZE - 10))
        
        if self.player_pos:
            pygame.draw.circle(screen, BLUE,
                             (self.player_pos[0] * GRID_SIZE + GRID_SIZE // 2,
                              self.player_pos[1] * GRID_SIZE + GRID_SIZE // 2),
                             GRID_SIZE // 3)

def sokoban_variants():
    current_level = 0
    levels_completed = 0
    
    while current_level < len(LEVELS):
        level = LEVELS[current_level]
        game = Sokoban(level)
        
        running = True
        won = False
        
        while running:
            screen.fill(BLACK)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game = Sokoban(level)
                    elif event.key == pygame.K_u:
                        game.undo()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        current_level = len(LEVELS)
                        break
                    elif not won:
                        if event.key in (pygame.K_UP, pygame.K_w):
                            game.move(0, -1)
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            game.move(0, 1)
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            game.move(-1, 0)
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            game.move(1, 0)
            
            if game.check_win():
                won = True
                levels_completed += 1
                
                screen.fill(GREEN)
                win_text = big_font.render("过关!", True, WHITE)
                screen.blit(win_text, (WIDTH // 2 - 80, HEIGHT // 2 - 30))
                
                stats = font.render(f"步数: {game.moves}  推箱子: {game.pushes}", True, BLACK)
                screen.blit(stats, (WIDTH // 2 - 100, HEIGHT // 2 + 30))
                
                next_text = font.render("按空格进入下一关", True, BLACK)
                screen.blit(next_text, (WIDTH // 2 - 100, HEIGHT // 2 + 80))
                
                pygame.display.flip()
                
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                current_level += 1
                                waiting = False
                                running = False
                            elif event.key == pygame.K_r:
                                waiting = False
            else:
                game.draw()
                
                pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 50))
                
                title = font.render(f"{level['name']}", True, YELLOW)
                screen.blit(title, (10, 15))
                
                stats_text = font.render(f"步数: {game.moves}  推: {game.pushes}", True, WHITE)
                screen.blit(stats_text, (200, 15))
                
                remaining = len([t for t in game.targets if t in game.boxes])
                progress = font.render(f"目标: {remaining}/{len(game.targets)}", True, GREEN)
                screen.blit(progress, (450, 15))
                
                inst = small_font.render("WASD/方向键移动 | U撤销 | R重试 | ESC返回", True, WHITE)
                screen.blit(inst, (10, HEIGHT - 30))
                
                pygame.display.flip()
                clock.tick(60)
    
    screen.fill(BLACK)
    result = big_font.render("恭喜全部通关!", True, YELLOW)
    screen.blit(result, (WIDTH // 2 - 150, HEIGHT // 2 - 50))
    
    complete = font.render(f"完成 {levels_completed} 个关卡!", True, GREEN)
    screen.blit(complete, (WIDTH // 2 - 100, HEIGHT // 2 + 20))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    sokoban_variants()
