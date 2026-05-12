import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("飞行棋")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)

COLORS = ["红", "黄", "蓝", "绿"]
START_POSITIONS = [0, 13, 26, 39]

class Piece:
    def __init__(self, color, position):
        self.color = color
        self.position = position
        self.start_position = START_POSITIONS[COLORS.index(color)]
        self.finished = False
    
    def can_move(self, dice, board):
        if self.finished:
            return False
        if self.position == -1:
            return dice == 6
        new_pos = self.position + dice
        if new_pos >= 52:
            return new_pos == 52
        return True
    
    def move(self, dice, board):
        if self.position == -1:
            self.position = self.start_position
        else:
            self.position = (self.position + dice) % 52
            if self.position == self.start_position:
                self.finished = True

def roll_dice():
    return random.randint(1, 6)

def play():
    players = []
    for i in range(4):
        players.append({
            'pieces': [Piece(COLORS[i], -1) for _ in range(4)],
            'color': COLORS[i],
            'finished': 0
        })
    
    current_player = 0
    consecutive_sixes = 0
    game_over = False
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    dice = roll_dice()
                    
                    text = font.render(f"玩家 {players[current_player]['color']} 掷出: {dice}", True, WHITE)
                    screen.fill(BLACK)
                    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
                    pygame.display.update()
                    pygame.time.wait(1000)
                    
                    if dice == 6:
                        consecutive_sixes += 1
                        if consecutive_sixes >= 3:
                            consecutive_sixes = 0
                            current_player = (current_player + 1) % 4
                            continue
                    else:
                        consecutive_sixes = 0
                    
                    moved = False
                    for piece in players[current_player]['pieces']:
                        if piece.can_move(dice, None):
                            piece.move(dice, None)
                            if piece.finished:
                                players[current_player]['finished'] += 1
                            moved = True
                            break
                    
                    if not moved or dice != 6:
                        current_player = (current_player + 1) % 4
                    
                    if players[current_player]['finished'] == 4:
                        game_over = True
        
        y_offset = 50
        for i, player in enumerate(players):
            player_text = font.render(f"{player['color']}: 完成 {player['finished']}/4", True, WHITE)
            screen.blit(player_text, (10, y_offset + i * 30))
        
        for i, player in enumerate(players):
            for piece in player['pieces']:
                piece_text = font.render(f"{player['color']}棋子位置: {piece.position if piece.position >= 0 else '起点'}", True, WHITE)
                screen.blit(piece_text, (10, y_offset + 150 + i * 30))
        
        current_text = font.render(f"当前玩家: {players[current_player]['color']}", True, GREEN)
        screen.blit(current_text, (WIDTH - 200, 10))
        
        instruction_text = font.render("按空格键掷骰子", True, WHITE)
        screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, HEIGHT - 50))
        
        if game_over:
            winner_text = font.render(f"玩家 {players[current_player]['color']} 获胜!", True, GREEN)
            screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, HEIGHT//2 - 50))
        
        pygame.display.update()
        clock.tick(30)
    
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    play()