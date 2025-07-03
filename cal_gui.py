import tkinter as tk
from tkinter import ttk, messagebox
import threading
import random
import sys
import locale
import tkinter.font  # 추가: 폰트 관련 모듈 명시적 import
import json
import os
import numpy as np

# 상수 정의
COOLDOWN_REDUCTION_MULTIPLIER = 0.8
AWAKENING_MULTIPLIER = 1.2
INSIGNIFICANT_DPM_DIFFERENCE_RATE_THRESHOLD = 0.01
INSIGNIFICANT_APM_DIFFERENCE_THRESHOLD = 1
SETTINGS_FILE = "settings.json"

# 한글 인코딩 설정
if sys.platform.startswith('linux'):
    try:
        locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass


class Character:
    DEFAULT_ATTACKS_PER_MINUTE = 129
    DEFAULT_ATTACK_POWER = 12.42
    DEFAULT_P_CRITICAL = 88.08 / 100
    DEFAULT_P_STRONG_HIT = 51.91 / 100
    DEFAULT_P_DOUBLE_SHOT = 22.44 / 100
    DEFAULT_P_TRIPLE_SHOT = 21.11 / 100
    DEFAULT_CRITICAL_MULTIPLIER = 1190.41 / 100
    DEFAULT_STRONG_HIT_MULTIPLIER = 159.03 / 100
    DEFAULT_AWAKENING = True
    DEFAULT_COOLDOWN = True
    DEFAULT_DAMAGE_SKILL_1 = 430 / 100
    DEFAULT_DAMAGE_SKILL_2 = 190 / 100
    DEFAULT_DAMAGE_SKILL_3 = 280 / 100
    DEFAULT_CRITICAL_COOLDOWN = 2
    DEFAULT_SKILL_COOLDOWN = 10
    DEFAULT_HIT_1 = 1
    DEFAULT_HIT_2 = 3
    DEFAULT_HIT_3 = 3

    def __init__(self, name="Character"):
        # 기본 설정
        self.name = name
        self.is_awakening = Character.DEFAULT_AWAKENING
        self.is_cooldown = Character.DEFAULT_COOLDOWN
        
        # 공격 관련
        self.attacks_per_minute = Character.DEFAULT_ATTACKS_PER_MINUTE
        self.attack_power = Character.DEFAULT_ATTACK_POWER
        
        # 확률 관련
        self.p_critical = Character.DEFAULT_P_CRITICAL
        self.p_strong_hit = Character.DEFAULT_P_STRONG_HIT
        self.p_double_shot = Character.DEFAULT_P_DOUBLE_SHOT
        self.p_triple_shot = Character.DEFAULT_P_TRIPLE_SHOT
        
        # 배율 관련
        self.critical_multiplier = Character.DEFAULT_CRITICAL_MULTIPLIER
        self.strong_hit_multiplier = Character.DEFAULT_STRONG_HIT_MULTIPLIER
        self.awakening_multiplier = AWAKENING_MULTIPLIER if self.is_awakening else 1
        
        # 데미지 배율
        self.damage_skill_1 = Character.DEFAULT_DAMAGE_SKILL_1
        self.damage_skill_2 = Character.DEFAULT_DAMAGE_SKILL_2
        self.damage_skill_3 = Character.DEFAULT_DAMAGE_SKILL_3
        
        # 쿨타임 설정
        self.critical_cooldown = Character.DEFAULT_CRITICAL_COOLDOWN
        self.skill_cooldown = Character.DEFAULT_SKILL_COOLDOWN
        
        # 타수 관련
        self.hit_1 = Character.DEFAULT_HIT_1
        self.hit_2 = Character.DEFAULT_HIT_2
        self.hit_3 = Character.DEFAULT_HIT_3
        
        # 쿨타임 감소 적용
        if self.is_cooldown:
            self.critical_cooldown *= COOLDOWN_REDUCTION_MULTIPLIER
            self.skill_cooldown *= COOLDOWN_REDUCTION_MULTIPLIER
    
    def simulate_damage(self, minutes=0.5, simulations=10000):
        """캐릭터의 데미지를 시뮬레이션하여 분당 데미지(DPM)를 계산"""
        return simulate_attacks_with_critical_and_skill(
            minutes=minutes,
            simulations=simulations,
            attack_power=self.attack_power,
            attacks_per_minute=self.attacks_per_minute,
            damage_skill_1=self.damage_skill_1,
            damage_skill_2=self.damage_skill_2,
            damage_skill_3=self.damage_skill_3,
            p_critical=self.p_critical,
            p_strong_hit=self.p_strong_hit,
            p_double_shot=self.p_double_shot,
            p_triple_shot=self.p_triple_shot,
            critical_multiplier=self.critical_multiplier,
            strong_hit_multiplier=self.strong_hit_multiplier,
            awakening_multiplier=self.awakening_multiplier,
            critical_cooldown=self.critical_cooldown,
            skill_cooldown=self.skill_cooldown,
            hit_1=self.hit_1,
            hit_2=self.hit_2,
            hit_3=self.hit_3
        )
    
    def print_stats(self):
        """캐릭터의 스탯을 출력"""
        print(f"=== {self.name} 스탯 ===")
        print(f"공격 속도: {self.attacks_per_minute}회/분")
        print(f"공격력: {self.attack_power}M")
        print(f"치명 확률: {self.p_critical*100:.2f}%")
        print(f"강타 확률: {self.p_strong_hit*100:.2f}%")
        print(f"더블샷 확률: {self.p_double_shot*100:.2f}%")
        print(f"트리플샷 확률: {self.p_triple_shot*100:.2f}%")
        print(f"치명 피해: {self.critical_multiplier:.4f}")
        print(f"강타 피해: {self.strong_hit_multiplier:.4f}")
        print(f"각성 배율: {self.awakening_multiplier:.1f}")
        print(f"일반 공격 데미지 배율: {self.damage_skill_1:.2f}")
        print(f"치명타 공격 데미지 배율: {self.damage_skill_2:.2f}")
        print(f"스킬 데미지 배율: {self.damage_skill_3:.2f}")
        print(f"치명타 쿨타임: {self.critical_cooldown:.1f}초")
        print(f"스킬 쿨타임: {self.skill_cooldown:.1f}초")
        print()


