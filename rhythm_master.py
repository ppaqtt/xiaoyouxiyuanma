import pygame
import random
import math
import sys
import time

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (180, 180, 180)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 100)
PURPLE = (200, 100, 255)
ORANGE = (255, 180, 100)

KEY_COLORS = [RED, BLUE, GREEN, YELLOW, PURPLE]
KEY_NAMES = ['D', 'F', 'J', 'K', '空格']
KEYS = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k, pygame.K_SPACE]

NOTE_HEIGHT = 30
LANE_WIDTH = 100
JUDGE_LINE_Y = 500
HIT_ZONE = 80
PERFECT_ZONE = 30
GREAT_ZONE = 50
GOOD_ZONE = HIT_ZONE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("节奏大师")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 60)
font_medium = pygame.font.Font(None, 40)
font_small = pygame.font.Font(None, 30)

def generate_sound(frequency, duration, volume=0.5):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buffer = bytearray()
    for i in range(n_samples):
        t = i / sample_rate
        value = int(volume * 127 * math.sin(2 * math.pi * frequency * t))
        buffer.append(value + 128)
    sound = pygame.mixer.Sound(buffer)
    return sound

hit_sounds = [
    generate_sound(440, 0.1),
    generate_sound(523, 0.1),
    generate_sound(659, 0.1),
    generate_sound(784, 0.1),
    generate_sound(880, 0.1)
]
miss_sound = generate_sound(200, 0.3, 0.3)
menu_sound = generate_sound(330, 0.1)

class Song:
    def __init__(self, name, difficulty, notes_data, speed=5):
        self.name = name
        self.difficulty = difficulty
        self.notes_data = notes_data
        self.speed = speed

class Note:
    def __init__(self, lane, time):
        self.lane = lane
        self.time = time
        self.y = -NOTE_HEIGHT
        self.hit = False
        self.missed = False
    
    def update(self, current_time, start_time, speed):
        elapsed = current_time - start_time
        self.y = (elapsed - self.time) * speed + JUDGE_LINE_Y - (JUDGE_LINE_Y + NOTE_HEIGHT)
    
    def draw(self, surface, lane_x):
        if not self.hit and not self.missed:
            color = KEY_COLORS[self.lane]
            pygame.draw.rect(surface, color, (lane_x, self.y, LANE_WIDTH - 10, NOTE_HEIGHT))
            pygame.draw.rect(surface, WHITE, (lane_x + 5, self.y + 5, LANE_WIDTH - 20, NOTE_HEIGHT - 10), 2)

