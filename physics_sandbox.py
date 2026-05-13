"""
物理沙盒 - 放置物体并观察物理效果
操作说明：
- 右键点击：添加物体（圆形/方形/三角形循环切换）
- 左键拖拽：拖拽物体
- 滚轮：调整重力大小
- 方向键：调整重力方向
- C键：清除所有物体
- R键：重置重力
- 1/2/3键：选择要放置的形状（圆/方/三角）
"""

import pygame
import math
import random
import sys

# 初始化pygame
pygame.init()

# 窗口设置
WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("物理沙盒 - Physics Sandbox")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (60, 60, 60)
BG_COLOR = (25, 25, 45)
PANEL_COLOR = (35, 35, 55)

# 物体颜色
COLORS = [
    (255, 100, 100), (100, 255, 100), (100, 100, 255),
    (255, 255, 100), (255, 100, 255), (100, 255, 255),
    (255, 180, 80), (180, 100, 255), (100, 255, 180),
]

# 字体
try:
    font_small = pygame.font.SysFont("simhei", 16)
    font_medium = pygame.font.SysFont("simhei", 22)
    font_large = pygame.font.SysFont("simhei", 28)
except:
    font_small = pygame.font.Font(None, 16)
    font_medium = pygame.font.Font(None, 22)
    font_large = pygame.font.Font(None, 28)


