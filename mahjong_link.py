#!/usr/bin/env python3
"""
连连看麻将版 - 麻将图案的连连看游戏
用不同中文字符代表不同麻将牌，找到相同的一对消除
路径最多转弯2次
"""

import pygame
import sys
import random
import math
from collections import deque

# 初始化pygame
pygame.init()

# 屏幕设置
WIDTH, HEIGHT = 800, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("连连看麻将版 - 点击相同牌消除")

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
GREEN = (50, 180, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 220, 50)
DARK_BG = (30, 60, 40)
TABLE_COLOR = (40, 90, 55)
TILE_BG = (245, 235, 220)
TILE_BORDER = (180, 160, 130)
TILE_SHADOW = (20, 40, 25)
TILE_HOVER = (255, 248, 230)
SELECTED_COLOR = (255, 200, 50)
PATH_COLOR = (255, 255, 100)
HINT_COLOR = (100, 255, 100)
GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)

# 麻将牌定义（中文字符）
MAHJONG_TILES = [
    ("一万", RED), ("二万", RED), ("三万", RED), ("四万", RED),
    ("五万", RED), ("六万", RED), ("七万", RED), ("八万", RED), ("九万", RED),
    ("一筒", BLUE), ("二筒", BLUE), ("三筒", BLUE), ("四筒", BLUE),
    ("五筒", BLUE), ("六筒", BLUE), ("七筒", BLUE), ("八筒", BLUE), ("九筒", BLUE),
    ("一条", GREEN), ("二条", GREEN), ("三条", GREEN), ("四条", GREEN),
    ("五条", GREEN), ("六条", GREEN), ("七条", GREEN), ("八条", GREEN), ("九条", GREEN),
    ("东", (200, 50, 50)), ("南", (200, 50, 50)),
    ("西", (200, 50, 50)), ("北", (200, 50, 50)),
    ("中", RED), ("发", GREEN), ("白", GRAY),
]

# 游戏网格参数
ROWS = 8       # 行数
COLS = 10      # 列数
TILE_W = 65    # 牌宽度
TILE_H = 50    # 牌高度
MARGIN_X = 50  # 左右边距
MARGIN_Y = 80  # 上边距
GAP = 4        # 牌间距

# 字体
font_large = pygame.font.SysFont("simhei", 38, bold=True)
font_medium = pygame.font.SysFont("simhei", 24)
font_small = pygame.font.SysFont("simhei", 18)
font_tile = pygame.font.SysFont("simhei", 22, bold=True)
font_tile_small = pygame.font.SysFont("simhei", 16)


