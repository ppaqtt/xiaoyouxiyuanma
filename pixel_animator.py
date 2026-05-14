"""
像素动画制作器 - 在网格上绘制像素图案并创建动画
操作说明：
- 左键绘制像素
- 右键擦除像素
- 中键取色
- 滚轮调整画笔大小
- 左侧面板选择颜色
- 底部按钮：添加帧、删除帧、复制帧、播放/停止动画
- 左右箭头键切换帧
- B键：画笔工具
- E键：橡皮擦工具
- G键：填充工具
"""

import pygame
import sys
import copy

# 初始化pygame
pygame.init()

# 窗口设置
WIDTH, HEIGHT = 1100, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("像素动画制作器 - Pixel Animator")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (220, 220, 220)
BG_COLOR = (35, 35, 50)
PANEL_COLOR = (45, 45, 65)
GRID_BG = (25, 25, 40)
YELLOW = (255, 255, 0)

# 网格设置
GRID_SIZE = 32       # 32x32像素网格
CELL_SIZE = 16       # 每个像素格的大小
GRID_PIXELS = GRID_SIZE * CELL_SIZE  # 网格总像素大小
GRID_LEFT = 200      # 网格左边距
GRID_TOP = 50        # 网格上边距

# 调色板颜色
PALETTE = [
    (0, 0, 0),         # 黑色
    (255, 255, 255),   # 白色
    (255, 0, 0),       # 红色
    (0, 255, 0),       # 绿色
    (0, 0, 255),       # 蓝色
    (255, 255, 0),     # 黄色
    (255, 0, 255),     # 品红
    (0, 255, 255),     # 青色
    (255, 128, 0),     # 橙色
    (128, 0, 255),     # 紫色
    (0, 128, 255),     # 天蓝
    (255, 128, 128),   # 浅红
    (128, 255, 128),   # 浅绿
    (128, 128, 255),   # 浅蓝
    (255, 200, 150),   # 肤色
    (139, 90, 43),     # 棕色
    (128, 128, 128),   # 灰色
    (64, 64, 64),      # 深灰
    (192, 192, 192),   # 银色
    (255, 192, 203),   # 粉色
    (0, 100, 0),       # 深绿
    (0, 0, 128),       # 深蓝
    (128, 0, 0),       # 深红
    (255, 215, 0),     # 金色
]

# 字体
try:
    font_small = pygame.font.SysFont("simhei", 14)
    font_medium = pygame.font.SysFont("simhei", 18)
    font_large = pygame.font.SysFont("simhei", 24)
except:
    font_small = pygame.font.Font(None, 14)
    font_medium = pygame.font.Font(None, 18)
    font_large = pygame.font.Font(None, 24)


class Frame:
    """动画帧"""
    def __init__(self, width=GRID_SIZE, height=GRID_SIZE):
        # 用None表示透明，元组表示颜色
        self.pixels = [[None] * width for _ in range(height)]
        self.width = width
        self.height = height

    def copy(self):
        """复制帧"""
        new_frame = Frame(self.width, self.height)
        new_frame.pixels = copy.deepcopy(self.pixels)
        return new_frame

    def get_pixel(self, x, y):
        """获取像素颜色"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.pixels[y][x]
        return None

    def set_pixel(self, x, y, color):
        """设置像素颜色"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color

    def clear(self):
        """清除所有像素"""
        self.pixels = [[None] * self.width for _ in range(self.height)]


