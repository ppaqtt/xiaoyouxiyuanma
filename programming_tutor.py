#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编程入门学习游戏
使用pygame实现的编程基础教学游戏
"""

import pygame
import os
import sys

class Lesson:
    def __init__(self, title, description, code, expected, hint):
        self.title = title
        self.description = description
        self.code = code
        self.expected = expected
        self.hint = hint

class ProgrammingTutor:
    def __init__(self):
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

self.width = 950
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('编程入门学习')
        self.clock = pygame.time.Clock()
        self.font = get_chinese_font(28)
        self.large_font = get_chinese_font(40)
        self.small_font = get_chinese_font(24)
        self.code_font = get_chinese_font(26)
        
        self.lessons = [
            Lesson(
                '第一课: 打印Hello',
                '使用 print() 函数打印 "Hello!"',
                'print("Hello!")',
                'Hello!',
                '提示: 使用 print("Hello!") 来输出'
            ),
            Lesson(
                '第二课: 变量赋值',
                '创建一个变量 x 并赋值为 10',
                'x = 10',
                '10',
                '提示: 直接赋值 x = 10'
            ),
            Lesson(
                '第三课: 加法运算',
                '计算 5 + 3 的结果',
                '5 + 3',
                '8',
                '提示: 直接写出数学表达式'
            ),
            Lesson(
                '第四课: 变量运算',
                '先赋值 a = 5, b = 3, 然后计算 a + b',
                'a = 5\nb = 3\na + b',
                '8',
                '提示: 分三行写代码'
            ),
            Lesson(
                '第五课: 字符串连接',
                '连接 "Hello" 和 "World"，用空格分开',
                '"Hello" + " " + "World"',
                'Hello World',
                '提示: 用 + 连接字符串'
            ),
            Lesson(
                '第六课: 条件判断',
                '判断 10 > 5 的结果（True或False）',
                '10 > 5',
                'True',
                '提示: 直接写比较表达式'
            ),
            Lesson(
                '第七课: 列表创建',
                '创建一个包含 1, 2, 3 的列表',
                '[1, 2, 3]',
                '[1, 2, 3]',
                '提示: 用方括号创建列表'
            ),
            Lesson(
                '第八课: 列表索引',
                '获取列表 [10, 20, 30] 的第一个元素',
                '[10, 20, 30][0]',
                '10',
                '提示: 使用 [0] 获取第一个元素'
            ),
        ]
        
        self.current_lesson = 0
        self.user_code = ''
        self.output = ''
        self.show_hint = False
        self.completed = [False] * len(self.lessons)
        self.success_timer = 0
        
        self.colors = {
            'bg': (245, 245, 250),
            'panel': (255, 255, 255),
            'text': (30, 30, 30),
            'code_bg': (40, 42, 54),
            'code_text': (248, 248, 242),
            'output_bg': (30, 30, 30),
            'output_text': (0, 255, 0),
            'button': (100, 150, 255),
            'button_hover': (130, 180, 255),
            'success': (100, 200, 100),
            'error': (255, 100, 100),
        }
        
        self.buttons = [
            {'text': '运行', 'x': 650, 'y': 620, 'w': 100, 'h': 50, 'action': 'run'},
            {'text': '提示', 'x': 760, 'y': 620, 'w': 100, 'h': 50, 'action': 'hint'},
            {'text': '上一课', 'x': 540, 'y': 620, 'w': 100, 'h': 50, 'action': 'prev'},
            {'text': '下一课', 'x': 870, 'y': 620, 'w': 70, 'h': 50, 'action': 'next'},
        ]
        
        self.hovered_button = None
        self.cursor_pos = 0
        self.code_lines = ['']
    
    def run_code(self):
        try:
            code = '\n'.join(self.code_lines)
            lesson = self.lessons[self.current_lesson]
            
            local_vars = {}
            exec(code, globals(), local_vars)
            
            result = None
            if 'x' in local_vars:
                result = local_vars['x']
            elif 'a' in local_vars and 'b' in local_vars:
                result = local_vars['a'] + local_vars['b']
            
            if result is None:
                try:
                    result = eval(code)
                except:
                    pass
            
            if result is not None:
                output = str(result)
            else:
                output = '代码运行成功!'
            
            expected = str(lesson.expected)
            if str(result) == expected or output == expected:
                self.output = f'✓ 正确！输出: {output}'
                self.success_timer = 180
                self.completed[self.current_lesson] = True
            else:
                self.output = f'输出: {output}\n期望: {expected}\n再试试！'
        
        except Exception as e:
            self.output = f'错误: {str(e)}'
    
    def draw_lesson_panel(self):
        pygame.draw.rect(self.screen, self.colors['panel'], (20, 20, 420, 180), border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 200), (20, 20, 420, 180), 2, border_radius=10)
        
        lesson = self.lessons[self.current_lesson]
        title = self.large_font.render(lesson.title, True, self.colors['text'])
        self.screen.blit(title, (35, 35))
        
        desc = self.wrap_text(lesson.description, 400)
        y = 80
        for line in desc:
            text = self.font.render(line, True, self.colors['text'])
            self.screen.blit(text, (35, y))
            y += 30
        
        progress = f'进度: {self.current_lesson + 1}/{len(self.lessons)}'
        progress_text = self.small_font.render(progress, True, (100, 100, 100))
        self.screen.blit(progress_text, (35, 170))
        
        completed_count = sum(self.completed)
        completed_text = self.small_font.render(f'已完成: {completed_count}', True, self.colors['success'])
        self.screen.blit(completed_text, (300, 170))
    
    def draw_code_editor(self):
        pygame.draw.rect(self.screen, self.colors['code_bg'], (20, 220, 420, 380), border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 100), (20, 220, 420, 380), 2, border_radius=10)
        
        title = self.font.render('代码编辑器', True, (200, 200, 200))
        self.screen.blit(title, (30, 230))
        
        line_y = 270
        for i, line in enumerate(self.code_lines):
            line_num = self.small_font.render(f'{i + 1:2d}', True, (120, 120, 120))
            self.screen.blit(line_num, (25, line_y))
            
            code_text = self.code_font.render(line, True, self.colors['code_text'])
            self.screen.blit(code_text, (60, line_y))
            
            if i == len(self.code_lines) - 1 and pygame.time.get_ticks() % 1000 < 500:
                cursor_x = 60 + self.code_font.size(line[:self.cursor_pos])[0]
                pygame.draw.rect(self.screen, (255, 255, 255), (cursor_x, line_y, 2, 28))
            
            line_y += 35
    
    def draw_output_panel(self):
        pygame.draw.rect(self.screen, self.colors['output_bg'], (460, 20, 470, 580), border_radius=10)
        pygame.draw.rect(self.screen, (100, 100, 100), (460, 20, 470, 580), 2, border_radius=10)
        
        title = self.font.render('输出结果', True, (200, 200, 200))
        self.screen.blit(title, (470, 30))
        
        if self.success_timer > 0:
            color = self.colors['success']
        else:
            color = self.colors['output_text']
        
        if self.output:
            lines = self.output.split('\n')
            y = 70
            for line in lines:
                text = self.font.render(line, True, color)
                self.screen.blit(text, (475, y))
                y += 35
        
        if self.show_hint:
            hint = self.lessons[self.current_lesson].hint
            hint_lines = self.wrap_text(hint, 450)
            pygame.draw.rect(self.screen, (60, 60, 80), (470, 400, 450, 180), border_radius=5)
            y = 410
            for line in hint_lines:
                text = self.small_font.render(line, True, (255, 220, 100))
                self.screen.blit(text, (480, y))
                y += 28
    
    def draw_buttons(self):
        for btn in self.buttons:
            color = self.colors['button_hover'] if btn == self.hovered_button else self.colors['button']
            pygame.draw.rect(self.screen, color, (btn['x'], btn['y'], btn['w'], btn['h']), border_radius=8)
            
            text = self.font.render(btn['text'], True, (255, 255, 255))
            text_rect = text.get_rect(center=(btn['x'] + btn['w'] // 2, btn['y'] + btn['h'] // 2))
            self.screen.blit(text, text_rect)
    
    def wrap_text(self, text, max_width):
        words = text.split(' ')
        lines = []
        current_line = ''
        
        for word in words:
            test_line = current_line + ' ' + word if current_line else word
            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def handle_click(self, pos):
        for btn in self.buttons:
            if btn['x'] <= pos[0] <= btn['x'] + btn['w'] and btn['y'] <= pos[1] <= btn['y'] + btn['h']:
                self.handle_button(btn['action'])
                return
        
        if 20 <= pos[0] <= 440 and 220 <= pos[1] <= 600:
            pass
    
    def handle_button(self, action):
        if action == 'run':
            self.run_code()
        elif action == 'hint':
            self.show_hint = not self.show_hint
        elif action == 'prev':
            if self.current_lesson > 0:
                self.current_lesson -= 1
                self.code_lines = ['']
                self.cursor_pos = 0
                self.output = ''
                self.show_hint = False
        elif action == 'next':
            if self.current_lesson < len(self.lessons) - 1:
                self.current_lesson += 1
                self.code_lines = ['']
                self.cursor_pos = 0
                self.output = ''
                self.show_hint = False
    
    def handle_mouse_move(self, pos):
        self.hovered_button = None
        for btn in self.buttons:
            if btn['x'] <= pos[0] <= btn['x'] + btn['w'] and btn['y'] <= pos[1] <= btn['y'] + btn['h']:
                self.hovered_button = btn
                break
    
    def handle_key_press(self, event):
        if event.key == pygame.K_BACKSPACE:
            if self.cursor_pos > 0:
                self.code_lines[-1] = self.code_lines[-1][:self.cursor_pos - 1] + self.code_lines[-1][self.cursor_pos:]
                self.cursor_pos -= 1
        elif event.key == pygame.K_RETURN:
            self.code_lines.append('')
            self.cursor_pos = 0
        elif event.key == pygame.K_LEFT:
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
        elif event.key == pygame.K_RIGHT:
            if self.cursor_pos < len(self.code_lines[-1]):
                self.cursor_pos += 1
        elif event.key == pygame.K_TAB:
            self.code_lines[-1] = self.code_lines[-1][:self.cursor_pos] + '    ' + self.code_lines[-1][self.cursor_pos:]
            self.cursor_pos += 4
        elif event.unicode:
            self.code_lines[-1] = self.code_lines[-1][:self.cursor_pos] + event.unicode + self.code_lines[-1][self.cursor_pos:]
            self.cursor_pos += 1
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_move(event.pos)
                elif event.type == pygame.KEYDOWN:
                    self.handle_key_press(event)
            
            if self.success_timer > 0:
                self.success_timer -= 1
            
            self.screen.fill(self.colors['bg'])
            
            title = self.large_font.render('📚 Python 编程入门', True, self.colors['text'])
            title_rect = title.get_rect(center=(self.width // 2, 650))
            self.screen.blit(title, title_rect)
            
            self.draw_lesson_panel()
            self.draw_code_editor()
            self.draw_output_panel()
            self.draw_buttons()
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == '__main__':
    game = ProgrammingTutor()
    game.run()
