"""
在线五子棋
支持双人对战和简单AI对战
"""

import pygame
import os
import random
import sys
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

WIDTH, HEIGHT = 700, 750
BOARD_SIZE = 15
CELL_SIZE = 40
MARGIN = 50
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("五子棋 ⚫")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (60, 60, 60)
BOARD_COLOR = (230, 200, 160)
PLAYER_BLACK = (20, 20, 20)
PLAYER_WHITE = (245, 245, 245)
BG_COLOR = (245, 242, 235)
HIGHLIGHT = (255, 100, 100)
WIN_COLOR = (100, 255, 100)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER = (100, 160, 210)

class Game:
    def __init__(self):
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 1
        self.game_over = False
        self.winner = 0
        self.win_line = []
        self.mode = "pvp"
        self.last_move = None
        self.hover_pos = None
        self.font = get_chinese_font(36)
        self.font_large = get_chinese_font(48)
        self.font_small = get_chinese_font(28)
        self.buttons = [
            {"text": "双人对战", "rect": pygame.Rect(100, 700, 120, 40), "action": "pvp"},
            {"text": "人机对战", "rect": pygame.Rect(250, 700, 120, 40), "action": "ai"},
            {"text": "重新开始", "rect": pygame.Rect(400, 700, 120, 40), "action": "restart"}
        ]
        self.ai_thinking = False
        self.ai_think_start = 0
    
    def reset(self):
        self.board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 1
        self.game_over = False
        self.winner = 0
        self.win_line = []
        self.last_move = None
        self.ai_thinking = False
    
    def get_board_pos(self, mouse_pos):
        x, y = mouse_pos
        board_x = x - MARGIN
        board_y = y - MARGIN
        
        if 0 <= board_x <= CELL_SIZE * (BOARD_SIZE - 1) and 0 <= board_y <= CELL_SIZE * (BOARD_SIZE - 1):
            col = round(board_x / CELL_SIZE)
            row = round(board_y / CELL_SIZE)
            col = max(0, min(BOARD_SIZE - 1, col))
            row = max(0, min(BOARD_SIZE - 1, row))
            return row, col
        return None, None
    
    def is_valid(self, row, col):
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and self.board[row][col] == 0
    
    def place_stone(self, row, col):
        if self.is_valid(row, col):
            self.board[row][col] = self.current_player
            self.last_move = (row, col)
            
            if self.check_win(row, col):
                self.game_over = True
                self.winner = self.current_player
            else:
                self.current_player = 3 - self.current_player
            return True
        return False
    
    def check_win(self, row, col):
        player = self.board[row][col]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1
            start_pos = (row, col)
            end_pos = (row, col)
            
            for i in range(1, 5):
                nx, ny = row + dx * i, col + dy * i
                if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and self.board[nx][ny] == player:
                    count += 1
                    end_pos = (nx, ny)
                else:
                    break
            
            for i in range(1, 5):
                nx, ny = row - dx * i, col - dy * i
                if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and self.board[nx][ny] == player:
                    count += 1
                    start_pos = (nx, ny)
                else:
                    break
            
            if count >= 5:
                self.win_line = (start_pos, end_pos)
                return True
        return False
    
    def evaluate_position(self, row, col, player):
        if self.board[row][col] != 0:
            return -1
        
        total_score = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            line = []
            for i in range(-4, 5):
                nx, ny = row + dx * i, col + dy * i
                if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                    line.append(self.board[nx][ny])
                else:
                    line.append(-1)
            
            score = self.evaluate_line(line, player)
            total_score += score
        
        return total_score
    
    def evaluate_line(self, line, player):
        opponent = 3 - player
        score = 0
        
        for i in range(len(line)):
            if line[i] == player:
                count = 1
                empty = 0
                
                for j in range(i + 1, len(line)):
                    if line[j] == player:
                        count += 1
                    elif line[j] == 0:
                        empty += 1
                        break
                    else:
                        break
                
                if count >= 5:
                    score += 100000
                elif count == 4 and empty == 1:
                    score += 10000
                elif count == 4:
                    score += 1000
                elif count == 3:
                    score += 100
                elif count == 2:
                    score += 10
        
        return score
    
    def ai_move(self):
        if self.current_player != 1 or self.mode != "ai":
            return
        
        self.ai_thinking = True
        self.ai_think_start = pygame.time.get_ticks()
        
        best_score = -1
        best_moves = []
        
        center = BOARD_SIZE // 2
        if self.board[center][center] == 0 and self.last_move is None:
            self.place_stone(center, center)
            self.ai_thinking = False
            return
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == 0:
                    dist = abs(row - center) + abs(col - center)
                    if dist > 6:
                        continue
                    
                    score = self.evaluate_position(row, col, 1)
                    if score > best_score:
                        best_score = score
                        best_moves = [(row, col)]
                    elif score == best_score:
                        best_moves.append((row, col))
        
        if best_moves:
            row, col = random.choice(best_moves)
            self.place_stone(row, col)
        
        self.ai_thinking = False
    
    def draw(self):
        screen.fill(BG_COLOR)
        
        pygame.draw.rect(screen, BOARD_COLOR, (MARGIN - 5, MARGIN - 5, 
                         CELL_SIZE * (BOARD_SIZE - 1) + 10, CELL_SIZE * (BOARD_SIZE - 1) + 10))
        
        for i in range(BOARD_SIZE):
            pygame.draw.line(screen, BLACK, 
                           (MARGIN + i * CELL_SIZE, MARGIN),
                           (MARGIN + i * CELL_SIZE, MARGIN + CELL_SIZE * (BOARD_SIZE - 1)))
            pygame.draw.line(screen, BLACK,
                           (MARGIN, MARGIN + i * CELL_SIZE),
                           (MARGIN + CELL_SIZE * (BOARD_SIZE - 1), MARGIN + i * CELL_SIZE))
        
        for i, j in [(3, 3), (3, 11), (11, 3), (11, 11), (7, 7)]:
            pygame.draw.circle(screen, BLACK, (MARGIN + j * CELL_SIZE, MARGIN + i * CELL_SIZE), 5)
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] != 0:
                    x = MARGIN + col * CELL_SIZE
                    y = MARGIN + row * CELL_SIZE
                    color = PLAYER_BLACK if self.board[row][col] == 1 else PLAYER_WHITE
                    
                    pygame.draw.circle(screen, color, (x, y), CELL_SIZE // 2 - 2)
                    
                    if self.board[row][col] == 1:
                        pygame.draw.circle(screen, (60, 60, 60), (x, y), CELL_SIZE // 2 - 2, 1)
                    else:
                        pygame.draw.circle(screen, GRAY, (x, y), CELL_SIZE // 2 - 2, 2)
        
        if self.last_move and not self.game_over:
            row, col = self.last_move
            x = MARGIN + col * CELL_SIZE
            y = MARGIN + row * CELL_SIZE
            pygame.draw.circle(screen, HIGHLIGHT, (x, y), CELL_SIZE // 4, 2)
        
        if self.win_line and self.game_over:
            start, end = self.win_line
            start_x = MARGIN + start[1] * CELL_SIZE
            start_y = MARGIN + start[0] * CELL_SIZE
            end_x = MARGIN + end[1] * CELL_SIZE
            end_y = MARGIN + end[0] * CELL_SIZE
            pygame.draw.line(screen, WIN_COLOR, (start_x, start_y), (end_x, end_y), 6)
        
        mode_text = "双人对战" if self.mode == "pvp" else "人机对战 (你执黑)"
        mode_surface = self.font_small.render(mode_text, True, DARK_GRAY)
        screen.blit(mode_surface, (20, 15))
        
        player_color = PLAYER_BLACK if self.current_player == 1 else PLAYER_WHITE
        player_text = "黑方回合" if self.current_player == 1 else "白方回合"
        text_surface = self.font_large.render(player_text, True, player_color)
        
        text_bg = pygame.Surface((text_surface.get_width() + 20, text_surface.get_height() + 10))
        text_bg.fill(BG_COLOR)
        text_bg.blit(text_surface, (10, 5))
        screen.blit(text_bg, (WIDTH - text_surface.get_width() - 40, 15))
        
        pygame.draw.circle(screen, player_color, (WIDTH - text_surface.get_width() - 55, 25), 15)
        
        for button in self.buttons:
            color = BUTTON_HOVER if button["rect"].collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
            pygame.draw.rect(screen, color, button["rect"], border_radius=8)
            text = self.font_small.render(button["text"], True, WHITE)
            screen.blit(text, (button["rect"].x + 10, button["rect"].y + 8))
        
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(WHITE)
            screen.blit(overlay, (0, 0))
            
            winner_name = "黑方" if self.winner == 1 else "白方"
            win_text = f"{winner_name} 获胜!" if self.winner != 0 else "平局!"
            text = self.font_large.render(win_text, True, WIN_COLOR if self.winner != 0 else DARK_GRAY)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
            
            hint = self.font_small.render("点击按钮重新开始", True, DARK_GRAY)
            screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 20))
        
        pygame.display.flip()
    
    def handle_click(self, pos):
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                if button["action"] == "pvp":
                    self.mode = "pvp"
                    self.reset()
                elif button["action"] == "ai":
                    self.mode = "ai"
                    self.reset()
                elif button["action"] == "restart":
                    self.reset()
                return
        
        if self.game_over or self.ai_thinking:
            return
        
        row, col = self.get_board_pos(pos)
        if row is not None and self.is_valid(row, col):
            if self.place_stone(row, col) and self.mode == "ai" and not self.game_over:
                self.ai_move()

def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                row, col = game.get_board_pos(event.pos)
                game.hover_pos = (row, col) if row is not None and game.is_valid(row, col) else None
        
        game.draw()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
