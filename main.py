import tkinter as tk
from tkinter import ttk, messagebox
import threading
import random
import sys
import locale
import tkinter.font
import json
import os

# 상수
COOLDOWN_REDUCTION_MULTIPLIER = 0.8
SEVENTH_AWAKENING_MULTIPLIER = 1.2
INSIGNIFICANT_DPM_DIFFERENCE_RATE_THRESHOLD = 0.2
INSIGNIFICANT_APM_DIFFERENCE_THRESHOLD = 1
SETTINGS_FILE = "settings.json"
PASTEL_BG = "#f9f6f2"

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
    DEFAULT_ATTACK_SPEED = 130
    DEFAULT_ATTACK_POWER = 12.32
    DEFAULT_P_CRITICAL = 90.35 / 100
    DEFAULT_P_STRONG_HIT = 58.12 / 100
    DEFAULT_P_DOUBLE_SHOT = 26.08 / 100
    DEFAULT_P_TRIPLE_SHOT = 11.23 / 100
    DEFAULT_CRITICAL_MULTIPLIER = 1171.71 / 100
    DEFAULT_STRONG_HIT_MULTIPLIER = 185.45 / 100
    DEFAULT_SEVENTH_AWAKENING = True
    DEFAULT_COOLDOWN = True
    DEFAULT_AMPLIFICATION = True
    DEFAULT_THIRD_AWAKENING = False
    DEFAULT_DAMAGE_SKILL_1 = 430 / 100
    DEFAULT_DAMAGE_SKILL_2 = 190 / 100
    DEFAULT_DAMAGE_SKILL_3 = 280 / 100
    DEFAULT_CRITICAL_COOLDOWN = 2
    DEFAULT_SKILL_COOLDOWN = 10
    DEFAULT_HIT_1 = 1
    DEFAULT_HIT_2 = 3
    DEFAULT_HIT_3 = 3
    AMPLIFICATION_BONUS = 0.6

    def __init__(self, name="Character"):
        self.name = name
        self.is_seventh_awakening = Character.DEFAULT_SEVENTH_AWAKENING
        self.is_cooldown = Character.DEFAULT_COOLDOWN
        self.is_amplification = Character.DEFAULT_AMPLIFICATION
        self.is_third_awakening = Character.DEFAULT_THIRD_AWAKENING
        self.attack_speed = Character.DEFAULT_ATTACK_SPEED
        self.attack_power = Character.DEFAULT_ATTACK_POWER
        self.p_critical = Character.DEFAULT_P_CRITICAL
        self.p_strong_hit = Character.DEFAULT_P_STRONG_HIT
        self.p_double_shot = Character.DEFAULT_P_DOUBLE_SHOT
        self.p_triple_shot = Character.DEFAULT_P_TRIPLE_SHOT
        self.critical_multiplier = Character.DEFAULT_CRITICAL_MULTIPLIER
        self.strong_hit_multiplier = Character.DEFAULT_STRONG_HIT_MULTIPLIER
        self.seventh_awakening_multiplier = SEVENTH_AWAKENING_MULTIPLIER if self.is_seventh_awakening else 1
        self.damage_skill_1 = Character.DEFAULT_DAMAGE_SKILL_1
        self.damage_skill_2 = Character.DEFAULT_DAMAGE_SKILL_2
        self.damage_skill_3 = Character.DEFAULT_DAMAGE_SKILL_3
        self.critical_cooldown = Character.DEFAULT_CRITICAL_COOLDOWN
        self.skill_cooldown = Character.DEFAULT_SKILL_COOLDOWN
        self.hit_1 = Character.DEFAULT_HIT_1
        self.hit_2 = Character.DEFAULT_HIT_2
        self.hit_3 = Character.DEFAULT_HIT_3
        if self.is_cooldown:
            self.critical_cooldown *= COOLDOWN_REDUCTION_MULTIPLIER
            self.skill_cooldown *= COOLDOWN_REDUCTION_MULTIPLIER

    def simulate_damage(self, minutes=0.5, simulations=10000, progress_callback=None):
        """캐릭터의 데미지를 시뮬레이션하여 분당 데미지(DPM)를 계산"""
        return simulate_attacks_with_critical_and_skill(
            minutes=minutes,
            simulations=simulations,
            attack_power=self.attack_power,
            attack_speed=self.attack_speed,
            damage_skill_1=self.damage_skill_1,
            damage_skill_2=self.damage_skill_2,
            damage_skill_3=self.damage_skill_3,
            p_critical=self.p_critical,
            p_strong_hit=self.p_strong_hit,
            p_double_shot=self.p_double_shot,
            p_triple_shot=self.p_triple_shot,
            critical_multiplier=self.critical_multiplier,
            strong_hit_multiplier=self.strong_hit_multiplier,
            seventh_awakening_multiplier=self.seventh_awakening_multiplier,
            critical_cooldown=self.critical_cooldown,
            skill_cooldown=self.skill_cooldown,
            hit_1=self.hit_1,
            hit_2=self.hit_2,
            hit_3=self.hit_3,
            progress_callback=progress_callback,
            third_awakening=self.is_third_awakening
        )


def simulate_attacks_with_critical_and_skill(
    minutes=1, 
    simulations=1000,
    attack_power=1,
    attack_speed=120,
    damage_skill_1=1, 
    damage_skill_2=2, 
    damage_skill_3=5, 
    p_critical=0.5, 
    p_strong_hit=0.1, 
    p_double_shot=0.1, 
    p_triple_shot=0.05,
    critical_multiplier=2, 
    strong_hit_multiplier=2, 
    seventh_awakening_multiplier=1,
    critical_cooldown=2, 
    skill_cooldown=10, 
    hit_1=1, 
    hit_2=1, 
    hit_3=1,
    progress_callback=None,
    third_awakening=False
):
    attack_speed = int(attack_speed)
    total_damage = 0
    total_attacks = 0
    
    # 소수점 시간을 처리하기 위해 초 단위로 변환
    total_seconds = minutes * 60
    # 공격속도 100당 1초에 1번 공격 (즉, 공격속도 100이면 1초에 1번, 200이면 1초에 2번)
    # 따라서 interval = 100 / attack_speed (초)
    attack_interval = 100 / attack_speed
    
    for _ in range(simulations):
        current_time = 0
        damage_this_simulation = 0
        time_since_last_critical = critical_cooldown if third_awakening else 0  
        time_since_last_skill = skill_cooldown if third_awakening else 0
        
        # 진행률 업데이트 (1000번마다)
        if progress_callback and (_ + 1) % 1000 == 0:
            progress = (_ + 1) / simulations * 100
            progress_callback(progress)
        
        while current_time < total_seconds:
            
            # 1. 스킬 (3각이 활성화되면 쿨타임 무시하고 바로 발동)
            if time_since_last_skill >= skill_cooldown:  # 스킬 쿨타임 체크
                base_damage = damage_skill_3 * attack_power * seventh_awakening_multiplier
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
            elif time_since_last_critical >= critical_cooldown and random.random() < p_critical:  # 치명타 쿨타임 체크 & 치명타 확률 체크
                base_damage = damage_skill_2 * attack_power * critical_multiplier * seventh_awakening_multiplier
                for _ in range(hit_2):
                    damage_tick = base_damage
                    if random.random() < p_strong_hit:
                        damage_tick *= strong_hit_multiplier
                    damage_this_simulation += damage_tick
                total_attacks += hit_2
                time_since_last_critical = 0

            # 3. 일반 공격
            else:
                base_damage = damage_skill_1 * attack_power * seventh_awakening_multiplier
                # 더블샷/트리플샷 확률 계산
                shot_count = 1
                if random.random() < p_double_shot:
                    shot_count = 2
                if random.random() < p_triple_shot:
                    shot_count = 3

                # 데미지 계산
                for _ in range(shot_count):
                    for _ in range(hit_1):
                        damage_tick = base_damage
                        if random.random() < p_critical and shot_count > 1: # 더블샷/트리플 샷 일 때 치명타 발생
                            damage_tick *= critical_multiplier
                        if random.random() < p_strong_hit: # 강타 발생
                            damage_tick *= strong_hit_multiplier
                        damage_this_simulation += damage_tick
                total_attacks += shot_count * hit_1

            # 시간 증가
            current_time += attack_interval
            time_since_last_critical += attack_interval
            time_since_last_skill += attack_interval

        total_damage += damage_this_simulation
    
    # 분당 데미지(DPM)와 분당 공격 횟수(APM) 반환
    return total_damage / (simulations * minutes), total_attacks / (simulations * minutes)


