import pygame
import sys
import random

# 1. 초기화 및 상수가 지정된 환경 설정
pygame.init()
WIDTH, HEIGHT = 800, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mega Rhythm Hero 2026")
clock = pygame.time.Clock()

# 색상 팔레트
BLACK  = (15, 15, 20)
WHITE  = (240, 240, 240)
GRAY   = (60, 60, 70)
LINE_COLOR = (100, 100, 120)
NOTE_COLORS = [(255, 90, 90), (90, 150, 255), (90, 150, 255), (255, 90, 90)] # 레인별 색상
EFFECT_COLOR = (255, 255, 100)

# 게임 플레이 관련 상수
LANES = [200, 300, 400, 500]
KEYS = [pygame.K_s, pygame.K_d, pygame.K_k, pygame.K_l]
JUDGMENT_LINE = 580

# 2. 오브젝트 클래스 설계
class Note:
    """화면 위에서 아래로 떨어지는 노트 객체"""
    def __init__(self, lane):
        self.lane = lane
        self.x = LANES[lane]
        self.y = -50
        self.width = 90
        self.height = 25
        self.speed = 7
        self.is_alive = True

    def move(self):
        self.y += self.speed
        if self.y > HEIGHT: # 화면 밖으로 벗어나면 MISS 처리용
            self.is_alive = False

    def draw(self, surface):
        if self.is_alive:
            pygame.draw.rect(surface, NOTE_COLORS[self.lane], (self.x + 5, self.y, self.width, self.height), border_radius=5)

class Effect:
    """노트를 맞췄을 때 뿜어져 나오는 콤보 및 판정 텍스트 이펙트"""
    def __init__(self, text, lane=None):
        self.text = text
        self.lane = lane
        self.timer = 20 # 이펙트가 유지될 프레임 수
        self.y_offset = 0

    def update(self):
        self.timer -= 1
        self.y_offset -= 1 # 위로 스르륵 올라가는 효과

    def draw(self, surface, font, combo_font):
        if self.timer > 0:
            if self.lane is not None: # PERFECT / MISS 판정
                txt_surf = font.render(self.text, True, EFFECT_COLOR if self.text == "PERFECT" else (255, 50, 50))
                surface.blit(txt_surf, (LANES[self.lane] + 10, JUDGMENT_LINE - 40 + self.y_offset))
            else: # 대형 콤보 표시
                txt_surf = combo_font.render(self.text, True, WHITE)
                surface.blit(txt_surf, (WIDTH // 2 - txt_surf.get_width() // 2, 250 + self.y_offset))

# 3. 게임 매니저 및 메인 루프 변수
notes = []
effects = []
score = 0
combo = 0
max_combo = 0
key_pressed = [False, False, False, False]

# 폰트 세팅
font = pygame.font.SysFont("comicsansms", 25)
combo_font = pygame.font.SysFont("impact", 60)
ui_font = pygame.font.SysFont("arial", 22)

# 노트 생성을 위한 타이머 이벤트 세팅 (0.4초마다 노트 생성 찬스)
NOTE_SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(NOTE_SPAWN_EVENT, 400)

# 메인 게임 루프
while True:
    screen.fill(BLACK)
    
    # --- 이벤트 핸들링 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        # 노트 자동 생성 호출
        if event.type == NOTE_SPAWN_EVENT:
            # 70% 확률로 노트 생성, 동시에 여러 라인에도 생성 가능하도록 세팅
            for i in range(4):
                if random.random() < 0.25:
                    notes.append(Note(i))
                    
        # 키보드를 누르는 순간 (HIT 판정 체크)
        if event.type == pygame.KEYDOWN:
            for i in range(4):
                if event.key == KEYS[i]:
                    key_pressed[i] = True
                    hit = False
                    
                    # 가장 아래에 있는 노트부터 판정 영역에 있는지 검사
                    for note in notes:
                        if note.lane == i and abs(note.y - JUDGMENT_LINE) < 45:
                            # 판정 성공 (PERFECT)
                            score += 150 + (combo * 2) # 콤보 보너스 스코어 적용
                            combo += 1
                            max_combo = max(max_combo, combo)
                            effects.append(Effect("PERFECT", i))
                            effects.append(Effect(f"{combo} COMBO"))
                            notes.remove(note)
                            hit = True
                            break
                    
                    # 공중에 대고 헛손질 한 경우 콤보 깨짐
                    if not hit:
                        pass # 리듬게임 특성상 빈 공간 연타는 보통 무시하거나 소량의 감점 가능
                            
        if event.type == pygame.KEYUP:
            for i in range(4):
                if event.key == KEYS[i]:
                    key_pressed[i] = False

    # --- 데이터 업데이트 (이동 및 소멸 처리) ---
    for note in notes[:]:
        note.move()
        # 노트를 치지 못하고 아래로 완전히 놓쳤을 때 (MISS)
        if not note.is_alive:
            combo = 0 # 콤보 초기화
            effects.append(Effect("MISS", note.lane))
            notes.remove(note)

    for effect in effects[:]:
        effect.update()
        if effect.timer <= 0:
            effects.remove(effect)

    # --- 화면 그리기 (렌더링) ---
    # 1. 배경 레인 가이드라인 및 판정선
    pygame.draw.line(screen, LINE_COLOR, (150, JUDGMENT_LINE), (650, JUDGMENT_LINE), 6)
    for i, x in enumerate(LANES):
        # 기둥 그리기
        pygame.draw.rect(screen, GRAY, (x, 0, 100, HEIGHT), 1)
        # 키를 누르고 있을 때 레인 하단에 불 들어오는 효과
        if key_pressed[i]:
            sub_surf = pygame.Surface((100, HEIGHT - JUDGMENT_LINE), pygame.SRCALPHA)
            sub_surf.fill((255, 255, 255, 40)) # 반투명 화이트 효과
            screen.blit(sub_surf, (x, JUDGMENT_LINE))

    # 2. 노트 및 이펙트 그리기
    for note in notes:
        note.draw(screen)
        
    for effect in effects:
        effect.draw(screen, font, combo_font)

    # 3. UI (점수, 콤보, 키 가이드) 표시
    score_txt = ui_font.render(f"SCORE: {score:,}", True, WHITE)
    max_combo_txt = ui_font.render(f"MAX COMBO: {max_combo}", True, LINE_COLOR)
    screen.blit(score_txt, (30, 30))
    screen.blit(max_combo_txt, (30, 65))
    
    # 하단 키 가이드 텍스트 (S D K L)
    key_guide = ["S", "D", "K", "L"]
    for i, x in enumerate(LANES):
        guide_txt = font.render(key_guide[i], True, WHITE if key_pressed[i] else GRAY)
        screen.blit(guide_txt, (x + 42, JUDGMENT_LINE + 15))

    # 화면 업데이트 및 프레임 제한
    pygame.display.flip()
    clock.tick(60)