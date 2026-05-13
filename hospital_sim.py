#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医院模拟器 - 模拟经营游戏
管理医院,治疗病人
"""

import pygame
import random
import math

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
PINK = (255, 150, 200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("医院模拟器 - 模拟经营")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 50)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

class Patient:
    def __init__(self, day):
        self.name = random.choice(["张", "李", "王", "刘", "陈", "杨", "赵", "黄"]) + \
                   random.choice(["伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "洋"])
        self.illness = random.choice(["感冒", "发烧", "头痛", "胃痛", "骨折", "感染", "过敏", "咳嗽"])
        self.severity = random.randint(1, 5)
        self.treatment_time = self.severity * 3
        self.waiting = 0
        self.x = WIDTH + random.randint(50, 200)
        self.y = 200 + random.randint(0, 300)
        self.target_x = 700 + random.randint(0, 100)
        self.target_y = 200 + random.randint(0, 300)
        self.treating = False
        self.treated = False
        self.color = random.choice([BLUE, GREEN, PURPLE, ORANGE])

class HospitalGame:
    def __init__(self):
        self.money = 5000
        self.day = 1
        self.reputation = 50
        self.patients = []
        self.doctors = [{"name": "医生1", "busy": False, "x": 600, "y": 400}]
        self.nurses = [{"name": "护士1", "busy": False, "x": 600, "y": 450}]
        self.spawn_timer = 0
        self.max_patients = 5
        self.treated_today = 0
        self.total_patients = 0
        self.game_over = False
    
    def spawn_patient(self):
        if len(self.patients) < self.max_patients:
            self.patients.append(Patient(self.day))
    
    def update(self):
        if self.money < 0:
            self.game_over = True
        
        self.spawn_timer += 1
        if self.spawn_timer > 120:
            self.spawn_timer = 0
            if random.random() < 0.3:
                self.spawn_patient()
        
        for patient in self.patients[:]:
            patient.waiting += 1
            
            if not patient.treating:
                if patient.x > patient.target_x:
                    patient.x -= 1
            else:
                patient.treatment_time -= 1
                if patient.treatment_time <= 0:
                    patient.treated = True
                    self.patients.remove(patient)
                    self.money += 100 * patient.severity
                    self.reputation += 5
                    self.treated_today += 1
                    self.total_patients += 1
                    for doctor in self.doctors:
                        if doctor["busy"] and doctor["treating"] == patient:
                            doctor["busy"] = False
                            doctor.pop("treating", None)
            
            if patient.waiting > 300:
                self.reputation -= 2
                if patient.waiting > 500:
                    self.patients.remove(patient)
                    self.reputation -= 5
    
    def assign_doctor(self, patient):
        for doctor in self.doctors:
            if not doctor["busy"]:
                doctor["busy"] = True
                doctor["treating"] = patient
                patient.treating = True
                patient.target_x = 550
                patient.target_y = doctor["y"]
                return True
        return False
    
    def hire_doctor(self):
        cost = 1000 + len(self.doctors) * 500
        if self.money >= cost:
            self.money -= cost
            new_id = len(self.doctors) + 1
            self.doctors.append({
                "name": f"医生{new_id}", 
                "busy": False, 
                "x": 600, 
                "y": 400 + (new_id - 1) * 50
            })
            return True
        return False
    
    def next_day(self):
        self.day += 1
        self.treated_today = 0
        self.max_patients = min(10, 5 + self.day // 2)
        self.money -= 200 * len(self.doctors)

def hospital_sim():
    game = HospitalGame()
    
    while not game.game_over:
        screen.fill((200, 220, 240))
        
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 80))
        pygame.draw.rect(screen, BLUE, (0, 80, 200, HEIGHT - 80))
        
        title = font_large.render("医院模拟器", True, BLUE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
        
        info = [
            f"资金: {game.money}元",
            f"天数: 第{game.day}天",
            f"声望: {game.reputation}",
            f"今日治疗: {game.treated_today}人",
            f"总治疗: {game.total_patients}人"
        ]
        
        for i, text in enumerate(info):
            t = font_small.render(text, True, BLACK)
            screen.blit(t, (10, 100 + i * 35))
        
        for i, doctor in enumerate(game.doctors):
            color = GREEN if not doctor["busy"] else RED
            pygame.draw.circle(screen, color, (doctor["x"], doctor["y"]), 20)
            pygame.draw.circle(screen, WHITE, (doctor["x"], doctor["y"]), 20, 2)
            
            name = font_small.render(doctor["name"], True, BLACK)
            screen.blit(name, (doctor["x"] - 20, doctor["y"] + 25))
            
            status = "[空闲]" if not doctor["busy"] else "[治疗中]"
            s = font_small.render(status, True, GREEN if status == "[空闲]" else RED)
            screen.blit(s, (doctor["x"] - 25, doctor["y"] + 45))
        
        for patient in game.patients:
            if not patient.treating:
                pygame.draw.circle(screen, patient.color, (int(patient.x), int(patient.y)), 15)
                
                info_text = font_small.render(f"{patient.name}", True, BLACK)
                screen.blit(info_text, (int(patient.x) - 25, int(patient.y) - 30))
                
                illness = font_small.render(f"{patient.illness}", True, RED)
                screen.blit(illness, (int(patient.x) - 20, int(patient.y) - 50))
                
                wait = font_small.render(f"等待:{patient.waiting}", True, ORANGE)
                screen.blit(wait, (int(patient.x) - 25, int(patient.y) + 20))
                
                if patient.waiting > 200:
                    warning = font_small.render("⚠️急需治疗!", True, RED)
                    screen.blit(warning, (int(patient.x) - 35, int(patient.y) - 70))
            else:
                pygame.draw.circle(screen, GREEN, (int(patient.x), int(patient.y)), 15)
                
                progress = 1 - patient.treatment_time / (patient.severity * 3)
                pygame.draw.rect(screen, RED, (int(patient.x) - 20, int(patient.y) - 30, 40, 5))
                pygame.draw.rect(screen, GREEN, 
                               (int(patient.x) - 20, int(patient.y) - 30, int(40 * progress), 5))
        
        pygame.draw.rect(screen, (50, 50, 70), (WIDTH - 220, 100, 200, HEIGHT - 200))
        
        actions = [
            "操作:",
            "",
            "按 1-5 治疗病人",
            f"H - 雇佣医生({1000 + len(game.doctors) * 500}元)",
            "空格 - 下一日"
        ]
        
        for i, text in enumerate(actions):
            t = font_small.render(text, True, WHITE)
            screen.blit(t, (WIDTH - 210, 110 + i * 30))
        
        if game.money < 1000:
            warning = font_small.render("⚠️资金不足!", True, RED)
            screen.blit(warning, (WIDTH - 210, HEIGHT - 150))
        
        if len(game.patients) < game.max_patients:
            hint = font_small.render(f"候诊区有空位({len(game.patients)}/{game.max_patients})", True, GREEN)
            screen.blit(hint, (250, 150))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    if game.hire_doctor():
                        pass
                elif event.key == pygame.K_SPACE:
                    game.next_day()
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                    idx = event.key - 49
                    if idx < len(game.patients):
                        patient = game.patients[idx]
                        if not patient.treating:
                            game.assign_doctor(patient)
        
        game.update()
        clock.tick(60)
    
    screen.fill(BLACK)
    result = font_large.render("游戏结束!", True, RED)
    screen.blit(result, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
    
    stats = [
        f"最终资金: {game.money}元",
        f"存活天数: {game.day}天",
        f"治疗病人: {game.total_patients}人",
        f"最终声望: {game.reputation}"
    ]
    
    for i, text in enumerate(stats):
        t = font_medium.render(text, True, WHITE)
        screen.blit(t, (WIDTH // 2 - 100, HEIGHT // 2 + i * 40))
    
    pygame.display.flip()
    pygame.time.wait(5000)
    pygame.quit()

if __name__ == "__main__":
    hospital_sim()
