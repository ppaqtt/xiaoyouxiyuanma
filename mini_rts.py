"""
简易RTS（即时战略）游戏
操作说明：
- 左键点击选择单位，拖拽框选多个单位
- 右键点击地面移动，右键点击敌方单位攻击
- 点击基地可以训练新单位（需要足够资源）
- 工人靠近资源点会自动采集
- 消灭所有敌方单位或基地获胜
"""

import pygame
import os
import random
import math
import sys

# 初始化
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

# 常量
SCREEN_W, SCREEN_H = 1200, 800
MAP_W, MAP_H = 2400, 1600
FPS = 60

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (144, 238, 144)
BLUE = (30, 100, 220)
RED = (220, 50, 50)
YELLOW = (255, 215, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
BROWN = (139, 90, 43)
ORANGE = (255, 165, 0)
CYAN = (0, 200, 200)
PANEL_BG = (40, 40, 50)
GOLD_COLOR = (255, 200, 50)

# 单位类型
WORKER = "worker"
SOLDIER = "soldier"
BASE = "base"
RESOURCE = "resource"

# 游戏状态
STATE_PLAYING = 0
STATE_WIN = 1
STATE_LOSE = 2


class Unit:
    """游戏单位基类"""
    def __init__(self, x, y, team, unit_type):
        self.x = x
        self.y = y
        self.team = team  # 0=玩家, 1=敌方
        self.unit_type = unit_type
        self.selected = False
        self.target_x = None
        self.target_y = None
        self.attack_target = None
        self.hp = 100
        self.max_hp = 100
        self.speed = 2.0
        self.attack_range = 0
        self.attack_damage = 0
        self.attack_cooldown = 0
        self.attack_timer = 0
        self.alive = True
        self.carrying = 0  # 携带资源量
        self.max_carry = 10
        self.collecting = False
        self.resource_target = None
        self.returning = False
        self.anim_frame = 0
        self.anim_timer = 0

        # 根据类型设置属性
        if unit_type == WORKER:
            self.hp = 50
            self.max_hp = 50
            self.speed = 2.5
            self.attack_range = 30
            self.attack_damage = 5
            self.attack_cooldown = 40
            self.radius = 8
        elif unit_type == SOLDIER:
            self.hp = 100
            self.max_hp = 100
            self.speed = 2.0
            self.attack_range = 50
            self.attack_damage = 15
            self.attack_cooldown = 30
            self.radius = 10
        elif unit_type == BASE:
            self.hp = 500
            self.max_hp = 500
            self.speed = 0
            self.attack_range = 0
            self.attack_damage = 0
            self.attack_cooldown = 0
            self.radius = 25
        elif unit_type == RESOURCE:
            self.hp = 300
            self.max_hp = 300
            self.speed = 0
            self.radius = 18

    def move_towards(self, tx, ty, all_units):
        """向目标移动，避免重叠"""
        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 2:
            return True
        # 归一化
        nx, ny = dx / dist, dy / dist
        new_x = self.x + nx * self.speed
        new_y = self.y + ny * self.speed
        # 简单碰撞避免
        for u in all_units:
            if u is self or not u.alive:
                continue
            d = math.sqrt((new_x - u.x) ** 2 + (new_y - u.y) ** 2)
            min_dist = self.radius + u.radius + 2
            if d < min_dist and d > 0:
                push_x = (new_x - u.x) / d
                push_y = (new_y - u.y) / d
                new_x = u.x + push_x * min_dist
                new_y = u.y + push_y * min_dist
        # 边界限制
        new_x = max(self.radius, min(MAP_W - self.radius, new_x))
        new_y = max(self.radius, min(MAP_H - self.radius, new_y))
        self.x = new_x
        self.y = new_y
        return False

    def distance_to(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def distance_to_point(self, px, py):
        return math.sqrt((self.x - px) ** 2 + (self.y - py) ** 2)

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def update_animation(self):
        self.anim_timer += 1
        if self.anim_timer >= 15:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4


class Game:
    """RTS游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("简易RTS - 即时战略游戏")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("simhei", 16)
        self.big_font = pygame.font.SysFont("simhei", 36)
        self.small_font = pygame.font.SysFont("simhei", 13)

        # 摄像机
        self.cam_x = 0
        self.cam_y = 0

        # 游戏状态
        self.state = STATE_PLAYING
        self.units = []
        self.resources = [0, 0]  # 玩家和AI的资源
        self.selected_units = []

        # 框选
        self.selecting = False
        self.sel_start = (0, 0)
        self.sel_end = (0, 0)

        # 训练队列
        self.train_queue = []  # 玩家训练队列
        self.train_timer = 0
        self.train_cost = {WORKER: 50, SOLDIER: 100}
        self.train_time = {WORKER: 120, SOLDIER: 180}

        # AI
        self.ai_timer = 0
        self.ai_train_timer = 0
        self.ai_train_queue = []

        # 地图装饰
        self.trees = []
        self.rocks = []
        self._generate_map()

        # 初始化单位和资源
        self._init_game()

    def _generate_map(self):
        """生成地图装饰"""
        for _ in range(80):
            self.trees.append((random.randint(50, MAP_W - 50),
                               random.randint(50, MAP_H - 50),
                               random.randint(8, 16)))
        for _ in range(40):
            self.rocks.append((random.randint(50, MAP_W - 50),
                               random.randint(50, MAP_H - 50),
                               random.randint(5, 12)))

    def _init_game(self):
        """初始化游戏单位"""
        # 玩家基地
        player_base = Unit(200, MAP_H // 2, 0, BASE)
        self.units.append(player_base)
        # 玩家初始工人
        for i in range(3):
            w = Unit(250 + i * 30, MAP_H // 2 + 40, 0, WORKER)
            self.units.append(w)
        # 玩家初始士兵
        for i in range(2):
            s = Unit(250 + i * 30, MAP_H // 2 - 40, 0, SOLDIER)
            self.units.append(s)

        # AI基地
        ai_base = Unit(MAP_W - 200, MAP_H // 2, 1, BASE)
        self.units.append(ai_base)
        # AI初始工人
        for i in range(3):
            w = Unit(MAP_W - 250 - i * 30, MAP_H // 2 + 40, 1, WORKER)
            self.units.append(w)
        # AI初始士兵
        for i in range(2):
            s = Unit(MAP_W - 250 - i * 30, MAP_H // 2 - 40, 1, SOLDIER)
            self.units.append(s)

        # 资源点
        resource_positions = [
            (500, 300), (500, MAP_H - 300),
            (MAP_W // 2, MAP_H // 2 - 200),
            (MAP_W // 2, MAP_H // 2 + 200),
            (MAP_W - 500, 300), (MAP_W - 500, MAP_H - 300),
            (400, MAP_H // 2), (MAP_W - 400, MAP_H // 2),
        ]
        for rx, ry in resource_positions:
            r = Unit(rx, ry, -1, RESOURCE)
            self.units.append(r)

    def get_player_base(self):
        for u in self.units:
            if u.unit_type == BASE and u.team == 0 and u.alive:
                return u
        return None

    def get_ai_base(self):
        for u in self.units:
            if u.unit_type == BASE and u.team == 1 and u.alive:
                return u
        return None

    def get_team_units(self, team, unit_type=None):
        result = []
        for u in self.units:
            if u.team == team and u.alive:
                if unit_type is None or u.unit_type == unit_type:
                    result.append(u)
        return result

    def get_nearest(self, unit, targets):
        nearest = None
        min_dist = float('inf')
        for t in targets:
            d = unit.distance_to(t)
            if d < min_dist:
                min_dist = d
                nearest = t
        return nearest, min_dist

    def screen_to_world(self, sx, sy):
        return sx + self.cam_x, sy + self.cam_y

    def world_to_screen(self, wx, wy):
        return wx - self.cam_x, wy - self.cam_y

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r and self.state != STATE_PLAYING:
                    self.__init__()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state != STATE_PLAYING:
                    continue
                mx, my = event.pos
                if my > SCREEN_H - 80:
                    # 点击底部面板
                    self._handle_panel_click(mx, my)
                    continue
                if event.button == 1:  # 左键
                    # 检查是否点击了单位
                    wx, wy = self.screen_to_world(mx, my)
                    clicked_unit = None
                    for u in self.units:
                        if u.alive and u.team == 0 and u.unit_type != RESOURCE:
                            if u.distance_to_point(wx, wy) < u.radius + 5:
                                clicked_unit = u
                                break
                    if clicked_unit:
                        # 取消其他选择
                        for u in self.selected_units:
                            u.selected = False
                        self.selected_units = [clicked_unit]
                        clicked_unit.selected = True
                    else:
                        # 开始框选
                        self.selecting = True
                        self.sel_start = (mx, my)
                        self.sel_end = (mx, my)
                elif event.button == 3:  # 右键
                    wx, wy = self.screen_to_world(mx, my)
                    self._handle_right_click(wx, wy)
            elif event.type == pygame.MOUSEMOTION:
                if self.selecting:
                    self.sel_end = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.selecting:
                    self.selecting = False
                    self._do_box_select()
        return True

    def _handle_panel_click(self, mx, my):
        """处理底部面板点击"""
        panel_y = SCREEN_H - 80
        # 训练工人按钮
        if 10 <= mx <= 110 and panel_y + 10 <= my <= panel_y + 50:
            if self.resources[0] >= self.train_cost[WORKER]:
                self.train_queue.append(WORKER)
                self.resources[0] -= self.train_cost[WORKER]
        # 训练士兵按钮
        elif 120 <= mx <= 220 and panel_y + 10 <= my <= panel_y + 50:
            if self.resources[0] >= self.train_cost[SOLDIER]:
                self.train_queue.append(SOLDIER)
                self.resources[0] -= self.train_cost[SOLDIER]

    def _handle_right_click(self, wx, wy):
        """处理右键命令"""
        if not self.selected_units:
            return
        # 检查是否右键点击了敌方单位
        target = None
        for u in self.units:
            if u.alive and u.team == 1 and u.unit_type != RESOURCE:
                if u.distance_to_point(wx, wy) < u.radius + 5:
                    target = u
                    break
        for u in self.selected_units:
            if target:
                u.attack_target = target
                u.target_x = None
                u.target_y = None
                u.collecting = False
                u.returning = False
                u.resource_target = None
            else:
                u.target_x = wx + random.randint(-15, 15)
                u.target_y = wy + random.randint(-15, 15)
                u.attack_target = None
                u.collecting = False
                u.returning = False
                u.resource_target = None

    def _do_box_select(self):
        """框选单位"""
        x1 = min(self.sel_start[0], self.sel_end[0])
        y1 = min(self.sel_start[1], self.sel_end[1])
        x2 = max(self.sel_start[0], self.sel_end[0])
        y2 = max(self.sel_start[1], self.sel_end[1])
        # 太小的框视为点击
        if x2 - x1 < 5 and y2 - y1 < 5:
            for u in self.selected_units:
                u.selected = False
            self.selected_units = []
            return
        for u in self.selected_units:
            u.selected = False
        self.selected_units = []
        for u in self.units:
            if u.alive and u.team == 0 and u.unit_type != RESOURCE:
                sx, sy = self.world_to_screen(u.x, u.y)
                if x1 <= sx <= x2 and y1 <= sy <= y2:
                    u.selected = True
                    self.selected_units.append(u)

    def update_camera(self):
        """更新摄像机位置"""
        keys = pygame.key.get_pressed()
        speed = 8
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.cam_x -= speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.cam_x += speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.cam_y -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.cam_y += speed
        # 边界
        self.cam_x = max(0, min(MAP_W - SCREEN_W, self.cam_x))
        self.cam_y = max(0, min(MAP_H - (SCREEN_H - 80), self.cam_y))

    def update_units(self):
        """更新所有单位"""
        alive_units = [u for u in self.units if u.alive]
        for u in alive_units:
            u.update_animation()
            if u.attack_timer > 0:
                u.attack_timer -= 1

            if u.unit_type == RESOURCE or u.unit_type == BASE:
                continue

            # 工人AI
            if u.unit_type == WORKER:
                self._update_worker(u, alive_units)
            # 士兵AI
            elif u.unit_type == SOLDIER:
                self._update_soldier(u, alive_units)

    def _update_worker(self, worker, alive_units):
        """更新工人行为"""
        base = self.get_player_base() if worker.team == 0 else self.get_ai_base()
        if not base:
            return

        # 返回基地卸货
        if worker.returning:
            if worker.distance_to(base) < base.radius + 20:
                self.resources[worker.team] += worker.carrying
                worker.carrying = 0
                worker.returning = False
                worker.collecting = False
            else:
                worker.move_towards(base.x, base.y, alive_units)
            return

        # 采集资源
        if worker.collecting and worker.resource_target:
            if not worker.resource_target.alive:
                worker.collecting = False
                worker.resource_target = None
                return
            if worker.distance_to(worker.resource_target) < worker.resource_target.radius + 15:
                # 采集
                worker.resource_target.hp -= 0.5
                worker.carrying += 0.05
                if worker.carrying >= worker.max_carry:
                    worker.returning = True
                if worker.resource_target.hp <= 0:
                    worker.resource_target.alive = False
                    worker.returning = True
            else:
                worker.move_towards(worker.resource_target.x,
                                    worker.resource_target.y, alive_units)
            return

        # 攻击目标
        if worker.attack_target:
            if not worker.attack_target.alive:
                worker.attack_target = None
            else:
                if worker.distance_to(worker.attack_target) < worker.attack_range:
                    if worker.attack_timer <= 0:
                        worker.attack_target.take_damage(worker.attack_damage)
                        worker.attack_timer = worker.attack_cooldown
                else:
                    worker.move_towards(worker.attack_target.x,
                                        worker.attack_target.y, alive_units)
                return

        # 移动到目标
        if worker.target_x is not None:
            arrived = worker.move_towards(worker.target_x, worker.target_y, alive_units)
            if arrived:
                worker.target_x = None
                worker.target_y = None
                # 到达目标后自动寻找附近资源
                resources = [u for u in alive_units if u.unit_type == RESOURCE and u.alive]
                if resources:
                    nearest, dist = self.get_nearest(worker, resources)
                    if dist < 200:
                        worker.collecting = True
                        worker.resource_target = nearest

    def _update_soldier(self, soldier, alive_units):
        """更新士兵行为"""
        # 攻击目标
        if soldier.attack_target:
            if not soldier.attack_target.alive:
                soldier.attack_target = None
                # 自动寻找新目标
                enemies = [u for u in alive_units if u.team != soldier.team
                           and u.unit_type != RESOURCE and u.alive]
                if enemies:
                    nearest, dist = self.get_nearest(soldier, enemies)
                    if dist < 200:
                        soldier.attack_target = nearest
            else:
                if soldier.distance_to(soldier.attack_target) < soldier.attack_range:
                    if soldier.attack_timer <= 0:
                        soldier.attack_target.take_damage(soldier.attack_damage)
                        soldier.attack_timer = soldier.attack_cooldown
                else:
                    soldier.move_towards(soldier.attack_target.x,
                                        soldier.attack_target.y, alive_units)
                return

        # 移动到目标
        if soldier.target_x is not None:
            arrived = soldier.move_towards(soldier.target_x, soldier.target_y, alive_units)
            if arrived:
                soldier.target_x = None
                soldier.target_y = None

    def update_training(self):
        """更新训练队列"""
        if self.train_queue:
            self.train_timer += 1
            unit_type = self.train_queue[0]
            if self.train_timer >= self.train_time[unit_type]:
                self.train_timer = 0
                self.train_queue.pop(0)
                base = self.get_player_base()
                if base:
                    offset = random.randint(-30, 30)
                    new_unit = Unit(base.x + offset, base.y + 40, 0, unit_type)
                    self.units.append(new_unit)

    def update_ai(self):
        """更新AI逻辑"""
        self.ai_timer += 1
        if self.ai_timer < 30:
            return
        self.ai_timer = 0

        ai_units = self.get_team_units(1)
        ai_workers = [u for u in ai_units if u.unit_type == WORKER]
        ai_soldiers = [u for u in ai_units if u.unit_type == SOLDIER]
        ai_base = self.get_ai_base()

        if not ai_base:
            return

        # AI训练
        self.ai_train_timer += 1
        if not self.ai_train_queue:
            if len(ai_workers) < 4 and self.resources[1] >= 50:
                self.ai_train_queue.append(WORKER)
                self.resources[1] -= 50
            elif len(ai_soldiers) < 6 and self.resources[1] >= 100:
                self.ai_train_queue.append(SOLDIER)
                self.resources[1] -= 100

        if self.ai_train_queue:
            self.ai_train_timer_check = getattr(self, 'ai_train_timer_check', 0) + 1
            if self.ai_train_timer_check >= 150:
                self.ai_train_timer_check = 0
                unit_type = self.ai_train_queue.pop(0)
                offset = random.randint(-30, 30)
                new_unit = Unit(ai_base.x + offset, ai_base.y + 40, 1, unit_type)
                self.units.append(new_unit)

        # AI工人行为
        resources = [u for u in self.units if u.unit_type == RESOURCE and u.alive]
        for w in ai_workers:
            if w.returning or w.attack_target:
                continue
            if not w.collecting:
                if resources:
                    nearest, dist = self.get_nearest(w, resources)
                    if nearest:
                        w.collecting = True
                        w.resource_target = nearest

        # AI士兵行为 - 进攻
        player_units = self.get_team_units(0)
        if player_units and len(ai_soldiers) >= 3:
            for s in ai_soldiers:
                if not s.attack_target:
                    nearest, dist = self.get_nearest(s, player_units)
                    if nearest and dist < 400:
                        s.attack_target = nearest
                    elif nearest:
                        # 向玩家方向移动
                        s.target_x = nearest.x + random.randint(-50, 50)
                        s.target_y = nearest.y + random.randint(-50, 50)

    def check_win_lose(self):
        """检查胜负条件"""
        player_base = self.get_player_base()
        ai_base = self.get_ai_base()
        player_units = self.get_team_units(0)
        ai_units = self.get_team_units(1)

        if not ai_base and not ai_units:
            self.state = STATE_WIN
        elif not player_base and not player_units:
            self.state = STATE_LOSE

    def draw(self):
        """绘制游戏画面"""
        self.screen.fill(DARK_GREEN)

        # 绘制地面网格
        grid_size = 100
        start_x = -(self.cam_x % grid_size)
        start_y = -(self.cam_y % grid_size)
        for x in range(int(start_x), SCREEN_W + grid_size, grid_size):
            pygame.draw.line(self.screen, (0, 90, 0), (x, 0), (x, SCREEN_H - 80))
        for y in range(int(start_y), SCREEN_H - 80 + grid_size, grid_size):
            pygame.draw.line(self.screen, (0, 90, 0), (0, y), (SCREEN_W, y))

        # 绘制装饰
        for tx, ty, tr in self.trees:
            sx, sy = self.world_to_screen(tx, ty)
            if -20 < sx < SCREEN_W + 20 and -20 < sy < SCREEN_H:
                pygame.draw.circle(self.screen, (0, 80, 0), (int(sx), int(sy)), tr)
                pygame.draw.circle(self.screen, (0, 110, 0), (int(sx) - 2, int(sy) - 2), tr - 2)

        for rx, ry, rr in self.rocks:
            sx, sy = self.world_to_screen(rx, ry)
            if -20 < sx < SCREEN_W + 20 and -20 < sy < SCREEN_H:
                pygame.draw.circle(self.screen, GRAY, (int(sx), int(sy)), rr)
                pygame.draw.circle(self.screen, LIGHT_GRAY, (int(sx) - 1, int(sy) - 1), rr - 1)

        # 绘制资源点
        for u in self.units:
            if u.unit_type == RESOURCE and u.alive:
                sx, sy = self.world_to_screen(u.x, u.y)
                if -30 < sx < SCREEN_W + 30 and -30 < sy < SCREEN_H:
                    # 金色矿脉
                    pygame.draw.circle(self.screen, (180, 140, 20), (int(sx), int(sy)), u.radius)
                    pygame.draw.circle(self.screen, GOLD_COLOR, (int(sx), int(sy)), u.radius - 3)
                    # 闪光效果
                    pygame.draw.circle(self.screen, YELLOW,
                                       (int(sx) - 4, int(sy) - 4), 4)
                    # 资源量
                    txt = self.small_font.render(f"{int(u.hp)}", True, BLACK)
                    self.screen.blit(txt, (sx - txt.get_width() // 2, sy - 6))

        # 绘制单位
        for u in self.units:
            if not u.alive or u.unit_type == RESOURCE:
                continue
            sx, sy = self.world_to_screen(u.x, u.y)
            if -30 < sx < SCREEN_W + 30 and -30 < sy < SCREEN_H:
                self._draw_unit(u, sx, sy)

        # 绘制框选
        if self.selecting:
            x1 = min(self.sel_start[0], self.sel_end[0])
            y1 = min(self.sel_start[1], self.sel_end[1])
            w = abs(self.sel_end[0] - self.sel_start[0])
            h = abs(self.sel_end[1] - self.sel_start[1])
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            s.fill((0, 150, 255, 40))
            self.screen.blit(s, (x1, y1))
            pygame.draw.rect(self.screen, (0, 150, 255), (x1, y1, w, h), 1)

        # 绘制移动/攻击指示
        for u in self.selected_units:
            if u.target_x is not None:
                sx, sy = self.world_to_screen(u.target_x, u.target_y)
                pygame.draw.circle(self.screen, GREEN, (int(sx), int(sy)), 5, 1)
            if u.attack_target and u.attack_target.alive:
                sx, sy = self.world_to_screen(u.attack_target.x, u.attack_target.y)
                pygame.draw.circle(self.screen, RED, (int(sx), int(sy)),
                                   u.attack_target.radius + 5, 2)

        # 绘制底部面板
        self._draw_panel()

        # 绘制胜负
        if self.state == STATE_WIN:
            self._draw_overlay("胜利!", (0, 200, 0))
        elif self.state == STATE_LOSE:
            self._draw_overlay("失败!", (200, 0, 0))

        pygame.display.flip()

    def _draw_unit(self, u, sx, sy):
        """绘制单个单位"""
        color = BLUE if u.team == 0 else RED
        dark = (20, 60, 150) if u.team == 0 else (150, 30, 30)

        if u.unit_type == BASE:
            # 基地 - 方形建筑
            r = u.radius
            pygame.draw.rect(self.screen, dark,
                             (sx - r, sy - r, r * 2, r * 2))
            pygame.draw.rect(self.screen, color,
                             (sx - r + 3, sy - r + 3, r * 2 - 6, r * 2 - 6))
            # 旗帜
            pygame.draw.line(self.screen, BLACK, (int(sx), int(sy) - r),
                             (int(sx), int(sy) - r - 15), 2)
            flag_color = BLUE if u.team == 0 else RED
            pygame.draw.polygon(self.screen, flag_color, [
                (int(sx), int(sy) - r - 15),
                (int(sx) + 12, int(sy) - r - 10),
                (int(sx), int(sy) - r - 5)
            ])
            # 训练进度
            if u.team == 0 and self.train_queue:
                progress = self.train_timer / self.train_time[self.train_queue[0]]
                bar_w = r * 2
                pygame.draw.rect(self.screen, DARK_GRAY, (sx - r, sy + r + 5, bar_w, 6))
                pygame.draw.rect(self.screen, CYAN, (sx - r, sy + r + 5, int(bar_w * progress), 6))
            txt = self.small_font.render("基地", True, WHITE)
            self.screen.blit(txt, (sx - txt.get_width() // 2, sy - 6))
        elif u.unit_type == WORKER:
            # 工人 - 小圆形
            pygame.draw.circle(self.screen, dark, (int(sx), int(sy)), u.radius)
            pygame.draw.circle(self.screen, color, (int(sx), int(sy)), u.radius - 2)
            # 工具标识
            pygame.draw.line(self.screen, YELLOW,
                             (int(sx) - 4, int(sy) - 4),
                             (int(sx) + 4, int(sy) + 4), 2)
            # 携带资源显示
            if u.carrying > 0:
                bar_w = 16
                ratio = u.carrying / u.max_carry
                pygame.draw.rect(self.screen, DARK_GRAY,
                                 (sx - bar_w // 2, sy - u.radius - 8, bar_w, 4))
                pygame.draw.rect(self.screen, GOLD_COLOR,
                                 (sx - bar_w // 2, sy - u.radius - 8, int(bar_w * ratio), 4))
        elif u.unit_type == SOLDIER:
            # 士兵 - 带盾牌的圆形
            pygame.draw.circle(self.screen, dark, (int(sx), int(sy)), u.radius)
            pygame.draw.circle(self.screen, color, (int(sx), int(sy)), u.radius - 2)
            # 剑标识
            pygame.draw.line(self.screen, WHITE,
                             (int(sx) - 3, int(sy) - 6),
                             (int(sx) + 3, int(sy) + 6), 2)
            pygame.draw.line(self.screen, WHITE,
                             (int(sx) - 4, int(sy) - 2),
                             (int(sx) + 4, int(sy) - 2), 2)

        # 选中高亮
        if u.selected:
            pygame.draw.circle(self.screen, (0, 255, 0),
                               (int(sx), int(sy)), u.radius + 4, 2)

        # 血条
        if u.hp < u.max_hp:
            bar_w = 24
            bar_h = 4
            bx = sx - bar_w // 2
            by = sy - u.radius - 12
            ratio = u.hp / u.max_hp
            pygame.draw.rect(self.screen, DARK_GRAY, (bx, by, bar_w, bar_h))
            bar_color = GREEN if ratio > 0.5 else YELLOW if ratio > 0.25 else RED
            pygame.draw.rect(self.screen, bar_color, (bx, by, int(bar_w * ratio), bar_h))

    def _draw_panel(self):
        """绘制底部信息面板"""
        panel_y = SCREEN_H - 80
        pygame.draw.rect(self.screen, PANEL_BG, (0, panel_y, SCREEN_W, 80))
        pygame.draw.line(self.screen, GRAY, (0, panel_y), (SCREEN_W, panel_y), 2)

        # 资源显示
        gold_txt = self.font.render(f"金币: {self.resources[0]}", True, GOLD_COLOR)
        self.screen.blit(gold_txt, (SCREEN_W // 2 - 60, panel_y + 5))

        # 人口
        player_units = self.get_team_units(0)
        pop_txt = self.font.render(f"人口: {len(player_units)}", True, WHITE)
        self.screen.blit(pop_txt, (SCREEN_W // 2 - 60, panel_y + 30))

        # 训练按钮
        base = self.get_player_base()
        if base:
            # 工人按钮
            btn_color = (60, 60, 80) if self.resources[0] >= 50 else (40, 40, 40)
            pygame.draw.rect(self.screen, btn_color, (10, panel_y + 10, 100, 40), border_radius=5)
            pygame.draw.rect(self.screen, CYAN, (10, panel_y + 10, 100, 40), 2, border_radius=5)
            w_txt = self.font.render(f"工人 50g", True, WHITE)
            self.screen.blit(w_txt, (20, panel_y + 18))

            # 士兵按钮
            btn_color2 = (60, 60, 80) if self.resources[0] >= 100 else (40, 40, 40)
            pygame.draw.rect(self.screen, btn_color2, (120, panel_y + 10, 100, 40), border_radius=5)
            pygame.draw.rect(self.screen, CYAN, (120, panel_y + 10, 100, 40), 2, border_radius=5)
            s_txt = self.font.render(f"士兵 100g", True, WHITE)
            self.screen.blit(s_txt, (128, panel_y + 18))

            # 训练队列
            if self.train_queue:
                q_txt = self.small_font.render(
                    f"训练中: {len(self.train_queue)}", True, CYAN)
                self.screen.blit(q_txt, (10, panel_y + 58))

        # 选中单位信息
        if self.selected_units:
            info = f"已选择: {len(self.selected_units)} 个单位"
            types = {}
            for u in self.selected_units:
                t = u.unit_type
                types[t] = types.get(t, 0) + 1
            for t, c in types.items():
                name = {WORKER: "工人", SOLDIER: "士兵"}.get(t, t)
                info += f" | {name}: {c}"
            info_txt = self.small_font.render(info, True, WHITE)
            self.screen.blit(info_txt, (SCREEN_W - info_txt.get_width() - 10, panel_y + 5))

        # 操作提示
        help_txt = self.small_font.render(
            "WASD/方向键:移动视角 | 左键:选择/框选 | 右键:移动/攻击 | R:重开",
            True, LIGHT_GRAY)
        self.screen.blit(help_txt, (SCREEN_W // 2 - help_txt.get_width() // 2, panel_y + 58))

    def _draw_overlay(self, text, color):
        """绘制胜负覆盖层"""
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        txt = self.big_font.render(text, True, color)
        self.screen.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2,
                               SCREEN_H // 2 - 50))
        sub = self.font.render("按 R 重新开始", True, WHITE)
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2,
                               SCREEN_H // 2 + 10))

    def run(self):
        """游戏主循环"""
        running = True
        while running:
            running = self.handle_events()
            if self.state == STATE_PLAYING:
                self.update_camera()
                self.update_units()
                self.update_training()
                self.update_ai()
                self.check_win_lose()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
