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

WIDTH, HEIGHT = 300, 350
CELL_SIZE = 100

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 200)
RED = (200, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("井字棋 AI版")

clock = pygame.time.Clock()
font = get_chinese_font(40)

class TicTacToeAI:
    def __init__(self):
        self.board = [[0 for _ in range(3)] for _ in range(3)]
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.difficulty = "easy"
    
    def check_win(self, player):
        for row in range(3):
            if all(self.board[row][col] == player for col in range(3)):
                return True
        for col in range(3):
            if all(self.board[row][col] == player for row in range(3)):
                return True
        if self.board[0][0] == self.board[1][1] == self.board[2][2] == player:
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] == player:
            return True
        return False
    
    def is_full(self):
        return all(self.board[row][col] != 0 for row in range(3) for col in range(3))
    
    def minimax(self, depth, is_maximizing):
        if self.check_win(2):
            return 1
        if self.check_win(1):
            return -1
        if self.is_full():
            return 0
        
        if is_maximizing:
            best_score = -float('inf')
            for row in range(3):
                for col in range(3):
                    if self.board[row][col] == 0:
                        self.board[row][col] = 2
                        score = self.minimax(depth + 1, False)
                        self.board[row][col] = 0
                        best_score = max(best_score, score)
            return best_score
        else:
            best_score = float('inf')
            for row in range(3):
                for col in range(3):
                    if self.board[row][col] == 0:
                        self.board[row][col] = 1
                        score = self.minimax(depth + 1, True)
                        self.board[row][col] = 0
                        best_score = min(best_score, score)
            return best_score
    
    def make_ai_move(self):
        if self.difficulty == "easy":
            empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == 0]
            if empty:
                row, col = random.choice(empty)
                self.board[row][col] = 2
                self.current_player = 1
        else:
            best_score = -float('inf')
            best_move = None
            for row in range(3):
                for col in range(3):
                    if self.board[row][col] == 0:
                        self.board[row][col] = 2
                        score = self.minimax(0, False)
                        self.board[row][col] = 0
                        if score > best_score:
                            best_score = score
                            best_move = (row, col)
            if best_move:
                self.board[best_move[0]][best_move[1]] = 2
                self.current_player = 1
    
    def draw(self):
        screen.fill(BLACK)
        
        for i in range(1, 3):
            pygame.draw.line(screen, WHITE, (i * CELL_SIZE, 0), (i * CELL_SIZE, 300), 3)
            pygame.draw.line(screen, WHITE, (0, i * CELL_SIZE), (300, i * CELL_SIZE), 3)
        
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == 1:
                    pygame.draw.line(screen, BLUE,
                        (col * CELL_SIZE + 20, row * CELL_SIZE + 20),
                        (col * CELL_SIZE + CELL_SIZE - 20, row * CELL_SIZE + CELL_SIZE - 20), 4)
                    pygame.draw.line(screen, BLUE,
                        (col * CELL_SIZE + CELL_SIZE - 20, row * CELL_SIZE + 20),
                        (col * CELL_SIZE + 20, row * CELL_SIZE + CELL_SIZE - 20), 4)
                elif self.board[row][col] == 2:
                    pygame.draw.circle(screen, RED,
                        (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), 35, 4)
        
        if self.game_over:
            if self.winner == 1:
                text = "玩家获胜!"
            elif self.winner == 2:
                text = "电脑获胜!"
            else:
                text = "平局!"
            result = font.render(text, True, WHITE)
            screen.blit(result, (WIDTH // 2 - result.get_width() // 2, 310))
        else:
            turn_text = "玩家回合" if self.current_player == 1 else "电脑思考..."
            text = font.render(turn_text, True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 310))

def tictactoe_ai():
    game = TicTacToeAI()
    
    while True:
        game.draw()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
                if game.current_player == 1:
                    x, y = pygame.mouse.get_pos()
                    col = x // CELL_SIZE
                    row = y // CELL_SIZE
                    
                    if 0 <= row < 3 and 0 <= col < 3 and game.board[row][col] == 0:
                        game.board[row][col] = 1
                        
                        if game.check_win(1):
                            game.winner = 1
                            game.game_over = True
                        elif game.is_full():
                            game.winner = None
                            game.game_over = True
                        else:
                            game.current_player = 2
        
        if game.current_player == 2 and not game.game_over:
            pygame.display.update()
            pygame.time.wait(500)
            game.make_ai_move()
            
            if game.check_win(2):
                game.winner = 2
                game.game_over = True
            elif game.is_full():
                game.winner = None
                game.game_over = True
        
        pygame.display.update()
        clock.tick(30)

if __name__ == "__main__":
    tictactoe_ai()