def create_clean_output_display(parent, char1, char2, damage1, apm1, damage2, apm2):
    """완전히 깔끔한 Treeview 기반 출력 방식 (결과 프레임 내부도 연베이지톤 통일)"""
    for widget in parent.winfo_children():
        widget.destroy()
    
    # 메인 스크롤 프레임
    main_canvas = tk.Canvas(parent, bg=PASTEL_BG, highlightthickness=0, height=700)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=main_canvas.yview, bg=PASTEL_BG)
    scrollable_frame = tk.Frame(main_canvas, bg=PASTEL_BG)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    )
    
    main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    main_canvas.configure(yscrollcommand=scrollbar.set)
    
    # 마우스 휠 스크롤 바인딩 (Windows 기준) - 더 자연스러운 방식
    def _on_mousewheel(event):
        main_canvas.yview_scroll(-1 * int(event.delta / 120), "units")
    
    # 결과창 전체에 마우스 휠 바인딩 적용
    def bind_mousewheel_to_widget(widget):
        widget.bind("<MouseWheel>", _on_mousewheel)
        # 라벨 위젯의 경우 focus를 받을 수 있도록 설정
        if isinstance(widget, tk.Label):
            widget.configure(takefocus=1)
    
    # 메인 Canvas와 scrollable_frame에 직접 바인딩
    bind_mousewheel_to_widget(main_canvas)
    bind_mousewheel_to_widget(scrollable_frame)
    
    # 제목
    title_label = tk.Label(scrollable_frame, text="캐릭터 데미지 비교 결과", font=("Arial", 16, "bold"), bg=PASTEL_BG, takefocus=1)
    title_label.pack(pady=(10, 20))
    bind_mousewheel_to_widget(title_label)
    
    # 캐릭터 1 정보
    char1_title_frame = tk.Frame(scrollable_frame, bg=PASTEL_BG)
    char1_title_frame.pack(fill='x', pady=(10, 5))
    char1_title_label = tk.Label(char1_title_frame, text=f"📊 {char1.name} 스탯", font=("Arial", 14, "bold"), bg=PASTEL_BG, takefocus=1)
    char1_title_label.pack(anchor='center')
    bind_mousewheel_to_widget(char1_title_frame)
    bind_mousewheel_to_widget(char1_title_label)
    
    char1_frame = tk.Frame(scrollable_frame, bg=PASTEL_BG)
    char1_frame.pack(fill='x', padx=10, pady=5)
    bind_mousewheel_to_widget(char1_frame)
    
    # 캐릭터 1 기본 정보
    char1_info = [
        ["3각 상태", "활성화" if char1.is_third_awakening else "비활성화"],
        ["7각 상태", "활성화" if char1.is_seventh_awakening else "비활성화"],
        ["증폭 상태", "활성화" if char1.is_amplification else "비활성화"]
    ]
    char1_info_table = create_table_frame(char1_frame, ["항목", "상태"], char1_info, "", height=3, main_canvas=main_canvas)
    char1_info_table.pack(fill='x', pady=(0, 10))
    
    # 캐릭터 1 기본 스탯
    char1_basic_stats = [
        ["공격 속도", f"{char1.attack_speed} ({60 * char1.attack_speed / 100:.1f}회/분)"],
        ["공격력", f"{char1.attack_power}M"],
        ["치명 확률", f"{char1.p_critical * 100:.2f}%"],
        ["강타 확률", f"{char1.p_strong_hit * 100:.2f}%"],
        ["더블샷 확률", f"{char1.p_double_shot * 100:.2f}%"],
        ["트리플샷 확률", f"{char1.p_triple_shot * 100:.2f}%"],
        ["치명 피해", f"{char1.critical_multiplier * 100:.2f}%"],
        ["강타 피해", f"{char1.strong_hit_multiplier * 100:.2f}%"],
        ["각성 배율", f"{char1.seventh_awakening_multiplier:.2f}"]
    ]
    char1_basic_table = create_table_frame(char1_frame, ["항목", "값"], char1_basic_stats, "기본 스탯", height=9, main_canvas=main_canvas)
    char1_basic_table.pack(fill='x', pady=(0, 10))
    
    # 캐릭터 1 스킬 배율
    char1_skill_stats = []
    base_damage_1 = char1.damage_skill_1
    if char1.is_amplification:
        base_damage_1 -= Character.AMPLIFICATION_BONUS
        char1_skill_stats.append(["일반 공격", f"{base_damage_1:.2f} + {Character.AMPLIFICATION_BONUS:.2f} (증폭)", f"{char1.damage_skill_1:.2f}", f"{char1.hit_1}", f"{char1.damage_skill_1 * char1.hit_1:.2f}"])
    else:
        char1_skill_stats.append(["일반 공격", f"{char1.damage_skill_1:.2f}", "-", f"{char1.hit_1}", f"{char1.damage_skill_1 * char1.hit_1:.2f}"])
    
    base_damage_2 = char1.damage_skill_2
    if char1.is_amplification:
        base_damage_2 -= Character.AMPLIFICATION_BONUS
        char1_skill_stats.append(["치명타 공격", f"{base_damage_2:.2f} + {Character.AMPLIFICATION_BONUS:.2f} (증폭)", f"{char1.damage_skill_2:.2f}", f"{char1.hit_2}", f"{char1.damage_skill_2 * char1.hit_2:.2f}"])
    else:
        char1_skill_stats.append(["치명타 공격", f"{char1.damage_skill_2:.2f}", "-", f"{char1.hit_2}", f"{char1.damage_skill_2 * char1.hit_2:.2f}"])
    
    base_damage_3 = char1.damage_skill_3
    if char1.is_amplification:
        base_damage_3 -= Character.AMPLIFICATION_BONUS
        char1_skill_stats.append(["전용 스킬", f"{base_damage_3:.2f} + {Character.AMPLIFICATION_BONUS:.2f} (증폭)", f"{char1.damage_skill_3:.2f}", f"{char1.hit_3}", f"{char1.damage_skill_3 * char1.hit_3:.2f}"])
    else:
        char1_skill_stats.append(["전용 스킬", f"{char1.damage_skill_3:.2f}", "-", f"{char1.hit_3}", f"{char1.damage_skill_3 * char1.hit_3:.2f}"])
    
    char1_skill_table = create_table_frame(char1_frame, ["스킬", "기본 배율", "증폭 보너스", "타수", "총합"], char1_skill_stats, "스킬 배율", height=3, is_amplification=char1.is_amplification, main_canvas=main_canvas)
    char1_skill_table.pack(fill='x', pady=(0, 10))
    
    # 캐릭터 1 쿨타임
    char1_cooldown_stats = [
        ["치명타 쿨타임", f"{char1.critical_cooldown:.1f}초"],
        ["스킬 쿨타임", f"{char1.skill_cooldown:.1f}초"]
    ]
    char1_cooldown_table = create_table_frame(char1_frame, ["항목", "값"], char1_cooldown_stats, "쿨타임", height=2, main_canvas=main_canvas)
    char1_cooldown_table.pack(fill='x')
    
    # 구분선
    separator1 = tk.Frame(scrollable_frame, height=2, bg="#e0d8c3")
    separator1.pack(fill='x', padx=20, pady=15)
    bind_mousewheel_to_widget(separator1)
    
    # 캐릭터 2 정보 (비교 표시 포함)
    char2_title_frame = tk.Frame(scrollable_frame, bg=PASTEL_BG)
    char2_title_frame.pack(fill='x', pady=(10, 5))
    char2_title_label = tk.Label(char2_title_frame, text=f"📊 {char2.name} 스탯", font=("Arial", 14, "bold"), bg=PASTEL_BG, takefocus=1)
    char2_title_label.pack(anchor='center')
    bind_mousewheel_to_widget(char2_title_frame)
    bind_mousewheel_to_widget(char2_title_label)
    
    char2_frame = tk.Frame(scrollable_frame, bg=PASTEL_BG)
    char2_frame.pack(fill='x', padx=10, pady=5)
    bind_mousewheel_to_widget(char2_frame)
    
    # 캐릭터 2 기본 정보 (비교)
    char2_info = []
    
    # 3각 상태 비교
    if char2.is_third_awakening:
        if char1.is_third_awakening:
            char2_info.append(["3각 상태", "활성화"])
        else:
            char2_info.append(["3각 상태", "활성화 ▲"])
    else:
        if char1.is_third_awakening:
            char2_info.append(["3각 상태", "비활성화 ▼"])
        else:
            char2_info.append(["3각 상태", "비활성화"])
    
    # 7각 상태 비교
    if char2.is_seventh_awakening:
        if char1.is_seventh_awakening:
            char2_info.append(["7각 상태", "활성화"])
        else:
            char2_info.append(["7각 상태", "활성화 ▲"])
    else:
        if char1.is_seventh_awakening:
            char2_info.append(["7각 상태", "비활성화 ▼"])
        else:
            char2_info.append(["7각 상태", "비활성화"])
    
    # 증폭 상태에 따른 색상 표시
    if char2.is_amplification:
        if char1.is_amplification:
            char2_info.append(["증폭 상태", "활성화"])
        else:
            char2_info.append(["증폭 상태", "활성화 ▲"])
    else:
        if char1.is_amplification:
            char2_info.append(["증폭 상태", "비활성화 ▼"])
        else:
            char2_info.append(["증폭 상태", "비활성화"])
    
    char2_info_table = create_table_frame(char2_frame, ["항목", "상태"], char2_info, "", height=3, main_canvas=main_canvas)
    char2_info_table.pack(fill='x', pady=(0, 10))
    
    # 캐릭터 2 기본 스탯 (비교)
    char2_basic_stats = [
        ["공격 속도", f"{char2.attack_speed} ({60 * char2.attack_speed / 100:.1f}회/분)"],
        ["공격력", f"{char2.attack_power}M"],
        ["치명 확률", f"{char2.p_critical * 100:.2f}%"],
        ["강타 확률", f"{char2.p_strong_hit * 100:.2f}%"],
        ["더블샷 확률", f"{char2.p_double_shot * 100:.2f}%"],
        ["트리플샷 확률", f"{char2.p_triple_shot * 100:.2f}%"],
        ["치명 피해", f"{char2.critical_multiplier * 100:.2f}%"],
        ["강타 피해", f"{char2.strong_hit_multiplier * 100:.2f}%"],
        ["각성 배율", f"{char2.seventh_awakening_multiplier:.2f}"]
    ]
    
    # 비교 표시 추가
    compare_values = [
        char1.attack_speed, char1.attack_power, char1.p_critical * 100,
        char1.p_strong_hit * 100, char1.p_double_shot * 100, char1.p_triple_shot * 100,
        char1.critical_multiplier * 100, char1.strong_hit_multiplier * 100, char1.seventh_awakening_multiplier
    ]
    
    for i, (label, value) in enumerate(char2_basic_stats):
        compare_val = compare_values[i]
        # 공격 속도 값에서 숫자만 추출 (괄호 안의 회/분 값은 제외)
        if '회/분' in value:
            # "129 (46.5회/분)" 형태에서 129만 추출
            current_val = float(value.split(' ')[0])
        else:
            current_val = float(value.replace('회/분', '').replace('M', '').replace('%', '').replace('x', ''))
        
        # 값이 실제로 다른 경우에만 증감 표시
        if abs(current_val - compare_val) > 0.01:  # 0.01 이상 차이나는 경우만
            if current_val > compare_val:
                char2_basic_stats[i][1] = value + " ▲"
            elif current_val < compare_val:
                char2_basic_stats[i][1] = value + " ▼"
    
    char2_basic_table = create_table_frame(char2_frame, ["항목", "값"], char2_basic_stats, "기본 스탯", height=9, main_canvas=main_canvas)
    char2_basic_table.pack(fill='x', pady=(0, 10))
    
    # 캐릭터 2 스킬 배율
    char2_skill_stats = []
    base_damage_1 = char2.damage_skill_1
    if char2.is_amplification:
        base_damage_1 -= Character.AMPLIFICATION_BONUS
        char2_skill_stats.append(["일반 공격", f"{base_damage_1:.2f} + {Character.AMPLIFICATION_BONUS:.2f} (증폭)", f"{char2.damage_skill_1:.2f}", f"{char2.hit_1}", f"{char2.damage_skill_1 * char2.hit_1:.2f}"])
    else:
        char2_skill_stats.append(["일반 공격", f"{char2.damage_skill_1:.2f}", "-", f"{char2.hit_1}", f"{char2.damage_skill_1 * char2.hit_1:.2f}"])
    
    base_damage_2 = char2.damage_skill_2
    if char2.is_amplification:
        base_damage_2 -= Character.AMPLIFICATION_BONUS
        char2_skill_stats.append(["치명타 공격", f"{base_damage_2:.2f} + {Character.AMPLIFICATION_BONUS:.2f} (증폭)", f"{char2.damage_skill_2:.2f}", f"{char2.hit_2}", f"{char2.damage_skill_2 * char2.hit_2:.2f}"])
    else:
        char2_skill_stats.append(["치명타 공격", f"{char2.damage_skill_2:.2f}", "-", f"{char2.hit_2}", f"{char2.damage_skill_2 * char2.hit_2:.2f}"])
    
    base_damage_3 = char2.damage_skill_3
    if char2.is_amplification:
        base_damage_3 -= Character.AMPLIFICATION_BONUS
        char2_skill_stats.append(["전용 스킬", f"{base_damage_3:.2f} + {Character.AMPLIFICATION_BONUS:.2f} (증폭)", f"{char2.damage_skill_3:.2f}", f"{char2.hit_3}", f"{char2.damage_skill_3 * char2.hit_3:.2f}"])
    else:
        char2_skill_stats.append(["전용 스킬", f"{char2.damage_skill_3:.2f}", "-", f"{char2.hit_3}", f"{char2.damage_skill_3 * char2.hit_3:.2f}"])
    
    char2_skill_table = create_table_frame(char2_frame, ["스킬", "기본 배율", "증폭 보너스", "타수", "총합"], char2_skill_stats, "스킬 배율", height=3, is_amplification=char2.is_amplification, main_canvas=main_canvas)
    char2_skill_table.pack(fill='x', pady=(0, 10))
    
    # 캐릭터 2 쿨타임 (비교)
    char2_cooldown_stats = [
        ["치명타 쿨타임", f"{char2.critical_cooldown:.1f}초"],
        ["스킬 쿨타임", f"{char2.skill_cooldown:.1f}초"]
    ]
    
    if abs(char2.critical_cooldown - char1.critical_cooldown) > 0.01:
        if char2.critical_cooldown < char1.critical_cooldown:
            char2_cooldown_stats[0][1] += " ▲"
        elif char2.critical_cooldown > char1.critical_cooldown:
            char2_cooldown_stats[0][1] += " ▼"
        
    if abs(char2.skill_cooldown - char1.skill_cooldown) > 0.01:
        if char2.skill_cooldown < char1.skill_cooldown:
            char2_cooldown_stats[1][1] += " ▲"
        elif char2.skill_cooldown > char1.skill_cooldown:
            char2_cooldown_stats[1][1] += " ▼"
    
    char2_cooldown_table = create_table_frame(char2_frame, ["항목", "값"], char2_cooldown_stats, "쿨타임", height=2, main_canvas=main_canvas)
    char2_cooldown_table.pack(fill='x')
    
    # 구분선
    separator2 = tk.Frame(scrollable_frame, height=2, bg="#e0d8c3")
    separator2.pack(fill='x', padx=20, pady=15)
    bind_mousewheel_to_widget(separator2)
    
    # 결과 비교
    result_title_frame = tk.Frame(scrollable_frame, bg=PASTEL_BG)
    result_title_frame.pack(fill='x', pady=(10, 5))
    result_title_label = tk.Label(result_title_frame, text="⚔️ 데미지 비교 결과", font=("Arial", 14, "bold"), bg=PASTEL_BG, takefocus=1)
    result_title_label.pack(anchor='center')
    bind_mousewheel_to_widget(result_title_frame)
    bind_mousewheel_to_widget(result_title_label)
    
    result_frame = tk.Frame(scrollable_frame, bg=PASTEL_BG)
    result_frame.pack(fill='x', padx=10, pady=5)
    bind_mousewheel_to_widget(result_frame)
    
    result_stats = [
        [char1.name, f"{damage1:,.2f}", f"{apm1:.1f}"],
        [char2.name, f"{damage2:,.2f}", f"{apm2:.1f}"]
    ]
    result_table = create_table_frame(result_frame, ["캐릭터", "DPM", "APM"], result_stats, "", height=2, main_canvas=main_canvas)
    result_table.pack(fill='x', pady=(0, 10))
    
    # 결과 분석
    if damage1 > damage2:
        diff = damage1 - damage2
        percentage = (diff / damage2) * 100
        if percentage <= INSIGNIFICANT_DPM_DIFFERENCE_RATE_THRESHOLD:
            result_text = f"{char2.name}이 {char1.name}보다 {diff:,.2f} DPM 낮음 ({percentage:.2f}% 차이, 의미 없음) ▼"
            result_color = "gray"
        else:
            result_text = f"{char2.name}이 {char1.name}보다 {diff:,.2f} DPM 낮음 ({percentage:.2f}% 약함) ▼"
            result_color = "red"
    elif damage2 > damage1:
        diff = damage2 - damage1
        percentage = (diff / damage1) * 100
        if percentage <= INSIGNIFICANT_DPM_DIFFERENCE_RATE_THRESHOLD:
            result_text = f"{char2.name}가 {char1.name}보다 {diff:,.2f} DPM 높음 ({percentage:.2f}% 차이, 의미 없음) ▲"
            result_color = "gray"
        else:
            result_text = f"{char2.name}가 {char1.name}보다 {diff:,.2f} DPM 높음 ({percentage:.2f}% 강함) ▲"
            result_color = "blue"
    else:
        result_text = "두 캐릭터의 데미지가 동일합니다."
        result_color = "black"
    
    result_label = tk.Label(result_frame, text=result_text, font=("Arial", 10, "bold"), bg=PASTEL_BG, fg=result_color, takefocus=1)
    result_label.pack(pady=5)
    bind_mousewheel_to_widget(result_label)
    
    # APM 비교
    apm_diff = apm1 - apm2
    if apm_diff > INSIGNIFICANT_APM_DIFFERENCE_THRESHOLD:
        apm_text = f"{char2.name}가 {char1.name}보다 {abs(apm_diff):.1f} APM 느림 ▼"
        apm_color = "red"
    elif apm_diff < -INSIGNIFICANT_APM_DIFFERENCE_THRESHOLD:
        apm_text = f"{char2.name}가 {char1.name}보다 {abs(apm_diff):.1f} APM 빠름 ▲"
        apm_color = "blue"
    else:
        apm_text = f"APM 차이: {apm_diff:+.1f} ({apm1:.1f} vs {apm2:.1f}) (의미 없음)"
        apm_color = "gray"
    
    apm_label = tk.Label(result_frame, text=apm_text, font=("Arial", 10), bg=PASTEL_BG, fg=apm_color, takefocus=1)
    apm_label.pack(pady=5)
    bind_mousewheel_to_widget(apm_label)
    
    # 스크롤바 배치
    main_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    return main_canvas