class MahjongLink:
    """连连看麻将版游戏主类"""

    def __init__(self):
        self.state = "menu"  # menu, playing, win
        self.grid = []       # 游戏网格 (ROWS x COLS)，0表示空
        self.selected = None  # 当前选中的牌 (row, col)
        self.score = 0
        self.pairs_left = 0
        self.path = []       # 连接路径（用于动画显示）
        self.path_timer = 0
        self.hint_pair = None
        self.hint_timer = 0
        self.combo = 0
        self.combo_timer = 0
        self.particles = []
        self.time_elapsed = 0
        self.start_ticks = 0
        self.no_match = False  # 是否无解

    def reset_game(self):
        """重置游戏"""
        self.grid = [[0] * COLS for _ in range(ROWS)]
        self.selected = None
        self.score = 0
        self.path = []
        self.path_timer = 0
        self.hint_pair = None
        self.hint_timer = 0
        self.combo = 0
        self.combo_timer = 0
        self.particles = []
        self.no_match = False

        # 生成牌对
        total_tiles = ROWS * COLS
        num_pairs = total_tiles // 2

        # 随机选择麻将牌类型
        available = list(range(len(MAHJONG_TILES)))
        random.shuffle(available)

        tiles = []
        for i in range(num_pairs):
            tile_type = available[i % len(available)]
            tiles.append(tile_type + 1)  # +1 因为0表示空
            tiles.append(tile_type + 1)

        random.shuffle(tiles)

        # 填入网格
        idx = 0
        for r in range(ROWS):
            for c in range(COLS):
                self.grid[r][c] = tiles[idx]
                idx += 1

        self.pairs_left = num_pairs
        self.start_ticks = pygame.time.get_ticks()
        self.state = "playing"

        # 确保有解
        if not self.find_any_match():
            self.reset_game()

    def get_tile_rect(self, row, col):
        """获取牌的屏幕矩形"""
        x = MARGIN_X + col * (TILE_W + GAP)
        y = MARGIN_Y + row * (TILE_H + GAP)
        return pygame.Rect(x, y, TILE_W, TILE_H)

    def get_tile_center(self, row, col):
        """获取牌的中心坐标"""
        rect = self.get_tile_rect(row, col)
        return rect.centerx, rect.centery

    def can_connect(self, r1, c1, r2, c2):
        """
        检查两个牌是否可以通过最多2次转弯的路径连接
        返回路径点列表，如果不可连接返回None
        路径可以经过网格外围（row=-1, row=ROWS, col=-1, col=COLS）
        """
        if self.grid[r1][c1] != self.grid[r2][c2] or (r1, c1) == (r2, c2):
            return None

        # 扩展网格，允许路径经过外围
        # 扩展范围：上-1行，下ROWS行，左-1列，右COLS列
        def is_free(r, c):
            """检查位置是否可通行（空或外围）"""
            if r < -1 or r > ROWS or c < -1 or c > COLS:
                return False
            if r == -1 or r == ROWS or c == -1 or c == COLS:
                return True  # 外围可通行
            if (r, c) == (r1, c1) or (r, c) == (r2, c2):
                return True  # 起点和终点可通行
            return self.grid[r][c] == 0

        def line_clear(r1, c1, r2, c2):
            """检查两点之间直线是否畅通（必须同行或同列）"""
            if r1 == r2:
                min_c, max_c = min(c1, c2), max(c1, c2)
                for c in range(min_c + 1, max_c):
                    if not is_free(r1, c):
                        return False
                return True
            elif c1 == c2:
                min_r, max_r = min(r1, r2), max(r1, r2)
                for r in range(min_r + 1, max_r):
                    if not is_free(r, c1):
                        return False
                return True
            return False

        # 0次转弯：直线连接
        if (r1 == r2 or c1 == c2) and line_clear(r1, c1, r2, c2):
            return [(r1, c1), (r2, c2)]

        # 1次转弯：经过一个拐点
        # 拐点1: (r1, c2)
        if is_free(r1, c2) and line_clear(r1, c1, r1, c2) and line_clear(r1, c2, r2, c2):
            return [(r1, c1), (r1, c2), (r2, c2)]
        # 拐点2: (r2, c1)
        if is_free(r2, c1) and line_clear(r1, c1, r2, c1) and line_clear(r2, c1, r2, c2):
            return [(r1, c1), (r2, c1), (r2, c2)]

        # 2次转弯：经过两个拐点
        # 水平扫描：从每一行找可能的中间水平线
        for r in range(-1, ROWS + 1):
            if r == r1 and r == r2:
                continue
            p1 = (r, c1)
            p2 = (r, c2)
            if (is_free(r, c1) and is_free(r, c2) and
                    line_clear(r1, c1, r, c1) and
                    line_clear(r, c1, r, c2) and
                    line_clear(r, c2, r2, c2)):
                return [(r1, c1), (r, c1), (r, c2), (r2, c2)]

        # 垂直扫描：从每一列找可能的中间垂直线
        for c in range(-1, COLS + 1):
            if c == c1 and c == c2:
                continue
            p1 = (r1, c)
            p2 = (r2, c)
            if (is_free(r1, c) and is_free(r2, c) and
                    line_clear(r1, c1, r1, c) and
                    line_clear(r1, c, r2, c) and
                    line_clear(r2, c, r2, c2)):
                return [(r1, c1), (r1, c), (r2, c), (r2, c2)]

        return None

    def find_any_match(self):
        """查找任意一对可消除的牌"""
        tiles = []
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] > 0:
                    tiles.append((r, c))

        for i in range(len(tiles)):
            for j in range(i + 1, len(tiles)):
                r1, c1 = tiles[i]
                r2, c2 = tiles[j]
                if self.grid[r1][c1] == self.grid[r2][c2]:
                    path = self.can_connect(r1, c1, r2, c2)
                    if path is not None:
                        return (r1, c1, r2, c2)
        return None

    def shuffle_tiles(self):
        """重新洗牌（保留剩余的牌）"""
        remaining = []
        positions = []
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] > 0:
                    remaining.append(self.grid[r][c])
                    positions.append((r, c))

        random.shuffle(remaining)
        for i, (r, c) in enumerate(positions):
            self.grid[r][c] = remaining[i]

        self.selected = None
        self.hint_pair = None
        self.hint_timer = 0

        # 洗牌后仍无解则再洗
        if remaining and not self.find_any_match():
            self.shuffle_tiles()

    def create_particles(self, x, y, color, count=8):
        """创建消除粒子"""
        for _ in range(count):
            self.particles.append({
                'x': x, 'y': y,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-4, -1),
                'life': random.randint(20, 40),
                'max_life': 40,
                'color': color,
                'size': random.randint(2, 5)
            })

    def handle_input(self, event):
        """处理输入"""
        if event.type == pygame.KEYDOWN:
            if self.state == "menu":
                if event.key == pygame.K_RETURN:
                    self.reset_game()
            elif self.state == "playing":
                if event.key == pygame.K_h:
                    # 提示
                    match = self.find_any_match()
                    if match:
                        self.hint_pair = (match[0], match[1], match[2], match[3])
                        self.hint_timer = 90
                elif event.key == pygame.K_s:
                    # 洗牌
                    self.shuffle_tiles()
                    self.score = max(0, self.score - 50)
                elif event.key == pygame.K_r:
                    self.reset_game()
            elif self.state == "win":
                if event.key == pygame.K_RETURN:
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"

        if self.state == "playing" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # 检查点击了哪个牌
            for r in range(ROWS):
                for c in range(COLS):
                    if self.grid[r][c] > 0:
                        rect = self.get_tile_rect(r, c)
                        if rect.collidepoint(mx, my):
                            self.on_tile_click(r, c)
                            return

    def on_tile_click(self, row, col):
        """处理牌点击"""
        if self.path_timer > 0:
            return  # 路径动画中不处理点击

        if self.selected is None:
            self.selected = (row, col)
        elif self.selected == (row, col):
            self.selected = None  # 取消选择
        else:
            sr, sc = self.selected
            # 尝试连接
            path = self.can_connect(sr, sc, row, col)
            if path is not None:
                # 消除成功
                self.path = path
                self.path_timer = 25

                # 获取牌类型用于粒子颜色
                tile_type = self.grid[sr][sc] - 1
                color = MAHJONG_TILES[tile_type][1]

                # 创建粒子
                cx1, cy1 = self.get_tile_center(sr, sc)
                cx2, cy2 = self.get_tile_center(row, col)
                self.create_particles(cx1, cy1, color, 10)
                self.create_particles(cx2, cy2, color, 10)

                # 消除牌
                self.grid[sr][sc] = 0
                self.grid[row][col] = 0
                self.pairs_left -= 1

                # 连击
                self.combo += 1
                self.combo_timer = 60

                # 计分
                base_score = 10
                combo_bonus = min(self.combo, 10) * 5
                self.score += base_score + combo_bonus

                self.selected = None
                self.hint_pair = None
                self.hint_timer = 0

                # 检查是否胜利
                if self.pairs_left <= 0:
                    self.state = "win"
                else:
                    # 检查是否有解
                    if not self.find_any_match():
                        self.no_match = True
            else:
                # 无法连接，选择新的牌
                self.selected = (row, col)
                self.combo = 0

    def update(self):
        """更新游戏逻辑"""
        if self.state == "playing":
            self.time_elapsed = (pygame.time.get_ticks() - self.start_ticks) / 1000

        if self.path_timer > 0:
            self.path_timer -= 1
            if self.path_timer <= 0:
                self.path = []

        if self.hint_timer > 0:
            self.hint_timer -= 1
            if self.hint_timer <= 0:
                self.hint_pair = None

        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo = 0

        # 更新粒子
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.15
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)

    def draw(self, surface):
        """绘制游戏画面"""
        surface.fill(DARK_BG)

        if self.state == "menu":
            self.draw_menu(surface)
        elif self.state == "playing":
            self.draw_game(surface)
        elif self.state == "win":
            self.draw_game(surface)
            self.draw_win(surface)

    def draw_menu(self, surface):
        """绘制菜单"""
        title = font_large.render("连连看麻将", True, WHITE)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        subtitle = font_medium.render("Mahjong Link", True, YELLOW)
        surface.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 130))

        pygame.draw.line(surface, YELLOW, (250, 170), (550, 170), 2)

        # 展示一些麻将牌
        sample_tiles = [0, 9, 18, 27, 31, 32, 33]
        for i, idx in enumerate(sample_tiles):
            x = WIDTH // 2 - len(sample_tiles) * 35 + i * 70
            y = 200
            self.draw_single_tile(surface, x, y, MAHJONG_TILES[idx], False, False)

        instructions = [
            "点击两个相同的麻将牌消除它们",
            "连接路径最多只能转弯2次",
            "路径可以经过棋盘边缘",
            "",
            "H - 提示（扣20分）",
            "S - 洗牌（扣50分）",
            "R - 重新开始",
            "",
            "按 Enter 开始游戏"
        ]
        for i, text in enumerate(instructions):
            color = YELLOW if "Enter" in text else LIGHT_GRAY if text else WHITE
            t = font_small.render(text, True, color)
            surface.blit(t, (WIDTH // 2 - t.get_width() // 2, 310 + i * 30))

    def draw_game(self, surface):
        """绘制游戏画面"""
        # 桌面背景
        table_rect = pygame.Rect(MARGIN_X - 15, MARGIN_Y - 15,
                                 COLS * (TILE_W + GAP) + 30 - GAP,
                                 ROWS * (TILE_H + GAP) + 30 - GAP)
        pygame.draw.rect(surface, TABLE_COLOR, table_rect, border_radius=10)
        pygame.draw.rect(surface, (60, 120, 75), table_rect, 2, border_radius=10)

        # 绘制连接路径
        if self.path and self.path_timer > 0:
            self.draw_path(surface)

        # 绘制所有牌
        mx, my = pygame.mouse.get_pos()
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] > 0:
                    rect = self.get_tile_rect(r, c)
                    is_selected = self.selected == (r, c)
                    is_hover = rect.collidepoint(mx, my) and not is_selected
                    is_hint = (self.hint_pair and
                               (r, c) == (self.hint_pair[0], self.hint_pair[1]) or
                               (r, c) == (self.hint_pair[2], self.hint_pair[3]))

                    tile_type = self.grid[r][c] - 1
                    tile_info = MAHJONG_TILES[tile_type]

                    # 阴影
                    shadow_rect = rect.move(3, 3)
                    pygame.draw.rect(surface, TILE_SHADOW, shadow_rect, border_radius=5)

                    # 牌面
                    bg_color = TILE_HOVER if is_hover else TILE_BG
                    pygame.draw.rect(surface, bg_color, rect, border_radius=5)

                    # 边框
                    if is_hint and self.hint_timer % 10 < 5:
                        pygame.draw.rect(surface, HINT_COLOR, rect, 3, border_radius=5)
                    elif is_selected:
                        pygame.draw.rect(surface, SELECTED_COLOR, rect, 3, border_radius=5)
                    else:
                        pygame.draw.rect(surface, TILE_BORDER, rect, 1, border_radius=5)

                    # 牌面文字
                    text = font_tile.render(tile_info[0], True, tile_info[1])
                    surface.blit(text, (rect.centerx - text.get_width() // 2,
                                        rect.centery - text.get_height() // 2))

        # 绘制粒子
        for p in self.particles:
            alpha = p['life'] / p['max_life']
            size = max(1, int(p['size'] * alpha))
            pygame.draw.circle(surface, p['color'], (int(p['x']), int(p['y'])), size)

        # 绘制UI
        self.draw_ui(surface)

    def draw_single_tile(self, surface, x, y, tile_info, selected, hover):
        """绘制单个麻将牌（用于菜单展示）"""
        rect = pygame.Rect(x, y, TILE_W, TILE_H)
        pygame.draw.rect(surface, TILE_SHADOW, rect.move(2, 2), border_radius=5)
        bg = TILE_HOVER if hover else TILE_BG
        pygame.draw.rect(surface, bg, rect, border_radius=5)
        border_color = SELECTED_COLOR if selected else TILE_BORDER
        pygame.draw.rect(surface, border_color, rect, 2, border_radius=5)
        text = font_tile.render(tile_info[0], True, tile_info[1])
        surface.blit(text, (rect.centerx - text.get_width() // 2,
                            rect.centery - text.get_height() // 2))

    def draw_path(self, surface):
        """绘制连接路径"""
        if len(self.path) < 2:
            return

        # 将网格坐标转换为屏幕坐标
        points = []
        for r, c in self.path:
            if r == -1:
                y = MARGIN_Y - 20
            elif r == ROWS:
                y = MARGIN_Y + ROWS * (TILE_H + GAP) - GAP + 20
            else:
                y = MARGIN_Y + r * (TILE_H + GAP) + TILE_H // 2

            if c == -1:
                x = MARGIN_X - 20
            elif c == COLS:
                x = MARGIN_X + COLS * (TILE_W + GAP) - GAP + 20
            else:
                x = MARGIN_X + c * (TILE_W + GAP) + TILE_W // 2

            points.append((x, y))

        # 绘制路径线
        alpha = min(255, self.path_timer * 12)
        for i in range(len(points) - 1):
            pygame.draw.line(surface, PATH_COLOR, points[i], points[i + 1], 4)
            # 路径节点
            pygame.draw.circle(surface, PATH_COLOR, points[i], 6)

        pygame.draw.circle(surface, PATH_COLOR, points[-1], 6)

    def draw_ui(self, surface):
        """绘制用户界面"""
        # 顶部信息栏
        ui_bg = pygame.Surface((WIDTH, 65), pygame.SRCALPHA)
        ui_bg.fill((0, 0, 0, 150))
        surface.blit(ui_bg, (0, 0))

        # 分数
        score_text = font_medium.render(f"得分: {self.score}", True, YELLOW)
        surface.blit(score_text, (20, 8))

        # 剩余对数
        pairs_text = font_small.render(f"剩余: {self.pairs_left}对", True, WHITE)
        surface.blit(pairs_text, (20, 38))

        # 时间
        minutes = int(self.time_elapsed) // 60
        seconds = int(self.time_elapsed) % 60
        time_text = font_medium.render(f"时间: {minutes:02d}:{seconds:02d}", True, WHITE)
        surface.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 8))

        # 连击
        if self.combo > 1:
            combo_text = font_medium.render(f"连击 x{self.combo}!", True, (255, 150, 50))
            surface.blit(combo_text, (WIDTH // 2 - combo_text.get_width() // 2, 38))

        # 操作提示
        hint_text = font_small.render("H提示 S洗牌 R重开", True, GRAY)
        surface.blit(hint_text, (WIDTH - hint_text.get_width() - 20, 38))

        # 无解提示
        if self.no_match:
            no_match_text = font_medium.render("无解! 按S洗牌", True, RED)
            # 闪烁效果
            if pygame.time.get_ticks() % 1000 < 700:
                surface.blit(no_match_text, (WIDTH // 2 - no_match_text.get_width() // 2,
                                             HEIGHT - 40))

    def draw_win(self, surface):
        """绘制胜利画面"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # 胜利面板
        panel = pygame.Rect(WIDTH // 2 - 200, 200, 400, 250)
        pygame.draw.rect(surface, (30, 60, 40), panel, border_radius=15)
        pygame.draw.rect(surface, YELLOW, panel, 3, border_radius=15)

        win_text = font_large.render("恭喜通关!", True, YELLOW)
        surface.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, 220))

        score_text = font_medium.render(f"最终得分: {self.score}", True, WHITE)
        surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 285))

        minutes = int(self.time_elapsed) // 60
        seconds = int(self.time_elapsed) % 60
        time_text = font_small.render(f"用时: {minutes:02d}:{seconds:02d}", True, LIGHT_GRAY)
        surface.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 325))

        hint1 = font_small.render("按 Enter 再来一局", True, YELLOW)
        hint2 = font_small.render("按 ESC 返回菜单", True, GRAY)
        surface.blit(hint1, (WIDTH // 2 - hint1.get_width() // 2, 380))
        surface.blit(hint2, (WIDTH // 2 - hint2.get_width() // 2, 410))


def main():
    """主函数"""
    clock = pygame.time.Clock()
    game = MahjongLink()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_input(event)

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
