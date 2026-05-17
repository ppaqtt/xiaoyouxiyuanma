import pygame
import os
import random
import sys

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

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
TILE_SIZE = 40
GRID_SIZE = 16
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("炸弹人专业版 Bomberman Pro")

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

EMPTY = 0
WALL = 1
BLOCK = 2
BOMB = 3
FIRE = 4
POWERUP_BOMB = 5
POWERUP_RANGE = 6
POWERUP_SPEED = 7
POWERUP_KICK = 8

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE - 4
        self.height = TILE_SIZE - 4
        self.bombs = 1
        self.bombs_left = 1
        self.fire_range = 2
        self.speed = 4
        self.can_kick = False
        self.alive = True

    def get_grid_pos(self):
        return (self.x + TILE_SIZE // 2) // TILE_SIZE, (self.y + TILE_SIZE // 2) // TILE_SIZE

class Bomb:
    def __init__(self, x, y, range):
        self.grid_x = x
        self.grid_y = y
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.range = range
        self.timer = 180
        self.kicked = False
        self.direction = (0, 0)

class Enemy:
    def __init__(self, x, y):
        self.grid_x = x
        self.grid_y = y
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = TILE_SIZE - 8
        self.height = TILE_SIZE - 8
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.alive = True
        self.move_timer = 0

class PowerUp:
    def __init__(self, x, y, type):
        self.grid_x = x
        self.grid_y = y
        self.type = type
        self.alive = True

class Game:
    def __init__(self):
        self.state = 'menu'
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.load_high_score()
        self.reset_game()

    def reset_game(self):
        self.grid = self.create_map()
        self.player = Player(TILE_SIZE + 2, TILE_SIZE + 2)
        self.bombs = []
        self.fires = []
        self.enemies = self.create_enemies()
        self.powerups = []
        self.game_timer = 0

    def create_map(self):
        grid = []
        for y in range(GRID_SIZE):
            row = []
            for x in range(GRID_SIZE):
                if x == 0 or x == GRID_SIZE - 1 or y == 0 or y == GRID_SIZE - 1:
                    row.append(WALL)
                elif x % 2 == 0 and y % 2 == 0:
                    row.append(WALL)
                elif (x <= 2 and y <= 2):
                    row.append(EMPTY)
                else:
                    if random.random() < 0.6:
                        row.append(BLOCK)
                    else:
                        row.append(EMPTY)
            grid.append(row)
        return grid

    def create_enemies(self):
        enemies = []
        count = min(4 + self.level, 10)
        for _ in range(count):
            placed = False
            while not placed:
                x = random.randint(3, GRID_SIZE - 3)
                y = random.randint(3, GRID_SIZE - 3)
                if self.grid[y][x] == EMPTY:
                    enemies.append(Enemy(x, y))
                    placed = True
        return enemies

    def load_high_score(self):
        try:
            with open('bm_highscore.txt', 'r') as f:
                self.high_score = int(f.read())
        except:
            self.high_score = 0

    def save_high_score(self):
        with open('bm_highscore.txt', 'w') as f:
            f.write(str(self.high_score))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.player.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.player.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.player.speed

        new_x = self.player.x + dx
        new_y = self.player.y + dy
        
        if not self.check_collision(new_x, self.player.y):
            self.player.x = new_x
        if not self.check_collision(self.player.x, new_y):
            self.player.y = new_y

    def check_collision(self, x, y):
        rect = pygame.Rect(x, y, self.player.width, self.player.height)
        
        for grid_y in range(GRID_SIZE):
            for grid_x in range(GRID_SIZE):
                if self.grid[grid_y][grid_x] in [WALL, BLOCK]:
                    tile_rect = pygame.Rect(grid_x * TILE_SIZE, grid_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if rect.colliderect(tile_rect):
                        return True
        
        for bomb in self.bombs:
            bomb_rect = pygame.Rect(bomb.x, bomb.y, TILE_SIZE, TILE_SIZE)
            if rect.colliderect(bomb_rect):
                if self.player.can_kick and not bomb.kicked:
                    bomb.kicked = True
                    if x < self.player.x:
                        bomb.direction = (-1, 0)
                    elif x > self.player.x:
                        bomb.direction = (1, 0)
                    elif y < self.player.y:
                        bomb.direction = (0, -1)
                    elif y > self.player.y:
                        bomb.direction = (0, 1)
                else:
                    return True
        
        return False

    def place_bomb(self):
        grid_x, grid_y = self.player.get_grid_pos()
        if self.player.bombs_left > 0 and self.grid[grid_y][grid_x] == EMPTY:
            self.grid[grid_y][grid_x] = BOMB
            self.bombs.append(Bomb(grid_x, grid_y, self.player.fire_range))
            self.player.bombs_left -= 1

    def update(self):
        self.game_timer += 1
        
        for bomb in self.bombs[:]:
            if bomb.kicked:
                new_x = bomb.x + bomb.direction[0] * 3
                new_y = bomb.y + bomb.direction[1] * 3
                
                grid_x = int(new_x // TILE_SIZE)
                grid_y = int(new_y // TILE_SIZE)
                
                if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                    if self.grid[grid_y][grid_x] == EMPTY or self.grid[grid_y][grid_x] == BOMB:
                        self.grid[bomb.grid_y][bomb.grid_x] = EMPTY
                        bomb.x = new_x
                        bomb.y = new_y
                        bomb.grid_x = grid_x
                        bomb.grid_y = grid_y
                        self.grid[grid_y][grid_x] = BOMB
                    else:
                        bomb.kicked = False
                        bomb.direction = (0, 0)
                else:
                    bomb.kicked = False
                    bomb.direction = (0, 0)
            
            bomb.timer -= 1
            if bomb.timer <= 0:
                self.explode(bomb)
        
        for fire in self.fires[:]:
            fire[2] -= 1
            if fire[2] <= 0:
                self.fires.remove(fire)
                if self.grid[fire[1]][fire[0]] == FIRE:
                    self.grid[fire[1]][fire[0]] = EMPTY
        
        for enemy in self.enemies[:]:
            if enemy.alive:
                enemy.move_timer += 1
                if enemy.move_timer >= 20:
                    enemy.move_timer = 0
                    if random.random() < 0.3:
                        enemy.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                    
                    new_x = enemy.x + enemy.direction[0] * TILE_SIZE
                    new_y = enemy.y + enemy.direction[1] * TILE_SIZE
                    grid_x = int(new_x // TILE_SIZE)
                    grid_y = int(new_y // TILE_SIZE)
                    
                    if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                        if self.grid[grid_y][grid_x] in [EMPTY, FIRE]:
                            enemy.x = new_x
                            enemy.y = new_y
                            enemy.grid_x = grid_x
                            enemy.grid_y = grid_y
        
        player_grid_x, player_grid_y = self.player.get_grid_pos()
        if self.grid[player_grid_y][player_grid_x] == FIRE:
            self.player.alive = False
        
        for enemy in self.enemies:
            if enemy.alive:
                dist_x = abs(self.player.x - enemy.x)
                dist_y = abs(self.player.y - enemy.y)
                if dist_x < TILE_SIZE // 2 and dist_y < TILE_SIZE // 2:
                    self.player.alive = False
                
                if self.grid[enemy.grid_y][enemy.grid_x] == FIRE:
                    enemy.alive = False
                    self.score += 100
        
        for powerup in self.powerups[:]:
            if powerup.alive:
                if powerup.grid_x == player_grid_x and powerup.grid_y == player_grid_y:
                    powerup.alive = False
                    self.score += 50
                    if powerup.type == POWERUP_BOMB:
                        self.player.bombs += 1
                        self.player.bombs_left += 1
                    elif powerup.type == POWERUP_RANGE:
                        self.player.fire_range += 1
                    elif powerup.type == POWERUP_SPEED:
                        self.player.speed = min(8, self.player.speed + 1)
                    elif powerup.type == POWERUP_KICK:
                        self.player.can_kick = True
        
        if not self.player.alive:
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            self.state = 'gameover'
        
        alive_enemies = [e for e in self.enemies if e.alive]
        if not alive_enemies:
            self.level += 1
            self.score += 1000
            self.reset_game()

    def explode(self, bomb):
        self.grid[bomb.grid_y][bomb.grid_x] = FIRE
        self.fires.append([bomb.grid_x, bomb.grid_y, 30])
        
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            for i in range(1, bomb.range + 1):
                nx = bomb.grid_x + dx * i
                ny = bomb.grid_y + dy * i
                
                if nx < 0 or nx >= GRID_SIZE or ny < 0 or ny >= GRID_SIZE:
                    break
                
                if self.grid[ny][nx] == WALL:
                    break
                
                if self.grid[ny][nx] == BLOCK:
                    self.grid[ny][nx] = FIRE
                    self.fires.append([nx, ny, 30])
                    if random.random() < 0.2:
                        powerup_types = [POWERUP_BOMB, POWERUP_RANGE, POWERUP_SPEED, POWERUP_KICK]
                        self.powerups.append(PowerUp(nx, ny, random.choice(powerup_types)))
                    break
                
                if self.grid[ny][nx] == BOMB:
                    for other_bomb in self.bombs:
                        if other_bomb.grid_x == nx and other_bomb.grid_y == ny:
                            other_bomb.timer = 1
                
                self.grid[ny][nx] = FIRE
                self.fires.append([nx, ny, 30])
        
        self.player.bombs_left += 1
        self.bombs.remove(bomb)

    def draw_menu(self):
        screen.fill(BLACK)
        font = get_chinese_font(72)
        title = font.render("炸弹人专业版 BOMBERMAN PRO", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        font = get_chinese_font(36)
        instructions = [
            "操作说明：",
            "WASD / 方向键 - 移动",
            "空格键 - 放置炸弹",
            "",
            "道具说明：",
            "红色 - 炸弹数量+1, 橙色 - 爆炸范围+1",
            "青色 - 移动速度+1, 紫色 - 可以踢炸弹",
            "",
            "按空格键开始游戏"
        ]
        y_pos = 200
        for line in instructions:
            text = font.render(line, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 40

        high_score_text = font.render(f"最高分: {self.high_score}", True, WHITE)
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, 520))

    def draw_game(self):
        screen.fill(BLACK)
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
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
                colors = [RED, ORANGE, CYAN, PURPLE]
                color = colors[powerup.type - POWERUP_BOMB]
                rect = pygame.Rect(powerup.grid_x * TILE_SIZE + 8, powerup.grid_y * TILE_SIZE + 8, TILE_SIZE - 16, TILE_SIZE - 16)
                pygame.draw.ellipse(screen, color, rect)
        
        for bomb in self.bombs:
            rect = pygame.Rect(bomb.x + 4, bomb.y + 4, TILE_SIZE - 8, TILE_SIZE - 8)
            pygame.draw.ellipse(screen, BLACK, rect)
            pygame.draw.ellipse(screen, RED, rect, 3)
        
        if self.player.alive:
            pygame.draw.rect(screen, WHITE, (self.player.x, self.player.y, self.player.width, self.player.height))
        
        for enemy in self.enemies:
            if enemy.alive:
                pygame.draw.ellipse(screen, RED, (enemy.x + 4, enemy.y + 4, enemy.width, enemy.height))

    def draw_gameover(self):
        screen.fill(BLACK)
        font = get_chinese_font(72)
        gameover_text = font.render("游戏结束", True, RED)
        screen.blit(gameover_text, (SCREEN_WIDTH // 2 - gameover_text.get_width() // 2, 150))
        
        font = get_chinese_font(48)
        score_text = font.render(f"得分: {self.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))
        
        font = get_chinese_font(36)
        restart_text = font.render("按空格键重新开始", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 400))

def main():
    clock = pygame.time.Clock()
    game = Game()
    bomb_key_pressed = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.state == 'menu':
                        game.state = 'playing'
                    elif game.state == 'gameover':
                        game.reset_game()
                        game.state = 'playing'
                    elif game.state == 'playing' and not bomb_key_pressed:
                        game.place_bomb()
                        bomb_key_pressed = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    bomb_key_pressed = False

        if game.state == 'menu':
            game.draw_menu()
        elif game.state == 'gameover':
            game.draw_gameover()
        elif game.state == 'playing':
            game.handle_input()
            game.update()
            game.draw_game()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
