import pygame
import random
import math
import struct

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

COLORS = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red': (220, 50, 50),
    'green': (50, 200, 80),
    'blue': (50, 100, 255),
    'yellow': (255, 220, 50),
    'purple': (150, 50, 200),
    'orange': (255, 150, 50),
    'cyan': (50, 220, 220),
    'gray': (80, 80, 80),
    'brown': (139, 90, 43),
    'darkgreen': (20, 60, 30),
    'lightbrown': (200, 150, 100),
    'gold': (255, 215, 0),
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("塔防卡牌融合")
clock = pygame.time.Clock()
font_small = pygame.font.Font(None, 22)
font_normal = pygame.font.Font(None, 28)
font_big = pygame.font.Font(None, 42)
font_title = pygame.font.Font(None, 56)

CARD_WIDTH = 70
CARD_HEIGHT = 95
HAND_Y = HEIGHT - 130
BATTLE_ZONE_Y = 280
BASE_X = 80

CARD_TEMPLATES = {
    'soldier': {'name': '步兵', 'cost': 1, 'atk': 2, 'hp': 3, 'range': 60, 'speed': 1, 'type': 'unit', 'color': COLORS['blue']},
    'archer': {'name': '弓手', 'cost': 2, 'atk': 3, 'hp': 2, 'range': 120, 'speed': 1, 'type': 'unit', 'color': COLORS['green']},
    'knight': {'name': '骑士', 'cost': 3, 'atk': 4, 'hp': 5, 'range': 50, 'speed': 2, 'type': 'unit', 'color': COLORS['yellow']},
    'mage': {'name': '法师', 'cost': 4, 'atk': 6, 'hp': 3, 'range': 150, 'speed': 1, 'type': 'unit', 'color': COLORS['purple']},
    'tank': {'name': '坦克', 'cost': 5, 'atk': 3, 'hp': 10, 'range': 40, 'speed': 1, 'type': 'unit', 'color': COLORS['gray']},
    'healer': {'name': '牧师', 'cost': 3, 'atk': 0, 'hp': 4, 'range': 100, 'speed': 1, 'type': 'unit', 'color': COLORS['white'], 'heal': 2},
    'fireball': {'name': '火球术', 'cost': 2, 'damage': 4, 'type': 'spell', 'color': COLORS['orange']},
    'lightning': {'name': '闪电术', 'cost': 3, 'damage': 6, 'type': 'spell', 'color': COLORS['cyan']},
    'freeze': {'name': '冰冻术', 'cost': 2, 'damage': 2, 'freeze': 2, 'type': 'spell', 'color': COLORS['lightbrown']},
    'arrow': {'name': '箭雨', 'cost': 1, 'damage': 2, 'type': 'spell', 'color': COLORS['brown']},
}

ENEMY_TEMPLATES = {
    'goblin': {'name': '哥布林', 'hp': 5, 'atk': 2, 'speed': 1.5, 'reward': 1},
    'orc': {'name': '兽人', 'hp': 12, 'atk': 4, 'speed': 1, 'reward': 2},
    'troll': {'name': '巨魔', 'hp': 25, 'atk': 6, 'speed': 0.7, 'reward': 3},
    'boss': {'name': 'BOSS', 'hp': 50, 'atk': 10, 'speed': 0.5, 'reward': 5},
}

