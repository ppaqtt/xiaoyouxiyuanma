import pygame
import sys
import random
import math
from enum import Enum

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 60, 60)
GREEN = (60, 255, 60)
BLUE = (60, 60, 255)
YELLOW = (255, 255, 60)
PURPLE = (200, 60, 200)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)

NOTE_WIDTH = 80
NOTE_HEIGHT = 40
HIT_ZONE_Y = SCREEN_HEIGHT - 120
LANE_COUNT = 4
LANE_WIDTH = NOTE_WIDTH + 20
TRACK_START_X = (SCREEN_WIDTH - LANE_COUNT * LANE_WIDTH) // 2

lanes = [TRACK_START_X + i * LANE_WIDTH for i in range(LANE_COUNT)]
keys = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
lane_colors = [RED, GREEN, BLUE, YELLOW]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("像素吉他英雄")
clock = pygame.time.Clock()

font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)

class Judgment(Enum):
    PERFECT = "完美!"
    GOOD = "好!"
    NORMAL = "普通"
    MISS = "Miss"

judgment_colors = {
    Judgment.PERFECT: (255, 215, 0),
    Judgment.GOOD: (0, 255, 0),
    Judgment.NORMAL: (0, 200, 255),
    Judgment.MISS: (255, 0, 0)
}

class Note:
    def __init__(self, lane, time):
        self.lane = lane
        self.time = time
        self.y = -NOTE_HEIGHT
        self.hit = False
        self.x = lanes[lane] + 10

    def update(self, dt, scroll_speed):
        if not self.hit:
            self.y += scroll_speed * dt

    def draw(self, surface):
        if not self.hit:
            color = lane_colors[self.lane]
            pygame.draw.rect(surface, color, (self.x, self.y, NOTE_WIDTH, NOTE_HEIGHT), 0)
            pygame.draw.rect(surface, WHITE, (self.x, self.y, NOTE_WIDTH, NOTE_HEIGHT), 3)

class Song:
    def __init__(self, name, tempo, notes_data):
        self.name = name
        self.tempo = tempo
        self.notes_data = notes_data

class SoundGenerator:
    @staticmethod
    def generate_tone(frequency, duration, volume=0.3):
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        buffer = bytearray(num_samples * 2)
        
        for i in range(num_samples):
            t = i / sample_rate
            value = int(32767 * volume * math.sin(2 * math.pi * frequency * t))
            value = max(-32768, min(32767, value))
            
            buffer[i * 2] = value & 0xff
            buffer[i * 2 + 1] = (value >> 8) & 0xff
        
        return pygame.mixer.Sound(buffer)

