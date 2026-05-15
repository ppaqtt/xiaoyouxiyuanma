import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("密室逃脱")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)

class EscapeRoom:
    def __init__(self):
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        self.items = {"key": False, "map": False, "lamp": False}
        self.current_room = "entrance"
        
        self.rooms = {
            "entrance": {
                "description": "你被困在一个神秘的房间里。房间里有一扇锁着的门，一张桌子，和一幅画。",
                "items": ["key", "map"],
                "exits": {"right": "bedroom", "up": "kitchen"}
            },
            "bedroom": {
                "description": "这是一间卧室。有一张床，一个衣柜，和一扇窗户。窗户是锁着的。",
                "items": ["lamp"],
                "exits": {"left": "entrance"}
            },
            "kitchen": {
                "description": "厨房里面有一个冰箱，一个烤箱，和一些餐具。墙上挂着一把钥匙。",
                "items": [],
                "exits": {"down": "entrance"}
            }
        }

    def draw(self):
        screen.fill(BLACK)
        
        room = self.rooms[self.current_room]
        
        title_text = self.font.render("密室逃脱", True, BLUE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 30))
        
        room_text = self.font.render(f"当前房间: {self.current_room}", True, GREEN)
        screen.blit(room_text, (50, 80))
        
        text_lines = self.wrap_text(room["description"], 700)
        y = 130
        for line in text_lines:
            text = self.small_font.render(line, True, WHITE)
            screen.blit(text, (50, y))
            y += 30
        
        y += 20
        items_text = self.small_font.render("物品栏:", True, WHITE)
        screen.blit(items_text, (50, y))
        y += 25
        for item, found in self.items.items():
            color = GREEN if found else RED
            item_text = self.small_font.render(f"  {item}: {'已找到' if found else '未找到'}", True, color)
            screen.blit(item_text, (50, y))
            y += 20
        
        y += 20
        exit_text = self.small_font.render("出口方向:", True, WHITE)
        screen.blit(exit_text, (50, y))
        y += 25
        for direction, room_name in room["exits"].items():
            dir_text = {"left": "← 左边", "right": "→ 右边", "up": "↑ 上边", "down": "↓ 下边"}
            exit_text = self.small_font.render(f"  {dir_text[direction]}: {room_name}", True, BLUE)
            screen.blit(exit_text, (50, y))
            y += 20
        
        hint_text = self.small_font.render("使用方向键移动，空格键检查物品", True, GRAY)
        screen.blit(hint_text, (50, HEIGHT - 30))

    def wrap_text(self, text, max_width):
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            test_surface = self.small_font.render(test_line, True, WHITE)
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        
        lines.append(current_line)
        return lines

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            room = self.rooms[self.current_room]
            
            if event.key == pygame.K_LEFT and "left" in room["exits"]:
                self.current_room = room["exits"]["left"]
            elif event.key == pygame.K_RIGHT and "right" in room["exits"]:
                self.current_room = room["exits"]["right"]
            elif event.key == pygame.K_UP and "up" in room["exits"]:
                self.current_room = room["exits"]["up"]
            elif event.key == pygame.K_DOWN and "down" in room["exits"]:
                self.current_room = room["exits"]["down"]
            elif event.key == pygame.K_SPACE:
                for item in room["items"]:
                    if not self.items[item]:
                        self.items[item] = True
                        break
                
                if all(self.items.values()):
                    self.show_win()

    def show_win(self):
        screen.fill(BLACK)
        win_text = self.font.render("恭喜！你找到了所有物品，成功逃脱！", True, GREEN)
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, 250))
        pygame.display.flip()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

game = EscapeRoom()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.handle_input(event)
    
    game.draw()
    pygame.display.flip()

pygame.quit()