#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数学实验室 - Geometry Lab
一个交互式的几何学习游戏，帮助用户学习几何图形、角度计算和面积计算。

功能：
- 绘制各种几何图形（圆形、矩形、三角形、正多边形）
- 计算角度、面积和周长
- 交互式参数调整
- 可视化几何概念

作者：科学教育游戏集合
版本：1.0
"""

import pygame
import os
import math
import random
import sys

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

# 屏幕设置
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("数学实验室 - Geometry Lab")

# 颜色定义
COLORS = {
    'background': (240, 248, 255),
    'primary': (70, 130, 180),
    'secondary': (100, 149, 237),
    'accent': (255, 140, 0),
    'text': (50, 50, 50),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'gray': (128, 128, 128),
    'light_gray': (211, 211, 211),
    'green': (34, 139, 34),
    'red': (220, 20, 60),
    'blue': (30, 144, 255),
    'yellow': (255, 215, 0),
    'purple': (138, 43, 226),
}

# 字体设置
font_large = None
font_medium = None
font_small = None

def init_fonts():
    """初始化字体"""
    global font_large, font_medium, font_small
    font_large = get_chinese_font(48)
    font_medium = get_chinese_font(32)
    font_small = get_chinese_font(24)

init_fonts()

# 按钮类
class Button:
    """可点击的按钮类"""
    def __init__(self, x, y, width, height, text, color=COLORS['primary'], hover_color=COLORS['secondary']):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        """绘制按钮"""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, COLORS['black'], self.rect, 2, border_radius=10)

        text_surf = font_small.render(self.text, True, COLORS['white'])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        """检查鼠标是否悬停"""
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos):
        """检查按钮是否被点击"""
        return self.rect.collidepoint(pos)

# 滑块类
class Slider:
    """参数滑块类"""
    def __init__(self, x, y, width, height, min_val, max_val, value, label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.label = label
        self.dragging = False

        # 计算滑块位置
        self.handle_width = 20
        self.handle_rect = pygame.Rect(x, y - 5, self.handle_width, height + 10)

    def draw(self, surface):
        """绘制滑块"""
        # 绘制标签
        label_surf = font_small.render(f"{self.label}: {self.value:.1f}", True, COLORS['text'])
        surface.blit(label_surf, (self.rect.x, self.rect.y - 25))

        # 绘制滑块槽
        pygame.draw.rect(surface, COLORS['light_gray'], self.rect, border_radius=5)

        # 计算滑块位置
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + int(ratio * (self.rect.width - self.handle_width))
        self.handle_rect.x = handle_x

        # 绘制滑块手柄
        pygame.draw.rect(surface, COLORS['primary'], self.handle_rect, border_radius=5)
        pygame.draw.rect(surface, COLORS['black'], self.handle_rect, 2, border_radius=5)

    def handle_event(self, event):
        """处理滑块事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                # 计算新值
                ratio = (event.pos[0] - self.rect.x) / self.rect.width
                ratio = max(0, min(1, ratio))
                self.value = self.min_val + ratio * (self.max_val - self.min_val)

    def update(self, pos):
        """更新滑块状态"""
        if self.dragging:
            ratio = (pos[0] - self.rect.x) / self.rect.width
            ratio = max(0, min(1, ratio))
            self.value = self.min_val + ratio * (self.max_val - self.min_val)

# 几何图形绘制函数
def draw_circle(surface, center, radius, color, filled=True, width=2):
    """绘制圆形"""
    if filled:
        pygame.draw.circle(surface, color, center, int(radius))
    else:
        pygame.draw.circle(surface, color, center, int(radius), width)

def draw_rectangle(surface, pos, size, color, filled=True, width=2):
    """绘制矩形"""
    if filled:
        pygame.draw.rect(surface, color, (*pos, *size))
    else:
        pygame.draw.rect(surface, color, (*pos, *size), width)

