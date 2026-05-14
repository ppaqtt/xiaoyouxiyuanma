import pygame
import random

pygame.init()

WIDTH, HEIGHT = 700, 600
GRID_SIZE = 50
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("时间循环解谜")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
big_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 22)

class Character:
    def __init__(self, x, y, color, name):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.moves = []
        self.current_move = 0
        self.active = True

class Level:
    def __init__(self, num):
        self.num = num
        
        if num == 1:
            self.char1 = Character(1, 1, GREEN, "A")
            self.char2 = Character(1, 3, BLUE, "B")
            self.goals = [(5, 5), (7, 5)]
            self.walls = [(3, 2), (3, 3), (3, 4)]
            self.description = "让两个角色交换位置"
        elif num == 2:
            self.char1 = Character(1, 1, GREEN, "A")
            self.char2 = Character(1, 3, BLUE, "B")
            self.goals = [(7, 3), (7, 1)]
            self.walls = [(4, 1), (4, 2), (4, 3)]
            self.description = "同时到达各自目标"
        elif num == 3:
            self.char1 = Character(1, 2, GREEN, "A")
            self.char2 = Character(1, 4, BLUE, "B")
            self.char3 = Character(7, 2, RED, "C")
            self.goals = [(7, 4), (7, 2), (1, 4)]
            self.walls = [(3, 1), (3, 2), (3, 3), (5, 3), (5, 4), (5, 5)]
            self.description = "三角交换"
        elif num == 4:
            self.char1 = Character(1, 1, GREEN, "A")
            self.char2 = Character(1, 5, BLUE, "B")
            self.goals = [(7, 5), (7, 1)]
            self.walls = [(3, 0), (3, 1), (3, 2), (3, 3), (5, 3), (5, 4), (5, 5), (5, 6)]
            self.description = "配合通过"
        else:
            self.char1 = Character(0, 3, GREEN, "A")
            self.char2 = Character(3, 0, BLUE, "B")
            self.char3 = Character(3, 6, RED, "C")
            self.goals = [(6, 0), (6, 3), (6, 6)]
            self.walls = [(2, 2), (2, 3), (2, 4), (4, 2), (4, 3), (4, 4)]
            self.description = "最终挑战"

def time_loop_puzzle():
    current_level = 1
    max_levels = 5
    
    while current_level <= max_levels:
        level = Level(current_level)
        
        recording = True
        characters = [level.char1, level.char2]
        if hasattr(level, 'char3'):
            characters.append(level.char3)
        
        chars_in_order = list(characters)
        
        running = True
        active_char_idx = 0
        game_won = False
        
        while running:
            screen.fill(BLACK)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        current_level = max_levels + 1
                    elif event.key == pygame.K_r:
                        for c in characters:
                            c.current_move = 0
                        recording = True
                        active_char_idx = 0
                        for c in characters:
                            c.x = level.char1.x if c == level.char1 else level.char2.x
                            c.y = level.char1.y if c == level.char1 else level.char2.y
                    elif event.key == pygame.K_SPACE:
                        if recording:
                            recording = False
                        else:
                            for c in characters:
                                c.current_move = 0
                                c.x = level.char1.x if c == level.char1 else level.char2.x
                                c.y = level.char1.y if c == level.char1 else level.char2.y
                            recording = True
                            active_char_idx = 0
                    elif recording:
                        current_char = chars_in_order[active_char_idx]
                        if event.key == pygame.K_w:
                            current_char.moves.append((0, -1))
                        elif event.key == pygame.K_s:
                            current_char.moves.append((0, 1))
                        elif event.key == pygame.K_a:
                            current_char.moves.append((-1, 0))
                        elif event.key == pygame.K_d:
                            current_char.moves.append((1, 0))
                        elif event.key == pygame.K_RETURN:
                            active_char_idx += 1
                            if active_char_idx >= len(chars_in_order):
                                recording = False
            
            if not recording:
                all_done = True
                for c in characters:
                    if c.current_move < len(c.moves):
                        all_done = False
                        dx, dy = c.moves[c.current_move]
                        new_x = c.x + dx
                        new_y = c.y + dy
                        
                        valid = True
                        if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
                            valid = False
                        for wall in level.walls:
                            if new_x == wall[0] and new_y == wall[1]:
                                valid = False
                        
                        if valid:
                            c.x = new_x
                            c.y = new_y
                        
                        c.current_move += 1
                
                if all_done:
                    game_won = True
            
            for wall in level.walls:
                pygame.draw.rect(screen, GRAY, 
                               (wall[0] * GRID_SIZE, wall[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            
            for i, goal in enumerate(level.goals):
                pygame.draw.rect(screen, GREEN, 
                               (goal[0] * GRID_SIZE + 5, goal[1] * GRID_SIZE + 5, 
                                GRID_SIZE - 10, GRID_SIZE - 10), 3)
            
            for c in characters:
                pygame.draw.circle(screen, c.color,
                               (int(c.x * GRID_SIZE + GRID_SIZE // 2),
                                int(c.y * GRID_SIZE + GRID_SIZE // 2)),
                               20)
                
                name = small_font.render(c.name, True, WHITE)
                screen.blit(name, (int(c.x * GRID_SIZE + GRID_SIZE // 2 - 8),
                                  int(c.y * GRID_SIZE + GRID_SIZE // 2 - 8)))
            
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    pygame.draw.rect(screen, (30, 30, 30), 
                                   (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)
            
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 50))
            
            level_text = font.render(f"关卡 {current_level}/{max_levels}", True, YELLOW)
            screen.blit(level_text, (10, 15))
            
            desc = small_font.render(level.description, True, WHITE)
            screen.blit(desc, (200, 15))
            
            status = "录制中 - " + chars_in_order[active_char_idx].name if recording else "播放中"
            status_color = GREEN if recording else BLUE
            status_text = font.render(status, True, status_color)
            screen.blit(status_text, (500, 15))
            
            pygame.draw.rect(screen, BLACK, (0, HEIGHT - 80, WIDTH, 80))
            
            for i, c in enumerate(chars_in_order):
                moves_str = str(len(c.moves))
                color = GREEN if i == active_char_idx and recording else WHITE
                text = small_font.render(f"{c.name}: {moves_str}步", True, color)
                screen.blit(text, (10 + i * 150, HEIGHT - 70))
            
            inst = small_font.render("WASD移动 | 回车下一个角色 | 空格播放/重录 | R重置", True, WHITE)
            screen.blit(inst, (10, HEIGHT - 30))
            
            if game_won:
                running = False
                current_level += 1
            
            pygame.display.flip()
            clock.tick(30)
    
    screen.fill(BLACK)
    result = big_font.render("恭喜通关!", True, YELLOW)
    screen.blit(result, (WIDTH // 2 - 100, HEIGHT // 2 - 30))
    complete = font.render("你理解了时间的循环!", True, GREEN)
    screen.blit(complete, (WIDTH // 2 - 120, HEIGHT // 2 + 30))
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    time_loop_puzzle()
