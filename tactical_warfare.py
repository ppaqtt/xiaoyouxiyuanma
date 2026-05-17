#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回合制战棋/战术游戏
使用pygame制作
操作说明：
- 鼠标左键点击选中单位
- 点击目标位置移动或攻击
- 空格键结束回合
- 支持玩家vs简单AI
"""

import pygame
import os
import sys
import random

# 初始化pygame
pygame.init()



# 尝试使用中文字体
def get_chinese_font(size):
    """获取支持中文的字体"""
    font_names = [
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux
        "/System/Library/Fonts/PingFang.ttc",  # macOS
    ]
    for font_name in font_names:
        if os.path.exists(font_name):
            try:
                return pygame.font.Font(font_name, size)
            except:
                continue
    return get_chinese_font(size)

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (76, 175, 80)
GRASS = (139, 195, 74)
FOREST = (46, 125, 50)
WATER = (30, 136, 229)
MOUNTAIN = (121, 85, 72)
PLAYER_COLOR = (33, 150, 243)
ENEMY_COLOR = (244, 67, 54)
SELECTED = (255, 235, 59)
MOVE_RANGE = (144, 202, 249, 128)
ATTACK_RANGE = (239, 83, 80, 128)
GRAY = (158, 158, 158)
DARK_GRAY = (96, 96, 96)

# 窗口大小
WIDTH, HEIGHT = 960, 760
ROWS, COLS = 12, 16
CELL_SIZE = 60

# 地形类型
TERRAIN = {
    0: ('平地', GRASS, 0),    # 名称, 颜色, 移动消耗
    1: ('森林', FOREST, 2),
    2: ('水域', WATER, 99),
    3: ('山地', MOUNTAIN, 3)
}

# 单位类型
UNIT_TYPES = {
    '步兵': {'hp': 100, 'attack': 20, 'defense': 10, 'move': 3, 'range': 1, 'symbol': '⚔'},
    '射手': {'hp': 70, 'attack': 25, 'defense': 5, 'move': 2, 'range': 3, 'symbol': '🏹'},
    '骑兵': {'hp': 120, 'attack': 30, 'defense': 15, 'move': 5, 'range': 1, 'symbol': '🐴'},
    '法师': {'hp': 60, 'attack': 40, 'defense': 5, 'move': 2, 'range': 4, 'symbol': '✨'}
}

class Unit:
    def __init__(self, unit_type, team, row, col):
        self.type = unit_type
        self.team = team
        self.row = row
        self.col = col
        self.stats = UNIT_TYPES[unit_type].copy()
        self.hp = self.stats['hp']
        self.max_hp = self.stats['hp']
        self.moved = False
        self.attacked = False

class TacticalWarfare:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('回合制战棋')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('simhei', 24)
        self.large_font = pygame.font.SysFont('simhei', 48)
        self.small_font = pygame.font.SysFont('simhei', 18)
        
        self.terrain = self.generate_terrain()
        self.units = []
        self.selected_unit = None
        self.current_team = 'player'
        self.turn = 1
        self.game_over = False
        self.winner = None
        self.move_range = []
        self.attack_range = []
        
        self.init_units()

    def generate_terrain(self):
        terrain = []
        for row in range(ROWS):
            row_data = []
            for col in range(COLS):
                rand = random.random()
                if rand < 0.6:
                    row_data.append(0)
                elif rand < 0.75:
                    row_data.append(1)
                elif rand < 0.85:
                    row_data.append(2)
                else:
                    row_data.append(3)
            terrain.append(row_data)
        return terrain

    def init_units(self):
        # 玩家单位
        self.units.append(Unit('步兵', 'player', 10, 3))
        self.units.append(Unit('射手', 'player', 10, 6))
        self.units.append(Unit('骑兵', 'player', 10, 9))
        self.units.append(Unit('法师', 'player', 10, 12))
        
        # 敌方单位
        self.units.append(Unit('步兵', 'enemy', 1, 3))
        self.units.append(Unit('射手', 'enemy', 1, 6))
        self.units.append(Unit('骑兵', 'enemy', 1, 9))
        self.units.append(Unit('法师', 'enemy', 1, 12))

    def get_unit_at(self, row, col):
        for unit in self.units:
            if unit.row == row and unit.col == col:
                return unit
        return None

    def draw_terrain(self):
        for row in range(ROWS):
            for col in range(COLS):
                terrain_type = self.terrain[row][col]
                name, color, cost = TERRAIN[terrain_type]
                pygame.draw.rect(self.screen, color, 
                                (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, DARK_GRAY, 
                                (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    def draw_ranges(self):
        for row, col in self.move_range:
            pygame.draw.rect(self.screen, (144, 202, 249), 
                            (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        for row, col in self.attack_range:
            pygame.draw.rect(self.screen, (239, 83, 80), 
                            (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def draw_units(self):
        for unit in self.units:
            x = unit.col * CELL_SIZE
            y = unit.row * CELL_SIZE
            
            color = PLAYER_COLOR if unit.team == 'player' else ENEMY_COLOR
            pygame.draw.rect(self.screen, color, (x + 5, y + 5, CELL_SIZE - 10, CELL_SIZE - 10), 2)
            
            text = self.font.render(unit.stats['symbol'], True, WHITE)
            self.screen.blit(text, (x + CELL_SIZE//2 - text.get_width()//2, 
                                   y + CELL_SIZE//2 - text.get_height()//2 - 10))
            
            # 血条
            hp_ratio = unit.hp / unit.max_hp
            pygame.draw.rect(self.screen, BLACK, (x + 5, y + CELL_SIZE - 15, CELL_SIZE - 10, 10))
            pygame.draw.rect(self.screen, (244, 67, 54), 
                            (x + 5, y + CELL_SIZE - 15, (CELL_SIZE - 10) * hp_ratio, 10))
            
            # 状态标记
            if unit.moved and unit.attacked:
                pygame.draw.circle(self.screen, GRAY, 
                                 (x + CELL_SIZE - 10, y + 10), 5)

    def draw_selected(self):
        if self.selected_unit:
            unit = self.selected_unit
            x = unit.col * CELL_SIZE
            y = unit.row * CELL_SIZE
            pygame.draw.rect(self.screen, SELECTED, 
                            (x, y, CELL_SIZE, CELL_SIZE), 4)

    def draw_ui(self):
        ui_y = ROWS * CELL_SIZE
        pygame.draw.rect(self.screen, DARK_GRAY, (0, ui_y, WIDTH, HEIGHT - ui_y))
        
        info_text = f"回合 {self.turn} | {'玩家' if self.current_team == 'player' else 'AI'} 回合"
        text = self.font.render(info_text, True, WHITE)
        self.screen.blit(text, (20, ui_y + 15))
        
        if self.selected_unit:
            unit = self.selected_unit
            unit_info = f"{unit.type} | HP:{unit.hp}/{unit.max_hp} | 攻击:{unit.stats['attack']} | 防御:{unit.stats['defense']}"
            text = self.small_font.render(unit_info, True, WHITE)
            self.screen.blit(text, (300, ui_y + 20))
        
        if self.game_over:
            winner_text = f"游戏结束! {'玩家' if self.winner == 'player' else 'AI'}获胜!"
            text = self.large_font.render(winner_text, True, SELECTED)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, ui_y + 15))

    def get_move_range(self, unit):
        if unit.moved:
            return []
        max_move = unit.stats['move']
        visited = set()
        queue = [(unit.row, unit.col, 0)]
        visited.add((unit.row, unit.col))
        moves = []
        
        while queue:
            r, c, dist = queue.pop(0)
            moves.append((r, c))
            if dist < max_move:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS and (nr, nc) not in visited:
                        terrain_type = self.terrain[nr][nc]
                        cost = TERRAIN[terrain_type][2]
                        if dist + cost <= max_move and not self.get_unit_at(nr, nc):
                            visited.add((nr, nc))
                            queue.append((nr, nc, dist + cost))
        return moves

    def get_attack_range(self, unit):
        if unit.attacked:
            return []
        attack_range = unit.stats['range']
        attacks = []
        for dr in range(-attack_range, attack_range + 1):
            for dc in range(-attack_range, attack_range + 1):
                if abs(dr) + abs(dc) <= attack_range and (dr != 0 or dc != 0):
                    nr, nc = unit.row + dr, unit.col + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS:
                        target = self.get_unit_at(nr, nc)
                        if target and target.team != unit.team:
                            attacks.append((nr, nc))
        return attacks

    def calculate_damage(self, attacker, defender):
        base_damage = attacker.stats['attack']
        defense = defender.stats['defense']
        damage = max(1, base_damage - defense // 2 + random.randint(-5, 5))
        return damage

    def attack(self, attacker, defender):
        damage = self.calculate_damage(attacker, defender)
        defender.hp -= damage
        attacker.attacked = True
        
        if defender.hp <= 0:
            self.units.remove(defender)
            self.check_game_over()

    def check_game_over(self):
        player_units = [u for u in self.units if u.team == 'player']
        enemy_units = [u for u in self.units if u.team == 'enemy']
        
        if not player_units:
            self.game_over = True
            self.winner = 'enemy'
        elif not enemy_units:
            self.game_over = True
            self.winner = 'player'

    def move_unit(self, unit, row, col):
        unit.row = row
        unit.col = col
        unit.moved = True

    def end_turn(self):
        for unit in self.units:
            unit.moved = False
            unit.attacked = False
        
        self.current_team = 'enemy' if self.current_team == 'player' else 'player'
        if self.current_team == 'player':
            self.turn += 1
        self.selected_unit = None
        self.move_range = []
        self.attack_range = []
        
        if self.current_team == 'enemy' and not self.game_over:
            self.ai_turn()

    def ai_turn(self):
        enemy_units = [u for u in self.units if u.team == 'enemy']
        player_units = [u for u in self.units if u.team == 'player']
        
        for unit in enemy_units:
            if not player_units:
                break
                
            # 移动
            moves = self.get_move_range(unit)
            if moves:
                best_move = moves[0]
                min_dist = float('inf')
                for mr, mc in moves:
                    for pu in player_units:
                        dist = abs(mr - pu.row) + abs(mc - pu.col)
                        if dist < min_dist:
                            min_dist = dist
                            best_move = (mr, mc)
                if best_move != (unit.row, unit.col):
                    self.move_unit(unit, best_move[0], best_move[1])
            
            # 攻击
            attacks = self.get_attack_range(unit)
            if attacks:
                ar, ac = random.choice(attacks)
                target = self.get_unit_at(ar, ac)
                if target:
                    self.attack(unit, target)
        
        self.end_turn()

    def handle_click(self, pos):
        if self.game_over:
            self.__init__()
            return
            
        x, y = pos
        col = x // CELL_SIZE
        row = y // CELL_SIZE
        
        if y >= ROWS * CELL_SIZE:
            return
            
        if self.selected_unit:
            unit = self.selected_unit
            
            if (row, col) in self.move_range:
                self.move_unit(unit, row, col)
                self.move_range = []
                self.attack_range = self.get_attack_range(unit)
            elif (row, col) in self.attack_range:
                target = self.get_unit_at(row, col)
                if target:
                    self.attack(unit, target)
                    self.attack_range = []
            else:
                clicked_unit = self.get_unit_at(row, col)
                if clicked_unit and clicked_unit.team == 'player':
                    self.selected_unit = clicked_unit
                    self.move_range = self.get_move_range(clicked_unit)
                    self.attack_range = self.get_attack_range(clicked_unit)
                else:
                    self.selected_unit = None
                    self.move_range = []
                    self.attack_range = []
        else:
            unit = self.get_unit_at(row, col)
            if unit and unit.team == 'player':
                self.selected_unit = unit
                self.move_range = self.get_move_range(unit)
                self.attack_range = self.get_attack_range(unit)

    def run(self):
        running = True
        while running:
            self.screen.fill(BLACK)
            self.draw_terrain()
            self.draw_ranges()
            self.draw_units()
            self.draw_selected()
            self.draw_ui()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.current_team == 'player':
                        self.end_turn()
                    
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = TacticalWarfare()
    print("=== 回合制战棋游戏 ===")
    print("操作说明：")
    print("- 鼠标左键点击选中单位")
    print("- 蓝色格子表示可移动范围")
    print("- 红色格子表示可攻击范围")
    print("- 空格键结束回合")
    print("- 地形说明：平地-消耗1, 森林-消耗2, 山地-消耗3, 水域-不可通过")
    game.run()