class Game:
    def __init__(self):
        self.state = 'menu'
        self.selected_song = 0
        self.songs = self.create_songs()
        self.reset_game()
    
    def create_songs(self):
        songs = []
        notes1 = []
        for i in range(30):
            notes1.append((random.randint(0, 4), i * 500 + 1000))
        songs.append(Song("小星星", "简单", notes1, 4))
        
        notes2 = []
        for i in range(50):
            notes2.append((random.randint(0, 4), i * 350 + 800))
        songs.append(Song("欢乐颂", "中等", notes2, 5))
        
        notes3 = []
        for i in range(80):
            notes3.append((random.randint(0, 4), i * 250 + 600))
        songs.append(Song("野蜂飞舞", "困难", notes3, 6))
        
        return songs
    
    def reset_game(self):
        self.notes = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.health = 100
        self.judgments = {'Perfect': 0, 'Great': 0, 'Good': 0, 'Miss': 0}
        self.start_time = 0
        self.current_time = 0
        self.game_over = False
        self.song_complete = False
        self.hit_effects = []
        self.notes_spawned = 0
    
    def start_game(self, song_index):
        self.reset_game()
        self.selected_song = song_index
        song = self.songs[song_index]
        for lane, note_time in song.notes_data:
            self.notes.append(Note(lane, note_time))
        self.state = 'playing'
        self.start_time = pygame.time.get_ticks()
    
    def calculate_judgment(self, note):
        note_target_y = JUDGE_LINE_Y
        distance = abs(note.y - note_target_y)
        
        if distance < PERFECT_ZONE:
            return 'Perfect', 100
        elif distance < GREAT_ZONE:
            return 'Great', 70
        elif distance < GOOD_ZONE:
            return 'Good', 30
        else:
            return 'Miss', 0
    
    def hit_note(self, lane):
        hit_sounds[lane].play()
        closest_note = None
        closest_distance = float('inf')
        
        for note in self.notes:
            if note.lane == lane and not note.hit and not note.missed:
                distance = abs(note.y - JUDGE_LINE_Y)
                if distance < HIT_ZONE and distance < closest_distance:
                    closest_distance = distance
                    closest_note = note
        
        if closest_note:
            closest_note.hit = True
            judgment, points = self.calculate_judgment(closest_note)
            self.judgments[judgment] += 1
            
            if judgment != 'Miss':
                self.combo += 1
                if self.combo > self.max_combo:
                    self.max_combo = self.combo
                multiplier = min(1.0 + self.combo / 50, 3.0)
                self.score += int(points * multiplier)
                self.health = min(100, self.health + 5)
                
                x = (SCREEN_WIDTH - LANE_WIDTH * 5) // 2 + lane * LANE_WIDTH + LANE_WIDTH // 2
                self.hit_effects.append({'x': x, 'y': JUDGE_LINE_Y, 'text': judgment, 'color': KEY_COLORS[lane], 'time': 0})
            else:
                self.combo = 0
                self.health -= 15
                miss_sound.play()
        else:
            self.combo = 0
    
    def update(self):
        if self.state == 'playing' and not self.game_over and not self.song_complete:
            self.current_time = pygame.time.get_ticks()
            song = self.songs[self.selected_song]
            
            for note in self.notes:
                note.update(self.current_time, self.start_time, song.speed)
                
                if not note.hit and not note.missed and note.y > JUDGE_LINE_Y + HIT_ZONE:
                    note.missed = True
                    self.judgments['Miss'] += 1
                    self.combo = 0
                    self.health -= 10
                    miss_sound.play()
            
            self.hit_effects = [effect for effect in self.hit_effects if effect['time'] < 60]
            for effect in self.hit_effects:
                effect['time'] += 1
                effect['y'] -= 2
            
            if self.health <= 0:
                self.game_over = True
            
            all_notes_done = all(note.hit or note.missed for note in self.notes)
            if all_notes_done and len(self.notes) > 0:
                self.song_complete = True
    
    def draw(self):
        screen.fill(BLACK)
        
        if self.state == 'menu':
            self.draw_menu()
        elif self.state == 'song_select':
            self.draw_song_select()
        elif self.state == 'playing':
            self.draw_game()
        elif self.state == 'result':
            self.draw_result()
    
    def draw_menu(self):
        title = font_large.render("节奏大师", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        
        play_text = font_medium.render("开始游戏", True, GREEN)
        screen.blit(play_text, (SCREEN_WIDTH // 2 - play_text.get_width() // 2, 300))
        
        help_text = font_small.render("按 Enter 开始", True, LIGHT_GRAY)
        screen.blit(help_text, (SCREEN_WIDTH // 2 - help_text.get_width() // 2, 400))
        
        controls_text = font_small.render("按键: D F J K 空格", True, LIGHT_GRAY)
        screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, 450))
    
    def draw_song_select(self):
        title = font_large.render("选择歌曲", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
        
        for i, song in enumerate(self.songs):
            y = 200 + i * 100
            color = WHITE if i == self.selected_song else GRAY
            bg_color = DARK_GRAY if i == self.selected_song else BLACK
            
            pygame.draw.rect(screen, bg_color, (150, y - 10, 500, 80))
            name_text = font_medium.render(song.name, True, color)
            diff_text = font_small.render(f"难度: {song.difficulty}", True, color)
            
            screen.blit(name_text, (170, y))
            screen.blit(diff_text, (170, y + 40))
        
        help_text = font_small.render("↑↓ 选择, Enter 确认, ESC 返回", True, LIGHT_GRAY)
        screen.blit(help_text, (SCREEN_WIDTH // 2 - help_text.get_width() // 2, 520))
    
    def draw_game(self):
        start_x = (SCREEN_WIDTH - LANE_WIDTH * 5) // 2
        
        for i in range(5):
            x = start_x + i * LANE_WIDTH
            pygame.draw.rect(screen, DARK_GRAY, (x, 0, LANE_WIDTH - 5, SCREEN_HEIGHT))
            pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 2)
        
        pygame.draw.rect(screen, ORANGE, (start_x, JUDGE_LINE_Y - 5, LANE_WIDTH * 5 - 5, 10))
        
        for i, key in enumerate(KEYS):
            x = start_x + i * LANE_WIDTH
            key_pressed = pygame.key.get_pressed()[key]
            color = KEY_COLORS[i] if key_pressed else GRAY
            pygame.draw.rect(screen, color, (x + 10, JUDGE_LINE_Y + 50, LANE_WIDTH - 25, 60))
            pygame.draw.rect(screen, WHITE, (x + 10, JUDGE_LINE_Y + 50, LANE_WIDTH - 25, 60), 3)
            key_text = font_medium.render(KEY_NAMES[i], True, BLACK if key_pressed else WHITE)
            screen.blit(key_text, (x + LANE_WIDTH // 2 - key_text.get_width() // 2, JUDGE_LINE_Y + 65))
        
        for note in self.notes:
            x = start_x + note.lane * LANE_WIDTH + 5
            note.draw(screen, x)
        
        for effect in self.hit_effects:
            alpha = max(0, 255 - effect['time'] * 4)
            text = font_medium.render(effect['text'], True, effect['color'])
            text.set_alpha(alpha)
            screen.blit(text, (effect['x'] - text.get_width() // 2, effect['y']))
        
        score_text = font_medium.render(f"分数: {self.score}", True, WHITE)
        combo_text = font_large.render(f"{self.combo}x", True, YELLOW) if self.combo > 0 else None
        health_text = font_medium.render(f"生命: {int(self.health)}", True, RED if self.health < 30 else GREEN)
        
        screen.blit(score_text, (20, 20))
        if combo_text:
            screen.blit(combo_text, (SCREEN_WIDTH // 2 - combo_text.get_width() // 2, 50))
        screen.blit(health_text, (SCREEN_WIDTH - health_text.get_width() - 20, 20))
        
        pygame.draw.rect(screen, DARK_GRAY, (20, 70, 200, 20))
        pygame.draw.rect(screen, GREEN if self.health > 30 else RED, (20, 70, self.health * 2, 20))
        pygame.draw.rect(screen, WHITE, (20, 70, 200, 20), 2)
        
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            game_over_text = font_large.render("游戏结束", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 250))
            
            continue_text = font_medium.render("按 Enter 查看结果", True, WHITE)
            screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 350))
        
        if self.song_complete:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            complete_text = font_large.render("歌曲完成!", True, GREEN)
            screen.blit(complete_text, (SCREEN_WIDTH // 2 - complete_text.get_width() // 2, 250))
            
            continue_text = font_medium.render("按 Enter 查看结果", True, WHITE)
            screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 350))
    
    def draw_result(self):
        title = font_large.render("游戏结果", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        song = self.songs[self.selected_song]
        song_text = font_medium.render(f"歌曲: {song.name}", True, LIGHT_GRAY)
        screen.blit(song_text, (SCREEN_WIDTH // 2 - song_text.get_width() // 2, 120))
        
        total_notes = sum(self.judgments.values())
        if total_notes > 0:
            accuracy = (self.judgments['Perfect'] * 100 + self.judgments['Great'] * 70 + self.judgments['Good'] * 30) / (total_notes * 100) * 100
        else:
            accuracy = 0
        
        grade = 'F'
        if accuracy >= 95:
            grade = 'S'
        elif accuracy >= 90:
            grade = 'A'
        elif accuracy >= 80:
            grade = 'B'
        elif accuracy >= 70:
            grade = 'C'
        elif accuracy >= 60:
            grade = 'D'
        
        grade_text = font_large.render(grade, True, YELLOW)
        screen.blit(grade_text, (SCREEN_WIDTH // 2 - grade_text.get_width() // 2, 160))
        
        y = 220
        results = [
            f"分数: {self.score}",
            f"最高连击: {self.max_combo}",
            f"准确率: {accuracy:.1f}%",
            f"Perfect: {self.judgments['Perfect']}",
            f"Great: {self.judgments['Great']}",
            f"Good: {self.judgments['Good']}",
            f"Miss: {self.judgments['Miss']}"
        ]
        
        colors = [WHITE, WHITE, WHITE, KEY_COLORS[0], KEY_COLORS[3], KEY_COLORS[2], RED]
        
        for result, color in zip(results, colors):
            text = font_medium.render(result, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 40
        
        menu_text = font_small.render("按 Enter 返回菜单, R 重新开始", True, LIGHT_GRAY)
        screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, 520))
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == 'menu':
                if event.key == pygame.K_RETURN:
                    menu_sound.play()
                    self.state = 'song_select'
            
            elif self.state == 'song_select':
                if event.key == pygame.K_UP:
                    menu_sound.play()
                    self.selected_song = (self.selected_song - 1) % len(self.songs)
                elif event.key == pygame.K_DOWN:
                    menu_sound.play()
                    self.selected_song = (self.selected_song + 1) % len(self.songs)
                elif event.key == pygame.K_RETURN:
                    menu_sound.play()
                    self.start_game(self.selected_song)
                elif event.key == pygame.K_ESCAPE:
                    menu_sound.play()
                    self.state = 'menu'
            
            elif self.state == 'playing':
                if not self.game_over and not self.song_complete:
                    for i, key in enumerate(KEYS):
                        if event.key == key:
                            self.hit_note(i)
                elif self.game_over or self.song_complete:
                    if event.key == pygame.K_RETURN:
                        menu_sound.play()
                        self.state = 'result'
            
            elif self.state == 'result':
                if event.key == pygame.K_RETURN:
                    menu_sound.play()
                    self.state = 'menu'
                elif event.key == pygame.K_r:
                    menu_sound.play()
                    self.start_game(self.selected_song)

def main():
    game = Game()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_input(event)
        
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
