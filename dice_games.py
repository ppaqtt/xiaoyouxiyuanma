"""
骰子游戏合集
包含三个小游戏：
  1. 比大小 - 玩家和电脑各掷骰子比大小
  2. 猜点数 - 猜骰子总和
  3. 21点骰子版 - 掷骰子尽量接近21点

操作说明：
- 鼠标点击按钮进行操作
- ESC 返回菜单
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
SCREEN_W, SCREEN_H = 800, 600
FPS = 60

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 180, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 215, 0)
GOLD = (255, 200, 50)
DARK_BG = (25, 25, 40)
PANEL_BG = (40, 40, 60)
BUTTON_BG = (60, 60, 90)
BUTTON_HOVER = (80, 80, 120)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
DARK_RED = (150, 30, 30)
DARK_GREEN = (30, 100, 30)
PURPLE = (150, 50, 200)
ORANGE = (255, 140, 0)
CYAN = (0, 200, 200)

# 游戏状态
MENU = 0
GAME_COMPARE = 1
GAME_GUESS = 2
GAME_BLACKJACK = 3


class DiceRenderer:
    """骰子渲染器，带动画效果"""
    def __init__(self):
        self.animating = False
        self.anim_timer = 0
        self.anim_duration = 30  # 动画帧数
        self.current_values = [1, 1]
        self.final_values = [1, 1]
        self.callback = None

    def start_roll(self, num_dice, final_values, callback):
        """开始掷骰子动画"""
        self.animating = True
        self.anim_timer = 0
        self.num_dice = num_dice
        self.final_values = final_values
        self.current_values = [random.randint(1, 6) for _ in range(num_dice)]
        self.callback = callback

    def update(self):
        """更新动画"""
        if not self.animating:
            return
        self.anim_timer += 1
        # 快速切换骰子面
        if self.anim_timer < self.anim_duration:
            self.current_values = [random.randint(1, 6) for _ in range(self.num_dice)]
        else:
            self.animating = False
            self.current_values = self.final_values[:]
            if self.callback:
                self.callback()

    def draw(self, screen, x, y, size=60):
        """绘制骰子"""
        if not hasattr(self, 'num_dice'):
            return
        total_w = self.num_dice * size + (self.num_dice - 1) * 10
        start_x = x - total_w // 2
        for i, val in enumerate(self.current_values):
            dx = start_x + i * (size + 10)
            self._draw_single_die(screen, dx, y, size, val)

    def _draw_single_die(self, screen, x, y, size, value):
        """绘制单个骰子"""
        # 骰子背景
        rect = pygame.Rect(x, y, size, size)
        pygame.draw.rect(screen, WHITE, rect, border_radius=8)
        pygame.draw.rect(screen, GRAY, rect, 2, border_radius=8)

        # 骰子阴影效果
        shadow = pygame.Rect(x + 2, y + 2, size - 4, size - 4)
        pygame.draw.rect(screen, (240, 240, 240), shadow, border_radius=6)

        # 点的位置
        cx, cy = x + size // 2, y + size // 2
        offset = size // 4
        dot_r = max(3, size // 10)

        # 根据点数绘制
        dot_positions = {
            1: [(cx, cy)],
            2: [(cx - offset, cy - offset), (cx + offset, cy + offset)],
            3: [(cx - offset, cy - offset), (cx, cy), (cx + offset, cy + offset)],
            4: [(cx - offset, cy - offset), (cx + offset, cy - offset),
                (cx - offset, cy + offset), (cx + offset, cy + offset)],
            5: [(cx - offset, cy - offset), (cx + offset, cy - offset),
                (cx, cy),
                (cx - offset, cy + offset), (cx + offset, cy + offset)],
            6: [(cx - offset, cy - offset), (cx + offset, cy - offset),
                (cx - offset, cy), (cx + offset, cy),
                (cx - offset, cy + offset), (cx + offset, cy + offset)],
        }
        for px, py in dot_positions.get(value, []):
            pygame.draw.circle(screen, BLACK, (int(px), int(py)), dot_r)


class Button:
    """按钮组件"""
    def __init__(self, x, y, w, h, text, color=BUTTON_BG, text_color=WHITE):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hovered = False
        self.enabled = True

    def draw(self, screen, font):
        color = self.color
        if not self.enabled:
            color = (50, 50, 50)
        elif self.hovered:
            color = BUTTON_HOVER
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE if self.enabled else GRAY,
                         self.rect, 2, border_radius=8)
        txt = font.render(self.text, True, self.text_color if self.enabled else GRAY)
        screen.blit(txt, (self.rect.centerx - txt.get_width() // 2,
                          self.rect.centery - txt.get_height() // 2))

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered

    def is_clicked(self, pos):
        return self.enabled and self.rect.collidepoint(pos)


class CompareGame:
    """比大小游戏"""
    def __init__(self, screen, font, big_font):
        self.screen = screen
        self.font = font
        self.big_font = big_font
        self.dice = DiceRenderer()
        self.player_score = 0
        self.computer_score = 0
        self.rounds = 0
        self.max_rounds = 5
        self.state = "ready"  # ready, rolling, result
        self.result_text = ""
        self.result_color = WHITE
        self.player_val = 0
        self.computer_val = 0
        self.roll_btn = Button(SCREEN_W // 2 - 80, 480, 160, 50, "掷骰子!")
        self.next_btn = Button(SCREEN_W // 2 - 80, 480, 160, 50, "下一轮")
        self.menu_btn = Button(SCREEN_W // 2 - 80, 540, 160, 40, "返回菜单")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "menu"
        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            self.roll_btn.check_hover(pos)
            self.next_btn.check_hover(pos)
            self.menu_btn.check_hover(pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.menu_btn.is_clicked(pos):
                return "menu"
            if self.state == "ready" and self.roll_btn.is_clicked(pos):
                self._roll()
            elif self.state == "result" and self.next_btn.is_clicked(pos):
                if self.rounds >= self.max_rounds:
                    self.state = "final"
                else:
                    self.state = "ready"
        return None

    def _roll(self):
        self.state = "rolling"
        self.player_val = random.randint(1, 6)
        self.computer_val = random.randint(1, 6)
        self.dice.start_roll(1, [self.player_val], self._on_player_done)

    def _on_player_done(self):
        # 玩家骰子动画结束，开始电脑骰子动画
        self.dice.start_roll(1, [self.computer_val], self._on_done)

    def _on_done(self):
        self.rounds += 1
        if self.player_val > self.computer_val:
            self.player_score += 1
            self.result_text = f"你赢了! {self.player_val} > {self.computer_val}"
            self.result_color = GREEN
        elif self.player_val < self.computer_val:
            self.computer_score += 1
            self.result_text = f"你输了! {self.player_val} < {self.computer_val}"
            self.result_color = RED
        else:
            self.result_text = f"平局! {self.player_val} = {self.computer_val}"
            self.result_color = YELLOW
        self.state = "result"

    def update(self):
        self.dice.update()

    def draw(self):
        self.screen.fill(DARK_BG)
        # 标题
        title = self.big_font.render("比大小", True, GOLD)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 20))

        # 比分
        score_txt = self.font.render(
            f"回合 {self.rounds}/{self.max_rounds}  |  "
            f"你: {self.player_score}  电脑: {self.computer_score}", True, WHITE)
        self.screen.blit(score_txt, (SCREEN_W // 2 - score_txt.get_width() // 2, 70))

        # 玩家区域
        player_label = self.font.render("你的骰子", True, CYAN)
        self.screen.blit(player_label, (SCREEN_W // 4 - player_label.get_width() // 2, 120))

        # 电脑区域
        comp_label = self.font.render("电脑骰子", True, ORANGE)
        self.screen.blit(comp_label, (3 * SCREEN_W // 4 - comp_label.get_width() // 2, 120))

        # 绘制骰子
        if self.state == "ready":
            # 显示空骰子
            self.dice.num_dice = 1
            self.dice.current_values = [1]
            self.dice.draw(self.screen, SCREEN_W // 4, 180, 80)
            self.dice.draw(self.screen, 3 * SCREEN_W // 4, 180, 80)
        elif self.state == "rolling":
            self.dice.draw(self.screen, SCREEN_W // 4, 180, 80)
            # 电脑骰子在玩家动画结束后才显示
            if not hasattr(self, '_show_computer'):
                pass
        elif self.state == "result":
            # 显示最终结果
            self.dice.num_dice = 1
            self.dice.current_values = [self.player_val]
            self.dice.draw(self.screen, SCREEN_W // 4, 180, 80)
            self.dice.current_values = [self.computer_val]
            self.dice.draw(self.screen, 3 * SCREEN_W // 4, 180, 80)

        # VS
        vs_txt = self.big_font.render("VS", True, RED)
        self.screen.blit(vs_txt, (SCREEN_W // 2 - vs_txt.get_width() // 2, 200))

        # 结果文字
        if self.state == "result":
            result = self.font.render(self.result_text, True, self.result_color)
            self.screen.blit(result, (SCREEN_W // 2 - result.get_width() // 2, 350))

        # 最终结果
        if self.state == "final":
            if self.player_score > self.computer_score:
                final = self.big_font.render("你获胜了!", True, GREEN)
            elif self.player_score < self.computer_score:
                final = self.big_font.render("电脑获胜!", True, RED)
            else:
                final = self.big_font.render("平局!", True, YELLOW)
            self.screen.blit(final, (SCREEN_W // 2 - final.get_width() // 2, 380))

        # 按钮
        if self.state == "ready":
            self.roll_btn.draw(self.screen, self.font)
        elif self.state == "result":
            self.next_btn.draw(self.screen, self.font)
        elif self.state == "final":
            self.next_btn.text = "再来一局"
            self.next_btn.draw(self.screen, self.font)
        self.menu_btn.draw(self.screen, self.font)

    def reset(self):
        self.player_score = 0
        self.computer_score = 0
        self.rounds = 0
        self.state = "ready"
        self.result_text = ""


class GuessGame:
    """猜点数游戏"""
    def __init__(self, screen, font, big_font):
        self.screen = screen
        self.font = font
        self.big_font = big_font
        self.dice = DiceRenderer()
        self.player_score = 0
        self.total_rounds = 0
        self.max_rounds = 5
        self.state = "ready"  # ready, rolling, result
        self.guess = 7
        self.actual = 0
        self.result_text = ""
        self.result_color = WHITE
        # 猜测按钮
        self.guess_buttons = []
        for i in range(2, 13):
            bx = 100 + (i - 2) * 52
            by = 200
            self.guess_buttons.append(Button(bx, by, 45, 40, str(i)))
        self.roll_btn = Button(SCREEN_W // 2 - 80, 350, 160, 50, "掷骰子!")
        self.next_btn = Button(SCREEN_W // 2 - 80, 480, 160, 50, "下一轮")
        self.menu_btn = Button(SCREEN_W // 2 - 80, 540, 160, 40, "返回菜单")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "menu"
        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            for b in self.guess_buttons:
                b.check_hover(pos)
            self.roll_btn.check_hover(pos)
            self.next_btn.check_hover(pos)
            self.menu_btn.check_hover(pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.menu_btn.is_clicked(pos):
                return "menu"
            if self.state == "ready":
                for i, b in enumerate(self.guess_buttons):
                    if b.is_clicked(pos):
                        self.guess = i + 2
                if self.roll_btn.is_clicked(pos):
                    self._roll()
            elif self.state == "result":
                if self.next_btn.is_clicked(pos):
                    if self.total_rounds >= self.max_rounds:
                        self.state = "final"
                    else:
                        self.state = "ready"
        return None

    def _roll(self):
        self.state = "rolling"
        v1 = random.randint(1, 6)
        v2 = random.randint(1, 6)
        self.actual = v1 + v2
        self.dice.start_roll(2, [v1, v2], self._on_done)

    def _on_done(self):
        self.total_rounds += 1
        diff = abs(self.guess - self.actual)
        if diff == 0:
            self.player_score += 10
            self.result_text = f"完全正确! 你猜 {self.guess}, 实际 {self.actual} (+10分)"
            self.result_color = GREEN
        elif diff == 1:
            self.player_score += 5
            self.result_text = f"接近! 你猜 {self.guess}, 实际 {self.actual} (+5分)"
            self.result_color = YELLOW
        else:
            self.result_text = f"没猜中! 你猜 {self.guess}, 实际 {self.actual} (+0分)"
            self.result_color = RED
        self.state = "result"

    def update(self):
        self.dice.update()

    def draw(self):
        self.screen.fill(DARK_BG)
        title = self.big_font.render("猜点数", True, GOLD)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 20))

        info = self.font.render(
            f"回合 {self.total_rounds}/{self.max_rounds}  |  得分: {self.player_score}",
            True, WHITE)
        self.screen.blit(info, (SCREEN_W // 2 - info.get_width() // 2, 70))

        # 提示
        hint = self.font.render("选择你猜测的两个骰子总和 (2-12):", True, LIGHT_GRAY)
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, 160))

        # 猜测按钮
        for i, b in enumerate(self.guess_buttons):
            if i + 2 == self.guess:
                b.color = BLUE
            else:
                b.color = BUTTON_BG
            b.draw(self.screen, self.font)

        # 骰子
        if self.state in ("rolling", "result"):
            self.dice.draw(self.screen, SCREEN_W // 2, 310, 70)

        # 结果
        if self.state == "result":
            result = self.font.render(self.result_text, True, self.result_color)
            self.screen.blit(result, (SCREEN_W // 2 - result.get_width() // 2, 420))

        if self.state == "final":
            final = self.big_font.render(f"最终得分: {self.player_score}", True, GOLD)
            self.screen.blit(final, (SCREEN_W // 2 - final.get_width() // 2, 380))

        # 按钮
        if self.state == "ready":
            self.roll_btn.draw(self.screen, self.font)
        elif self.state == "result":
            self.next_btn.draw(self.screen, self.font)
        elif self.state == "final":
            self.next_btn.text = "再来一局"
            self.next_btn.draw(self.screen, self.font)
        self.menu_btn.draw(self.screen, self.font)

    def reset(self):
        self.player_score = 0
        self.total_rounds = 0
        self.state = "ready"
        self.guess = 7
        self.result_text = ""


class BlackjackDiceGame:
    """21点骰子版"""
    def __init__(self, screen, font, big_font):
        self.screen = screen
        self.font = font
        self.big_font = big_font
        self.dice = DiceRenderer()
        self.state = "ready"  # ready, player_turn, rolling, dealer_turn, result
        self.player_total = 0
        self.dealer_total = 0
        self.player_dice = []
        self.dealer_dice = []
        self.result_text = ""
        self.result_color = WHITE
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.hit_btn = Button(SCREEN_W // 2 - 170, 460, 150, 50, "要骰子 (Hit)")
        self.stand_btn = Button(SCREEN_W // 2 + 20, 460, 150, 50, "停牌 (Stand)")
        self.next_btn = Button(SCREEN_W // 2 - 80, 460, 160, 50, "下一局")
        self.menu_btn = Button(SCREEN_W // 2 - 80, 540, 160, 40, "返回菜单")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "menu"
        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            self.hit_btn.check_hover(pos)
            self.stand_btn.check_hover(pos)
            self.next_btn.check_hover(pos)
            self.menu_btn.check_hover(pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.menu_btn.is_clicked(pos):
                return "menu"
            if self.state == "player_turn":
                if self.hit_btn.is_clicked(pos):
                    self._player_hit()
                elif self.stand_btn.is_clicked(pos):
                    self._dealer_turn()
            elif self.state == "result":
                if self.next_btn.is_clicked(pos):
                    self._new_round()
        return None

    def _new_round(self):
        self.player_total = 0
        self.dealer_total = 0
        self.player_dice = []
        self.dealer_dice = []
        self.result_text = ""
        self.state = "ready"
        # 发初始骰子
        self._player_hit()

    def _player_hit(self):
        self.state = "rolling"
        val = random.randint(1, 6)
        self.player_dice.append(val)
        self.player_total += val
        self.dice.start_roll(1, [val], self._on_player_roll_done)

    def _on_player_roll_done(self):
        if self.player_total > 21:
            self.result_text = f"爆了! 你的点数: {self.player_total} > 21"
            self.result_color = RED
            self.losses += 1
            self.state = "result"
            # 揭示庄家
            self._reveal_dealer()
        elif self.player_total == 21:
            self.result_text = f"完美21点!"
            self.result_color = GREEN
            self._dealer_turn()
        else:
            self.state = "player_turn"

    def _dealer_turn(self):
        self.state = "dealer_turn"
        self.dealer_dice = []
        self.dealer_total = 0
        self._dealer_hit()

    def _dealer_hit(self):
        val = random.randint(1, 6)
        self.dealer_dice.append(val)
        self.dealer_total += val
        self.dice.start_roll(1, [val], self._on_dealer_roll_done)

    def _on_dealer_roll_done(self):
        if self.dealer_total >= 17:
            # 庄家停牌，比较结果
            self._compare()
        else:
            # 延迟继续
            pygame.time.set_timer(pygame.USEREVENT + 1, 500)

    def _compare(self):
        if self.dealer_total > 21:
            self.result_text = (f"庄家爆了! 你: {self.player_total}  "
                                f"庄家: {self.dealer_total}")
            self.result_color = GREEN
            self.wins += 1
        elif self.player_total > self.dealer_total:
            self.result_text = (f"你赢了! 你: {self.player_total}  "
                                f"庄家: {self.dealer_total}")
            self.result_color = GREEN
            self.wins += 1
        elif self.player_total < self.dealer_total:
            self.result_text = (f"庄家赢了! 你: {self.player_total}  "
                                f"庄家: {self.dealer_total}")
            self.result_color = RED
            self.losses += 1
        else:
            self.result_text = (f"平局! 都是 {self.player_total}")
            self.result_color = YELLOW
            self.draws += 1
        self.state = "result"

    def _reveal_dealer(self):
        """爆牌时揭示庄家的骰子"""
        while self.dealer_total < 17:
            val = random.randint(1, 6)
            self.dealer_dice.append(val)
            self.dealer_total += val

    def update(self):
        self.dice.update()

    def draw(self):
        self.screen.fill(DARK_BG)
        title = self.big_font.render("21点骰子版", True, GOLD)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 15))

        # 战绩
        record = self.font.render(
            f"胜: {self.wins}  负: {self.losses}  平: {self.draws}", True, WHITE)
        self.screen.blit(record, (SCREEN_W // 2 - record.get_width() // 2, 60))

        # 庄家区域
        dealer_label = self.font.render(f"庄家 ({self.dealer_total}点)", True, ORANGE)
        self.screen.blit(dealer_label, (SCREEN_W // 2 - dealer_label.get_width() // 2, 100))

        # 庄家骰子
        if self.dealer_dice:
            self.dice.num_dice = len(self.dealer_dice)
            self.dice.current_values = self.dealer_dice
            total_w = len(self.dealer_dice) * 50 + (len(self.dealer_dice) - 1) * 8
            self.dice.draw(self.screen, SCREEN_W // 2, 140, 50)

        # 分隔线
        pygame.draw.line(self.screen, GRAY, (100, 220), (SCREEN_W - 100, 220), 1)

        # 玩家区域
        player_label = self.font.render(f"你的点数: {self.player_total}", True, CYAN)
        self.screen.blit(player_label, (SCREEN_W // 2 - player_label.get_width() // 2, 240))

        # 玩家骰子
        if self.player_dice:
            self.dice.num_dice = len(self.player_dice)
            self.dice.current_values = self.player_dice
            self.dice.draw(self.screen, SCREEN_W // 2, 280, 50)

        # 目标提示
        if self.state == "player_turn":
            hint = self.font.render("要骰子还是停牌? (尽量接近21点,超过则爆牌)", True, LIGHT_GRAY)
            self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, 400))

        # 结果
        if self.state == "result":
            result = self.font.render(self.result_text, True, self.result_color)
            self.screen.blit(result, (SCREEN_W // 2 - result.get_width() // 2, 400))

        # 按钮
        if self.state == "player_turn":
            self.hit_btn.enabled = self.player_total < 21
            self.hit_btn.draw(self.screen, self.font)
            self.stand_btn.draw(self.screen, self.font)
        elif self.state == "result":
            self.next_btn.draw(self.screen, self.font)
        elif self.state == "ready":
            start_btn = Button(SCREEN_W // 2 - 80, 460, 160, 50, "开始游戏")
            start_btn.check_hover(pygame.mouse.get_pos())
            start_btn.draw(self.screen, self.font)
            self._start_btn = start_btn
        self.menu_btn.draw(self.screen, self.font)

    def reset(self):
        self.player_total = 0
        self.dealer_total = 0
        self.player_dice = []
        self.dealer_dice = []
        self.state = "ready"
        self.result_text = ""


class DiceGames:
    """骰子游戏合集主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("骰子游戏合集")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("simhei", 20)
        self.big_font = pygame.font.SysFont("simhei", 40)
        self.small_font = pygame.font.SysFont("simhei", 16)

        self.state = MENU
        self.compare_game = CompareGame(self.screen, self.font, self.big_font)
        self.guess_game = GuessGame(self.screen, self.font, self.big_font)
        self.blackjack_game = BlackjackDiceGame(self.screen, self.font, self.big_font)

        # 菜单按钮
        self.menu_buttons = [
            Button(SCREEN_W // 2 - 120, 200, 240, 60, "比大小", (50, 100, 50)),
            Button(SCREEN_W // 2 - 120, 280, 240, 60, "猜点数", (50, 50, 120)),
            Button(SCREEN_W // 2 - 120, 360, 240, 60, "21点骰子版", (120, 50, 50)),
        ]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.USEREVENT + 1:
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                if self.blackjack_game.state == "dealer_turn":
                    if self.blackjack_game.dealer_total < 17:
                        self.blackjack_game._dealer_hit()
                    else:
                        self.blackjack_game._compare()
                continue

            if self.state == MENU:
                if event.type == pygame.MOUSEMOTION:
                    for b in self.menu_buttons:
                        b.check_hover(event.pos)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, b in enumerate(self.menu_buttons):
                        if b.is_clicked(event.pos):
                            self.state = [GAME_COMPARE, GAME_GUESS, GAME_BLACKJACK][i]
                            # 重置游戏
                            [self.compare_game, self.guess_game,
                             self.blackjack_game][i].reset()
            elif self.state == GAME_COMPARE:
                result = self.compare_game.handle_event(event)
                if result == "menu":
                    self.state = MENU
            elif self.state == GAME_GUESS:
                result = self.guess_game.handle_event(event)
                if result == "menu":
                    self.state = MENU
            elif self.state == GAME_BLACKJACK:
                result = self.blackjack_game.handle_event(event)
                if result == "menu":
                    self.state = MENU
                # 处理开始按钮
                if (self.blackjack_game.state == "ready" and
                        event.type == pygame.MOUSEBUTTONDOWN):
                    if hasattr(self.blackjack_game, '_start_btn'):
                        if self.blackjack_game._start_btn.is_clicked(event.pos):
                            self.blackjack_game._new_round()
        return True

    def update(self):
        if self.state == GAME_COMPARE:
            self.compare_game.update()
        elif self.state == GAME_GUESS:
            self.guess_game.update()
        elif self.state == GAME_BLACKJACK:
            self.blackjack_game.update()

    def draw(self):
        if self.state == MENU:
            self._draw_menu()
        elif self.state == GAME_COMPARE:
            self.compare_game.draw()
        elif self.state == GAME_GUESS:
            self.guess_game.draw()
        elif self.state == GAME_BLACKJACK:
            self.blackjack_game.draw()
        pygame.display.flip()

    def _draw_menu(self):
        self.screen.fill(DARK_BG)
        # 标题
        title = self.big_font.render("骰子游戏合集", True, GOLD)
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 60))

        # 装饰骰子
        dice_r = DiceRenderer()
        dice_r.num_dice = 3
        dice_r.current_values = [5, 3, 6]
        dice_r.draw(self.screen, SCREEN_W // 2, 130, 40)

        # 游戏说明
        descs = [
            "玩家和电脑各掷骰子比大小",
            "猜两个骰子的总和",
            "掷骰子尽量接近21点"
        ]
        for i, desc in enumerate(descs):
            txt = self.small_font.render(desc, True, LIGHT_GRAY)
            self.screen.blit(txt, (SCREEN_W // 2 - txt.get_width() // 2, 218 + i * 80))

        for b in self.menu_buttons:
            b.draw(self.screen, self.font)

        # 底部提示
        hint = self.small_font.render("点击选择游戏 | ESC 返回菜单", True, GRAY)
        self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, SCREEN_H - 30))

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = DiceGames()
    game.run()
