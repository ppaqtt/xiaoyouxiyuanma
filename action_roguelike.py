
import pygame
import random
import sys

# 初始化Pygame
pygame.init()

# 窗口设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("横版动作Roguelike - 细胞地牢")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 200)
GRAY = (100, 100, 100)
DARK_GRAY = (60, 60, 60)
GOLD = (255, 215, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
LIGHT_BLUE = (100, 200, 255)

# 字体
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# 玩家类
class Player:
    def __init__(self):
        self.x = 100
        self.y = 400
        self.width = 40
        self.height = 60
        self.vx = 0
        self.vy = 0
        self.speed = 5
        self.jump_power = -15
        self.gravity = 0.8
        self.on_ground = False
        self.max_hp = 100
        self.hp = 100
        self.damage = 10
        self.attack_cooldown = 0
        self.combo = 0
        self.combo_timer = 0
        self.facing_right = True
        self.invincible = 0
        self.attacking = False
        self.attack_timer = 0
        self.permanent_upgrades = {}
        self.items = []
        self.current_weapon = None
        
    def update(self, platforms, enemies):
        keys = pygame.key.get_pressed()
        
        # 移动
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -self.speed
            self.facing_right = False
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = self.speed
            self.facing_right = True
        else:
            self.vx = 0
        
        # 跳跃
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vy = self.jump_power
        
        # 重力
        self.vy += self.gravity
        
        # 更新位置
        self.x += self.vx
        self.y += self.vy
        
        # 平台碰撞
        self.on_ground = False
        for plat in platforms:
            if (self.x + self.width &gt; plat.x and 
                self.x &lt; plat.x + plat.width and 
                self.y + self.height &gt; plat.y and 
                self.y + self.height &lt; plat.y + plat.height + 10 and 
                self.vy &gt;= 0):
                self.y = plat.y - self.height
                self.vy = 0
                self.on_ground = True
        
        # 边界检查
        if self.x &lt; 0:
            self.x = 0
        if self.x &gt; WIDTH - self.width:
            self.x = WIDTH - self.width
        if self.y &gt; HEIGHT:
            self.hp = 0
        
        # 更新状态
        if self.attack_cooldown &gt; 0:
            self.attack_cooldown -= 1
        
        if self.combo_timer &gt; 0:
            self.combo_timer -= 1
        else:
            self.combo = 0
        
        if self.invincible &gt; 0:
            self.invincible -= 1
        
        if self.attacking:
            self.attack_timer -= 1
            if self.attack_timer &lt;= 0:
                self.attacking = False
    
    def attack(self):
        if self.attack_cooldown &lt;= 0:
            self.attacking = True
            self.attack_timer = 15
            self.attack_cooldown = 25
            self.combo += 1
            self.combo_timer = 60
            return self.combo
    
    def draw(self, surface):
        color = BLUE
        if self.invincible &gt; 0:
            if self.invincible % 4 &lt; 2:
                color = WHITE
        
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))
        
        # 攻击范围
        if self.attacking:
            attack_width = 60
            attack_x = self.x + self.width if self.facing_right else self.x - attack_width
            pygame.draw.rect(surface, ORANGE, (attack_x, self.y, attack_width, self.height))

