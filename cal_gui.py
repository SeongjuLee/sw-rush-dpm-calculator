import tkinter as tk
from tkinter import ttk, messagebox
import threading
import random
import sys
import locale
import tkinter.font  # 추가: 폰트 관련 모듈 명시적 import

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
    DEFAULT_P_DOUBLE_SHOT = 22.36 / 100
    DEFAULT_P_TRIPLE_SHOT = 21.11 / 100
    DEFAULT_CRITICAL_MULTIPLIER = 1184.28 / 100
    DEFAULT_STRONG_HIT_MULTIPLIER = 158.03 / 100
    DEFAULT_AWAKENING = True
    DEFAULT_COOLDOWN = True
    DEFAULT_DAMAGE_SKILL_1 = 430 / 100
    DEFAULT_DAMAGE_SKILL_2 = 190 * 3 / 100
    DEFAULT_DAMAGE_SKILL_3 = 840 / 100
    DEFAULT_CRITICAL_COOLDOWN = 2
    DEFAULT_SKILL_COOLDOWN = 10

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
        self.awakening_multiplier = 1.2 if self.is_awakening else 1
        
        # 데미지 배율
        self.damage_skill_1 = Character.DEFAULT_DAMAGE_SKILL_1
        self.damage_skill_2 = Character.DEFAULT_DAMAGE_SKILL_2
        self.damage_skill_3 = Character.DEFAULT_DAMAGE_SKILL_3
        
        # 쿨타임 설정
        self.critical_cooldown = Character.DEFAULT_CRITICAL_COOLDOWN
        self.skill_cooldown = Character.DEFAULT_SKILL_COOLDOWN
        
        # 쿨타임 감소 적용
        if self.is_cooldown:
            self.critical_cooldown *= 0.8
            self.skill_cooldown *= 0.8
    
    def simulate_damage(self, minutes=10, simulations=10000):
        """캐릭터의 데미지를 시뮬레이션하여 분당 데미지(DPM)를 계산"""
        return simulate_attacks_with_critical_and_skill(
            self.attacks_per_minute, minutes, self.p_critical, self.attack_power,
            self.damage_skill_1, self.damage_skill_2, self.damage_skill_3,
            self.critical_multiplier, self.p_strong_hit, self.strong_hit_multiplier, 
            self.awakening_multiplier, self.p_double_shot, self.p_triple_shot,
            self.critical_cooldown, self.skill_cooldown, simulations
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


def simulate_attacks_with_critical_and_skill(attacks_per_minute, minutes, p_critical, attack_power=1,
                                           damage_skill_1=1, damage_skill_2=2, damage_skill_3=5, 
                                           critical_multiplier=2, p_strong_hit=0.1, strong_hit_multiplier=2, awakening_multiplier=1,
                                           p_double_shot=0.1, p_triple_shot=0.05,
                                           critical_cooldown=2, skill_cooldown=10, simulations=10000):
    # attacks_per_minute를 정수로 변환 (range() 함수에서 사용하기 위해)
    attacks_per_minute = int(attacks_per_minute)
    """
    치명타 공격과 스킬 공격을 모두 고려한 몬테카를로 시뮬레이션을 통한 데미지 기댓값 계산
    우선순위: 스킬 > 치명타 > 일반 공격
    스킬은 쿨타임이 다 되면 무조건 발동
    
    Args:
        attacks_per_minute (int): 1분당 공격 횟수 (k)
        minutes (int): 공격 시간 (n분)
        p_critical (float): 치명 확률 (0~1)
        attack_power (int): 공격력 (기본값: 1)
        damage_skill_1 (int): 일반 공격당 데미지 (기본값: 1)
        damage_skill_2 (int): 치명타 공격당 데미지 (기본값: 2)
        damage_skill_3 (int): 스킬 공격당 데미지 (기본값: 5)
        critical_multiplier (int): 치명 피해 (기본값: 2)
        p_strong_hit (float): 강타 확률 (0~1, 기본값: 0.1)
        strong_hit_multiplier (int): 강타 피해 (기본값: 2)
        awakening_multiplier (int): 각성 배율 (기본값: 1)
        p_double_shot (float): 더블샷 확률 (0~1, 기본값: 0.1)
        p_triple_shot (float): 트리플샷 확률 (0~1, 기본값: 0.05)
        critical_cooldown (int): 치명타 쿨타임 (초, 기본값: 2)
        skill_cooldown (int): 스킬 쿨타임 (초, 기본값: 10)
        simulations (int): 시뮬레이션 횟수
    
    Returns:
        float: 시뮬레이션을 통한 데미지 기댓값 (분당)
    """
    total_damage = 0
    
    for _ in range(simulations):
        damage_this_simulation = 0
        time_since_last_critical = critical_cooldown  # 초기값을 쿨타임으로 설정
        time_since_last_skill = skill_cooldown  # 초기값을 쿨타임으로 설정
        
        # 각 분마다 attacks_per_minute만큼 공격
        for minute in range(minutes):
            # 1분 동안의 공격 횟수를 정확히 attacks_per_minute로 설정
            for attack in range(attacks_per_minute):
                # 공격 간격 (초 단위)
                attack_interval = 60 / attacks_per_minute
                time_since_last_critical += attack_interval
                time_since_last_skill += attack_interval
                
                # 우선순위에 따른 공격 타입 결정
                # 1. 스킬 쿨타임이 지났으면 무조건 스킬 사용 (우선순위 최고)
                if time_since_last_skill >= skill_cooldown:
                    # 스킬 공격에 치명 확률 적용
                    damge_tick = damage_skill_3 * attack_power * awakening_multiplier
                    # 강타 확률 적용
                    if random.random() < p_strong_hit:
                        damge_tick *= strong_hit_multiplier
                    damage_this_simulation += damge_tick
                    time_since_last_skill = 0  # 스킬 사용 시 쿨타임 리셋
                # 2. 스킬이 사용되지 않았고, 치명타 쿨타임이 지났고 치명 확률에 따라 치명타 공격
                elif time_since_last_critical >= critical_cooldown and random.random() < p_critical:
                    damge_tick = damage_skill_2 * critical_multiplier * attack_power * awakening_multiplier
                    # 강타 확률 적용
                    if random.random() < p_strong_hit:
                        damge_tick *= strong_hit_multiplier
                    damage_this_simulation += damge_tick
                    time_since_last_critical = 0  # 치명타 발생 시 쿨타임 리셋
                # 3. 스킬과 치명타가 모두 발생하지 않았으면 일반 공격
                else:
                    # 더블샷/트리플샷 확률 결정 (둘 다는 불가능)
                    shot_count = 1
                    if random.random() < p_triple_shot:
                        shot_count = 3
                    elif random.random() < p_double_shot:
                        shot_count = 2
                    
                    # 각 샷에 대해 데미지 계산
                    for _ in range(shot_count):
                        # 일반 공격에 치명 확률 적용
                        damge_tick = damage_skill_1 * attack_power * awakening_multiplier
                        # 강타 확률 적용
                        if random.random() < p_strong_hit:
                            damge_tick *= strong_hit_multiplier
                        damage_this_simulation += damge_tick
        
        total_damage += damage_this_simulation
    
    return total_damage / (simulations * minutes)


def compare_characters(char1, char2, minutes=10, simulations=10000):
    """두 캐릭터의 데미지를 비교"""
    print("=" * 60)
    print("캐릭터 데미지 비교")
    print("=" * 60)
    
    # 각 캐릭터의 스탯 출력
    char1.print_stats()
    char2.print_stats()
    
    # 데미지 계산
    damage1 = char1.simulate_damage(minutes, simulations)
    damage2 = char2.simulate_damage(minutes, simulations)
    
    # 결과 출력
    print("=" * 60)
    print("데미지 비교 결과")
    print("=" * 60)
    print(f"{char1.name} DPM: {damage1:,.2f}")
    print(f"{char2.name} DPM: {damage2:,.2f}")
    print()
    
    if damage1 > damage2:
        diff = damage1 - damage2
        percentage = (diff / damage2) * 100
        print(f"{char1.name}이 {char2.name}보다 {diff:,.2f} DPM 높음 ({percentage:.2f}% 더 강함)")
    elif damage2 > damage1:
        diff = damage2 - damage1
        percentage = (diff / damage1) * 100
        print(f"{char2.name}이 {char1.name}보다 {diff:,.2f} DPM 높음 ({percentage:.2f}% 더 강함)")
    else:
        print("두 캐릭터의 데미지가 동일합니다.")
    
    print("=" * 60)


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
        
    def create_widgets(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)
        main_frame.columnconfigure(2, weight=1)

        # 캐릭터 1 프레임
        char1_frame = ttk.LabelFrame(main_frame, text="캐릭터 1", padding="2", style="Korean.TLabelframe")
        char1_frame.grid(row=1, column=0, sticky=tk.NW, padx=0, pady=0)
        # 중간 패딩 (빈 라벨)
        ttk.Label(main_frame, text="", width=2).grid(row=1, column=1)
        # 캐릭터 2 프레임
        char2_frame = ttk.LabelFrame(main_frame, text="캐릭터 2", padding="2", style="Korean.TLabelframe")
        char2_frame.grid(row=1, column=2, sticky=tk.NW, padx=0, pady=0)

        # 설정 프레임
        settings_frame = ttk.LabelFrame(main_frame, text="시뮬레이션 설정", padding="2", style="Korean.TLabelframe")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 2), padx=0)

        # 시뮬레이션 설정
        ttk.Label(settings_frame, text="시뮬레이션 시간 (분):", font=self.text_font).grid(row=0, column=0, sticky=tk.W)
        self.minutes_var = tk.StringVar(value="10")
        ttk.Entry(settings_frame, textvariable=self.minutes_var, width=12, font=self.text_font).grid(row=0, column=1, padx=(4, 23))
        ttk.Label(settings_frame, text="시뮬레이션 횟수:", font=self.text_font).grid(row=0, column=2, sticky=tk.W)
        self.simulations_var = tk.StringVar(value="10000")
        ttk.Entry(settings_frame, textvariable=self.simulations_var, width=12, font=self.text_font).grid(row=0, column=3, padx=(31.5, 0))

        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)

        # 결과 프레임
        result_frame = ttk.LabelFrame(main_frame, text="결과", padding="2", style="Korean.TLabelframe")
        result_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(2, 0), padx=0)
        self.result_text = tk.Text(result_frame, height=25, width=65, wrap=tk.WORD, font=self.text_font)
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 캐릭터 1 위젯 생성
        self.create_character_widgets(char1_frame, "char1")
        
        # 캐릭터 2 위젯 생성
        self.create_character_widgets(char2_frame, "char2")
        
        # 버튼들
        ttk.Button(button_frame, text="기본값으로 설정", command=self.set_default_values, style="Korean.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="캐릭터 1→2 복사", command=self.set_char2_default, style="Korean.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="캐릭터 2→1 복사", command=self.set_char1_default, style="Korean.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="데미지 비교", command=self.compare_damage, style="Korean.TButton").pack(side=tk.LEFT, padx=5)
        
        # 초기값 설정
        self.set_default_values()
        
        # 창이 내용에 맞게 자동으로 크기 조정되도록 설정
        self.root.update_idletasks()
        self.root.geometry("")  # 내용에 맞게 자동 조정
        
    def create_character_widgets(self, parent, char_prefix):
        # 캐릭터 이름
        ttk.Label(parent, text="캐릭터 이름:", font=self.text_font).grid(row=0, column=0, sticky=tk.W, pady=2)
        if char_prefix == "char1":
            setattr(self, f"{char_prefix}_name_var", tk.StringVar(value="캐릭터 (전)"))
        else:
            setattr(self, f"{char_prefix}_name_var", tk.StringVar(value="캐릭터 (후)"))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_name_var"), width=10, font=self.text_font).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 체크박스들
        setattr(self, f"{char_prefix}_awakening_var", tk.BooleanVar(value=Character.DEFAULT_AWAKENING))
        ttk.Checkbutton(parent, text="각성", variable=getattr(self, f"{char_prefix}_awakening_var"), style="Korean.TCheckbutton").grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        setattr(self, f"{char_prefix}_cooldown_var", tk.BooleanVar(value=Character.DEFAULT_COOLDOWN))
        ttk.Checkbutton(parent, text="쿨타임 감소", variable=getattr(self, f"{char_prefix}_cooldown_var"), style="Korean.TCheckbutton").grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 공격 관련
        row = 2
        ttk.Label(parent, text="공격 속도 (회/분):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, pady=2)
        setattr(self, f"{char_prefix}_attacks_var", tk.StringVar(value=str(Character.DEFAULT_ATTACKS_PER_MINUTE)))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_attacks_var"), width=6, font=self.text_font).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
        
        row += 1
        ttk.Label(parent, text="공격력 (M):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, pady=2)
        setattr(self, f"{char_prefix}_attack_power_var", tk.StringVar(value=str(Character.DEFAULT_ATTACK_POWER)))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_attack_power_var"), width=6, font=self.text_font).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 확률 관련
        row += 1
        ttk.Label(parent, text="치명 확률 (%):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, pady=2)
        setattr(self, f"{char_prefix}_critical_var", tk.StringVar(value=str(round(Character.DEFAULT_P_CRITICAL*100, 2))))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_critical_var"), width=6, font=self.text_font).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
        
        row += 1
        ttk.Label(parent, text="강타 확률 (%):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, pady=2)
        setattr(self, f"{char_prefix}_strong_hit_var", tk.StringVar(value=str(round(Character.DEFAULT_P_STRONG_HIT*100, 2))))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_strong_hit_var"), width=6, font=self.text_font).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
        
        row += 1
        ttk.Label(parent, text="더블샷 확률 (%):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, pady=2)
        setattr(self, f"{char_prefix}_double_shot_var", tk.StringVar(value=str(round(Character.DEFAULT_P_DOUBLE_SHOT*100, 2))))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_double_shot_var"), width=6, font=self.text_font).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
        
        row += 1
        ttk.Label(parent, text="트리플샷 확률 (%):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, pady=2)
        setattr(self, f"{char_prefix}_triple_shot_var", tk.StringVar(value=str(round(Character.DEFAULT_P_TRIPLE_SHOT*100, 2))))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_triple_shot_var"), width=6, font=self.text_font).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 배율 관련
        row += 1
        ttk.Label(parent, text="치명 피해 (%):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, pady=2)
        setattr(self, f"{char_prefix}_critical_mult_var", tk.StringVar(value=str(round(Character.DEFAULT_CRITICAL_MULTIPLIER*100, 2))))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_critical_mult_var"), width=6, font=self.text_font).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
        
        row += 1
        ttk.Label(parent, text="강타 피해 (%):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, pady=2)
        setattr(self, f"{char_prefix}_strong_hit_mult_var", tk.StringVar(value=str(round(Character.DEFAULT_STRONG_HIT_MULTIPLIER*100, 2))))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_strong_hit_mult_var"), width=6, font=self.text_font).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 데미지 배율
        row += 1
        ttk.Label(parent, text="일반 공격 배율 (%):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, pady=2)
        setattr(self, f"{char_prefix}_damage_1_var", tk.StringVar(value=str(round(Character.DEFAULT_DAMAGE_SKILL_1*100, 2))))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_damage_1_var"), width=6, font=self.text_font).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
        
        row += 1
        ttk.Label(parent, text="치명타 공격 배율 (%):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, pady=2)
        setattr(self, f"{char_prefix}_damage_2_var", tk.StringVar(value=str(round(Character.DEFAULT_DAMAGE_SKILL_2*100, 2))))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_damage_2_var"), width=6, font=self.text_font).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
        
        row += 1
        ttk.Label(parent, text="전용 스킬 배율 (%):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, pady=2)
        setattr(self, f"{char_prefix}_damage_3_var", tk.StringVar(value=str(round(Character.DEFAULT_DAMAGE_SKILL_3*100, 2))))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_damage_3_var"), width=6, font=self.text_font).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 쿨타임
        row += 1
        ttk.Label(parent, text="치명타 쿨타임 (초):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, pady=2)
        setattr(self, f"{char_prefix}_critical_cd_var", tk.StringVar(value=str(Character.DEFAULT_CRITICAL_COOLDOWN)))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_critical_cd_var"), width=6, font=self.text_font).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
        
        row += 1
        ttk.Label(parent, text="스킬 쿨타임 (초):", font=self.text_font).grid(row=row, column=0, sticky=tk.W, pady=2)
        setattr(self, f"{char_prefix}_skill_cd_var", tk.StringVar(value=str(Character.DEFAULT_SKILL_COOLDOWN)))
        ttk.Entry(parent, textvariable=getattr(self, f"{char_prefix}_skill_cd_var"), width=6, font=self.text_font).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
    
    def set_default_values(self):
        """Character 클래스의 원래 기본값으로 설정"""
        # 기본 캐릭터 이름 설정
        self.char1_name_var.set("캐릭터 (전)")
        self.char2_name_var.set("캐릭터 (후)")
        
        # Character 클래스의 기본값으로 설정
        self.set_character_to_default("char1")
        self.set_character_to_default("char2")
    
    def set_character_to_default(self, char_prefix):
        """캐릭터를 Character 클래스의 기본값으로 설정"""
        # 기본 설정
        getattr(self, f"{char_prefix}_awakening_var").set(Character.DEFAULT_AWAKENING)
        getattr(self, f"{char_prefix}_cooldown_var").set(Character.DEFAULT_COOLDOWN)
        
        # 공격 관련
        getattr(self, f"{char_prefix}_attacks_var").set(str(Character.DEFAULT_ATTACKS_PER_MINUTE))
        getattr(self, f"{char_prefix}_attack_power_var").set(str(Character.DEFAULT_ATTACK_POWER))
        
        # 확률 관련
        getattr(self, f"{char_prefix}_critical_var").set(str(round(Character.DEFAULT_P_CRITICAL*100, 2)))
        getattr(self, f"{char_prefix}_strong_hit_var").set(str(round(Character.DEFAULT_P_STRONG_HIT*100, 2)))
        getattr(self, f"{char_prefix}_double_shot_var").set(str(round(Character.DEFAULT_P_DOUBLE_SHOT*100, 2)))
        getattr(self, f"{char_prefix}_triple_shot_var").set(str(round(Character.DEFAULT_P_TRIPLE_SHOT*100, 2)))
        
        # 배율 관련
        getattr(self, f"{char_prefix}_critical_mult_var").set(str(round(Character.DEFAULT_CRITICAL_MULTIPLIER*100, 2)))
        getattr(self, f"{char_prefix}_strong_hit_mult_var").set(str(round(Character.DEFAULT_STRONG_HIT_MULTIPLIER*100, 2)))
        
        # 데미지 배율
        getattr(self, f"{char_prefix}_damage_1_var").set(str(round(Character.DEFAULT_DAMAGE_SKILL_1*100, 2)))
        getattr(self, f"{char_prefix}_damage_2_var").set(str(round(Character.DEFAULT_DAMAGE_SKILL_2*100, 2)))
        getattr(self, f"{char_prefix}_damage_3_var").set(str(round(Character.DEFAULT_DAMAGE_SKILL_3*100, 2)))
        
        # 쿨타임
        getattr(self, f"{char_prefix}_critical_cd_var").set(str(Character.DEFAULT_CRITICAL_COOLDOWN))
        getattr(self, f"{char_prefix}_skill_cd_var").set(str(Character.DEFAULT_SKILL_COOLDOWN))
        
    def set_char1_default(self):
        """캐릭터 2의 정보를 캐릭터 1로 복사 (이름 제외)"""
        # 이름은 복사하지 않음
        self.char1_awakening_var.set(self.char2_awakening_var.get())
        self.char1_cooldown_var.set(self.char2_cooldown_var.get())
        self.char1_attacks_var.set(self.char2_attacks_var.get())
        self.char1_attack_power_var.set(self.char2_attack_power_var.get())
        self.char1_critical_var.set(self.char2_critical_var.get())
        self.char1_strong_hit_var.set(self.char2_strong_hit_var.get())
        self.char1_double_shot_var.set(self.char2_double_shot_var.get())
        self.char1_triple_shot_var.set(self.char2_triple_shot_var.get())
        self.char1_critical_mult_var.set(self.char2_critical_mult_var.get())
        self.char1_strong_hit_mult_var.set(self.char2_strong_hit_mult_var.get())
        self.char1_damage_1_var.set(self.char2_damage_1_var.get())
        self.char1_damage_2_var.set(self.char2_damage_2_var.get())
        self.char1_damage_3_var.set(self.char2_damage_3_var.get())
        self.char1_critical_cd_var.set(self.char2_critical_cd_var.get())
        self.char1_skill_cd_var.set(self.char2_skill_cd_var.get())
        
    def set_char2_default(self):
        """캐릭터 1의 정보를 캐릭터 2로 복사 (이름 제외)"""
        # 이름은 복사하지 않음
        self.char2_awakening_var.set(self.char1_awakening_var.get())
        self.char2_cooldown_var.set(self.char1_cooldown_var.get())
        self.char2_attacks_var.set(self.char1_attacks_var.get())
        self.char2_attack_power_var.set(self.char1_attack_power_var.get())
        self.char2_critical_var.set(self.char1_critical_var.get())
        self.char2_strong_hit_var.set(self.char1_strong_hit_var.get())
        self.char2_double_shot_var.set(self.char1_double_shot_var.get())
        self.char2_triple_shot_var.set(self.char1_triple_shot_var.get())
        self.char2_critical_mult_var.set(self.char1_critical_mult_var.get())
        self.char2_strong_hit_mult_var.set(self.char1_strong_hit_mult_var.get())
        self.char2_damage_1_var.set(self.char1_damage_1_var.get())
        self.char2_damage_2_var.set(self.char1_damage_2_var.get())
        self.char2_damage_3_var.set(self.char1_damage_3_var.get())
        self.char2_critical_cd_var.set(self.char1_critical_cd_var.get())
        self.char2_skill_cd_var.set(self.char1_skill_cd_var.get())
    
    def create_character_from_gui(self, char_prefix):
        """GUI 입력값으로부터 Character 객체 생성"""
        try:
            char = Character(getattr(self, f"{char_prefix}_name_var").get())
            
            # 기본 설정
            char.is_awakening = getattr(self, f"{char_prefix}_awakening_var").get()
            char.is_cooldown = getattr(self, f"{char_prefix}_cooldown_var").get()
            
            # 공격 관련
            char.attacks_per_minute = int(float(getattr(self, f"{char_prefix}_attacks_var").get()))
            char.attack_power = float(getattr(self, f"{char_prefix}_attack_power_var").get())
            
            # 확률 관련
            char.p_critical = float(getattr(self, f"{char_prefix}_critical_var").get()) / 100
            char.p_strong_hit = float(getattr(self, f"{char_prefix}_strong_hit_var").get()) / 100
            char.p_double_shot = float(getattr(self, f"{char_prefix}_double_shot_var").get()) / 100
            char.p_triple_shot = float(getattr(self, f"{char_prefix}_triple_shot_var").get()) / 100
            
            # 배율 관련
            char.critical_multiplier = float(getattr(self, f"{char_prefix}_critical_mult_var").get()) / 100
            char.strong_hit_multiplier = float(getattr(self, f"{char_prefix}_strong_hit_mult_var").get()) / 100
            char.awakening_multiplier = 1.2 if char.is_awakening else 1
            
            # 데미지 배율
            char.damage_skill_1 = float(getattr(self, f"{char_prefix}_damage_1_var").get()) / 100
            char.damage_skill_2 = float(getattr(self, f"{char_prefix}_damage_2_var").get()) / 100
            char.damage_skill_3 = float(getattr(self, f"{char_prefix}_damage_3_var").get()) / 100
            
            # 쿨타임 설정
            char.critical_cooldown = float(getattr(self, f"{char_prefix}_critical_cd_var").get())
            char.skill_cooldown = float(getattr(self, f"{char_prefix}_skill_cd_var").get())
            
            # 쿨타임 감소 적용
            if char.is_cooldown:
                char.critical_cooldown *= 0.8
                char.skill_cooldown *= 0.8
                
            return char
            
        except ValueError as e:
            messagebox.showerror("입력 오류", f"숫자 입력에 오류가 있습니다: {str(e)}")
            return None
    
    def compare_damage(self):
        """데미지 비교 실행"""
        try:
            # 입력값 검증
            minutes = int(self.minutes_var.get())
            simulations = int(self.simulations_var.get())
            
            if minutes <= 0 or simulations <= 0:
                messagebox.showerror("입력 오류", "시뮬레이션 시간과 횟수는 양수여야 합니다.")
                return
                
        except ValueError:
            messagebox.showerror("입력 오류", "시뮬레이션 설정에 숫자를 입력해주세요.")
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
                # 결과를 캡처하기 위한 StringIO 사용
                import io
                import sys
                
                # 표준 출력을 캡처
                old_stdout = sys.stdout
                result_capture = io.StringIO()
                sys.stdout = result_capture
                
                # 비교 실행
                compare_characters(char1, char2, minutes, simulations)
                
                # 결과 가져오기
                result = result_capture.getvalue()
                sys.stdout = old_stdout
                
                # GUI 업데이트
                self.root.after(0, lambda: self.result_text.insert(tk.END, result))
                
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