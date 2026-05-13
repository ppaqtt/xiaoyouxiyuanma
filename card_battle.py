import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("卡牌对决")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
big_font = pygame.font.Font(None, 50)

CARDS_DB = [
    {'name': '战士', 'cost': 2, 'atk': 3, 'hp': 4, 'color': RED},
    {'name': '弓手', 'cost': 2, 'atk': 4, 'hp': 2, 'color': GREEN},
    {'name': '法师', 'cost': 3, 'atk': 5, 'hp': 3, 'color': BLUE},
    {'name': '骑士', 'cost': 4, 'atk': 4, 'hp': 6, 'color': YELLOW},
    {'name': '刺客', 'cost': 3, 'atk': 6, 'hp': 2, 'color': PURPLE},
    {'name': '牧师', 'cost': 2, 'atk': 1, 'hp': 5, 'color': WHITE},
    {'name': '龙骑', 'cost': 5, 'atk': 7, 'hp': 5, 'color': ORANGE},
    {'name': '盾卫', 'cost': 3, 'atk': 2, 'hp': 8, 'color': GRAY},
]

class Card:
    def __init__(self, data):
        self.name = data['name']
        self.cost = data['cost']
        self.atk = data['atk']
        self.hp = data['hp']
        self.color = data['color']
        self.has_attacked = False
    
    def draw(self, x, y, w=90, h=120, highlight=False):
        pygame.draw.rect(screen, self.color, (x, y, w, h), border_radius=8)
        pygame.draw.rect(screen, WHITE, (x + 3, y + 3, w - 6, h - 6), border_radius=6)
        
        name_text = font.render(self.name, True, BLACK)
        screen.blit(name_text, (x + w // 2 - name_text.get_width() // 2, y + 5))
        
        cost_text = font.render(str(self.cost), True, BLUE)
        pygame.draw.circle(screen, (200, 200, 255), (x + w // 2, y + 35), 12)
        screen.blit(cost_text, (x + w // 2 - cost_text.get_width() // 2, y + 27))
        
        atk_text = font.render(str(self.atk), True, RED)
        screen.blit(atk_text, (x + 8, y + h - 25))
        
        hp_text = font.render(str(self.hp), True, GREEN)
        screen.blit(hp_text, (x + w - 20, y + h - 25))
        
        if highlight:
            pygame.draw.rect(screen, YELLOW, (x, y, w, h), 3, border_radius=8)

class CardGame:
    def __init__(self):
        self.player_hp = 30
        self.ai_hp = 30
        self.player_mana = 1
        self.ai_mana = 1
        self.max_mana = 1
        self.turn = 1
        self.player_hand = []
        self.player_field = []
        self.ai_field = []
        self.selected = None
        self.game_over = False
        self.phase = 'player'  # player, ai
        self.message = ""
        self.msg_timer = 0
        
        for _ in range(4):
            self.player_hand.append(Card(random.choice(CARDS_DB)))
    
    def draw_card(self):
        if len(self.player_hand) < 8:
            self.player_hand.append(Card(random.choice(CARDS_DB)))
    
    def play_card(self, idx):
        card = self.player_hand[idx]
        if card.cost <= self.player_mana and len(self.player_field) < 5:
            self.player_mana -= card.cost
            self.player_hand.pop(idx)
            self.player_field.append(card)
            self.message = f"召唤了{card.name}!"
            self.msg_timer = 60
    
    def attack(self, attacker_idx, target_idx=None):
        attacker = self.player_field[attacker_idx]
        if attacker.has_attacked:
            return
        
        if target_idx is not None and target_idx < len(self.ai_field):
            target = self.ai_field[target_idx]
            target.hp -= attacker.atk
            attacker.hp -= target.atk
            attacker.has_attacked = True
            
            if target.hp <= 0:
                self.ai_field.pop(target_idx)
            if attacker.hp <= 0:
                self.player_field.pop(attacker_idx)
        elif len(self.ai_field) == 0:
            self.ai_hp -= attacker.atk
            attacker.has_attacked = True
            self.message = f"直接攻击! 造成{attacker.atk}伤害"
            self.msg_timer = 60
    
    def end_turn(self):
        self.player_mana = 0
        self.phase = 'ai'
    
    def ai_turn(self):
        # AI抽牌和出牌
        self.ai_mana = self.max_mana
        ai_hand = [Card(random.choice(CARDS_DB)) for _ in range(2)]
        
        for card in ai_hand[:]:
            if card.cost <= self.ai_mana and len(self.ai_field) < 5:
                self.ai_mana -= card.cost
                ai_hand.remove(card)
                self.ai_field.append(card)
        
        # AI攻击
        for attacker in self.ai_field:
            if self.player_field:
                target = random.choice(self.player_field)
                target.hp -= attacker.atk
                attacker.hp -= target.atk
                if target.hp <= 0:
                    self.player_field.remove(target)
                if attacker.hp <= 0:
                    self.ai_field.remove(attacker)
            else:
                self.player_hp -= attacker.atk
        
        # 下一回合
        self.turn += 1
        self.max_mana = min(10, self.turn)
        self.player_mana = self.max_mana
        self.draw_card()
        
        for c in self.player_field:
            c.has_attacked = False
        
        self.phase = 'player'
    
    def draw(self):
        screen.fill((20, 60, 20))
        
        # AI血量和法力
        ai_hp_text = font.render(f"AI HP: {self.ai_hp}", True, RED)
        screen.blit(ai_hp_text, (10, 10))
        
        # AI场
        for i, card in enumerate(self.ai_field):
            card.draw(200 + i * 100, 50)
        
        # 玩家场
        for i, card in enumerate(self.player_field):
            hl = (self.selected == ('field', i))
            card.draw(200 + i * 100, 300, highlight=hl)
        
        # 玩家手牌
        for i, card in enumerate(self.player_hand):
            hl = (self.selected == ('hand', i))
            card.draw(100 + i * 100, 470, highlight=hl)
        
        # UI
        pygame.draw.rect(screen, BLACK, (0, HEIGHT - 30, WIDTH, 30))
        hp_text = font.render(f"HP: {self.player_hp}  法力: {self.player_mana}/{self.max_mana}  回合: {self.turn}", True, WHITE)
        screen.blit(hp_text, (10, HEIGHT - 25))
        
        end_text = font.render("E-结束回合", True, YELLOW)
        screen.blit(end_text, (WIDTH - 130, HEIGHT - 25))
        
        if self.msg_timer > 0:
            self.msg_timer -= 1
            msg = font.render(self.message, True, WHITE)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 200))
        
        if self.phase == 'ai':
            ai_text = big_font.render("AI回合...", True, RED)
            screen.blit(ai_text, (WIDTH // 2 - 80, HEIGHT // 2))

def card_battle():
    game = CardGame()
    running = True
    ai_timer = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and game.phase == 'player' and not game.game_over:
                mx, my = event.pos
                
                if event.button == 1:
                    # 点击手牌
                    for i in range(len(game.player_hand)):
                        x, y = 100 + i * 100, 470
                        if x < mx < x + 90 and y < my < y + 120:
                            game.play_card(i)
                            break
                    
                    # 点击场上的牌
                    for i in range(len(game.player_field)):
                        x, y = 200 + i * 100, 300
                        if x < mx < x + 90 and y < my < y + 120:
                            if game.selected and game.selected[0] == 'field' and game.selected[1] != i:
                                pass
                            else:
                                game.selected = ('field', i)
                            break
                    
                    # 点击AI场上的牌（攻击目标）
                    if game.selected and game.selected[0] == 'field':
                        for i in range(len(game.ai_field)):
                            x, y = 200 + i * 100, 50
                            if x < mx < x + 90 and y < my < y + 120:
                                game.attack(game.selected[1], i)
                                game.selected = None
                                break
                        else:
                            # 点击AI头像区域=直接攻击
                            if my < 200 and len(game.ai_field) == 0:
                                game.attack(game.selected[1])
                                game.selected = None
                
                elif event.button == 3:
                    game.selected = None
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e and game.phase == 'player':
                    game.end_turn()
                    ai_timer = 60
        
        # AI回合
        if game.phase == 'ai':
            ai_timer -= 1
            if ai_timer <= 0:
                game.ai_turn()
        
        # 检查胜负
        if game.player_hp <= 0:
            game.game_over = True
        elif game.ai_hp <= 0:
            game.game_over = True
        
        game.draw()
        
        if game.game_over:
            winner = "玩家获胜!" if game.ai_hp <= 0 else "AI获胜!"
            go_text = big_font.render(winner, True, YELLOW)
            screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    card_battle()
