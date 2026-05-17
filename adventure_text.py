# -*- coding: utf-8 -*-
"""
文字冒险游戏 - Adventure Text Game
一款充满中国古典风格的文字冒险游戏，玩家通过选择推动故事发展
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

# 游戏常量
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# 颜色定义
BG_COLOR = (30, 30, 50)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 215, 0)
BUTTON_COLOR = (70, 70, 120)
BUTTON_HOVER_COLOR = (100, 100, 160)
TITLE_COLOR = (255, 200, 100)

# 设置中文字体
pygame.font.init()
try:
    FONT = pygame.font.Font("simsun.ttc", 24)
    TITLE_FONT = pygame.font.Font("simsun.ttc", 48)
    SMALL_FONT = pygame.font.Font("simsun.ttc", 20)
except:
    FONT = pygame.font.SysFont("simhei", 24)
    TITLE_FONT = pygame.font.SysFont("simhei", 48)
    SMALL_FONT = pygame.font.SysFont("simhei", 20)

# 游戏场景数据
SCENES = {
    "start": {
        "title": "桃花源记",
        "description": """
在大唐盛世年间，你是一位年轻的书生，名叫柳清风。

你正在赶考途中，忽然天降大雨，你匆忙躲进了一座古庙。

古庙中有一面古老的铜镜，镜面泛着奇异的光芒...

据说这面铜镜可以通向一个神秘的世界——桃花源。

你的选择将决定你的命运...
        """,
        "choices": [
            {"text": "触碰铜镜", "next": "mirror_touch"},
            {"text": "在庙中休息，等待雨停", "next": "rest_temple"},
            {"text": "仔细研究铜镜上的铭文", "next": "study_mirror"}
        ]
    },
    "mirror_touch": {
        "title": "穿越之门",
        "description": """
你轻轻触碰铜镜，指尖传来一阵温热。

刹那间，光芒大盛，你感到天旋地转。

当你再次睁开眼睛时，发现自己置身于一片桃林之中。

漫天的桃花如雪般飘落，空气中弥漫着芬芳。

远处隐约可见炊烟袅袅的村庄。

你遇到了一个正在采花的少女。
        """,
        "choices": [
            {"text": "上前询问这是什么地方", "next": "ask_girl"},
            {"text": "独自探索这片桃林", "next": "explore_forest"},
            {"text": "跟随少女前往村庄", "next": "follow_girl"}
        ]
    },
    "rest_temple": {
        "title": "古庙奇遇",
        "description": """
你在古庙中找了一个干燥的角落休息。

迷迷糊糊中，你听到了一个苍老的声音在耳边响起：

"年轻人，你可愿听一个故事？"

"从前有一个书生，他找到了一条通往仙境的道路..."

你猛然惊醒，发现铜镜中似乎有一扇门在召唤你。
        """,
        "choices": [
            {"text": "鼓起勇气进入铜镜", "next": "mirror_touch"},
            {"text": "装作没看见，继续睡觉", "next": "sleep_more"},
            {"text": "仔细研究那扇门", "next": "study_mirror"}
        ]
    },
    "study_mirror": {
        "title": "铭文之谜",
        "description": """
你仔细研究铜镜上的铭文，发现上面刻着：

"桃花源记，晋太元中，武陵人捕鱼为业。
缘溪行，忘路之远近。忽逢桃花林，夹岸数百步，
中无杂树，芳草鲜美，落英缤纷..."

铭文的最后还有一行小字：
"心诚则灵，有缘者得入。"

你感到一股神秘的力量在召唤你。
        """,
        "choices": [
            {"text": "虔诚地叩拜后触碰铜镜", "next": "blessing_mirror"},
            {"text": "先离开古庙去赶路", "next": "leave_temple"}
        ]
    },
    "ask_girl": {
        "title": "桃花少女",
        "description": """
少女转过身来，她的面容如桃花般娇艳。

"公子从何而来？这里是桃花源，外人不得入内。"