# 敌人类
class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        
        if enemy_type == "slime":
            self.width = 40
            self.height = 30
            self.hp = 20
            self.damage = 5
            self.speed = 1
            self.color = GREEN
        elif enemy_type == "goblin":
            self.width = 35
            self.height = 50
            self.hp = 35
            self.damage = 8
            self.speed = 2
            self.color = PURPLE
        elif enemy_type == "skeleton":
            self.width = 30
            self.height = 55
            self.hp = 25
            self.damage = 10
            self.speed = 1.5
            self.color = GRAY
        
        self.vx = random.choice([-1, 1]) * self.speed
        self.vy = 0
        self.max_hp = self.hp
    
    def update(self, platforms, player):
        # 向玩家移动
        if abs(player.x - self.x) &lt; 300:
            if player.x &gt; self.x:
                self.vx = self.speed
            else:
                self.vx = -self.speed
        
        self.x += self.vx
        self.vy += 0.5
        self.y += self.vy
        
        # 平台碰撞
        for plat in platforms:
            if (self.x + self.width &gt; plat.x and 
                self.x &lt; plat.x + plat.width and 
                self.y + self.height &gt; plat.y and 
                self.y + self.height &lt; plat.y + plat.height + 10 and 
                self.vy &gt;= 0):
                self.y = plat.y - self.height
                self.vy = 0
        
        if self.x &lt; 0 or self.x &gt; WIDTH - self.width:
            self.vx *= -1
            self.x += self.vx
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        
        # 血条
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, DARK_GRAY, (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(surface, RED, (self.x, self.y - 10, self.width * hp_ratio, 5))

# 道具类
class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.item_type = item_type
        
        if item_type == "health":
            self.color = GREEN
        elif item_type == "damage":
            self.color = RED
        elif item_type == "speed":
            self.color = LIGHT_BLUE
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

# 平台类
class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def draw(self, surface):
        pygame.draw.rect(surface, GRAY, (self.x, self.y, self.width, self.height))

# 生成房间
def generate_room():
    platforms = []
    enemies = []
    items = []
    
    platforms.append(Platform(0, 550, WIDTH, 50))
    
    num_platforms = random.randint(3, 6)
    for _ in range(num_platforms):
        x = random.randint(50, WIDTH - 200)
        y = random.randint(200, 450)
        w = random.randint(100, 200)
        platforms.append(Platform(x, y, w, 20))
    
    num_enemies = random.randint(2, 5)
    enemy_types = ["slime", "goblin", "skeleton"]
    for _ in range(num_enemies):
        x = random.randint(200, WIDTH - 100)
        y = random.randint(100, 400)
        enemy_type = random.choice(enemy_types)
        enemies.append(Enemy(x, y, enemy_type))
    
    if random.random() &lt; 0.5:
        item_types = ["health", "damage", "speed"]
        x = random.randint(100, WIDTH - 100)
        y = random.randint(200, 450)
        items.append(Item(x, y, random.choice(item_types)))
    
    return platforms, enemies, items

# 游戏状态
class GameState:
    def __init__(self):
        self.state = "menu"
        self.player = Player()
        self.level = 1
        self.kills = 0
        self.platforms = []
        self.enemies = []
        self.items = []
        self.exit_x = 0
        self.exit_y = 0
        self.generate_level()
    
    def generate_level(self):
        self.platforms, self.enemies, self.items = generate_room()
        self.exit_x = WIDTH - 80
        self.exit_y = 490
        self.player.x = 100
        self.player.y = 400
    
    def reset(self):
        self.__init__()

game = GameState()

# 主循环
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if game.state == "menu":
                if event.key == pygame.K_RETURN:
                    game.state = "playing"
            elif game.state == "playing":
                if event.key == pygame.K_j or event.key == pygame.K_z:
                    combo = game.player.attack()
                    if combo:
                        # 检测攻击碰撞
                        attack_width = 60
                        attack_x = game.player.x + game.player.width if game.player.facing_right else game.player.x - attack_width
                        attack_rect = pygame.Rect(attack_x, game.player.y, attack_width, game.player.height)
                        
                        for enemy in game.enemies[:]:
                            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                            if attack_rect.colliderect(enemy_rect):
                                enemy.hp -= game.player.damage * (1 + combo * 0.2)
                                if enemy.hp &lt;= 0:
                                    game.enemies.remove(enemy)
                                    game.kills += 1
            elif game.state == "gameover" or game.state == "victory":
                if event.key == pygame.K_RETURN:
                    game.reset()
    
    if game.state == "menu":
        title = font_large.render("细胞地牢", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        instr = font_medium.render("按回车键开始", True, WHITE)
        screen.blit(instr, (WIDTH//2 - instr.get_width()//2, 250))
        controls = font_small.render("A/D 移动, 空格 跳跃, J 攻击", True, GRAY)
        screen.blit(controls, (WIDTH//2 - controls.get_width()//2, 350))
    
    elif game.state == "playing":
        game.player.update(game.platforms, game.enemies)
        for enemy in game.enemies:
            enemy.update(game.platforms, game.player)
        
        # 敌人碰撞
        player_rect = pygame.Rect(game.player.x, game.player.y, game.player.width, game.player.height)
        for enemy in game.enemies:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            if player_rect.colliderect(enemy_rect) and game.player.invincible &lt;= 0:
                game.player.hp -= enemy.damage
                game.player.invincible = 60
                game.player.vx = -10 if game.player.facing_right else 10
        
        # 道具碰撞
        for item in game.items[:]:
            item_rect = pygame.Rect(item.x, item.y, item.width, item.height)
            if player_rect.colliderect(item_rect):
                if item.item_type == "health":
                    game.player.hp = min(game.player.hp + 20, game.player.max_hp)
                elif item.item_type == "damage":
                    game.player.damage += 2
                elif item.item_type == "speed":
                    game.player.speed += 0.5
                game.items.remove(item)
        
        # 出口检测
        exit_rect = pygame.Rect(game.exit_x, game.exit_y, 60, 60)
        if len(game.enemies) == 0 and player_rect.colliderect(exit_rect):
            game.level += 1
            game.generate_level()
            if game.level &gt; 5:
                game.state = "victory"
        
        # 死亡检测
        if game.player.hp &lt;= 0:
            game.state = "gameover"
        
        # 绘制
        for plat in game.platforms:
            plat.draw(screen)
        
        for item in game.items:
            item.draw(screen)
        
        for enemy in game.enemies:
            enemy.draw(screen)
        
        game.player.draw(screen)
        
        if len(game.enemies) == 0:
            pygame.draw.rect(screen, GOLD, (game.exit_x, game.exit_y, 60, 60))
            exit_text = font_small.render("出口", True, BLACK)
            screen.blit(exit_text, (game.exit_x + 10, game.exit_y + 20))
        
        # UI
        hp_text = font_medium.render(f"HP: {game.player.hp}/{game.player.max_hp}", True, GREEN)
        screen.blit(hp_text, (20, 20))
        level_text = font_medium.render(f"层数: {game.level}", True, WHITE)
        screen.blit(level_text, (20, 60))
        kills_text = font_medium.render(f"击杀: {game.kills}", True, WHITE)
        screen.blit(kills_text, (20, 100))
        
        if game.player.combo &gt; 1:
            combo_text = font_large.render(f"连击 x{game.player.combo}!", True, GOLD)
            screen.blit(combo_text, (WIDTH//2 - combo_text.get_width()//2, 50))
        
        dmg_text = font_small.render(f"伤害: {game.player.damage}", True, RED)
        screen.blit(dmg_text, (WIDTH - 150, 20))
    
    elif game.state == "gameover":
        title = font_large.render("游戏结束", True, RED)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        level_text = font_medium.render(f"到达第 {game.level} 层", True, WHITE)
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, 280))
        kills_text = font_medium.render(f"击杀: {game.kills}", True, WHITE)
        screen.blit(kills_text, (WIDTH//2 - kills_text.get_width()//2, 320))
        restart = font_medium.render("按回车重新开始", True, GOLD)
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 400))
    
    elif game.state == "victory":
        title = font_large.render("胜利！", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        victory_text = font_medium.render("你逃出了地牢！", True, WHITE)
        screen.blit(victory_text, (WIDTH//2 - victory_text.get_width()//2, 280))
        kills_text = font_medium.render(f"总击杀: {game.kills}", True, WHITE)
        screen.blit(kills_text, (WIDTH//2 - kills_text.get_width()//2, 320))
        restart = font_medium.render("按回车再来一局", True, GOLD)
        screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 400))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
