import pygame
import random
import sys
import time

pygame.init()

SCREEN_WIDTH = 560
SCREEN_HEIGHT = 620
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("吃豆人 Pac-Man")

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
WHITE = (255, 255, 255)

TILE_SIZE = 20

MAP = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#O####.#####.##.#####.####O#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "######.##### ## #####.######",
    "######.##          ##.######",
    "######.## ######## ##.######",
    "######.## ######## ##.######",
    "#..........##  ##..........#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#O..##.......  .......##..O#",
    "###.##.##.########.##.##.###",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################",
]

class PacMan:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.mouth_open = False
        self.score = 0
        self.lives = 3
        self.power_mode = False
        self.power_timer = 0

    def move(self):
        if self.can_move(self.next_direction):
            self.direction = self.next_direction
        if self.can_move(self.direction):
            self.x += self.direction[0] * TILE_SIZE
            self.y += self.direction[1] * TILE_SIZE
            self.mouth_open = not self.mouth_open
            self.check_warp()

    def can_move(self, direction):
        new_x = self.x + direction[0] * TILE_SIZE
        new_y = self.y + direction[1] * TILE_SIZE
        if new_y < 0 or new_y >= len(MAP) * TILE_SIZE:
            return False
        if new_x < 0 or new_x >= len(MAP[0]) * TILE_SIZE:
            return False
        tile = MAP[int(new_y / TILE_SIZE)][int(new_x / TILE_SIZE)]
        return tile != '#'

    def check_warp(self):
        if self.x < 0:
            self.x = (len(MAP[0]) - 1) * TILE_SIZE
        elif self.x >= len(MAP[0]) * TILE_SIZE:
            self.x = 0

    def draw(self, surface):
        center_x = self.x + TILE_SIZE // 2
        center_y = self.y + TILE_SIZE // 2
        if self.mouth_open:
            start_angle = 45 if self.direction == (0, -1) else 135 if self.direction == (-1, 0) else 225 if self.direction == (0, 1) else 315
            end_angle = start_angle + 270
        else:
            start_angle = 0
            end_angle = 360
        pygame.draw.circle(surface, YELLOW, (center_x, center_y), TILE_SIZE // 2 - 2)
        if self.mouth_open:
            pygame.draw.polygon(surface, BLACK, [
                (center_x, center_y),
                (center_x + (TILE_SIZE // 2 - 2) * 1, center_y),
                (center_x + (TILE_SIZE // 2 - 2) * 0.707, center_y + (TILE_SIZE // 2 - 2) * 0.707)
            ])

    def update_power_mode(self):
        if self.power_mode:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.power_mode = False

class Ghost:
    def __init__(self, x, y, color, behavior):
        self.x = x
        self.y = y
        self.color = color
        self.behavior = behavior
        self.direction = (0, -1)
        self.eaten = False

    def move(self, pacman, ghosts):
        possible_moves = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            if (dx, dy) == (-self.direction[0], -self.direction[1]):
                continue
            new_x = self.x + dx * TILE_SIZE
            new_y = self.y + dy * TILE_SIZE
            if new_y < 0 or new_y >= len(MAP) * TILE_SIZE:
                continue
            if new_x < 0 or new_x >= len(MAP[0]) * TILE_SIZE:
                continue
            tile = MAP[int(new_y / TILE_SIZE)][int(new_x / TILE_SIZE)]
            if tile != '#':
                possible_moves.append((dx, dy))
        if not possible_moves:
            possible_moves.append((-self.direction[0], -self.direction[1]))
        
        if self.behavior == 'chase':
            best_move = None
            best_dist = float('inf')
            for move in possible_moves:
                new_x = self.x + move[0] * TILE_SIZE
                new_y = self.y + move[1] * TILE_SIZE
                dist = abs(new_x - pacman.x) + abs(new_y - pacman.y)
                if dist < best_dist:
                    best_dist = dist
                    best_move = move
            self.direction = best_move
        elif self.behavior == 'ambush':
            target_x = pacman.x + pacman.direction[0] * TILE_SIZE * 4
            target_y = pacman.y + pacman.direction[1] * TILE_SIZE * 4
            best_move = None
            best_dist = float('inf')
            for move in possible_moves:
                new_x = self.x + move[0] * TILE_SIZE
                new_y = self.y + move[1] * TILE_SIZE
                dist = abs(new_x - target_x) + abs(new_y - target_y)
                if dist < best_dist:
                    best_dist = dist
                    best_move = move
            self.direction = best_move
        elif self.behavior == 'random':
            self.direction = random.choice(possible_moves)
        elif self.behavior == 'follow':
            if random.random() < 0.7:
                best_move = None
                best_dist = float('inf')
                for move in possible_moves:
                    new_x = self.x + move[0] * TILE_SIZE
                    new_y = self.y + move[1] * TILE_SIZE
                    dist = abs(new_x - pacman.x) + abs(new_y - pacman.y)
                    if dist < best_dist:
                        best_dist = dist
                        best_move = move
                self.direction = best_move
            else:
                self.direction = random.choice(possible_moves)
        
        self.x += self.direction[0] * TILE_SIZE
        self.y += self.direction[1] * TILE_SIZE

    def draw(self, surface, power_mode):
        center_x = self.x + TILE_SIZE // 2
        center_y = self.y + TILE_SIZE // 2
        color = BLUE if power_mode and not self.eaten else self.color
        pygame.draw.circle(surface, color, (center_x, center_y - 2), TILE_SIZE // 2 - 2)
        pygame.draw.rect(surface, color, (self.x + 2, self.y + TILE_SIZE // 2, TILE_SIZE - 4, TILE_SIZE // 2))
        if not power_mode or self.eaten:
            pygame.draw.circle(surface, WHITE, (center_x - 4, center_y - 4), 4)
            pygame.draw.circle(surface, WHITE, (center_x + 4, center_y - 4), 4)
            pygame.draw.circle(surface, BLACK, (center_x - 3, center_y - 4), 2)
            pygame.draw.circle(surface, BLACK, (center_x + 5, center_y - 4), 2)

class Game:
    def __init__(self):
        self.pacman = PacMan(14 * TILE_SIZE, 23 * TILE_SIZE)
        self.ghosts = [
            Ghost(13 * TILE_SIZE, 13 * TILE_SIZE, RED, 'chase'),
            Ghost(14 * TILE_SIZE, 13 * TILE_SIZE, PINK, 'ambush'),
            Ghost(12 * TILE_SIZE, 13 * TILE_SIZE, CYAN, 'random'),
            Ghost(15 * TILE_SIZE, 13 * TILE_SIZE, ORANGE, 'follow')
        ]
        self.state = 'menu'
        self.level = 1
        self.high_score = 0
        self.load_high_score()
        self.dots = self.create_dots()
        self.power_dots = self.create_power_dots()

    def create_dots(self):
        dots = []
        for y, row in enumerate(MAP):
            for x, tile in enumerate(row):
                if tile == '.':
                    dots.append((x * TILE_SIZE, y * TILE_SIZE))
        return dots

    def create_power_dots(self):
        power_dots = []
        for y, row in enumerate(MAP):
            for x, tile in enumerate(row):
                if tile == 'O':
                    power_dots.append((x * TILE_SIZE, y * TILE_SIZE))
        return power_dots

    def load_high_score(self):
        try:
            with open('pacman_highscore.txt', 'r') as f:
                self.high_score = int(f.read())
        except:
            self.high_score = 0

    def save_high_score(self):
        with open('pacman_highscore.txt', 'w') as f:
            f.write(str(self.high_score))

    def check_collisions(self):
        for i, (dot_x, dot_y) in enumerate(self.dots):
            if self.pacman.x == dot_x and self.pacman.y == dot_y:
                self.pacman.score += 10
                self.dots.pop(i)
                break
        
        for i, (dot_x, dot_y) in enumerate(self.power_dots):
            if self.pacman.x == dot_x and self.pacman.y == dot_y:
                self.pacman.score += 50
                self.pacman.power_mode = True
                self.pacman.power_timer = 600
                self.power_dots.pop(i)
                for ghost in self.ghosts:
                    ghost.eaten = False
                break

        for ghost in self.ghosts:
            if self.pacman.x == ghost.x and self.pacman.y == ghost.y:
                if self.pacman.power_mode and not ghost.eaten:
                    self.pacman.score += 200
                    ghost.eaten = True
                    ghost.x = 13 * TILE_SIZE
                    ghost.y = 13 * TILE_SIZE
                elif not self.pacman.power_mode and not ghost.eaten:
                    self.pacman.lives -= 1
                    self.pacman.x = 14 * TILE_SIZE
                    self.pacman.y = 23 * TILE_SIZE
                    self.pacman.direction = (0, 0)
                    self.pacman.next_direction = (0, 0)
                    self.ghosts = [
                        Ghost(13 * TILE_SIZE, 13 * TILE_SIZE, RED, 'chase'),
                        Ghost(14 * TILE_SIZE, 13 * TILE_SIZE, PINK, 'ambush'),
                        Ghost(12 * TILE_SIZE, 13 * TILE_SIZE, CYAN, 'random'),
                        Ghost(15 * TILE_SIZE, 13 * TILE_SIZE, ORANGE, 'follow')
                    ]
                    if self.pacman.lives <= 0:
                        if self.pacman.score > self.high_score:
                            self.high_score = self.pacman.score
                            self.save_high_score()
                        self.state = 'gameover'

    def draw_menu(self):
        screen.fill(BLACK)
        font = pygame.font.Font(None, 72)
        title = font.render("PAC-MAN", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        font = pygame.font.Font(None, 36)
        instructions = [
            "操作说明：",
            "WASD / 方向键 - 移动",
            "",
            "游戏规则：",
            "吃掉所有豆子过关",
            "能量豆可以吃鬼",
            "",
            "按空格键开始游戏"
        ]
        y_pos = 200
        for line in instructions:
            text = font.render(line, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
            y_pos += 40

        high_score_text = font.render(f"最高分: {self.high_score}", True, WHITE)
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, 500))

    def draw_game(self):
        screen.fill(BLACK)
        
        for y, row in enumerate(MAP):
            for x, tile in enumerate(row):
                if tile == '#':
                    pygame.draw.rect(screen, BLUE, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
        
        for dot_x, dot_y in self.dots:
            pygame.draw.circle(screen, WHITE, (dot_x + TILE_SIZE // 2, dot_y + TILE_SIZE // 2), 3)
        
        for dot_x, dot_y in self.power_dots:
            pygame.draw.circle(screen, WHITE, (dot_x + TILE_SIZE // 2, dot_y + TILE_SIZE // 2), 7)
        
        for ghost in self.ghosts:
            ghost.draw(screen, self.pacman.power_mode)
        
        self.pacman.draw(screen)
        
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"分数: {self.pacman.score}", True, WHITE)
        lives_text = font.render(f"生命: {self.pacman.lives}", True, WHITE)
        level_text = font.render(f"关卡: {self.level}", True, WHITE)
        screen.blit(score_text, (10, 530))
        screen.blit(lives_text, (200, 530))
        screen.blit(level_text, (350, 530))

    def draw_gameover(self):
        screen.fill(BLACK)
        font = pygame.font.Font(None, 72)
        gameover_text = font.render("游戏结束", True, RED)
        screen.blit(gameover_text, (SCREEN_WIDTH // 2 - gameover_text.get_width() // 2, 150))
        
        font = pygame.font.Font(None, 48)
        score_text = font.render(f"得分: {self.pacman.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))
        
        font = pygame.font.Font(None, 36)
        restart_text = font.render("按空格键重新开始", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 400))

    def next_level(self):
        self.level += 1
        self.pacman.x = 14 * TILE_SIZE
        self.pacman.y = 23 * TILE_SIZE
        self.pacman.direction = (0, 0)
        self.pacman.next_direction = (0, 0)
        self.pacman.power_mode = False
        self.ghosts = [
            Ghost(13 * TILE_SIZE, 13 * TILE_SIZE, RED, 'chase'),
            Ghost(14 * TILE_SIZE, 13 * TILE_SIZE, PINK, 'ambush'),
            Ghost(12 * TILE_SIZE, 13 * TILE_SIZE, CYAN, 'random'),
            Ghost(15 * TILE_SIZE, 13 * TILE_SIZE, ORANGE, 'follow')
        ]
        self.dots = self.create_dots()
        self.power_dots = self.create_power_dots()

    def reset_game(self):
        self.pacman = PacMan(14 * TILE_SIZE, 23 * TILE_SIZE)
        self.ghosts = [
            Ghost(13 * TILE_SIZE, 13 * TILE_SIZE, RED, 'chase'),
            Ghost(14 * TILE_SIZE, 13 * TILE_SIZE, PINK, 'ambush'),
            Ghost(12 * TILE_SIZE, 13 * TILE_SIZE, CYAN, 'random'),
            Ghost(15 * TILE_SIZE, 13 * TILE_SIZE, ORANGE, 'follow')
        ]
        self.level = 1
        self.dots = self.create_dots()
        self.power_dots = self.create_power_dots()
        self.state = 'playing'

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.pacman.next_direction = (0, -1)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.pacman.next_direction = (0, 1)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.pacman.next_direction = (-1, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.pacman.next_direction = (1, 0)

def main():
    clock = pygame.time.Clock()
    game = Game()
    frame_count = 0

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

        if game.state == 'menu':
            game.draw_menu()
        elif game.state == 'gameover':
            game.draw_gameover()
        elif game.state == 'playing':
            game.handle_input()
            
            frame_count += 1
            if frame_count % 8 == 0:
                game.pacman.move()
                game.pacman.update_power_mode()
            
            if frame_count % 12 == 0:
                for ghost in game.ghosts:
                    ghost.move(game.pacman, game.ghosts)
            
            game.check_collisions()
            
            if not game.dots and not game.power_dots:
                game.next_level()
            
            game.draw_game()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