def compare_characters(char1, char2, minutes=0.5, simulations=10000, text_widget=None):
    """캐릭터 데미지 비교 - 새로운 깔끔한 출력 방식 사용"""
    print(f"시뮬레이션 시작: {minutes}분, {simulations}회")
    
    # 시뮬레이션 실행
    damage1, apm1 = char1.simulate_damage(minutes, simulations)
    damage2, apm2 = char2.simulate_damage(minutes, simulations)
    
    print(f"시뮬레이션 완료!")
    print(f"{char1.name}: {damage1:,.2f} DPM, {apm1:.1f} APM")
    print(f"{char2.name}: {damage2:,.2f} DPM, {apm2:.1f} APM")
    
    # GUI 업데이트 (새로운 깔끔한 방식 사용)
    if text_widget:
        # text_widget의 부모 위젯을 찾아서 새로운 출력 방식 적용
        parent_widget = text_widget.master
        while parent_widget and not hasattr(parent_widget, 'winfo_children'):
            parent_widget = parent_widget.master
        
        if parent_widget:
            # 기존 텍스트 위젯 숨기기
            text_widget.pack_forget()
            
            # 새로운 깔끔한 출력 생성
            create_clean_output_display(parent_widget, char1, char2, damage1, apm1, damage2, apm2)
    
    # 콘솔 출력
    print("\n" + "="*50)
    print("캐릭터 데미지 비교 결과")
    print("="*50)
    
    # 결과 테이블 출력
    result_data = [
        [char1.name, f"{damage1:,.2f}", f"{apm1:.1f}"],
        [char2.name, f"{damage2:,.2f}", f"{apm2:.1f}"]
    ]
    
    print("\n데미지 비교:")
    print("┌" + "─" * 40 + "┐")
    print("│" + "캐릭터".center(15) + "│" + "DPM".center(15) + "│" + "APM".center(10) + "│")
    print("├" + "─" * 40 + "┤")
    for char_name, dpm, apm in result_data:
        print(f"│{char_name:^15}│{dpm:^15}│{apm:^10}│")
    print("└" + "─" * 40 + "┘")
    
    # 결과 분석
    if damage1 > damage2:
        diff = damage1 - damage2
        percentage = (diff / damage2) * 100
        if percentage <= INSIGNIFICANT_DPM_DIFFERENCE_RATE_THRESHOLD:
            print(f"\n{char2.name}이 {char1.name}보다 {diff:,.2f} DPM 낮음 ({percentage:.2f}% 차이, 의미 없음)")
        else:
            print(f"\n{char2.name}이 {char1.name}보다 {diff:,.2f} DPM 낮음 ({percentage:.2f}% 약함)")
    elif damage2 > damage1:
        diff = damage2 - damage1
        percentage = (diff / damage1) * 100
        if percentage <= INSIGNIFICANT_DPM_DIFFERENCE_RATE_THRESHOLD:
            print(f"\n{char2.name}가 {char1.name}보다 {diff:,.2f} DPM 높음 ({percentage:.2f}% 차이, 의미 없음)")
        else:
            print(f"\n{char2.name}가 {char1.name}보다 {diff:,.2f} DPM 높음 ({percentage:.2f}% 강함)")
    else:
        print("\n두 캐릭터의 데미지가 동일합니다.")
    
    # APM 비교
    apm_diff = apm1 - apm2
    if apm_diff > INSIGNIFICANT_APM_DIFFERENCE_THRESHOLD:
        print(f"{char2.name}가 {char1.name}보다 {abs(apm_diff):.1f} APM 느림")
    elif apm_diff < -INSIGNIFICANT_APM_DIFFERENCE_THRESHOLD:
        print(f"{char2.name}가 {char1.name}보다 {abs(apm_diff):.1f} APM 빠름")
    else:
        print(f"APM 차이: {apm_diff:+.1f} ({apm1:.1f} vs {apm2:.1f}) (의미 없음)")
    
    print("="*50)


class CharacterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("캐릭터 추가스펙 계산기")
        self.root.geometry("1x1000")
        self.root.update_idletasks()
        self.root.geometry("")
        self.root.resizable(True, True)
        self.root.configure(bg=PASTEL_BG)
        
        # 폰트 정의를 먼저!
        self.text_font = ("맑은 고딕", 10)
        
        # 스타일 설정 (연베이지톤)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.TFrame", background=PASTEL_BG)
        style.configure("Custom.TLabel", background=PASTEL_BG)
        style.configure("Custom.TLabelframe", background=PASTEL_BG)
        style.configure("Custom.Treeview", background=PASTEL_BG, fieldbackground=PASTEL_BG, borderwidth=0)
        style.configure("Custom.Treeview.Heading", background=PASTEL_BG)
        style.map("Custom.Treeview", background=[('selected', '#e0d8c3')])
        style.configure("Custom.TEntry", fieldbackground=PASTEL_BG, background=PASTEL_BG)
        style.configure("Korean.TCheckbutton", background=PASTEL_BG)
        style.configure("Korean.TButton", background=PASTEL_BG)
        
        self.create_widgets()
        self.root.after(100, self.auto_load_settings)
    
    def setup_korean_font(self):
        """한글 폰트 설정 (WSL2 등 환경 자동 대응)"""
        try:
            # 고정폭 한글 폰트 우선 (표 출력용)
            monospace_korean_fonts = [
                'D2Coding', 'NanumGothicCoding', 'NanumBarunGothicCoding',
                'Consolas', 'Courier New', 'Monaco', 'Menlo'
            ]
            
            # 일반 한글 폰트들
            korean_fonts = [
                'NanumGothic', 'NanumBarunGothic', 'NanumSquare', 'NanumMyeongjo',
                'Malgun Gothic', 'Dotum', 'Gulim', 'Batang',
                'DejaVu Sans', 'Liberation Sans', 'Ubuntu', 'Noto Sans CJK KR'
            ]

            # 사용 가능한 폰트 찾기 (tkinter.font 명시적 사용)
            available_fonts = list(tkinter.font.families())
            selected_font = None
            selected_monospace_font = None

            # 고정폭 폰트 먼저 찾기
            for font_name in monospace_korean_fonts:
                if font_name in available_fonts:
                    selected_monospace_font = font_name
                    break

            # 일반 폰트 찾기
            for font_name in korean_fonts:
                if font_name in available_fonts:
                    selected_font = font_name
                    break

            if selected_font:
                # 기본 폰트 설정
                default_font = tkinter.font.nametofont("TkDefaultFont")
                default_font.configure(family=selected_font, size=10)
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
                
            # 고정폭 폰트 설정
            if selected_monospace_font:
                self.monospace_font = (selected_monospace_font, 10)
                print(f"[INFO] 고정폭 폰트 적용: {selected_monospace_font}")
            else:
                self.monospace_font = ("Consolas", 10)
                print("[INFO] 기본 고정폭 폰트 적용: Consolas")
                
        except Exception as e:
            print(f"폰트 설정 중 오류: {e}")
            self.text_font = ("TkDefaultFont", 10)
            self.monospace_font = ("Consolas", 10)
    


    
    def save_settings(self):
        """현재 설정을 JSON 파일로 저장"""
        settings = {
            "char1": {
                "name": self.char1_name_var.get(),
                "seventh_awakening": self.char1_seventh_awakening_var.get(),
                "cooldown": self.char1_cooldown_var.get(),
                "amplification": self.char1_amplification_var.get(),
                "third_awakening": self.char1_third_awakening_var.get(),
                "attack_speed": self.char1_attack_speed_var.get(),
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
                "seventh_awakening": self.char2_seventh_awakening_var.get(),
                "cooldown": self.char2_cooldown_var.get(),
                "amplification": self.char2_amplification_var.get(),
                "third_awakening": self.char2_third_awakening_var.get(),
                "attack_speed": self.char2_attack_speed_var.get(),
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
                self.char1_name_var.set(char1.get("name", "사브리나(전)"))
                self.char1_seventh_awakening_var.set(char1.get("seventh_awakening", True))
                self.char1_cooldown_var.set(char1.get("cooldown", True))
                self.char1_amplification_var.set(char1.get("amplification", False))
                self.char1_third_awakening_var.set(char1.get("third_awakening", False))
                self.char1_attack_speed_var.set(char1.get("attack_speed", "129"))
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
                self.char2_name_var.set(char2.get("name", "사브리나(후)"))
                self.char2_seventh_awakening_var.set(char2.get("seventh_awakening", True))
                self.char2_cooldown_var.set(char2.get("cooldown", True))
                self.char2_amplification_var.set(char2.get("amplification", False))
                self.char2_third_awakening_var.set(char2.get("third_awakening", False))
                self.char2_attack_speed_var.set(char2.get("attack_speed", "129"))
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
                self.minutes_var.set(sim.get("minutes", "1"))
                self.simulations_var.set(sim.get("simulations", "20000"))
            
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
        main_frame = ttk.Frame(self.root, style="Custom.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        for i in range(2):
            main_frame.grid_columnconfigure(i, minsize=140)
        main_frame.grid_rowconfigure(5, weight=1)

        # 캐릭터 1 프레임 (tk.LabelFrame, 배경색 지정)
        char1_frame = tk.LabelFrame(main_frame, text="캐릭터 1", bg=PASTEL_BG, fg="black", font=self.text_font)
        char1_frame.grid(row=0, column=0, sticky=tk.NW, padx=(2, 8), pady=(4, 0))
        # 캐릭터 2 프레임 (tk.LabelFrame, 배경색 지정)
        char2_frame = tk.LabelFrame(main_frame, text="캐릭터 2", bg=PASTEL_BG, fg="black", font=self.text_font)
        char2_frame.grid(row=0, column=1, sticky=tk.NW, padx=0, pady=(4, 0))

        # 공통 설정 프레임 (tk.LabelFrame)
        common_frame = tk.LabelFrame(main_frame, text="공통 설정", bg=PASTEL_BG, fg="black", font=self.text_font)
        common_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 2), padx=(2, 2))
        entry_width = 12
        entry_justify = 'right'
        entry_padx_1 = (3, 6)
        entry_padx_2 = (29, 2)
        label_padx_1 = (2, 3)
        label_padx_2 = (10, 2)
        # 1행
        tk.Label(common_frame, text="일반 공격 배율 (%):", font=self.text_font, bg=PASTEL_BG).grid(row=0, column=0, sticky=tk.W, padx=label_padx_1)
        self.damage_1_var = tk.StringVar(value=str(round(Character.DEFAULT_DAMAGE_SKILL_1*100, 2)))
        tk.Entry(common_frame, textvariable=self.damage_1_var, width=entry_width, font=self.text_font, justify=entry_justify, bg="white", relief="groove").grid(row=0, column=1, sticky=tk.W, padx=entry_padx_1)
        tk.Label(common_frame, text="일반 공격 타수:", font=self.text_font, bg=PASTEL_BG).grid(row=0, column=2, sticky=tk.W, padx=label_padx_2)
        self.hit_1_var = tk.StringVar(value=str(Character.DEFAULT_HIT_1))
        tk.Entry(common_frame, textvariable=self.hit_1_var, width=entry_width, font=self.text_font, justify=entry_justify, bg="white", relief="groove").grid(row=0, column=3, sticky=tk.W, padx=entry_padx_2)
        # 2행
        tk.Label(common_frame, text="치명타 공격 배율 (%):", font=self.text_font, bg=PASTEL_BG).grid(row=1, column=0, sticky=tk.W, padx=label_padx_1)
        self.damage_2_var = tk.StringVar(value=str(round(Character.DEFAULT_DAMAGE_SKILL_2*100, 2)))
        tk.Entry(common_frame, textvariable=self.damage_2_var, width=entry_width, font=self.text_font, justify=entry_justify, bg="white", relief="groove").grid(row=1, column=1, sticky=tk.W, padx=entry_padx_1)
        tk.Label(common_frame, text="치명타 공격 타수:", font=self.text_font, bg=PASTEL_BG).grid(row=1, column=2, sticky=tk.W, padx=label_padx_2)
        self.hit_2_var = tk.StringVar(value=str(Character.DEFAULT_HIT_2))
        tk.Entry(common_frame, textvariable=self.hit_2_var, width=entry_width, font=self.text_font, justify=entry_justify, bg="white", relief="groove").grid(row=1, column=3, sticky=tk.W, padx=entry_padx_2)
        # 3행
        tk.Label(common_frame, text="전용 스킬 배율 (%):", font=self.text_font, bg=PASTEL_BG).grid(row=2, column=0, sticky=tk.W, padx=label_padx_1)
        self.damage_3_var = tk.StringVar(value=str(round(Character.DEFAULT_DAMAGE_SKILL_3*100, 2)))
        tk.Entry(common_frame, textvariable=self.damage_3_var, width=entry_width, font=self.text_font, justify=entry_justify, bg="white", relief="groove").grid(row=2, column=1, sticky=tk.W, padx=entry_padx_1)
        tk.Label(common_frame, text="전용 스킬 타수:", font=self.text_font, bg=PASTEL_BG).grid(row=2, column=2, sticky=tk.W, padx=label_padx_2)
        self.hit_3_var = tk.StringVar(value=str(Character.DEFAULT_HIT_3))
        tk.Entry(common_frame, textvariable=self.hit_3_var, width=entry_width, font=self.text_font, justify=entry_justify, bg="white", relief="groove").grid(row=2, column=3, sticky=tk.W, padx=entry_padx_2)
        # 4행
        tk.Label(common_frame, text="치명타 쿨타임 (초):", font=self.text_font, bg=PASTEL_BG).grid(row=3, column=0, sticky=tk.W, padx=label_padx_1, pady=(0, 1))
        self.critical_cd_var = tk.StringVar(value=str(Character.DEFAULT_CRITICAL_COOLDOWN))
        tk.Entry(common_frame, textvariable=self.critical_cd_var, width=entry_width, font=self.text_font, justify=entry_justify, bg="white", relief="groove").grid(row=3, column=1, sticky=tk.W, padx=entry_padx_1, pady=(0, 1))
        tk.Label(common_frame, text="스킬 쿨타임 (초):", font=self.text_font, bg=PASTEL_BG).grid(row=3, column=2, sticky=tk.W, padx=label_padx_2, pady=(0, 1))
        self.skill_cd_var = tk.StringVar(value=str(Character.DEFAULT_SKILL_COOLDOWN))
        tk.Entry(common_frame, textvariable=self.skill_cd_var, width=entry_width, font=self.text_font, justify=entry_justify, bg="white", relief="groove").grid(row=3, column=3, sticky=tk.W, padx=entry_padx_2, pady=(0, 1))

        # 시뮬레이션 설정 프레임 (tk.LabelFrame)
        simulation_frame = tk.LabelFrame(main_frame, text="시뮬레이션 설정", bg=PASTEL_BG, fg="black", font=self.text_font)
        simulation_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 2), padx=(2, 2))
        tk.Label(simulation_frame, text="시뮬레이션 시간 (분):", font=self.text_font, bg=PASTEL_BG).grid(row=0, column=0, sticky=tk.W, padx=(2, 6), pady=(0, 1))
        self.minutes_var = tk.StringVar(value="1")
        tk.Entry(simulation_frame, textvariable=self.minutes_var, width=entry_width, font=self.text_font, justify=entry_justify, bg="white", relief="groove").grid(row=0, column=1, sticky=tk.W, padx=entry_padx_1, pady=(0, 1))
        tk.Label(simulation_frame, text="시뮬레이션 횟수:", font=self.text_font, bg=PASTEL_BG).grid(row=0, column=2, sticky=tk.W, padx=label_padx_2, pady=(0, 1))
        self.simulations_var = tk.StringVar(value="10000")
        tk.Entry(simulation_frame, textvariable=self.simulations_var, width=entry_width, font=self.text_font, justify=entry_justify, bg="white", relief="groove").grid(row=0, column=3, sticky=tk.W, padx=(32, 2), pady=(0, 1))

        # 버튼 프레임 (tk.Frame)
        button_frame = tk.Frame(main_frame, bg=PASTEL_BG)
        button_frame.grid(row=4, column=0, columnspan=4, pady=10)
        button_width = 18
        tk.Button(button_frame, text="초기 값으로 돌리기", command=self.set_default_values, bg=PASTEL_BG, activebackground=PASTEL_BG, highlightbackground=PASTEL_BG, font=self.text_font, width=button_width).grid(row=0, column=0, padx=8, pady=4)
        tk.Button(button_frame, text="설정 저장", command=self.save_settings, bg=PASTEL_BG, activebackground=PASTEL_BG, highlightbackground=PASTEL_BG, font=self.text_font, width=button_width).grid(row=0, column=1, padx=8, pady=4)
        tk.Button(button_frame, text="설정 불러오기", command=self.load_settings, bg=PASTEL_BG, activebackground=PASTEL_BG, highlightbackground=PASTEL_BG, font=self.text_font, width=button_width).grid(row=0, column=2, padx=8, pady=4)
        tk.Button(button_frame, text="캐릭터 1→2 복사", command=self.set_char1_to_char2, bg=PASTEL_BG, activebackground=PASTEL_BG, highlightbackground=PASTEL_BG, font=self.text_font, width=button_width).grid(row=1, column=0, padx=8, pady=4)
        tk.Button(button_frame, text="캐릭터 2→1 복사", command=self.set_char2_to_char1, bg=PASTEL_BG, activebackground=PASTEL_BG, highlightbackground=PASTEL_BG, font=self.text_font, width=button_width).grid(row=1, column=1, padx=8, pady=4)
        tk.Button(button_frame, text="데미지 비교", command=self.compare_damage, bg=PASTEL_BG, activebackground=PASTEL_BG, highlightbackground=PASTEL_BG, font=self.text_font, width=button_width).grid(row=1, column=2, padx=8, pady=4)

        # 결과 프레임 (tk.LabelFrame, 배경색 지정)
        self.result_frame = tk.LabelFrame(main_frame, text="결과", bg=PASTEL_BG, fg="black", font=self.text_font)
        self.result_frame.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0), padx=(2, 2))
        self.result_frame.grid_rowconfigure(0, weight=3)
        self.result_frame.grid_columnconfigure(0, weight=1)
        # 결과 프레임 제목 라벨(배경 통일)
        # tk.Label(self.result_frame, text="결과", bg=PASTEL_BG, font=self.text_font).pack(anchor='w', padx=8, pady=(2, 0))
        self.initial_message = tk.Label(self.result_frame, text="데미지 비교 버튼을 클릭하여 결과를 확인하세요.", bg=PASTEL_BG, font=self.text_font)
        self.initial_message.pack(expand=True, fill='both', pady=20)

        # 저작권 정보 (맨 밑 오른쪽)
        copyright_label = tk.Label(main_frame, text="Made by 교수 (Ch. KO17)", font=("Arial", 8), bg=PASTEL_BG, fg="#888888")
        copyright_label.grid(row=6, column=0, columnspan=4, sticky='se', padx=(0, 5), pady=(2, 2))

        # 캐릭터 1/2 위젯 생성
        self.create_character_widgets(char1_frame, "char1")
        self.create_character_widgets(char2_frame, "char2")
        self.root.update_idletasks()
        self.root.geometry("")
        
    def create_character_widgets(self, parent, char_prefix):
        # 캐릭터 이름
        tk.Label(parent, text="캐릭터 이름:", font=self.text_font, bg=PASTEL_BG).grid(row=0, column=0, sticky=tk.W, padx=(2, 24))
        if char_prefix == "char1":
            setattr(self, f"{char_prefix}_name_var", tk.StringVar(value="사브리나(전)"))
        else:
            setattr(self, f"{char_prefix}_name_var", tk.StringVar(value="사브리나(후)"))
        tk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_name_var"), width=12, font=self.text_font, justify='right', bg="white", relief="groove").grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        # 체크박스 영역을 별도 Frame으로 분리 (1행 4열 가로 배치, 촘촘한 간격)
        check_frame = tk.Frame(parent, bg=PASTEL_BG)
        check_frame.grid(row=1, column=0, columnspan=2, sticky='ew')
        for i in range(4):
            check_frame.grid_columnconfigure(i, weight=1)
        # 3각
        setattr(self, f"{char_prefix}_third_awakening_var", tk.BooleanVar(value=False if char_prefix == "char1" else True))
        tk.Checkbutton(check_frame, text="3각", variable=getattr(self, f"{char_prefix}_third_awakening_var"), bg=PASTEL_BG, activebackground=PASTEL_BG, highlightbackground=PASTEL_BG, relief="flat", borderwidth=0, font=self.text_font).grid(row=0, column=0, sticky='ew', padx=(4, 2))
        # 7각
        setattr(self, f"{char_prefix}_seventh_awakening_var", tk.BooleanVar(value=False if char_prefix == "char1" else True))
        tk.Checkbutton(check_frame, text="7각", variable=getattr(self, f"{char_prefix}_seventh_awakening_var"), bg=PASTEL_BG, activebackground=PASTEL_BG, highlightbackground=PASTEL_BG, relief="flat", borderwidth=0, font=self.text_font).grid(row=0, column=1, sticky='ew', padx=(2, 2))
        # 증폭
        setattr(self, f"{char_prefix}_amplification_var", tk.BooleanVar(value=False if char_prefix == "char1" else True))
        tk.Checkbutton(check_frame, text="증폭", variable=getattr(self, f"{char_prefix}_amplification_var"), bg=PASTEL_BG, activebackground=PASTEL_BG, highlightbackground=PASTEL_BG, relief="flat", borderwidth=0, font=self.text_font).grid(row=0, column=2, sticky='ew', padx=(2, 2))
        # 쿨감
        setattr(self, f"{char_prefix}_cooldown_var", tk.BooleanVar(value=False if char_prefix == "char1" else True))
        tk.Checkbutton(check_frame, text="쿨감", variable=getattr(self, f"{char_prefix}_cooldown_var"), bg=PASTEL_BG, activebackground=PASTEL_BG, highlightbackground=PASTEL_BG, relief="flat", borderwidth=0, font=self.text_font).grid(row=0, column=3, sticky='ew', padx=(2, 4))
        # 공격 관련
        row = 3
        tk.Label(parent, text="공격 속도:", font=self.text_font, bg=PASTEL_BG).grid(row=row, column=0, sticky=tk.W, padx=(2, 24))
        setattr(self, f"{char_prefix}_attack_speed_var", tk.StringVar(value=str(Character.DEFAULT_ATTACK_SPEED)))
        tk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_attack_speed_var"), width=12, font=self.text_font, justify='right', bg="white", relief="groove").grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        row += 1
        tk.Label(parent, text="공격력 (M):", font=self.text_font, bg=PASTEL_BG).grid(row=row, column=0, sticky=tk.W, padx=(2, 24))
        setattr(self, f"{char_prefix}_attack_power_var", tk.StringVar(value=str(Character.DEFAULT_ATTACK_POWER)))
        tk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_attack_power_var"), width=12, font=self.text_font, justify='right', bg="white", relief="groove").grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        # 이하 확률/배율 관련 Entry도 모두 width=12로 통일
        row += 1
        tk.Label(parent, text="치명 확률 (%):", font=self.text_font, bg=PASTEL_BG).grid(row=row, column=0, sticky=tk.W, padx=(2, 24))
        setattr(self, f"{char_prefix}_critical_var", tk.StringVar(value=str(round(Character.DEFAULT_P_CRITICAL*100, 2))))
        critical_entry = tk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_critical_var"), width=12, font=self.text_font, justify='right', bg="white", relief="groove")
        critical_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        critical_entry.bind('<FocusOut>', lambda e, prefix=char_prefix: self.limit_probability(prefix, 'critical'))
        row += 1
        tk.Label(parent, text="강타 확률 (%):", font=self.text_font, bg=PASTEL_BG).grid(row=row, column=0, sticky=tk.W, padx=(2, 24))
        setattr(self, f"{char_prefix}_strong_hit_var", tk.StringVar(value=str(round(Character.DEFAULT_P_STRONG_HIT*100, 2))))
        strong_hit_entry = tk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_strong_hit_var"), width=12, font=self.text_font, justify='right', bg="white", relief="groove")
        strong_hit_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        strong_hit_entry.bind('<FocusOut>', lambda e, prefix=char_prefix: self.limit_probability(prefix, 'strong_hit'))
        row += 1
        tk.Label(parent, text="더블샷 확률 (%):", font=self.text_font, bg=PASTEL_BG).grid(row=row, column=0, sticky=tk.W, padx=(2, 24))
        setattr(self, f"{char_prefix}_double_shot_var", tk.StringVar(value=str(round(Character.DEFAULT_P_DOUBLE_SHOT*100, 2))))
        double_shot_entry = tk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_double_shot_var"), width=12, font=self.text_font, justify='right', bg="white", relief="groove")
        double_shot_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        double_shot_entry.bind('<FocusOut>', lambda e, prefix=char_prefix: self.limit_probability(prefix, 'double_shot'))
        row += 1
        tk.Label(parent, text="트리플샷 확률 (%):", font=self.text_font, bg=PASTEL_BG).grid(row=row, column=0, sticky=tk.W, padx=(2, 24))
        if char_prefix == "char1":
            triple_shot_default = 11.23
        else:
            triple_shot_default = 21.23
        setattr(self, f"{char_prefix}_triple_shot_var", tk.StringVar(value=str(triple_shot_default)))
        triple_shot_entry = tk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_triple_shot_var"), width=12, font=self.text_font, justify='right', bg="white", relief="groove")
        triple_shot_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        triple_shot_entry.bind('<FocusOut>', lambda e, prefix=char_prefix: self.limit_probability(prefix, 'triple_shot'))
        row += 1
        tk.Label(parent, text="치명 피해 (%):", font=self.text_font, bg=PASTEL_BG).grid(row=row, column=0, sticky=tk.W, padx=(2, 24))
        setattr(self, f"{char_prefix}_critical_mult_var", tk.StringVar(value=str(round(Character.DEFAULT_CRITICAL_MULTIPLIER*100, 2))))
        tk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_critical_mult_var"), width=12, font=self.text_font, justify='right', bg="white", relief="groove").grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 2))
        row += 1
        tk.Label(parent, text="강타 피해 (%):", font=self.text_font, bg=PASTEL_BG).grid(row=row, column=0, sticky=tk.W, padx=(2, 24), pady=(0, 1))
        setattr(self, f"{char_prefix}_strong_hit_mult_var", tk.StringVar(value=str(round(Character.DEFAULT_STRONG_HIT_MULTIPLIER*100, 2))))
        tk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_strong_hit_mult_var"), width=12, font=self.text_font, justify='right', bg="white", relief="groove").grid(row=row, column=1, sticky=(tk.W, tk.E), padx=(0, 2), pady=(0, 1))

    def save_initial_values(self):
        self.initial_values = {
            'char1_name': self.char1_name_var.get(),
            'char1_seventh_awakening': self.char1_seventh_awakening_var.get(),
            'char1_cooldown': self.char1_cooldown_var.get(),
            'char1_amplification': self.char1_amplification_var.get(),
            'char1_third_awakening': self.char1_third_awakening_var.get(),
            'char1_attack_speed': self.char1_attack_speed_var.get(),
            'char1_attack_power': self.char1_attack_power_var.get(),
            'char1_critical': self.char1_critical_var.get(),
            'char1_strong_hit': self.char1_strong_hit_var.get(),
            'char1_double_shot': self.char1_double_shot_var.get(),
            'char1_triple_shot': self.char1_triple_shot_var.get(),
            'char1_critical_mult': self.char1_critical_mult_var.get(),
            'char1_strong_hit_mult': self.char1_strong_hit_mult_var.get(),
            'char2_name': self.char2_name_var.get(),
            'char2_seventh_awakening': self.char2_seventh_awakening_var.get(),
            'char2_cooldown': self.char2_cooldown_var.get(),
            'char2_amplification': self.char2_amplification_var.get(),
            'char2_third_awakening': self.char2_third_awakening_var.get(),
            'char2_attack_speed': self.char2_attack_speed_var.get(),
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
            'minutes': self.minutes_var.get() or "1",
            'simulations': self.simulations_var.get()
        }

    def set_default_values(self):
        """프로그램 시작 시점의 값으로 복원"""
        vals = getattr(self, 'initial_values', None)
        if vals is None:
            return
        self.char1_name_var.set(vals['char1_name'])
        self.char1_seventh_awakening_var.set(vals['char1_seventh_awakening'])
        self.char1_cooldown_var.set(vals['char1_cooldown'])
        self.char1_amplification_var.set(vals['char1_amplification'])
        self.char1_third_awakening_var.set(vals['char1_third_awakening'])
        self.char1_attack_speed_var.set(vals['char1_attack_speed'])
        self.char1_attack_power_var.set(vals['char1_attack_power'])
        self.char1_critical_var.set(vals['char1_critical'])
        self.char1_strong_hit_var.set(vals['char1_strong_hit'])
        self.char1_double_shot_var.set(vals['char1_double_shot'])
        self.char1_triple_shot_var.set(vals['char1_triple_shot'])
        self.char1_critical_mult_var.set(vals['char1_critical_mult'])
        self.char1_strong_hit_mult_var.set(vals['char1_strong_hit_mult'])
        self.char2_name_var.set(vals['char2_name'])
        self.char2_seventh_awakening_var.set(vals['char2_seventh_awakening'])
        self.char2_cooldown_var.set(vals['char2_cooldown'])
        self.char2_amplification_var.set(vals['char2_amplification'])
        self.char2_third_awakening_var.set(vals['char2_third_awakening'])
        self.char2_attack_speed_var.set(vals['char2_attack_speed'])
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
            'seventh_awakening', 'cooldown', 'amplification', 'third_awakening', 'attack_speed', 'attack_power',
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
            char.is_seventh_awakening = getattr(self, f"{char_prefix}_seventh_awakening_var").get()
            char.is_cooldown = getattr(self, f"{char_prefix}_cooldown_var").get()
            char.is_amplification = getattr(self, f"{char_prefix}_amplification_var").get()
            char.is_third_awakening = getattr(self, f"{char_prefix}_third_awakening_var").get()
            
            # 공격 관련 - 입력 검증
            attack_speed_value = getattr(self, f"{char_prefix}_attack_speed_var").get()
            if not self.validate_integer_input(attack_speed_value, 1, "공격 속도"):
                return None
            char.attack_speed = int(float(attack_speed_value))
            
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
            
            char.seventh_awakening_multiplier = SEVENTH_AWAKENING_MULTIPLIER if char.is_seventh_awakening else 1
            
            # 데미지 배율 (공통 설정 사용)
            char.damage_skill_1 = float(self.damage_1_var.get()) / 100
            char.damage_skill_2 = float(self.damage_2_var.get()) / 100
            char.damage_skill_3 = float(self.damage_3_var.get()) / 100
            
            # 증폭 효과 적용 (60%p 증가)
            if char.is_amplification:
                char.damage_skill_1 += Character.AMPLIFICATION_BONUS
                char.damage_skill_2 += Character.AMPLIFICATION_BONUS
                char.damage_skill_3 += Character.AMPLIFICATION_BONUS
            
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
        """데미지 비교 실행 - 새로운 깔끔한 출력 방식 사용"""
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
        
        # 기존 결과창 정리 (초기 메시지, 프로그레스 바, 결과창 모두 제거)
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        
        # 초기 메시지 숨기기
        if hasattr(self, 'initial_message'):
            self.initial_message.pack_forget()
        
        # 프로그레스 바 생성
        progress_frame = tk.Frame(self.result_frame, bg=PASTEL_BG)
        progress_frame.pack(fill='x', padx=10, pady=10)
        
        progress_label = tk.Label(progress_frame, text="시뮬레이션 진행 중...", font=self.text_font, bg=PASTEL_BG)
        progress_label.pack(pady=(0, 5))
        
        progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        progress_bar.pack(pady=(0, 5))
        
        progress_text = tk.Label(progress_frame, text="0%", font=self.text_font, bg=PASTEL_BG)
        progress_text.pack()
        
        # 진행률 업데이트 함수
        def update_progress(progress):
            self.root.after(0, lambda: progress_bar.configure(value=progress))
            self.root.after(0, lambda: progress_text.configure(text=f"{progress:.1f}%"))
        
        # 별도 스레드에서 계산 실행 (GUI 블록 방지)
        def run_calculation():
            try:
                minutes = float(self.minutes_var.get())
                simulations = int(self.simulations_var.get())
                
                # 시뮬레이션 실행 (진행률 콜백 포함)
                damage1, apm1 = char1.simulate_damage(minutes, simulations, lambda p: update_progress(p * 0.5))
                damage2, apm2 = char2.simulate_damage(minutes, simulations, lambda p: update_progress(50 + p * 0.5))
                
                # 프로그레스 바 제거
                self.root.after(0, lambda: progress_frame.destroy())
                
                # GUI 업데이트 (새로운 깔끔한 방식 사용)
                self.root.after(0, lambda: create_clean_output_display(self.result_frame, char1, char2, damage1, apm1, damage2, apm2))
                
            except Exception as e:
                error_msg = f"계산 중 오류가 발생했습니다: {str(e)}"
                self.root.after(0, lambda: progress_frame.destroy())
                self.root.after(0, lambda: messagebox.showerror("계산 오류", error_msg))
        
        # 스레드 시작
        thread = threading.Thread(target=run_calculation)
        thread.daemon = True
        thread.start()