class Game:
    def __init__(self):
        self.state = "menu"
        self.songs = self.create_songs()
        self.current_song = None
        self.song_index = 0
        self.notes = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.health = 100
        self.scroll_speed = 400
        self.start_time = 0
        self.current_time = 0
        self.note_index = 0
        self.judgments = []
        self.sounds = self.create_sounds()

    def create_songs(self):
        songs = [
            Song("小星星", 120, [
                (0, 0.5), (1, 1.0), (1, 1.5), (2, 2.0), (2, 2.5), (1, 3.0),
                (0, 3.5), (1, 4.0), (2, 4.5), (2, 5.0), (1, 5.5), (0, 6.0),
            ]),
            Song("欢乐颂", 140, [
                (0, 0.5), (0, 1.0), (1, 1.5), (2, 2.0), (2, 2.5), (1, 3.0),
                (0, 3.5), (3, 4.0), (2, 4.5), (1, 5.0), (1, 5.5), (0, 6.0),
            ]),
            Song("两只老虎", 100, [
                (0, 0.5), (1, 1.0), (0, 1.5), (2, 2.0), (0, 2.5), (2, 3.0),
                (1, 3.5), (3, 4.0), (0, 4.5), (1, 5.0), (0, 5.5), (2, 6.0),
            ])
        ]
        return songs

    def create_sounds(self):
        frequencies = [261.63, 329.63, 392.00, 523.25]
        sounds = {}
        for i, freq in enumerate(frequencies):
            sounds[i] = SoundGenerator.generate_tone(freq, 0.2)
        sounds[Judgment.PERFECT] = SoundGenerator.generate_tone(880, 0.1, 0.2)
        sounds[Judgment.GOOD] = SoundGenerator.generate_tone(660, 0.1, 0.2)
        sounds[Judgment.NORMAL] = SoundGenerator.generate_tone(440, 0.1, 0.2)
        return sounds

    def play_sound(self, lane):
        if lane in self.sounds:
            self.sounds[lane].play()

    def play_judgment_sound(self, judgment):
        if judgment in self.sounds:
            self.sounds[judgment].play()

    def start_game(self, song):
        self.current_song = song
        self.notes = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.health = 100
        self.note_index = 0
        self.judgments = []
        self.start_time = pygame.time.get_ticks()
        self.state = "playing"

    def update(self, dt):
        if self.state == "playing":
            self.current_time = (pygame.time.get_ticks() - self.start_time) / 1000

            while self.note_index < len(self.current_song.notes_data):
                lane, note_time = self.current_song.notes_data[self.note_index]
                if self.current_time >= note_time - (HIT_ZONE_Y / self.scroll_speed):
                    self.notes.append(Note(lane, note_time))
                    self.note_index += 1
                else:
                    break

            for note in self.notes:
                note.update(dt, self.scroll_speed)

            for note in self.notes[:]:
                if not note.hit and note.y > HIT_ZONE_Y + 80:
                    self.add_judgment(Judgment.MISS, note.lane)
                    note.hit = True
                    self.combo = 0
                    self.health -= 10

            self.notes = [note for note in self.notes if note.y < SCREEN_HEIGHT + 50]

            if self.health <= 0:
                self.state = "gameover"
            elif self.note_index >= len(self.current_song.notes_data) and all(note.hit for note in self.notes):
                self.state = "result"

            self.judgments = [j for j in self.judgments if j[3] > 0]
            for j in self.judgments:
                j[1] -= dt * 100
                j[3] -= dt

    def handle_key_press(self, key):
        if self.state == "menu":
            if key == pygame.K_RETURN:
                self.start_game(self.songs[self.song_index])
            elif key == pygame.K_LEFT:
                self.song_index = (self.song_index - 1) % len(self.songs)
            elif key == pygame.K_RIGHT:
                self.song_index = (self.song_index + 1) % len(self.songs)
        elif self.state == "playing":
            if key in keys:
                lane = keys.index(key)
                self.check_hit(lane)
        elif self.state == "gameover" or self.state == "result":
            if key == pygame.K_RETURN:
                self.state = "menu"

    def check_hit(self, lane):
        closest_note = None
        closest_distance = float('inf')

        for note in self.notes:
            if not note.hit and note.lane == lane:
                distance = abs(note.y - HIT_ZONE_Y)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_note = note

        if closest_note:
            if closest_distance < 30:
                self.add_judgment(Judgment.PERFECT, lane)
                self.score += 100 * (1 + self.combo * 0.1)
                self.combo += 1
                self.health = min(100, self.health + 2)
                closest_note.hit = True
                self.play_sound(lane)
                self.play_judgment_sound(Judgment.PERFECT)
            elif closest_distance < 60:
                self.add_judgment(Judgment.GOOD, lane)
                self.score += 50 * (1 + self.combo * 0.1)
                self.combo += 1
                self.health = min(100, self.health + 1)
                closest_note.hit = True
                self.play_sound(lane)
                self.play_judgment_sound(Judgment.GOOD)
            elif closest_distance < 100:
                self.add_judgment(Judgment.NORMAL, lane)
                self.score += 20
                self.combo += 1
                closest_note.hit = True
                self.play_sound(lane)
                self.play_judgment_sound(Judgment.NORMAL)
            else:
                pass
        else:
            pass

        if self.combo > self.max_combo:
            self.max_combo = self.combo

    def add_judgment(self, judgment, lane):
        x = lanes[lane] + NOTE_WIDTH // 2
        y = HIT_ZONE_Y
        self.judgments.append([judgment, y, x, 1.0])

    def draw(self):
        screen.fill(BLACK)

        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "gameover":
            self.draw_gameover()
        elif self.state == "result":
            self.draw_result()

        pygame.display.flip()

    def draw_menu(self):
        title = font_large.render("像素吉他英雄", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        for i in range(3):
            indicator = "<<" if i < self.song_index else "  "
            indicator += "  "
            indicator += ">>" if i > self.song_index else "  "
            
            color = WHITE if i == self.song_index else GRAY
            song_name = font_medium.render(f"{indicator} {self.songs[i].name} {indicator}", True, color)
            screen.blit(song_name, (SCREEN_WIDTH // 2 - song_name.get_width() // 2, 200 + i * 80))

        instructions = font_small.render("按 ← → 选择歌曲，回车开始", True, GRAY)
        screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 450))

        key_hints = font_small.render("D F J K 对应四列音符", True, GRAY)
        screen.blit(key_hints, (SCREEN_WIDTH // 2 - key_hints.get_width() // 2, 500))

    def draw_game(self):
        for i in range(LANE_COUNT):
            x = lanes[i]
            pygame.draw.rect(screen, DARK_GRAY, (x, 0, NOTE_WIDTH + 20, SCREEN_HEIGHT))
            pygame.draw.rect(screen, GRAY, (x, 0, 3, SCREEN_HEIGHT))
            pygame.draw.rect(screen, GRAY, (x + NOTE_WIDTH + 17, 0, 3, SCREEN_HEIGHT))

        pygame.draw.rect(screen, PURPLE, (TRACK_START_X - 10, HIT_ZONE_Y, LANE_COUNT * LANE_WIDTH + 20, 5))

        for i in range(LANE_COUNT):
            x = lanes[i] + 10
            pygame.draw.rect(screen, lane_colors[i], (x, HIT_ZONE_Y, NOTE_WIDTH, NOTE_HEIGHT), 3)

        for note in self.notes:
            note.draw(screen)

        for judgment, y, x, alpha in self.judgments:
            text = font_medium.render(judgment.value, True, judgment_colors[judgment])
            text.set_alpha(int(alpha * 255))
            screen.blit(text, (x - text.get_width() // 2, y))

        score_text = font_medium.render(f"分数: {int(self.score)}", True, WHITE)
        screen.blit(score_text, (20, 20))

        combo_text = font_medium.render(f"连击: {self.combo}", True, YELLOW)
        screen.blit(combo_text, (20, 60))

        song_text = font_small.render(f"歌曲: {self.current_song.name}", True, GRAY)
        screen.blit(song_text, (20, 100))

        pygame.draw.rect(screen, DARK_GRAY, (SCREEN_WIDTH - 220, 20, 200, 30))
        health_color = GREEN if self.health > 50 else (YELLOW if self.health > 25 else RED)
        pygame.draw.rect(screen, health_color, (SCREEN_WIDTH - 220, 20, self.health * 2, 30))
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH - 220, 20, 200, 30), 2)
        health_text = font_small.render(f"生命: {int(self.health)}%", True, WHITE)
        screen.blit(health_text, (SCREEN_WIDTH - 220, 60))

        key_labels = ["D", "F", "J", "K"]
        for i in range(LANE_COUNT):
            key_text = font_small.render(key_labels[i], True, lane_colors[i])
            screen.blit(key_text, (lanes[i] + NOTE_WIDTH // 2 - key_text.get_width() // 2, HIT_ZONE_Y + NOTE_HEIGHT + 10))

    def draw_gameover(self):
        gameover_text = font_large.render("游戏结束!", True, RED)
        screen.blit(gameover_text, (SCREEN_WIDTH // 2 - gameover_text.get_width() // 2, 150))

        score_text = font_medium.render(f"最终分数: {int(self.score)}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))

        max_combo_text = font_medium.render(f"最高连击: {self.max_combo}", True, YELLOW)
        screen.blit(max_combo_text, (SCREEN_WIDTH // 2 - max_combo_text.get_width() // 2, 320))

        restart_text = font_small.render("按回车返回菜单", True, GRAY)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 450))

    def draw_result(self):
        result_text = font_large.render("演奏完成!", True, GREEN)
        screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, 120))

        score_text = font_medium.render(f"最终分数: {int(self.score)}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 220))

        max_combo_text = font_medium.render(f"最高连击: {self.max_combo}", True, YELLOW)
        screen.blit(max_combo_text, (SCREEN_WIDTH // 2 - max_combo_text.get_width() // 2, 290))

        if self.max_combo == len(self.current_song.notes_data):
            fc_text = font_medium.render("全连!", True, (255, 215, 0))
            screen.blit(fc_text, (SCREEN_WIDTH // 2 - fc_text.get_width() // 2, 360))

        restart_text = font_small.render("按回车返回菜单", True, GRAY)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 480))

def main():
    game = Game()

    while True:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                game.handle_key_press(event.key)

        game.update(dt)
        game.draw()

if __name__ == "__main__":
    main()
