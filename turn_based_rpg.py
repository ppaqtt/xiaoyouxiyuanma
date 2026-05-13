import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
GRID_SIZE = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("回合制RPG冒险")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)
big_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 22)

class Player:
    def __init__(self):
        self.name = "冒险者"
        self.level = 1
        self.exp = 0
        self.exp_to_level = 100
        self.hp = 100
        self.max_hp = 100
        self.mp = 50
        self.max_mp = 50
        self.attack = 10
        self.defense = 5
        self.gold = 0
        self.inventory = []
        self.quests = []
        self.skills = [{"name": "普通攻击", "damage": 10, "mp_cost": 0}]
    
    def level_up(self):
        if self.exp >= self.exp_to_level:
            self.level += 1
            self.exp -= self.exp_to_level
            self.exp_to_level = int(self.exp_to_level * 1.5)
            self.max_hp += 20
            self.max_mp += 10
            self.attack += 5
            self.defense += 2
            self.hp = self.max_hp
            self.mp = self.max_mp
            return True
        return False

class Enemy:
    def __init__(self, name, hp, attack, exp_reward, gold_reward, boss=False):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
        self.boss = boss

class Quest:
    def __init__(self, name, desc, target, reward_exp, reward_gold):
        self.name = name
        self.desc = desc
        self.target = target
        self.progress = 0
        self.completed = False
        self.reward_exp = reward_exp
        self.reward_gold = reward_gold

class RPGGame:
    def __init__(self):
        self.state = "menu"
        self.player = Player()
        self.current_enemy = None
        self.battle_log = []
        self.current_area = 0
        self.areas = [
            {"name": "新手森林", "enemies": ["史莱姆", "野兔", "野猪"], "min_lv": 1},
            {"name": "幽暗洞穴", "enemies": ["蝙蝠", "骷髅", "蜘蛛"], "min_lv": 3},
            {"name": "燃烧山脉", "enemies": ["火元素", "熔岩怪", "火龙"], "min_lv": 5},
        ]
        self.quests = [
            Quest("初学者", "击败5只史莱姆", "史莱姆", 50, 100),
            Quest("洞穴探险", "击败3只骷髅", "骷髅", 100, 200),
            Quest("屠龙勇士", "击败火龙", "火龙", 500, 1000),
        ]
        self.shop_items = [
            {"name": "生命药水", "price": 50, "effect": "恢复50HP"},
            {"name": "魔法药水", "price": 30, "effect": "恢复30MP"},
            {"name": "铁剑", "price": 200, "effect": "攻击+5"},
            {"name": "皮甲", "price": 150, "effect": "防御+3"},
        ]