def draw_triangle(surface, points, color, filled=True, width=2):
    """绘制三角形"""
    if filled:
        pygame.draw.polygon(surface, color, points)
    else:
        pygame.draw.polygon(surface, color, points, width)

def draw_polygon(surface, center, radius, sides, color, rotation=0, filled=True, width=2):
    """绘制正多边形"""
    points = []
    for i in range(sides):
        angle = rotation + (2 * math.pi * i / sides) - math.pi / 2
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        points.append((x, y))

    if filled:
        pygame.draw.polygon(surface, color, points)
    else:
        pygame.draw.polygon(surface, color, points, width)

    return points

def draw_line(surface, start, end, color, width=2):
    """绘制线条"""
    pygame.draw.line(surface, color, start, end, width)

def draw_angle_arc(surface, center, radius, start_angle, end_angle, color):
    """绘制角度弧线"""
    # 绘制两条边
    x1 = center[0] + radius * math.cos(start_angle)
    y1 = center[1] + radius * math.sin(start_angle)
    x2 = center[0] + radius * math.cos(end_angle)
    y2 = center[1] + radius * math.sin(end_angle)

    pygame.draw.line(surface, color, center, (x1, y1), 2)
    pygame.draw.line(surface, color, center, (x2, y2), 2)

    # 绘制弧线
    rect = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)
    pygame.draw.arc(surface, color, rect, start_angle, end_angle, 2)

def calculate_polygon_area(sides, radius):
    """计算正多边形面积"""
    angle = math.pi / sides
    side_length = 2 * radius * math.sin(angle)
    perimeter = sides * side_length
    apothem = radius * math.cos(angle)
    return 0.5 * perimeter * apothem

def calculate_polygon_perimeter(sides, radius):
    """计算正多边形周长"""
    angle = math.pi / sides
    side_length = 2 * radius * math.sin(angle)
    return sides * side_length

def draw_grid(surface):
    """绘制网格"""
    grid_color = (200, 200, 200)
    spacing = 50

    for x in range(0, SCREEN_WIDTH, spacing):
        pygame.draw.line(surface, grid_color, (x, 0), (x, SCREEN_HEIGHT), 1)

    for y in range(0, SCREEN_HEIGHT, spacing):
        pygame.draw.line(surface, grid_color, (0, y), (SCREEN_WIDTH, y), 1)

def draw_axis(surface):
    """绘制坐标轴"""
    axis_color = (100, 100, 100)
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2

    # X轴
    pygame.draw.line(surface, axis_color, (0, center_y), (SCREEN_WIDTH, center_y), 2)
    # Y轴
    pygame.draw.line(surface, axis_color, (center_x, 0), (center_x, SCREEN_HEIGHT), 2)

def draw_ruler(surface, length, start_pos, horizontal=True):
    """绘制标尺"""
    tick_color = COLORS['text']
    spacing = 20

    for i in range(int(length / spacing) + 1):
        if horizontal:
            x = start_pos[0] + i * spacing
            y = start_pos[1]
            pygame.draw.line(surface, tick_color, (x, y), (x, y + 10 if i % 5 == 0 else y + 5), 1)
        else:
            x = start_pos[0]
            y = start_pos[1] + i * spacing
            pygame.draw.line(surface, tick_color, (x, y), (x + 10 if i % 5 == 0 else x + 5, y), 1)

