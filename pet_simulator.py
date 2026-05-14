import pygame
import random
import math
import time
from enum import Enum


class PetType(Enum):
    CAT = "猫"
    DOG = "狗"


class PetState(Enum):
    IDLE = "idle"
    SLEEPING = "sleeping"
    PLAYING = "playing"
    EATING = "eating"
    BATHING = "bathing"
    SICK = "sick"


class SoundSystem:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self._generate_sounds()

    def _generate_square_wave(self, frequency, duration, volume=0.3):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        sound_data = bytearray()
        
        for i in range(n_samples):
            t = i / sample_rate
            value = int(volume * 127 * (1 if math.sin(2 * math.pi * frequency * t) > 0 else -1))
            sound_data.append(value + 128)
        
        return pygame.mixer.Sound(buffer=bytes(sound_data))

    def _generate_sine_wave(self, frequency, duration, volume=0.2):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        sound_data = bytearray()
        
        for i in range(n_samples):
            t = i / sample_rate
            value = int(volume * 127 * math.sin(2 * math.pi * frequency * t))
            sound_data.append(value + 128)
        
        return pygame.mixer.Sound(buffer=bytes(sound_data))

    def _generate_sounds(self):
        self.sounds['meow'] = self._generate_sine_wave(800, 0.3)
        self.sounds['bark'] = self._generate_square_wave(300, 0.2)
        self.sounds['eat'] = self._generate_sine_wave(200, 0.15)
        self.sounds['play'] = self._generate_sine_wave(600, 0.2)
        self.sounds['bath'] = self._generate_sine_wave(400, 0.4)
        self.sounds['sleep'] = self._generate_sine_wave(100, 0.5)
        self.sounds['sick'] = self._generate_sine_wave(150, 0.3)

    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()


class Pet:
    def __init__(self, pet_type):
        self.pet_type = pet_type
        self.state = PetState.IDLE
        self.hunger = 80
        self.happiness = 80
        self.health = 100
        self.cleanliness = 80
        self.age = 0
        self.is_sick = False
        self.anim_frame = 0
        self.anim_timer = 0
        self.x = 200
        self.y = 280
        self.direction = 1
        self.move_timer = 0
        self.last_update = time.time()

    def update(self):
        current_time = time.time()
        delta = current_time - self.last_update
        self.last_update = current_time

        if self.state != PetState.SLEEPING:
            self.hunger = max(0, self.hunger - 0.5 * delta)
            self.happiness = max(0, self.happiness - 0.3 * delta)
            self.cleanliness = max(0, self.cleanliness - 0.4 * delta)

        if self.hunger < 30 or self.cleanliness < 30:
            self.health = max(0, self.health - 0.3 * delta)

        if self.state == PetState.SLEEPING:
            self.health = min(100, self.health + 0.5 * delta)
            self.happiness = min(100, self.happiness + 0.2 * delta)

        if self.health < 30 and not self.is_sick:
            self.is_sick = True
            self.state = PetState.SICK

        if self.is_sick and self.health > 60:
            self.is_sick = False
            self.state = PetState.IDLE

        self.age += delta * 0.01

        self.anim_timer += delta
        if self.anim_timer > 0.2:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4

        if self.state == PetState.IDLE:
            self.move_timer += delta
            if self.move_timer > 2:
                self.move_timer = 0
                self.direction = random.choice([-1, 1])
            self.x += self.direction * 0.5
            if self.x < 100:
                self.x = 100
                self.direction = 1
            if self.x > 300:
                self.x = 300
                self.direction = -1

    def feed(self):
        if self.state == PetState.SLEEPING:
            return
        self.state = PetState.EATING
        self.hunger = min(100, self.hunger + 30)
        self.happiness = min(100, self.happiness + 10)
        self.cleanliness = max(0, self.cleanliness - 5)

    def play(self):
        if self.state == PetState.SLEEPING or self.is_sick:
            return
        self.state = PetState.PLAYING
        self.happiness = min(100, self.happiness + 30)
        self.hunger = max(0, self.hunger - 15)
        self.health = min(100, self.health + 5)

    def bathe(self):
        if self.state == PetState.SLEEPING:
            return
        self.state = PetState.BATHING
        self.cleanliness = min(100, self.cleanliness + 40)
        self.happiness = max(0, self.happiness - 10)

    def sleep(self):
        if self.state == PetState.SLEEPING:
            self.state = PetState.IDLE
        else:
            self.state = PetState.SLEEPING

    def get_stage(self):
        if self.age < 50:
            return "幼年"
        elif self.age < 150:
            return "青年"
        else:
            return "成年"


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)
        
        text_surf = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height

    def is_clicked(self, pos):
        return self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height


