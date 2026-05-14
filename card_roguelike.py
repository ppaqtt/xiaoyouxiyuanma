
import pygame
import random
import sys

# 初始化Pygame
pygame.init()

# 窗口设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("卡牌Roguelike - 卡牌地牢")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 200)
GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)

# 字体
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# 卡牌类
class Card:
    def __init__(self, name, cost, damage, block, effect, description):
        self.name = name
        self.cost = cost
        self.damage = damage
        self.block = block
        self.effect = effect
        self.description = description

# 遗物类
class Relic:
    def __init__(self, name, effect, description):
        self.name = name
        self.effect = effect
        self.description = description

# 敌人类
class Enemy:
    def __init__(self, name, hp, damage):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.damage = damage
        self.block = 0
        self.intent = damage

# 玩家类
class Player:
    def __init__(self):
        self.max_hp = 80
        self.hp = 80
        self.block = 0
        self.energy = 3
        self.max_energy = 3
        self.gold = 100
        self.deck = []
        self.hand = []
        self.discard = []
        self.relics = []
        self.strength = 0
        self.dexterity = 0
        
        # 初始卡组
        self.deck = [
            Card("打击", 1, 6, 0, "none", "造成6点伤害"),
            Card("打击", 1, 6, 0, "none", "造成6点伤害"),
            Card("打击", 1, 6, 0, "none", "造成6点伤害"),
            Card("打击", 1, 6, 0, "none", "造成6点伤害"),
            Card("防御", 1, 0, 5, "none", "获得5点护甲"),
            Card("防御", 1, 0, 5, "none", "获得5点护甲"),
            Card("防御", 1, 0, 5, "none", "获得5点护甲"),
            Card("防御", 1, 0, 5, "none", "获得5点护甲"),
        ]

# 游戏状态
class GameState:
    def __init__(self):
        self.player = Player()
        self.floor = 1
        self.state = "map"  # map, battle, shop, rest
        self.enemy = None
        self.selected_card = None
        self.message = ""
        self.map_nodes = []
        self.current_node = 0
        self.generate_map()

    def generate_map(self):
        self.map_nodes = []
        for i in range(10):
            if i == 9:
                node_type = "boss"
            elif i == 0:
                node_type = "start"
            else:
                node_type = random.choice(["battle", "battle", "battle", "rest", "shop", "elite"])
            self.map_nodes.append(node_type)

    def draw_card(self, num=5):
        for _ in range(num):
            if not self.player.deck:
                self.player.deck = self.player.discard[:]
                self.player.discard = []
                random.shuffle(self.player.deck)
            if self.player.deck:
                self.player.hand.append(self.player.deck.pop())

    def discard_hand(self):
        self.player.discard.extend(self.player.hand)
        self.player.hand = []

    def start_battle(self, is_elite=False, is_boss=False):
        self.state = "battle"
        self.player.block = 0
        self.player.energy = self.player.max_energy
        
        if is_boss:
            self.enemy = Enemy("史莱姆王", 150, 15)
        elif is_elite:
            self.enemy = Enemy("精英史莱姆", 60, 12)
        else:
            enemies = [
                Enemy("史莱姆", 30, 6),
                Enemy("哥布林", 25, 8),
                Enemy("骷髅", 35, 7),
            ]
            self.enemy = random.choice(enemies)
        
        self.discard_hand()
        self.draw_card()
        self.message = f"战斗开始！面对 {self.enemy.name}"

    def play_card(self, card):
        if self.player.energy >= card.cost:
            self.player.energy -= card.cost
            
            # 计算伤害
            damage = card.damage + self.player.strength
            if damage > 0:
                # 先破甲
                if self.enemy.block > 0:
                    if damage >= self.enemy.block:
                        damage -= self.enemy.block
                        self.enemy.block = 0
                    else:
                        self.enemy.block -= damage
                        damage = 0
                self.enemy.hp -= damage
                if damage > 0:
                    self.message = f"对 {self.enemy.name} 造成 {damage} 点伤害！"
            
            # 获得护甲
            block = card.block + self.player.dexterity
            if block > 0:
                self.player.block += block
                self.message = f"获得 {block} 点护甲！"
            
            # 特殊效果
            if card.effect == "draw":
                self.draw_card(2)
            elif card.effect == "strength":
                self.player.strength += 2
                self.message = "力量 +2！"
            elif card.effect == "dexterity":
                self.player.dexterity += 2
                self.message = "敏捷 +2！"
            
            self.player.discard.append(card)
            self.player.hand.remove(card)
            
            # 检查敌人死亡
            if self.enemy.hp <= 0:
                self.end_battle()

    def end_turn(self):
        # 敌人攻击
        damage = self.enemy.intent
        if self.player.block > 0:
            if damage >= self.player.block:
                damage -= self.player.block
                self.player.block = 0
            else:
                self.player.block -= damage
                damage = 0
        self.player.hp -= damage
        if damage > 0:
            self.message = f"{self.enemy.name} 造成 {damage} 点伤害！"
        
        # 检查玩家死亡
        if self.player.hp <= 0:
            self.state = "gameover"
            return
        
        # 新回合
        self.player.block = 0
        self.player.energy = self.player.max_energy
        self.discard_hand()
        self.draw_card()
        self.enemy.block = 0
        self.enemy.intent = self.enemy.damage + random.randint(-2, 2)

    def end_battle(self):
        self.state = "reward"
        self.player.gold += random.randint(20, 50)
        self.message = "战斗胜利！"

    def next_floor(self):
        self.current_node += 1
        if self.current_node >= len(self.map_nodes):
            self.state = "victory"
            return
        
        node_type = self.map_nodes[self.current_node]
        if node_type == "battle":
            self.start_battle()
        elif node_type == "elite":
            self.start_battle(is_elite=True)
        elif node_type == "boss":
            self.start_battle(is_boss=True)
        elif node_type == "shop":
            self.state = "shop"
        elif node_type == "rest":
            self.state = "rest"

