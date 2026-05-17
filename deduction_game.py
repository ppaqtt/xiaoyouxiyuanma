#!/usr/bin/env python3
"""
弹丸风格推理游戏 - 猜数字密码
系统随机选择一个4位数字密码（1-6），玩家猜测并得到反馈
10次机会内猜出密码
"""

import pygame
import os
import sys
import random
import math

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
WIDTH, HEIGHT = 700, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("弹丸推理 - 猜数字密码")

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 220, 50)
PURPLE = (150, 50, 200)
ORANGE = (240, 150, 30)
CYAN = (0, 200, 200)
DARK_GRAY = (50, 50, 50)
GRAY = (120, 120, 120)
LIGHT_GRAY = (180, 180, 180)
DARK_BG = (25, 25, 40)
PANEL_BG = (35, 35, 55)
PANEL_BORDER = (80, 80, 120)

# 数字颜色（1-6对应不同颜色）
NUM_COLORS = {
    1: (220, 60, 60),    # 红
    2: (60, 140, 220),   # 蓝
    3: (60, 200, 60),    # 绿
    4: (240, 180, 30),   # 黄
    5: (180, 60, 220),   # 紫
    6: (240, 130, 30),   # 橙
}

# 游戏参数
CODE_LENGTH = 4
MAX_GUESSES = 10
NUM_RANGE = (1, 6)  # 数字范围

# 字体
font_large = pygame.font.SysFont("simhei", 40, bold=True)
font_medium = pygame.font.SysFont("simhei", 26)
font_small = pygame.font.SysFont("simhei", 20)
font_tiny = pygame.font.SysFont("simhei", 16)
font_num = pygame.font.SysFont("arial", 28, bold=True)
font_num_large = pygame.font.SysFont("arial", 36, bold=True)


class GuessRow:
    """猜测行类"""

    def __init__(self, index):
        self.index = index
        self.guess = [0, 0, 0, 0]  # 当前猜测
        self.bulls = 0  # 位置和数字都正确
        self.cows = 0   # 数字正确但位置错误
        self.submitted = False
        self.anim_progress = 0  # 动画进度

    def calculate_feedback(self, secret):
        """计算反馈（公牛和母牛）"""
        bulls = 0
        cows = 0
        secret_copy = list(secret)
        guess_copy = list(self.guess)

        # 先计算公牛（位置正确）
        for i in range(CODE_LENGTH):
            if guess_copy[i] == secret_copy[i]:
                bulls += 1
                secret_copy[i] = -1
                guess_copy[i] = -2

        # 再计算母牛（数字正确位置错误）
        for i in range(CODE_LENGTH):
            if guess_copy[i] > 0 and guess_copy[i] in secret_copy:
                cows += 1
                secret_copy[secret_copy.index(guess_copy[i])] = -1

        self.bulls = bulls
        self.cows = cows
        self.submitted = True


