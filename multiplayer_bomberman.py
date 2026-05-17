import pygame
import os
import random
import sys
import struct
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

try:
    pygame.mixer.init()
    mixer_available = True
except Exception:
    mixer_available = False

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
TILE_SIZE = 40
GRID_WIDTH = 20
GRID_HEIGHT = 16
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("多人炸弹人 Multiplayer Bomberman")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
GRAY = (128, 128, 128)

EMPTY = 0
WALL = 1
BLOCK = 2
BOMB = 3
FIRE = 4
POWERUP_SPEED = 5
POWERUP_BOMB = 6
POWERUP_RANGE = 7

player_colors = [WHITE, RED, GREEN, YELLOW]

class SoundSystem:
    def __init__(self):
        self.sounds = {}
        if mixer_available:
            self.generate_sounds()
    
    def generate_sounds(self):
        try:
            self.sounds['place'] = self.generate_tone(440, 0.1, 'square')
            self.sounds['explode'] = self.generate_noise(0.3)
            self.sounds['powerup'] = self.generate_tone(880, 0.2, 'sine')
            self.sounds['death'] = self.generate_tone(220, 0.5, 'sawtooth')
        except Exception:
            pass
    
    def generate_tone(self, frequency, duration, wave_type='sine'):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        
        samples = []
        for i in range(n_samples):
            t = i / sample_rate
            if wave_type == 'sine':
                sample = math.sin(2 * math.pi * frequency * t)
            elif wave_type == 'square':
                sample = 1.0 if math.sin(2 * math.pi * frequency * t) > 0 else -1.0
            elif wave_type == 'sawtooth':
                sample = 2 * (t * frequency - math.floor(t * frequency + 0.5))
            else:
                sample = math.sin(2 * math.pi * frequency * t)
            
            envelope = max(0, 1 - i / n_samples)
            samples.append(int(32767 * sample * envelope))
        
        byte_data = bytearray()
        for sample in samples:
            byte_data.extend(struct.pack('<h', int(sample)))
        
        sound = pygame.mixer.Sound(byte_data)
        sound.set_volume(0.3)
        return sound
    
    def generate_noise(self, duration):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        
        samples = []
        for i in range(n_samples):
            sample = random.random() * 2 - 1
            envelope = max(0, 1 - i / n_samples)
            samples.append(int(32767 * sample * envelope))
        
        byte_data = bytearray()
        for sample in samples:
            byte_data.extend(struct.pack('<h', int(sample)))
        
        sound = pygame.mixer.Sound(byte_data)
        sound.set_volume(0.4)
        return sound
    
    def play(self, sound_name):
        if mixer_available and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except Exception:
                pass

sound_system = SoundSystem()