class Game:
    def __init__(self):
        pygame.init()
        self.width = 400
        self.height = 500
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("宠物模拟器")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 36)
        self.sound_system = SoundSystem()
        self.pet = None
        self.game_state = "select"
        self.action_timer = 0

        self.feed_btn = Button(20, 420, 80, 60, "喂食", (100, 200, 100), (150, 255, 150))
        self.play_btn = Button(110, 420, 80, 60, "玩耍", (200, 150, 100), (255, 200, 150))
        self.bathe_btn = Button(200, 420, 80, 60, "洗澡", (100, 150, 200), (150, 200, 255))
        self.sleep_btn = Button(290, 420, 90, 60, "睡觉", (150, 100, 150), (200, 150, 200))

        self.cat_btn = Button(80, 200, 100, 80, "猫咪", (255, 200, 200), (255, 220, 220))
        self.dog_btn = Button(220, 200, 100, 80, "狗狗", (200, 200, 255), (220, 220, 255))

    def draw_pixel_pet(self):
        if not self.pet:
            return

        stage = self.pet.get_stage()
        scale = 1.0 if stage == "幼年" else 1.3 if stage == "青年" else 1.6
        
        x = int(self.pet.x)
        y = int(self.pet.y)
        
        if self.pet.pet_type == PetType.CAT:
            self._draw_cat(x, y, scale)
        else:
            self._draw_dog(x, y, scale)

    def _draw_cat(self, x, y, scale):
        color = (255, 150, 100) if not self.pet.is_sick else (180, 180, 180)
        s = int(8 * scale)
        
        offset = 0
        if self.pet.state == PetState.PLAYING:
            offset = int(math.sin(time.time() * 10) * 5)
        elif self.pet.state == PetState.SLEEPING:
            y += 10

        pygame.draw.rect(self.screen, color, (x - s, y - s, s * 2, s * 2))
        pygame.draw.rect(self.screen, color, (x - s, y - s * 2 - 5, s * 2, s * 2))
        
        pygame.draw.polygon(self.screen, color, [(x - s, y - s * 2 - 5), (x - s - 5, y - s * 3 - 5), (x - s + 5, y - s * 2 - 5)])
        pygame.draw.polygon(self.screen, color, [(x + s, y - s * 2 - 5), (x + s + 5, y - s * 3 - 5), (x + s - 5, y - s * 2 - 5)])
        
        eye_color = (0, 0, 0)
        if self.pet.state == PetState.SLEEPING:
            pygame.draw.line(self.screen, (0, 0, 0), (x - 4, y - s * 2), (x + 4, y - s * 2), 2)
            pygame.draw.line(self.screen, (0, 0, 0), (x - 4 + s // 2, y - s * 2), (x + 4 + s // 2, y - s * 2), 2)
        else:
            pygame.draw.circle(self.screen, eye_color, (x - 3, y - s * 2 + 2), 2)
            pygame.draw.circle(self.screen, eye_color, (x + 3 + s // 2, y - s * 2 + 2), 2)
        
        pygame.draw.circle(self.screen, (255, 100, 100), (x + s // 4, y - s * 2 + 6), 2)
        
        tail_wag = int(math.sin(time.time() * 5) * 5) if self.pet.state != PetState.SLEEPING else 0
        pygame.draw.line(self.screen, color, (x + s, y), (x + s + 10 + tail_wag, y - 5), 3)

        if self.pet.is_sick:
            self._draw_sick_effect(x, y - s * 3 - 10)

    def _draw_dog(self, x, y, scale):
        color = (150, 100, 50) if not self.pet.is_sick else (180, 180, 180)
        s = int(8 * scale)
        
        offset = 0
        if self.pet.state == PetState.PLAYING:
            offset = int(math.sin(time.time() * 10) * 5)
        elif self.pet.state == PetState.SLEEPING:
            y += 10

        pygame.draw.rect(self.screen, color, (x - s, y - s, s * 2, s * 2))
        pygame.draw.rect(self.screen, color, (x - s, y - s * 2 - 5, s * 2, s * 2))
        
        pygame.draw.rect(self.screen, color, (x - s - 4, y - s * 2 - 10, 6, 10))
        pygame.draw.rect(self.screen, color, (x + s - 2, y - s * 2 - 10, 6, 10))
        
        eye_color = (0, 0, 0)
        if self.pet.state == PetState.SLEEPING:
            pygame.draw.line(self.screen, (0, 0, 0), (x - 4, y - s * 2), (x + 4, y - s * 2), 2)
            pygame.draw.line(self.screen, (0, 0, 0), (x - 4 + s // 2, y - s * 2), (x + 4 + s // 2, y - s * 2), 2)
        else:
            pygame.draw.circle(self.screen, eye_color, (x - 3, y - s * 2 + 2), 2)
            pygame.draw.circle(self.screen, eye_color, (x + 3 + s // 2, y - s * 2 + 2), 2)
        
        pygame.draw.ellipse(self.screen, (50, 30, 20), (x + s // 4 - 3, y - s * 2 + 5, 6, 4))
        
        tail_wag = int(math.sin(time.time() * 8) * 8) if self.pet.state != PetState.SLEEPING else 0
        pygame.draw.line(self.screen, color, (x - s, y), (x - s - 10 - tail_wag, y - 8), 3)

        if self.pet.is_sick:
            self._draw_sick_effect(x, y - s * 3 - 10)

    def _draw_sick_effect(self, x, y):
        for i in range(3):
            offset = int(math.sin(time.time() * 3 + i) * 5)
            text = self.font.render("×", True, (100, 100, 255))
            self.screen.blit(text, (x - 20 + i * 20 + offset, y))

    def draw_ui(self):
        if self.game_state == "select":
            self.screen.fill((255, 240, 220))
            title = self.large_font.render("选择你的宠物", True, (0, 0, 0))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))
            self.cat_btn.draw(self.screen, self.font)
            self.dog_btn.draw(self.screen, self.font)
        else:
            self.screen.fill((200, 230, 255))
            
            pygame.draw.rect(self.screen, (100, 200, 100), (0, 350, self.width, 150))
            
            info = f"{self.pet.pet_type.value} - {self.pet.get_stage()}"
            text = self.font.render(info, True, (0, 0, 0))
            self.screen.blit(text, (10, 10))
            
            self._draw_bar(10, 40, 180, "饥饿", self.pet.hunger, (255, 100, 100))
            self._draw_bar(10, 70, 180, "快乐", self.pet.happiness, (255, 255, 100))
            self._draw_bar(210, 40, 180, "健康", self.pet.health, (100, 255, 100))
            self._draw_bar(210, 70, 180, "清洁", self.pet.cleanliness, (100, 200, 255))
            
            state_text = {
                PetState.IDLE: "休息中",
                PetState.SLEEPING: "睡觉中",
                PetState.PLAYING: "玩耍中",
                PetState.EATING: "进食中",
                PetState.BATHING: "洗澡中",
                PetState.SICK: "生病了！"
            }
            status = self.font.render(f"状态: {state_text[self.pet.state]}", True, (0, 0, 0))
            self.screen.blit(status, (10, 100))
            
            self.draw_pixel_pet()
            
            self.feed_btn.draw(self.screen, self.font)
            self.play_btn.draw(self.screen, self.font)
            self.bathe_btn.draw(self.screen, self.font)
            self.sleep_btn.draw(self.screen, self.font)

    def _draw_bar(self, x, y, width, label, value, color):
        text = self.font.render(f"{label}: {int(value)}", True, (0, 0, 0))
        self.screen.blit(text, (x, y))
        
        bar_width = width - 50
        fill_width = int(bar_width * (value / 100))
        pygame.draw.rect(self.screen, (200, 200, 200), (x + 50, y + 5, bar_width, 15))
        pygame.draw.rect(self.screen, color, (x + 50, y + 5, fill_width, 15))
        pygame.draw.rect(self.screen, (0, 0, 0), (x + 50, y + 5, bar_width, 15), 1)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    pos = pygame.mouse.get_pos()
                    if self.game_state == "select":
                        self.cat_btn.check_hover(pos)
                        self.dog_btn.check_hover(pos)
                    else:
                        self.feed_btn.check_hover(pos)
                        self.play_btn.check_hover(pos)
                        self.bathe_btn.check_hover(pos)
                        self.sleep_btn.check_hover(pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.game_state == "select":
                        if self.cat_btn.is_clicked(pos):
                            self.pet = Pet(PetType.CAT)
                            self.game_state = "play"
                            self.sound_system.play('meow')
                        elif self.dog_btn.is_clicked(pos):
                            self.pet = Pet(PetType.DOG)
                            self.game_state = "play"
                            self.sound_system.play('bark')
                    else:
                        if self.feed_btn.is_clicked(pos):
                            self.pet.feed()
                            self.sound_system.play('eat')
                            self.action_timer = 1
                        elif self.play_btn.is_clicked(pos):
                            self.pet.play()
                            self.sound_system.play('play')
                            self.action_timer = 1
                        elif self.bathe_btn.is_clicked(pos):
                            self.pet.bathe()
                            self.sound_system.play('bath')
                            self.action_timer = 1
                        elif self.sleep_btn.is_clicked(pos):
                            self.pet.sleep()
                            self.sound_system.play('sleep')
                            self.action_timer = 1

            if self.game_state == "play":
                self.pet.update()
                
                if self.action_timer > 0:
                    self.action_timer -= 0.016
                    if self.action_timer <= 0 and self.pet.state not in [PetState.SLEEPING, PetState.SICK]:
                        self.pet.state = PetState.IDLE

                if self.pet.is_sick and random.random() < 0.01:
                    self.sound_system.play('sick')

            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
