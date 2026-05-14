# -*- coding: utf-8 -*-
"""
密码破译游戏 - Code Breaker Game
一款融合密码学知识的解密挑战游戏，玩家需要破译各种经典密码
"""

import pygame
import sys
import random
import string

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# 颜色定义
BG_COLOR = (25, 25, 45)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (0, 255, 128)
ERROR_COLOR = (255, 80, 80)
SUCCESS_COLOR = (80, 255, 80)
BUTTON_COLOR = (60, 60, 100)
BUTTON_HOVER_COLOR = (80, 80, 130)
TITLE_COLOR = (0, 200, 255)
HINT_COLOR = (200, 200, 100)

# 设置字体
pygame.font.init()
try:
    FONT = pygame.font.Font("simsun.ttc", 24)
    TITLE_FONT = pygame.font.Font("simsun.ttc", 42)
    SMALL_FONT = pygame.font.Font("simsun.ttc", 18)
    LARGE_FONT = pygame.font.Font("simsun.ttc", 32)
except:
    FONT = pygame.font.SysFont("simhei", 24)
    TITLE_FONT = pygame.font.SysFont("simhei", 42)
    SMALL_FONT = pygame.font.SysFont("simhei", 18)
    LARGE_FONT = pygame.font.SysFont("simhei", 32)

# 密码学知识介绍
CIPHER_INFO = {
    "凯撒密码": """
【凯撒密码 Caesar Cipher】

凯撒密码是一种最简单且最广为人知的加密技术。

它是一种替换加密技术，明文中的所有字母都在字母表上
基于一个固定数目进行偏移。

例如：当偏移量为3时，A会被替换成D，B变成E，
以此类推，X变成A。

历史背景：
古罗马的尤利乌斯·凯撒（Julius Caesar）曾使用
此方法来与将军们进行秘密通信。
    """,
    "栅栏密码": """
【栅栏密码 Rail Fence Cipher】

栅栏密码是一种简单的换位密码。

加密方法：
将明文按照一定的规则填入多行，
然后按行读取来产生密文。

例如：将 "WEAREDISCOVEREDFLEEATONCE" 填入3行栅栏：
W . . . E . . . C . . . R . . . L . . . T . . . E
. E . R . D . S . O . E . E . F . E . A . O . C .
. . A . . . I . . . V . . . D . . . N . . . . .

按行读取得到密文。
    """,
    "维吉尼亚密码": """
【维吉尼亚密码 Vigenere Cipher】

维吉尼亚密码是凯撒密码的升级版。

它使用一个关键字来生成不同的偏移量。
每个字母使用不同的偏移量进行加密。

例如：明文 "HELLO"，关键字 "KEY"
H偏移K(10)位 -> R
E偏移E(4)位 -> I
L偏移Y(24)位 -> J
L偏移K(10)位 -> V
O偏移E(4)位 -> S

密文："RIJVS"

历史背景：
16世纪由法国外交官布莱斯·德·维吉尼亚发明。
曾被认为是不可破解的密码，直到19世纪被破解。
    """,
    "猪圈密码": """
【猪圈密码 Pigpen Cipher】

猪圈密码是一种以图形为基础的替代密码。

它使用一系列的符号来表示字母：

┌─┐   .━.
│▒│   ┃▒┃
└─┘   ━┛
类似这样的符号组合代表不同的字母。

历史背景：
这种密码据说是由Freemasons在18世纪发明的，
所以也被称为"共济会密码"。

它的优点是容易记忆和书写，
缺点是密文比较显眼，容易被发现。
    """,
    "摩斯电码": """
【摩斯电码 Morse Code】

摩斯电码是一种时断时续的信号代码，
通过不同的排列顺序来表达不同的英文字母、数字和标点。

基本符号：
- 点(·)：短促的信号
- 划(━)：持久的信号

例如：
A = ·━
B = ━···
C = ━·━·
D = ━··
E = ·
F = ··━·
...

用途：
广泛用于电报通信、航海通信等领域。
SOS求救信号：···━━━···

学习摩斯电码可以锻炼记忆力和注意力！
    """,
    "base64编码": """
【Base64编码 Base64 Encoding】

Base64是一种基于64个可打印字符来表示
二进制数据的方法。

64个字符包括：
A-Z (26个)、a-z (26个)、0-9 (10个)、+、/

原理：
将3个字节的二进制数据分成4个6位的块，
每个块对应一个Base64字符。

用途：
- 电子邮件的附件编码
- URL中特殊字符的处理
- 数据传输和存储

注意：Base64不是加密，只是一种编码方式！
    """,
    "培根密码": """
【培根密码 Bacon Cipher】

培根密码由英国哲学家弗朗西斯·培根发明。

它使用两种不同样式的字母（A和B）来表示文本。

基本对应表：
A = aaaaa   G = abbba   M = baaaa   T = babab
B = aaaab   H = abbab   N = baaab   U/V = babaa
C = aaaba   I/J = abbaa O = baaba   W = babba
D = aaabb   K = abbab   P = baabb   X = babbb
E = aabaa   L = abbaa   Q = baabb   Y = babba
F = aabab   L = abbaa   R = baaab   Z = babbb

示例："HELLO" 可以用不同的字体样式来隐藏表示。
    """,
    "打字机密码": """
【打字机密码 Typewriter Cipher】

这是一种使用键盘布局规律创造的密码。

常见规律：
1. QWERTY密码：将字母按键盘行错位
2. 打字机密码：相邻字母互换

例如：明文 "SECRET"
按某种键盘偏移后可能变成其他形式。

特点：
- 简单易学
- 依赖键盘布局
- 适合快速加密

常用于娱乐和简单信息隐藏。
    """
}


