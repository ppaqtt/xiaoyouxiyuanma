import pygame
import os
import random
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

WIDTH, HEIGHT = 900, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (60, 60, 80)
RED = (255, 50, 50)
PURPLE = (150, 50, 200)
CYAN = (0, 200, 255)
GREEN = (50, 200, 100)
ORANGE = (255, 150, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("灵魂收割者")
clock = pygame.time.Clock()
font = get_chinese_font(28)
big_font = get_chinese_font(50)
small_font = get_chinese_font(20)

class SoulReaper:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed = 3.5
        self.souls = 0
        self.max_souls = 5
        self.hp = 100
        self.max_hp = 100
        self.dash_cooldown = 0
        self.invincible = 0
        self.level = 1
        self.soul_bank = 0
        self.upgrades = 0
    
    def update(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1
        
        if dx != 0 or dy != 0:
            length = math.sqrt(dx**2 + dy**2)
            self.x += (dx / length) * self.speed
            self.y += (dy / length) * self.speed
        
        self.x = max(30, min(WIDTH-30, self.x))
        self.y = max(30, min(HEIGHT-30, self.y))
        
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.invincible > 0:
            self.invincible -= 1
    
    def dash(self, mouse_pos):
        if self.dash_cooldown == 0:
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                self.x += (dx / dist) * 100
                self.y += (dy / dist) * 100
                self.dash_cooldown = 60
                self.invincible = 20
    
    def can_collect(self):
        return self.souls < self.max_souls
    
    def collect_soul(self):
        self.souls += 1
        self.soul_bank += 1
    
    def release_souls(self):
        released = self.souls
        self.souls = 0
        return released
    
    def draw(self):
        color = WHITE if self.invincible == 0 or (self.invincible // 3) % 2 == 0 else (200, 200, 200)
        
        for i in range(self.souls):
            angle = i * (math.pi * 2 / self.max_souls)
            sx = self.x + math.cos(angle) * 25
            sy = self.y + math.sin(angle) * 25
            pygame.draw.circle(screen, CYAN, (int(sx), int(sy)), 6)
        
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 22)
        pygame.draw.circle(screen, PURPLE, (int(self.x), int(self.y)), 22, 3)
        
        hp_width = 50
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, RED, (int(self.x)-25, int(self.y)-38, hp_width, 6))
        pygame.draw.rect(screen, GREEN, (int(self.x)-25, int(self.y)-38, int(hp_width*hp_ratio), 6))

class Soul:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.pulse = 0
        self.target_reaper = None
        self.vx = 0
        self.vy = 0
    
    def update(self, reaper):
        self.pulse += 0.1
        
        dx = reaper.x - self.x
        dy = reaper.y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist < 120 and reaper.can_collect():
            self.vx += (dx / dist) * 0.5
            self.vy += (dy / dist) * 0.5
        
        self.x += self.vx * 0.9
        self.y += self.vy * 0.9
    
    def draw(self):
        size = self.radius + math.sin(self.pulse) * 2
        pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), int(size))
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), int(size * 0.6))

class Enemy:
    def __init__(self, x, y, e_type):
        self.x = x
        self.y = y
        self.e_type = e_type
        self.hp = 30 if e_type == "basic" else 60 if e_type == "tank" else 20
        self.max_hp = self.hp
        self.speed = 1.2 if e_type == "basic" else 0.8 if e_type == "tank" else 2.5
        self.damage = 10 if e_type == "basic" else 20 if e_type == "tank" else 5
        self.color = RED if e_type == "basic" else ORANGE if e_type == "tank" else (255, 200, 0)
        self.radius = 18 if e_type == "basic" else 25 if e_type == "tank" else 12
        self.death_timer = 0
        self.dead = False
    
    def update(self, reaper):
        if self.dead:
            self.death_timer += 1
            return
        
        dx = reaper.x - self.x
        dy = reaper.y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
    
    def draw(self):
        if self.dead:
            alpha = max(0, 255 - self.death_timer * 10)
            pygame.draw.circle(screen, (*self.color, alpha), (int(self.x), int(self.y)), self.radius - self.death_timer // 2)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            
            hp_ratio = self.hp / self.max_hp
            pygame.draw.rect(screen, RED, (int(self.x)-15, int(self.y)-self.radius-10, 30, 5))
            pygame.draw.rect(screen, GREEN, (int(self.x)-15, int(self.y)-self.radius-10, int(30*hp_ratio), 5))

class Portal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 50
        self.pulse = 0
        self.cooldown = 0
    
    def update(self):
        self.pulse += 0.05
        if self.cooldown > 0:
            self.cooldown -= 1
    
    def draw(self):
        color = PURPLE if self.cooldown == 0 else GRAY
        size = self.radius + math.sin(self.pulse) * 8
        
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(size), 4)
        pygame.draw.circle(screen, (*color, 50), (int(self.x), int(self.y)), int(size * 0.8))
        
        if self.cooldown > 0:
            cd_text = small_font.render(f"{int(self.cooldown/10)}", True, WHITE)
            screen.blit(cd_text, (self.x - 8, self.y - 10))

class Explosion:
    def __init__(self, x, y, power):
        self.x = x
        self.y = y
        self.power = power
        self.radius = 0
        self.max_radius = 30 + power * 10
    
    def update(self):
        self.radius += 5
        return self.radius < self.max_radius
    
    def draw(self):
        alpha = int(255 * (1 - self.radius / self.max_radius))
        pygame.draw.circle(screen, (255, 100, 50, alpha), (int(self.x), int(self.y)), int(self.radius), 3)
        pygame.draw.circle(screen, (255, 200, 0, alpha), (int(self.x), int(self.y)), int(self.radius * 0.6))

