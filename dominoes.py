"""
多米诺骨牌游戏
经典多米诺骨牌对对碰规则：
- 玩家和AI各有7张牌
- 轮流在链条两端放置匹配的骨牌
- 不能出牌时从牌堆摸牌
- 先出完所有牌的获胜

操作说明：
- 点击手中的骨牌选中
- 点击链条左端或右端放置
- 点击牌堆摸牌
- R 重新开始
"""

import pygame
import random
import sys

# 初始化
pygame.init()

# 常量
SCREEN_W, SCREEN_H = 1100, 750
FPS = 60

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
IVORY = (240, 235, 220)
DARK_BG = (20, 60, 20)
TABLE_GREEN = (30, 100, 40)
FELT_GREEN = (35, 110, 45)
BLUE = (50, 100, 220)
RED = (220, 50, 50)
YELLOW = (255, 215, 0)
GOLD = (255, 200, 50)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)
HIGHLIGHT = (255, 255, 100, 128)
ORANGE = (255, 165, 0)
PANEL_BG = (25, 70, 30)

# 骨牌尺寸
DOMINO_W = 70
DOMINO_H = 35
DOT_RADIUS = 4


class Domino:
    """单个骨牌"""
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.rect = pygame.Rect(0, 0, DOMINO_W, DOMINO_H)
        self.selected = False
        self.hovered = False

    def __repr__(self):
        return f"[{self.left}|{self.right}]"

    def total(self):
        return self.left + self.right

    def is_double(self):
        return self.left == self.right

    def can_match(self, value):
        """检查是否可以匹配给定值"""
        return self.left == value or self.right == value

    def flip(self):
        """翻转骨牌"""
        self.left, self.right = self.right, self.left


class DominoChain:
    """骨牌链条"""
    def __init__(self):
        self.tiles = []  # 链中的骨牌列表
        self.left_value = None  # 左端值
        self.right_value = None  # 右端值

    def is_empty(self):
        return len(self.tiles) == 0

    def add_first(self, domino):
        """添加第一张骨牌"""
        self.tiles.append(domino)
        self.left_value = domino.left
        self.right_value = domino.right

    def can_play_left(self, domino):
        """检查是否可以放在左端"""
        if self.is_empty():
            return True
        return domino.can_match(self.left_value)

    def can_play_right(self, domino):
        """检查是否可以放在右端"""
        if self.is_empty():
            return True
        return domino.can_match(self.right_value)

    def play_left(self, domino):
        """放在左端"""
        if self.is_empty():
            self.add_first(domino)
            return
        if domino.right == self.left_value:
            pass  # 正确方向
        elif domino.left == self.left_value:
            domino.flip()
        self.tiles.insert(0, domino)
        self.left_value = domino.left

    def play_right(self, domino):
        """放在右端"""
        if self.is_empty():
            self.add_first(domino)
            return
        if domino.left == self.right_value:
            pass  # 正确方向
        elif domino.right == self.right_value:
            domino.flip()
        self.tiles.append(domino)
        self.right_value = domino.right