"不过既然你能来到这里，说明你我有缘。"

"我叫桃夭，是这里的村长的女儿。"

"父亲常说，能找到这里的人，都是心善之人。"

她递给你一颗晶莹的桃子作为见面礼。
        """,
        "choices": [
            {"text": "接受桃子，感谢她的好意", "next": "accept_peach"},
            {"text": "询问她能否带你参观村庄", "next": "visit_village"},
            {"text": "询问离开这里的方法", "next": "ask_way_out"}
        ]
    },
    "explore_forest": {
        "title": "桃林迷踪",
        "description": """
你独自走进桃林深处，桃花越开越盛。

走着走着，你发现自己迷路了。

四周都是一模一样的桃树，让你分不清方向。

忽然，你听到远处传来悠扬的笛声。

笛声似乎在指引你前进的方向。
        """,
        "choices": [
            {"text": "跟随笛声前行", "next": "follow_flute"},
            {"text": "大声呼救", "next": "shout_help"},
            {"text": "爬上桃树观察地形", "next": "climb_tree"}
        ]
    },
    "follow_girl": {
        "title": "村口欢迎",
        "description": """
你悄悄跟在少女身后，穿过一片又一片桃林。

终于，一座美丽的村庄出现在眼前。

村口站着一位白发苍苍的老者，正是村长。

"远方来的客人，欢迎来到桃花源！"

"我们这里已经几百年没有来过外人了。"

"你一定是特别的缘分才能找到这里。"

村长热情地邀请你参加今晚的篝火晚会。
        """,
        "choices": [
            {"text": "欣然接受邀请", "next": "campfire"},
            {"text": "询问这里的历史", "next": "ask_history"},
            {"text": "感谢款待，但想尽快回家", "next": "want_go_home"}
        ]
    },
    "sleep_more": {
        "title": "梦中惊醒",
        "description": """
你决定继续睡觉，但那个声音越来越清晰。

"年轻人，机遇稍纵即逝..."

忽然，你感到一阵剧痛，从梦中惊醒。

原来有一条蛇从柱子后面爬过，差点咬到你。

铜镜依然泛着光芒，似乎在等待你。
        """,
        "choices": [
            {"text": "立刻触碰铜镜", "next": "mirror_touch"},
            {"text": "先观察周围环境", "next": "study_mirror"}
        ]
    },
    "blessing_mirror": {
        "title": "神镜祝福",
        "description": """
你虔诚地叩拜，心中默念心愿。

铜镜忽然发出耀眼的金光，光芒中走出一个仙人。

"年轻人，你的诚心感动了我。"

"我是这里的守护者——镜仙。"

"我将赐予你进入桃花源的能力。"

"但记住，在那里的所见所闻，不可对外人言说。"

说完，仙人化作一道金光，融入了铜镜之中。
        """,
        "choices": [
            {"text": "带着仙人的祝福触碰铜镜", "next": "mirror_touch"},
            {"text": "感谢仙人后离开", "next": "leave_temple"}
        ]
    },
    "leave_temple": {
        "title": "错过机缘",
        "description": """
你决定不去冒险，继续赶路。

雨渐渐小了，你离开了古庙。

后来你听说，那年赶考，有人高中状元，

有人名落孙山，而那个古庙所在的地方，

后来变成了一片桃林，再也找不到古庙的痕迹。

但每逢春天，那里的桃花开得格外灿烂。

也许，那真的是通往桃花源的路呢？
        """,
        "choices": [
            {"text": "重新开始旅程", "next": "start"},
            {"text": "结束游戏", "next": "end"}
        ]
    },
    "accept_peach": {
        "title": "仙桃之缘",
        "description": """
你接过桃子，轻轻咬了一口。

一股清凉甘甜的汁水流入喉中。

忽然，你感到神清气爽，仿佛获得了某种力量。

"这颗桃子是我们桃花源的特产。"

"吃了它，你会对我们的文化有更深的理解。"

"而且你将永远记住这里的一切。"

