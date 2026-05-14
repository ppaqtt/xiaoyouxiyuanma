#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学校模拟器 - 模拟经营游戏
管理学校,培养学生
"""

import pygame
import random

pygame.init()

WIDTH, HEIGHT = 1000, 700

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 100)
RED = (255, 50, 50)
BLUE = (0, 100, 200)
YELLOW = (255, 200, 0)
PURPLE = (150, 50, 200)
ORANGE = (255, 150, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("学校模拟器 - 模拟经营")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 50)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

class Student:
    def __init__(self, grade_level):
        self.name = random.choice(["小明", "小红", "小华", "小丽", "小刚", "小雨", "小强", "小芳"])
        self.grade = grade_level
        self.math = random.randint(50, 80)
        self.english = random.randint(50, 80)
        self.science = random.randint(50, 80)
        self.happiness = random.randint(60, 90)
        self.x = WIDTH + random.randint(50, 200)
        self.y = 200 + random.randint(0, 300)
        self.target_x = 700 + random.randint(0, 100)
        self.target_y = 200 + random.randint(0, 300)
        self.learning = False
        self.finished = False
        self.color = random.choice([BLUE, GREEN, PURPLE, ORANGE])

class SchoolGame:
    def __init__(self):
        self.money = 10000
        self.day = 1
        self.reputation = 50
        self.students = []
        self.teachers = [
            {"name": "数学老师", "subject": "math", "busy": False, "x": 600, "y": 380},
            {"name": "英语老师", "subject": "english", "busy": False, "x": 600, "y": 430},
            {"name": "科学老师", "subject": "science", "busy": False, "x": 600, "y": 480}
        ]
        self.spawn_timer = 0
        self.max_students = 8
        self.graduated = 0
        self.total_students = 0
        self.year = 1
        self.phase = "day"
        self.phase_timer = 0
        self.game_over = False
    
    def spawn_student(self):
        if len(self.students) < self.max_students:
            self.students.append(Student(self.year))
    
    def update(self):
        if self.money < -1000:
            self.game_over = True
        
        self.phase_timer += 1
        
        if self.phase == "day":
            if self.phase_timer > 180:
                self.phase = "class"
                self.phase_timer = 0
        
        elif self.phase == "class":
            for teacher in self.teachers:
                if teacher["busy"] and "student" in teacher:
                    student = teacher["student"]
                    student.grade += 0.1
                    if teacher["subject"] == "math":
                        student.math = min(100, student.math + 0.2)
                    elif teacher["subject"] == "english":
                        student.english = min(100, student.english + 0.2)
                    elif teacher["subject"] == "science":
                        student.science = min(100, student.science + 0.2)
            
            if self.phase_timer > 300:
                self.phase = "night"
                self.phase_timer = 0
                for teacher in self.teachers:
                    teacher["busy"] = False
                    teacher.pop("student", None)
        
        elif self.phase == "night":
            if self.phase_timer > 60:
                for student in self.students[:]:
                    student.finished = True
                    self.students.remove(student)
                    self.graduated += 1
                    self.total_students += 1
                    self.reputation += 10
                
                self.spawn_timer += 1
                if self.spawn_timer > 30:
                    self.spawn_timer = 0
                    if random.random() < 0.5 and len(self.students) < self.max_students:
                        self.spawn_student()
                
                self.phase = "day"
                self.phase_timer = 0
                self.day += 1
                
                if self.day > 30:
                    self.year += 1
                    self.day = 1
                    self.money -= 1000
        
        for student in self.students[:]:
            if not student.learning:
                if student.x > student.target_x:
                    student.x -= 1
        
        for student in self.students[:]:
            if student.grade >= 6 and student.finished:
                self.students.remove(student)
    
    def assign_teacher(self, student, teacher):
        if not teacher["busy"] and not student.learning:
            teacher["busy"] = True
            teacher["student"] = student
            student.learning = True
            student.target_x = 550
            student.target_y = teacher["y"]
            return True
        return False
    
    def hire_teacher(self):
        cost = 2000
        if self.money >= cost and len(self.teachers) < 6:
            self.money -= cost
            subjects = ["math", "english", "science"]
            new_id = len(self.teachers) + 1
            self.teachers.append({
                "name": f"老师{new_id}", 
                "subject": random.choice(subjects),
                "busy": False, 
                "x": 600, 
                "y": 380 + (new_id - 1) * 50
            })
            return True
        return False

def school_sim():
    game = SchoolGame()
    
    for _ in range(3):
        game.spawn_student()
    
    while not game.game_over:
        screen.fill((240, 248, 255))
        
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 80))
        pygame.draw.rect(screen, BLUE, (0, 80, 200, HEIGHT - 80))
        
        title = font_large.render(f"学校模拟器 - 第{game.year}年 第{game.day}天", True, BLUE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
        
        info = [
            f"资金: {game.money}元",
            f"声望: {game.reputation}",
            f"在校生: {len(game.students)}人",
            f"毕业总数: {game.graduated}人",
            f"阶段: {game.phase}"
        ]
        
        for i, text in enumerate(info):
            t = font_small.render(text, True, BLACK)
            screen.blit(t, (10, 100 + i * 35))
        
        phase_color = {"day": YELLOW, "class": GREEN, "night": PURPLE}
        phase_text = font_medium.render(f"当前: {game.phase}", True, phase_color[game.phase])
        screen.blit(phase_text, (10, 300))
        
        for i, teacher in enumerate(game.teachers):
            color = GREEN if not teacher["busy"] else RED
            subject_colors = {"math": BLUE, "english": GREEN, "science": PURPLE}
            
            pygame.draw.circle(screen, subject_colors.get(teacher["subject"], WHITE), 
                             (teacher["x"], teacher["y"]), 20)
            pygame.draw.circle(screen, WHITE, (teacher["x"], teacher["y"]), 20, 2)
            
            name = font_small.render(teacher["name"], True, BLACK)
            screen.blit(name, (teacher["x"] - 25, teacher["y"] + 25))
            
            status = "[空闲]" if not teacher["busy"] else "[教学中]"
            s = font_small.render(status, True, GREEN if status == "[空闲]" else RED)
            screen.blit(s, (teacher["x"] - 25, teacher["y"] + 45))
        
        for student in game.students:
            if not student.learning:
                pygame.draw.circle(screen, student.color, (int(student.x), int(student.y)), 15)
                
                info_text = font_small.render(f"{student.name}", True, BLACK)
                screen.blit(info_text, (int(student.x) - 15, int(student.y) - 30))
                
                grade = font_small.render(f"年级:{int(student.grade)}", True, ORANGE)
                screen.blit(grade, (int(student.x) - 25, int(student.y) + 20))
                
                scores = f"M:{int(student.math)} E:{int(student.english)} S:{int(student.science)}"
                score_text = font_small.render(scores, True, BLUE)
                screen.blit(score_text, (int(student.x) - 40, int(student.y) + 40))
        
        pygame.draw.rect(screen, (50, 50, 70), (WIDTH - 220, 100, 200, HEIGHT - 200))
        
        actions = [
            "操作:",
            "",
            "按 1-8 分配学生",
            f"H - 雇佣老师({2000}元)",
            "自动教学进行中...",
            "",
            "目标:",
            "培养学生到6年级毕业"
        ]
        
        for i, text in enumerate(actions):
            t = font_small.render(text, True, WHITE)
            screen.blit(t, (WIDTH - 210, 110 + i * 30))
        
        if game.phase == "class":
            class_text = font_medium.render("上课中...", True, GREEN)
            screen.blit(class_text, (WIDTH - 210, 400))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    game.hire_teacher()
                
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, 
                                 pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8]:
                    idx = event.key - 49
                    if idx < len(game.students):
                        student = game.students[idx]
                        if not student.learning:
                            available_teacher = None
                            for teacher in game.teachers:
                                if not teacher["busy"]:
                                    available_teacher = teacher
                                    break
                            
                            if available_teacher:
                                game.assign_teacher(student, available_teacher)
        
        game.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    result = font_large.render("游戏结束!", True, RED)
    screen.blit(result, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
    
    stats = [
        f"毕业学生: {game.graduated}人",
        f"总收入声望: {game.reputation}"
    ]
    
    for i, text in enumerate(stats):
        t = font_medium.render(text, True, WHITE)
        screen.blit(t, (WIDTH // 2 - 100, HEIGHT // 2 + i * 40))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    school_sim()
