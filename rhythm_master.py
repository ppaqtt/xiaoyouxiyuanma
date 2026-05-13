import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 700

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("音乐节奏大师")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 60)

class Note:
    def __init__(self, lane, speed):
        self.lane = lane
        self.y = -50
        self.speed = speed
        self.size = 50
        self.hit = False
    
    def update(self):
        self.y += self.speed
    
    def draw(self):
        if not self.hit:
            x = 100 + self.lane * 150
            colors = [RED, GREEN, BLUE, YELLOW]
            pygame.draw.rect(screen, colors[self.lane], 
                           (x, self.y, self.size, self.size), border_radius=10)

class HitZone:
    def __init__(self, lane):
        self.lane = lane
        self.y = HEIGHT - 100
        self.x = 100 + lane * 150
        self.width = 50
        self.height = 80
        self.active = False
        self.timer = 0
    
    def draw(self):
        color = WHITE if not self.active else GREEN
        pygame.draw.rect(screen, color, 
                        (self.x, self.y, self.width, self.height), 3, border_radius=5)
    
    def trigger(self):
        self.active = True
        self.timer = 10
    
    def update(self):
        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                self.active = False

def rhythm_master():
    lanes = 4
    notes = []
    hit_zones = [HitZone(i) for i in range(lanes)]
    score = 0
    combo = 0
    max_combo = 0
    bpm = 120
    beat_interval = 60 / bpm * 60
    last_beat = 0
    game_time = 0
    perfects = 0
    goods = 0
    misses = 0
    game_over = False
    
    key_map = [pygame.K_LEFT, pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT]
    key_names = ["←", "↓", "↑", "→"]
    
    while not game_over:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                for i, key in enumerate(key_map):
                    if event.key == key:
                        hit_zone = hit_zones[i]
                        found = False
                        for note in notes:
                            if note.lane == i and not note.hit:
                                dist = abs(note.y + note.size - hit_zone.y)
                                if dist < 30:
                                    note.hit = True
                                    found = True
                                    if dist < 15:
                                        score += 100 * (1 + combo // 10)
                                        combo += 1
                                        perfects += 1
                                        hit_zone.trigger()
                                    elif dist < 30:
                                        score += 50 * (1 + combo // 10)
                                        combo += 1
                                        goods += 1
                                        hit_zone.trigger()
                                    break
                        if not found:
                            combo = 0
        
        game_time += 1
        
        if game_time - last_beat > beat_interval:
            if random.random() < 0.8:
                lane = random.randint(0, lanes - 1)
                notes.append(Note(lane, 6))
            last_beat = game_time
        
        for note in notes[:]:
            note.update()
            if note.y > HEIGHT:
                if not note.hit:
                    misses += 1
                    combo = 0
                notes.remove(note)
        
        for zone in hit_zones:
            zone.update()
            zone.draw()
        
        for note in notes:
            note.draw()
        
        pygame.draw.line(screen, WHITE, (0, HEIGHT - 100), (WIDTH, HEIGHT - 100), 3)
        
        for i, (key, name) in enumerate(zip(key_map, key_names)):
            x = 100 + i * 150 + 25
            key_text = font.render(name, True, WHITE)
            screen.blit(key_text, (x - 10, HEIGHT - 70))
        
        combo_multiplier = 1 + combo // 10
        score_text = font.render(f"得分: {score}", True, WHITE)
        combo_text = font.render(f"连击: {combo} x{combo_multiplier}", True, 
                               YELLOW if combo >= 10 else WHITE)
        perfects_text = font.render(f"完美: {perfects}", True, GREEN)
        goods_text = font.render(f"良好: {goods}", True, BLUE)
        misses_text = font.render(f"失误: {misses}", True, RED)
        
        screen.blit(score_text, (10, 10))
        screen.blit(combo_text, (10, 50))
        screen.blit(perfects_text, (10, 90))
        screen.blit(goods_text, (10, 130))
        screen.blit(misses_text, (10, 170))
        
        pygame.display.flip()
        clock.tick(60)
        
        if misses >= 20:
            game_over = True
    
    screen.fill(BLACK)
    result = big_font.render("游戏结束!", True, YELLOW)
    screen.blit(result, (WIDTH // 2 - 120, 100))
    
    final_score = font.render(f"最终得分: {score}", True, WHITE)
    screen.blit(final_score, (WIDTH // 2 - 100, 200))
    
    max_combo_text = font.render(f"最高连击: {max_combo}", True, YELLOW)
    screen.blit(max_combo_text, (WIDTH // 2 - 100, 250))
    
    stats = font.render(f"完美: {perfects}  良好: {goods}  失误: {misses}", True, WHITE)
    screen.blit(stats, (WIDTH // 2 - 150, 300))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    rhythm_master()