class PixelAnimator:
    """像素动画制作器"""
    def __init__(self):
        self.frames = [Frame()]
        self.current_frame = 0
        self.current_color = (255, 0, 0)
        self.tool = "brush"  # brush, eraser, fill
        self.brush_size = 1
        self.playing = False
        self.play_timer = 0
        self.play_fps = 8
        self.play_frame = 0
        self.drawing = False
        self.last_cell = None
        # 洋葱皮（显示前一帧的半透明图像）
        self.onion_skin = True

    def get_current_frame(self):
        """获取当前帧"""
        return self.frames[self.current_frame]

    def add_frame(self):
        """添加新帧"""
        self.frames.insert(self.current_frame + 1, Frame())
        self.current_frame += 1

    def delete_frame(self):
        """删除当前帧"""
        if len(self.frames) > 1:
            self.frames.pop(self.current_frame)
            if self.current_frame >= len(self.frames):
                self.current_frame = len(self.frames) - 1

    def duplicate_frame(self):
        """复制当前帧"""
        new_frame = self.frames[self.current_frame].copy()
        self.frames.insert(self.current_frame + 1, new_frame)
        self.current_frame += 1

    def prev_frame(self):
        """上一帧"""
        if self.current_frame > 0:
            self.current_frame -= 1

    def next_frame(self):
        """下一帧"""
        if self.current_frame < len(self.frames) - 1:
            self.current_frame += 1

    def flood_fill(self, x, y, new_color):
        """洪水填充算法"""
        frame = self.get_current_frame()
        target_color = frame.get_pixel(x, y)
        if target_color == new_color:
            return

        stack = [(x, y)]
        visited = set()

        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited:
                continue
            if cx < 0 or cx >= frame.width or cy < 0 or cy >= frame.height:
                continue
            if frame.get_pixel(cx, cy) != target_color:
                continue

            visited.add((cx, cy))
            frame.set_pixel(cx, cy, new_color)

            stack.append((cx + 1, cy))
            stack.append((cx - 1, cy))
            stack.append((cx, cy + 1))
            stack.append((cx, cy - 1))

    def paint(self, mx, my):
        """在指定位置绘制"""
        # 计算网格坐标
        gx = (mx - GRID_LEFT) // CELL_SIZE
        gy = (my - GRID_TOP) // CELL_SIZE

        if not (0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE):
            return

        frame = self.get_current_frame()

        if self.tool == "brush":
            # 画笔工具
            for dx in range(self.brush_size):
                for dy in range(self.brush_size):
                    frame.set_pixel(gx + dx, gy + dy, self.current_color)
        elif self.tool == "eraser":
            # 橡皮擦
            for dx in range(self.brush_size):
                for dy in range(self.brush_size):
                    frame.set_pixel(gx + dx, gy + dy, None)
        elif self.tool == "fill":
            # 填充工具
            self.flood_fill(gx, gy, self.current_color)

    def draw_grid(self, surface):
        """绘制像素网格"""
        # 网格背景
        grid_rect = pygame.Rect(GRID_LEFT, GRID_TOP, GRID_PIXELS, GRID_PIXELS)
        pygame.draw.rect(surface, GRID_BG, grid_rect)

        # 棋盘格背景（表示透明区域）
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                px = GRID_LEFT + x * CELL_SIZE
                py = GRID_TOP + y * CELL_SIZE
                if (x + y) % 2 == 0:
                    pygame.draw.rect(surface, (30, 30, 45), (px, py, CELL_SIZE, CELL_SIZE))
                else:
                    pygame.draw.rect(surface, (40, 40, 55), (px, py, CELL_SIZE, CELL_SIZE))

        # 洋葱皮：显示前一帧的半透明内容
        if self.onion_skin and self.current_frame > 0 and not self.playing:
            prev_frame = self.frames[self.current_frame - 1]
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    color = prev_frame.get_pixel(x, y)
                    if color:
                        px = GRID_LEFT + x * CELL_SIZE
                        py = GRID_TOP + y * CELL_SIZE
                        onion_color = tuple(c // 4 for c in color)
                        pygame.draw.rect(surface, onion_color, (px, py, CELL_SIZE, CELL_SIZE))

        # 绘制当前帧的像素
        display_frame = self.frames[self.play_frame] if self.playing else self.get_current_frame()
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                color = display_frame.get_pixel(x, y)
                if color:
                    px = GRID_LEFT + x * CELL_SIZE
                    py = GRID_TOP + y * CELL_SIZE
                    pygame.draw.rect(surface, color, (px, py, CELL_SIZE, CELL_SIZE))

        # 绘制网格线
        for i in range(GRID_SIZE + 1):
            # 竖线
            x = GRID_LEFT + i * CELL_SIZE
            pygame.draw.line(surface, (50, 50, 70), (x, GRID_TOP), (x, GRID_TOP + GRID_PIXELS), 1)
            # 横线
            y = GRID_TOP + i * CELL_SIZE
            pygame.draw.line(surface, (50, 50, 70), (GRID_LEFT, y), (GRID_LEFT + GRID_PIXELS, y), 1)

        # 网格边框
        pygame.draw.rect(surface, GRAY, grid_rect, 2)

    def draw_palette(self, surface):
        """绘制调色板"""
        # 调色板标题
        title = font_medium.render("调色板", True, WHITE)
        surface.blit(title, (15, 10))

        # 颜色格子
        for i, color in enumerate(PALETTE):
            row = i // 4
            col = i % 4
            x = 15 + col * 42
            y = 40 + row * 42
            rect = pygame.Rect(x, y, 38, 38)
            pygame.draw.rect(surface, color, rect)
            # 选中标记
            if color == self.current_color:
                pygame.draw.rect(surface, WHITE, rect, 3)
            else:
                pygame.draw.rect(surface, DARK_GRAY, rect, 1)

        # 当前颜色预览
        preview_y = 310
        preview_label = font_small.render("当前颜色:", True, GRAY)
        surface.blit(preview_label, (15, preview_y))
        pygame.draw.rect(surface, self.current_color, (15, preview_y + 20, 160, 30))
        pygame.draw.rect(surface, WHITE, (15, preview_y + 20, 160, 30), 1)

        # RGB值
        r, g, b = self.current_color
        rgb_text = font_small.render(f"RGB: {r},{g},{b}", True, GRAY)
        surface.blit(rgb_text, (15, preview_y + 55))

    def draw_tools(self, surface):
        """绘制工具栏"""
        tools_y = 400
        title = font_medium.render("工具", True, WHITE)
        surface.blit(title, (15, tools_y))

        tool_info = [
            ("B - 画笔", "brush"),
            ("E - 橡皮擦", "eraser"),
            ("G - 填充", "fill"),
        ]
        for i, (label, tool_id) in enumerate(tool_info):
            y = tools_y + 30 + i * 35
            color = YELLOW if self.tool == tool_id else GRAY
            text = font_small.render(label, True, color)
            surface.blit(text, (15, y))
            if self.tool == tool_id:
                pygame.draw.rect(surface, YELLOW, (12, y - 2, 5, 20))

        # 画笔大小
        size_y = tools_y + 145
        size_text = font_small.render(f"画笔大小: {self.brush_size}", True, GRAY)
        surface.blit(size_text, (15, size_y))
        size_hint = font_small.render("(滚轮调整)", True, DARK_GRAY)
        surface.blit(size_hint, (15, size_y + 20))

    def draw_timeline(self, surface):
        """绘制时间轴"""
        timeline_y = GRID_TOP + GRID_PIXELS + 20

        # 时间轴背景
        timeline_rect = pygame.Rect(GRID_LEFT - 10, timeline_y, GRID_PIXELS + 20, 100)
        pygame.draw.rect(surface, PANEL_COLOR, timeline_rect, border_radius=5)

        # 帧缩略图
        thumb_size = 50
        thumb_gap = 10
        start_x = GRID_LEFT

        for i, frame in enumerate(self.frames):
            x = start_x + i * (thumb_size + thumb_gap)
            y = timeline_y + 10

            # 缩略图背景
            thumb_rect = pygame.Rect(x, y, thumb_size, thumb_size)
            pygame.draw.rect(surface, GRID_BG, thumb_rect)

            # 绘制缩略图内容
            scale = thumb_size / GRID_SIZE
            for py in range(GRID_SIZE):
                for px in range(GRID_SIZE):
                    color = frame.get_pixel(px, py)
                    if color:
                        sx = x + int(px * scale)
                        sy = y + int(py * scale)
                        sw = max(1, int(scale))
                        pygame.draw.rect(surface, color, (sx, sy, sw, sw))

            # 当前帧高亮
            if i == self.current_frame and not self.playing:
                pygame.draw.rect(surface, YELLOW, thumb_rect, 2)
            elif i == self.play_frame and self.playing:
                pygame.draw.rect(surface, GREEN, thumb_rect, 2)
            else:
                pygame.draw.rect(surface, DARK_GRAY, thumb_rect, 1)

            # 帧编号
            num_text = font_small.render(str(i + 1), True, GRAY)
            surface.blit(num_text, (x + thumb_size // 2 - num_text.get_width() // 2, y + thumb_size + 2))

        # 帧信息
        frame_info = font_small.render(
            f"帧 {self.current_frame + 1}/{len(self.frames)}", True, WHITE)
        surface.blit(frame_info, (GRID_LEFT, timeline_y + 75))

    def draw_buttons(self, surface):
        """绘制按钮"""
        btn_y = GRID_TOP + GRID_PIXELS + 130
        buttons_info = [
            ("添加帧", (60, 140, 60)),
            ("删除帧", (140, 60, 60)),
            ("复制帧", (60, 60, 140)),
            ("播放/停止", (140, 140, 60)),
            ("清除帧", (100, 60, 100)),
            ("洋葱皮", (60, 100, 100)),
        ]

        self.button_rects = []
        for i, (text, color) in enumerate(buttons_info):
            x = GRID_LEFT + i * 110
            rect = pygame.Rect(x, btn_y, 100, 32)
            self.button_rects.append(rect)

            # 洋葱皮按钮特殊处理
            if text == "洋葱皮" and self.onion_skin:
                color = (80, 180, 180)

            pygame.draw.rect(surface, color, rect, border_radius=5)
            pygame.draw.rect(surface, WHITE, rect, 1, border_radius=5)
            text_surf = font_small.render(text, True, WHITE)
            surface.blit(text_surf, (rect.centerx - text_surf.get_width() // 2,
                                      rect.centery - text_surf.get_height() // 2))

    def draw_info(self, surface):
        """绘制信息栏"""
        # 标题
        title = font_large.render("像素动画制作器", True, WHITE)
        surface.blit(title, (GRID_LEFT, 10))

        # FPS信息
        fps_text = font_small.render(f"播放速度: {self.play_fps} FPS", True, GRAY)
        surface.blit(fps_text, (GRID_LEFT + 300, 15))

        # 操作提示
        help_texts = [
            "左键绘制 | 右键擦除 | 中键取色 | 滚轮画笔大小",
            "B画笔 E橡皮 G填充 | 方向键切换帧 | 空格播放"
        ]
        for i, text in enumerate(help_texts):
            surf = font_small.render(text, True, DARK_GRAY)
            surface.blit(surf, (GRID_LEFT + 500, 10 + i * 18))

    def handle_button_click(self, pos):
        """处理按钮点击"""
        if not hasattr(self, 'button_rects'):
            return

        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(pos):
                if i == 0:  # 添加帧
                    self.add_frame()
                elif i == 1:  # 删除帧
                    self.delete_frame()
                elif i == 2:  # 复制帧
                    self.duplicate_frame()
                elif i == 3:  # 播放/停止
                    self.playing = not self.playing
                    if self.playing:
                        self.play_frame = 0
                        self.play_timer = pygame.time.get_ticks()
                elif i == 4:  # 清除帧
                    self.get_current_frame().clear()
                elif i == 5:  # 洋葱皮
                    self.onion_skin = not self.onion_skin
                return True
        return False

    def handle_palette_click(self, pos):
        """处理调色板点击"""
        for i, color in enumerate(PALETTE):
            row = i // 4
            col = i % 4
            x = 15 + col * 42
            y = 40 + row * 42
            rect = pygame.Rect(x, y, 38, 38)
            if rect.collidepoint(pos):
                self.current_color = color
                return True
        return False

    def update_playback(self):
        """更新动画播放"""
        if not self.playing:
            return

        now = pygame.time.get_ticks()
        interval = 1000 // self.play_fps
        if now - self.play_timer >= interval:
            self.play_frame = (self.play_frame + 1) % len(self.frames)
            self.play_timer = now


def main():
    clock = pygame.time.Clock()
    animator = PixelAnimator()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_b:
                    animator.tool = "brush"
                elif event.key == pygame.K_e:
                    animator.tool = "eraser"
                elif event.key == pygame.K_g:
                    animator.tool = "fill"
                elif event.key == pygame.K_LEFT:
                    if not animator.playing:
                        animator.prev_frame()
                elif event.key == pygame.K_RIGHT:
                    if not animator.playing:
                        animator.next_frame()
                elif event.key == pygame.K_SPACE:
                    animator.playing = not animator.playing
                    if animator.playing:
                        animator.play_frame = 0
                        animator.play_timer = pygame.time.get_ticks()
                elif event.key == pygame.K_UP:
                    animator.play_fps = min(30, animator.play_fps + 1)
                elif event.key == pygame.K_DOWN:
                    animator.play_fps = max(1, animator.play_fps - 1)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                # 检查按钮
                if animator.handle_button_click(pos):
                    continue

                # 检查调色板
                if animator.handle_palette_click(pos):
                    continue

                # 检查网格区域
                grid_rect = pygame.Rect(GRID_LEFT, GRID_TOP, GRID_PIXELS, GRID_PIXELS)
                if grid_rect.collidepoint(pos) and not animator.playing:
                    if event.button == 1:  # 左键绘制
                        animator.drawing = True
                        animator.paint(*pos)
                        animator.last_cell = ((pos[0] - GRID_LEFT) // CELL_SIZE,
                                              (pos[1] - GRID_TOP) // CELL_SIZE)
                    elif event.button == 3:  # 右键擦除
                        old_tool = animator.tool
                        animator.tool = "eraser"
                        animator.paint(*pos)
                        animator.tool = old_tool
                    elif event.button == 2:  # 中键取色
                        gx = (pos[0] - GRID_LEFT) // CELL_SIZE
                        gy = (pos[1] - GRID_TOP) // CELL_SIZE
                        color = animator.get_current_frame().get_pixel(gx, gy)
                        if color:
                            animator.current_color = color

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    animator.drawing = False
                    animator.last_cell = None

            elif event.type == pygame.MOUSEMOTION:
                if animator.drawing and not animator.playing:
                    pos = event.pos
                    grid_rect = pygame.Rect(GRID_LEFT, GRID_TOP, GRID_PIXELS, GRID_PIXELS)
                    if grid_rect.collidepoint(pos):
                        animator.paint(*pos)

            elif event.type == pygame.MOUSEWHEEL:
                animator.brush_size = max(1, min(8, animator.brush_size + event.y))

        # 更新播放
        animator.update_playback()

        # 绘制
        screen.fill(BG_COLOR)
        animator.draw_grid(screen)
        animator.draw_palette(screen)
        animator.draw_tools(screen)
        animator.draw_timeline(screen)
        animator.draw_buttons(screen)
        animator.draw_info(screen)

        # 播放指示
        if animator.playing:
            play_text = font_medium.render("播放中...", True, (100, 255, 100))
            screen.blit(play_text, (GRID_LEFT + GRID_PIXELS - 100, 15))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
