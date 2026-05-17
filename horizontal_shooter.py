import pygame
import os
import random
import sys
import math

# 初始化pygame
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

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 100)
PURPLE = (200, 100, 200)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
DARK_GRAY = (30, 30, 30)

# 设置屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("横版射击游戏")
clock = pygame.time.Clock()

# 字体
font = get_chinese_font(36)
small_font = get_chinese_font(24)

class Player:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.width = 50
        self.height = 40
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.shoot_cooldown = 0
        self.weapon_level = 1
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.invincible = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed

        # 边界检测
        self.x = max(0, min(self.x, SCREEN_WIDTH // 3))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))

        # 更新射击冷却
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # 更新连击计时器
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

        # 更新无敌时间
        if self.invincible > 0:
            self.invincible -= 1

    def shoot(self):
        if self.shoot_cooldown <= 0:
            bullets = []
            if self.weapon_level == 1:
                bullets.append(Bullet(self.x + self.width, self.y + self.height // 2, 10, 0))
            elif self.weapon_level == 2:
                bullets.append(Bullet(self.x + self.width, self.y + self.height // 2 - 10, 10, 0))
                bullets.append(Bullet(self.x + self.width, self.y + self.height // 2 + 10, 10, 0))
            elif self.weapon_level >= 3:
                bullets.append(Bullet(self.x + self.width, self.y + self.height // 2, 10, 0))
                bullets.append(Bullet(self.x + self.width, self.y + self.height // 2 - 15, 10, -1))
                bullets.append(Bullet(self.x + self.width, self.y + self.height // 2 + 15, 10, 1))
            
            self.shoot_cooldown = max(5, 15 - self.weapon_level * 2)
            return bullets
        return []

    def take_damage(self, amount):
        if self.invincible <= 0:
            self.health -= amount
            self.invincible = 60
            self.combo = 0
            if self.health < 0:
                self.health = 0

    def add_combo(self):
        self.combo += 1
        self.combo_timer = 120
        self.score += 10 * (1 + self.combo // 5)

    def draw(self, surface):
        if self.invincible > 0 and self.invincible % 4 < 2:
            return
        # 绘制飞船主体
        pygame.draw.polygon(surface, BLUE, [
            (self.x, self.y + self.height // 2),
            (self.x + self.width, self.y),
            (self.x + self.width - 10, self.y + self.height // 2),
            (self.x + self.width, self.y + self.height)
        ])
        # 绘制机翼
        pygame.draw.rect(surface, CYAN, (self.x + 10, self.y + 5, 20, 5))
        pygame.draw.rect(surface, CYAN, (self.x + 10, self.y + self.height - 10, 20, 5))
        # 绘制引擎火焰
        pygame.draw.rect(surface, ORANGE, (self.x - 10, self.y + self.height // 2 - 5, 15, 10))

class Bullet:
    def __init__(self, x, y, speed_x, speed_y):
        self.x = x
        self.y = y
        self.width = 12
        self.height = 6
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.active = True

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x > SCREEN_WIDTH or self.x < 0 or self.y > SCREEN_HEIGHT or self.y < 0:
            self.active = False

    def draw(self, surface):
        pygame.draw.rect(surface, YELLOW, (self.x, self.y, self.width, self.height))

class EnemyBullet:
    def __init__(self, x, y, speed_x, speed_y):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 8
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.active = True

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x > SCREEN_WIDTH or self.x < 0 or self.y > SCREEN_HEIGHT or self.y < 0:
            self.active = False

    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x + self.width // 2), int(self.y + self.height // 2)), self.width // 2)

class Enemy:
    def __init__(self, enemy_type, x=None, y=None):
        self.type = enemy_type
        if x is None:
            self.x = SCREEN_WIDTH
        else:
            self.x = x
        if y is None:
            self.y = random.randint(50, SCREEN_HEIGHT - 100)
        else:
            self.y = y
        self.width = 40
        self.height = 40
        self.speed_x = -3
        self.speed_y = 0
        self.health = 30
        self.max_health = 30
        self.shoot_cooldown = 0
        self.move_timer = 0
        self.points = 10

        if enemy_type == 'fast':
            self.speed_x = -5
            self.health = 20
            self.max_health = 20
            self.width = 30
            self.height = 30
            self.points = 15
        elif enemy_type == 'big':
            self.speed_x = -1.5
            self.health = 80
            self.max_health = 80
            self.width = 60
            self.height = 60
            self.points = 30
        elif enemy_type == 'zigzag':
            self.speed_x = -2
            self.health = 40
            self.max_health = 40
            self.points = 20

    def update(self):
        self.x += self.speed_x
        self.move_timer += 1

        if self.type == 'zigzag':
            self.speed_y = math.sin(self.move_timer * 0.1) * 3
            self.y += self.speed_y
            self.y = max(50, min(self.y, SCREEN_HEIGHT - 100))

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def shoot(self):
        if self.shoot_cooldown <= 0 and self.type in ['big', 'zigzag']:
            self.shoot_cooldown = 90
            return [EnemyBullet(self.x, self.y + self.height // 2, -6, 0)]
        return []

    def draw(self, surface):
        if self.type == 'fast':
            pygame.draw.polygon(surface, GREEN, [
                (self.x + self.width, self.y + self.height // 2),
                (self.x, self.y),
                (self.x + 10, self.y + self.height // 2),
                (self.x, self.y + self.height)
            ])
        elif self.type == 'big':
            pygame.draw.rect(surface, PURPLE, (self.x, self.y, self.width, self.height))
            pygame.draw.circle(surface, RED, (int(self.x + 15), int(self.y + self.height // 2)), 8)
        elif self.type == 'zigzag':
            pygame.draw.ellipse(surface, ORANGE, (self.x, self.y, self.width, self.height))
        else:
            pygame.draw.rect(surface, RED, (self.x, self.y, self.width, self.height))

        # 血条
        if self.health < self.max_health:
            pygame.draw.rect(surface, RED, (self.x, self.y - 10, self.width, 5))
            pygame.draw.rect(surface, GREEN, (self.x, self.y - 10, self.width * (self.health / self.max_health), 5))

class Boss:
    def __init__(self):
        self.x = SCREEN_WIDTH + 100
        self.y = SCREEN_HEIGHT // 2 - 75
        self.width = 150
        self.height = 150
        self.speed_x = -1
        self.speed_y = 0
        self.health = 500
        self.max_health = 500
        self.shoot_cooldown = 0
        self.phase = 1
        self.move_timer = 0
        self.active = True
        self.entering = True

    def update(self):
        if self.entering:
            self.x -= 2
            if self.x <= SCREEN_WIDTH - 200:
                self.entering = False
            return

        self.move_timer += 1
        self.speed_y = math.sin(self.move_timer * 0.02) * 2
        self.y += self.speed_y
        self.y = max(50, min(self.y, SCREEN_HEIGHT - self.height - 50))

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def shoot(self):
        if self.shoot_cooldown <= 0 and not self.entering:
            bullets = []
            if self.phase == 1:
                self.shoot_cooldown = 60
                bullets.append(EnemyBullet(self.x, self.y + 50, -8, 0))
                bullets.append(EnemyBullet(self.x, self.y + self.height - 50, -8, 0))
            elif self.phase == 2:
                self.shoot_cooldown = 40
                bullets.append(EnemyBullet(self.x, self.y + self.height // 2, -7, -2))
                bullets.append(EnemyBullet(self.x, self.y + self.height // 2, -7, 0))
                bullets.append(EnemyBullet(self.x, self.y + self.height // 2, -7, 2))
            else:
                self.shoot_cooldown = 30
                for i in range(5):
                    angle = math.radians(-40 + i * 20)
                    bullets.append(EnemyBullet(self.x, self.y + self.height // 2, math.cos(angle) * 6, math.sin(angle) * 6))
            return bullets
        return []

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 200 and self.phase < 3:
            self.phase = 3
        elif self.health <= 350 and self.phase < 2:
            self.phase = 2

    def draw(self, surface):
        # 主体
        pygame.draw.rect(surface, RED, (self.x, self.y, self.width, self.height))
        # 眼睛
        pygame.draw.circle(surface, YELLOW, (int(self.x + 40), int(self.y + 40)), 20)
        pygame.draw.circle(surface, YELLOW, (int(self.x + 110), int(self.y + 40)), 20)
        pygame.draw.circle(surface, BLACK, (int(self.x + 40), int(self.y + 40)), 10)
        pygame.draw.circle(surface, BLACK, (int(self.x + 110), int(self.y + 40)), 10)
        # 武器
        pygame.draw.rect(surface, DARK_GRAY, (self.x, self.y + 50, 30, 20))
        pygame.draw.rect(surface, DARK_GRAY, (self.x, self.y + 80, 30, 20))

        # 血条
        pygame.draw.rect(surface, BLACK, (SCREEN_WIDTH // 2 - 150, 20, 300, 25))
        pygame.draw.rect(surface, RED, (SCREEN_WIDTH // 2 - 148, 22, 296 * (self.health / self.max_health), 21))
        boss_text = small_font.render("BOSS", True, WHITE)
        screen.blit(boss_text, (SCREEN_WIDTH // 2 - 25, 25))

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        self.speed_x = -2
        self.type = random.choice(['weapon', 'health', 'score'])
        self.active = True
        self.anim_timer = 0

    def update(self):
        self.x += self.speed_x
        self.anim_timer += 1
        if self.x < -50:
            self.active = False

    def draw(self, surface):
        y_offset = math.sin(self.anim_timer * 0.1) * 3
        if self.type == 'weapon':
            color = PURPLE
        elif self.type == 'health':
            color = GREEN
        else:
            color = YELLOW
        pygame.draw.rect(surface, color, (self.x, self.y + y_offset, self.width, self.height))
        pygame.draw.rect(surface, WHITE, (self.x + 5, self.y + 5 + y_offset, 15, 15), 2)

class Game:
    def __init__(self):
        self.player = Player()
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.powerups = []
        self.boss = None
        self.level = 1
        self.spawn_timer = 0
        self.boss_spawned = False
        self.game_over = False
        self.win = False
        self.stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(50)]

    def spawn_enemy(self):
        types = ['normal', 'fast', 'big', 'zigzag']
        weights = [40 - self.level * 3, 20 + self.level, 10 + self.level, 10 + self.level]
        total = sum(weights)
        r = random.randint(0, total)
        cumulative = 0
        for t, w in zip(types, weights):
            cumulative += w
            if r <= cumulative:
                self.enemies.append(Enemy(t))
                break

    def update(self):
        if self.game_over or self.win:
            return

        self.player.update()

        # 射击
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.bullets.extend(self.player.shoot())

        # 更新子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)

        # 更新敌人子弹
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.enemy_bullets.remove(bullet)

        # 生成敌人
        self.spawn_timer += 1
        spawn_rate = max(30, 90 - self.level * 5)
        if self.spawn_timer >= spawn_rate and not self.boss_spawned:
            self.spawn_timer = 0
            self.spawn_enemy()

        # 更新敌人
        for enemy in self.enemies[:]:
            enemy.update()
            self.enemy_bullets.extend(enemy.shoot())
            if enemy.x < -100:
                self.enemies.remove(enemy)

        # Boss战
        if self.player.score >= 500 and not self.boss_spawned:
            self.boss_spawned = True
            self.boss = Boss()

        if self.boss is not None:
            self.boss.update()
            self.enemy_bullets.extend(self.boss.shoot())
            if self.boss.health <= 0:
                self.player.score += 1000
                self.boss = None
                self.win = True

        # 碰撞检测 - 玩家子弹击中敌人
        for bullet in self.bullets[:]:
            bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)
            
            for enemy in self.enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if bullet_rect.colliderect(enemy_rect):
                    enemy.health -= 20
                    bullet.active = False
                    if enemy.health <= 0:
                        self.player.add_combo()
                        self.player.score += enemy.points
                        if random.random() < 0.2:
                            self.powerups.append(PowerUp(enemy.x, enemy.y))
                        self.enemies.remove(enemy)
                    break

            # 玩家子弹击中boss
            if self.boss is not None:
                boss_rect = pygame.Rect(self.boss.x, self.boss.y, self.boss.width, self.boss.height)
                if bullet_rect.colliderect(boss_rect):
                    self.boss.take_damage(10)
                    bullet.active = False

        # 碰撞检测 - 敌人子弹击中玩家
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        for bullet in self.enemy_bullets[:]:
            bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)
            if player_rect.colliderect(bullet_rect):
                self.player.take_damage(15)
                bullet.active = False

        # 碰撞检测 - 敌人撞上玩家
        for enemy in self.enemies[:]:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            if player_rect.colliderect(enemy_rect):
                self.player.take_damage(25)
                self.enemies.remove(enemy)

        # 碰撞检测 - 收集强化道具
        for powerup in self.powerups[:]:
            powerup.update()
            powerup_rect = pygame.Rect(powerup.x, powerup.y, powerup.width, powerup.height)
            if player_rect.colliderect(powerup_rect):
                if powerup.type == 'weapon':
                    self.player.weapon_level = min(3, self.player.weapon_level + 1)
                elif powerup.type == 'health':
                    self.player.health = min(self.player.max_health, self.player.health + 30)
                elif powerup.type == 'score':
                    self.player.score += 50
                self.powerups.remove(powerup)
            elif not powerup.active:
                self.powerups.remove(powerup)

        # 游戏结束检查
        if self.player.health <= 0:
            self.game_over = True

        # 更新背景星星
        for i in range(len(self.stars)):
            self.stars[i] = (self.stars[i][0] - 1, self.stars[i][1])
            if self.stars[i][0] < 0:
                self.stars[i] = (SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT))

    def draw(self):
        screen.fill(BLACK)

        # 绘制背景星星
        for x, y in self.stars:
            pygame.draw.circle(screen, WHITE, (x, y), 1)

        # 绘制UI
        self.draw_ui()

        # 绘制玩家
        self.player.draw(screen)

        # 绘制子弹
        for bullet in self.bullets:
            bullet.draw(screen)

        # 绘制敌人子弹
        for bullet in self.enemy_bullets:
            bullet.draw(screen)

        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(screen)

        # 绘制Boss
        if self.boss is not None:
            self.boss.draw(screen)

        # 绘制强化道具
        for powerup in self.powerups:
            powerup.draw(screen)

        # 游戏结束画面
        if self.game_over:
            game_over_text = font.render("游戏结束! R键重新开始", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2))
        elif self.win:
            win_text = font.render("恭喜通关! R键重新开始", True, GREEN)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2))

    def draw_ui(self):
        # 生命值
        pygame.draw.rect(screen, BLACK, (10, 10, 104, 24))
        pygame.draw.rect(screen, RED, (12, 12, self.player.health, 20))
        health_text = small_font.render(f"HP", True, WHITE)
        screen.blit(health_text, (120, 12))

        # 分数
        score_text = font.render(f"分数: {self.player.score}", True, WHITE)
        screen.blit(score_text, (10, 40))

        # 连击
        if self.player.combo > 0:
            combo_text = font.render(f"连击 x{self.player.combo}", True, YELLOW)
            screen.blit(combo_text, (10, 70))

        # 武器等级
        weapon_text = small_font.render(f"武器等级: {self.player.weapon_level}", True, CYAN)
        screen.blit(weapon_text, (10, 100))

    def reset(self):
        self.__init__()

def main():
    game = Game()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.reset()

        game.update()
        game.draw()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