class DeductionGame:
    """弹丸推理游戏主类"""

    def __init__(self):
        self.state = "menu"  # menu, playing, win, lose
        self.guess_rows = []
        self.secret = []
        self.current_row = 0
        self.selected_slot = 0
        self.anim_timer = 0
        self.shake_timer = 0
        self.particles = []
        self.reveal_timer = 0
        self.reset_game()

    def reset_game(self):
        """重置游戏"""
        self.secret = [random.randint(*NUM_RANGE) for _ in range(CODE_LENGTH)]
        self.guess_rows = [GuessRow(i) for i in range(MAX_GUESSES)]
        self.current_row = 0
        self.selected_slot = 0
        self.anim_timer = 0
        self.shake_timer = 0
        self.particles = []
        self.reveal_timer = 0

    def create_particles(self, x, y, color, count=15):
        """创建庆祝粒子"""
        for _ in range(count):
            self.particles.append({
                'x': x, 'y': y,
                'vx': random.uniform(-4, 4),
                'vy': random.uniform(-6, -1),
                'life': random.randint(30, 60),
                'max_life': 60,
                'color': color,
                'size': random.randint(3, 7)
            })

    def submit_guess(self):
        """提交当前猜测"""
        row = self.guess_rows[self.current_row]

        # 检查是否所有位置都已填入数字
        if 0 in row.guess:
            self.shake_timer = 15
            return

        row.calculate_feedback(self.secret)
        self.anim_timer = 30

        # 检查是否猜对
        if row.bulls == CODE_LENGTH:
            self.state = "win"
            self.reveal_timer = 0
            # 庆祝粒子
            for _ in range(5):
                self.create_particles(
                    random.randint(100, WIDTH - 100),
                    random.randint(200, 400),
                    random.choice(list(NUM_COLORS.values())),
                    20
                )
        elif self.current_row >= MAX_GUESSES - 1:
            self.state = "lose"
            self.reveal_timer = 0
        else:
            self.current_row += 1
            self.selected_slot = 0

    def handle_input(self, event):
        """处理输入"""
        if event.type == pygame.KEYDOWN:
            if self.state == "menu":
                if event.key == pygame.K_RETURN:
                    self.state = "playing"
                    self.reset_game()
            elif self.state == "playing":
                # 数字键1-6输入
                if event.key in (pygame.K_1, pygame.K_KP1):
                    self.set_number(1)
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    self.set_number(2)
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    self.set_number(3)
                elif event.key in (pygame.K_4, pygame.K_KP4):
                    self.set_number(4)
                elif event.key in (pygame.K_5, pygame.K_KP5):
                    self.set_number(5)
                elif event.key in (pygame.K_6, pygame.K_KP6):
                    self.set_number(6)
                # 左右移动选择位置
                elif event.key == pygame.K_LEFT:
                    self.selected_slot = max(0, self.selected_slot - 1)
                elif event.key == pygame.K_RIGHT:
                    self.selected_slot = min(CODE_LENGTH - 1, self.selected_slot + 1)
                # 回车提交
                elif event.key == pygame.K_RETURN:
                    self.submit_guess()
                # 退格删除
                elif event.key == pygame.K_BACKSPACE:
                    row = self.guess_rows[self.current_row]
                    row.guess[self.selected_slot] = 0
                # R重新开始
                elif event.key == pygame.K_r:
                    self.reset_game()
            elif self.state in ("win", "lose"):
                if event.key == pygame.K_RETURN:
                    self.state = "playing"
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"

        # 鼠标点击数字选择面板
        if self.state == "playing" and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # 检查是否点击了数字面板
            panel_y = HEIGHT - 100
            for i, num in enumerate(range(1, 7)):
                bx = WIDTH // 2 - 150 + i * 60
                by = panel_y
                if bx <= mx <= bx + 45 and by <= my <= by + 45:
                    self.set_number(num)
                    break

            # 检查是否点击了当前行的某个位置
            row_y = 130 + self.current_row * 52
            for j in range(CODE_LENGTH):
                sx = 120 + j * 65
                if sx <= mx <= sx + 50 and row_y <= my <= row_y + 45:
                    self.selected_slot = j
                    break

            # 检查是否点击了提交按钮
            submit_x = 420
            submit_y = 130 + self.current_row * 52
            if submit_x <= mx <= submit_x + 80 and submit_y <= my <= submit_y + 45:
                self.submit_guess()

    def set_number(self, num):
        """设置当前位置的数字"""
        row = self.guess_rows[self.current_row]
        row.guess[self.selected_slot] = num
        # 自动移到下一个位置
        if self.selected_slot < CODE_LENGTH - 1:
            self.selected_slot += 1

    def update(self):
        """更新游戏逻辑"""
        if self.anim_timer > 0:
            self.anim_timer -= 1
        if self.shake_timer > 0:
            self.shake_timer -= 1
        if self.reveal_timer < 60:
            self.reveal_timer += 1

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
        else:
            self.draw_game(surface)
            if self.state == "win":
                self.draw_result(surface, True)
            elif self.state == "lose":
                self.draw_result(surface, False)

    def draw_menu(self, surface):
        """绘制菜单"""
        # 标题
        title = font_large.render("弹丸推理", True, WHITE)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        subtitle = font_medium.render("猜数字密码", True, CYAN)
        surface.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 135))

        pygame.draw.line(surface, PURPLE, (200, 175), (500, 175), 2)

        # 规则说明
        rules = [
            "系统随机生成一个4位数字密码（数字范围1-6）",
            "你有10次机会来猜出这个密码",
            "每次猜测后你会得到反馈：",
            "",
            "  红色标记 = 数字和位置都正确（公牛）",
            "  白色标记 = 数字正确但位置错误（母牛）",
            "",
            "用数字键1-6输入，方向键移动位置",
            "按 Enter 提交猜测",
            "",
            "按 Enter 开始游戏"
        ]
        for i, text in enumerate(rules):
            if "红色标记" in text:
                color = RED
            elif "白色标记" in text:
                color = WHITE
            elif "Enter 开始" in text:
                color = YELLOW
            else:
                color = LIGHT_GRAY
            t = font_tiny.render(text, True, color)
            surface.blit(t, (WIDTH // 2 - t.get_width() // 2, 200 + i * 28))

        # 装饰性密码展示
        for i in range(4):
            x = WIDTH // 2 - 90 + i * 55
            y = 560
            color = list(NUM_COLORS.values())[i]
            pygame.draw.circle(surface, color, (x + 22, y + 22), 22)
            pygame.draw.circle(surface, WHITE, (x + 22, y + 22), 22, 2)
            q = font_num.render("?", True, WHITE)
            surface.blit(q, (x + 22 - q.get_width() // 2, y + 22 - q.get_height() // 2))

    def draw_game(self, surface):
        """绘制游戏画面"""
        # 标题栏
        title = font_medium.render("弹丸推理", True, WHITE)
        surface.blit(title, (20, 15))

        # 剩余次数
        remaining = MAX_GUESSES - self.current_row
        if self.state == "playing":
            remain_text = font_small.render(f"剩余机会: {remaining}", True,
                                            RED if remaining <= 3 else WHITE)
            surface.blit(remain_text, (WIDTH - 180, 18))

        # 分隔线
        pygame.draw.line(surface, PANEL_BORDER, (20, 50), (WIDTH - 20, 50), 1)

        # 绘制猜测行
        shake_offset = 0
        if self.shake_timer > 0:
            shake_offset = math.sin(self.shake_timer * 2) * 5

        for i in range(MAX_GUESSES):
            row = self.guess_rows[i]
            row_y = 65 + i * 52
            is_current = (i == self.current_row and self.state == "playing")

            # 行背景
            bg_color = PANEL_BG if is_current else (30, 30, 45)
            if is_current:
                row_x = int(shake_offset)
            else:
                row_x = 0

            pygame.draw.rect(surface, bg_color,
                             (15 + row_x, row_y, WIDTH - 30, 48),
                             border_radius=6)
            if is_current:
                pygame.draw.rect(surface, PANEL_BORDER,
                                 (15 + row_x, row_y, WIDTH - 30, 48),
                                 2, border_radius=6)

            # 行号
            num_text = font_tiny.render(f"{i + 1:2d}", True, GRAY)
            surface.blit(num_text, (25 + row_x, row_y + 14))

            # 绘制4个数字槽
            for j in range(CODE_LENGTH):
                sx = 70 + j * 65 + row_x
                sy = row_y + 4
                num = row.guess[j]

                # 槽位背景
                slot_color = (50, 50, 70)
                if is_current and j == self.selected_slot:
                    # 选中状态 - 闪烁效果
                    pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 30
                    slot_color = (60 + int(pulse), 60 + int(pulse), 90 + int(pulse))

                pygame.draw.rect(surface, slot_color, (sx, sy, 50, 40), border_radius=8)

                if num > 0:
                    # 绘制数字球
                    color = NUM_COLORS[num]
                    pygame.draw.circle(surface, color, (sx + 25, sy + 20), 17)
                    # 高光
                    pygame.draw.circle(surface, tuple(min(255, c + 80) for c in color),
                                       (sx + 20, sy + 15), 6)
                    # 数字
                    nt = font_num.render(str(num), True, WHITE)
                    surface.blit(nt, (sx + 25 - nt.get_width() // 2,
                                      sy + 20 - nt.get_height() // 2))
                elif is_current and j == self.selected_slot:
                    # 空位提示
                    hint = font_num.render("_", True, GRAY)
                    surface.blit(hint, (sx + 25 - hint.get_width() // 2,
                                        sy + 20 - hint.get_height() // 2))

            # 提交按钮（仅当前行）
            if is_current:
                btn_x = 340 + row_x
                btn_y = row_y + 8
                btn_rect = pygame.Rect(btn_x, btn_y, 70, 32)
                # 检查鼠标悬停
                mx, my = pygame.mouse.get_pos()
                hover = btn_rect.collidepoint(mx, my)
                btn_color = (80, 80, 140) if hover else (60, 60, 100)
                pygame.draw.rect(surface, btn_color, btn_rect, border_radius=5)
                pygame.draw.rect(surface, PANEL_BORDER, btn_rect, 1, border_radius=5)
                btn_text = font_tiny.render("提交", True, WHITE)
                surface.blit(btn_text, (btn_x + 35 - btn_text.get_width() // 2,
                                        btn_y + 16 - btn_text.get_height() // 2))

            # 绘制反馈（已提交的行）
            if row.submitted:
                feedback_x = 430
                # 公牛（红色标记）
                for b in range(row.bulls):
                    pygame.draw.circle(surface, RED, (feedback_x + b * 22, row_y + 24), 8)
                    pygame.draw.circle(surface, (255, 100, 100),
                                       (feedback_x + b * 22 - 2, row_y + 22), 3)

                # 母牛（白色标记）
                for c in range(row.cows):
                    cx = feedback_x + (row.bulls + c) * 22
                    pygame.draw.circle(surface, WHITE, (cx, row_y + 24), 8)
                    pygame.draw.circle(surface, LIGHT_GRAY, (cx - 2, row_y + 22), 3)

                # 反馈文字
                fb_text = font_tiny.render(f"{row.bulls}A{row.cows}B", True, LIGHT_GRAY)
                surface.blit(fb_text, (feedback_x + 100, row_y + 14))

        # 数字选择面板
        self.draw_number_panel(surface)

        # 操作提示
        if self.state == "playing":
            hint = font_tiny.render("数字键1-6输入 | 左右键移动 | Enter提交 | Backspace删除",
                                    True, GRAY)
            surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 30))

    def draw_number_panel(self, surface):
        """绘制数字选择面板"""
        panel_y = HEIGHT - 100

        # 面板背景
        pygame.draw.rect(surface, PANEL_BG,
                         (WIDTH // 2 - 180, panel_y - 15, 360, 65),
                         border_radius=8)
        pygame.draw.rect(surface, PANEL_BORDER,
                         (WIDTH // 2 - 180, panel_y - 15, 360, 65),
                         1, border_radius=8)

        mx, my = pygame.mouse.get_pos()

        for i, num in enumerate(range(1, 7)):
            bx = WIDTH // 2 - 150 + i * 60
            by = panel_y
            color = NUM_COLORS[num]

            # 鼠标悬停效果
            hover = bx <= mx <= bx + 45 and by <= my <= by + 45
            size = 22 if hover else 20

            pygame.draw.circle(surface, color, (bx + 22, by + 22), size)
            if hover:
                pygame.draw.circle(surface, WHITE, (bx + 22, by + 22), size, 2)

            # 高光
            pygame.draw.circle(surface, tuple(min(255, c + 80) for c in color),
                               (bx + 17, by + 17), 6)

            # 数字
            nt = font_num.render(str(num), True, WHITE)
            surface.blit(nt, (bx + 22 - nt.get_width() // 2,
                              by + 22 - nt.get_height() // 2))

    def draw_result(self, surface, is_win):
        """绘制结果画面"""
        # 半透明遮罩
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # 绘制粒子
        for p in self.particles:
            alpha = p['life'] / p['max_life']
            size = max(1, int(p['size'] * alpha))
            pygame.draw.circle(surface, p['color'], (int(p['x']), int(p['y'])), size)

        # 结果面板
        panel_rect = pygame.Rect(WIDTH // 2 - 200, 200, 400, 300)
        pygame.draw.rect(surface, PANEL_BG, panel_rect, border_radius=15)
        pygame.draw.rect(surface, PANEL_BORDER, panel_rect, 2, border_radius=15)

        if is_win:
            result_text = font_large.render("破解成功!", True, GREEN)
        else:
            result_text = font_large.render("破解失败", True, RED)
        surface.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, 220))

        # 显示密码
        label = font_small.render("密码是:", True, LIGHT_GRAY)
        surface.blit(label, (WIDTH // 2 - label.get_width() // 2, 285))

        for i, num in enumerate(self.secret):
            x = WIDTH // 2 - 90 + i * 55
            y = 315
            color = NUM_COLORS[num]
            pygame.draw.circle(surface, color, (x + 22, y + 22), 22)
            pygame.draw.circle(surface, WHITE, (x + 22, y + 22), 22, 2)
            nt = font_num_large.render(str(num), True, WHITE)
            surface.blit(nt, (x + 22 - nt.get_width() // 2, y + 22 - nt.get_height() // 2))

        # 统计
        guesses_used = self.current_row + (1 if is_win else 0)
        if not is_win:
            guesses_used = MAX_GUESSES
        stat = font_small.render(f"使用了 {guesses_used} 次猜测", True, WHITE)
        surface.blit(stat, (WIDTH // 2 - stat.get_width() // 2, 370))

        # 提示
        hint1 = font_small.render("按 Enter 再来一局", True, YELLOW)
        hint2 = font_small.render("按 ESC 返回菜单", True, GRAY)
        surface.blit(hint1, (WIDTH // 2 - hint1.get_width() // 2, 420))
        surface.blit(hint2, (WIDTH // 2 - hint2.get_width() // 2, 450))


def main():
    """主函数"""
    clock = pygame.time.Clock()
    game = DeductionGame()

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