def simulate_attacks_with_critical_and_skill(
    minutes=1, 
    simulations=1000,
    attack_power=1,
    attacks_per_minute=120,
    damage_skill_1=1, 
    damage_skill_2=2, 
    damage_skill_3=5, 
    p_critical=0.5, 
    p_strong_hit=0.1, 
    p_double_shot=0.1, 
    p_triple_shot=0.05,
    critical_multiplier=2, 
    strong_hit_multiplier=2, 
    awakening_multiplier=1,
    critical_cooldown=2, 
    skill_cooldown=10, 
    hit_1=1, 
    hit_2=1, 
    hit_3=1
):
    attacks_per_minute = int(attacks_per_minute)
    total_damage = 0
    total_attacks = 0
    
    # 소수점 시간을 처리하기 위해 초 단위로 변환
    total_seconds = minutes * 60
    attack_interval = 60 / attacks_per_minute
    
    for _ in range(simulations):
        damage_this_simulation = 0
        time_since_last_critical = critical_cooldown
        time_since_last_skill = skill_cooldown
        current_time = 0
        
        while current_time < total_seconds:
            current_time += attack_interval
            time_since_last_critical += attack_interval
            time_since_last_skill += attack_interval
            
            # 1. 스킬
            if time_since_last_skill >= skill_cooldown: # 스킬 쿨타임 체크
                base_damage = damage_skill_3 * attack_power * awakening_multiplier
                for _ in range(hit_3):
                    damage_tick = base_damage
                    if random.random() < p_critical:
                        damage_tick *= critical_multiplier
                    if random.random() < p_strong_hit:
                        damage_tick *= strong_hit_multiplier
                    damage_this_simulation += damage_tick
                total_attacks += hit_3
                time_since_last_skill = 0

            # 2. 치명타
            elif time_since_last_critical >= critical_cooldown and random.random() < p_critical: # 치명타 쿨타임 체크 & 치명타 확률 체크
                base_damage = damage_skill_2 * attack_power * critical_multiplier * awakening_multiplier
                for _ in range(hit_2):
                    damage_tick = base_damage
                    if random.random() < p_strong_hit:
                        damage_tick *= strong_hit_multiplier
                    damage_this_simulation += damage_tick
                total_attacks += hit_2
                time_since_last_critical = 0

            # 3. 일반 공격
            else:
                base_damage = damage_skill_1 * attack_power * awakening_multiplier

                # 더블샷/트리플샷 확률 계산
                if random.random() < p_triple_shot:
                    shot_count = 3
                elif random.random() < p_double_shot:
                    shot_count = 2
                else:
                    shot_count = 1

                # 데미지 계산
                for _ in range(shot_count):
                    for _ in range(hit_1):
                        damage_tick = base_damage
                        if random.random() < p_strong_hit:
                            damage_tick *= strong_hit_multiplier
                        damage_this_simulation += damage_tick
                total_attacks += shot_count * hit_1
        total_damage += damage_this_simulation
    
    # 분당 데미지(DPM)와 분당 공격 횟수(APM) 반환
    return total_damage / (simulations * minutes), total_attacks / (simulations * minutes)


def compare_characters(char1, char2, minutes=0.5, simulations=10000, text_widget=None):
    """두 캐릭터의 데미지를 비교"""
    if text_widget:
        text_widget.insert(tk.END, "=" * 60 + "\n", "normal")
        text_widget.insert(tk.END, "캐릭터 데미지 비교\n", "normal")
        text_widget.insert(tk.END, "=" * 60 + "\n", "normal")
        
        # 공통 스탯 (데미지 배율) 먼저 출력
        text_widget.insert(tk.END, "=== 공통 스탯 ===\n", "normal")
        text_widget.insert(tk.END, f"일반 공격 데미지 배율: {char1.damage_skill_1:.2f} (타수: {char1.hit_1}) → 총합: {char1.damage_skill_1 * char1.hit_1:.2f}\n", "normal")
        text_widget.insert(tk.END, f"치명타 공격 데미지 배율: {char1.damage_skill_2:.2f} (타수: {char1.hit_2}) → 총합: {char1.damage_skill_2 * char1.hit_2:.2f}\n", "normal")
        text_widget.insert(tk.END, f"전용 스킬 데미지 배율: {char1.damage_skill_3:.2f} (타수: {char1.hit_3}) → 총합: {char1.damage_skill_3 * char1.hit_3:.2f}\n", "normal")
        text_widget.insert(tk.END, "\n", "normal")
    else:
        print("=" * 60)
        print("캐릭터 데미지 비교")
        print("=" * 60)
        print("=== 공통 스탯 ===")
        print(f"일반 공격 데미지 배율: {char1.damage_skill_1:.2f} (타수: {char1.hit_1}) → 총합: {char1.damage_skill_1 * char1.hit_1:.2f}")
        print(f"치명타 공격 데미지 배율: {char1.damage_skill_2:.2f} (타수: {char1.hit_2}) → 총합: {char1.damage_skill_2 * char1.hit_2:.2f}")
        print(f"전용 스킬 데미지 배율: {char1.damage_skill_3:.2f} (타수: {char1.hit_3}) → 총합: {char1.damage_skill_3 * char1.hit_3:.2f}")
        print()
    
    # 각 캐릭터의 스탯 출력
    if text_widget:
        print_stats_to_widget(char1, text_widget, char2, is_second_char=False)  # char1은 증감 표시 안함
        print_stats_to_widget(char2, text_widget, char1, is_second_char=True)   # char2만 증감 표시
    else:
        char1.print_stats()
        char2.print_stats()
    
    # 데미지 계산
    damage1, apm1 = char1.simulate_damage(minutes, simulations)
    damage2, apm2 = char2.simulate_damage(minutes, simulations)
    
    # 결과 출력
    if text_widget:
        text_widget.insert(tk.END, "=" * 60 + "\n", "normal")
        text_widget.insert(tk.END, "데미지 비교 결과\n", "normal")
        text_widget.insert(tk.END, "=" * 60 + "\n", "normal")
        text_widget.insert(tk.END, f"{char1.name} DPM: {damage1:,.2f} | APM: {apm1:.1f}\n", "normal")
        text_widget.insert(tk.END, f"{char2.name} DPM: {damage2:,.2f} | APM: {apm2:.1f}\n", "normal")
        text_widget.insert(tk.END, "\n", "normal")
    else:
        print("=" * 60)
        print("데미지 비교 결과")
        print("=" * 60)
        print(f"{char1.name} DPM: {damage1:,.2f} | APM: {apm1:.1f}")
        print(f"{char2.name} DPM: {damage2:,.2f} | APM: {apm2:.1f}")
        print()
    
    if damage1 > damage2:
        diff = damage1 - damage2
        percentage = (diff / damage2) * 100
        if text_widget:
            if percentage <= INSIGNIFICANT_DPM_DIFFERENCE_RATE_THRESHOLD:
                text_widget.insert(tk.END, f"{char2.name}이 {char1.name}보다 {diff:,.2f} DPM 낮음 (의미 없음) ▼\n", "insignificant")
            else:
                text_widget.insert(tk.END, f"{char2.name}이 {char1.name}보다 {diff:,.2f} DPM 낮음 ({percentage:.2f}% 약함) ▼\n", "decrease")
        else:
            if percentage <= INSIGNIFICANT_DPM_DIFFERENCE_RATE_THRESHOLD:
                print(f"{char2.name}이 {char1.name}보다 {diff:,.2f} DPM 낮음 (의미 없음)")
            else:
                print(f"{char2.name}이 {char1.name}보다 {diff:,.2f} DPM 낮음 ({percentage:.2f}% 약함)")
    elif damage2 > damage1:
        diff = damage2 - damage1
        percentage = (diff / damage1) * 100
        if text_widget:
            if percentage <= INSIGNIFICANT_DPM_DIFFERENCE_RATE_THRESHOLD:
                text_widget.insert(tk.END, f"{char2.name}가 {char1.name}보다 {diff:,.2f} DPM 높음 (의미 없음) ▲\n", "insignificant")
            else:
                text_widget.insert(tk.END, f"{char2.name}가 {char1.name}보다 {diff:,.2f} DPM 높음 ({percentage:.2f}% 강함) ▲\n", "increase")
        else:
            if percentage <= INSIGNIFICANT_DPM_DIFFERENCE_RATE_THRESHOLD:
                print(f"{char2.name}이 {char1.name}보다 {diff:,.2f} DPM 높음 (의미 없음)")
            else:
                print(f"{char2.name}이 {char1.name}보다 {diff:,.2f} DPM 높음 ({percentage:.2f}% 강함)")
    else:
        if text_widget:
            text_widget.insert(tk.END, "두 캐릭터의 데미지가 동일합니다.\n", "normal")
        else:
            print("두 캐릭터의 데미지가 동일합니다.")

    # APM 비교
    apm_diff = apm1 - apm2
    if text_widget:
        if apm_diff > INSIGNIFICANT_APM_DIFFERENCE_THRESHOLD:  # 캐릭터1이 더 빠름
            apm_text = f"{char2.name}가 {char1.name}보다 {abs(apm_diff):.1f} APM 느림 ▼"
            apm_tag = "decrease"
        elif apm_diff < -INSIGNIFICANT_APM_DIFFERENCE_THRESHOLD:  # 캐릭터2가 더 빠름
            apm_text = f"{char2.name}가 {char1.name}보다 {abs(apm_diff):.1f} APM 빠름 ▲"
            apm_tag = "increase"
        else:  # 차이가 미미함
            apm_text = f"APM 차이: {apm_diff:+.1f} ({apm1:.1f} vs {apm2:.1f}) (의미 없음)"
            apm_tag = "insignificant"
        text_widget.insert(tk.END, apm_text + "\n", apm_tag)
    else:
        print(f"APM 차이: {apm_diff:+.1f} ({apm1:.1f} vs {apm2:.1f})")

    if text_widget:
        text_widget.insert(tk.END, "=" * 60 + "\n", "normal")
    else:
        print("=" * 60)


