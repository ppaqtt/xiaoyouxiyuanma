import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 800

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (255, 0, 0),    # 红
    (0, 255, 0),    # 绿
    (0, 0, 255),    # 蓝
    (255, 255, 0),  # 黄
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("节奏大师")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)
big_font = pygame.font.Font(None, 80)

class Note:
    def __init__(self, lane, speed):
        self.lane = lane
        self.y = -50
        self.speed = speed
        self.size = 60
        self.hit = False
    
    def move(self):
        self.y += self.speed
    
    def draw(self):
        if not self.hit:
            x = 75 + self.lane * 150
            pygame.draw.rect(screen, COLORS[self.lane],
                          (x, self.y, self.size, self.size), border_radius=10)

def rhythm_game():
    notes = []
    lanes = 4
    speed = 5
    score = 0
    combo = 0
    time_left = 60
    game_over = False
    start_ticks = pygame.time.get_ticks()
    
    key_mapping = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
    
    while not game_over:
        screen.fill(BLACK)
        
        pygame.draw.line(screen, WHITE, (0, HEIGHT - 100), (WIDTH, HEIGHT - 100), 3)
        
        for i in range(lanes):
            x = 75 + i * 150
            pygame.draw.rect(screen, (50, 50, 50),
                          (x, HEIGHT - 100, 60, 100), border_radius=5)
            
            text = font.render(chr(key_mapping[i]), True, WHITE)
            screen.blit(text, (x + 20, HEIGHT - 70))
        
        if random.randint(1, 20) == 1:
            lane = random.randint(0, lanes - 1)
            notes.append(Note(lane, speed))
        
        for note in notes[:]:
            note.move()
            note.draw()
            
            if note.y > HEIGHT:
                combo = 0
                notes.remove(note)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                for i, key in enumerate(key_mapping):
                    if event.key == key:
                        for note in notes[:]:
                            if note.lane == i and abs(note.y - (HEIGHT - 100)) < 50:
                                note.hit = True
                                combo += 1
                                score += 10 * combo
                                notes.remove(note)
                                break
        
        seconds = max(0, time_left - (pygame.time.get_ticks() - start_ticks) // 1000)
        if seconds == 0:
            game_over = True
        
        score_text = font.render(f"得分: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        combo_text = font.render(f"连击: {combo}", True, WHITE)
        screen.blit(combo_text, (WIDTH - 120, 10))
        
        time_text = font.render(f"时间: {seconds}秒", True, WHITE)
        screen.blit(time_text, (WIDTH//2 - 50, 10))
        
        if combo >= 10:
            combo_bonus = font.render(f"{combo}连击!", True, (255, 0, 255))
            screen.blit(combo_bonus, (WIDTH//2 - 50, HEIGHT//2))
        
        pygame.display.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    result_text = big_font.render(f"最终得分: {score}", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2 - 50))
    
    max_combo = font.render(f"最高连击: {combo}", True, WHITE)
    screen.blit(max_combo, (WIDTH//2 - max_combo.get_width()//2, HEIGHT//2 + 50))
    
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    rhythm_game()