import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import pygame
import sys
import random

# ==========================================
# CORE CONFIGURATION
# ==========================================
SPAWNS_PER_FRAME = 85  
FILE_NAME = 'PS_20174392719_1491204439457_log.csv'

# ==========================================
# 1. THE BRAIN: 80/20 Split & Math
# ==========================================
print("Loading dataset (~6.3 Million rows) - Please wait...")
try:
    df = pd.read_csv(FILE_NAME)
except FileNotFoundError:
    print(f"\n[ERROR] FILE NOT FOUND: {FILE_NAME}")
    sys.exit()

X = df[['amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']]
y = df['isFraud']

print("Splitting data: 80% Train / 20% Test...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

print("Training Decision Tree...")
model = DecisionTreeClassifier(max_depth=5, random_state=42)
model.fit(X_train, y_train)

print("Predicting on 20% Testbench...")
predictions = model.predict(X_test)

pred_list = predictions.tolist()
truth_list = y_test.tolist()
total_data_points = len(pred_list)

# --- THE NEW MATH: Count the real bad guys ---
total_frauds_in_batch = sum(truth_list)

print("System Ready. Launching UI...")

# ==========================================
# 2. THE UI SETUP
# ==========================================
pygame.init()

WIDTH, HEIGHT = 1600, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SYS.ML // FRAUD PIPELINE [TRUTH CHECK]")
clock = pygame.time.Clock()

C_BG_DARK = (8, 8, 12)           
C_BG_UI = (15, 15, 18)           
C_NEON_GREEN = (40, 255, 100)     
C_NEON_RED = (255, 60, 60)       
C_NEON_CYAN = (0, 200, 255)     
C_BELT = (45, 45, 50)           
C_PACKET_RAW = (150, 150, 160)   
C_WARNING_YELLOW = (255, 200, 50)

try:
    font_path = pygame.font.match_font('consolas, courier new, monospace')
    font_header = pygame.font.Font(font_path, 24)
    font_meter = pygame.font.Font(font_path, 22)
    font_small = pygame.font.Font(font_path, 14)
except:
    font_header = pygame.font.SysFont(None, 30)
    font_meter = pygame.font.SysFont(None, 26)
    font_small = pygame.font.SysFont(None, 18)

DASH_HEIGHT = 90
BELT_Y = HEIGHT // 2 
SCANNER_X = WIDTH // 2 - 100

SURF_PACKET_RAW = pygame.Surface((10, 5))
SURF_PACKET_RAW.fill(C_PACKET_RAW)

SURF_PACKET_SAFE = pygame.Surface((10, 5))
SURF_PACKET_SAFE.fill(C_NEON_GREEN)

RED_RADIUS = 6
SURF_PACKET_FRAUD = pygame.Surface((RED_RADIUS*2, RED_RADIUS*2), pygame.SRCALPHA)
for i in range(RED_RADIUS, 0, -1):
    alpha = int(180 * (i / RED_RADIUS))
    pygame.draw.circle(SURF_PACKET_FRAUD, (*C_NEON_RED, alpha), (RED_RADIUS, RED_RADIUS), i)
pygame.draw.circle(SURF_PACKET_FRAUD, (255, 200, 200), (RED_RADIUS, RED_RADIUS), 2)

class ConveyorPacket:
    __slots__ = ['x', 'y', 'pred_fraud', 'actual_fraud', 'speed_x', 'speed_y', 'scanned', 'ejected']

    def __init__(self, is_pred_fraud, is_actual_fraud):
        self.x = random.uniform(-200, 0)
        self.y = BELT_Y + random.uniform(-35, 35) 
        self.pred_fraud = is_pred_fraud      
        self.actual_fraud = is_actual_fraud  
        self.speed_x = random.uniform(15, 22) 
        self.speed_y = 0
        self.scanned = False
        self.ejected = False

    def update(self):
        just_scanned_trigger = False
        self.x += self.speed_x
        self.y += self.speed_y

        if not self.scanned and self.x >= SCANNER_X:
            self.scanned = True
            just_scanned_trigger = True
            if self.pred_fraud == 1:
                self.ejected = True
                self.speed_x = random.uniform(-0.5, 0.5) 
                self.speed_y = random.uniform(10, 16) 

        return just_scanned_trigger

    def draw(self, surface):
        if not self.scanned:
            surface.blit(SURF_PACKET_RAW, (int(self.x), int(self.y)))
        elif self.ejected:
            surface.blit(SURF_PACKET_FRAUD, (int(self.x) - RED_RADIUS, int(self.y) - RED_RADIUS))
        else:
            surface.blit(SURF_PACKET_SAFE, (int(self.x), int(self.y)))

# ==========================================
# 3. MAIN LOOP
# ==========================================
packets = []
data_idx = 0

count_safe_routed = 0
count_dropped = 0
count_real_frauds_caught = 0
count_real_frauds_missed = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(C_BG_DARK)

    pygame.draw.rect(screen, C_BELT, (0, BELT_Y - 45, WIDTH, 90))
    pygame.draw.line(screen, (80, 80, 90), (0, BELT_Y - 45), (WIDTH, BELT_Y - 45), 3) 
    pygame.draw.line(screen, (20, 20, 25), (0, BELT_Y + 45), (WIDTH, BELT_Y + 45), 4) 
    
    pygame.draw.rect(screen, (25, 25, 30), (SCANNER_X, BELT_Y - 90, 20, 180)) 
    pygame.draw.line(screen, C_NEON_CYAN, (SCANNER_X+10, BELT_Y-90), (SCANNER_X+10, BELT_Y+90), 2)
    pygame.draw.circle(screen, C_NEON_CYAN, (SCANNER_X+10, BELT_Y-90), 4) 

    for _ in range(SPAWNS_PER_FRAME):
        if data_idx < total_data_points:
            packets.append(ConveyorPacket(pred_list[data_idx], truth_list[data_idx]))
            data_idx += 1

    for i in range(len(packets) - 1, -1, -1):
        p = packets[i]
        just_scanned = p.update()
        
        if just_scanned:
            # Did the machine drop it?
            if p.pred_fraud == 1:
                count_dropped += 1
            else:
                count_safe_routed += 1
            
            # THE TRUTH CHECK: Was it actually a bad guy?
            if p.actual_fraud == 1:
                if p.pred_fraud == 1:
                    count_real_frauds_caught += 1
                else:
                    count_real_frauds_missed += 1
                
        p.draw(screen)
        
        if p.x > WIDTH + 20 or p.y > HEIGHT + 20:
            packets.pop(i)

    # --- Dashboard UI ---
    pygame.draw.rect(screen, C_BG_UI, (0, 0, WIDTH, DASH_HEIGHT))
    pygame.draw.line(screen, (40, 40, 50), (0, DASH_HEIGHT), (WIDTH, DASH_HEIGHT), 1) 

    col1_x, col2_x, col3_x, col4_x = 30, 350, 700, 1150
    text_y_top = 20
    text_y_bot = 50

    # 1. Scanner Actions
    screen.blit(font_small.render("ML RUNNING", True, (100, 100, 110)), (col2_x, text_y_top))
    screen.blit(font_meter.render(f"SAFE: {count_safe_routed:,}", True, C_NEON_GREEN), (col2_x, text_y_bot))
    screen.blit(font_meter.render(f"DROPPED: {count_dropped:,}", True, C_NEON_RED), (col2_x + 180, text_y_bot))

    # 2. Ground Truth Setup
    screen.blit(font_small.render("ACTUAL THREATS IN BATCH", True, (100, 100, 110)), (col3_x, text_y_top))
    screen.blit(font_meter.render(f"TOTAL: {total_frauds_in_batch:,} FRAUDS", True, C_WARNING_YELLOW), (col3_x, text_y_bot))

    # 3. The Real Test (Caught vs Missed)
    screen.blit(font_small.render("THREAT NEUTRALIZATION (RECALL)", True, (100, 100, 110)), (col4_x, text_y_top))
    screen.blit(font_meter.render(f"CAUGHT: {count_real_frauds_caught:,}", True, C_NEON_GREEN), (col4_x, text_y_bot))
    screen.blit(font_meter.render(f"SLIPPED PAST: {count_real_frauds_missed:,}", True, C_NEON_RED), (col4_x + 180, text_y_bot))

    pygame.display.flip()
    clock.tick(60) 

pygame.quit()
sys.exit()