桃夭笑着说，眼中闪烁着温暖的光芒。
        """,
        "choices": [
            {"text": "跟随桃夭参观村庄", "next": "visit_village"},
            {"text": "与桃夭分享你的故事", "next": "share_story"}
        ]
    },
    "visit_village": {
        "title": "桃花源记",
        "description": """
在桃夭的带领下，你参观了整个村庄。

这里的人们安居乐业，鸡犬相闻，怡然自乐。

你看到：
- 老人在树下下棋
- 孩童在溪边嬉戏
- 农夫在田间劳作
- 妇女在河边洗衣

一切都那么和谐美好，仿佛世外桃源。

村长设宴款待你，你在这里住了七天。

第七天，你决定回家。
        """,
        "choices": [
            {"text": "带着美好的回忆回家", "next": "good_ending"},
            {"text": "请求留在桃花源", "next": "stay_ending"}
        ]
    },
    "ask_way_out": {
        "title": "离别时刻",
        "description": """
桃夭的表情有些黯然。

"公子真的要离开吗？"

"不过我可以告诉你回去的路。"

"沿着溪水一直走，穿过桃林，你就能找到出口。"

"但我希望你记住这里。"

"也许有一天，你会再回来的。"

她的眼中似乎有不舍之情。
        """,
        "choices": [
            {"text": "感谢她，依依不舍地离开", "next": "bittersweet_ending"},
            {"text": "邀请她一起离开", "next": "invite_leave"}
        ]
    },
    "follow_flute": {
        "title": "笛声指引",
        "description": """
你跟随笛声，穿过一片又一片桃林。

笛声越来越近，最终你来到了一处山洞前。

一位白发老者坐在洞口，吹奏着玉笛。

"年轻人，你终于来了。"

"我在这里等你很久了。"

"我是这里的隐士，人称桃花仙人。"

"我有一些人生的智慧想要传授给你。"
        """,
        "choices": [
            {"text": "恭敬地向仙人学习", "next": "learn_wisdom"},
            {"text": "询问仙人的来历", "next": "ask_immortal"}
        ]
    },
    "shout_help": {
        "title": "虚惊一场",
        "description": """
你大声呼救，声音在桃林中回荡。

不一会儿，桃夭循声赶来。

"公子，你怎么一个人在这里？"

"这里的桃林很容易迷路，我带你出去吧。"

她拉着你的手，带你走出了桃林。

她的手温暖而柔软，让你的心跳加速。
        """,
        "choices": [
            {"text": "感谢她的帮助", "next": "accept_peach"},
            {"text": "请她带你参观村庄", "next": "visit_village"}
        ]
    },
    "climb_tree": {
        "title": "登高望远",
        "description": """
你爬上一棵最高的桃树，极目远眺。

原来你已经离村庄不远了。

从高处看去，整个桃花源尽收眼底：

四面环山，中间是一片开阔的谷地
桃林环绕村庄，溪水潺潺
炊烟袅袅，鸡犬相闻

你心中豁然开朗，这真是人间仙境！
        """,
        "choices": [
            {"text": "下树前往村庄", "next": "visit_village"},
            {"text": "在树上静心欣赏风景", "next": "meditate_tree"}
        ]
    },
    "campfire": {
        "title": "篝火晚会",
        "description": """
篝火晚会上，全村人都来欢迎你。

村民们载歌载舞，热情款待。

你品尝了桃花源的美食：
- 桃花酿（香甜的美酒）
- 仙桃宴（各种桃子做的菜肴）
- 桃花糕（香甜软糯的点心）

村长把一本古籍送给你：

《桃花源记》——记载着这个神奇地方的秘密。
        """,
        "choices": [
            {"text": "接受礼物，研读古籍", "next": "learn_culture"},
            {"text": "与村民们一起歌舞", "next": "dance_night"}
        ]
    },
    "ask_history": {
        "title": "源远流长",
        "description": """
村长带你来到村中的祠堂，开始讲述桃花源的历史：