def soul_reaper_game():
    reaper = SoulReaper()
    souls = []
    enemies = []
    portals = []
    explosions = []
    score = 0
    wave = 1
    spawn_timer = 0
    game_over = False
    wave_complete = False
    
    portals.append(Portal(100, HEIGHT // 2))
    portals.append(Portal(WIDTH - 100, HEIGHT // 2))
    
    for _ in range(3):
        ex = random.randint(100, WIDTH-100)
        ey = random.randint(100, HEIGHT-100)
        enemies.append(Enemy(ex, ey, "basic"))
    
    while not game_over:
        screen.fill(BLACK)
        
        for x in range(0, WIDTH, 40):
            pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 40):
            pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y), 1)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    reaper.dash(pygame.mouse.get_pos())
                elif event.button == 3:
                    if reaper.souls > 0:
                        power = reaper.release_souls()
                        explosions.append(Explosion(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], power))
        
        keys = pygame.key.get_pressed()
        reaper.update(keys)
        
        for portal in portals:
            portal.update()
        
        spawn_timer += 1
        if len(enemies) < 3 + wave and spawn_timer > 120 - wave * 8:
            spawn_timer = 0
            ex = random.choice([50, WIDTH-50])
            ey = random.randint(100, HEIGHT-100)
            
            if wave >= 3 and random.random() < 0.2:
                e_type = "tank"
            elif wave >= 2 and random.random() < 0.3:
                e_type = "swift"
            else:
                e_type = "basic"
            
            enemies.append(Enemy(ex, ey, e_type))
        
        if len(enemies) == 0 and not wave_complete:
            wave_complete = True
            wave += 1
        
        if wave_complete and keys[pygame.K_SPACE]:
            wave_complete = False
            for _ in range(2 + wave):
                ex = random.choice([50, WIDTH-50])
                ey = random.randint(100, HEIGHT-100)
                e_type = random.choice(["basic", "basic", "swift", "tank"])
                enemies.append(Enemy(ex, ey, e_type))
        
        for enemy in enemies[:]:
            enemy.update(reaper)
            
            if not enemy.dead:
                dist = math.sqrt((reaper.x - enemy.x)**2 + (reaper.y - enemy.y)**2)
                if dist < reaper.radius + enemy.radius and reaper.invincible == 0:
                    reaper.hp -= enemy.damage
                    reaper.invincible = 45
            
            if enemy.dead and enemy.death_timer > 20:
                enemies.remove(enemy)
                continue
            
            for expl in explosions:
                if not enemy.dead:
                    d = math.sqrt((enemy.x - expl.x)**2 + (enemy.y - expl.y)**2)
                    if d < expl.radius + enemy.radius:
                        enemy.hp -= expl.power * 3
                        if enemy.hp <= 0:
                            enemy.dead = True
                            score += 20 if enemy.e_type == "basic" else 50 if enemy.e_type == "tank" else 10
                            souls.append(Soul(enemy.x, enemy.y))
        
        for expl in explosions[:]:
            if not expl.update():
                explosions.remove(expl)
        
        for soul in souls[:]:
            soul.update(reaper)
            
            dist = math.sqrt((reaper.x - soul.x)**2 + (reaper.y - soul.y)**2)
            if dist < 25 and reaper.can_collect():
                reaper.collect_soul()
                souls.remove(soul)
        
        for portal in portals:
            if portal.cooldown == 0 and reaper.souls > 0:
                dist = math.sqrt((reaper.x - portal.x)**2 + (reaper.y - portal.y)**2)
                if dist < portal.radius:
                    score += reaper.souls * 15
                    reaper.souls = 0
                    portal.cooldown = 80
        
        if reaper.soul_bank >= 10 and reaper.upgrades == 0:
            reaper.max_souls = 7
            reaper.upgrades = 1
        if reaper.soul_bank >= 25 and reaper.upgrades == 1:
            reaper.max_hp = 150
            reaper.hp = reaper.max_hp
            reaper.upgrades = 2
        if reaper.soul_bank >= 50 and reaper.upgrades == 2:
            reaper.speed = 4.5
            reaper.upgrades = 3
        
        for portal in portals:
            portal.draw()
        
        for soul in souls:
            soul.draw()
        
        for enemy in enemies:
            enemy.draw()
        
        for expl in explosions:
            expl.draw()
        
        reaper.draw()
        
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 70))
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        wave_text = font.render(f"波次: {wave}", True, ORANGE)
        screen.blit(wave_text, (150, 10))
        
        soul_text = font.render(f"灵魂: {reaper.souls}/{reaper.max_souls}", True, CYAN)
        screen.blit(soul_text, (10, 40))
        
        upgrade_text = small_font.render(f"收集灵魂: {reaper.soul_bank}", True, PURPLE)
        screen.blit(upgrade_text, (150, 45))
        
        if wave_complete:
            next_text = big_font.render(f"波次 {wave-1} 完成! 按空格继续", True, GREEN)
            screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2))
        
        inst_text = small_font.render("WASD移动 | 左键冲刺 | 右键释放灵魂", True, WHITE)
        screen.blit(inst_text, (WIDTH-350, 50))
        
        if reaper.hp <= 0:
            game_over = True
        
        pygame.display.flip()
        clock.tick(60)
    
    screen.fill(BLACK)
    game_over_text = big_font.render("游戏结束!", True, RED)
    screen.blit(game_over_text, (WIDTH//2 - 100, HEIGHT//2 - 50))
    
    final_score = font.render(f"最终得分: {score}", True, WHITE)
    screen.blit(final_score, (WIDTH//2 - 80, HEIGHT//2 + 20))
    
    final_wave = font.render(f"最终波次: {wave}", True, ORANGE)
    screen.blit(final_wave, (WIDTH//2 - 80, HEIGHT//2 + 60))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    soul_reaper_game()