def print_stat_with_comparison(text_widget, label, value, compare_char, compare_attr, format_str="{:.2f}", reverse=False, is_second_char=False, multiply_compare=1):
    """능력치를 비교하여 출력하는 헬퍼 함수"""
    stat_text = f"{label}: {format_str.format(value)}"
    if compare_char and is_second_char:  # 캐릭터(후)에만 증감 표시
        compare_value = getattr(compare_char, compare_attr) * multiply_compare
        if reverse:
            # 쿨타임처럼 낮을수록 좋은 경우
            if value < compare_value:
                stat_text += " ▲"
                text_widget.insert(tk.END, stat_text + "\n", "increase")
            elif value > compare_value:
                stat_text += " ▼"
                text_widget.insert(tk.END, stat_text + "\n", "decrease")
            else:
                text_widget.insert(tk.END, stat_text + "\n", "normal")
        else:
            # 일반적으로 높을수록 좋은 경우
            if value > compare_value:
                stat_text += " ▲"
                text_widget.insert(tk.END, stat_text + "\n", "increase")
            elif value < compare_value:
                stat_text += " ▼"
                text_widget.insert(tk.END, stat_text + "\n", "decrease")
            else:
                text_widget.insert(tk.END, stat_text + "\n", "normal")
    else:
        text_widget.insert(tk.END, stat_text + "\n", "normal")


def print_stats_to_widget(char, text_widget, compare_char=None, is_second_char=False):
    """캐릭터의 스탯을 Text 위젯에 출력 (비교용)"""
    text_widget.insert(tk.END, f"=== {char.name} 스탯 ===\n", "normal")
    
    # 각성 여부 표시
    awakening_status = "각성 활성화" if char.is_awakening else "각성 비활성화"
    if compare_char and is_second_char:
        # 캐릭터(후)에서만 비교하여 증감 표시
        if char.is_awakening > compare_char.is_awakening:
            awakening_tag = "increase"
            awakening_status += " ▲"
        elif char.is_awakening < compare_char.is_awakening:
            awakening_tag = "decrease"
            awakening_status += " ▼"
        else:
            awakening_tag = "normal"
    else:
        # 캐릭터(전)에서는 항상 검은색으로 표시
        awakening_tag = "normal"
    text_widget.insert(tk.END, f"각성 상태: {awakening_status}\n", awakening_tag)
    
    # 각 능력치 출력 (높을수록 좋은 것들)
    print_stat_with_comparison(text_widget, "공격 속도", char.attacks_per_minute, compare_char, "attacks_per_minute", "{}회/분", is_second_char=is_second_char)
    print_stat_with_comparison(text_widget, "공격력", char.attack_power, compare_char, "attack_power", "{}M", is_second_char=is_second_char)
    print_stat_with_comparison(text_widget, "치명 확률", char.p_critical * 100, compare_char, "p_critical", "{:.2f}%", reverse=False, is_second_char=is_second_char, multiply_compare=100)
    print_stat_with_comparison(text_widget, "강타 확률", char.p_strong_hit * 100, compare_char, "p_strong_hit", "{:.2f}%", reverse=False, is_second_char=is_second_char, multiply_compare=100)
    print_stat_with_comparison(text_widget, "더블샷 확률", char.p_double_shot * 100, compare_char, "p_double_shot", "{:.2f}%", reverse=False, is_second_char=is_second_char, multiply_compare=100)
    print_stat_with_comparison(text_widget, "트리플샷 확률", char.p_triple_shot * 100, compare_char, "p_triple_shot", "{:.2f}%", reverse=False, is_second_char=is_second_char, multiply_compare=100)
    print_stat_with_comparison(text_widget, "치명 피해", char.critical_multiplier * 100, compare_char, "critical_multiplier", "{:.2f}%", is_second_char=is_second_char, multiply_compare=100)
    print_stat_with_comparison(text_widget, "강타 피해", char.strong_hit_multiplier * 100, compare_char, "strong_hit_multiplier", "{:.2f}%", is_second_char=is_second_char, multiply_compare=100)
    print_stat_with_comparison(text_widget, "각성 배율", char.awakening_multiplier, compare_char, "awakening_multiplier", "{:.1f}", is_second_char=is_second_char)
    
    # 쿨타임 (낮을수록 좋음)
    print_stat_with_comparison(text_widget, "치명타 쿨타임", char.critical_cooldown, compare_char, "critical_cooldown", "{:.1f}초", reverse=True, is_second_char=is_second_char)
    print_stat_with_comparison(text_widget, "스킬 쿨타임", char.skill_cooldown, compare_char, "skill_cooldown", "{:.1f}초", reverse=True, is_second_char=is_second_char)
    
    text_widget.insert(tk.END, "\n", "normal")


class CharacterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("캐릭터 추가스펙 계산기")
        # 창 크기 설정 (가로는 자동, 세로는 900)
        self.root.geometry("1x900")
        self.root.update_idletasks()
        self.root.geometry("")
        # 창이 내용에 맞게 자동으로 크기 조정되도록 설정
        self.root.resizable(True, True)
        
        # 한글 폰트 설정
        self.setup_korean_font()
        
        # 스타일 설정
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Korean.TCheckbutton", font=self.text_font)
        style.configure("Korean.TButton", font=self.text_font)
        
        self.create_widgets()
        
        # Text 위젯 색상 태그 설정
        self.setup_text_tags()
        
        # 프로그램 시작 시 JSON 파일이 있으면 자동으로 불러오기
        self.root.after(100, self.auto_load_settings)
    
    def setup_korean_font(self):
        """한글 폰트 설정 (WSL2 등 환경 자동 대응)"""
        try:
            # Linux에서 사용 가능한 한글 폰트들
            korean_fonts = [
                'NanumGothic', 'NanumBarunGothic', 'NanumSquare', 'NanumMyeongjo',
                'Malgun Gothic', 'Dotum', 'Gulim', 'Batang',
                'DejaVu Sans', 'Liberation Sans', 'Ubuntu', 'Noto Sans CJK KR'
            ]

            # 사용 가능한 폰트 찾기 (tkinter.font 명시적 사용)
            available_fonts = list(tkinter.font.families())
            selected_font = None

            for font_name in korean_fonts:
                if font_name in available_fonts:
                    selected_font = font_name
                    break

            if selected_font:
                # 기본 폰트 설정
                default_font = tkinter.font.nametofont("TkDefaultFont")
                default_font.configure(family=selected_font, size=10)
                # 고정폭 폰트 설정
                fixed_font = tkinter.font.nametofont("TkFixedFont")
                fixed_font.configure(family=selected_font, size=10)
                # 텍스트 위젯 폰트 설정
                self.text_font = (selected_font, 10)
                print(f"[INFO] 한글 폰트 적용: {selected_font}")
            else:
                # 폰트를 찾지 못한 경우 안내 메시지 출력
                print("[WARNING] 시스템에 한글 폰트가 설치되어 있지 않습니다.\n"
                      "WSL2 Ubuntu 환경이라면 아래 명령어로 한글 폰트를 설치하세요:\n"
                      "sudo apt update && sudo apt install fonts-nanum fonts-nanum-coding fonts-nanum-extra\n"
                      "설치 후 WSL을 재시작하세요.")
                self.text_font = ("TkDefaultFont", 10)
        except Exception as e:
            print(f"폰트 설정 중 오류: {e}")
            self.text_font = ("TkDefaultFont", 10)
    
    def setup_text_tags(self):
        """Text 위젯의 색상 태그 설정"""
        self.result_text.tag_configure("increase", foreground="blue")
        self.result_text.tag_configure("decrease", foreground="red")
        self.result_text.tag_configure("normal", foreground="black")
        self.result_text.tag_configure("insignificant", foreground="gray")
    
    def save_settings(self):
        """현재 설정을 JSON 파일로 저장"""
        settings = {
            "char1": {
                "name": self.char1_name_var.get(),
                "awakening": self.char1_awakening_var.get(),
                "cooldown": self.char1_cooldown_var.get(),
                "attacks": self.char1_attacks_var.get(),
                "attack_power": self.char1_attack_power_var.get(),
                "critical": self.char1_critical_var.get(),
                "strong_hit": self.char1_strong_hit_var.get(),
                "double_shot": self.char1_double_shot_var.get(),
                "triple_shot": self.char1_triple_shot_var.get(),
                "critical_mult": self.char1_critical_mult_var.get(),
                "strong_hit_mult": self.char1_strong_hit_mult_var.get()
            },
            "char2": {
                "name": self.char2_name_var.get(),
                "awakening": self.char2_awakening_var.get(),
                "cooldown": self.char2_cooldown_var.get(),
                "attacks": self.char2_attacks_var.get(),
                "attack_power": self.char2_attack_power_var.get(),
                "critical": self.char2_critical_var.get(),
                "strong_hit": self.char2_strong_hit_var.get(),
                "double_shot": self.char2_double_shot_var.get(),
                "triple_shot": self.char2_triple_shot_var.get(),
                "critical_mult": self.char2_critical_mult_var.get(),
                "strong_hit_mult": self.char2_strong_hit_mult_var.get()
            },
            "common": {
                "damage_1": self.damage_1_var.get(),
                "damage_2": self.damage_2_var.get(),
                "damage_3": self.damage_3_var.get(),
                "hit_1": self.hit_1_var.get(),
                "hit_2": self.hit_2_var.get(),
                "hit_3": self.hit_3_var.get(),
                "critical_cd": self.critical_cd_var.get(),
                "skill_cd": self.skill_cd_var.get()
            },
            "simulation": {
                "minutes": self.minutes_var.get(),
                "simulations": self.simulations_var.get()
            }
        }
        
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            print("설정이 저장되었습니다.")
        except Exception as e:
            print(f"설정 저장 중 오류: {e}")
    
    def load_settings(self):
        """JSON 파일에서 설정을 불러옴"""
        if not os.path.exists(SETTINGS_FILE):
            return False
        
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
            
            # 캐릭터 1 설정 불러오기
            if "char1" in settings:
                char1 = settings["char1"]
                self.char1_name_var.set(char1.get("name", "캐릭터(전)"))
                self.char1_awakening_var.set(char1.get("awakening", True))
                self.char1_cooldown_var.set(char1.get("cooldown", True))
                self.char1_attacks_var.set(char1.get("attacks", "129"))
                self.char1_attack_power_var.set(char1.get("attack_power", "12.42"))
                self.char1_critical_var.set(char1.get("critical", "88.08"))
                self.char1_strong_hit_var.set(char1.get("strong_hit", "51.91"))
                self.char1_double_shot_var.set(char1.get("double_shot", "22.36"))
                self.char1_triple_shot_var.set(char1.get("triple_shot", "21.11"))
                self.char1_critical_mult_var.set(char1.get("critical_mult", "1184.28"))
                self.char1_strong_hit_mult_var.set(char1.get("strong_hit_mult", "158.03"))
            
            # 캐릭터 2 설정 불러오기
            if "char2" in settings:
                char2 = settings["char2"]
                self.char2_name_var.set(char2.get("name", "캐릭터(후)"))
                self.char2_awakening_var.set(char2.get("awakening", True))
                self.char2_cooldown_var.set(char2.get("cooldown", True))
                self.char2_attacks_var.set(char2.get("attacks", "129"))
                self.char2_attack_power_var.set(char2.get("attack_power", "12.42"))
                self.char2_critical_var.set(char2.get("critical", "88.08"))
                self.char2_strong_hit_var.set(char2.get("strong_hit", "51.91"))
                self.char2_double_shot_var.set(char2.get("double_shot", "22.36"))
                self.char2_triple_shot_var.set(char2.get("triple_shot", "21.11"))
                self.char2_critical_mult_var.set(char2.get("critical_mult", "1184.28"))
                self.char2_strong_hit_mult_var.set(char2.get("strong_hit_mult", "158.03"))
            
            # 공통 설정 불러오기
            if "common" in settings:
                common = settings["common"]
                self.damage_1_var.set(common.get("damage_1", str(round(Character.DEFAULT_DAMAGE_SKILL_1*100, 2))))
                self.damage_2_var.set(common.get("damage_2", str(round(Character.DEFAULT_DAMAGE_SKILL_2*100, 2))))
                self.damage_3_var.set(common.get("damage_3", str(round(Character.DEFAULT_DAMAGE_SKILL_3*100, 2))))
                self.hit_1_var.set(common.get("hit_1", str(Character.DEFAULT_HIT_1)))
                self.hit_2_var.set(common.get("hit_2", str(Character.DEFAULT_HIT_2)))
                self.hit_3_var.set(common.get("hit_3", str(Character.DEFAULT_HIT_3)))
                self.critical_cd_var.set(common.get("critical_cd", str(Character.DEFAULT_CRITICAL_COOLDOWN)))
                self.skill_cd_var.set(common.get("skill_cd", str(Character.DEFAULT_SKILL_COOLDOWN)))
            
            # 시뮬레이션 설정 불러오기
            if "simulation" in settings:
                sim = settings["simulation"]
                self.minutes_var.set(sim.get("minutes", "0.5"))
                self.simulations_var.set(sim.get("simulations", "10000"))
            
            print("설정을 불러왔습니다.")
            return True
            
        except Exception as e:
            print(f"설정 불러오기 중 오류: {e}")
            return False
    
    def auto_load_settings(self):
        """프로그램 시작 시 자동으로 설정 파일 불러오기"""
        if self.load_settings():
            print("프로그램 시작 시 설정 파일을 자동으로 불러왔습니다.")
        # 설정 불러오기 후 초기값 저장 (JSON에서 불러온 값이 초기값이 되도록)
        self.save_initial_values()
    
    def validate_numeric_input(self, value, min_value=0, max_value=None, field_name="값"):
        """숫자 입력 검증"""
        try:
            num_value = float(value)
            if num_value < min_value:
                messagebox.showwarning("입력 경고", f"{field_name}은 {min_value} 이상이어야 합니다.")
                return False
            if max_value is not None and num_value > max_value:
                messagebox.showwarning("입력 경고", f"{field_name}은 {max_value} 이하여야 합니다.")
                return False
            return True
        except ValueError:
            messagebox.showerror("입력 오류", f"{field_name}에 숫자를 입력해주세요.")
            return False
    
    def validate_integer_input(self, value, min_value=1, field_name="값"):
        """정수 입력 검증"""
        try:
            int_value = int(float(value))
            if int_value < min_value:
                messagebox.showwarning("입력 경고", f"{field_name}은 {min_value} 이상이어야 합니다.")
                return False
            return True
        except ValueError:
            messagebox.showerror("입력 오류", f"{field_name}에 정수를 입력해주세요.")
            return False
    
    def limit_probability(self, char_prefix, prob_type):
        """확률 값을 100% 이하로 제한하는 함수"""
        try:
            var_name = f"{char_prefix}_{prob_type}_var"
            var = getattr(self, var_name)
            current_value = float(var.get())
            
            if current_value > 100:
                var.set("100.00")
                print(f"{prob_type} 확률이 100%를 초과하여 100%로 제한되었습니다.")
        except ValueError:
            # 숫자가 아닌 값이 입력된 경우 기본값으로 설정
            default_values = {
                'critical': round(Character.DEFAULT_P_CRITICAL * 100, 2),
                'strong_hit': round(Character.DEFAULT_P_STRONG_HIT * 100, 2),
                'double_shot': round(Character.DEFAULT_P_DOUBLE_SHOT * 100, 2),
                'triple_shot': round(Character.DEFAULT_P_TRIPLE_SHOT * 100, 2)
            }
            var.set(str(default_values.get(prob_type, "0.00")))
            print(f"{prob_type} 확률에 잘못된 값이 입력되어 기본값으로 설정되었습니다.")
        
    def create_widgets(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        for i in range(2):
            main_frame.grid_columnconfigure(i, minsize=140)

        # 캐릭터 1 프레임
        char1_frame = ttk.LabelFrame(main_frame, text="캐릭터 1", padding="2", style="Korean.TLabelframe")
        char1_frame.grid(row=0, column=0, sticky=tk.NW, padx=(2, 8), pady=(4, 0))
        # 캐릭터 2 프레임
        char2_frame = ttk.LabelFrame(main_frame, text="캐릭터 2", padding="2", style="Korean.TLabelframe")
        char2_frame.grid(row=0, column=1, sticky=tk.NW, padx=0, pady=(4, 0))

        # 공통 설정 프레임 (2열 4행)
        common_frame = ttk.LabelFrame(main_frame, text="공통 설정", padding="2", style="Korean.TLabelframe")
        common_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 2), padx=(2, 2))
        entry_width = 12
        entry_justify = 'right'
        entry_padx_1 = (4, 8)
        entry_padx_2 = (31, 2)
        label_padx_1 = (2, 3)
        label_padx_2 = (14, 2)
        # 1행
        ttk.Label(common_frame, text="일반 공격 배율 (%):", font=self.text_font).grid(row=0, column=0, sticky=tk.W, padx=label_padx_1)
        self.damage_1_var = tk.StringVar(value=str(round(Character.DEFAULT_DAMAGE_SKILL_1*100, 2)))
        ttk.Entry(common_frame, textvariable=self.damage_1_var, width=entry_width, font=self.text_font, justify=entry_justify).grid(row=0, column=1, sticky=tk.W, padx=entry_padx_1)
        ttk.Label(common_frame, text="일반 공격 타수:", font=self.text_font).grid(row=0, column=2, sticky=tk.W, padx=label_padx_2)
        self.hit_1_var = tk.StringVar(value="1")
        ttk.Entry(common_frame, textvariable=self.hit_1_var, width=entry_width, font=self.text_font, justify=entry_justify).grid(row=0, column=3, sticky=tk.W, padx=entry_padx_2)
        # 2행
        ttk.Label(common_frame, text="치명타 공격 배율 (%):", font=self.text_font).grid(row=1, column=0, sticky=tk.W, padx=label_padx_1)
        self.damage_2_var = tk.StringVar(value=str(round(Character.DEFAULT_DAMAGE_SKILL_2*100, 2)))
        ttk.Entry(common_frame, textvariable=self.damage_2_var, width=entry_width, font=self.text_font, justify=entry_justify).grid(row=1, column=1, sticky=tk.W, padx=entry_padx_1)
        ttk.Label(common_frame, text="치명타 공격 타수:", font=self.text_font).grid(row=1, column=2, sticky=tk.W, padx=label_padx_2)
        self.hit_2_var = tk.StringVar(value="1")
        ttk.Entry(common_frame, textvariable=self.hit_2_var, width=entry_width, font=self.text_font, justify=entry_justify).grid(row=1, column=3, sticky=tk.W, padx=entry_padx_2)
        # 3행
        ttk.Label(common_frame, text="전용 스킬 배율 (%):", font=self.text_font).grid(row=2, column=0, sticky=tk.W, padx=label_padx_1)
        self.damage_3_var = tk.StringVar(value=str(round(Character.DEFAULT_DAMAGE_SKILL_3*100, 2)))
        ttk.Entry(common_frame, textvariable=self.damage_3_var, width=entry_width, font=self.text_font, justify=entry_justify).grid(row=2, column=1, sticky=tk.W, padx=entry_padx_1)
        ttk.Label(common_frame, text="전용 스킬 타수:", font=self.text_font).grid(row=2, column=2, sticky=tk.W, padx=label_padx_2)
        self.hit_3_var = tk.StringVar(value="1")
        ttk.Entry(common_frame, textvariable=self.hit_3_var, width=entry_width, font=self.text_font, justify=entry_justify).grid(row=2, column=3, sticky=tk.W, padx=entry_padx_2)
        # 4행
        ttk.Label(common_frame, text="치명타 쿨타임 (초):", font=self.text_font).grid(row=3, column=0, sticky=tk.W, padx=label_padx_1)
        self.critical_cd_var = tk.StringVar(value=str(Character.DEFAULT_CRITICAL_COOLDOWN))
        ttk.Entry(common_frame, textvariable=self.critical_cd_var, width=entry_width, font=self.text_font, justify=entry_justify).grid(row=3, column=1, sticky=tk.W, padx=entry_padx_1)
        ttk.Label(common_frame, text="스킬 쿨타임 (초):", font=self.text_font).grid(row=3, column=2, sticky=tk.W, padx=label_padx_2)
        self.skill_cd_var = tk.StringVar(value=str(Character.DEFAULT_SKILL_COOLDOWN))
        ttk.Entry(common_frame, textvariable=self.skill_cd_var, width=entry_width, font=self.text_font, justify=entry_justify).grid(row=3, column=3, sticky=tk.W, padx=entry_padx_2)

        # 시뮬레이션 설정 프레임
        simulation_frame = ttk.LabelFrame(main_frame, text="시뮬레이션 설정", padding="2", style="Korean.TLabelframe")
        simulation_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(2, 2), padx=(2, 2))
        ttk.Label(simulation_frame, text="시뮬레이션 시간 (분):", font=self.text_font).grid(row=0, column=0, sticky=tk.W, padx=(2, 6))
        self.minutes_var = tk.StringVar(value="0.5")
        ttk.Entry(simulation_frame, textvariable=self.minutes_var, width=entry_width, font=self.text_font, justify=entry_justify).grid(row=0, column=1, sticky=tk.W, padx=entry_padx_1)
        ttk.Label(simulation_frame, text="시뮬레이션 횟수:", font=self.text_font).grid(row=0, column=2, sticky=tk.W, padx=label_padx_2)
        self.simulations_var = tk.StringVar(value="10000")
        ttk.Entry(simulation_frame, textvariable=self.simulations_var, width=entry_width, font=self.text_font, justify=entry_justify).grid(row=0, column=3, sticky=tk.W, padx=(35, 2))

        # 버튼 프레임 (2줄 3열)
        button_width = 18
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        # 버튼들을 2줄 3열로 배치 (일정한 너비와 간격)
        # 첫 번째 줄: 기본 설정 관련
        ttk.Button(button_frame, text="초기 값으로 돌리기", command=self.set_default_values, style="Korean.TButton", width=button_width).grid(row=0, column=0, padx=8, pady=4)
        ttk.Button(button_frame, text="설정 저장", command=self.save_settings, style="Korean.TButton", width=button_width).grid(row=0, column=1, padx=8, pady=4)
        ttk.Button(button_frame, text="설정 불러오기", command=self.load_settings, style="Korean.TButton", width=button_width).grid(row=0, column=2, padx=8, pady=4)
        
        # 두 번째 줄: 복사 및 계산 관련
        ttk.Button(button_frame, text="캐릭터 1→2 복사", command=self.set_char1_to_char2, style="Korean.TButton", width=button_width).grid(row=1, column=0, padx=8, pady=4)
        ttk.Button(button_frame, text="캐릭터 2→1 복사", command=self.set_char2_to_char1, style="Korean.TButton", width=button_width).grid(row=1, column=1, padx=8, pady=4)
        ttk.Button(button_frame, text="데미지 비교", command=self.compare_damage, style="Korean.TButton", width=button_width).grid(row=1, column=2, padx=8, pady=4)

        # 결과 프레임
        result_frame = ttk.LabelFrame(main_frame, text="결과", padding="2", style="Korean.TLabelframe")
        result_frame.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 0), padx=(2, 2))
        self.result_text = tk.Text(result_frame, height=30, width=67, wrap=tk.WORD, font=self.text_font)
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 캐릭터 1 위젯 생성
        self.create_character_widgets(char1_frame, "char1")
        
        # 캐릭터 2 위젯 생성
        self.create_character_widgets(char2_frame, "char2")
        
        # 창이 내용에 맞게 자동으로 크기 조정되도록 설정
        self.root.update_idletasks()
        self.root.geometry("")  # 내용에 맞게 자동 조정
        
    def create_character_widgets(self, parent, char_prefix):
        # 캐릭터 이름
        ttk.Label(parent, text="캐릭터 이름:", font=self.text_font).grid(row=0, column=0, sticky=tk.W, padx=(2, 24))
        if char_prefix == "char1":
            setattr(self, f"{char_prefix}_name_var", tk.StringVar(value="캐릭터(전)"))
        else:
            setattr(self, f"{char_prefix}_name_var", tk.StringVar(value="캐릭터(후)"))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_name_var"), width=10, font=self.text_font, justify='right').grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        
        # 체크박스들
        setattr(self, f"{char_prefix}_awakening_var", tk.BooleanVar(value=Character.DEFAULT_AWAKENING))
        ttk.Checkbutton(parent, text="각성", variable=getattr(self, f"{char_prefix}_awakening_var"), style="Korean.TCheckbutton").grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(2, 24))
        
        setattr(self, f"{char_prefix}_cooldown_var", tk.BooleanVar(value=Character.DEFAULT_COOLDOWN))
        ttk.Checkbutton(parent, text="쿨타임 감소", variable=getattr(self, f"{char_prefix}_cooldown_var"), style="Korean.TCheckbutton").grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        
        # 공격 관련
        row = 2
        ttk.Label(parent, text="공격 속도 (회/분):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, padx=(2, 24))
        setattr(self, f"{char_prefix}_attacks_var", tk.StringVar(value=str(Character.DEFAULT_ATTACKS_PER_MINUTE)))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_attacks_var"), width=6, font=self.text_font, justify='right').grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        
        row += 1
        ttk.Label(parent, text="공격력 (M):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, padx=(2, 24))
        setattr(self, f"{char_prefix}_attack_power_var", tk.StringVar(value=str(Character.DEFAULT_ATTACK_POWER)))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_attack_power_var"), width=6, font=self.text_font, justify='right').grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        
        # 확률 관련
        row += 1
        ttk.Label(parent, text="치명 확률 (%):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, padx=(2, 24))
        setattr(self, f"{char_prefix}_critical_var", tk.StringVar(value=str(round(Character.DEFAULT_P_CRITICAL*100, 2))))
        critical_entry = ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_critical_var"), width=6, font=self.text_font, justify='right')
        critical_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        # 치명 확률 입력 제한 (100% 초과 시 100%로 제한)
        critical_entry.bind('<FocusOut>', lambda e, prefix=char_prefix: self.limit_probability(prefix, 'critical'))
        
        row += 1
        ttk.Label(parent, text="강타 확률 (%):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, padx=(2, 24))
        setattr(self, f"{char_prefix}_strong_hit_var", tk.StringVar(value=str(round(Character.DEFAULT_P_STRONG_HIT*100, 2))))
        strong_hit_entry = ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_strong_hit_var"), width=6, font=self.text_font, justify='right')
        strong_hit_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        strong_hit_entry.bind('<FocusOut>', lambda e, prefix=char_prefix: self.limit_probability(prefix, 'strong_hit'))
        
        row += 1
        ttk.Label(parent, text="더블샷 확률 (%):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, padx=(2, 24))
        setattr(self, f"{char_prefix}_double_shot_var", tk.StringVar(value=str(round(Character.DEFAULT_P_DOUBLE_SHOT*100, 2))))
        double_shot_entry = ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_double_shot_var"), width=6, font=self.text_font, justify='right')
        double_shot_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        double_shot_entry.bind('<FocusOut>', lambda e, prefix=char_prefix: self.limit_probability(prefix, 'double_shot'))
        
        row += 1
        ttk.Label(parent, text="트리플샷 확률 (%):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, padx=(2, 24))
        setattr(self, f"{char_prefix}_triple_shot_var", tk.StringVar(value=str(round(Character.DEFAULT_P_TRIPLE_SHOT*100, 2))))
        triple_shot_entry = ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_triple_shot_var"), width=6, font=self.text_font, justify='right')
        triple_shot_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        triple_shot_entry.bind('<FocusOut>', lambda e, prefix=char_prefix: self.limit_probability(prefix, 'triple_shot'))
        
        # 배율 관련
        row += 1
        ttk.Label(parent, text="치명 피해 (%):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, padx=(2, 24))
        setattr(self, f"{char_prefix}_critical_mult_var", tk.StringVar(value=str(round(Character.DEFAULT_CRITICAL_MULTIPLIER*100, 2))))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_critical_mult_var"), width=6, font=self.text_font, justify='right').grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        
        row += 1
        ttk.Label(parent, text="강타 피해 (%):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, padx=(2, 24))
        setattr(self, f"{char_prefix}_strong_hit_mult_var", tk.StringVar(value=str(round(Character.DEFAULT_STRONG_HIT_MULTIPLIER*100, 2))))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_strong_hit_mult_var"), width=6, font=self.text_font, justify='right').grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        

    def save_initial_values(self):
        self.initial_values = {
            'char1_name': self.char1_name_var.get(),
            'char1_awakening': self.char1_awakening_var.get(),
            'char1_cooldown': self.char1_cooldown_var.get(),
            'char1_attacks': self.char1_attacks_var.get(),
            'char1_attack_power': self.char1_attack_power_var.get(),
            'char1_critical': self.char1_critical_var.get(),
            'char1_strong_hit': self.char1_strong_hit_var.get(),
            'char1_double_shot': self.char1_double_shot_var.get(),
            'char1_triple_shot': self.char1_triple_shot_var.get(),
            'char1_critical_mult': self.char1_critical_mult_var.get(),
            'char1_strong_hit_mult': self.char1_strong_hit_mult_var.get(),
            'char2_name': self.char2_name_var.get(),
            'char2_awakening': self.char2_awakening_var.get(),
            'char2_cooldown': self.char2_cooldown_var.get(),
            'char2_attacks': self.char2_attacks_var.get(),
            'char2_attack_power': self.char2_attack_power_var.get(),
            'char2_critical': self.char2_critical_var.get(),
            'char2_strong_hit': self.char2_strong_hit_var.get(),
            'char2_double_shot': self.char2_double_shot_var.get(),
            'char2_triple_shot': self.char2_triple_shot_var.get(),
            'char2_critical_mult': self.char2_critical_mult_var.get(),
            'char2_strong_hit_mult': self.char2_strong_hit_mult_var.get(),
            'damage_1': self.damage_1_var.get(),
            'damage_2': self.damage_2_var.get(),
            'damage_3': self.damage_3_var.get(),
            'hit_1': self.hit_1_var.get(),
            'hit_2': self.hit_2_var.get(),
            'hit_3': self.hit_3_var.get(),
            'critical_cd': self.critical_cd_var.get(),
            'skill_cd': self.skill_cd_var.get(),
            'minutes': self.minutes_var.get() or "0.5",
            'simulations': self.simulations_var.get()
        }

    def set_default_values(self):
        """프로그램 시작 시점의 값으로 복원"""
        vals = getattr(self, 'initial_values', None)
        if vals is None:
            return
        self.char1_name_var.set(vals['char1_name'])
        self.char1_awakening_var.set(vals['char1_awakening'])
        self.char1_cooldown_var.set(vals['char1_cooldown'])
        self.char1_attacks_var.set(vals['char1_attacks'])
        self.char1_attack_power_var.set(vals['char1_attack_power'])
        self.char1_critical_var.set(vals['char1_critical'])
        self.char1_strong_hit_var.set(vals['char1_strong_hit'])
        self.char1_double_shot_var.set(vals['char1_double_shot'])
        self.char1_triple_shot_var.set(vals['char1_triple_shot'])
        self.char1_critical_mult_var.set(vals['char1_critical_mult'])
        self.char1_strong_hit_mult_var.set(vals['char1_strong_hit_mult'])
        self.char2_name_var.set(vals['char2_name'])
        self.char2_awakening_var.set(vals['char2_awakening'])
        self.char2_cooldown_var.set(vals['char2_cooldown'])
        self.char2_attacks_var.set(vals['char2_attacks'])
        self.char2_attack_power_var.set(vals['char2_attack_power'])
        self.char2_critical_var.set(vals['char2_critical'])
        self.char2_strong_hit_var.set(vals['char2_strong_hit'])
        self.char2_double_shot_var.set(vals['char2_double_shot'])
        self.char2_triple_shot_var.set(vals['char2_triple_shot'])
        self.char2_critical_mult_var.set(vals['char2_critical_mult'])
        self.char2_strong_hit_mult_var.set(vals['char2_strong_hit_mult'])
        self.damage_1_var.set(vals['damage_1'])
        self.damage_2_var.set(vals['damage_2'])
        self.damage_3_var.set(vals['damage_3'])
        self.hit_1_var.set(vals['hit_1'])
        self.hit_2_var.set(vals['hit_2'])
        self.hit_3_var.set(vals['hit_3'])
        self.critical_cd_var.set(vals['critical_cd'])
        self.skill_cd_var.set(vals['skill_cd'])
        self.minutes_var.set(vals['minutes'])
        self.simulations_var.set(vals['simulations'])

    def copy_character_stats(self, from_prefix, to_prefix):
        """캐릭터 간 스탯 복사 (이름 제외)"""
        # 복사할 속성 목록
        attributes = [
            'awakening', 'cooldown', 'attacks', 'attack_power',
            'critical', 'strong_hit', 'double_shot', 'triple_shot',
            'critical_mult', 'strong_hit_mult'
        ]
        
        for attr in attributes:
            from_var = getattr(self, f"{from_prefix}_{attr}_var")
            to_var = getattr(self, f"{to_prefix}_{attr}_var")
            to_var.set(from_var.get())
    
    def set_char2_to_char1(self):
        """캐릭터 2의 정보를 캐릭터 1로 복사 (이름 제외)"""
        self.copy_character_stats("char2", "char1")
        
    def set_char1_to_char2(self):
        """캐릭터 1의 정보를 캐릭터 2로 복사 (이름 제외)"""
        self.copy_character_stats("char1", "char2")
    
    def create_character_from_gui(self, char_prefix):
        """GUI 입력값으로부터 Character 객체 생성"""
        try:
            char = Character(getattr(self, f"{char_prefix}_name_var").get())
            
            # 기본 설정
            char.is_awakening = getattr(self, f"{char_prefix}_awakening_var").get()
            char.is_cooldown = getattr(self, f"{char_prefix}_cooldown_var").get()
            
            # 공격 관련 - 입력 검증
            attacks_value = getattr(self, f"{char_prefix}_attacks_var").get()
            if not self.validate_integer_input(attacks_value, 1, "공격 속도"):
                return None
            char.attacks_per_minute = int(float(attacks_value))
            
            attack_power_value = getattr(self, f"{char_prefix}_attack_power_var").get()
            if not self.validate_numeric_input(attack_power_value, 0, field_name="공격력"):
                return None
            char.attack_power = float(attack_power_value)
            
            # 확률 관련 (100% 초과 시 100%로 제한)
            char.p_critical = min(float(getattr(self, f"{char_prefix}_critical_var").get()) / 100, 1.0)
            char.p_strong_hit = min(float(getattr(self, f"{char_prefix}_strong_hit_var").get()) / 100, 1.0)
            char.p_double_shot = min(float(getattr(self, f"{char_prefix}_double_shot_var").get()) / 100, 1.0)
            char.p_triple_shot = min(float(getattr(self, f"{char_prefix}_triple_shot_var").get()) / 100, 1.0)
            
            # 배율 관련 - 입력 검증
            critical_mult_value = getattr(self, f"{char_prefix}_critical_mult_var").get()
            if not self.validate_numeric_input(critical_mult_value, 0, field_name="치명 피해"):
                return None
            char.critical_multiplier = float(critical_mult_value) / 100
            
            strong_hit_mult_value = getattr(self, f"{char_prefix}_strong_hit_mult_var").get()
            if not self.validate_numeric_input(strong_hit_mult_value, 0, field_name="강타 피해"):
                return None
            char.strong_hit_multiplier = float(strong_hit_mult_value) / 100
            
            char.awakening_multiplier = AWAKENING_MULTIPLIER if char.is_awakening else 1
            
            # 데미지 배율 (공통 설정 사용)
            char.damage_skill_1 = float(self.damage_1_var.get()) / 100
            char.damage_skill_2 = float(self.damage_2_var.get()) / 100
            char.damage_skill_3 = float(self.damage_3_var.get()) / 100
            
            # 쿨타임 설정 (공통 설정 사용)
            char.critical_cooldown = float(self.critical_cd_var.get())
            char.skill_cooldown = float(self.skill_cd_var.get())
            
            # 쿨타임 감소 적용
            if char.is_cooldown:
                char.critical_cooldown *= COOLDOWN_REDUCTION_MULTIPLIER
                char.skill_cooldown *= COOLDOWN_REDUCTION_MULTIPLIER
            
            # 타수(공통설정) 적용
            char.hit_1 = int(self.hit_1_var.get())
            char.hit_2 = int(self.hit_2_var.get())
            char.hit_3 = int(self.hit_3_var.get())
            
            return char
            
        except (ValueError, AttributeError) as e:
            messagebox.showerror("입력 오류", f"캐릭터 생성 중 오류가 발생했습니다: {str(e)}")
            return None
    
    def compare_damage(self):
        """데미지 비교 실행"""
        # 입력값 검증
        if not self.validate_numeric_input(self.minutes_var.get(), 0.1, field_name="시뮬레이션 시간"):
            return
        if not self.validate_integer_input(self.simulations_var.get(), 1, "시뮬레이션 횟수"):
            return
        
        # 공통 설정 검증
        if not self.validate_numeric_input(self.damage_1_var.get(), 0, field_name="일반 공격 배율"):
            return
        if not self.validate_numeric_input(self.damage_2_var.get(), 0, field_name="치명타 공격 배율"):
            return
        if not self.validate_numeric_input(self.damage_3_var.get(), 0, field_name="전용 스킬 배율"):
            return
        if not self.validate_integer_input(self.hit_1_var.get(), 1, "일반 공격 타수"):
            return
        if not self.validate_integer_input(self.hit_2_var.get(), 1, "치명타 공격 타수"):
            return
        if not self.validate_integer_input(self.hit_3_var.get(), 1, "전용 스킬 타수"):
            return
        if not self.validate_numeric_input(self.critical_cd_var.get(), 0, field_name="치명타 쿨타임"):
            return
        if not self.validate_numeric_input(self.skill_cd_var.get(), 0, field_name="스킬 쿨타임"):
            return
        
        # 캐릭터 생성
        char1 = self.create_character_from_gui("char1")
        char2 = self.create_character_from_gui("char2")
        
        if char1 is None or char2 is None:
            return
        
        # 결과 텍스트 초기화
        self.result_text.delete(1.0, tk.END)
        
        # 별도 스레드에서 계산 실행 (GUI 블록 방지)
        def run_calculation():
            try:
                minutes = float(self.minutes_var.get())
                simulations = int(self.simulations_var.get())
                # GUI에서 직접 출력
                self.root.after(0, lambda: compare_characters(char1, char2, minutes, simulations, self.result_text))
                
            except Exception as e:
                error_msg = f"계산 중 오류가 발생했습니다: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("계산 오류", error_msg))
        
        # 스레드 시작
        thread = threading.Thread(target=run_calculation)
        thread.daemon = True
        thread.start()


def main():
    root = tk.Tk()
    app = CharacterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main() 