def create_table_frame(parent, headers, data, table_name="", height=6, is_amplification=False, main_canvas=None):
    """Treeview를 사용한 표 프레임 생성 (연베이지톤 스타일 적용)"""
    try:
        frame = ttk.Frame(parent, style="Custom.TFrame")
        if table_name:
            title_label = ttk.Label(frame, text=table_name, font=("Arial", 10, "bold"), style="Custom.TLabel")
            title_label.pack(pady=(5, 2))
            # 테이블 제목 라벨에도 마우스 휠 바인딩 적용
            if main_canvas and hasattr(main_canvas, 'yview_scroll'):
                def _on_mousewheel(event):
                    main_canvas.yview_scroll(-1 * int(event.delta / 120), "units")
                title_label.bind("<MouseWheel>", _on_mousewheel)
        
        # 고정된 총 너비 설정
        total_width = 434  # 총 테이블 너비 (픽셀)
        column_count = len(headers)
        base_width = total_width // column_count  # 기본 컬럼 너비
        
        tree = ttk.Treeview(frame, columns=headers, show='headings', height=height, style="Custom.Treeview")
        
        for i, header in enumerate(headers):
            tree.heading(header, text=header)
            # 스킬 배율 표에서 증폭이 활성화된 경우 두 번째 열("기본 배율") 너비 조정
            if table_name == "스킬 배율" and is_amplification and i == 1:  # 두 번째 열 (index 1)
                column_width = int(base_width * 1.4)  # 40% 더 넓게
            elif table_name == "스킬 배율" and is_amplification and i != 1:  # 나머지 컬럼은 좁게
                column_width = int(base_width * 0.85)  # 15% 더 좁게
            else:
                column_width = int(base_width * 1)  # 기본 너비
            tree.column(header, width=column_width, anchor='center')
        
        for row in data:
            item = tree.insert('', 'end', values=row)
            
            # 색상 태그 설정
            tree.tag_configure('white_bg', background='white')
            tree.tag_configure('red_text', foreground='red')
            tree.tag_configure('blue_text', foreground='blue')
            tree.tag_configure('gray_text', foreground='gray')
            
            # 비교 표시가 있는 경우 색상 적용
            tags = ['white_bg']
            for value in row:
                if isinstance(value, str):
                    if '▲' in value:
                        tags.append('blue_text')
                        break
                    elif '▼' in value:
                        tags.append('red_text')
                        break
                    elif '(의미 없음)' in value:
                        tags.append('gray_text')
                        break
            
            tree.item(item, tags=tuple(tags))
        
        tree.pack(side='left', fill='both', expand=True)
        
        # Treeview에도 마우스 휠 스크롤 바인딩 적용 (main_canvas가 전달된 경우에만)
        if main_canvas and hasattr(main_canvas, 'yview_scroll'):
            def _on_mousewheel(event):
                main_canvas.yview_scroll(-1 * int(event.delta / 120), "units")
            tree.bind("<MouseWheel>", _on_mousewheel)
            
        return frame
    except Exception as e:
        print(f"Treeview 생성 중 오류: {e}")
        return ttk.Frame(parent, style="Custom.TFrame")




def main():
    root = tk.Tk()
    app = CharacterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main() 