"很久很久以前，秦朝末年天下大乱。"

"一群百姓为了躲避战乱，逃入了这片山谷。"

"他们在这里建立家园，世代繁衍。"

"我们已经在这里生活了几百年。"

"外面的朝代更迭，对我们来说仿佛过眼云烟。"

"我们只想守护这份宁静与美好。"
        """,
        "choices": [
            {"text": "感叹这里的历史", "next": "good_ending"},
            {"text": "询问能否留下", "next": "stay_ending"}
        ]
    },
    "want_go_home": {
        "title": "归心似箭",
        "description": """
村长理解你的思乡之情。

"人之常情，我理解。"

"但在我们这里住几日再走吧。"

"我们虽然没有外面的繁华，但也有独特的美好。"

"让我带你领略一下我们的风土人情。"

村长带你参观了村庄的各个角落。
        """,
        "choices": [
            {"text": "接受安排，留下几日", "next": "visit_village"},
            {"text": "坚持马上回家", "next": "hasty_ending"}
        ]
    },
    "good_ending": {
        "title": "美好结局",
        "description": """
你在桃花源住了七七四十九天。

临别时，村民们都来送行。

桃夭送给你一颗桃核：

"把它种在你家门前。"

"当它开花的那一天，也许就是我们再见的时候。"

你带着美好的回忆回到了家。

那颗桃核很快发芽、开花、结果。

每年春天，你都会想起那段奇妙的经历。

你把这个故事写成了文章，传给了后人。

这就是《桃花源记》的由来。
        """,
        "choices": [
            {"text": "重新开始旅程", "next": "start"},
            {"text": "结束游戏", "next": "end"}
        ]
    },
    "stay_ending": {
        "title": "留下为仙",
        "description": """
你决定留在桃花源，不再回去。

村长欣然接受，让你成为村里的一员。

你在这里学习耕种、酿酒、作画...

渐渐地，你成为了村里有名的才子。

多年后，你娶了桃夭为妻，过上了幸福的生活。

你们的孩子也在这里健康成长。

你终于明白，真正的幸福，就在这桃花源中。
        """,
        "choices": [
            {"text": "重新开始旅程", "next": "start"},
            {"text": "结束游戏", "next": "end"}
        ]
    },
    "bittersweet_ending": {
        "title": "依依惜别",
        "description": """
你沿着溪水走去，穿过桃林，回到了古庙。

铜镜依然在那里，光芒已经消散。

你回头望去，只见桃花漫天，却再也找不到来时的路。

你知道，桃花源将永远留在你的心中。

后来你高中状元，为官一方。

但每到春天，你都会去那片桃林走走，

希望能再见到那个如桃花般的少女。

虽然再也没能相见，但那份美好的回忆，将伴随你一生。
        """,
        "choices": [
            {"text": "重新开始旅程", "next": "start"},
            {"text": "结束游戏", "next": "end"}
        ]
    },
    "invite_leave": {
        "title": "共同离开",
        "description": """
桃夭犹豫了很久，最终摇了摇头。

"公子，这是我们的约定。"

"桃花源的人不能离开这里。"

"如果我离开，我将失去这里的一切。"

"而且，外面的世界不适合我。"

她轻轻拥抱了你，然后转身离去。

你独自踏上了归途。

虽然遗憾，但你知道，这就是缘分。
        """,
        "choices": [
            {"text": "重新开始旅程", "next": "start"},
            {"text": "结束游戏", "next": "end"}
        ]
    },
    "learn_wisdom": {
        "title": "仙人传授",
        "description": """
仙人将毕生所学传授给你：

"道法自然，无为而治。"

"人生如梦，珍惜当下。"

"祸兮福所倚，福兮祸所伏。"

"上善若水，水善利万物而不争。"

你将这些道理铭记于心。

仙人还传授你一套养生功法。

学成之后，你顺利找到了回家的路。
        """,
        "choices": [
            {"text": "带着智慧回家", "next": "good_ending"},
            {"text": "重新开始旅程", "next": "start"}
        ]
    },
    "ask_immortal": {
        "title": "仙人自述",
        "description": """