class PhysicsBody:
    """物理物体基类"""
    def __init__(self, x, y, shape="circle", size=25):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.shape = shape  # circle, square, triangle
        self.size = size
        self.mass = size * size * 0.01
        self.restitution = 0.6  # 弹性系数
        self.friction = 0.98
        self.color = random.choice(COLORS)
        self.angle = 0.0  # 旋转角度
        self.angular_vel = 0.0
        self.dragging = False

    def update(self, gravity, dt):
        """更新物理状态"""
        if self.dragging:
            return

        # 应用重力
        self.vx += gravity[0] * dt
        self.vy += gravity[1] * dt

        # 应用摩擦力
        self.vx *= self.friction
        self.vy *= self.friction

        # 更新位置
        self.x += self.vx * dt
        self.y += self.vy * dt

        # 更新旋转
        self.angular_vel *= 0.99
        self.angle += self.angular_vel * dt

        # 边界碰撞
        self.handle_boundaries()

    def handle_boundaries(self):
        """处理边界碰撞"""
        # 地面
        if self.y + self.size > HEIGHT - 10:
            self.y = HEIGHT - 10 - self.size
            self.vy = -self.vy * self.restitution
            self.angular_vel += self.vx * 0.01
            if abs(self.vy) < 1:
                self.vy = 0

        # 天花板
        if self.y - self.size < 10:
            self.y = 10 + self.size
            self.vy = -self.vy * self.restitution

        # 左墙
        if self.x - self.size < 10:
            self.x = 10 + self.size
            self.vx = -self.vx * self.restitution

        # 右墙
        if self.x + self.size > WIDTH - 10:
            self.x = WIDTH - 10 - self.size
            self.vx = -self.vx * self.restitution

    def draw(self, surface):
        """绘制物体"""
        if self.shape == "circle":
            self.draw_circle(surface)
        elif self.shape == "square":
            self.draw_square(surface)
        elif self.shape == "triangle":
            self.draw_triangle(surface)

    def draw_circle(self, surface):
        """绘制圆形"""
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        # 高光效果
        highlight_color = tuple(min(255, c + 60) for c in self.color)
        pygame.draw.circle(surface, highlight_color,
            (int(self.x - self.size * 0.3), int(self.y - self.size * 0.3)),
            max(2, self.size // 4))
        # 边框
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.size, 2)

    def draw_square(self, surface):
        """绘制方形（带旋转）"""
        corners = []
        for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
            rx = dx * self.size
            ry = dy * self.size
            # 旋转
            cos_a = math.cos(self.angle)
            sin_a = math.sin(self.angle)
            nx = rx * cos_a - ry * sin_a + self.x
            ny = rx * sin_a + ry * cos_a + self.y
            corners.append((nx, ny))
        pygame.draw.polygon(surface, self.color, corners)
        pygame.draw.polygon(surface, WHITE, corners, 2)

    def draw_triangle(self, surface):
        """绘制三角形（带旋转）"""
        corners = []
        for i in range(3):
            a = self.angle + i * 2 * math.pi / 3 - math.pi / 2
            rx = math.cos(a) * self.size
            ry = math.sin(a) * self.size
            corners.append((self.x + rx, self.y + ry))
        pygame.draw.polygon(surface, self.color, corners)
        pygame.draw.polygon(surface, WHITE, corners, 2)

    def contains_point(self, px, py):
        """检测点是否在物体内部"""
        dist = math.sqrt((px - self.x) ** 2 + (py - self.y) ** 2)
        return dist <= self.size + 5


def check_collision(a, b):
    """检测两个物体之间的碰撞"""
    dx = b.x - a.x
    dy = b.y - a.y
    dist = math.sqrt(dx * dx + dy * dy)
    min_dist = a.size + b.size

    if dist < min_dist and dist > 0:
        # 法线方向
        nx = dx / dist
        ny = dy / dist

        # 分离物体
        overlap = min_dist - dist
        total_mass = a.mass + b.mass
        if not a.dragging:
            a.x -= nx * overlap * (b.mass / total_mass)
            a.y -= ny * overlap * (b.mass / total_mass)
        if not b.dragging:
            b.x += nx * overlap * (a.mass / total_mass)
            b.y += ny * overlap * (a.mass / total_mass)

        # 相对速度
        dvx = a.vx - b.vx
        dvy = a.vy - b.vy
        dvn = dvx * nx + dvy * ny

        # 只在物体靠近时处理碰撞
        if dvn > 0:
            # 弹性碰撞
            restitution = min(a.restitution, b.restitution)
            impulse = (1 + restitution) * dvn / total_mass

            if not a.dragging:
                a.vx -= impulse * b.mass * nx
                a.vy -= impulse * b.mass * ny
                a.angular_vel += dvn * 0.01
            if not b.dragging:
                b.vx += impulse * a.mass * nx
                b.vy += impulse * a.mass * ny
                b.angular_vel -= dvn * 0.01


class Button:
    """UI按钮"""
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover = False

    def draw(self, surface):
        color = tuple(min(255, c + 30) for c in self.color) if self.hover else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, WHITE, self.rect, 1, border_radius=6)
        text_surf = font_small.render(self.text, True, WHITE)
        surface.blit(text_surf, (self.rect.centerx - text_surf.get_width() // 2,
                                  self.rect.centery - text_surf.get_height() // 2))

    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def main():
    clock = pygame.time.Clock()
    bodies = []
    gravity = [0, 500]  # 重力向量（像素/秒^2）
    current_shape = "circle"  # 当前选择的形状
    dragging_body = None
    drag_offset = (0, 0)
    paused = False

    # 创建UI按钮
    btn_circle = Button(15, 10, 70, 35, "圆形(1)", (180, 60, 60))
    btn_square = Button(95, 10, 70, 35, "方形(2)", (60, 60, 180))
    btn_triangle = Button(175, 10, 80, 35, "三角(3)", (60, 180, 60))
    btn_clear = Button(270, 10, 70, 35, "清除(C)", (150, 60, 60))
    btn_reset_g = Button(350, 10, 80, 35, "重置重力(R)", (100, 100, 60))
    btn_pause = Button(445, 10, 70, 35, "暂停", (100, 100, 100))
    buttons = [btn_circle, btn_square, btn_triangle, btn_clear, btn_reset_g, btn_pause]

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.02)  # 限制最大时间步长
        mouse_pos = pygame.mouse.get_pos()

        # 更新按钮悬停状态
        for btn in buttons:
            btn.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                if event.button == 1:  # 左键
                    # 检查按钮
                    if btn_circle.is_clicked(pos):
                        current_shape = "circle"
                    elif btn_square.is_clicked(pos):
                        current_shape = "square"
                    elif btn_triangle.is_clicked(pos):
                        current_shape = "triangle"
                    elif btn_clear.is_clicked(pos):
                        bodies.clear()
                    elif btn_reset_g.is_clicked(pos):
                        gravity = [0, 500]
                    elif btn_pause.is_clicked(pos):
                        paused = not paused
                        btn_pause.text = "继续" if paused else "暂停"
                    else:
                        # 检查是否点击了物体（拖拽）
                        for body in reversed(bodies):
                            if body.contains_point(*pos):
                                dragging_body = body
                                body.dragging = True
                                drag_offset = (body.x - pos[0], body.y - pos[1])
                                break

                elif event.button == 3:  # 右键添加物体
                    # 避免在按钮区域添加
                    if pos[1] > 55:
                        size = random.randint(15, 35)
                        body = PhysicsBody(pos[0], pos[1], current_shape, size)
                        bodies.append(body)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging_body:
                    dragging_body.dragging = False
                    dragging_body = None

            elif event.type == pygame.MOUSEMOTION:
                if dragging_body:
                    dragging_body.x = event.pos[0] + drag_offset[0]
                    dragging_body.y = event.pos[1] + drag_offset[1]
                    dragging_body.vx = 0
                    dragging_body.vy = 0

            elif event.type == pygame.MOUSEWHEEL:
                # 滚轮调整重力大小
                g_mag = math.sqrt(gravity[0] ** 2 + gravity[1] ** 2)
                if g_mag > 0:
                    scale = 1.1 if event.y > 0 else 0.9
                    gravity[0] *= scale
                    gravity[1] *= scale
                    # 限制范围
                    g_mag = math.sqrt(gravity[0] ** 2 + gravity[1] ** 2)
                    if g_mag > 2000:
                        gravity[0] = gravity[0] / g_mag * 2000
                        gravity[1] = gravity[1] / g_mag * 2000
                    elif g_mag < 0:
                        gravity = [0, 0]

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    bodies.clear()
                elif event.key == pygame.K_r:
                    gravity = [0, 500]
                elif event.key == pygame.K_1:
                    current_shape = "circle"
                elif event.key == pygame.K_2:
                    current_shape = "square"
                elif event.key == pygame.K_3:
                    current_shape = "triangle"
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    btn_pause.text = "继续" if paused else "暂停"
                elif event.key == pygame.K_LEFT:
                    gravity[0] -= 100
                elif event.key == pygame.K_RIGHT:
                    gravity[0] += 100
                elif event.key == pygame.K_UP:
                    gravity[1] -= 100
                elif event.key == pygame.K_DOWN:
                    gravity[1] += 100

        # 物理更新
        if not paused:
            # 更新物体
            for body in bodies:
                body.update(gravity, dt)

            # 碰撞检测
            for i in range(len(bodies)):
                for j in range(i + 1, len(bodies)):
                    if not bodies[i].dragging or not bodies[j].dragging:
                        check_collision(bodies[i], bodies[j])

        # 绘制
        screen.fill(BG_COLOR)

        # 绘制边界
        pygame.draw.rect(screen, DARK_GRAY, (0, 0, WIDTH, HEIGHT), 10, border_radius=5)

        # 绘制重力方向指示器
        center_x, center_y = WIDTH - 60, 60
        g_mag = math.sqrt(gravity[0] ** 2 + gravity[1] ** 2)
        if g_mag > 0:
            arrow_len = min(40, g_mag / 50)
            end_x = center_x + gravity[0] / g_mag * arrow_len
            end_y = center_y + gravity[1] / g_mag * arrow_len
            pygame.draw.circle(screen, DARK_GRAY, (center_x, center_y), 45)
            pygame.draw.circle(screen, GRAY, (center_x, center_y), 45, 1)
            pygame.draw.line(screen, YELLOW, (center_x, center_y), (int(end_x), int(end_y)), 3)
            # 箭头头部
            angle = math.atan2(gravity[1], gravity[0])
            for da in [2.5, -2.5]:
                ax = end_x - 10 * math.cos(angle + da)
                ay = end_y - 10 * math.sin(angle + da)
                pygame.draw.line(screen, YELLOW, (int(end_x), int(end_y)), (int(ax), int(ay)), 2)

        g_label = font_small.render(f"G={g_mag:.0f}", True, GRAY)
        screen.blit(g_label, (WIDTH - 90, 110))

        # 绘制所有物体
        for body in bodies:
            body.draw(screen)

        # 绘制UI面板
        panel_rect = pygame.Rect(0, 0, WIDTH, 50)
        pygame.draw.rect(screen, PANEL_COLOR, panel_rect)
        pygame.draw.line(screen, GRAY, (0, 50), (WIDTH, 50), 1)

        # 绘制按钮
        for btn in buttons:
            btn.draw(screen)

        # 当前形状指示
        shape_names = {"circle": "圆形", "square": "方形", "triangle": "三角形"}
        shape_text = font_small.render(f"当前: {shape_names[current_shape]}", True, YELLOW)
        screen.blit(shape_text, (540, 18))

        # 物体数量
        count_text = font_small.render(f"物体: {len(bodies)}", True, GRAY)
        screen.blit(count_text, (680, 18))

        # 操作提示
        help_text = font_small.render("右键添加 | 左键拖拽 | 滚轮重力大小 | 方向键重力方向", True, GRAY)
        screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, HEIGHT - 25))

        # 暂停指示
        if paused:
            pause_surf = font_large.render("已暂停", True, YELLOW)
            screen.blit(pause_surf, (WIDTH // 2 - pause_surf.get_width() // 2, HEIGHT // 2 - 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