class Card:
    def __init__(self, template_key, level=1):
        template = CARD_TEMPLATES[template_key]
        self.template_key = template_key
        self.name = template['name']
        self.cost = template['cost'] + (level - 1)
        self.level = level
        self.type = template['type']
        self.color = template['color']
        
        if self.type == 'unit':
            self.max_hp = template['hp'] + (level - 1) * 2
            self.hp = self.max_hp
            self.atk = template['atk'] + (level - 1)
            self.range = template['range']
            self.speed = template['speed']
            self.x = 0
            self.y = 0
            self.cooldown = 0
            self.has_target = False
            if 'heal' in template:
                self.heal_amount = template['heal']
        else:
            self.damage = template.get('damage', 0)
            self.freeze = template.get('freeze', 0)
    
    def draw(self, surface, x, y, selected=False, in_hand=True):
        bw = CARD_WIDTH
        bh = CARD_HEIGHT
        if in_hand:
            bh = CARD_HEIGHT + 15
        
        pygame.draw.rect(surface, COLORS['black'], (x, y, bw, bh), border_radius=6)
        pygame.draw.rect(surface, self.color, (x + 2, y + 2, bw - 4, bh - 4), border_radius=5)
        
        level_colors = [COLORS['white'], COLORS['green'], COLORS['blue'], COLORS['purple'], COLORS['orange']]
        lvl_color = level_colors[min(self.level - 1, 4)]
        
        pygame.draw.rect(surface, lvl_color, (x + bw - 18, y + 3, 15, 15), border_radius=3)
        lvl_text = font_small.render(str(self.level), True, COLORS['black'])
        surface.blit(lvl_text, (x + bw - 15, y + 5))
        
        name_text = font_small.render(self.name, True, COLORS['white'])
        if self.type == 'unit':
            shadow = font_small.render(self.name, True, COLORS['black'])
            surface.blit(shadow, (x + bw // 2 - name_text.get_width() // 2 + 1, y + 20 + 1))
            surface.blit(name_text, (x + bw // 2 - name_text.get_width() // 2, y + 20))
        else:
            shadow = font_small.render(self.name, True, COLORS['black'])
            surface.blit(shadow, (x + bw // 2 - name_text.get_width() // 2 + 1, y + 15 + 1))
            surface.blit(name_text, (x + bw // 2 - name_text.get_width() // 2, y + 15))
        
        if self.type == 'unit':
            bar_w = bw - 10
            bar_h = 6
            bar_x = x + 5
            bar_y = y + 40
            
            pygame.draw.rect(surface, COLORS['red'], (bar_x, bar_y, bar_w, bar_h), border_radius=2)
            hp_ratio = self.hp / self.max_hp
            pygame.draw.rect(surface, COLORS['green'], (bar_x, bar_y, int(bar_w * hp_ratio), bar_h), border_radius=2)
            
            atk_icon = font_small.render(f"⚔{self.atk}", True, COLORS['yellow'])
            hp_icon = font_small.render(f"♥{self.hp}", True, COLORS['red'])
            surface.blit(atk_icon, (x + 5, y + 50))
            surface.blit(hp_icon, (x + bw - 35, y + 50))
            
            range_icon = font_small.render(f"◎{self.range}", True, COLORS['cyan'])
            surface.blit(range_icon, (x + bw // 2 - 15, y + 50))
        else:
            dmg_text = font_small.render(f"伤害:{self.damage}", True, COLORS['yellow'])
            surface.blit(dmg_text, (x + bw // 2 - dmg_text.get_width() // 2, y + 35))
            
            if self.freeze > 0:
                frz_text = font_small.render(f"冻结:{self.freeze}", True, COLORS['cyan'])
                surface.blit(frz_text, (x + bw // 2 - frz_text.get_width() // 2, y + 50))
        
        cost_text = font_small.render(f"{self.cost}费", True, COLORS['blue'])
        pygame.draw.circle(surface, (100, 100, 200), (x + 15, y + bh - 15), 10)
        surface.blit(cost_text, (x + 7, y + bh - 22))
        
        if self.type == 'spell':
            spell_icon = font_small.render("法", True, COLORS['purple'])
            surface.blit(spell_icon, (x + bw // 2 - 8, y + bh - 25))
        
        if selected:
            pygame.draw.rect(surface, COLORS['yellow'], (x - 2, y - 2, bw + 4, bh + 4), 3, border_radius=7)
    
    def can_fuse_with(self, other):
        return (self.template_key == other.template_key and 
                self.level == other.level and self.level < 5)

class Unit:
    def __init__(self, card, x, y):
        self.card = card
        self.x = x
        self.y = y
        self.hp = card.hp
        self.max_hp = card.max_hp
        self.atk = card.atk
        self.range = card.range
        self.speed = card.speed
        self.cooldown = 0
        self.target = None
        self.heal_amount = getattr(card, 'heal_amount', 0)
        self.fuse_source = True
    
    def update(self, enemies, units):
        if self.cooldown > 0:
            self.cooldown -= 1
        
        if self.heal_amount > 0:
            for u in units:
                if u != self and u.hp < u.max_hp and self.distance_to(u) <= self.range:
                    u.hp = min(u.max_hp, u.hp + self.heal_amount)
                    break
        
        self.target = None
        for e in enemies:
            if self.distance_to(e) <= self.range:
                self.target = e
                break
        
        if self.target and self.cooldown <= 0 and self.atk > 0:
            self.target.hp -= self.atk
            self.cooldown = max(10, 60 // self.speed)
            return True, self.target
        return False, None
    
    def distance_to(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    
    def draw(self, surface):
        size = 25 + self.card.level * 3
        pygame.draw.circle(surface, self.card.color, (int(self.x), int(self.y)), size)
        pygame.draw.circle(surface, COLORS['white'], (int(self.x), int(self.y)), size, 2)
        
        if self.target:
            pygame.draw.line(surface, COLORS['red'], (self.x, self.y), (self.target.x, self.target.y), 1)
        
        bar_w = size * 2
        bar_h = 5
        bar_x = self.x - size
        bar_y = self.y - size - 10
        
        pygame.draw.rect(surface, COLORS['red'], (bar_x, bar_y, bar_w, bar_h), border_radius=2)
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, COLORS['green'], (bar_x, bar_y, int(bar_w * hp_ratio), bar_h), border_radius=2)
        
        pygame.draw.rect(surface, COLORS['black'], (int(self.x - 6), int(self.y - 6), 12, 12))
        pygame.draw.rect(surface, COLORS['white'], (int(self.x - 5), int(self.y - 5), 10, 10))
        lvl_text = font_small.render(str(self.card.level), True, COLORS['black'])
        surface.blit(lvl_text, (int(self.x - lvl_text.get_width() // 2 - 0.5), int(self.y - lvl_text.get_height() // 2 - 0.5)))

class Enemy:
    def __init__(self, template_key, x, y):
        template = ENEMY_TEMPLATES[template_key]
        self.template_key = template_key
        self.name = template['name']
        self.hp = template['hp']
        self.max_hp = template['hp']
        self.atk = template['atk']
        self.speed = template['speed']
        self.reward = template['reward']
        self.x = x
        self.y = y
        self.frozen = 0
        self.size = 20 + (3 if template_key == 'boss' else 0)
    
    def update(self, units, base_hp):
        if self.frozen > 0:
            self.frozen -= 1
            return None
        
        self.x -= self.speed
        for u in units:
            dist = math.sqrt((self.x - u.x) ** 2 + (self.y - u.y) ** 2)
            if dist < self.size + 25:
                u.hp -= self.atk
                self.x += self.speed * 3
                break
        
        if self.x <= BASE_X:
            return True
        return False
    
    def draw(self, surface):
        color = COLORS['cyan'] if self.frozen > 0 else COLORS['red']
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(surface, COLORS['black'], (int(self.x), int(self.y)), self.size, 2)
        
        eyes_x = int(self.x - 8)
        eyes_y = int(self.y - 5)
        pygame.draw.circle(surface, COLORS['white'], (eyes_x, eyes_y), 4)
        pygame.draw.circle(surface, COLORS['white'], (eyes_x + 16, eyes_y), 4)
        pygame.draw.circle(surface, COLORS['black'], (eyes_x - 1, eyes_y - 1), 2)
        pygame.draw.circle(surface, COLORS['black'], (eyes_x + 15, eyes_y - 1), 2)
        
        mouth_x = int(self.x - 10)
        mouth_y = int(self.y + 5)
        pygame.draw.rect(surface, COLORS['black'], (mouth_x, mouth_y, 20, 8), border_radius=3)
        for i in range(3):
            tooth_x = mouth_x + 3 + i * 6
            pygame.draw.polygon(surface, COLORS['white'], [(tooth_x, mouth_y), (tooth_x + 3, mouth_y + 5), (tooth_x + 6, mouth_y)])
        
        bar_w = self.size * 2
        bar_h = 5
        bar_x = self.x - self.size
        bar_y = self.y - self.size - 10
        
        pygame.draw.rect(surface, COLORS['red'], (bar_x, bar_y, bar_w, bar_h), border_radius=2)
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, COLORS['green'], (bar_x, bar_y, int(bar_w * hp_ratio), bar_h), border_radius=2)
        
        if self.frozen > 0:
            frz_text = font_small.render("❄", True, COLORS['cyan'])
            surface.blit(frz_text, (int(self.x - 5), int(self.y - self.size - 20)))

class Game:
    def __init__(self):
        self.state = 'menu'
        self.player_hp = 20
        self.max_player_hp = 20
        self.gold = 5
        self.mana = 3
        self.max_mana = 3
        self.turn = 1
        self.wave = 1
        
        self.hand = []
        self.battle_units = []
        self.enemies = []
        self.projectiles = []
        
        self.selected_card = None
        self.selected_unit = None
        self.fuse_mode = False
        
        self.wave_timer = 0
        self.wave_cooldown = 300
        self.wave_active = False
        self.wave_enemies_remaining = 0
        
        self.enemies_killed = 0
        self.score = 0
        
        self.message = ""
        self.message_timer = 0
        
        self.effects = []
        
        self.sound_enabled = True
        self.init_audio()
    
    def init_audio(self):
        try:
            pygame.mixer.init(frequency=22050, size=-8, channels=1)
            self.sounds = {
                'place': self.generate_sound(400, 0.1, 'square'),
                'attack': self.generate_sound(200, 0.15, 'sawtooth'),
                'hit': self.generate_sound(150, 0.1, 'noise'),
                'spell': self.generate_sound(600, 0.2, 'sine'),
                'fuse': self.generate_sound(800, 0.3, 'triangle'),
                'wave': self.generate_sound(300, 0.5, 'square'),
                'death': self.generate_sound(100, 0.3, 'sawtooth'),
            }
        except:
            self.sound_enabled = False
    
    def generate_sound(self, freq, duration, wave_type='sine'):
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        data = bytearray()
        
        for i in range(num_samples):
            t = i / sample_rate
            envelope = 1.0 - (i / num_samples) * 0.7
            
            if wave_type == 'sine':
                val = math.sin(2 * math.pi * freq * t)
            elif wave_type == 'square':
                val = 1.0 if (freq * t) % 1 < 0.5 else -1.0
            elif wave_type == 'sawtooth':
                val = 2 * ((freq * t) % 1) - 1
            elif wave_type == 'triangle':
                val = 2 * abs(2 * ((freq * t) % 1) - 1) - 1
            elif wave_type == 'noise':
                val = random.uniform(-1, 1)
            
            sample = int(val * envelope * 8000)
            sample = max(-32768, min(32767, sample))
            data.extend(struct.pack('<h', sample))
        
        return pygame.mixer.Sound(buffer=bytes(data))
    
    def play_sound(self, name):
        if self.sound_enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except:
                pass
    
    def draw_menu(self):
        screen.fill(COLORS['darkgreen'])
        
        for i in range(10):
            y = 100 + i * 50
            for j in range(20):
                x = j * 40 + (i % 2) * 20
                pygame.draw.rect(screen, (30, 70, 40), (x, y, 38, 48), 1)
        
        title = font_title.render("塔防卡牌融合", True, COLORS['gold'])
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        
        subtitle = font_normal.render("融合卡牌召唤单位，抵御敌人入侵！", True, COLORS['white'])
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 160))
        
        btn_width, btn_height = 200, 50
        start_btn = pygame.Rect(WIDTH // 2 - btn_width // 2, 280, btn_width, btn_height)
        pygame.draw.rect(screen, COLORS['green'], start_btn, border_radius=10)
        start_text = font_big.render("开始游戏", True, COLORS['white'])
        screen.blit(start_text, (start_btn.centerx - start_text.get_width() // 2, start_btn.centery - start_text.get_height() // 2))
        
        help_btn = pygame.Rect(WIDTH // 2 - btn_width // 2, 350, btn_width, btn_height)
        pygame.draw.rect(screen, COLORS['blue'], help_btn, border_radius=10)
        help_text = font_big.render("游戏说明", True, COLORS['white'])
        screen.blit(help_text, (help_btn.centerx - help_text.get_width() // 2, help_btn.centery - help_text.get_height() // 2))
        
        quit_btn = pygame.Rect(WIDTH // 2 - btn_width // 2, 420, btn_width, btn_height)
        pygame.draw.rect(screen, COLORS['red'], quit_btn, border_radius=10)
        quit_text = font_big.render("退出游戏", True, COLORS['white'])
        screen.blit(quit_text, (quit_btn.centerx - quit_text.get_width() // 2, quit_btn.centery - quit_text.get_height() // 2))
        
        version_text = font_small.render("v1.0", True, COLORS['gray'])
        screen.blit(version_text, (WIDTH - 50, HEIGHT - 30))
        
        return start_btn, help_btn, quit_btn
    
    def draw_help(self):
        screen.fill(COLORS['darkgreen'])
        
        title = font_big.render("游戏说明", True, COLORS['gold'])
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
        
        instructions = [
            "【基本操作】",
            "点击手牌选中，然后点击战场放置单位",
            "右键点击两个同等级单位进行融合升级",
            "法术卡直接对敌人造成伤害",
            "",
            "【单位卡】",
            "步兵、弓手、骑士、法师、坦克、牧师",
            "单位会在范围内攻击敌人",
            "牧师可以治疗友方单位",
            "",
            "【法术卡】",
            "火球术：造成4点伤害",
            "闪电术：造成6点伤害",
            "冰冻术：造成2点伤害并冻结",
            "箭雨：对所有敌人造成2点伤害",
            "",
            "【融合系统】",
            "两张相同等级的单位卡可融合",
            "融合后等级+1，属性大幅提升",
            "",
            "【胜利条件】",
            "抵御所有波次敌人进攻",
        ]
        
        y = 70
        for line in instructions:
            if line.startswith("【"):
                text = font_normal.render(line, True, COLORS['yellow'])
            else:
                text = font_small.render(line, True, COLORS['white'])
            screen.blit(text, (50, y))
            y += 25
        
        back_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT - 80, 160, 45)
        pygame.draw.rect(screen, COLORS['blue'], back_btn, border_radius=8)
        back_text = font_normal.render("返回主菜单", True, COLORS['white'])
        screen.blit(back_text, (back_btn.centerx - back_text.get_width() // 2, back_btn.centery - back_text.get_height() // 2))
        
        return back_btn
    
    def draw_game(self):
        screen.fill(COLORS['darkgreen'])
        
        pygame.draw.rect(screen, COLORS['brown'], (0, 0, BASE_X + 30, HEIGHT))
        pygame.draw.rect(screen, COLORS['lightbrown'], (BASE_X, 0, 30, HEIGHT))
        
        for i in range(5):
            pygame.draw.rect(screen, COLORS['brown'], 
                           (BASE_X + 5, BATTLE_ZONE_Y + 15 + i * 60, 20, 50))
            pygame.draw.rect(screen, COLORS['black'],
                           (BASE_X + 8, BATTLE_ZONE_Y + 20 + i * 60, 14, 40))
        
        heart_x, heart_y = 35, 50
        pygame.draw.circle(screen, COLORS['red'], (heart_x, heart_y), 20)
        for dx, dy in [(-5, 0), (5, 0), (0, -5), (0, 5)]:
            pygame.draw.circle(screen, COLORS['red'], (heart_x + dx, heart_y + dy), 10)
        pygame.draw.circle(screen, COLORS['white'], (heart_x, heart_y), 20, 2)
        
        hp_text = font_normal.render(f"{self.player_hp}/{self.max_player_hp}", True, COLORS['white'])
        screen.blit(hp_text, (heart_x - hp_text.get_width() // 2, heart_y + 25))
        
        pygame.draw.rect(screen, (40, 80, 50), (0, HAND_Y - 10, WIDTH, HEIGHT - HAND_Y + 10))
        
        lane_colors = [(60, 100, 70), (50, 90, 60), (60, 100, 70), (50, 90, 60), (60, 100, 70)]
        for i in range(5):
            lane_y = BATTLE_ZONE_Y + 10 + i * 60
            pygame.draw.rect(screen, lane_colors[i], (BASE_X + 30, lane_y, WIDTH - BASE_X - 60, 55))
            pygame.draw.rect(screen, (30, 60, 40), (BASE_X + 30, lane_y, WIDTH - BASE_X - 60, 55), 1)
        
        for enemy in self.enemies:
            enemy.draw(screen)
        
        for unit in self.battle_units:
            unit.draw(screen)
        
        for proj in self.projectiles:
            pygame.draw.circle(screen, proj['color'], (int(proj['x']), int(proj['y'])), proj['size'])
        
        for effect in self.effects[:]:
            alpha = effect['life'] / effect['max_life']
            color = tuple(int(c * alpha) for c in effect['color'])
            pygame.draw.circle(screen, color, (int(effect['x']), int(effect['y'])), int(effect['size'] * alpha))
            effect['life'] -= 1
            effect['size'] *= 1.05
            if effect['life'] <= 0:
                self.effects.remove(effect)
        
        hand_start = 50
        card_spacing = 85
        for i, card in enumerate(self.hand):
            x = hand_start + i * card_spacing
            selected = (self.selected_card == i)
            card.draw(screen, x, HAND_Y, selected=selected, in_hand=True)
        
        if self.selected_unit is not None:
            unit = self.battle_units[self.selected_unit]
            for i, other in enumerate(self.battle_units):
                if i != self.selected_unit and unit.card.can_fuse_with(other.card):
                    pygame.draw.circle(screen, COLORS['gold'], (int(other.x), int(other.y)), 35, 3)
        
        info_y = 10
        pygame.draw.rect(screen, (0, 0, 0, 150), (5, 5, 200, 80), border_radius=5)
        hp_bar = pygame.Rect(10, info_y + 25, 120, 15)
        pygame.draw.rect(screen, COLORS['red'], hp_bar, border_radius=3)
        pygame.draw.rect(screen, COLORS['green'], (10, info_y + 25, int(120 * self.player_hp / self.max_player_hp), 15), border_radius=3)
        screen.blit(font_small.render(f"生命: {self.player_hp}/{self.max_player_hp}", True, COLORS['white']), (10, info_y))
        
        screen.blit(font_small.render(f"金币: {self.gold}", True, COLORS['yellow']), (10, info_y + 45))
        
        pygame.draw.rect(screen, (0, 0, 0, 150), (WIDTH - 155, 5, 150, 80), border_radius=5)
        mana_text = font_small.render(f"法力: {self.mana}/{self.max_mana}", True, COLORS['cyan'])
        screen.blit(mana_text, (WIDTH - 150, info_y))
        
        for i in range(self.max_mana):
            x = WIDTH - 150 + i * 20
            color = COLORS['cyan'] if i < self.mana else COLORS['gray']
            pygame.draw.circle(screen, color, (x, info_y + 30), 8)
        
        screen.blit(font_small.render(f"波次: {self.wave}", True, COLORS['orange']), (WIDTH - 150, info_y + 45))
        screen.blit(font_small.render(f"回合: {self.turn}", True, COLORS['white']), (WIDTH - 150, info_y + 65))
        
        if self.fuse_mode:
            fuse_text = font_normal.render("融合模式: 点击两个同等级单位", True, COLORS['gold'])
            screen.blit(fuse_text, (WIDTH // 2 - fuse_text.get_width() // 2, HEIGHT - 30))
        
        if self.wave_cooldown > 0 and not self.wave_active:
            countdown = self.wave_cooldown // 60
            wave_text = font_normal.render(f"下一波次: {countdown}秒", True, COLORS['orange'])
            screen.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, 50))
        
        if self.message_timer > 0:
            self.message_timer -= 1
            alpha = min(255, self.message_timer * 5)
            msg_surf = font_normal.render(self.message, True, COLORS['yellow'])
            screen.blit(msg_surf, (WIDTH // 2 - msg_surf.get_width() // 2, HEIGHT // 2))
        
        if self.player_hp <= 0:
            self.state = 'gameover'
        
        if self.wave > 10 and len(self.enemies) == 0 and self.wave_cooldown <= 0:
            self.state = 'victory'
    
    def draw_gameover(self):
        screen.fill(COLORS['black'])
        
        title = font_title.render("游戏结束", True, COLORS['red'])
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
        
        stats = [
            f"最终波次: {self.wave}",
            f"击杀敌人: {self.enemies_killed}",
            f"最终得分: {self.score}",
        ]
        
        y = 250
        for stat in stats:
            text = font_normal.render(stat, True, COLORS['white'])
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 40
        
        btn_width, btn_height = 180, 50
        restart_btn = pygame.Rect(WIDTH // 2 - btn_width // 2, 400, btn_width, btn_height)
        pygame.draw.rect(screen, COLORS['green'], restart_btn, border_radius=10)
        restart_text = font_big.render("重新开始", True, COLORS['white'])
        screen.blit(restart_text, (restart_btn.centerx - restart_text.get_width() // 2, restart_btn.centery - restart_text.get_height() // 2))
        
        menu_btn = pygame.Rect(WIDTH // 2 - btn_width // 2, 470, btn_width, btn_height)
        pygame.draw.rect(screen, COLORS['blue'], menu_btn, border_radius=10)
        menu_text = font_big.render("返回主菜单", True, COLORS['white'])
        screen.blit(menu_text, (menu_btn.centerx - menu_text.get_width() // 2, menu_btn.centery - menu_text.get_height() // 2))
        
        return restart_btn, menu_btn
    
    def draw_victory(self):
        screen.fill(COLORS['darkgreen'])
        
        title = font_title.render("胜利！", True, COLORS['gold'])
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        
        subtitle = font_big.render("你成功抵御了所有敌人！", True, COLORS['white'])
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 170))
        
        stats = [
            f"防守回合: {self.turn}",
            f"击杀敌人: {self.enemies_killed}",
            f"最终得分: {self.score}",
        ]
        
        y = 250
        for stat in stats:
            text = font_normal.render(stat, True, COLORS['yellow'])
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 40
        
        btn_width, btn_height = 180, 50
        restart_btn = pygame.Rect(WIDTH // 2 - btn_width // 2, 400, btn_width, btn_height)
        pygame.draw.rect(screen, COLORS['green'], restart_btn, border_radius=10)
        restart_text = font_big.render("再玩一次", True, COLORS['white'])
        screen.blit(restart_text, (restart_btn.centerx - restart_text.get_width() // 2, restart_btn.centery - restart_text.get_height() // 2))
        
        menu_btn = pygame.Rect(WIDTH // 2 - btn_width // 2, 470, btn_width, btn_height)
        pygame.draw.rect(screen, COLORS['blue'], menu_btn, border_radius=10)
        menu_text = font_big.render("返回主菜单", True, COLORS['white'])
        screen.blit(menu_text, (menu_btn.centerx - menu_text.get_width() // 2, menu_btn.centery - menu_text.get_height() // 2))
        
        return restart_btn, menu_btn
    
    def spawn_unit(self, card, lane):
        y = BATTLE_ZONE_Y + 37 + lane * 60
        x = BASE_X + 60 + len([u for u in self.battle_units if abs(u.y - y) < 30]) * 35
        x = min(x, WIDTH - 100)
        
        unit = Unit(card, x, y)
        self.battle_units.append(unit)
        self.play_sound('place')
        
        self.effects.append({'x': x, 'y': y, 'size': 30, 'life': 20, 'max_life': 20, 'color': COLORS['green']})
    
    def spawn_enemies(self):
        if self.wave > 10:
            return
        
        self.wave_active = True
        enemy_count = 3 + self.wave
        self.wave_enemies_remaining = enemy_count
        
        for i in range(enemy_count):
            delay = i * (40 - min(self.wave * 2, 30))
            lane = i % 5
            
            if self.wave >= 8 and i == enemy_count - 1:
                template = 'boss'
            elif self.wave >= 5 and random.random() < 0.3:
                template = 'troll'
            elif self.wave >= 3 and random.random() < 0.4:
                template = 'orc'
            else:
                template = random.choice(['goblin', 'goblin', 'orc'])
            
            enemy = Enemy(template, WIDTH + 50 + delay * 2, BATTLE_ZONE_Y + 37 + lane * 60)
            self.enemies.append(enemy)
        
        self.play_sound('wave')
        self.show_message(f"第{self.wave}波敌人来袭！")
    
    def cast_spell(self, card, target_enemy):
        self.play_sound('spell')
        
        if target_enemy:
            target_enemy.hp -= card.damage
            if card.freeze > 0:
                target_enemy.frozen += card.freeze * 30
            
            self.effects.append({
                'x': target_enemy.x,
                'y': target_enemy.y,
                'size': 20,
                'life': 30,
                'max_life': 30,
                'color': card.color
            })
            
            self.show_message(f"{card.name}对{target_enemy.name}造成{card.damage}伤害！")
        else:
            for enemy in self.enemies[:]:
                enemy.hp -= card.damage
                if card.freeze > 0:
                    enemy.frozen += card.freeze * 30
            
            self.show_message(f"{card.name}对所有敌人造成{card.damage}伤害！")
            
            for enemy in self.enemies:
                self.effects.append({
                    'x': enemy.x,
                    'y': enemy.y,
                    'size': 15,
                    'life': 20,
                    'max_life': 20,
                    'color': card.color
                })
    
    def fuse_units(self, idx1, idx2):
        u1 = self.battle_units[idx1]
        u2 = self.battle_units[idx2]
        
        if u1.card.can_fuse_with(u2.card):
            new_card = Card(u1.card.template_key, u1.card.level + 1)
            new_unit = Unit(new_card, (u1.x + u2.x) // 2, (u1.y + u2.y) // 2)
            
            self.battle_units.remove(u1)
            self.battle_units.remove(u2)
            self.battle_units.append(new_unit)
            
            self.play_sound('fuse')
            
            self.effects.append({
                'x': new_unit.x,
                'y': new_unit.y,
                'size': 40,
                'life': 40,
                'max_life': 40,
                'color': COLORS['gold']
            })
            
            self.show_message(f"融合成功！{new_card.name} Lv.{new_card.level}")
            return True
        return False
    
    def end_turn(self):
        self.turn += 1
        self.mana = min(10, self.max_mana + 1)
        self.max_mana = min(10, self.max_mana + 1)
        
        if len(self.hand) < 7:
            self.draw_new_card()
        
        self.selected_card = None
        self.selected_unit = None
    
    def draw_new_card(self):
        templates = list(CARD_TEMPLATES.keys())
        weights = [3 if CARD_TEMPLATES[t]['type'] == 'unit' else 2 for t in templates]
        template = random.choices(templates, weights=weights)[0]
        level = random.choice([1, 1, 1, 2])
        self.hand.append(Card(template, level))
    
    def update_game(self):
        if self.wave_cooldown > 0:
            self.wave_cooldown -= 1
            if self.wave_cooldown == 0:
                self.spawn_enemies()
        
        for unit in self.battle_units[:]:
            attacked, target = unit.update(self.enemies, self.battle_units)
            if attacked:
                self.play_sound('attack')
                
                self.projectiles.append({
                    'x': unit.x,
                    'y': unit.y,
                    'target_x': target.x,
                    'target_y': target.y,
                    'color': COLORS['yellow'],
                    'size': 5,
                    'speed': 15
                })
        
        for enemy in self.enemies[:]:
            reached_base = enemy.update(self.battle_units, self.player_hp)
            if reached_base:
                self.player_hp -= enemy.atk
                self.enemies.remove(enemy)
                self.play_sound('hit')
                self.show_message("敌人攻击了基地！")
        
        for proj in self.projectiles[:]:
            dx = proj['target_x'] - proj['x']
            dy = proj['target_y'] - proj['y']
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < proj['speed']:
                self.projectiles.remove(proj)
            else:
                proj['x'] += (dx / dist) * proj['speed']
                proj['y'] += (dy / dist) * proj['speed']
        
        dead_units = [u for u in self.battle_units if u.hp <= 0]
        for u in dead_units:
            self.battle_units.remove(u)
            self.play_sound('death')
            self.effects.append({
                'x': u.x, 'y': u.y, 'size': 25, 'life': 25, 'max_life': 25, 'color': COLORS['red']
            })
        
        dead_enemies = [e for e in self.enemies if e.hp <= 0]
        for e in dead_enemies:
            self.enemies.remove(e)
            self.gold += e.reward
            self.score += e.reward * 10
            self.enemies_killed += 1
            self.play_sound('death')
            self.effects.append({
                'x': e.x, 'y': e.y, 'size': 30, 'life': 30, 'max_life': 30, 'color': COLORS['orange']
            })
        
        if self.wave_active and len(self.enemies) == 0:
            self.wave_active = False
            self.wave += 1
            self.wave_cooldown = 180
            self.show_message(f"成功抵御第{self.wave - 1}波！")
    
    def show_message(self, msg):
        self.message = msg
        self.message_timer = 90
    
    def get_card_at(self, mx, my):
        if HAND_Y <= my <= HAND_Y + CARD_HEIGHT + 15:
            for i in range(len(self.hand)):
                x = 50 + i * 85
                if x <= mx <= x + CARD_WIDTH:
                    return ('card', i)
        return None
    
    def get_unit_at(self, mx, my):
        for i, unit in enumerate(self.battle_units):
            dist = math.sqrt((unit.x - mx) ** 2 + (unit.y - my) ** 2)
            if dist <= 30:
                return ('unit', i)
        return None
    
    def get_lane_at(self, mx, my):
        if BATTLE_ZONE_Y <= my <= BATTLE_ZONE_Y + 300:
            lane = int((my - BATTLE_ZONE_Y) / 60)
            return max(0, min(4, lane))
        return None
    
    def get_enemy_at(self, mx, my):
        for enemy in self.enemies:
            dist = math.sqrt((enemy.x - mx) ** 2 + (enemy.y - my) ** 2)
            if dist <= enemy.size:
                return enemy
        return None
    
    def reset(self):
        self.__init__()

def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                if game.state == 'menu':
                    start_btn, help_btn, quit_btn = game.draw_menu()
                    if start_btn.collidepoint(mx, my):
                        game.state = 'playing'
                        for _ in range(4):
                            game.draw_new_card()
                    elif help_btn.collidepoint(mx, my):
                        game.state = 'help'
                    elif quit_btn.collidepoint(mx, my):
                        running = False
                
                elif game.state == 'help':
                    back_btn = game.draw_help()
                    if back_btn.collidepoint(mx, my):
                        game.state = 'menu'
                
                elif game.state == 'playing':
                    if event.button == 1:
                        card_hit = game.get_card_at(mx, my)
                        
                        if card_hit:
                            game.selected_card = card_hit[1]
                            game.selected_unit = None
                        
                        elif game.selected_card is not None:
                            lane = game.get_lane_at(mx, my)
                            if lane is not None:
                                card = game.hand[game.selected_card]
                                if card.cost <= game.mana:
                                    if card.type == 'unit':
                                        game.spawn_unit(card, lane)
                                        game.mana -= card.cost
                                        game.hand.pop(game.selected_card)
                                        game.show_message(f"放置了{card.name}")
                                    else:
                                        target = game.get_enemy_at(mx, my)
                                        game.cast_spell(card, target)
                                        game.mana -= card.cost
                                        game.hand.pop(game.selected_card)
                                    game.selected_card = None
                        
                        unit_hit = game.get_unit_at(mx, my)
                        if unit_hit:
                            if game.selected_unit is None:
                                game.selected_unit = unit_hit[1]
                            else:
                                game.fuse_units(game.selected_unit, unit_hit[1])
                                game.selected_unit = None
                        
                        elif game.selected_unit is not None and game.selected_card is None:
                            game.selected_unit = None
                        
                        for i in range(len(game.battle_units)):
                            unit = game.battle_units[i]
                            if game.selected_card is not None and game.get_unit_at(mx, my) is None:
                                card = game.hand[game.selected_card]
                                if card.type == 'spell':
                                    target = game.get_enemy_at(mx, my)
                                    if target:
                                        game.cast_spell(card, target)
                                        game.mana -= card.cost
                                        game.hand.pop(game.selected_card)
                                        game.selected_card = None
                    
                    elif event.button == 3:
                        game.selected_card = None
                        game.selected_unit = None
                
                elif game.state == 'gameover':
                    restart_btn, menu_btn = game.draw_gameover()
                    if restart_btn.collidepoint(mx, my):
                        game.reset()
                        game.state = 'playing'
                        for _ in range(4):
                            game.draw_new_card()
                    elif menu_btn.collidepoint(mx, my):
                        game.state = 'menu'
                
                elif game.state == 'victory':
                    restart_btn, menu_btn = game.draw_victory()
                    if restart_btn.collidepoint(mx, my):
                        game.reset()
                        game.state = 'playing'
                        for _ in range(4):
                            game.draw_new_card()
                    elif menu_btn.collidepoint(mx, my):
                        game.state = 'menu'
            
            elif event.type == pygame.KEYDOWN:
                if game.state == 'playing':
                    if event.key == pygame.K_SPACE:
                        game.end_turn()
                    elif event.key == pygame.K_f:
                        if game.selected_unit is not None and game.selected_card is None:
                            game.selected_unit = None
                        else:
                            game.fuse_mode = not game.fuse_mode
        
        if game.state == 'playing':
            game.update_game()
        
        if game.state == 'menu':
            game.draw_menu()
        elif game.state == 'help':
            game.draw_help()
        elif game.state == 'playing':
            game.draw_game()
        elif game.state == 'gameover':
            game.draw_gameover()
        elif game.state == 'victory':
            game.draw_victory()
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()