class Button:
    """按钮类"""
    def __init__(self, x, y, width, height, text, callback, color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.is_hovered = False
        self.color = color or BUTTON_COLOR

    def draw(self, surface):
        color = self.color if not self.is_hovered else BUTTON_HOVER_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, self.rect, 1, border_radius=8)

        text_surface = FONT.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered:
            self.callback()


class InputBox:
    """输入框类"""
    def __init__(self, x, y, width, height, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def draw(self, surface):
        color = HIGHLIGHT_COLOR if self.active else TEXT_COLOR
        pygame.draw.rect(surface, (40, 40, 60), self.rect, border_radius=8)
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=8)

        if self.text:
            text_surface = FONT.render(self.text, True, TEXT_COLOR)
            surface.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))
        elif not self.active:
            placeholder_surface = FONT.render(self.placeholder, True, (100, 100, 100))
            surface.blit(placeholder_surface, (self.rect.x + 10, self.rect.y + 10))

        # 光标
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 10 + FONT.render(self.text, True, TEXT_COLOR).get_width()
            pygame.draw.line(surface, TEXT_COLOR, (cursor_x, self.rect.y + 8),
                          (cursor_x, self.rect.y + self.rect.height - 8), 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            elif event.unicode and len(self.text) < 30:
                self.text += event.unicode
        return False

    def update(self):
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0


class CodeBreakerGame:
    """密码破译游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("密码破译大师 - Code Breaker")
        self.clock = pygame.time.Clock()

        # 游戏状态
        self.current_level = 1
        self.max_level = 8
        self.score = 0
        self.streak = 0  # 连续答对
        self.mode = "menu"  # menu, playing, learn, result
        self.current_cipher = None
        self.cipher_text = ""
        self.answer = ""
        self.hint_level = 0
        self.max_hints = 3
        self.show_info = False
        self.info_text = ""

        # 密文和答案
        self.cipher_data = self.generate_cipher_data()

        # UI元素
        self.buttons = []
        self.input_box = None
        self.message = ""
        self.message_timer = 0
        self.show_success = False
        self.success_timer = 0

    def generate_cipher_data(self):
        """生成密码数据"""
        data = {}

        # 1. 凯撒密码
        caesar_pairs = [
            ("加密是保护信息安全的重要手段", "MJJXTIWGMWZIEPJSKIXDMJGISRXV"),
            ("努力学习密码学知识", "SXYVLSYWITPIZIVQMGEHI"),
            ("信息安全关乎每个人", "LQIVQIRXIHWIHYREZIV"),
            ("密码破译需要智慧和耐心", "WLVJGLYHIHWZMGLJLITIZ"),
            ("古典密码充满智慧", "JXDLXZWLJFPIFRXLMJ")
        ]
        data["凯撒密码"] = random.choice(caesar_pairs)

        # 2. 栅栏密码
        rail_pairs = [
            ("密码学真有趣", "码真学密趣有"),
            ("挑战大脑极限", "挑战限脑大极"),
            ("学习使人进步", "学使人步进习"),
            ("解密需要技巧", "需要技巧解密"),
            ("知识就是力量", "知就是量识力")
        ]
        data["栅栏密码"] = random.choice(rail_pairs)

        # 3. 维吉尼亚密码
        vig_pairs = [
            ("学习密码学", "SSBWKOKGI"),
            ("挑战自我", "HQSSUWHG"),
            ("智慧无敌", "JSIHTSGH"),
            ("解密成功", "BWVHBYJV"),
            ("密码破译", "HNSFBKIZW")
        ]
        data["维吉尼亚密码"] = random.choice(vig_pairs)

        # 4. 猪圈密码
        pigpen_pairs = [
            ("密码", "�📗📕📗"),
            ("学习", "📗📕📗📘"),
            ("挑战", "📙📕📘📘"),
            ("智慧", "📗📕📕📘"),
            ("解密", "📙📗📘📘")
        ]
        data["猪圈密码"] = random.choice(pigpen_pairs)

        # 5. 摩斯电码
        morse_pairs = [
            ("HELLO", "···· · −·· −·· −−−"),
            ("CIPHER", "−·−· ··· −−· · · −·−· · −·−·"),
            ("SECRET", "··· · −·−· · ·−· −"),
            ("DECODE", "−·· · −−− −·· ·"),
            ("PUZZLE", "·−−− ·−−− −−−· ·−·· · −·· ·")
        ]
        data["摩斯电码"] = random.choice(morse_pairs)

        # 6. Base64
        base64_pairs = [
            ("CODE", "Q09ERQ=="),
            ("DATA", "REFUQQ=="),
            ("KEY", "S0VZ"),
            ("SECRET", "U0VDUkVU"),
            ("ENCODE", "RU5DT0RF")
        ]
        data["base64编码"] = random.choice(base64_pairs)

        # 7. 培根密码
        bacon_pairs = [
            ("ACE", "AAAAA AABAB AABAA"),
            ("BIG", "AAAAA AABBB BAAAB"),
            ("CAT", "AAABA AAAAA BAABB"),
            ("DOG", "AAABB AABAA ABBAA"),
            ("SUN", "BAAAB BAABB AABAA")
        ]
        data["培根密码"] = random.choice(bacon_pairs)

        # 8. 打字机密码
        typewriter_pairs = [
            ("秘密", "托运"),
            ("密码", "拉针"),
            ("学习", "兴组"),
            ("挑战", "投肩"),
            ("智慧", "资会")
        ]
        data["打字机密码"] = random.choice(typewriter_pairs)

        return data

    def get_hint(self):
        """获取提示"""
        hints = {
            "凯撒密码": [
                "提示1：这是一个字母偏移密码，试试将每个字母向前移动几位...",
                "提示2：偏移量可能是3、5或7...",
                "提示3：试试将密文中每个字母向前移动3位（A→D）..."
            ],
            "栅栏密码": [
                "提示1：这是将文字按某种规律重新排列的密码...",
                "提示2：尝试按2行或3行的方式读取...",
                "提示3：按奇偶位置交替读取..."
            ],
            "维吉尼亚密码": [
                "提示1：这是一个循环使用密钥的密码...",
                "提示2：密钥可能是 'KEY' 或 'SECRET'...",
                "提示3：每个字母的偏移量由密钥对应字符决定..."
            ],
            "猪圈密码": [
                "提示1：这是用符号图形表示的密码...",
                "提示2：每个符号对应一个字母，参考中文提示的符号...",
                "提示3：将符号转换为对应的英文字母..."
            ],
            "摩斯电码": [
                "提示1：点代表短信号，划代表长信号...",
                "提示2：每个字母由点和划组成，E是一个点...",
                "提示3：H=···· I=·· S=··· O=−−−..."
            ],
            "base64编码": [
                "提示1：这是一种二进制到文本的编码方式...",
                "提示2：特征是只用字母、数字和+、=符号...",
                "提示3：解码方法是将字符转为6位二进制，然后每8位为一个字节..."
            ],
            "培根密码": [
                "提示1：这是用两种字母样式表示的密码...",
                "提示2：A和B（或不同字体）代表二进制...",
                "提示3：AAAAA=A, AABAB=B, AAABA=C..."
            ],
            "打字机密码": [
                "提示1：这是基于键盘布局的密码...",
                "提示2：每个字由键盘上相邻的键表示...",
                "提示3：想想每个字对应键盘的哪个键..."
            ]
        }

        if self.current_cipher in hints and self.hint_level < self.max_hints:
            hint = hints[self.current_cipher][self.hint_level]
            self.hint_level += 1
            return hint
        return ""

    def load_level(self):
        """加载关卡"""
        cipher_names = list(CIPHER_INFO.keys())
        self.current_cipher = cipher_names[self.current_level - 1]

        if self.current_cipher in self.cipher_data:
            pair = self.cipher_data[self.current_cipher]
            if self.current_cipher in ["凯撒密码", "维吉尼亚密码", "猪圈密码"]:
                self.cipher_text = pair[1]
                self.answer = pair[0].upper()
            elif self.current_cipher in ["摩斯电码", "base64编码", "培根密码"]:
                self.cipher_text = pair[1]
                self.answer = pair[0]
            elif self.current_cipher == "栅栏密码":
                self.cipher_text = pair[1]
                self.answer = pair[0]
            elif self.current_cipher == "打字机密码":
                self.cipher_text = pair[1]
                self.answer = pair[0]
        else:
            self.cipher_text = "未知密文"
            self.answer = ""

        self.hint_level = 0
        self.message = ""
        self.show_success = False

    def check_answer(self, user_answer):
        """检查答案"""
        user_answer = user_answer.strip().upper()
        correct = user_answer == self.answer.upper()

        if correct:
            self.score += 100 + self.streak * 20
            self.streak += 1
            self.message = f"正确！+{100 + (self.streak-1)*20}分！"
            self.show_success = True
            self.success_timer = 60
        else:
            self.streak = 0
            self.message = f"错误！正确答案是：{self.answer}"
            self.show_success = False

        self.message_timer = 180
        return correct

    def draw_menu(self):
        """绘制主菜单"""
        self.screen.fill(BG_COLOR)

        # 标题
        title = TITLE_FONT.render("密码破译大师", True, TITLE_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)

        subtitle = FONT.render("Code Breaker - 密码学知识挑战", True, HIGHLIGHT_COLOR)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 160))
        self.screen.blit(subtitle, subtitle_rect)

        # 密码类型列表
        y_pos = 230
        header = SMALL_FONT.render("=== 可破解的密码类型 ===", True, HINT_COLOR)
        self.screen.blit(header, (SCREEN_WIDTH//2 - header.get_width()//2, y_pos))

        y_pos += 50
        cipher_names = list(CIPHER_INFO.keys())
        for i, name in enumerate(cipher_names):
            color = TEXT_COLOR if i < self.current_level else (100, 100, 100)
            text = f"  {i+1}. {name} {'✓' if i < self.current_level else '🔒'}"
            surface = SMALL_FONT.render(text, True, color)
            self.screen.blit(surface, (SCREEN_WIDTH//2 - 150, y_pos + i * 35))

        # 按钮
        self.draw_button("开始挑战", 350, 600, self.start_game, HIGHLIGHT_COLOR)
        self.draw_button("学习密码知识", 520, 600, self.show_learn, (100, 200, 100))
        self.draw_button("重置进度", 380, 650, self.reset_progress, ERROR_COLOR)

        # 分数显示
        score_text = FONT.render(f"当前分数: {self.score}", True, HIGHLIGHT_COLOR)
        self.screen.blit(score_text, (50, 50))

        # 最高关卡
        level_text = FONT.render(f"已解锁: {self.current_level}/{self.max_level} 关", True, TEXT_COLOR)
        self.screen.blit(level_text, (50, 85))

    def draw_playing(self):
        """绘制游戏界面"""
        self.screen.fill(BG_COLOR)

        # 顶部信息
        level_text = LARGE_FONT.render(f"第 {self.current_level} 关", True, TITLE_COLOR)
        self.screen.blit(level_text, (50, 30))

        score_text = FONT.render(f"分数: {self.score}", True, HIGHLIGHT_COLOR)
        self.screen.blit(score_text, (SCREEN_WIDTH - 180, 30))

        streak_text = FONT.render(f"连击: {self.streak}", True, (255, 200, 0))
        self.screen.blit(streak_text, (SCREEN_WIDTH - 180, 65))

        # 密码类型
        cipher_name = SMALL_FONT.render(f"密码类型: {self.current_cipher}", True, HINT_COLOR)
        self.screen.blit(cipher_name, (SCREEN_WIDTH//2 - cipher_name.get_width()//2, 100))

        # 密文显示区域
        pygame.draw.rect(self.screen, (35, 35, 55), (50, 150, SCREEN_WIDTH-100, 200), border_radius=15)
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, (50, 150, SCREEN_WIDTH-100, 200), 2, border_radius=15)

        # 密文
        cipher_label = SMALL_FONT.render("【密文】", True, ERROR_COLOR)
        self.screen.blit(cipher_label, (70, 165))

        # 密文内容
        cipher_display = LARGE_FONT.render(self.cipher_text, True, TEXT_COLOR)
        cipher_rect = cipher_display.get_rect(center=(SCREEN_WIDTH//2, 250))
        self.screen.blit(cipher_display, cipher_rect)

        # 输入区域
        input_label = SMALL_FONT.render("请输入解密后的明文:", True, TEXT_COLOR)
        self.screen.blit(input_label, (50, 380))

        # 输入框
        if self.input_box:
            self.input_box.rect = pygame.Rect(50, 410, SCREEN_WIDTH - 300, 50)
            self.input_box.draw(self.screen)

        # 提交按钮
        self.draw_button("提交答案", SCREEN_WIDTH - 230, 410, self.submit_answer, HIGHLIGHT_COLOR)

        # 提示按钮
        hint_color = (150, 150, 50) if self.hint_level < self.max_hints else (80, 80, 80)
        hint_text = f"获取提示 ({self.max_hints - self.hint_level}次)"
        self.draw_button(hint_text, 50, 480, self.use_hint, hint_text != "获取提示 (0次)" and hint_color or (80, 80, 80))

        # 学习按钮
        self.draw_button("学习此密码", 200, 480, self.show_cipher_info, (100, 150, 100))

        # 消息显示
        if self.message_timer > 0:
            color = SUCCESS_COLOR if self.show_success else ERROR_COLOR
            msg_surface = FONT.render(self.message, True, color)
            msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH//2, 550))
            pygame.draw.rect(self.screen, (40, 40, 60), msg_rect.inflate(40, 20), border_radius=10)
            self.screen.blit(msg_surface, msg_rect)

        # 返回按钮
        self.draw_button("返回菜单", SCREEN_WIDTH - 150, 650, self.show_menu, TEXT_COLOR)

        # 提示显示
        if self.current_hint:
            hint_surface = SMALL_FONT.render(self.current_hint, True, HINT_COLOR)
            hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH//2, 620))
            self.screen.blit(hint_surface, hint_rect)

        # 下一关按钮
        if self.show_success and self.message_timer > 60:
            self.draw_button("下一关 ➜", SCREEN_WIDTH//2 - 80, 680, self.next_level, SUCCESS_COLOR)

    def draw_learn(self):
        """绘制学习界面"""
        self.screen.fill(BG_COLOR)

        # 标题
        title = TITLE_FONT.render("密码学知识库", True, TITLE_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title, title_rect)

        # 选择密码类型
        y_pos = 110
        cipher_names = list(CIPHER_INFO.keys())

        for i, name in enumerate(cipher_names):
            color = (100, 200, 100) if self.learn_selection == i else BUTTON_COLOR
            btn_rect = pygame.Rect(50, y_pos + i * 70, 200, 60)
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=10)

            text = FONT.render(name, True, TEXT_COLOR)
            text_rect = text.get_rect(center=btn_rect.center)
            self.screen.blit(text, text_rect)

            # 检测点击
            if self.learn_selection == i:
                pygame.draw.rect(self.screen, HIGHLIGHT_COLOR, btn_rect, 2, border_radius=10)

        # 显示选中密码的详细信息
        if self.learn_selection is not None:
            selected_name = cipher_names[self.learn_selection]
            info = CIPHER_INFO[selected_name]

            # 信息区域
            info_rect = pygame.Rect(270, 100, SCREEN_WIDTH - 320, SCREEN_HEIGHT - 150)
            pygame.draw.rect(self.screen, (35, 35, 55), info_rect, border_radius=15)

            # 绘制信息文本
            lines = info.strip().split('\n')
            y = info_rect.y + 20
            for line in lines:
                if line.strip():
                    color = TITLE_COLOR if '【' in line else TEXT_COLOR
                    if '例如' in line or '特点' in line or '用途' in line:
                        color = HIGHLIGHT_COLOR
                    surface = SMALL_FONT.render(line, True, color)
                    self.screen.blit(surface, (info_rect.x + 20, y))
                y += 28
                if y > info_rect.bottom - 30:
                    break

        # 返回按钮
        self.draw_button("返回菜单", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50, self.show_menu, TEXT_COLOR)

        # 交互检测
        for i in range(len(cipher_names)):
            btn_rect = pygame.Rect(50, 110 + i * 70, 200, 60)
            if btn_rect.collidepoint(pygame.mouse.get_pos()):
                if self.hover_cipher != i:
                    self.hover_cipher = i

    def draw_button(self, text, x, y, callback, color=None):
        """绘制按钮"""
        btn_rect = pygame.Rect(x, y, 130, 45)
        hover = btn_rect.collidepoint(pygame.mouse.get_pos())
        bg_color = color or (BUTTON_HOVER_COLOR if hover else BUTTON_COLOR)

        pygame.draw.rect(self.screen, bg_color, btn_rect, border_radius=8)
        surface = FONT.render(text, True, TEXT_COLOR)
        rect = surface.get_rect(center=btn_rect.center)
        self.screen.blit(surface, rect)

        # 检测点击
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and hover:
                callback()

    def draw(self):
        """绘制主方法"""
        if self.mode == "menu":
            self.draw_menu()
        elif self.mode == "playing":
            self.draw_playing()
        elif self.mode == "learn":
            self.draw_learn()
        elif self.mode == "result":
            self.draw_result()

        pygame.display.flip()

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                if self.mode == "menu":
                    # 开始按钮
                    if pygame.Rect(350, 600, 130, 45).collidepoint(mouse_pos):
                        self.start_game()
                    # 学习按钮
                    elif pygame.Rect(520, 600, 130, 45).collidepoint(mouse_pos):
                        self.show_learn()
                    # 重置按钮
                    elif pygame.Rect(380, 650, 130, 45).collidepoint(mouse_pos):
                        self.reset_progress()

                elif self.mode == "playing":
                    # 提交按钮
                    if pygame.Rect(SCREEN_WIDTH - 230, 410, 130, 50).collidepoint(mouse_pos):
                        self.submit_answer()
                    # 提示按钮
                    if pygame.Rect(50, 480, 130, 45).collidepoint(mouse_pos):
                        self.use_hint()
                    # 学习按钮
                    elif pygame.Rect(200, 480, 130, 45).collidepoint(mouse_pos):
                        self.show_cipher_info()
                    # 返回按钮
                    elif pygame.Rect(SCREEN_WIDTH - 150, 650, 130, 45).collidepoint(mouse_pos):
                        self.show_menu()
                    # 下一关
                    if self.show_success and self.message_timer > 60:
                        if pygame.Rect(SCREEN_WIDTH//2 - 80, 680, 160, 45).collidepoint(mouse_pos):
                            self.next_level()

                    # 输入框
                    if self.input_box:
                        input_rect = pygame.Rect(50, 410, SCREEN_WIDTH - 300, 50)
                        self.input_box.active = input_rect.collidepoint(mouse_pos)

                elif self.mode == "learn":
                    # 密码类型选择
                    for i in range(len(CIPHER_INFO)):
                        btn_rect = pygame.Rect(50, 110 + i * 70, 200, 60)
                        if btn_rect.collidepoint(mouse_pos):
                            self.learn_selection = i

                    # 返回按钮
                    if pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50, 130, 45).collidepoint(mouse_pos):
                        self.show_menu()

            elif event.type == pygame.KEYDOWN and self.mode == "playing":
                if self.input_box:
                    if event.key == pygame.K_BACKSPACE:
                        self.input_box.text = self.input_box.text[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.submit_answer()
                    elif event.unicode and len(self.input_box.text) < 30:
                        self.input_box.text += event.unicode

    def submit_answer(self):
        """提交答案"""
        if self.input_box:
            user_answer = self.input_box.text.strip()
            if user_answer:
                correct = self.check_answer(user_answer)
                if correct:
                    self.input_box.text = ""

    def use_hint(self):
        """使用提示"""
        if self.hint_level < self.max_hints:
            self.current_hint = self.get_hint()

    def show_cipher_info(self):
        """显示密码信息"""
        if self.current_cipher in CIPHER_INFO:
            self.info_text = CIPHER_INFO[self.current_cipher]
            self.show_info = True

    def show_menu(self):
        """显示菜单"""
        self.mode = "menu"
        self.input_box = None
        self.current_hint = ""

    def start_game(self):
        """开始游戏"""
        self.mode = "playing"
        self.load_level()
        self.input_box = InputBox(50, 410, SCREEN_WIDTH - 300, 50, "输入你的答案...")
        self.current_hint = ""

    def show_learn(self):
        """显示学习模式"""
        self.mode = "learn"
        self.learn_selection = 0
        self.hover_cipher = -1

    def next_level(self):
        """下一关"""
        if self.current_level < self.max_level:
            self.current_level += 1
            # 重新生成数据
            self.cipher_data = self.generate_cipher_data()
            self.load_level()
            self.input_box.text = ""
            self.current_hint = ""

    def reset_progress(self):
        """重置进度"""
        self.current_level = 1
        self.score = 0
        self.streak = 0
        self.cipher_data = self.generate_cipher_data()

    def draw_result(self):
        """绘制结果界面"""
        self.screen.fill(BG_COLOR)

        title = TITLE_FONT.render("恭喜通关！", True, SUCCESS_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title, title_rect)

        score_text = LARGE_FONT.render(f"最终得分: {self.score}", True, HIGHLIGHT_COLOR)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 250))
        self.screen.blit(score_text, score_rect)

        message = FONT.render("你已经掌握了8种经典密码的破译方法！", True, TEXT_COLOR)
        msg_rect = message.get_rect(center=(SCREEN_WIDTH//2, 320))
        self.screen.blit(message, msg_rect)

        self.draw_button("返回菜单", SCREEN_WIDTH//2 - 65, 450, self.show_menu, HIGHLIGHT_COLOR)

    def run(self):
        """游戏主循环"""
        self.learn_selection = 0
        self.hover_cipher = -1
        self.current_hint = ""

        running = True
        while running:
            self.clock.tick(FPS)

            self.handle_events()

            # 更新
            if self.message_timer > 0:
                self.message_timer -= 1
            if self.success_timer > 0:
                self.success_timer -= 1

            # 绘制
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = CodeBreakerGame()
    game.run()
