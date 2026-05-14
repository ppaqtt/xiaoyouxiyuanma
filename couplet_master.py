# -*- coding: utf-8 -*-
"""
对联大师游戏 - Couplet Master Game
一款弘扬中华对联文化的文字游戏，玩家需要掌握对联的对仗、平仄和意境
"""

import pygame
import sys
import random

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# 颜色定义
BG_COLOR = (40, 30, 50)
TEXT_COLOR = (255, 255, 255)
RED_COLOR = (220, 50, 50)
GOLD_COLOR = (255, 215, 0)
GREEN_COLOR = (50, 200, 100)
BLUE_COLOR = (100, 150, 255)
PURPLE_COLOR = (180, 100, 200)
BUTTON_COLOR = (80, 60, 100)
BUTTON_HOVER_COLOR = (110, 80, 140)
INPUT_COLOR = (60, 50, 80)

# 设置字体
pygame.font.init()
try:
    FONT = pygame.font.Font("simsun.ttc", 26)
    TITLE_FONT = pygame.font.Font("simsun.ttc", 52)
    COUPLET_FONT = pygame.font.Font("simsun.ttc", 48)
    SMALL_FONT = pygame.font.Font("simsun.ttc", 20)
    LARGE_FONT = pygame.font.Font("simsun.ttc", 36)
except:
    FONT = pygame.font.SysFont("simhei", 26)
    TITLE_FONT = pygame.font.SysFont("simhei", 52)
    COUPLET_FONT = pygame.font.SysFont("simhei", 48)
    SMALL_FONT = pygame.font.SysFont("simhei", 20)
    LARGE_FONT = pygame.font.SysFont("simhei", 36)

# 对联数据库
COUPLET_DATABASE = {
    "春联": {
        "easy": [
            ("新年纳余庆", "嘉节号长春"),
            ("春风得意马蹄疾", "春日寻芳泗水滨"),
            ("春回大地千山秀", "日照神州百业兴"),
            ("春满人间欢歌阵阵", "福临门第喜气洋洋"),
            ("又是一年芳草绿", "依然十里桃花红"),
            ("春到江南塞北", "福临天地之间"),
            ("春风绿遍千山草", "旭日红映万里天"),
            ("春光明媚百花艳", "人寿年丰百业兴"),
        ],
        "medium": [
            ("天增岁月人增寿", "春满乾坤福满门"),
            ("爆竹声中一岁除", "春风送暖入屠苏"),
            ("春到堂前增瑞气", "日临庭中起祥光"),
            ("红梅傲雪花千树", "紫燕衔泥春一家"),
            ("春色满园关不住", "红杏出墙报春来"),
            ("冬去山明水秀", "春来鸟语花香"),
        ],
        "hard": [
            ("春风化雨润桃李", "丹心育苗培栋梁"),
            ("绿柳舒眉辞旧岁", "红桃开口笑新年"),
            ("春到人间气象新", "福临大地阳光暖"),
            ("万紫千红总是春", "五湖四海皆为家"),
            ("春回大地千山秀", "日照神州万象新"),
        ]
    },
    "春联横批": [
        "春回大地", "万象更新", "辞旧迎新", "春满人间",
        "福满人间", "欣欣向荣", "国泰民安", "春和景明"
    ],
    "格言联": {
        "easy": [
            ("书山有路勤为径", "学海无涯苦作舟"),
            ("欲穷千里目", "更上一层楼"),
            ("山重水复疑无路", "柳暗花明又一村"),
            ("世上无难事", "只要肯登攀"),
            ("千里之行始于足下", "万丈高楼平地起"),
        ],
        "medium": [
            ("宝剑锋从磨砺出", "梅花香自苦寒来"),
            ("业精于勤荒于嬉", "行成于思毁于随"),
            ("书到用时方恨少", "事非经过不知难"),
            ("海纳百川有容乃大", "壁立千仞无欲则刚"),
            ("删繁就简三秋树", "领异标新二月花"),
        ],
        "hard": [
            ("风声雨声读书声 声声入耳", "家事国事天下事 事事关心"),
            ("有志者事竟成 破釜沉舟 百二秦关终属楚", "苦心人天不负 卧薪尝胆 三千越甲可吞吴"),
            ("海阔凭鱼跃", "天高任鸟飞"),
            ("宠辱不惊 看庭前花开花落", "去留无意 望天上云卷云舒"),
            ("与有肝胆人共事", "从无字句处读书"),
        ]
    },
    "风景联": {
        "easy": [
            ("青山绿水", "碧海蓝天"),
            ("日出江花红胜火", "春来江水绿如蓝"),
            ("两个黄鹂鸣翠柳", "一行白鹭上青天"),
            ("明月松间照", "清泉石上流"),
            ("山重水复疑无路", "柳暗花明又一村"),
        ],
        "medium": [
            ("山寺月中寻桂子", "郡亭枕上看潮头"),
            ("窗含西岭千秋雪", "门泊东吴万里船"),
            ("水光潋滟晴方好", "山色空蒙雨亦奇"),
            ("大江东去浪淘尽", "千古风流人物"),
        ],
        "hard": [
            ("四面荷花三面柳", "一城山色半城湖"),
            ("桃花流水窅然去", "别有天地非人间"),
            ("山高月小", "水落石出"),
            ("清风明月本无价", "近水远山皆有情"),
            ("峰回路转不见君", "雪上空留马行处"),
        ]
    },
    "人物联": {
        "easy": [
            ("李白斗酒诗百篇", "张旭三杯草圣传"),
            ("武松打虎景阳冈", "林冲雪夜上梁山"),
        ],
        "medium": [
            ("三顾频烦天下计", "两朝开济老臣心"),
            ("出师未捷身先死", "长使英雄泪满襟"),
            ("犹留正气参天地", "永剩丹心照古今"),
        ],
        "hard": [
            ("铜板铁琶继东坡高唱大江东去", "美芹悲黍冀南宋莫随鸿雁南飞"),
            ("物外乾坤谁梦见", "壶中日月我淹留"),
        ]
    },
    "商业联": [
        ("生意兴隆通四海", "财源茂盛达三江"),
        ("货真价实公平交易", "童叟无欺诚信经营"),
        ("开门迎客笑脸相迎", "笑脸送宾满意而归"),
        ("薄利多销利虽小", "货真价实客常来"),
        ("诚信经营通万贾", "公平交易达千商"),
    ],
    "寿联": [
        ("福如东海长流水", "寿比南山不老松"),
        ("柏翠松苍歌五福", "椿荣萱茂祝千秋"),
        ("人近百年犹赤子", "天留二老看玄孙"),
        ("花甲重开外加三七岁月", "古稀双庆内多一个春秋"),
    ],
    "婚联": [
        ("百年好合永结同心", "佳偶天成喜结良缘"),
        ("金风玉露一相逢", "便胜却人间无数"),
        ("在天愿作比翼鸟", "在地愿为连理枝"),
        ("两情若是久长时", "又岂在朝朝暮暮"),
        ("琴瑟友之宜室家", "钟鼓乐之宜子孙"),
    ],
    "挽联": [
        ("音容宛在", "德泽永存"),
        ("名留千古", "光耀千秋"),
        ("浩气长存", "英灵永昭"),
        ("音容已杳", "德泽犹存"),
    ]
}