def turn_based_rpg():
    game = RPGGame()
    game.state = "title"
    
    while True:
        screen.fill(BLACK)
        
        if game.state == "title":
            title = big_font.render("回合制RPG冒险", True, YELLOW)
            screen.blit(title, (WIDTH // 2 - 150, 100))
            
            start = font.render("按 ENTER 开始冒险", True, GREEN)
            screen.blit(start, (WIDTH // 2 - 100, 300))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game.state = "explore"
        
        elif game.state == "explore":
            player = game.player
            
            info = font.render(f"{player.name} Lv.{player.level}", True, YELLOW)
            screen.blit(info, (10, 10))
            
            stats = font.render(f"HP: {player.hp}/{player.max_hp} MP: {player.mp}/{player.max_mp}", True, GREEN)
            screen.blit(stats, (10, 50))
            
            exp_text = font.render(f"经验: {player.exp}/{player.exp_to_level}", True, BLUE)
            screen.blit(exp_text, (10, 90))
            
            gold_text = font.render(f"金币: {player.gold}", True, YELLOW)
            screen.blit(gold_text, (10, 130))
            
            area_text = font.render(f"当前位置: {game.areas[game.current_area]['name']}", True, WHITE)
            screen.blit(area_text, (10, 170))
            
            options = ["1. 探索战斗", "2. 商店", "3. 任务", "4. 状态", "5. 存档"]
            for i, opt in enumerate(options):
                text = font.render(opt, True, WHITE)
                screen.blit(text, (WIDTH // 2 - 50, 220 + i * 40))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        enemies = game.areas[game.current_area]["enemies"]
                        enemy_name = random.choice(enemies)
                        enemy = Enemy(enemy_name, 20 + game.current_area * 10, 
                                    5 + game.current_area * 3, 20 + game.current_area * 10,
                                    10 + game.current_area * 5, boss=(enemy_name in ["火龙"]))
                        game.current_enemy = enemy
                        game.state = "battle"
                    elif event.key == pygame.K_2:
                        game.state = "shop"
                    elif event.key == pygame.K_3:
                        game.state = "quests"
                    elif event.key == pygame.K_4:
                        game.state = "status"
        
        elif game.state == "battle":
            player = game.player
            enemy = game.current_enemy
            
            title = big_font.render(f"战斗: {enemy.name}", True, RED)
            screen.blit(title, (WIDTH // 2 - 100, 50))
            
            ehp = font.render(f"敌人HP: {enemy.hp}/{enemy.max_hp}", True, RED)
            screen.blit(ehp, (WIDTH // 2 - 80, 120))
            
            php = font.render(f"你的HP: {player.hp}/{player.max_hp}", True, GREEN)
            screen.blit(php, (WIDTH // 2 - 80, 160))
            
            for i, log in enumerate(game.battle_log[-3:]):
                log_text = small_font.render(log, True, WHITE)
                screen.blit(log_text, (WIDTH // 2 - 150, 200 + i * 25))
            
            options = ["1. 攻击", "2. 技能", "3. 道具", "4. 逃跑"]
            for i, opt in enumerate(options):
                text = font.render(opt, True, WHITE)
                screen.blit(text, (WIDTH // 2 - 50, 400 + i * 35))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        damage = max(1, player.attack - enemy.max_hp // 10)
                        enemy.hp -= damage
                        game.battle_log.append(f"你造成了 {damage} 点伤害!")
                    elif event.key == pygame.K_4:
                        if random.random() < 0.5:
                            game.state = "explore"
                            game.battle_log = []
                            continue
                        else:
                            game.battle_log.append("逃跑失败!")
                    
                    player_damage = max(1, enemy.attack - player.defense)
                    player.hp -= player_damage
                    game.battle_log.append(f"{enemy.name}造成了 {player_damage} 点伤害!")
                    
                    if enemy.hp <= 0:
                        game.battle_log.append(f"击败了{enemy.name}!")
                        player.exp += enemy.exp_reward
                        player.gold += enemy.gold_reward
                        player.level_up()
                        game.state = "explore"
                        game.battle_log = []
                    elif player.hp <= 0:
                        game.battle_log.append("你被击败了!")
                        player.hp = player.max_hp // 2
                        player.gold = max(0, player.gold - player.gold // 2)
                        game.state = "explore"
                        game.battle_log = []
        
        elif game.state == "shop":
            title = big_font.render("商店", True, YELLOW)
            screen.blit(title, (WIDTH // 2 - 50, 50))
            
            gold = font.render(f"金币: {game.player.gold}", True, YELLOW)
            screen.blit(gold, (10, 10))
            
            for i, item in enumerate(game.shop_items):
                text = f"{i+1}. {item['name']} - {item['price']}金币 ({item['effect']})"
                item_text = small_font.render(text, True, WHITE)
                screen.blit(item_text, (50, 120 + i * 35))
            
            back = font.render("按 ESC 返回", True, GRAY)
            screen.blit(back, (50, HEIGHT - 50))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game.state = "explore"
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        idx = event.key - 49
                        if idx < len(game.shop_items):
                            item = game.shop_items[idx]
                            if game.player.gold >= item["price"]:
                                game.player.gold -= item["price"]
                                if "HP" in item["effect"]:
                                    game.player.hp = min(game.player.max_hp, game.player.hp + 50)
                                elif "MP" in item["effect"]:
                                    game.player.mp = min(game.player.max_mp, game.player.mp + 30)
                                elif "攻击" in item["effect"]:
                                    game.player.attack += 5
                                elif "防御" in item["effect"]:
                                    game.player.defense += 3
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    turn_based_rpg()