class DominoGame:
    """多米诺骨牌游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("多米诺骨牌")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("simhei", 18)
        self.big_font = pygame.font.SysFont("simhei", 32)
        self.small_font = pygame.font.SysFont("simhei", 14)
        self.title_font = pygame.font.SysFont("simhei", 24)

        # 链条滚动
        self.chain_scroll = 0

        self.new_game()

    def new_game(self):
        """开始新游戏"""
        # 生成所有28张骨牌
        all_dominoes = []
        for i in range(7):
            for j in range(i, 7):
                all_dominoes.append(Domino(i, j))
        random.shuffle(all_dominoes)

        # 发牌
        self.player_hand = all_dominoes[:7]
        self.ai_hand = all_dominoes[7:14]
        self.stock = all_dominoes[14:]  # 牌堆

        # 链条
        self.chain = DominoChain()

        # 游戏状态
        self.turn = "player"  # player, ai
        self.selected_domino = None
        self.game_over = False
        self.winner = None
        self.message = "你的回合 - 选择一张骨牌"
        self.message_color = WHITE

        # 放置模式
        self.placing = False  # 是否在放置模式
        self.placing_domino = None

        # AI思考延迟
        self.ai_thinking = False
        self.ai_think_timer = 0

        # 链条滚动
        self.chain_scroll = 0
        self.chain_dragging = False
        self.chain_drag_start = 0
        self.chain_scroll_start = 0

        # 动画
        self.ai_played_anim = 0
        self.last_ai_play = None

    def get_player_playable(self):
        """获取玩家可出的牌"""
        if self.chain.is_empty():
            return self.player_hand[:]
        playable = []
        for d in self.player_hand:
            if self.chain.can_play_left(d) or self.chain.can_play_right(d):
                playable.append(d)
        return playable

    def get_ai_playable(self):
        """获取AI可出的牌"""
        if self.chain.is_empty():
            return self.ai_hand[:]
        playable = []
        for d in self.ai_hand:
            if self.chain.can_play_left(d) or self.chain.can_play_right(d):
                playable.append(d)
        return playable

    def ai_play(self):
        """AI出牌逻辑"""
        playable = self.get_ai_playable()
        if playable:
            # 优先出点数大的牌
            playable.sort(key=lambda d: d.total(), reverse=True)
            domino = playable[0]

            # 决定放哪端
            can_left = self.chain.can_play_left(domino)
            can_right = self.chain.can_play_right(domino)

            if can_left and can_right:
                # 优先放对自己更有利的一端
                if random.random() < 0.5:
                    self.chain.play_left(domino)
                else:
                    self.chain.play_right(domino)
            elif can_left:
                self.chain.play_left(domino)
            else:
                self.chain.play_right(domino)

            self.ai_hand.remove(domino)
            self.last_ai_play = domino
            self.ai_played_anim = 30
            self.message = f"AI 出了 {domino}"
            self.message_color = ORANGE

            # 检查AI是否获胜
            if not self.ai_hand:
                self.game_over = True
                self.winner = "ai"
                self.message = "AI 获胜!"
                self.message_color = RED
                return

            self.turn = "player"
            self._check_player_can_play()
        else:
            # AI摸牌
            if self.stock:
                drawn = self.stock.pop()
                self.ai_hand.append(drawn)
                self.message = f"AI 摸了一张牌 (剩余 {len(self.stock)})"
                self.message_color = LIGHT_GRAY
                # 摸牌后再试
                self.ai_think_timer = 30
            else:
                # AI无牌可出也无牌可摸
                self.message = "AI 无牌可出"
                self.message_color = GRAY
                self.turn = "player"
                self._check_player_can_play()

    def _check_player_can_play(self):
        """检查玩家是否能出牌"""
        if not self.get_player_playable():
            if self.stock:
                self.message = "你没有可出的牌，请点击牌堆摸牌"
                self.message_color = YELLOW
            else:
                # 双方都无法出牌，比较点数
                self._end_game_no_moves()

    def _end_game_no_moves(self):
        """双方都无法出牌时结束游戏"""
        player_total = sum(d.total() for d in self.player_hand)
        ai_total = sum(d.total() for d in self.ai_hand)
        if player_total < ai_total:
            self.winner = "player"
            self.message = f"无牌可出! 你的点数({player_total}) < AI点数({ai_total}), 你赢了!"
            self.message_color = GREEN
        elif ai_total < player_total:
            self.winner = "ai"
            self.message = f"无牌可出! AI点数({ai_total}) < 你的点数({player_total}), AI赢了!"
            self.message_color = RED
        else:
            self.winner = "draw"
            self.message = f"无牌可出! 平局! (都是{player_total}点)"
            self.message_color = YELLOW
        self.game_over = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    self.new_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_click(event.pos)
                elif event.button == 3:
                    # 右键取消选择
                    self.selected_domino = None
                    self.placing = False
                    self.message = "已取消选择"
                    self.message_color = GRAY
            elif event.type == pygame.MOUSEMOTION:
                self._handle_hover(event.pos)
                # 链条拖动
                if self.chain_dragging:
                    dx = event.pos[0] - self.chain_drag_start
                    self.chain_scroll = self.chain_scroll_start + dx
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.chain_dragging = False
        return True

    def _handle_click(self, pos):
        """处理鼠标点击"""
        if self.game_over:
            return
        if self.turn != "player":
            return

        mx, my = pos

        # 检查是否点击了放置区域（链条端点）
        if self.placing and self.placing_domino:
            if self._check_chain_end_click(mx, my):
                return

        # 检查是否点击了牌堆
        stock_rect = self._get_stock_rect()
        if stock_rect.collidepoint(mx, my):
            if not self.get_player_playable() and self.stock:
                drawn = self.stock.pop()
                self.player_hand.append(drawn)
                self.message = f"你摸了 {drawn} (牌堆剩余 {len(self.stock)})"
                self.message_color = CYAN
                # 摸牌后检查能否出牌
                if not self.get_player_playable():
                    if self.stock:
                        self.message = "还是不能出，继续摸牌"
                    else:
                        self._end_game_no_moves()
                return

        # 检查是否点击了手中的骨牌
        hand_rects = self._get_hand_rects()
        for i, (rect, domino) in enumerate(hand_rects):
            if rect.collidepoint(mx, my):
                if self.placing and self.placing_domino == domino:
                    # 再次点击取消
                    self.placing = False
                    self.placing_domino = None
                    self.message = "已取消放置"
                    self.message_color = GRAY
                elif domino in self.get_player_playable():
                    self.selected_domino = domino
                    self.placing = True
                    self.placing_domino = domino
                    self.message = f"选择了 {domino} - 点击链条端点放置"
                    self.message_color = YELLOW
                else:
                    self.message = f"{domino} 无法匹配当前链条端点"
                    self.message_color = RED
                return

        # 检查链条区域拖动
        chain_area = pygame.Rect(50, 250, SCREEN_W - 100, 200)
        if chain_area.collidepoint(mx, my):
            self.chain_dragging = True
            self.chain_drag_start = mx
            self.chain_scroll_start = self.chain_scroll

    def _check_chain_end_click(self, mx, my):
        """检查是否点击了链条端点"""
        if not self.placing_domino:
            return False

        domino = self.placing_domino
        can_left = self.chain.can_play_left(domino)
        can_right = self.chain.can_play_right(domino)

        # 计算链条端点位置
        chain_area_y = 320
        if self.chain.is_empty():
            # 空链条，放在中间
            center_x = SCREEN_W // 2 + self.chain_scroll
            if abs(mx - center_x) < 60 and abs(my - chain_area_y) < 40:
                self.chain.play_right(domino)
                self.player_hand.remove(domino)
                self.placing = False
                self.placing_domino = None
                self.selected_domino = None
                self._after_player_play()
                return True
        else:
            # 左端
            left_x = 100 + self.chain_scroll
            if can_left and abs(mx - left_x) < 50 and abs(my - chain_area_y) < 50:
                self.chain.play_left(domino)
                self.player_hand.remove(domino)
                self.placing = False
                self.placing_domino = None
                self.selected_domino = None
                self._after_player_play()
                return True
            # 右端
            right_x = SCREEN_W - 100 + self.chain_scroll
            if can_right and abs(mx - right_x) < 50 and abs(my - chain_area_y) < 50:
                self.chain.play_right(domino)
                self.player_hand.remove(domino)
                self.placing = False
                self.placing_domino = None
                self.selected_domino = None
                self._after_player_play()
                return True

        return False

    def _after_player_play(self):
        """玩家出牌后"""
        if not self.player_hand:
            self.game_over = True
            self.winner = "player"
            self.message = "恭喜你获胜了!"
            self.message_color = GREEN
            return
        self.turn = "ai"
        self.ai_thinking = True
        self.ai_think_timer = 45

    def _handle_hover(self, pos):
        """处理鼠标悬停"""
        mx, my = pos
        hand_rects = self._get_hand_rects()
        for rect, domino in hand_rects:
            domino.hovered = rect.collidepoint(mx, my)

    def _get_hand_rects(self):
        """获取玩家手牌的矩形区域"""
        rects = []
        n = len(self.player_hand)
        if n == 0:
            return rects
        total_w = n * (DOMINO_W + 8) - 8
        start_x = (SCREEN_W - total_w) // 2
        y = SCREEN_H - 100
        for i, domino in enumerate(self.player_hand):
            x = start_x + i * (DOMINO_W + 8)
            rect = pygame.Rect(x, y, DOMINO_W, DOMINO_H)
            rects.append((rect, domino))
        return rects

    def _get_stock_rect(self):
        """获取牌堆的矩形区域"""
        return pygame.Rect(SCREEN_W - 120, 300, 80, 50)

    def update(self):
        """更新游戏逻辑"""
        if self.ai_played_anim > 0:
            self.ai_played_anim -= 1

        if self.turn == "ai" and self.ai_thinking:
            self.ai_think_timer -= 1
            if self.ai_think_timer <= 0:
                self.ai_thinking = False
                self.ai_play()

    def draw(self):
        """绘制游戏画面"""
        self.screen.fill(DARK_BG)

        # 桌面
        table_rect = pygame.Rect(20, 20, SCREEN_W - 40, SCREEN_H - 40)
        pygame.draw.rect(self.screen, TABLE_GREEN, table_rect, border_radius=15)
        pygame.draw.rect(self.screen, (20, 80, 30), table_rect, 3, border_radius=15)

        # 标题
        title = self.title_font.render("多米诺骨牌", True, GOLD)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 30))

        # AI手牌（背面）
        ai_y = 80
        ai_n = len(self.ai_hand)
        ai_total_w = ai_n * 30
        ai_start_x = (SCREEN_W - ai_total_w) // 2
        for i in range(ai_n):
            x = ai_start_x + i * 30
            rect = pygame.Rect(x, ai_y, 25, 40)
            pygame.draw.rect(self.screen, (40, 40, 80), rect, border_radius=3)
            pygame.draw.rect(self.screen, (60, 60, 120), rect, 1, border_radius=3)
            # 花纹
            pygame.draw.circle(self.screen, (50, 50, 100),
                               (x + 12, ai_y + 20), 6)

        ai_label = self.small_font.render(f"AI ({ai_n}张)", True, LIGHT_GRAY)
        self.screen.blit(ai_label, (SCREEN_W // 2 - ai_label.get_width() // 2, ai_y + 45))

        # 链条区域
        chain_area = pygame.Rect(40, 240, SCREEN_W - 80, 180)
        pygame.draw.rect(self.screen, FELT_GREEN, chain_area, border_radius=10)
        pygame.draw.rect(self.screen, (20, 80, 30), chain_area, 2, border_radius=10)

        # 绘制链条
        self._draw_chain()

        # 放置提示
        if self.placing and self.placing_domino:
            self._draw_placement_hints()

        # 牌堆
        self._draw_stock()

        # 玩家手牌
        self._draw_player_hand()

        # 消息
        msg = self.font.render(self.message, True, self.message_color)
        self.screen.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2, 460))

        # 游戏结束覆盖
        if self.game_over:
            self._draw_game_over()

        # 操作提示
        help_txt = self.small_font.render(
            "左键:选择/放置 | 右键:取消 | R:重开 | 拖动链条区域滚动",
            True, GRAY)
        self.screen.blit(help_txt, (SCREEN_W // 2 - help_txt.get_width() // 2,
                                    SCREEN_H - 30))

        pygame.display.flip()

    def _draw_chain(self):
        """绘制骨牌链条"""
        if self.chain.is_empty():
            txt = self.font.render("链条为空 - 请出第一张牌", True, GRAY)
            self.screen.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2, 320))
            return

        n = len(self.chain.tiles)
        tile_w = DOMINO_W + 4
        total_w = n * tile_w
        start_x = SCREEN_W // 2 - total_w // 2 + self.chain_scroll
        y = 310

        # 裁剪区域
        clip_rect = pygame.Rect(45, 245, SCREEN_W - 90, 170)
        self.screen.set_clip(clip_rect)

        for i, domino in enumerate(self.chain.tiles):
            x = start_x + i * tile_w
            self._draw_domino(x, y, domino, horizontal=True, face_up=True)

        # 左端和右端标记
        if not self.chain.is_empty():
            left_x = start_x - 15
            right_x = start_x + n * tile_w + 5
            # 左端值
            lv = self.small_font.render(f"<{self.chain.left_value}", True, YELLOW)
            self.screen.blit(lv, (left_x - 20, y + 10))
            # 右端值
            rv = self.small_font.render(f"{self.chain.right_value}>", True, YELLOW)
            self.screen.blit(rv, (right_x, y + 10))

        self.screen.set_clip(None)

    def _draw_placement_hints(self):
        """绘制放置提示"""
        if self.chain.is_empty():
            # 中间放置提示
            cx = SCREEN_W // 2
            cy = 320
            pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
            r = int(30 + pulse * 10)
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 0, 60), (r, r), r)
            self.screen.blit(s, (cx - r, cy - r))
            txt = self.small_font.render("点击此处放置", True, YELLOW)
            self.screen.blit(txt, (cx - txt.get_width() // 2, cy + 35))
        else:
            domino = self.placing_domino
            # 左端提示
            if self.chain.can_play_left(domino):
                lx = 100 + self.chain_scroll
                pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
                r = int(25 + pulse * 8)
                s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (0, 255, 0, 80), (r, r), r)
                self.screen.blit(s, (lx - r, 320 - r))
                txt = self.small_font.render("放左端", True, GREEN)
                self.screen.blit(txt, (lx - txt.get_width() // 2, 355))
            # 右端提示
            if self.chain.can_play_right(domino):
                rx = SCREEN_W - 100 + self.chain_scroll
                pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
                r = int(25 + pulse * 8)
                s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (0, 255, 0, 80), (r, r), r)
                self.screen.blit(s, (rx - r, 320 - r))
                txt = self.small_font.render("放右端", True, GREEN)
                self.screen.blit(txt, (rx - txt.get_width() // 2, 355))

    def _draw_stock(self):
        """绘制牌堆"""
        rect = self._get_stock_rect()
        # 牌堆背景
        pygame.draw.rect(self.screen, (30, 30, 60), rect, border_radius=5)
        pygame.draw.rect(self.screen, (60, 60, 100), rect, 2, border_radius=5)
        # 叠放效果
        for i in range(min(3, len(self.stock))):
            r = pygame.Rect(rect.x - i * 2, rect.y - i * 2, rect.w, rect.h)
            pygame.draw.rect(self.screen, (35, 35, 70), r, border_radius=5)
            pygame.draw.rect(self.screen, (50, 50, 90), r, 1, border_radius=5)
        txt = self.font.render(f"牌堆", True, WHITE)
        self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.y + 5))
        cnt = self.small_font.render(f"{len(self.stock)}张", True, LIGHT_GRAY)
        self.screen.blit(cnt, (rect.centerx - cnt.get_width() // 2, rect.y + 28))

    def _draw_player_hand(self):
        """绘制玩家手牌"""
        hand_rects = self._get_hand_rects()
        for rect, domino in hand_rects:
            y_offset = -10 if domino.hovered else 0
            if domino == self.selected_domino:
                y_offset = -15
            draw_rect = pygame.Rect(rect.x, rect.y + y_offset, rect.w, rect.h)
            self._draw_domino(draw_rect.x, draw_rect.y, domino,
                              horizontal=True, face_up=True,
                              selected=(domino == self.selected_domino),
                              hovered=domino.hovered)

    def _draw_domino(self, x, y, domino, horizontal=True, face_up=True,
                     selected=False, hovered=False):
        """绘制单个骨牌"""
        if horizontal:
            w, h = DOMINO_W, DOMINO_H
        else:
            w, h = DOMINO_H, DOMINO_W

        rect = pygame.Rect(x, y, w, h)

        if not face_up:
            pygame.draw.rect(self.screen, (40, 40, 80), rect, border_radius=4)
            pygame.draw.rect(self.screen, (60, 60, 120), rect, 1, border_radius=4)
            return

        # 背景
        bg_color = IVORY
        if selected:
            bg_color = (255, 255, 200)
        elif hovered:
            bg_color = (250, 248, 235)

        pygame.draw.rect(self.screen, bg_color, rect, border_radius=4)
        border_color = GOLD if selected else (BLACK if hovered else DARK_GRAY)
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=4)

        # 中间分割线
        if horizontal:
            mid_x = x + w // 2
            pygame.draw.line(self.screen, DARK_GRAY, (mid_x, y + 3), (mid_x, y + h - 3), 2)
            # 左半点数
            self._draw_dots(mid_x - w // 4, y + h // 2, domino.left, w // 4 - 2, h // 2 - 4)
            # 右半点数
            self._draw_dots(mid_x + w // 4, y + h // 2, domino.right, w // 4 - 2, h // 2 - 4)
        else:
            mid_y = y + h // 2
            pygame.draw.line(self.screen, DARK_GRAY, (x + 3, mid_y), (x + w - 3, mid_y), 2)
            self._draw_dots(x + w // 2, mid_y - h // 4, domino.left, w // 2 - 4, h // 4 - 2)
            self._draw_dots(x + w // 2, mid_y + h // 4, domino.right, w // 2 - 4, h // 4 - 2)

    def _draw_dots(self, cx, cy, value, half_w, half_h):
        """绘制骨牌上的点"""
        r = min(DOT_RADIUS, half_w // 3, half_h // 3)
        positions = {
            0: [],
            1: [(cx, cy)],
            2: [(cx - half_w // 2, cy - half_h // 2),
                (cx + half_w // 2, cy + half_h // 2)],
            3: [(cx - half_w // 2, cy - half_h // 2),
                (cx, cy),
                (cx + half_w // 2, cy + half_h // 2)],
            4: [(cx - half_w // 2, cy - half_h // 2),
                (cx + half_w // 2, cy - half_h // 2),
                (cx - half_w // 2, cy + half_h // 2),
                (cx + half_w // 2, cy + half_h // 2)],
            5: [(cx - half_w // 2, cy - half_h // 2),
                (cx + half_w // 2, cy - half_h // 2),
                (cx, cy),
                (cx - half_w // 2, cy + half_h // 2),
                (cx + half_w // 2, cy + half_h // 2)],
            6: [(cx - half_w // 2, cy - half_h // 2),
                (cx + half_w // 2, cy - half_h // 2),
                (cx - half_w // 2, cy),
                (cx + half_w // 2, cy),
                (cx - half_w // 2, cy + half_h // 2),
                (cx + half_w // 2, cy + half_h // 2)],
        }
        for px, py in positions.get(value, []):
            pygame.draw.circle(self.screen, BLACK, (int(px), int(py)), r)

    def _draw_game_over(self):
        """绘制游戏结束覆盖"""
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        if self.winner == "player":
            text = "你赢了!"
            color = GREEN
        elif self.winner == "ai":
            text = "AI 赢了!"
            color = RED
        else:
            text = "平局!"
            color = YELLOW

        txt = self.big_font.render(text, True, color)
        self.screen.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2,
                               SCREEN_H // 2 - 60))

        sub = self.font.render("按 R 重新开始", True, WHITE)
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2,
                               SCREEN_H // 2))

    def run(self):
        """游戏主循环"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = DominoGame()
    game.run()