# 对联知识介绍
COUPLET_KNOWLEDGE = {
    "对仗": """
【对仗的基本规则】

对仗是对联最核心的规则，要求上下联对应的词
在词性、结构、字数等方面相互对应。

一、词性对应：
  名词对名词 动词对动词
  形容词对形容词 数词对数词
  量词对量词 代词对代词

二、结构对应：
  主谓结构对主谓结构
  偏正结构对偏正结构
  动宾结构对动宾结构

三、例子：
  天对地，雨对风，大陆对长空。
  山花对海树，赤日对苍穹。

平仄口诀：
  平对仄，仄对平，平仄要分明。
  一三五不论，二四六分明。
    """,
    "平仄": """
【平仄的学问】

平仄是汉语的声调分类：
- 平声：阴平（一声）、阳平（二声）
- 仄声：上声（三声）、去声（四声）

基本规则：
1. 上联末字仄，下联末字平
2. 上下联对应位置的字平仄相反
3. 关键位置（第二、四、六字）必须严格

五言律诗平仄格式：
  仄仄平平仄
  平平仄仄平
  平平平仄仄
  仄仄仄平平

七言律诗平仄格式：
  平平仄仄平平仄
  仄仄平平仄仄平
  仄仄平平平仄仄
  平平仄仄仄平平

练习平仄有助于写好对联！
    """,
    "意境": """
【对联的意境】

意境是对联的灵魂，好的对联不仅对仗工整，
更要营造出优美的意境。

一、意境的类型：
  1. 写景意境：如"明月松间照，清泉石上流"
  2. 抒情意境：如"但愿人长久，千里共婵娟"
  3. 哲理意境：如"山重水复疑无路，柳暗花明又一村"
  4. 豪放意境：如"大江东去浪淘尽，千古风流人物"

二、意境的营造：
  1. 借景抒情：借助景物表达情感
  2. 动静结合：动中有静，静中有动
  3. 虚实相生：实的景象与虚的想象结合
  4. 情景交融：情与景融为一体

三、名句赏析：
  "春风得意马蹄疾，一日看尽长安花"
  ——孟郊《登科后》

  "海内存知己，天涯若比邻"
  ——王勃《送杜少府之任蜀州》
    """,
    "种类": """
【对联的种类】

一、按用途分类：
  1. 春联：春节贴在门上的对联
  2. 寿联：祝贺寿辰的对联
  3. 婚联：祝贺新婚的对联
  4. 挽联：哀悼逝者的对联
  5. 行业联：各行业的专用对联
  6. 风景名胜联：题刻在风景区的对联
  7. 格言联：富有哲理的对联

二、按字数分类：
  1. 短联：十字以内
  2. 中联：十一字到二十字
  3. 长联：二十一字以上

三、按形式分类：
  1. 拆字联：将汉字拆开或合并
  2. 回文联：正读反读都成文
  3. 谐音联：利用谐音双关
  4. 叠字联：使用重叠字
    """,
    "典故": """
【对联中的典故】

典故是对联文化的重要组成部分，
运用典故可以增加对联的深度和趣味。

常用典故：
1. 姜太公钓鱼 —— 愿者上钩
2. 刘玄德三顾茅庐 —— 礼贤下士
3. 诸葛亮草船借箭 —— 智谋过人
4. 关云长千里走单骑 —— 忠义无双
5. 陶渊明采菊东篱 —— 隐逸高洁
6. 李太白醉酒捞月 —— 浪漫不羁
7. 杜子美忧国忧民 —— 爱国情怀
8. 苏东坡大江东去 —— 豪放旷达

名联举例：
"三顾频烦天下计，两朝开济老臣心"
—— 杜甫《蜀相》，写诸葛亮

"出师未捷身先死，长使英雄泪满襟"
—— 杜甫《蜀相》，写诸葛亮壮志未酬
    """,
    "技巧": """
【对联创作技巧】

一、选材立意：
  选择有意义的题材，明确创作目的

二、对仗工整：
  词性、词义、结构都要对应

三、平仄协调：
  注意声调搭配，读来朗朗上口

四、意境深远：
  情景交融，引人入胜

五、炼字精准：
  一个好字可以使整联生辉

六、避免合掌：
  上下联意思不能完全相同

七、注意禁忌：
  避免重字（叠字联除外）
  避免孤平（单仄或单平）

创作练习：
  以"读书"为题，试写一副对联
  参考：风声雨声读书声 声声入耳
        家事国事天下事 事事关心
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
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, GOLD_COLOR, self.rect, 2, border_radius=10)

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
        self.max_chars = 20

    def draw(self, surface):
        color = GOLD_COLOR if self.active else TEXT_COLOR
        pygame.draw.rect(surface, INPUT_COLOR, self.rect, border_radius=8)
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=8)

        # 显示字数限制
        limit_text = SMALL_FONT.render(f"{len(self.text)}/{self.max_chars}", True, (150, 150, 150))
        surface.blit(limit_text, (self.rect.right - 45, self.rect.y + self.rect.height - 22))

        if self.text:
            text_surface = COUPLET_FONT.render(self.text, True, TEXT_COLOR)
            # 居中显示
            text_x = self.rect.centerx - text_surface.get_width() // 2
            surface.blit(text_surface, (text_x, self.rect.y + 5))
        elif not self.active:
            placeholder_surface = SMALL_FONT.render(self.placeholder, True, (120, 120, 120))
            text_rect = placeholder_surface.get_rect(center=self.rect.center)
            surface.blit(placeholder_surface, text_rect)

        # 光标
        if self.active and self.cursor_visible and self.text:
            text_surface = COUPLET_FONT.render(self.text, True, TEXT_COLOR)
            cursor_x = self.rect.centerx + text_surface.get_width() // 2 + 5
            pygame.draw.line(surface, TEXT_COLOR, (cursor_x, self.rect.y + 10),
                          (cursor_x, self.rect.y + self.rect.height - 10), 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            elif event.unicode and len(self.text) < self.max_chars:
                # 只接受汉字
                if '\u4e00' <= event.unicode <= '\u9fff':
                    self.text += event.unicode
        return False

    def update(self):
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0


class CoupletMasterGame:
    """对联大师游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("对联大师 - Couplet Master")
        self.clock = pygame.time.Clock()

        # 游戏状态
        self.mode = "menu"  # menu, game, learn, practice, about
        self.current_category = "春联"
        self.current_difficulty = "easy"
        self.current_level = 1
        self.score = 0
        self.streak = 0
        self.round = 0
        self.max_rounds = 10

        # 当前题目
        self.upper_couplet = ""
        self.answer = ""
        self.category = ""
        self.hint_used = False
        self.round_result = None  # None, True, False
        self.feedback_text = ""

        # UI元素
        self.input_box = None
        self.buttons = []
        self.current_hint = ""

        # 统计
        self.correct_count = 0
        self.total_attempts = 0

    def generate_question(self):
        """生成题目"""
        categories = ["春联", "格言联", "风景联", "人物联"]
        self.category = random.choice(categories)

        difficulty_map = {
            "easy": "easy",
            "medium": "medium",
            "hard": "hard"
        }

        diff = difficulty_map.get(self.current_difficulty, "easy")

        if self.category in COUPLET_DATABASE:
            if self.category in ["春联", "格言联", "风景联", "人物联"]:
                if diff in COUPLET_DATABASE[self.category]:
                    pairs = COUPLET_DATABASE[self.category][diff]
                else:
                    pairs = COUPLET_DATABASE[self.category]["easy"]
            else:
                pairs = COUPLET_DATABASE[self.category]
        else:
            pairs = COUPLET_DATABASE["春联"]["easy"]

        pair = random.choice(pairs)
        self.upper_couplet = pair[0]
        self.answer = pair[1]
        self.hint_used = False
        self.round_result = None
        self.feedback_text = ""

    def check_couplet(self, user_input):
        """检查对联"""
        self.total_attempts += 1

        # 精确匹配
        if user_input == self.answer:
            return "perfect"

        # 检查字数
        if len(user_input) != len(self.answer):
            return "length_error"

        # 检查每个字的匹配
        match_count = 0
        errors = []
        for i, (user_char, correct_char) in enumerate(zip(user_input, self.answer)):
            if user_char == correct_char:
                match_count += 1
            else:
                errors.append(i)

        # 计算匹配率
        match_rate = match_count / len(self.answer)

        if match_rate >= 0.8:
            return "good"
        elif match_rate >= 0.5:
            return "fair"
        else:
            return "poor"

    def get_hint(self):
        """获取提示"""
        if not self.hint_used:
            self.hint_used = True
            hint_len = len(self.answer)
            if hint_len <= 5:
                self.current_hint = f"提示：下联共有{hint_len}个字，首字是'{self.answer[0]}'"
            elif hint_len <= 10:
                first_two = self.answer[:2]
                last_one = self.answer[-1]
                self.current_hint = f"提示：下联共有{hint_len}个字，前两字是'{first_two}'，末字是'{last_one}'"
            else:
                first_two = self.answer[:2]
                last_two = self.answer[-2:]
                self.current_hint = f"提示：下联共有{hint_len}个字，前两字是'{first_two}'，末两字是'{last_two}'"
        else:
            # 第二个提示，给出部分
            half = len(self.answer) // 2
            self.current_hint = f"提示：下联中'{self.answer[:half]}{'□' * half}'..."
        return self.current_hint

    def draw_menu(self):
        """绘制主菜单"""
        self.screen.fill(BG_COLOR)

        # 装饰边框
        pygame.draw.rect(self.screen, (60, 40, 80), (20, 20, SCREEN_WIDTH-40, SCREEN_HEIGHT-40), 3)
        pygame.draw.rect(self.screen, (80, 60, 100), (30, 30, SCREEN_WIDTH-60, SCREEN_HEIGHT-60), 1)

        # 标题
        title = TITLE_FONT.render("对 联 大 师", True, RED_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
        self.screen.blit(title, title_rect)

        # 副标题
        subtitle = SMALL_FONT.render("—— 传承千年的文字艺术 ——", True, GOLD_COLOR)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 130))
        self.screen.blit(subtitle, subtitle_rect)

        # 对联装饰
        left_couplet = LARGE_FONT.render("诗", True, RED_COLOR)
        right_couplet = LARGE_FONT.render("词", True, RED_COLOR)
        self.screen.blit(left_couplet, (200, 180))
        self.screen.blit(right_couplet, (SCREEN_WIDTH - 250, 180))

        # 装饰线
        pygame.draw.line(self.screen, GOLD_COLOR, (250, 200), (SCREEN_WIDTH - 250, 200), 1)

        # 分数显示
        score_text = FONT.render(f"累计得分: {self.score}", True, GOLD_COLOR)
        self.screen.blit(score_text, (50, 50))

        if self.total_attempts > 0:
            accuracy = int(self.correct_count / self.total_attempts * 100)
            acc_text = FONT.render(f"正确率: {accuracy}%", True, GREEN_COLOR)
            self.screen.blit(acc_text, (50, 85))

        # 菜单选项
        menu_items = [
            ("挑战模式", "game", BLUE_COLOR),
            ("学习园地", "learn", GREEN_COLOR),
            ("自由练习", "practice", PURPLE_COLOR),
            ("游戏说明", "about", (150, 150, 150)),
        ]

        y_start = 260
        for i, (text, mode, color) in enumerate(menu_items):
            btn = Button(SCREEN_WIDTH//2 - 120, y_start + i * 80, 240, 60, text,
                        lambda m=mode: self.change_mode(m), color)
            btn.draw(self.screen)

        # 每日名联
        daily_y = y_start + 340
        daily_title = SMALL_FONT.render("【每日名联】", True, GOLD_COLOR)
        self.screen.blit(daily_title, (SCREEN_WIDTH//2 - daily_title.get_width()//2, daily_y))

        daily_couplet = random.choice([
            "春风得意马蹄疾，一日看尽长安花",
            "海纳百川有容乃大，壁立千仞无欲则刚",
            "山重水复疑无路，柳暗花明又一村"
        ])
        daily_text = SMALL_FONT.render(daily_couplet, True, TEXT_COLOR)
        self.screen.blit(daily_text, (SCREEN_WIDTH//2 - daily_text.get_width()//2, daily_y + 30))

        # 底部信息
        footer = SMALL_FONT.render("传承中华文化，品味对联之美", True, (120, 120, 120))
        self.screen.blit(footer, (SCREEN_WIDTH//2 - footer.get_width()//2, SCREEN_HEIGHT - 40))

    def draw_game(self):
        """绘制游戏界面"""
        self.screen.fill(BG_COLOR)

        # 顶部信息栏
        pygame.draw.rect(self.screen, (50, 40, 70), (20, 20, SCREEN_WIDTH-40, 80), border_radius=10)

        round_text = FONT.render(f"第 {self.round}/{self.max_rounds} 题", True, TEXT_COLOR)
        self.screen.blit(round_text, (50, 45))

        score_text = FONT.render(f"得分: {self.score}", True, GOLD_COLOR)
        self.screen.blit(score_text, (200, 45))

        streak_text = FONT.render(f"连击: {self.streak}", True, GREEN_COLOR)
        self.screen.blit(streak_text, (350, 45))

        # 类别和难度
        cat_text = SMALL_FONT.render(f"类别: {self.category}", True, PURPLE_COLOR)
        self.screen.blit(cat_text, (500, 45))

        diff_text = SMALL_FONT.render(f"难度: {self.get_difficulty_name()}", True, BLUE_COLOR)
        self.screen.blit(diff_text, (700, 45))

        # 返回按钮
        back_btn = Button(SCREEN_WIDTH - 120, 35, 90, 40, "返回", self.show_menu, (80, 60, 100))
        back_btn.draw(self.screen)

        # 上联显示
        upper_label = SMALL_FONT.render("【上联】", True, RED_COLOR)
        self.screen.blit(upper_label, (50, 130))

        pygame.draw.rect(self.screen, (50, 40, 70), (50, 155, SCREEN_WIDTH - 100, 100), border_radius=10)
        pygame.draw.rect(self.screen, RED_COLOR, (50, 155, SCREEN_WIDTH - 100, 100), 2, border_radius=10)

        upper_text = COUPLET_FONT.render(self.upper_couplet, True, GOLD_COLOR)
        upper_rect = upper_text.get_rect(center=(SCREEN_WIDTH//2, 205))
        self.screen.blit(upper_text, upper_rect)

        # 下联输入
        lower_label = SMALL_FONT.render("【下联】", True, GREEN_COLOR)
        self.screen.blit(lower_label, (50, 280))

        pygame.draw.rect(self.screen, INPUT_COLOR, (50, 305, SCREEN_WIDTH - 100, 100), border_radius=10)
        pygame.draw.rect(self.screen, GOLD_COLOR if self.input_box and self.input_box.active else TEXT_COLOR,
                        (50, 305, SCREEN_WIDTH - 100, 100), 2, border_radius=10)

        if self.input_box:
            self.input_box.rect = pygame.Rect(50, 305, SCREEN_WIDTH - 100, 100)
            self.input_box.draw(self.screen)

        # 提示
        if self.current_hint:
            hint_surface = SMALL_FONT.render(self.current_hint, True, (200, 200, 100))
            hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH//2, 430))
            self.screen.blit(hint_surface, hint_rect)

        # 按钮区
        button_y = 480

        # 提交按钮
        submit_btn = Button(50, button_y, 180, 50, "提交答案",
                           self.submit_answer, GREEN_COLOR)
        submit_btn.draw(self.screen)

        # 提示按钮
        hint_btn = Button(250, button_y, 150, 50,
                          "获取提示" if not self.hint_used else "更多提示",
                          self.show_hint, (180, 180, 50))
        if self.hint_used and self.current_hint:
            hint_btn.text = "再给提示"
        hint_btn.draw(self.screen)

        # 跳过按钮
        skip_btn = Button(420, button_y, 120, 50, "跳过此题",
                         self.skip_question, (150, 100, 150))
        skip_btn.draw(self.screen)

        # 下一题按钮
        if self.round_result:
            next_btn = Button(SCREEN_WIDTH//2 - 60, button_y + 70, 120, 45, "下一题 ➜",
                             self.next_question, BLUE_COLOR)
            next_btn.draw(self.screen)

        # 结果反馈
        if self.round_result is not None:
            if self.round_result == True:
                result_text = FONT.render("恭喜答对！", True, GREEN_COLOR)
            else:
                result_text = FONT.render(f"正确答案是：{self.answer}", True, RED_COLOR)
            result_rect = result_text.get_rect(center=(SCREEN_WIDTH//2, 620))
            self.screen.blit(result_text, result_rect)

        # 难度选择
        diff_y = 580
        diff_label = SMALL_FONT.render("选择难度:", True, TEXT_COLOR)
        self.screen.blit(diff_label, (SCREEN_WIDTH - 300, diff_y))

        difficulties = [("简单", "easy", GREEN_COLOR), ("中等", "medium", BLUE_COLOR), ("困难", "hard", RED_COLOR)]
        for i, (name, key, color) in enumerate(difficulties):
            diff_btn = Button(SCREEN_WIDTH - 300 + i * 100, diff_y + 30, 90, 35, name,
                            lambda d=key: self.change_difficulty(d), color)
            if self.current_difficulty == key:
                diff_btn.color = color
            diff_btn.draw(self.screen)

    def draw_learn(self):
        """绘制学习界面"""
        self.screen.fill(BG_COLOR)

        # 标题
        title = TITLE_FONT.render("对联学习园地", True, GOLD_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title, title_rect)

        # 左侧目录
        topics = list(COUPLET_KNOWLEDGE.keys())
        y_start = 110

        for i, topic in enumerate(topics):
            btn = Button(50, y_start + i * 70, 180, 55, topic,
                        lambda t=topic: self.select_topic(t), PURPLE_COLOR)
            if self.selected_topic == topic:
                btn.color = GREEN_COLOR
            btn.draw(self.screen)

        # 右侧内容
        if self.selected_topic in COUPLET_KNOWLEDGE:
            content_rect = pygame.Rect(260, 100, SCREEN_WIDTH - 320, SCREEN_HEIGHT - 150)
            pygame.draw.rect(self.screen, (50, 40, 70), content_rect, border_radius=15)

            lines = COUPLET_KNOWLEDGE[self.selected_topic].strip().split('\n')
            y = content_rect.y + 20

            for line in lines:
                if line.strip():
                    # 标题样式
                    if line.startswith('【') and line.endswith('】'):
                        color = GOLD_COLOR
                        size = LARGE_FONT
                    elif line.startswith('一、') or line.startswith('二、') or line.startswith('三、'):
                        color = GREEN_COLOR
                        size = FONT
                    else:
                        color = TEXT_COLOR
                        size = SMALL_FONT

                    surface = size.render(line, True, color)
                    self.screen.blit(surface, (content_rect.x + 20, y))
                y += 32
                if y > content_rect.bottom - 50:
                    break

        # 名联赏析
        self.draw_famous_couplets()

        # 返回按钮
        back_btn = Button(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 60, 100, 45, "返回", self.show_menu)
        back_btn.draw(self.screen)

    def draw_famous_couplets(self):
        """绘制名联赏析"""
        famous_couplets = [
            "风声雨声读书声 声声入耳\n家事国事天下事 事事关心",
            "海纳百川 有容乃大\n壁立千仞 无欲则刚",
            "山重水复疑无路\n柳暗花明又一村",
            "宝剑锋从磨砺出\n梅花香自苦寒来",
            "有志者 事竟成 破釜沉舟 百二秦关终属楚\n苦心人 天不负 卧薪尝胆 三千越甲可吞吴"
        ]

        y_start = 110
        section_title = SMALL_FONT.render("【经典名联】", True, RED_COLOR)
        self.screen.blit(section_title, (50, y_start))

        for i, couplet in enumerate(famous_couplets[:3]):
            lines = couplet.split('\n')
            for j, line in enumerate(lines):
                text = SMALL_FONT.render(line, True, TEXT_COLOR)
                self.screen.blit(text, (50, y_start + 30 + i * 60 + j * 28))

    def draw_practice(self):
        """绘制练习界面"""
        self.screen.fill(BG_COLOR)

        # 标题
        title = TITLE_FONT.render("自由练习", True, PURPLE_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title, title_rect)

        # 类别选择
        categories = list(COUPLET_DATABASE.keys())
        y_start = 110

        cat_label = SMALL_FONT.render("选择类别:", True, TEXT_COLOR)
        self.screen.blit(cat_label, (50, y_start))

        for i, cat in enumerate(categories[:6]):
            color = PURPLE_COLOR if self.practice_category != cat else GREEN_COLOR
            btn = Button(200 + (i % 3) * 150, y_start + (i // 3) * 60, 140, 50, cat,
                        lambda c=cat: self.set_practice_category(c), color)
            btn.draw(self.screen)

        # 显示选中的对联
        if self.practice_category in COUPLET_DATABASE:
            all_couplets = []
            if self.practice_category in ["春联", "格言联", "风景联", "人物联"]:
                for diff in ["easy", "medium", "hard"]:
                    if diff in COUPLET_DATABASE[self.practice_category]:
                        all_couplets.extend(COUPLET_DATABASE[self.practice_category][diff])
            else:
                all_couplets = COUPLET_DATABASE[self.practice_category]

            if all_couplets:
                selected = random.choice(all_couplets)
                upper, lower = selected[0], selected[1]

                # 上联
                upper_label = SMALL_FONT.render("【上联】", True, RED_COLOR)
                self.screen.blit(upper_label, (100, 280))

                pygame.draw.rect(self.screen, (50, 40, 70), (100, 310, SCREEN_WIDTH - 200, 80), border_radius=10)
                upper_text = COUPLET_FONT.render(upper, True, GOLD_COLOR)
                upper_rect = upper_text.get_rect(center=(SCREEN_WIDTH//2, 350))
                self.screen.blit(upper_text, upper_rect)

                # 下联
                lower_label = SMALL_FONT.render("【下联】", True, GREEN_COLOR)
                self.screen.blit(lower_label, (100, 420))

                pygame.draw.rect(self.screen, (50, 40, 70), (100, 450, SCREEN_WIDTH - 200, 80), border_radius=10)
                lower_text = COUPLET_FONT.render(lower, True, GOLD_COLOR)
                lower_rect = lower_text.get_rect(center=(SCREEN_WIDTH//2, 490))
                self.screen.blit(lower_text, lower_rect)

        # 按钮
        new_btn = Button(SCREEN_WIDTH//2 - 100, 570, 200, 50, "换一副", self.refresh_practice, BLUE_COLOR)
        new_btn.draw(self.screen)

        # 返回
        back_btn = Button(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 60, 100, 45, "返回", self.show_menu)
        back_btn.draw(self.screen)

    def draw_about(self):
        """绘制关于界面"""
        self.screen.fill(BG_COLOR)

        # 标题
        title = TITLE_FONT.render("对联文化简介", True, GOLD_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(title, title_rect)

        # 内容
        about_text = """
【什么是对联】

对联，又称楹联、对子，是中华文化独特的文学形式。
它起源于桃符，历经千年发展，成为华人文化的重要组成。

【基本特征】

1. 对仗工整：词性、结构相互对应
2. 平仄协调：声调有规律地交替
3. 意境深远：情景交融，意味深长
4. 字数相等：上下联字数必须相同

【对联的分类】

按用途分：春联、寿联、婚联、挽联、行业联等
按字数分：短联、中联、长联
按形式分：正联、叠字联、回文联、拆字联等

【著名对联故事】

1. 王羲之书春联：
   "春风春雨春色，新年新岁新景"
   因太受欢迎，写一幅偷一幅，最后写了"福无双至今朝至，
   祸不单行昨夜行"，终于保住了春联。

2. 苏东坡与佛印对联：
   苏轼：投石击破水中天
   佛印：乘舟而来的是东坡

【学习对联的意义】

1. 传承中华优秀传统文化
2. 提高文学素养和审美能力
3. 锻炼思维和语言表达能力
4. 丰富精神文化生活
        """

        lines = about_text.strip().split('\n')
        y = 110
        for line in lines:
            if line.strip():
                if line.startswith('【') and line.endswith('】'):
                    color = GOLD_COLOR
                    size = LARGE_FONT
                elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.'):
                    color = GREEN_COLOR
                    size = SMALL_FONT
                else:
                    color = TEXT_COLOR
                    size = SMALL_FONT
                surface = size.render(line, True, color)
                self.screen.blit(surface, (50, y))
            y += 30
            if y > SCREEN_HEIGHT - 50:
                break

        # 返回
        back_btn = Button(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 60, 100, 45, "返回", self.show_menu)
        back_btn.draw(self.screen)

    def draw(self):
        """主绘制方法"""
        if self.mode == "menu":
            self.draw_menu()
        elif self.mode == "game":
            self.draw_game()
        elif self.mode == "learn":
            self.draw_learn()
        elif self.mode == "practice":
            self.draw_practice()
        elif self.mode == "about":
            self.draw_about()

        pygame.display.flip()

    def handle_events(self):
        """处理事件"""
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # 按钮点击检测
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_button_clicks(event.pos)

            # 输入处理
            if self.input_box:
                self.input_box.handle_event(event)

    def handle_button_clicks(self, pos):
        """处理按钮点击"""
        if self.mode == "menu":
            # 菜单按钮
            if pygame.Rect(SCREEN_WIDTH//2 - 120, 260, 240, 60).collidepoint(pos):
                self.change_mode("game")
            elif pygame.Rect(SCREEN_WIDTH//2 - 120, 340, 240, 60).collidepoint(pos):
                self.change_mode("learn")
            elif pygame.Rect(SCREEN_WIDTH//2 - 120, 420, 240, 60).collidepoint(pos):
                self.change_mode("practice")
            elif pygame.Rect(SCREEN_WIDTH//2 - 120, 500, 240, 60).collidepoint(pos):
                self.change_mode("about")

        elif self.mode == "game":
            # 游戏按钮
            if pygame.Rect(50, 480, 180, 50).collidepoint(pos):
                self.submit_answer()
            elif pygame.Rect(250, 480, 150, 50).collidepoint(pos):
                self.show_hint()
            elif pygame.Rect(420, 480, 120, 50).collidepoint(pos):
                self.skip_question()
            elif pygame.Rect(SCREEN_WIDTH//2 - 80, 550, 120, 45).collidepoint(pos) and self.round_result:
                self.next_question()
            elif pygame.Rect(SCREEN_WIDTH - 120, 35, 90, 40).collidepoint(pos):
                self.show_menu()

            # 难度选择
            for i, key in enumerate(["easy", "medium", "hard"]):
                if pygame.Rect(SCREEN_WIDTH - 300 + i * 100, 610, 90, 35).collidepoint(pos):
                    self.change_difficulty(key)

            # 输入框
            if self.input_box:
                input_rect = pygame.Rect(50, 305, SCREEN_WIDTH - 100, 100)
                self.input_box.active = input_rect.collidepoint(pos)

        elif self.mode == "learn":
            # 学习目录
            topics = list(COUPLET_KNOWLEDGE.keys())
            for i, topic in enumerate(topics):
                if pygame.Rect(50, 110 + i * 70, 180, 55).collidepoint(pos):
                    self.selected_topic = topic

            if pygame.Rect(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 60, 100, 45).collidepoint(pos):
                self.show_menu()

        elif self.mode == "practice":
            categories = list(COUPLET_DATABASE.keys())
            for i, cat in enumerate(categories[:6]):
                col, row = i % 3, i // 3
                if pygame.Rect(200 + col * 150, 170 + row * 60, 140, 50).collidepoint(pos):
                    self.practice_category = cat
                    self.refresh_practice()

            if pygame.Rect(SCREEN_WIDTH//2 - 100, 570, 200, 50).collidepoint(pos):
                self.refresh_practice()
            elif pygame.Rect(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 60, 100, 45).collidepoint(pos):
                self.show_menu()

        elif self.mode == "about":
            if pygame.Rect(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 60, 100, 45).collidepoint(pos):
                self.show_menu()

    def change_mode(self, mode):
        """切换模式"""
        self.mode = mode

        if mode == "game":
            self.round = 0
            self.score = 0
            self.streak = 0
            self.correct_count = 0
            self.total_attempts = 0
            self.input_box = InputBox(50, 305, SCREEN_WIDTH - 100, 100, "请输入下联...")
            self.next_question()

        elif mode == "learn":
            self.selected_topic = list(COUPLET_KNOWLEDGE.keys())[0]

        elif mode == "practice":
            self.practice_category = "春联"
            self.refresh_practice()

    def show_menu(self):
        """显示菜单"""
        self.mode = "menu"

    def next_question(self):
        """下一题"""
        self.round += 1
        if self.round > self.max_rounds:
            self.show_result()
        else:
            self.generate_question()
            self.input_box.text = ""
            self.current_hint = ""

    def submit_answer(self):
        """提交答案"""
        if not self.input_box or self.round_result:
            return

        user_answer = self.input_box.text.strip()
        if not user_answer:
            return

        result = self.check_couplet(user_answer)

        if result == "perfect":
            self.score += 100 + self.streak * 20
            self.streak += 1
            self.correct_count += 1
            self.round_result = True
            self.feedback_text = "完美！太厉害了！"
        elif result == "good":
            self.score += 60 + self.streak * 10
            self.streak += 1
            self.correct_count += 1
            self.round_result = True
            self.feedback_text = "很好！基本正确！"
        elif result == "fair":
            self.streak = 0
            self.round_result = False
            self.feedback_text = "差一点，继续加油！"
        else:
            self.streak = 0
            self.round_result = False
            self.feedback_text = "答案错误，请学习后再试！"

    def show_hint(self):
        """显示提示"""
        self.get_hint()

    def skip_question(self):
        """跳过题目"""
        self.round_result = False
        self.feedback_text = f"正确答案是：{self.answer}"
        self.streak = 0

    def change_difficulty(self, difficulty):
        """更改难度"""
        self.current_difficulty = difficulty
        self.generate_question()
        if self.input_box:
            self.input_box.text = ""
        self.current_hint = ""

    def get_difficulty_name(self):
        """获取难度名称"""
        names = {"easy": "简单", "medium": "中等", "hard": "困难"}
        return names.get(self.current_difficulty, "简单")

    def set_practice_category(self, category):
        """设置练习类别"""
        self.practice_category = category
        self.refresh_practice()

    def refresh_practice(self):
        """刷新练习内容"""
        if self.practice_category in COUPLET_DATABASE:
            all_couplets = []
            if self.practice_category in ["春联", "格言联", "风景联", "人物联"]:
                for diff in ["easy", "medium", "hard"]:
                    if diff in COUPLET_DATABASE[self.practice_category]:
                        all_couplets.extend(COUPLET_DATABASE[self.practice_category][diff])
            else:
                all_couplets = COUPLET_DATABASE[self.practice_category]

            if all_couplets:
                selected = random.choice(all_couplets)
                self.practice_upper = selected[0]
                self.practice_lower = selected[1]

    def select_topic(self, topic):
        """选择学习主题"""
        self.selected_topic = topic

    def show_result(self):
        """显示结果"""
        self.mode = "result"
        accuracy = int(self.correct_count / self.total_attempts * 100) if self.total_attempts > 0 else 0

        # 创建结果画面
        self.screen.fill(BG_COLOR)

        title = TITLE_FONT.render("挑战完成！", True, GOLD_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)

        score_text = LARGE_FONT.render(f"最终得分: {self.score}", True, GREEN_COLOR)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(score_text, score_rect)

        acc_text = FONT.render(f"正确率: {accuracy}%", True, BLUE_COLOR)
        acc_rect = acc_text.get_rect(center=(SCREEN_WIDTH//2, 260))
        self.screen.blit(acc_text, acc_rect)

        correct_text = FONT.render(f"答对: {self.correct_count}/{self.max_rounds} 题", True, TEXT_COLOR)
        correct_rect = correct_text.get_rect(center=(SCREEN_WIDTH//2, 310))
        self.screen.blit(correct_text, correct_rect)

        # 评价
        if accuracy >= 90:
            comment = "太厉害了！你是对联大师！"
            color = GOLD_COLOR
        elif accuracy >= 70:
            comment = "很棒！继续加油！"
            color = GREEN_COLOR
        elif accuracy >= 50:
            comment = "还不错，多学习一下！"
            color = BLUE_COLOR
        else:
            comment = "建议先去学习园地看看哦！"
            color = PURPLE_COLOR

        comment_text = LARGE_FONT.render(comment, True, color)
        comment_rect = comment_text.get_rect(center=(SCREEN_WIDTH//2, 380))
        self.screen.blit(comment_text, comment_rect)

        # 按钮
        retry_btn = Button(SCREEN_WIDTH//2 - 220, 450, 180, 50, "再来一局", lambda: self.change_mode("game"), GREEN_COLOR)
        retry_btn.draw(self.screen)

        menu_btn = Button(SCREEN_WIDTH//2 + 40, 450, 180, 50, "返回菜单", self.show_menu, BLUE_COLOR)
        menu_btn.draw(self.screen)

        pygame.display.flip()

    def run(self):
        """游戏主循环"""
        self.selected_topic = "对仗"
        self.practice_category = "春联"
        self.refresh_practice()

        running = True
        while running:
            self.clock.tick(FPS)

            self.handle_events()

            if self.input_box:
                self.input_box.update()

            if self.mode != "result":
                self.draw()

            # 处理鼠标悬停
            mouse_pos = pygame.mouse.get_pos()
            for btn in self.buttons:
                btn.update(mouse_pos)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = CoupletMasterGame()
    game.run()
