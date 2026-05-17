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

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("大金刚 Donkey Kong")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
PINK = (255, 192, 203)
GRAY = (128, 128, 128)

PLAYER_SIZE = 30
GRAVITY = 0.5
JUMP_FORCE = -12
MOVE_SPEED = 5

class Platform:
    def __init__(self, x, y, width, slope=0):
        self.x = x
        self.y = y
        self.width = width
        self.slope = slope
        self.height = 10

class Ladder:
    def __init__(self, x, y, height):
        self.x = x
        self.y = y
        self.width = 20
        self.height = height

class Barrel:
    def __init__(self, x, y, direction=1):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        self.vx = 3 * direction
        self.vy = 0
        self.direction = direction
        self.rotation = 0

    def update(self, platforms, ladders):
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy
        self.rotation += 10

        on_platform = False
        for platform in platforms:
            if (self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and
                self.y + self.height > platform.y and
                self.y + self.height < platform.y + 20 and
                self.vy > 0):
                self.y = platform.y - self.height
                self.vy = 0
                on_platform = True
                
                if platform.slope != 0:
                    self.vx = 3 * (1 if platform.slope > 0 else -1)
                
                if random.random() < 0.02:
                    self.vx = -self.vx

        for ladder in ladders:
            if (self.x + self.width > ladder.x and 
                self.x < ladder.x + ladder.width and
                self.y + self.height > ladder.y and
                self.y < ladder.y + ladder.height):
                if random.random() < 0.05:
                    self.vy = 5

        if self.x < 0:
            self.x = 0
            self.vx = -self.vx
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
            self.vx = -self.vx

    def draw(self, surface):
        barrel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.ellipse(surface, BROWN, barrel_rect)
        pygame.draw.ellipse(surface, ORANGE, barrel_rect, 3)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.on_ladder = False
        self.lives = 3
        self.score = 0
        self.jumping = False

    def update(self, platforms, ladders):
        keys = pygame.key.get_pressed()
        
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -MOVE_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = MOVE_SPEED

        self.on_ladder = False
        for ladder in ladders:
            if (self.x + self.width > ladder.x and 
                self.x < ladder.x + ladder.width and
                self.y + self.height > ladder.y and
                self.y < ladder.y + ladder.height):
                self.on_ladder = True
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.vy = -MOVE_SPEED
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    self.vy = MOVE_SPEED
                else:
                    self.vy = 0
        
        if not self.on_ladder:
            self.vy += GRAVITY
            if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
                self.vy = JUMP_FORCE
                self.on_ground = False

        self.x += self.vx
        self.y += self.vy

        self.on_ground = False
        for platform in platforms:
            if (self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and
                self.y + self.height > platform.y and
                self.y + self.height < platform.y + 20 and
                self.vy > 0):
                self.y = platform.y - self.height
                self.vy = 0
                self.on_ground = True

        if self.x < 0:
            self.x = 0
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
        if self.y + self.height > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.height
            self.vy = 0
            self.on_ground = True

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(surface, (255, 200, 150), (self.x + self.width // 2, self.y - 5), 12)

class DonkeyKong:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 80
        self.frame = 0
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer % 30 == 0:
            self.frame = (self.frame + 1) % 2

    def draw(self, surface):
        pygame.draw.rect(surface, BROWN, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(surface, BROWN, (self.x + self.width // 2, self.y - 20), 30)
        pygame.draw.circle(surface, RED, (self.x + self.width // 2 - 10, self.y - 25), 5)
        pygame.draw.circle(surface, RED, (self.x + self.width // 2 + 10, self.y - 25), 5)

class Princess:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 50

    def draw(self, surface):
        pygame.draw.rect(surface, PINK, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(surface, (255, 200, 150), (self.x + self.width // 2, self.y - 10), 15)

class Game:
    def __init__(self):
        self.state = 'menu'
        self.level = 1
        self.score = 0
        self.high_score = 0
        self.load_high_score()
        
        self.platforms = [
            Platform(0, 550, 800, 0),
            Platform(100, 480, 600, 1),
            Platform(100, 410, 600, -1),
            Platform(100, 340, 600, 1),
            Platform(100, 270, 600, -1),
            Platform(100, 200, 600, 1),
            Platform(300, 130, 200, 0)
        ]
        
        self.ladders = [
            Ladder(700, 480, 70),
            Ladder(150, 410, 70),
            Ladder(700, 340, 70),
            Ladder(150, 270, 70),
            Ladder(700, 200, 70),
            Ladder(350, 130, 70)
        ]
        
        self.player = Player(50, 500)
        self.dk = DonkeyKong(350, 50)
        self.princess = Princess(420, 80)
        self.barrels = []
        self.barrel_timer = 0

    def load_high_score(self):
        try:
            with open('dk_highscore.txt', 'r') as f:
                self.high_score = int(f.read())
        except:
            self.high_score = 0

    def save_high_score(self):
        with open('dk_highscore.txt', 'w') as f:
            f.write(str(self.high_score))

    def reset_game(self):
        self.player = Player(50, 500)
        self.barrels = []
        self.barrel_timer = 0
        self.state = 'playing'

    def spawn_barrel(self):
        self.barrel_timer += 1
        spawn_rate = max(60, 120 - self.level * 10)
        if self.barrel_timer >= spawn_rate:
            self.barrels.append(Barrel(400, 120, 1))
            self.barrel_timer = 0

    def check_collisions(self):
        for barrel in self.barrels[:]:
            if (self.player.x < barrel.x + barrel.width and
                self.player.x + self.player.width > barrel.x and
                self.player.y < barrel.y + barrel.height and
                self.player.y + self.player.height > barrel.y):
                self.player.lives -= 1
                self.player.x = 50
                self.player.y = 500
                self.player.vx = 0
                self.player.vy = 0
                if self.player.lives <= 0:
                    if self.player.score > self.high_score:
                        self.high_score = self.player.score
                        self.save_high_score()
                    self.state = 'gameover'
        
        if (self.player.x < self.princess.x + self.princess.width and
            self.player.x + self.player.width > self.princess.x and
            self.player.y < self.princess.y + self.princess.height and
            self.player.y + self.player.height > self.princess.y):
            self.player.score += 1000
            self.level += 1
            self.player.x = 50
            self.player.y = 500
            self.barrels = []

    def draw_menu(self):
        screen.fill(BLACK)
        font = get_chinese_font(72)
        title = font.render("大金刚 DONKEY KONG", True, RED)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        font = get_chinese_font(36)
        instructions = [
            "操作说明：",
            "WASD / 方向键 - 移动",
            "W / 空格 / 上 - 跳跃",
            "",
            "游戏规则：",
            "躲避滚桶，爬到顶端解救公主",
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
        
        for platform in self.platforms:
            pygame.draw.rect(surface=screen, color=GRAY, rect=(platform.x, platform.y, platform.width, platform.height))
        
        for ladder in self.ladders:
            pygame.draw.rect(screen, BROWN, (ladder.x, ladder.y, ladder.width, ladder.height))
            for i in range(0, ladder.height, 20):
                pygame.draw.rect(screen, ORANGE, (ladder.x - 5, ladder.y + i, ladder.width + 10, 5))
        
        for barrel in self.barrels:
            barrel.draw(screen)
        
        self.dk.draw(screen)
        self.princess.draw(screen)
        self.player.draw(screen)
        
        font = get_chinese_font(36)
        score_text = font.render(f"分数: {self.player.score}", True, WHITE)
        lives_text = font.render(f"生命: {self.player.lives}", True, WHITE)
        level_text = font.render(f"关卡: {self.level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (200, 10))
        screen.blit(level_text, (380, 10))

    def draw_gameover(self):
        screen.fill(BLACK)
        font = get_chinese_font(72)
        gameover_text = font.render("游戏结束", True, RED)
        screen.blit(gameover_text, (SCREEN_WIDTH // 2 - gameover_text.get_width() // 2, 150))
        
        font = get_chinese_font(48)
        score_text = font.render(f"得分: {self.player.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))
        
        font = get_chinese_font(36)
        restart_text = font.render("按空格键重新开始", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 400))

def main():
    clock = pygame.time.Clock()
    game = Game()

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
            game.player.update(game.platforms, game.ladders)
            game.dk.update()
            game.spawn_barrel()
            
            for barrel in game.barrels[:]:
                barrel.update(game.platforms, game.ladders)
                if barrel.y > SCREEN_HEIGHT + 50:
                    game.barrels.remove(barrel)
                    game.player.score += 10
            
            game.check_collisions()
            game.draw_game()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