仙人微笑着说：

"我本是秦朝的一位术士，喜好炼丹修仙。"

"后来发现了这片世外桃源，便隐居于此。"

"经过几百年的修炼，终于得道成仙。"

"但我并不想离开，这里就是我的仙境。"

"年轻人，你的资质不错，若努力修炼，将来也能得道。"

"不过，还是先回去好好生活吧。"
        """,
        "choices": [
            {"text": "感谢仙人指教", "next": "good_ending"},
            {"text": "请求留下修炼", "next": "stay_ending"}
        ]
    },
    "meditate_tree": {
        "title": "桃林悟道",
        "description": """
你静静地坐在树上，看着满天飞舞的桃花。

忽然，你的心境变得无比宁静。

你想起了一首诗：

"去年今日此门中，人面桃花相映红。
人面不知何处去，桃花依旧笑春风。"

你感悟到，人生就像这桃花一样，美丽而短暂。

我们应该珍惜每一个当下，珍惜每一个人。

带着这份领悟，你下树前往村庄。
        """,
        "choices": [
            {"text": "带着感悟继续旅程", "next": "visit_village"}
        ]
    },
    "learn_culture": {
        "title": "文化传承",
        "description": """
你仔细研读《桃花源记》古籍。

书中记载了这个神奇地方的点点滴滴：

- 桃花源的由来
- 村民们的生活习俗
- 独特的农耕文化
- 精美的桃花艺术品
- 古老的养生之道

你将这些文化精华铭记于心。

后来你将这些文化传播到外面的世界，

让更多人了解了桃花源的美好。
        """,
        "choices": [
            {"text": "带着文化回家", "next": "good_ending"}
        ]
    },
    "dance_night": {
        "title": "欢乐之夜",
        "description": """
你和村民们一起围着篝火载歌载舞。

桃花酿让你微醺，但心情无比畅快。

这一刻，你忘记了一切烦恼。

你学到了桃花源的舞蹈和歌曲。

村民们都很喜欢你，把你当作好朋友。

这一夜的欢乐，将永远留在你的记忆中。
        """,
        "choices": [
            {"text": "带着欢乐回家", "next": "good_ending"}
        ]
    },
    "hasty_ending": {
        "title": "匆忙离开",
        "description": """
你坚持要马上离开。

村长给了你一些干粮，依依不舍地送你离去。

你穿过桃林，沿着来时的路返回。

当你醒来时，发现自己还在古庙中。

雨已经停了，阳光明媚。

也许，这只是一场梦？

但你的口袋中，确实放着一颗晶莹的桃子...

也许，桃花源是真实存在的吧。
        """,
        "choices": [
            {"text": "重新开始旅程", "next": "start"},
            {"text": "结束游戏", "next": "end"}
        ]
    },
    "end": {
        "title": "感谢游玩",
        "description": """
感谢你体验了《桃花源记》文字冒险游戏！

通过这个游戏，你了解了：

- 中国古典文学《桃花源记》的故事背景
- 陶渊明笔下的世外桃源
- 中国传统文化中的隐士思想
- 珍惜当下、热爱生活的道理

"采菊东篱下，悠然见南山"
这是多少人心中的梦想啊！