# 创建游戏实例
game = GameState()

# 卡牌池
card_pool = [
    Card("打击", 1, 6, 0, "none", "造成6点伤害"),
    Card("防御", 1, 0, 5, "none", "获得5点护甲"),
    Card("重击", 2, 12, 0, "none", "造成12点伤害"),
    Card("铁壁", 2, 0, 12, "none", "获得12点护甲"),
    Card("多重打击", 1, 4, 0, "draw", "造成4点伤害，抽2张牌"),
    Card("狂暴", 0, 0, 0, "strength", "力量+2"),
    Card("灵活", 0, 0, 0, "dexterity", "敏捷+2"),
    Card("剑柄打击", 1, 8, 3, "none", "造成8伤害，获得3护甲"),
]

# 遗物池
relic_pool = [
    Relic("燃烧之血", "heal", "每场战斗结束恢复6HP"),
    Relic("红骷髅", "damage", "HP低于50%时伤害+3"),
    Relic("发条靴", "energy", "首回合额外+1能量"),
    Relic("开心花", "gold", "获得更多金币"),
]

# 主循环
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if game.state == "map":
                # 地图节点点击
                for i in range(len(game.map_nodes)):
                    node_x = 100 + i * 70
                    node_y = 300
                    if (node_x - 30 < mouse_pos[0] < node_x + 30 and 
                        node_y - 30 < mouse_pos[1] < node_y + 30):
                        if i == game.current_node + 1:
                            game.next_floor()
            
            elif game.state == "battle":
                # 卡牌点击
                card_width = 100
                card_height = 140
                start_x = (WIDTH - len(game.player.hand) * card_width) // 2
                
                for i, card in enumerate(game.player.hand):
                    card_x = start_x + i * card_width
                    card_y = HEIGHT - card_height - 20
                    if (card_x < mouse_pos[0] < card_x + card_width - 10 and 
                        card_y < mouse_pos[1] < card_y + card_height):
                        game.play_card(card)
                        break
                
                # 结束回合按钮
                if 650 < mouse_pos[0] < 750 and 400 < mouse_pos[1] < 450:
                    game.end_turn()
            
            elif game.state == "reward":
                # 奖励选择
                if 300 < mouse_pos[0] < 500 and 350 < mouse_pos[1] < 400:
                    game.state = "map"
                # 添加卡牌奖励
                if 200 < mouse_pos[0] < 300 and 250 < mouse_pos[1] < 350:
                    game.player.deck.append(random.choice(card_pool))
                    game.state = "map"
                if 350 < mouse_pos[0] < 450 and 250 < mouse_pos[1] < 350:
                    game.player.deck.append(random.choice(card_pool))
                    game.state = "map"
                if 500 < mouse_pos[0] < 600 and 250 < mouse_pos[1] < 350:
                    game.player.deck.append(random.choice(card_pool))
                    game.state = "map"
            
            elif game.state == "shop":
                # 商店购买
                shop_cards = random.sample(card_pool, 3)
                prices = [50, 75, 100]
                for i in range(3):
                    if 200 + i * 150 < mouse_pos[0] < 300 + i * 150 and 250 < mouse_pos[1] < 350:
                        if game.player.gold >= prices[i]:
                            game.player.gold -= prices[i]
                            game.player.deck.append(shop_cards[i])
                if 300 < mouse_pos[0] < 500 and 450 < mouse_pos[1] < 500:
                    game.state = "map"
            
            elif game.state == "rest":
                # 休息选择
                if 200 < mouse_pos[0] < 350 and 300 < mouse_pos[1] < 350:
                    game.player.hp = min(game.player.hp + 30, game.player.max_hp)
                    game.state = "map"
                if 450 < mouse_pos[0] < 600 and 300 < mouse_pos[1] < 350:
                    if len(game.player.deck) > 5:
                        game.player.deck.pop()
                    game.state = "map"
            
            elif game.state == "gameover" or game.state == "victory":
                if 300 < mouse_pos[0] < 500 and 400 < mouse_pos[1] < 450:
                    game = GameState()
    
    # 绘制
    if game.state == "map":
        # 绘制地图
        title = font_large.render("卡牌地牢 - 第{}层".format(game.current_node + 1), True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # 绘制节点
        for i, node_type in enumerate(game.map_nodes):
            node_x = 100 + i * 70
            node_y = 300
            color = GRAY
            if i == game.current_node:
                color = GREEN
            elif i == game.current_node + 1:
                color = GOLD
            elif i < game.current_node:
                color = DARK_GRAY
            
            pygame.draw.circle(screen, color, (node_x, node_y), 25)
            node_text = font_small.render(node_type[0].upper(), True, WHITE)
            screen.blit(node_text, (node_x - 8, node_y - 10))
        
        # 玩家状态
        hp_text = font_medium.render(f"HP: {game.player.hp}/{game.player.max_hp}", True, GREEN)
        screen.blit(hp_text, (50, 500))
        gold_text = font_medium.render(f"金币: {game.player.gold}", True, GOLD)
        screen.blit(gold_text, (50, 540))
        
        if game.current_node < len(game.map_nodes) - 1:
            instr = font_small.render("点击下一个节点前进", True, WHITE)
            screen.blit(instr, (WIDTH//2 - instr.get_width()//2, 500))
    
    elif game.state == "battle":
        # 绘制敌人
        enemy_x, enemy_y = WIDTH//2, 150
        pygame.draw.circle(screen, RED, (enemy_x, enemy_y), 60)
        enemy_name = font_medium.render(game.enemy.name, True, WHITE)
        screen.blit(enemy_name, (enemy_x - enemy_name.get_width()//2, enemy_y - 80))
        
        # 敌人血条
        enemy_hp_bar_width = 120
        pygame.draw.rect(screen, DARK_GRAY, (enemy_x - enemy_hp_bar_width//2, enemy_y + 70, enemy_hp_bar_width, 20))
        hp_ratio = max(0, game.enemy.hp / game.enemy.max_hp)
        pygame.draw.rect(screen, RED, (enemy_x - enemy_hp_bar_width//2, enemy_y + 70, enemy_hp_bar_width * hp_ratio, 20))
        enemy_hp_text = font_small.render(f"{game.enemy.hp}/{game.enemy.max_hp}", True, WHITE)
        screen.blit(enemy_hp_text, (enemy_x - enemy_hp_text.get_width()//2, enemy_y + 72))
        
        # 敌人意图
        intent_text = font_medium.render(f"意图: {game.enemy.intent} 伤害", True, RED)
        screen.blit(intent_text, (enemy_x - intent_text.get_width()//2, enemy_y + 100))
        
        if game.enemy.block > 0:
            block_text = font_small.render(f"护甲: {game.enemy.block}", True, BLUE)
            screen.blit(block_text, (enemy_x + 80, enemy_y - 20))
        
        # 绘制玩家
        player_x, player_y = 100, 400
        pygame.draw.circle(screen, BLUE, (player_x, player_y), 40)
        
        # 玩家血条
        player_hp_bar_width = 100
        pygame.draw.rect(screen, DARK_GRAY, (player_x - player_hp_bar_width//2, player_y + 50, player_hp_bar_width, 15))
        player_hp_ratio = max(0, game.player.hp / game.player.max_hp)
        pygame.draw.rect(screen, GREEN, (player_x - player_hp_bar_width//2, player_y + 50, player_hp_bar_width * player_hp_ratio, 15))
        player_hp_text = font_small.render(f"{game.player.hp}/{game.player.max_hp}", True, WHITE)
        screen.blit(player_hp_text, (player_x - player_hp_text.get_width()//2, player_y + 52))
        
        if game.player.block > 0:
            player_block_text = font_small.render(f"护甲: {game.player.block}", True, BLUE)
            screen.blit(player_block_text, (player_x - 50, player_y + 75))
        
        energy_text = font_medium.render(f"能量: {game.player.energy}/{game.player.max_energy}", True, GOLD)
        screen.blit(energy_text, (player_x - 50, player_y - 70))
        
        # 绘制手牌
        card_width = 100
        card_height = 140
        start_x = (WIDTH - len(game.player.hand) * card_width) // 2
        
        for i, card in enumerate(game.player.hand):
            card_x = start_x + i * card_width
            card_y = HEIGHT - card_height - 20
            
            # 卡牌背景
            color = BLUE if card.cost <= game.player.energy else GRAY
            pygame.draw.rect(screen, color, (card_x, card_y, card_width - 10, card_height))
            pygame.draw.rect(screen, WHITE, (card_x, card_y, card_width - 10, card_height), 2)
            
            # 卡牌信息
            cost_text = font_large.render(str(card.cost), True, GOLD)
            screen.blit(cost_text, (card_x + 5, card_y + 5))
            
            name_text = font_small.render(card.name, True, WHITE)
            screen.blit(name_text, (card_x + 5, card_y + 40))
            
            if card.damage > 0:
                dmg_text = font_small.render(f"伤害: {card.damage}", True, RED)
                screen.blit(dmg_text, (card_x + 5, card_y + 70))
            
            if card.block > 0:
                blk_text = font_small.render(f"护甲: {card.block}", True, BLUE)
                screen.blit(blk_text, (card_x + 5, card_y + 90))
        
        # 结束回合按钮
        pygame.draw.rect(screen, GREEN, (650, 400, 100, 50))
        end_turn_text = font_medium.render("结束", True, WHITE)
        screen.blit(end_turn_text, (670, 410))
        
        # 消息
        msg_text = font_small.render(game.message, True, WHITE)
        screen.blit(msg_text, (WIDTH//2 - msg_text.get_width()//2, 50))
    
    elif game.state == "reward":
        title = font_large.render("战斗胜利！", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        gold_text = font_medium.render(f"获得金币: {game.player.gold}", True, GOLD)
        screen.blit(gold_text, (WIDTH//2 - gold_text.get_width()//2, 100))
        
        instr = font_medium.render("选择一张卡牌加入卡组", True, WHITE)
        screen.blit(instr, (WIDTH//2 - instr.get_width()//2, 180))
        
        reward_cards = random.sample(card_pool, 3)
        for i in range(3):
            pygame.draw.rect(screen, BLUE, (200 + i * 150, 250, 100, 100))
            card_name = font_small.render(reward_cards[i].name, True, WHITE)
            screen.blit(card_name, (210 + i * 150, 290))
        
        pygame.draw.rect(screen, GREEN, (300, 350, 200, 50))
        skip_text = font_medium.render("跳过", True, WHITE)
        screen.blit(skip_text, (370, 360))
    
    elif game.state == "shop":
        title = font_large.render("商店", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        gold_text = font_medium.render(f"金币: {game.player.gold}", True, GOLD)
        screen.blit(gold_text, (WIDTH//2 - gold_text.get_width()//2, 100))
        
        shop_cards = random.sample(card_pool, 3)
        prices = [50, 75, 100]
        for i in range(3):
            pygame.draw.rect(screen, PURPLE, (200 + i * 150, 250, 100, 100))
            card_name = font_small.render(shop_cards[i].name, True, WHITE)
            screen.blit(card_name, (210 + i * 150, 280))
            price_text = font_small.render(f"{prices[i]}G", True, GOLD)
            screen.blit(price_text, (230 + i * 150, 310))
        
        pygame.draw.rect(screen, GREEN, (300, 450, 200, 50))
        leave_text = font_medium.render("离开商店", True, WHITE)
        screen.blit(leave_text, (350, 460))
    
    elif game.state == "rest":
        title = font_large.render("休息点", True, GREEN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        pygame.draw.rect(screen, GREEN, (200, 300, 150, 50))
        heal_text = font_medium.render("休息 (+30HP)", True, WHITE)
        screen.blit(heal_text, (215, 310))
        
        pygame.draw.rect(screen, RED, (450, 300, 150, 50))
        remove_text = font_medium.render("移除卡牌", True, WHITE)
        screen.blit(remove_text, (460, 310))
    
    elif game.state == "gameover":
        title = font_large.render("游戏结束", True, RED)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        
        floor_text = font_medium.render(f"到达第 {game.current_node + 1} 层", True, WHITE)
        screen.blit(floor_text, (WIDTH//2 - floor_text.get_width()//2, 280))
        
        pygame.draw.rect(screen, BLUE, (300, 400, 200, 50))
        restart_text = font_medium.render("重新开始", True, WHITE)
        screen.blit(restart_text, (350, 410))
    
    elif game.state == "victory":
        title = font_large.render("胜利！", True, GOLD)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        
        victory_text = font_medium.render("你击败了地牢！", True, WHITE)
        screen.blit(victory_text, (WIDTH//2 - victory_text.get_width()//2, 280))
        
        pygame.draw.rect(screen, BLUE, (300, 400, 200, 50))
        restart_text = font_medium.render("再来一局", True, WHITE)
        screen.blit(restart_text, (350, 410))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
