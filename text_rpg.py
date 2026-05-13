import pygame
import sys
import random

# 初始化pygame
pygame.init()

# 游戏常量
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("文字RPG冒险")
FONT = pygame.font.Font(None, 24)
TITLE_FONT = pygame.font.Font(None, 36)

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (50, 50, 50)
GRAY = (100, 100, 100)
LIGHT_GRAY = (180, 180, 180)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
YELLOW = (200, 200, 50)

# 物品定义
ITEMS = {
    "health_potion": {"name": "生命药水", "type": "consumable", "effect": {"hp": 30}, "desc": "恢复30点生命"},
    "sword": {"name": "铁剑", "type": "weapon", "damage": 15, "desc": "+15攻击力"},
    "shield": {"name": "木盾", "type": "armor", "defense": 10, "desc": "+10防御力"},
    "key": {"name": "钥匙", "type": "key", "desc": "打开锁着的门"},
    "gold": {"name": "金币", "type": "currency", "desc": "闪闪发光的金币"}
}

# 敌人定义
ENEMIES = {
    "slime": {"name": "史莱姆", "hp": 30, "max_hp": 30, "attack": 8, "gold": 10, "exp": 15},
    "goblin": {"name": "哥布林", "hp": 50, "max_hp": 50, "attack": 12, "gold": 20, "exp": 30},
    "orc": {"name": "兽人", "hp": 80, "max_hp": 80, "attack": 18, "gold": 35, "exp": 50},
    "dragon": {"name": "幼龙", "hp": 150, "max_hp": 150, "attack": 25, "gold": 100, "exp": 100}
}

# 房间定义
ROOMS = {
    "start": {
        "name": "起始村庄",
        "desc": "你站在一个宁静的村庄广场上，村民们忙碌着。东边是森林，北边是城堡。",
        "exits": {"east": "forest", "north": "castle_entrance"},
        "items": [],
        "enemies": [],
        "npc": {"name": "村长", "dialog": "欢迎来到勇者村！东边的森林最近出现了怪物，你能帮我们清除吗？"}
    },
    "forest": {
        "name": "神秘森林",
        "desc": "茂密的树木遮天蔽日，空气中弥漫着潮湿的气息。西边是村庄，东边是深处。",
        "exits": {"west": "start", "east": "deep_forest"},
        "items": ["health_potion"],
        "enemies": ["slime", "slime"],
        "npc": None
    },
    "deep_forest": {
        "name": "森林深处",
        "desc": "这里更加阴暗，一只哥布林正在巡逻！西边是原路返回。",
        "exits": {"west": "forest"},
        "items": ["sword", "gold"],
        "enemies": ["goblin"],
        "npc": None
    },
    "castle_entrance": {
        "name": "城堡入口",
        "desc": "宏伟的城堡矗立在你面前，大门紧闭。南边是村庄，东边是地牢入口。",
        "exits": {"south": "start", "east": "dungeon"},
        "items": ["shield"],
        "enemies": [],
        "npc": {"name": "守卫", "dialog": "城堡被兽人占领了！地牢里有通往内部的钥匙。"}
    },
    "dungeon": {
        "name": "黑暗地牢",
        "desc": "阴冷潮湿的地牢，墙上挂满了铁链。西边是城堡入口，北边有一扇锁着的门。",
        "exits": {"west": "castle_entrance", "north": "treasure_room"},
        "locked_exits": ["north"],
        "items": ["key"],
        "enemies": ["orc"],
        "npc": None
    },
    "treasure_room": {
        "name": "宝藏室",
        "desc": "金光闪闪！宝藏室里堆满了财宝，但一只幼龙正在守护！",
        "exits": {"south": "dungeon"},
        "items": ["gold", "gold", "gold", "health_potion"],
        "enemies": ["dragon"],
        "npc": None
    }
}

class Player:
    def __init__(self):
        self.name = "勇者"
        self.hp = 100
        self.max_hp = 100
        self.attack = 10
        self.defense = 5
        self.level = 1
        self.exp = 0
        self.exp_to_next = 50
        self.gold = 0
        self.inventory = ["health_potion"]
        self.current_room = "start"
        self.weapon = None
        self.armor = None

    def get_total_attack(self):
        total = self.attack
        if self.weapon:
            total += ITEMS[self.weapon]["damage"]
        return total

    def get_total_defense(self):
        total = self.defense
        if self.armor:
            total += ITEMS[self.armor]["defense"]
        return total

    def gain_exp(self, amount):
        self.exp += amount
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            self.max_hp += 20
            self.hp = self.max_hp
            self.attack += 5
            self.defense += 3
            self.exp_to_next = int(self.exp_to_next * 1.5)
            return True
        return False