希望这个游戏给你带来了快乐和启发！
        """,
        "choices": [
            {"text": "重新开始旅程", "next": "start"}
        ]
    }
}


class Button:
    """按钮类"""
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.is_hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, self.rect, 2, border_radius=10)

        text_surface = FONT.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered:
            self.callback()


class TextAdventureGame:
    """文字冒险游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("桃花源记 - 文字冒险游戏")
        self.clock = pygame.time.Clock()

        self.current_scene = "start"
        self.buttons = []
        self.scroll_offset = 0
        self.max_scroll = 0

        # 背景装饰
        self.particles = []
        self.init_particles()

    def init_particles(self):
        """初始化桃花粒子"""
        for _ in range(30):
            self.particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.randint(2, 6),
                'speed': random.uniform(0.3, 1.0),
                'wobble': random.uniform(0, 2 * 3.14159)
            })

    def update_particles(self):
        """更新桃花粒子"""
        for p in self.particles:
            p['y'] += p['speed']
            p['x'] += math.sin(p['wobble']) * 0.5
            p['wobble'] += 0.02
            if p['y'] > SCREEN_HEIGHT:
                p['y'] = -10
                p['x'] = random.randint(0, SCREEN_WIDTH)

    def draw_particles(self, surface):
        """绘制桃花粒子"""
        for p in self.particles:
            color = (255, 182, 193)  # 粉色
            pygame.draw.circle(surface, color, (int(p['x']), int(p['y'])), p['size'])

    def load_scene(self, scene_id):
        """加载场景"""
        self.current_scene = scene_id
        self.create_buttons()
        self.scroll_offset = 0

    def create_buttons(self):
        """创建选择按钮"""
        self.buttons = []
        scene = SCENES[self.current_scene]

        # 文字区域高度估算
        text_height = len(scene['description'].split('\n')) * 30
        button_start_y = min(350 + text_height // 2, SCREEN_HEIGHT - 150)

        for i, choice in enumerate(scene['choices']):
            btn = Button(
                250, button_start_y + i * 55,
                500, 45,
                choice['text'],
                lambda c=choice: self.load_scene(c['next'])
            )
            self.buttons.append(btn)

    def draw_text_box(self, surface, text, pos, max_width, color=TEXT_COLOR):
        """绘制自动换行的文本框"""
        words = text.split('\n')
        y = pos[1]
        line_height = 32

        for line in words:
            if line.strip():
                # 处理每行文字
                chars = []
                width = 0
                for char in line:
                    char_surface = FONT.render(char, True, color)
                    char_width = char_surface.get_width()
                    if width + char_width > max_width:
                        surface.blit(FONT.render(''.join(chars), True, color), (pos[0], y))
                        y += line_height
                        chars = [char]
                        width = char_width
                    else:
                        chars.append(char)
                        width += char_width
                if chars:
                    surface.blit(FONT.render(''.join(chars), True, color), (pos[0], y))
            y += line_height

    def draw(self):
        """绘制游戏画面"""
        self.screen.fill(BG_COLOR)

        # 绘制桃花装饰
        self.draw_particles(self.screen)

        # 绘制边框装饰
        pygame.draw.rect(self.screen, (50, 50, 80), (20, 20, SCREEN_WIDTH-40, SCREEN_HEIGHT-40), 2)

        # 绘制标题
        scene = SCENES[self.current_scene]
        title = scene['title']
        title_surface = TITLE_FONT.render(title, True, TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 60))
        self.screen.blit(title_surface, title_rect)

        # 绘制装饰线
        pygame.draw.line(self.screen, HIGHLIGHT_COLOR, (200, 95), (SCREEN_WIDTH-200, 95), 2)

        # 绘制场景描述
        desc_y = 120
        self.draw_text_box(self.screen, scene['description'].strip(), (80, desc_y), SCREEN_WIDTH - 160)

        # 绘制按钮
        for btn in self.buttons:
            btn.draw(self.screen)

        # 底部提示
        hint = SMALL_FONT.render("使用鼠标点击选择，游戏内容改编自陶渊明《桃花源记》", True, (150, 150, 150))
        self.screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT - 40))

        pygame.display.flip()

    def handle_events(self):
        """处理事件"""
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            for btn in self.buttons:
                btn.handle_event(event)

        for btn in self.buttons:
            btn.update(mouse_pos)

        return True

    def run(self):
        """游戏主循环"""
        import math
        self.create_buttons()

        running = True
        while running:
            self.clock.tick(FPS)

            # 事件处理
            running = self.handle_events()

            # 更新粒子
            self.update_particles()

            # 绘制
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = TextAdventureGame()
    game.run()
