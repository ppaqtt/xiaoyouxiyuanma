#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生物进化模拟器 - Evolution Simulator
使用遗传算法演示生物进化过程，帮助用户理解自然选择、变异和遗传的概念。

功能：
- 可视化生物种群的进化过程
- 展示DNA/基因的遗传和变异
- 实时统计种群特性变化
- 模拟食物链和生存竞争
- 记录进化历史

作者：科学教育游戏集合
版本：1.0
"""

import pygame
import random
import math
import sys
import time

# 初始化pygame
pygame.init()

# 屏幕设置
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("生物进化模拟器 - Evolution Simulator")

# 颜色定义
COLORS = {
    'background': (245, 250, 240),
    'primary': (34, 139, 34),
    'secondary': (60, 179, 113),
    'accent': (255, 140, 0),
    'text': (40, 40, 40),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'gray': (128, 128, 128),
    'light_gray': (211, 211, 211),
    'red': (220, 20, 60),
    'blue': (30, 144, 255),
    'yellow': (255, 215, 0),
    'purple': (138, 43, 226),
    'orange': (255, 165, 0),
    'green': (0, 200, 100),
}

# 字体设置
font_large = None
font_medium = None
font_small = None

def init_fonts():
    """初始化字体"""
    global font_large, font_medium, font_small
    font_large = pygame.font.Font(None, 36)
    font_medium = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 22)

init_fonts()

# 按钮类
class Button:
    """可点击的按钮类"""
    def __init__(self, x, y, width, height, text, color=COLORS['primary'], hover_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color if hover_color else tuple(min(c + 30, 255) for c in color)
        self.is_hovered = False

    def draw(self, surface):
        """绘制按钮"""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLORS['black'], self.rect, 2, border_radius=8)

        text_surf = font_small.render(self.text, True, COLORS['white'])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        """检查鼠标是否悬停"""
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos):
        """检查按钮是否被点击"""
        return self.rect.collidepoint(pos)

# 基因类
class Gene:
    """基因类，表示生物的一个特征"""
    def __init__(self, value, mutation_rate=0.05, min_val=0, max_val=100):
        self.value = value
        self.mutation_rate = mutation_rate
        self.min_val = min_val
        self.max_val = max_val

    def mutate(self):
        """基因变异"""
        if random.random() < self.mutation_rate:
            # 随机改变基因值
            change = random.uniform(-10, 10)
            self.value = max(self.min_val, min(self.max_val, self.value + change))
            return True
        return False

    @staticmethod
    def crossover(gene1, gene2):
        """基因交叉"""
        # 取两个基因的平均值作为子代基因
        child_value = (gene1.value + gene2.value) / 2
        # 添加小幅度随机扰动
        child_value += random.uniform(-5, 5)
        child_value = max(gene1.min_val, min(gene1.max_val, child_value))
        return Gene(child_value, gene1.mutation_rate, gene1.min_val, gene1.max_val)

# DNA类
class DNA:
    """DNA类，包含多个基因"""
    def __init__(self):
        # 定义各种基因
        self.genes = {
            'speed': Gene(50, 0.1, 10, 100),           # 速度
            'size': Gene(50, 0.08, 20, 100),          # 大小
            'vision': Gene(50, 0.06, 20, 100),        # 视力/感知范围
            'energy': Gene(80, 0.05, 30, 100),         # 初始能量
            'reproduction': Gene(50, 0.07, 20, 100),  # 繁殖能力
            'age': Gene(0, 0, 0, 500),                # 年龄
        }

    def get_fitness(self):
        """计算适应度"""
        speed = self.genes['speed'].value
        size = self.genes['size'].value
        vision = self.genes['vision'].value
        energy = self.genes['energy'].value
        reproduction = self.genes['reproduction'].value
        age = self.genes['age'].value

        # 适应度公式：综合各项指标
        # 速度和视力有利于觅食
        # 大小有利于防御但消耗更多能量
        # 繁殖能力直接影响后代数量
        fitness = (speed * 0.2 + vision * 0.15 +
                  (100 - size) * 0.1 +  # 较小体型更灵活
                  energy * 0.15 +
                  reproduction * 0.25 +
                  max(0, 100 - age) * 0.15)  # 年龄越大适应度越低

        return fitness

    def mutate(self):
        """DNA变异"""
        mutated = False
        for gene in self.genes.values():
            if gene.mutate():
                mutated = True
        return mutated

    @staticmethod
    def crossover(parent1_dna, parent2_dna):
        """DNA交叉"""
        child_dna = DNA()
        for key in child_dna.genes:
            # 随机选择父本基因
            if random.random() < 0.5:
                child_dna.genes[key].value = parent1_dna.genes[key].value
            else:
                child_dna.genes[key].value = parent2_dna.genes[key].value

        # 子代DNA也有小概率变异
        child_dna.mutate()
        return child_dna

    def get_color(self):
        """根据基因生成颜色"""
        speed = self.genes['speed'].value
        size = self.genes['size'].value

        # 颜色由速度和大小决定
        r = int(100 + speed * 1.5)
        g = int(100 + size * 0.5)
        b = int(50 + (speed + size) * 0.5)

        return (min(255, r), min(255, g), min(255, b))

# 生物类
class Creature:
    """生物类"""
    def __init__(self, x, y, dna=None):
        self.x = x
        self.y = y
        self.dna = dna if dna else DNA()
        self.age = 0
        self.energy = self.dna.genes['energy'].value
        self.max_energy = 100
        self.vx = 0
        self.vy = 0
        self.target_x = None
        self.target_y = None
        self.reproduction_cooldown = 0
        self.is_alive = True

    def get_radius(self):
        """获取生物大小"""
        return 5 + self.dna.genes['size'].value * 0.15

    def get_speed(self):
        """获取移动速度"""
        return 1 + self.dna.genes['speed'].value * 0.05

    def get_vision_range(self):
        """获取视野范围"""
        return 30 + self.dna.genes['vision'].value * 0.5

    def update(self, foods, creatures):
        """更新生物状态"""
        if not self.is_alive:
            return

        # 更新年龄和能量
        self.age += 1
        self.dna.genes['age'].value = self.age
        self.energy -= 0.1  # 基础能量消耗

        # 繁殖冷却
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1

        # 能量耗尽或太老则死亡
        if self.energy <= 0 or self.age > 500:
            self.is_alive = False
            return

        # 寻找食物
        nearest_food = self.find_nearest_food(foods)
        if nearest_food:
            self.move_towards(nearest_food.x, nearest_food.y)
        else:
            # 随机移动
            self.random_move()

        # 吃食物
        for food in foods:
            dist = math.sqrt((self.x - food.x) ** 2 + (self.y - food.y) ** 2)
            if dist < self.get_radius() + food.radius:
                self.energy += food.energy
                food.consumed = True
                self.energy = min(self.energy, self.max_energy)

    def find_nearest_food(self, foods):
        """找到最近的的食物"""
        vision_range = self.get_vision_range()
        nearest = None
        min_dist = vision_range

        for food in foods:
            if food.consumed:
                continue
            dist = math.sqrt((self.x - food.x) ** 2 + (self.y - food.y) ** 2)
            if dist < min_dist:
                min_dist = dist
                nearest = food

        return nearest

    def move_towards(self, target_x, target_y):
        """向目标移动"""
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        if dist > 0:
            speed = self.get_speed()
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed

        # 边界检测
        self.x = max(self.get_radius(), min(SCREEN_WIDTH - 200, self.x))
        self.y = max(self.get_radius(), min(SCREEN_HEIGHT - 50, self.y))

    def random_move(self):
        """随机移动"""
        if random.random() < 0.02:  # 2%概率改变方向
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-1, 1)

        speed = self.get_speed()
        self.x += self.vx * speed
        self.y += self.vy * speed

        # 边界检测
        self.x = max(self.get_radius(), min(SCREEN_WIDTH - 200, self.x))
        self.y = max(self.get_radius(), min(SCREEN_HEIGHT - 50, self.y))

    def can_reproduce(self):
        """能否繁殖"""
        return (self.energy > 60 and
                self.age > 50 and
                self.reproduction_cooldown == 0 and
                self.dna.genes['reproduction'].value > 40)

    def reproduce(self):
        """繁殖"""
        self.energy -= 30
        self.reproduction_cooldown = 100

        # 创建子代DNA
        child_dna = DNA()

        return Creature(self.x + random.uniform(-20, 20),
                       self.y + random.uniform(-20, 20),
                       child_dna)

    def draw(self, surface):
        """绘制生物"""
        if not self.is_alive:
            return

        radius = int(self.get_radius())
        color = self.dna.get_color()

        # 绘制身体
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), radius)

        # 绘制能量条
        energy_ratio = self.energy / self.max_energy
        bar_width = radius * 2
        bar_height = 4
        bar_x = self.x - radius
        bar_y = self.y - radius - 8

        # 背景条
        pygame.draw.rect(surface, COLORS['gray'],
                        (bar_x, bar_y, bar_width, bar_height))
        # 能量条
        energy_color = COLORS['green'] if energy_ratio > 0.3 else COLORS['red']
        pygame.draw.rect(surface, energy_color,
                        (bar_x, bar_y, bar_width * energy_ratio, bar_height))

        # 绘制视野范围（半透明）
        vision_range = int(self.get_vision_range())
        vision_surface = pygame.Surface((vision_range * 2, vision_range * 2), pygame.SRCALPHA)
        pygame.draw.circle(vision_surface, (*color, 30), (vision_range, vision_range), vision_range)
        surface.blit(vision_surface, (int(self.x) - vision_range, int(self.y) - vision_range))

# 食物类
class Food:
    """食物类"""
    def __init__(self, x, y, energy=20):
        self.x = x
        self.y = y
        self.radius = random.randint(5, 10)
        self.energy = energy
        self.consumed = False
        self.color = COLORS['green']
        self.pulse = 0

    def update(self):
        """更新食物"""
        if not self.consumed:
            self.pulse = (self.pulse + 0.1) % (2 * math.pi)

    def draw(self, surface):
        """绘制食物"""
        if self.consumed:
            return

        pulse_radius = self.radius + int(math.sin(self.pulse) * 2)

        # 绘制食物
        pygame.draw.circle(surface, self.color,
                          (int(self.x), int(self.y)), pulse_radius)
        pygame.draw.circle(surface, COLORS['white'],
                          (int(self.x) - 2, int(self.y) - 2), 2)

# 统计数据类
class Statistics:
    """统计数据类"""
    def __init__(self):
        self.history = {
            'population': [],
            'avg_speed': [],
            'avg_size': [],
            'avg_fitness': [],
            'avg_age': [],
            'births': [],
            'deaths': [],
        }
        self.max_history = 100

    def update(self, creatures):
        """更新统计数据"""
        if len(creatures) == 0:
            return

        # 计算平均值
        avg_speed = sum(c.dna.genes['speed'].value for c in creatures) / len(creatures)
        avg_size = sum(c.dna.genes['size'].value for c in creatures) / len(creatures)
        avg_fitness = sum(c.dna.get_fitness() for c in creatures) / len(creatures)
        avg_age = sum(c.age for c in creatures) / len(creatures)

        # 添加到历史
        self.history['population'].append(len(creatures))
        self.history['avg_speed'].append(avg_speed)
        self.history['avg_size'].append(avg_size)
        self.history['avg_fitness'].append(avg_fitness)
        self.history['avg_age'].append(avg_age)

        # 限制历史长度
        for key in self.history:
            if len(self.history[key]) > self.max_history:
                self.history[key] = self.history[key][-self.max_history:]

    def draw_chart(self, surface, x, y, width, height, data, title, color):
        """绘制图表"""
        if len(data) < 2:
            return

        # 标题
        title_surf = font_small.render(title, True, COLORS['text'])
        surface.blit(title_surf, (x, y))

        # 绘制图表背景
        chart_rect = pygame.Rect(x, y + 20, width, height - 20)
        pygame.draw.rect(surface, COLORS['white'], chart_rect)
        pygame.draw.rect(surface, COLORS['gray'], chart_rect, 1)

        # 绘制数据线
        max_val = max(data) if max(data) > 0 else 1
        min_val = min(data)
        val_range = max_val - min_val if max_val != min_val else 1

        points = []
        for i, val in enumerate(data[-50:]):  # 只显示最近50个点
            px = x + int(i * width / 49)
            py = y + 20 + int((height - 25) * (1 - (val - min_val) / val_range))
            points.append((px, py))

        if len(points) > 1:
            pygame.draw.lines(surface, color, False, points, 2)

        # 显示当前值
        current_val = data[-1]
        val_surf = font_small.render(f"{current_val:.1f}", True, color)
        surface.blit(val_surf, (x + width - 40, y))

# 进化模拟器主类
class EvolutionSimulator:
    """进化模拟器主类"""

    def __init__(self):
        self.running = True
        self.paused = False
        self.clock = pygame.time.Clock()

        # 模拟参数
        self.population_size = 30
        self.food_count = 50
        self.mutation_rate = 0.1
        self.generation = 0

        # 创建生物和食物
        self.creatures = []
        self.foods = []
        self.statistics = Statistics()

        # 按钮
        self.create_buttons()

        # 初始化种群
        self.initialize_population()

        # 初始化食物
        self.spawn_food(self.food_count)

        # 动画计时器
        self.update_timer = 0
        self.update_interval = 5  # 每隔几帧更新一次

    def create_buttons(self):
        """创建按钮"""
        button_y = SCREEN_HEIGHT - 45
        self.control_buttons = [
            Button(510, button_y, 80, 35, "暂停/继续", COLORS['blue']),
            Button(600, button_y, 70, 35, "加速", COLORS['green']),
            Button(680, button_y, 70, 35, "减速", COLORS['orange']),
            Button(760, button_y, 70, 35, "重置", COLORS['red']),
        ]

        self.speed_buttons = [
            Button(850, button_y, 60, 35, "x1", COLORS['primary']),
            Button(920, button_y, 60, 35, "x2", COLORS['secondary']),
        ]

    def initialize_population(self):
        """初始化种群"""
        self.creatures = []
        for _ in range(self.population_size):
            x = random.randint(100, SCREEN_WIDTH - 300)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            creature = Creature(x, y)
            self.creatures.append(creature)

    def spawn_food(self, count):
        """生成食物"""
        for _ in range(count):
            x = random.randint(50, SCREEN_WIDTH - 250)
            y = random.randint(50, SCREEN_HEIGHT - 100)
            food = Food(x, y, random.randint(15, 25))
            self.foods.append(food)

    def update(self):
        """更新模拟"""
        if self.paused:
            return

        self.update_timer += 1
        if self.update_timer < self.update_interval:
            return
        self.update_timer = 0

        # 更新食物
        for food in self.foods:
            food.update()

        # 补充食物
        available_food = [f for f in self.foods if not f.consumed]
        if len(available_food) < self.food_count // 2:
            self.spawn_food(5)

        # 移除被吃掉的食物
        self.foods = [f for f in self.foods if not f.consumed]

        # 更新生物
        for creature in self.creatures:
            creature.update(self.foods, self.creatures)

        # 繁殖
        new_creatures = []
        for creature in self.creatures:
            if creature.can_reproduce() and len(self.creatures) + len(new_creatures) < 50:
                # 选择一个邻居作为配偶
                neighbors = [c for c in self.creatures
                            if c != creature and c.is_alive and
                            math.sqrt((c.x - creature.x) ** 2 + (c.y - creature.y) ** 2) < 100]

                if neighbors and random.random() < 0.3:
                    # 使用遗传算法交叉
                    child_dna = DNA.crossover(creature.dna, random.choice(neighbors).dna)
                    child = Creature(creature.x + random.uniform(-20, 20),
                                    creature.y + random.uniform(-20, 20),
                                    child_dna)
                    new_creatures.append(child)
                    creature.reproduction_cooldown = 50

        self.creatures.extend(new_creatures)

        # 移除死亡生物
        self.creatures = [c for c in self.creatures if c.is_alive]

        # 如果种群太少，重新初始化
        if len(self.creatures) < 5:
            self.initialize_population()
            self.generation += 1

        # 更新统计
        self.statistics.update(self.creatures)

        # 更新代数
        if len(self.creatures) > 0:
            max_age = max(c.age for c in self.creatures)
            if max_age < 50:
                self.generation += 1

    def draw(self):
        """绘制画面"""
        # 清屏
        screen.fill(COLORS['background'])

        # 绘制标题栏
        self.draw_header()

        # 绘制信息面板
        self.draw_info_panel()

        # 绘制模拟区域
        self.draw_simulation_area()

        # 绘制控制按钮
        self.draw_controls()

        # 绘制统计图表
        self.draw_statistics()

    def draw_header(self):
        """绘制标题栏"""
        # 标题
        title = font_large.render("生物进化模拟器", True, COLORS['primary'])
        screen.blit(title, (20, 15))

        # 副标题
        subtitle = font_small.render("遗传算法演示 - 自然选择与进化", True, COLORS['gray'])
        screen.blit(subtitle, (20, 50))

        # 代数
        gen_text = font_medium.render(f"代数: {self.generation}", True, COLORS['blue'])
        screen.blit(gen_text, (350, 20))

        # 种群数量
        pop_text = font_medium.render(f"种群: {len(self.creatures)}", True, COLORS['green'])
        screen.blit(pop_text, (450, 20))

        # 暂停状态
        if self.paused:
            pause_text = font_medium.render("已暂停", True, COLORS['red'])
            screen.blit(pause_text, (550, 20))

    def draw_info_panel(self):
        """绘制信息面板"""
        panel_rect = pygame.Rect(SCREEN_WIDTH - 190, 70, 180, 300)
        pygame.draw.rect(screen, COLORS['white'], panel_rect, border_radius=10)
        pygame.draw.rect(screen, COLORS['secondary'], panel_rect, 2, border_radius=10)

        # 标题
        title = font_medium.render("生物特性", True, COLORS['primary'])
        screen.blit(title, (SCREEN_WIDTH - 180, 80))

        # 计算平均值
        if len(self.creatures) > 0:
            avg_speed = sum(c.dna.genes['speed'].value for c in self.creatures) / len(self.creatures)
            avg_size = sum(c.dna.genes['size'].value for c in self.creatures) / len(self.creatures)
            avg_vision = sum(c.dna.genes['vision'].value for c in self.creatures) / len(self.creatures)
            avg_energy = sum(c.dna.genes['energy'].value for c in self.creatures) / len(self.creatures)

            info_items = [
                ("速度", avg_speed, COLORS['blue']),
                ("大小", avg_size, COLORS['purple']),
                ("视力", avg_vision, COLORS['green']),
                ("能量", avg_energy, COLORS['orange']),
            ]

            for i, (name, value, color) in enumerate(info_items):
                y = 110 + i * 40
                # 绘制标签
                label = font_small.render(name, True, COLORS['text'])
                screen.blit(label, (SCREEN_WIDTH - 180, y))

                # 绘制进度条
                bar_rect = pygame.Rect(SCREEN_WIDTH - 120, y + 5, 100, 15)
                pygame.draw.rect(screen, COLORS['light_gray'], bar_rect, border_radius=5)
                pygame.draw.rect(screen, color, (bar_rect.x, bar_rect.y,
                                                  int(bar_rect.width * value / 100),
                                                  bar_rect.height), border_radius=5)

                # 数值
                val_text = font_small.render(f"{value:.1f}", True, color)
                screen.blit(val_text, (SCREEN_WIDTH - 40, y))
        else:
            no_data = font_small.render("无生物数据", True, COLORS['gray'])
            screen.blit(no_data, (SCREEN_WIDTH - 170, 120))

    def draw_simulation_area(self):
        """绘制模拟区域"""
        # 模拟区域背景
        sim_rect = pygame.Rect(20, 70, SCREEN_WIDTH - 220, SCREEN_HEIGHT - 130)
        pygame.draw.rect(screen, COLORS['white'], sim_rect, border_radius=10)
        pygame.draw.rect(screen, COLORS['primary'], sim_rect, 2, border_radius=10)

        # 绘制食物
        for food in self.foods:
            food.draw(screen)

        # 绘制生物
        for creature in self.creatures:
            creature.draw(screen)

        # 绘制说明
        legend_y = SCREEN_HEIGHT - 90
        legend_items = [
            ("圆形", COLORS['green'], "食物"),
            ("生物", COLORS['blue'], "生物（颜色表示基因）"),
        ]

        for i, (shape, color, desc) in enumerate(legend_items):
            x = 40 + i * 200
            pygame.draw.circle(screen, color, (x + 10, legend_y + 10), 8)
            text = font_small.render(f"{desc}", True, COLORS['text'])
            screen.blit(text, (x + 25, legend_y))

    def draw_controls(self):
        """绘制控制按钮"""
        y = SCREEN_HEIGHT - 45

        # 控制按钮
        for button in self.control_buttons:
            button.draw(screen)

        # 速度选择
        speed_label = font_small.render("速度:", True, COLORS['text'])
        screen.blit(speed_label, (835, y + 5))

        for button in self.speed_buttons:
            button.draw(screen)

    def draw_statistics(self):
        """绘制统计图表"""
        chart_x = SCREEN_WIDTH - 190
        chart_y = 380
        chart_width = 180
        chart_height = 100

        # 面板背景
        panel_rect = pygame.Rect(SCREEN_WIDTH - 190, 370, 180, 300)
        pygame.draw.rect(screen, COLORS['white'], panel_rect, border_radius=10)
        pygame.draw.rect(screen, COLORS['secondary'], panel_rect, 2, border_radius=10)

        # 标题
        title = font_medium.render("种群统计", True, COLORS['primary'])
        screen.blit(title, (chart_x, chart_y))

        # 绘制图表
        if len(self.statistics.history['population']) > 1:
            self.statistics.draw_chart(
                screen, chart_x, chart_y + 30, chart_width, chart_height - 30,
                self.statistics.history['population'],
                "种群数量",
                COLORS['primary']
            )

            self.statistics.draw_chart(
                screen, chart_x, chart_y + 140, chart_width, chart_height - 30,
                self.statistics.history['avg_fitness'],
                "平均适应度",
                COLORS['accent']
            )

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEMOTION:
                # 更新按钮悬停状态
                for button in self.control_buttons + self.speed_buttons:
                    button.check_hover(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 检查控制按钮
                if self.control_buttons[0].is_clicked(event.pos):  # 暂停/继续
                    self.paused = not self.paused
                elif self.control_buttons[1].is_clicked(event.pos):  # 加速
                    self.update_interval = max(1, self.update_interval - 2)
                elif self.control_buttons[2].is_clicked(event.pos):  # 减速
                    self.update_interval = min(30, self.update_interval + 2)
                elif self.control_buttons[3].is_clicked(event.pos):  # 重置
                    self.reset()

                # 检查速度按钮
                if self.speed_buttons[0].is_clicked(event.pos):
                    self.update_interval = 10
                elif self.speed_buttons[1].is_clicked(event.pos):
                    self.update_interval = 3

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def reset(self):
        """重置模拟"""
        self.generation = 0
        self.creatures = []
        self.foods = []
        self.statistics = Statistics()
        self.initialize_population()
        self.spawn_food(self.food_count)
        self.paused = False

    def run(self):
        """运行模拟"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

# 主函数
def main():
    """主函数"""
    game = EvolutionSimulator()
    game.run()

if __name__ == "__main__":
    main()