class Player:
    def __init__(self, x, y, color, controls, bomb_key, player_id):
        self.x = x
        self.y = y
        self.width = TILE_SIZE - 8
        self.height = TILE_SIZE - 8
        self.color = color
        self.controls = controls
        self.bomb_key = bomb_key
        self.player_id = player_id
        self.bombs = 1
        self.bombs_left = 1
        self.fire_range = 1
        self.speed = 3
        self.alive = True
    
    def get_grid_pos(self):
        return (self.x + TILE_SIZE // 2) // TILE_SIZE, (self.y + TILE_SIZE // 2) // TILE_SIZE

class Bomb:
    def __init__(self, x, y, fire_range, owner_id):
        self.grid_x = x
        self.grid_y = y
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.fire_range = fire_range
        self.timer = 180
        self.owner_id = owner_id

class PowerUp:
    def __init__(self, x, y, type):
        self.grid_x = x
        self.grid_y = y
        self.type = type
        self.alive = True

class Game:
    def __init__(self, num_players):
        self.state = 'playing'
        self.num_players = num_players
        self.grid = self.create_map()
        self.players = self.create_players()
        self.bombs = []
        self.fires = []
        self.powerups = []
        self.winner = None
    
    def create_map(self):
        grid = []
        for y in range(GRID_HEIGHT):
            row = []
            for x in range(GRID_WIDTH):
                if x == 0 or x == GRID_WIDTH - 1 or y == 0 or y == GRID_HEIGHT - 1:
                    row.append(WALL)
                elif x % 2 == 0 and y % 2 == 0:
                    row.append(WALL)
                elif (x <= 2 and y <= 2) or (x >= GRID_WIDTH - 3 and y <= 2) or \
                     (x <= 2 and y >= GRID_HEIGHT - 3) or (x >= GRID_WIDTH - 3 and y >= GRID_HEIGHT - 3):
                    row.append(EMPTY)
                else:
                    if random.random() < 0.6:
                        row.append(BLOCK)
                    else:
                        row.append(EMPTY)
            grid.append(row)
        return grid
    
    def create_players(self):
        players = []
        start_positions = [
            (TILE_SIZE + 2, TILE_SIZE + 2),
            ((GRID_WIDTH - 2) * TILE_SIZE + 2, TILE_SIZE + 2),
            (TILE_SIZE + 2, (GRID_HEIGHT - 2) * TILE_SIZE + 2),
            ((GRID_WIDTH - 2) * TILE_SIZE + 2, (GRID_HEIGHT - 2) * TILE_SIZE + 2)
        ]
        controls_list = [
            (pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d),
            (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT),
            (pygame.K_i, pygame.K_k, pygame.K_j, pygame.K_l),
            (pygame.K_t, pygame.K_g, pygame.K_f, pygame.K_h)
        ]
        bomb_keys = [pygame.K_SPACE, pygame.K_RETURN, pygame.K_o, pygame.K_y]
        
        for i in range(self.num_players):
            x, y = start_positions[i]
            players.append(Player(x, y, player_colors[i], controls_list[i], bomb_keys[i], i))
        return players
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        for player in self.players:
            if not player.alive:
                continue
            
            dx, dy = 0, 0
            up, down, left, right = player.controls
            
            if keys[left]:
                dx = -player.speed
            if keys[right]:
                dx = player.speed
            if keys[up]:
                dy = -player.speed
            if keys[down]:
                dy = player.speed
            
            new_x = player.x + dx
            new_y = player.y + dy
            
            if not self.check_collision(new_x, player.y, player):
                player.x = new_x
            if not self.check_collision(player.x, new_y, player):
                player.y = new_y
    
    def check_collision(self, x, y, player):
        rect = pygame.Rect(x, y, player.width, player.height)
        
        for grid_y in range(GRID_HEIGHT):
            for grid_x in range(GRID_WIDTH):
                if self.grid[grid_y][grid_x] in [WALL, BLOCK]:
                    tile_rect = pygame.Rect(grid_x * TILE_SIZE, grid_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if rect.colliderect(tile_rect):
                        return True
        
        for bomb in self.bombs:
            bomb_rect = pygame.Rect(bomb.x, bomb.y, TILE_SIZE, TILE_SIZE)
            if rect.colliderect(bomb_rect):
                return True
        
        return False
    
    def place_bomb(self, player):
        grid_x, grid_y = player.get_grid_pos()
        if player.bombs_left > 0 and self.grid[grid_y][grid_x] == EMPTY:
            self.grid[grid_y][grid_x] = BOMB
            self.bombs.append(Bomb(grid_x, grid_y, player.fire_range, player.player_id))
            player.bombs_left -= 1
            sound_system.play('place')
    
    def update(self):
        for bomb in self.bombs[:]:
            bomb.timer -= 1
            if bomb.timer <= 0:
                self.explode(bomb)
        
        for fire in self.fires[:]:
            fire[2] -= 1
            if fire[2] <= 0:
                self.fires.remove(fire)
                if self.grid[fire[1]][fire[0]] == FIRE:
                    self.grid[fire[1]][fire[0]] = EMPTY
        
        for player in self.players:
            if not player.alive:
                continue
            
            grid_x, grid_y = player.get_grid_pos()
            if self.grid[grid_y][grid_x] == FIRE:
                player.alive = False
                sound_system.play('death')
            
            for powerup in self.powerups[:]:
                if powerup.alive and powerup.grid_x == grid_x and powerup.grid_y == grid_y:
                    powerup.alive = False
                    sound_system.play('powerup')
                    if powerup.type == POWERUP_SPEED:
                        player.speed = min(6, player.speed + 1)
                    elif powerup.type == POWERUP_BOMB:
                        player.bombs += 1
                        player.bombs_left += 1
                    elif powerup.type == POWERUP_RANGE:
                        player.fire_range += 1
        
        alive_players = [p for p in self.players if p.alive]
        if len(alive_players) <= 1:
            self.state = 'gameover'
            if len(alive_players) == 1:
                self.winner = alive_players[0]
    
    def explode(self, bomb):
        self.grid[bomb.grid_y][bomb.grid_x] = FIRE
        self.fires.append([bomb.grid_x, bomb.grid_y, 30])
        sound_system.play('explode')
        
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            for i in range(1, bomb.fire_range + 1):
                nx = bomb.grid_x + dx * i
                ny = bomb.grid_y + dy * i
                
                if nx < 0 or nx >= GRID_WIDTH or ny < 0 or ny >= GRID_HEIGHT:
                    break
                
                if self.grid[ny][nx] == WALL:
                    break
                
                if self.grid[ny][nx] == BLOCK:
                    self.grid[ny][nx] = FIRE
                    self.fires.append([nx, ny, 30])
                    if random.random() < 0.3:
                        powerup_types = [POWERUP_SPEED, POWERUP_BOMB, POWERUP_RANGE]
                        self.powerups.append(PowerUp(nx, ny, random.choice(powerup_types)))
                    break
                
                if self.grid[ny][nx] == BOMB:
                    for other_bomb in self.bombs:
                        if other_bomb.grid_x == nx and other_bomb.grid_y == ny:
                            other_bomb.timer = 1
                
                self.grid[ny][nx] = FIRE
                self.fires.append([nx, ny, 30])
        
        for player in self.players:
            if player.player_id == bomb.owner_id:
                player.bombs_left += 1
        self.bombs.remove(bomb)
    
    def draw(self):
        screen.fill(BLACK)
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if self.grid[y][x] == WALL:
                    pygame.draw.rect(screen, BLUE, rect)
                    pygame.draw.rect(screen, WHITE, rect, 2)
                elif self.grid[y][x] == BLOCK:
                    pygame.draw.rect(screen, BROWN, rect)
                elif self.grid[y][x] == FIRE:
                    pygame.draw.rect(screen, ORANGE, rect)
                    pygame.draw.rect(screen, YELLOW, rect, 3)
        
        for powerup in self.powerups:
            if powerup.alive:
                if powerup.type == POWERUP_SPEED:
                    color = CYAN
                elif powerup.type == POWERUP_BOMB:
                    color = RED
                else:
                    color = ORANGE
                rect = pygame.Rect(powerup.grid_x * TILE_SIZE + 8, powerup.grid_y * TILE_SIZE + 8, TILE_SIZE - 16, TILE_SIZE - 16)
                pygame.draw.ellipse(screen, color, rect)
        
        for bomb in self.bombs:
            rect = pygame.Rect(bomb.x + 4, bomb.y + 4, TILE_SIZE - 8, TILE_SIZE - 8)
            pygame.draw.ellipse(screen, BLACK, rect)
            pygame.draw.ellipse(screen, RED, rect, 3)
        
        for player in self.players:
            if player.alive:
                pygame.draw.rect(screen, player.color, (player.x, player.y, player.width, player.height))
                font = get_chinese_font(24)
                text = font.render(str(player.player_id + 1), True, BLACK)
                screen.blit(text, (player.x + player.width//2 - text.get_width()//2, player.y + player.height//2 - text.get_height()//2))
        
        self.draw_ui()
    
    def draw_ui(self):
        font = get_chinese_font(24)
        y_pos = 10
        for i, player in enumerate(self.players):
            status = f"玩家{i+1}: "
            if player.alive:
                status += f"炸弹:{player.bombs} 范围:{player.fire_range+1}"
                color = player.color
            else:
                status += "已淘汰"
                color = GRAY
            text = font.render(status, True, color)
            screen.blit(text, (10, y_pos))
            y_pos += 25
    
    def draw_gameover(self):
        screen.fill(BLACK)
        font = get_chinese_font(72)
        if self.winner:
            text = font.render(f"玩家 {self.winner.player_id + 1} 获胜!", True, self.winner.color)
        else:
            text = font.render("平局!", True, GRAY)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200))
        
        font = get_chinese_font(36)
        restart_text = font.render("按 R 重新开始", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 350))

class Menu:
    def __init__(self):
        self.state = 'menu'
        self.selected_players = 2
    
    def draw(self):
        screen.fill(BLACK)
        font = get_chinese_font(72)
        title = font.render("多人炸弹人", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        font = get_chinese_font(48)
        player_text = font.render(f"玩家数量: {self.selected_players}", True, WHITE)
        screen.blit(player_text, (SCREEN_WIDTH // 2 - player_text.get_width() // 2, 250))
        
        font = get_chinese_font(36)
        instructions = [
            "操作说明：",
            "玩家1: WASD移动, 空格放炸弹",
            "玩家2: 方向键移动, Enter放炸弹",
            "玩家3: IJKL移动, O放炸弹",
            "玩家4: TFGH移动, Y放炸弹",
            "",
            "道具：红色-炸弹+1 橙色-范围+1 青色-速度+1",
            "",
            "按 左/右 调整玩家数量, 按 空格 开始"
        ]
        y_pos = 320
        for line in instructions:
            text = font.render(line, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 35
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.selected_players = max(2, self.selected_players - 1)
                if event.key == pygame.K_RIGHT:
                    self.selected_players = min(4, self.selected_players + 1)
                if event.key == pygame.K_SPACE:
                    self.state = 'playing'
                    return Game(self.selected_players)
        return self

def main():
    clock = pygame.time.Clock()
    current_state = Menu()
    bomb_keys_pressed = {}
    
    while True:
        if isinstance(current_state, Menu):
            current_state.draw()
            new_state = current_state.handle_input()
            if isinstance(new_state, Game):
                current_state = new_state
                bomb_keys_pressed = {p.bomb_key: False for p in current_state.players}
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if current_state.state == 'gameover' and event.key == pygame.K_r:
                        current_state = Menu()
                    elif current_state.state == 'playing':
                        for player in current_state.players:
                            if event.key == player.bomb_key and not bomb_keys_pressed.get(player.bomb_key, False):
                                current_state.place_bomb(player)
                                bomb_keys_pressed[player.bomb_key] = True
                if event.type == pygame.KEYUP:
                    for player in current_state.players:
                        if event.key == player.bomb_key:
                            bomb_keys_pressed[player.bomb_key] = False
            
            if current_state.state == 'playing':
                current_state.handle_input()
                current_state.update()
                current_state.draw()
            elif current_state.state == 'gameover':
                current_state.draw_gameover()
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