# 主游戏类
class GeometryLab:
    """数学实验室主类"""

    def __init__(self):
        self.running = True
        self.clock = pygame.time.Clock()
        self.mode = "menu"  # menu, circle, rectangle, triangle, polygon, angle, calculator

        # 图形参数
        self.center_x = SCREEN_WIDTH // 2 + 100
        self.center_y = SCREEN_HEIGHT // 2 - 50
        self.radius = 100
        self.width = 150
        self.height = 100
        self.sides = 5
        self.rotation = 0

        # 角度参数
        self.angle1 = 0
        self.angle2 = math.pi / 4

        # 计算器参数
        self.input_num1 = ""
        self.input_num2 = ""
        self.calc_result = ""
        self.calc_operation = "+"
        self.calculator_mode = "add"  # add, subtract, multiply, divide, sqrt, power

        # 创建按钮
        self.create_buttons()

        # 创建滑块
        self.create_sliders()

    def create_buttons(self):
        """创建按钮"""
        button_y = 100
        button_width = 160
        button_height = 50
        spacing = 20

        # 菜单按钮
        self.menu_buttons = [
            Button(50, button_y, button_width, button_height, "圆形", COLORS['blue']),
            Button(50, button_y + 70, button_width, button_height, "矩形", COLORS['green']),
            Button(50, button_y + 140, button_width, button_height, "三角形", COLORS['purple']),
            Button(50, button_y + 210, button_width, button_height, "正多边形", COLORS['accent']),
            Button(50, button_y + 280, button_width, button_height, "角度计算", COLORS['red']),
            Button(50, button_y + 350, button_width, button_height, "计算器", COLORS['primary']),
            Button(50, button_y + 420, button_width, button_height, "退出", COLORS['gray']),
        ]

        # 模式按钮
        self.mode_buttons = [
            Button(50, SCREEN_HEIGHT - 100, 100, 40, "返回菜单"),
            Button(170, SCREEN_HEIGHT - 100, 100, 40, "清空"),
        ]

        # 计算器按钮
        calc_y = SCREEN_HEIGHT - 180
        self.calc_buttons = [
            Button(50, calc_y, 60, 40, "+", COLORS['primary']),
            Button(120, calc_y, 60, 40, "-", COLORS['primary']),
            Button(190, calc_y, 60, 40, "*", COLORS['primary']),
            Button(260, calc_y, 60, 40, "/", COLORS['primary']),
            Button(50, calc_y + 50, 130, 40, "x^2", COLORS['secondary']),
            Button(190, calc_y + 50, 130, 40, "sqrt", COLORS['secondary']),
            Button(50, calc_y + 100, 270, 40, "=", COLORS['accent']),
            Button(50, calc_y + 150, 270, 40, "清空", COLORS['gray']),
        ]

    def create_sliders(self):
        """创建滑块"""
        self.sliders = {
            'radius': Slider(250, 60, 200, 20, 30, 200, self.radius, "半径"),
            'width': Slider(250, 60, 200, 20, 50, 300, self.width, "宽度"),
            'height': Slider(250, 100, 200, 20, 30, 200, self.height, "高度"),
            'sides': Slider(250, 60, 200, 20, 3, 12, self.sides, "边数"),
            'rotation': Slider(250, 100, 200, 20, 0, 360, 0, "旋转角度"),
            'angle1': Slider(250, 60, 200, 20, 0, 360, 45, "角度1"),
            'angle2': Slider(250, 100, 200, 20, 0, 360, 90, "角度2"),
        }

    def draw_menu(self):
        """绘制主菜单"""
        # 标题
        title = font_large.render("数学实验室", True, COLORS['primary'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2 + 100, 50))
        screen.blit(title, title_rect)

        # 副标题
        subtitle = font_medium.render("选择你想要学习的几何图形", True, COLORS['text'])
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2 + 100, 80))
        screen.blit(subtitle, subtitle_rect)

        # 绘制装饰图形
        self.draw_decorative_shapes()

        # 绘制按钮
        for button in self.menu_buttons:
            button.draw(screen)

        # 说明文字
        info_texts = [
            "欢迎来到数学实验室！",
            "这里你可以学习各种几何图形",
            "点击左侧按钮开始学习",
        ]

        for i, text in enumerate(info_texts):
            text_surf = font_small.render(text, True, COLORS['text'])
            screen.blit(text_surf, (SCREEN_WIDTH // 2, 500 + i * 30))

    def draw_decorative_shapes(self):
        """绘制装饰性图形"""
        # 绘制一些几何图形装饰
        shapes = [
            ("circle", (750, 200), 40, COLORS['blue']),
            ("circle", (850, 150), 25, COLORS['green']),
            ("rect", (800, 300), (60, 40), COLORS['purple']),
            ("triangle", [(720, 400), (780, 400), (750, 350)], COLORS['accent']),
            ("polygon", (750, 500), 35, 6, COLORS['red']),
        ]

        for shape in shapes:
            if shape[0] == "circle":
                draw_circle(screen, shape[1], shape[2], shape[3])
            elif shape[0] == "rect":
                draw_rectangle(screen, shape[1], shape[2], shape[3])
            elif shape[0] == "triangle":
                draw_triangle(screen, shape[1], shape[2])
            elif shape[0] == "polygon":
                draw_polygon(screen, shape[1], shape[2], shape[3], shape[4])

    def draw_circle_mode(self):
        """绘制圆形模式"""
        self.draw_mode_header("圆形 - Circle")

        # 获取当前滑块值
        radius = int(self.sliders['radius'].value)

        # 绘制圆形
        center = (self.center_x, self.center_y)
        draw_circle(screen, center, radius, COLORS['blue'])
        draw_circle(screen, center, radius, COLORS['black'], filled=False, width=2)

        # 绘制半径线
        pygame.draw.line(screen, COLORS['red'], center,
                        (center[0] + radius, center[1]), 3)
        radius_text = font_small.render("r", True, COLORS['red'])
        screen.blit(radius_text, (center[0] + radius // 2, center[1] - 20))

        # 绘制直径
        pygame.draw.line(screen, COLORS['green'], center,
                        (center[0] - radius, center[1]), 2)
        pygame.draw.line(screen, COLORS['green'], center,
                        (center[0] + radius, center[1]), 2)

        # 绘制直径文字
        diameter_text = font_small.render("直径 = 2r", True, COLORS['green'])
        screen.blit(diameter_text, (center[0] - 50, center[1] + 20))

        # 计算并显示公式
        area = math.pi * radius ** 2
        perimeter = 2 * math.pi * radius

        formulas = [
            f"半径 (r) = {radius}",
            f"直径 (d) = {2 * radius}",
            f"面积 (A) = π × r² = π × {radius}² = {area:.2f}",
            f"周长 (C) = 2 × π × r = 2 × π × {radius} = {perimeter:.2f}",
        ]

        self.draw_formula_box(formulas)

        # 绘制滑块
        self.sliders['radius'].draw(screen)

    def draw_rectangle_mode(self):
        """绘制矩形模式"""
        self.draw_mode_header("矩形 - Rectangle")

        width = int(self.sliders['width'].value)
        height = int(self.sliders['height'].value)

        # 计算矩形位置（居中显示）
        rect_x = self.center_x - width // 2
        rect_y = self.center_y - height // 2

        # 绘制矩形
        draw_rectangle(screen, (rect_x, rect_y), (width, height), COLORS['green'])
        draw_rectangle(screen, (rect_x, rect_y), (width, height), COLORS['black'], filled=False, width=2)

        # 绘制边长标注
        width_text = font_small.render(f"宽={width}", True, COLORS['red'])
        screen.blit(width_text, (self.center_x - 20, rect_y + height + 10))

        height_text = font_small.render(f"高={height}", True, COLORS['blue'])
        screen.blit(height_text, (rect_x - 50, self.center_y - 10))

        # 绘制对角线
        pygame.draw.line(screen, COLORS['accent'], (rect_x, rect_y),
                        (rect_x + width, rect_y + height), 2)
        pygame.draw.line(screen, COLORS['accent'], (rect_x + width, rect_y),
                        (rect_x, rect_y + height), 2)

        # 计算并显示公式
        area = width * height
        perimeter = 2 * (width + height)
        diagonal = math.sqrt(width ** 2 + height ** 2)

        formulas = [
            f"宽度 (w) = {width}",
            f"高度 (h) = {height}",
            f"面积 (A) = w × h = {width} × {height} = {area}",
            f"周长 (P) = 2(w + h) = 2({width} + {height}) = {perimeter}",
            f"对角线 (d) = √(w² + h²) = {diagonal:.2f}",
        ]

        self.draw_formula_box(formulas)

        # 绘制滑块
        self.sliders['width'].draw(screen)
        self.sliders['height'].draw(screen)

    def draw_triangle_mode(self):
        """绘制三角形模式"""
        self.draw_mode_header("三角形 - Triangle")

        # 定义三角形顶点
        base = int(self.sliders['width'].value)
        height = int(self.sliders['height'].value)

        p1 = (self.center_x, self.center_y - height // 2)
        p2 = (self.center_x - base // 2, self.center_y + height // 2)
        p3 = (self.center_x + base // 2, self.center_y + height // 2)

        # 绘制三角形
        draw_triangle(screen, [p1, p2, p3], COLORS['purple'])
        draw_triangle(screen, [p1, p2, p3], COLORS['black'], filled=False, width=2)

        # 标注顶点
        vertices = ['A', 'B', 'C']
        points = [p1, p2, p3]
        for i, (v, p) in enumerate(zip(vertices, points)):
            text = font_small.render(v, True, COLORS['red'])
            screen.blit(text, (p[0] + 10, p[1] - 20))

        # 绘制高
        height_x = self.center_x
        height_y = self.center_y + height // 2
        pygame.draw.line(screen, COLORS['red'], (height_x, p1[1]), (height_x, height_y), 2)
        pygame.draw.line(screen, COLORS['red'], (height_x - 5, height_y), (height_x + 5, height_y), 2)

        # 计算并显示公式
        # 使用海伦公式计算面积
        a = math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)  # AB边
        b = math.sqrt((p3[0] - p2[0]) ** 2 + (p3[1] - p2[1]) ** 2)  # BC边
        c = math.sqrt((p3[0] - p1[0]) ** 2 + (p3[1] - p1[1]) ** 2)  # AC边

        s = (a + b + c) / 2  # 半周长
        area = math.sqrt(s * (s - a) * (s - b) * (s - c))  # 海伦公式

        perimeter = a + b + c

        formulas = [
            f"底边 (b) = {base:.1f}",
            f"高 (h) = {height:.1f}",
            f"边长: a={a:.1f}, b={b:.1f}, c={c:.1f}",
            f"面积 (A) = (b × h) / 2 = {base * height / 2:.1f}",
            f"周长 (P) = a + b + c = {perimeter:.1f}",
        ]

        self.draw_formula_box(formulas)

        # 绘制滑块
        self.sliders['width'].draw(screen)
        self.sliders['height'].draw(screen)

    def draw_polygon_mode(self):
        """绘制正多边形模式"""
        self.draw_mode_header("正多边形 - Regular Polygon")

        sides = int(self.sliders['sides'].value)
        radius = int(self.sliders['radius'].value)
        rotation = self.sliders['rotation'].value

        # 绘制正多边形
        rotation_rad = math.radians(rotation)
        draw_polygon(screen, (self.center_x, self.center_y), radius, sides,
                    COLORS['accent'], rotation_rad)
        draw_polygon(screen, (self.center_x, self.center_y), radius, sides,
                    COLORS['black'], rotation_rad, filled=False, width=2)

        # 绘制中心点和半径
        pygame.draw.circle(screen, COLORS['red'], (self.center_x, self.center_y), 5)
        pygame.draw.line(screen, COLORS['red'], (self.center_x, self.center_y),
                        (self.center_x + radius, self.center_y), 2)

        # 计算并显示公式
        area = calculate_polygon_area(sides, radius)
        perimeter = calculate_polygon_perimeter(sides, radius)
        interior_angle = (sides - 2) * 180 / sides
        central_angle = 360 / sides

        formulas = [
            f"边数 (n) = {sides}",
            f"半径 (r) = {radius}",
            f"边长 = {2 * radius * math.sin(math.pi / sides):.2f}",
            f"面积 (A) = {area:.2f}",
            f"周长 (P) = {perimeter:.2f}",
            f"内角 = {interior_angle:.1f}°",
            f"中心角 = {central_angle:.1f}°",
        ]

        self.draw_formula_box(formulas)

        # 绘制滑块
        self.sliders['radius'].value = radius
        self.sliders['sides'].draw(screen)
        self.sliders['radius'].draw(screen)
        self.sliders['rotation'].draw(screen)

    def draw_angle_mode(self):
        """绘制角度计算模式"""
        self.draw_mode_header("角度计算 - Angle Calculation")

        # 获取角度值
        angle1_rad = math.radians(self.sliders['angle1'].value)
        angle2_rad = math.radians(self.sliders['angle2'].value)

        center = (self.center_x, self.center_y)
        radius = 150

        # 绘制角度弧
        draw_angle_arc(screen, center, radius, 0, angle1_rad, COLORS['blue'])
        draw_angle_arc(screen, center, radius, 0, angle2_rad, COLORS['red'])

        # 绘制角度标注
        angle1_text = font_medium.render(f"角度1: {self.sliders['angle1'].value:.0f}°", True, COLORS['blue'])
        screen.blit(angle1_text, (self.center_x - 100, self.center_y - 180))

        angle2_text = font_medium.render(f"角度2: {self.sliders['angle2'].value:.0f}°", True, COLORS['red'])
        screen.blit(angle2_text, (self.center_x + 50, self.center_y - 180))

        # 计算并显示公式
        sum_angle = self.sliders['angle1'].value + self.sliders['angle2'].value
        diff_angle = abs(self.sliders['angle1'].value - self.sliders['angle2'].value)

        formulas = [
            f"角度1 = {self.sliders['angle1'].value:.1f}°",
            f"角度2 = {self.sliders['angle2'].value:.1f}°",
            f"和角 = {sum_angle:.1f}°",
            f"差角 = {diff_angle:.1f}°",
            f"弧度1 = {angle1_rad:.4f} rad",
            f"弧度2 = {angle2_rad:.4f} rad",
            f"sin(θ) = 对边/斜边",
            f"cos(θ) = 邻边/斜边",
            f"tan(θ) = 对边/邻边",
        ]

        self.draw_formula_box(formulas)

        # 绘制滑块
        self.sliders['angle1'].draw(screen)
        self.sliders['angle2'].draw(screen)

    def draw_calculator_mode(self):
        """绘制计算器模式"""
        self.draw_mode_header("计算器 - Calculator")

        # 显示输入框
        input_box = pygame.Rect(50, 60, 270, 50)
        pygame.draw.rect(screen, COLORS['white'], input_box, border_radius=5)
        pygame.draw.rect(screen, COLORS['primary'], input_box, 2, border_radius=5)

        # 显示输入值
        display_text = self.input_num1 if self.input_num1 else "0"
        text_surf = font_large.render(display_text, True, COLORS['text'])
        text_rect = text_surf.get_rect(midleft=(input_box.x + 15, input_box.centery))
        screen.blit(text_surf, text_rect)

        # 显示操作符
        op_text = font_medium.render(f"运算: {self.calc_operation}", True, COLORS['primary'])
        screen.blit(op_text, (50, 130))

        # 显示结果
        result_box = pygame.Rect(50, 160, 270, 50)
        pygame.draw.rect(screen, COLORS['light_gray'], result_box, border_radius=5)
        pygame.draw.rect(screen, COLORS['gray'], result_box, 2, border_radius=5)

        result_text = font_large.render(f"= {self.calc_result}" if self.calc_result else "= ", True, COLORS['green'])
        text_rect = result_text.get_rect(midleft=(result_box.x + 15, result_box.centery))
        screen.blit(result_text, text_rect)

        # 绘制按钮
        for button in self.calc_buttons:
            button.draw(screen)

        # 绘制计算公式
        formulas = [
            "数学计算器",
            "支持: + - * / x^2 sqrt",
            "点击按钮进行计算",
        ]

        self.draw_formula_box(formulas, y_offset=300)

    def draw_mode_header(self, title):
        """绘制模式标题"""
        # 标题
        title_surf = font_large.render(title, True, COLORS['primary'])
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2 + 100, 30))
        screen.blit(title_surf, title_rect)

        # 绘制返回按钮
        self.mode_buttons[0].draw(screen)
        self.mode_buttons[1].draw(screen)

    def draw_formula_box(self, formulas, y_offset=180):
        """绘制公式框"""
        box_rect = pygame.Rect(500, y_offset, 450, 400)
        pygame.draw.rect(screen, COLORS['white'], box_rect, border_radius=10)
        pygame.draw.rect(screen, COLORS['secondary'], box_rect, 3, border_radius=10)

        # 标题
        title = font_medium.render("公式与计算", True, COLORS['primary'])
        screen.blit(title, (box_rect.x + 15, box_rect.y + 10))

        # 绘制分隔线
        pygame.draw.line(screen, COLORS['light_gray'], (box_rect.x + 10, box_rect.y + 45),
                        (box_rect.right - 10, box_rect.y + 45), 2)

        # 绘制公式
        for i, formula in enumerate(formulas):
            text_surf = font_small.render(formula, True, COLORS['text'])
            screen.blit(text_surf, (box_rect.x + 15, box_rect.y + 55 + i * 30))

    def handle_menu_events(self, event):
        """处理菜单事件"""
        for i, button in enumerate(self.menu_buttons):
            if button.is_clicked(event.pos):
                if i == 0:
                    self.mode = "circle"
                    self.sliders['radius'].value = 100
                elif i == 1:
                    self.mode = "rectangle"
                    self.sliders['width'].value = 150
                    self.sliders['height'].value = 100
                elif i == 2:
                    self.mode = "triangle"
                    self.sliders['width'].value = 180
                    self.sliders['height'].value = 120
                elif i == 3:
                    self.mode = "polygon"
                    self.sliders['sides'].value = 5
                    self.sliders['radius'].value = 100
                    self.sliders['rotation'].value = 0
                elif i == 4:
                    self.mode = "angle"
                    self.sliders['angle1'].value = 45
                    self.sliders['angle2'].value = 90
                elif i == 5:
                    self.mode = "calculator"
                    self.input_num1 = ""
                    self.input_num2 = ""
                    self.calc_result = ""
                elif i == 6:
                    self.running = False

    def handle_mode_events(self, event):
        """处理模式事件"""
        # 返回菜单
        if self.mode_buttons[0].is_clicked(event.pos):
            self.mode = "menu"
            return

        # 清空
        if self.mode_buttons[1].is_clicked(event.pos):
            if self.mode == "circle":
                self.sliders['radius'].value = 100
            elif self.mode == "rectangle":
                self.sliders['width'].value = 150
                self.sliders['height'].value = 100
            elif self.mode == "triangle":
                self.sliders['width'].value = 180
                self.sliders['height'].value = 120
            elif self.mode == "polygon":
                self.sliders['sides'].value = 5
                self.sliders['radius'].value = 100
                self.sliders['rotation'].value = 0
            elif self.mode == "angle":
                self.sliders['angle1'].value = 45
                self.sliders['angle2'].value = 90

        # 处理计算器按钮
        if self.mode == "calculator":
            self.handle_calculator_events(event)

    def handle_calculator_events(self, event):
        """处理计算器事件"""
        button_labels = ["+", "-", "*", "/", "x^2", "sqrt", "=", "清空"]

        for i, button in enumerate(self.calc_buttons):
            if button.is_clicked(event.pos):
                label = button_labels[i]

                if label == "清空":
                    self.input_num1 = ""
                    self.input_num2 = ""
                    self.calc_result = ""
                elif label == "=":
                    self.calculate()
                elif label == "x^2":
                    try:
                        num = float(self.input_num1) if self.input_num1 else 0
                        self.calc_result = str(num ** 2)
                        self.input_num1 = self.calc_result
                    except ValueError:
                        self.calc_result = "错误"
                elif label == "sqrt":
                    try:
                        num = float(self.input_num1) if self.input_num1 else 0
                        if num >= 0:
                            self.calc_result = str(math.sqrt(num))
                            self.input_num1 = self.calc_result
                        else:
                            self.calc_result = "负数无法开方"
                    except ValueError:
                        self.calc_result = "错误"
                else:
                    self.calc_operation = label
                    self.calc_result = ""

    def calculate(self):
        """执行计算"""
        try:
            num1 = float(self.input_num1) if self.input_num1 else 0
            num2 = float(self.input_num2) if self.input_num2 else 0

            if self.calc_operation == "+":
                result = num1 + num2
            elif self.calc_operation == "-":
                result = num1 - num2
            elif self.calc_operation == "*":
                result = num1 * num2
            elif self.calc_operation == "/":
                if num2 != 0:
                    result = num1 / num2
                else:
                    self.calc_result = "除数不能为0"
                    return

            self.calc_result = str(result)
            self.input_num1 = self.calc_result
            self.input_num2 = ""
        except ValueError:
            self.calc_result = "输入错误"

    def handle_key_events(self, event):
        """处理键盘事件"""
        if self.mode == "calculator":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.input_num1 = self.input_num1[:-1]
                elif event.key == pygame.K_RETURN:
                    self.calculate()
                elif event.key == pygame.K_ESCAPE:
                    self.mode = "menu"
                elif event.unicode.isdigit() or event.unicode == '.':
                    self.input_num1 += event.unicode
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.mode = "menu"

    def update(self):
        """更新游戏状态"""
        # 更新滑块
        for slider in self.sliders.values():
            slider.update(pygame.mouse.get_pos())

        # 旋转动画（正多边形模式）
        if self.mode == "polygon":
            self.sliders['rotation'].value = (self.sliders['rotation'].value + 0.5) % 360

    def draw(self):
        """绘制游戏画面"""
        # 清屏
        screen.fill(COLORS['background'])

        # 绘制网格
        draw_grid(screen)

        # 根据模式绘制不同内容
        if self.mode == "menu":
            self.draw_menu()
        elif self.mode == "circle":
            self.draw_circle_mode()
        elif self.mode == "rectangle":
            self.draw_rectangle_mode()
        elif self.mode == "triangle":
            self.draw_triangle_mode()
        elif self.mode == "polygon":
            self.draw_polygon_mode()
        elif self.mode == "angle":
            self.draw_angle_mode()
        elif self.mode == "calculator":
            self.draw_calculator_mode()

        # 底部提示
        if self.mode != "menu":
            hint = font_small.render("按 ESC 键返回菜单 | 拖动滑块调整参数", True, COLORS['gray'])
            screen.blit(hint, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 30))

    def run(self):
        """运行游戏"""
        while self.running:
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEMOTION:
                    # 更新按钮悬停状态
                    for button in self.menu_buttons:
                        button.check_hover(event.pos)
                    for button in self.mode_buttons:
                        button.check_hover(event.pos)
                    for button in self.calc_buttons:
                        button.check_hover(event.pos)

                    # 更新滑块
                    if self.mode != "menu" and self.mode != "calculator":
                        for slider in self.sliders.values():
                            slider.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.mode == "menu":
                        self.handle_menu_events(event)
                    else:
                        self.handle_mode_events(event)

                self.handle_key_events(event)

            # 更新
            self.update()

            # 绘制
            self.draw()

            # 更新显示
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

# 主函数
def main():
    """主函数"""
    game = GeometryLab()
    game.run()

if __name__ == "__main__":
    main()