class Game:
    def __init__(self):
        self.player = Player()
        self.game_state = "explore"  # explore, battle, inventory, dialog
        self.messages = []
        self.choices = []
        self.selected_choice = 0
        self.current_enemy = None
        self.room_enemies = []
        self.init_room()
        self.add_message("欢迎来到文字RPG冒险！")
        self.add_message("使用方向键或点击选项来行动。")

    def init_room(self):
        room = ROOMS[self.player.current_room]
        self.room_enemies = room["enemies"].copy()

    def add_message(self, msg):
        self.messages.append(msg)
        if len(self.messages) > 10:
            self.messages.pop(0)

    def update_choices(self):
        room = ROOMS[self.player.current_room]
        self.choices = []
        
        if self.game_state == "explore":
            for direction, dest in room["exits"].items():
                if "locked_exits" in room and direction in room["locked_exits"]:
                    if "key" in self.player.inventory:
                        self.choices.append(f"使用钥匙打开{direction}边的门")
                    else:
                        self.choices.append(f"{direction}边的门（需要钥匙）")
                else:
                    self.choices.append(f"向{direction}走")
            
            if room["items"]:
                self.choices.append("搜索物品")
            
            if self.room_enemies:
                self.choices.append(f"战斗！（{len(self.room_enemies)}个敌人）")
            
            if room["npc"]:
                self.choices.append(f"与{room['npc']['name']}对话")
            
            self.choices.append("查看背包")
            self.choices.append("状态")
        
        elif self.game_state == "battle":
            self.choices = ["攻击", "使用物品", "逃跑"]
        
        elif self.game_state == "inventory":
            self.choices = ["返回"]
            if self.player.inventory:
                for item in self.player.inventory:
                    self.choices.append(f"使用/装备 {ITEMS[item]['name']}")
        
        elif self.game_state == "dialog":
            self.choices = ["结束对话"]

    def handle_choice(self, choice_idx):
        room = ROOMS[self.player.current_room]
        
        if self.game_state == "explore":
            choice_text = self.choices[choice_idx]
            
            for direction, dest in room["exits"].items():
                if choice_text.startswith(f"向{direction}走"):
                    self.player.current_room = dest
                    self.init_room()
                    self.add_message(f"你来到了{ROOMS[dest]['name']}")
                    return
                elif choice_text.startswith(f"使用钥匙打开{direction}边的门"):
                    self.player.inventory.remove("key")
                    if "locked_exits" in room:
                        room["locked_exits"].remove(direction)
                    self.player.current_room = dest
                    self.init_room()
                    self.add_message("门开了！")
                    return
            
            if choice_text == "搜索物品" and room["items"]:
                for item in room["items"]:
                    self.player.inventory.append(item)
                    self.add_message(f"获得了{ITEMS[item]['name']}！")
                room["items"] = []
            
            elif choice_text.startswith("战斗！"):
                if self.room_enemies:
                    enemy_type = self.room_enemies.pop(0)
                    self.current_enemy = ENEMIES[enemy_type].copy()
                    self.game_state = "battle"
                    self.add_message(f"遭遇了{self.current_enemy['name']}！")
            
            elif choice_text.startswith("与"):
                self.game_state = "dialog"
                self.add_message(f"{room['npc']['name']}: {room['npc']['dialog']}")
            
            elif choice_text == "查看背包":
                self.game_state = "inventory"
            
            elif choice_text == "状态":
                self.add_message(f"等级: {self.player.level} HP: {self.player.hp}/{self.player.max_hp}")
                self.add_message(f"攻击: {self.player.get_total_attack()} 防御: {self.player.get_total_defense()}")
                self.add_message(f"经验: {self.player.exp}/{self.player.exp_to_next} 金币: {self.player.gold}")
        
        elif self.game_state == "battle":
            if choice_idx == 0:
                player_dmg = max(1, self.player.get_total_attack() - random.randint(0, 5))
                self.current_enemy["hp"] -= player_dmg
                self.add_message(f"你造成了{player_dmg}点伤害！")
                
                if self.current_enemy["hp"] <= 0:
                    self.add_message(f"打败了{self.current_enemy['name']}！")
                    self.player.gold += self.current_enemy["gold"]
                    if self.player.gain_exp(self.current_enemy["exp"]):
                        self.add_message(f"升级了！现在是{self.player.level}级！")
                    self.current_enemy = None
                    self.game_state = "explore"
                else:
                    enemy_dmg = max(1, self.current_enemy["attack"] - self.player.get_total_defense() // 2)
                    self.player.hp -= enemy_dmg
                    self.add_message(f"{self.current_enemy['name']}造成了{enemy_dmg}点伤害！")
                    if self.player.hp <= 0:
                        self.add_message("你被打败了...游戏结束")
                        self.game_state = "gameover"
            
            elif choice_idx == 1:
                self.game_state = "inventory"
            
            elif choice_idx == 2:
                if random.random() < 0.5:
                    self.add_message("成功逃跑！")
                    self.game_state = "explore"
                    self.current_enemy = None
                else:
                    self.add_message("逃跑失败！")
                    enemy_dmg = max(1, self.current_enemy["attack"] - self.player.get_total_defense() // 2)
                    self.player.hp -= enemy_dmg
                    self.add_message(f"{self.current_enemy['name']}造成了{enemy_dmg}点伤害！")
        
        elif self.game_state == "inventory":
            if choice_idx == 0:
                self.game_state = "battle" if self.current_enemy else "explore"
            else:
                item_idx = choice_idx - 1
                if item_idx < len(self.player.inventory):
                    item = self.player.inventory[item_idx]
                    item_data = ITEMS[item]
                    if item_data["type"] == "consumable":
                        if "hp" in item_data["effect"]:
                            self.player.hp = min(self.player.max_hp, self.player.hp + item_data["effect"]["hp"])
                            self.add_message(f"使用了{item_data['name']}，恢复了生命！")
                        self.player.inventory.pop(item_idx)
                    elif item_data["type"] == "weapon":
                        self.player.weapon = item
                        self.add_message(f"装备了{item_data['name']}！")
                    elif item_data["type"] == "armor":
                        self.player.armor = item
                        self.add_message(f"装备了{item_data['name']}！")
        
        elif self.game_state == "dialog":
            self.game_state = "explore"

    def draw(self):
        SCREEN.fill(DARK_GRAY)
        
        room = ROOMS[self.player.current_room]
        
        room_name = TITLE_FONT.render(room["name"], True, YELLOW)
        SCREEN.blit(room_name, (20, 20))
        
        y_offset = 70
        room_desc_lines = self.wrap_text(room["desc"], 760)
        for line in room_desc_lines:
            desc_text = FONT.render(line, True, WHITE)
            SCREEN.blit(desc_text, (20, y_offset))
            y_offset += 30
        
        if self.game_state == "battle" and self.current_enemy:
            enemy_info = f"{self.current_enemy['name']} HP: {self.current_enemy['hp']}/{self.current_enemy['max_hp']}"
            enemy_text = FONT.render(enemy_info, True, RED)
            SCREEN.blit(enemy_text, (20, y_offset))
            y_offset += 30
        
        y_offset = 250
        for msg in self.messages:
            msg_text = FONT.render(msg, True, LIGHT_GRAY)
            SCREEN.blit(msg_text, (20, y_offset))
            y_offset += 25
        
        self.update_choices()
        y_offset = 420
        for i, choice in enumerate(self.choices):
            color = GREEN if i == self.selected_choice else WHITE
            choice_text = FONT.render(f"> {choice}" if i == self.selected_choice else f"  {choice}", True, color)
            SCREEN.blit(choice_text, (20, y_offset))
            y_offset += 30
        
        status_text = FONT.render(f"HP: {self.player.hp}/{self.player.max_hp} | 等级: {self.player.level} | 金币: {self.player.gold}", True, BLUE)
        SCREEN.blit(status_text, (20, HEIGHT - 40))
        
        pygame.display.flip()

    def wrap_text(self, text, max_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if FONT.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.QUIT:
                        running = False
                    elif event.key == pygame.K_UP:
                        self.selected_choice = (self.selected_choice - 1) % len(self.choices) if self.choices else 0
                    elif event.key == pygame.K_DOWN:
                        self.selected_choice = (self.selected_choice + 1) % len(self.choices) if self.choices else 0
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if self.choices and self.game_state != "gameover":
                            self.handle_choice(self.selected_choice)
                            self.selected_choice = 0
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        y_offset = 420
                        for i, _ in enumerate(self.choices):
                            if 420 <= my <= 420 + 30 * len(self.choices):
                                choice_idx = (my - 420) // 30
                                if 0 <= choice_idx < len(self.choices):
                                    self.handle_choice(choice_idx)
                                    self.selected_choice = 0
                                    break
            
            self.draw()
            clock.tick(30)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
