import pygame
import os
import random
import cv2
import mediapipe as mp

pygame.init()

# --- MediaPipe & Camera Setup ---
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)

# --- Global Constants ---
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Motion Controlled Dino Game")

# --- Asset Loading ---
RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

#Cái này là làm UI Calibrate nha 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
GREEN = (80, 170, 90)
RED = (200, 70, 70)
BLUE = (70, 130, 210)
PANEL = (242, 242, 242)

CAM_WIDTH = 260
CAM_HEIGHT = 195
CAM_POS = (20, 20)
CALIBRATION_HOLD_FRAMES = 45
HIGH_FIVE_HOLD_FRAMES = 12
#Tới đây nè

neutral_y = 0.5
JUMP_THRESHOLD = 0.38
DUCK_THRESHOLD = 0.62


# --- Classes ---
class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if userInput[pygame.K_UP] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < - self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 250
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index//5], self.rect)
        self.index += 1


def update_thresholds(new_neutral_y):
    global neutral_y, JUMP_THRESHOLD, DUCK_THRESHOLD
    neutral_y = max(0.28, min(0.72, new_neutral_y))
    JUMP_THRESHOLD = max(0.20, neutral_y - 0.12)
    DUCK_THRESHOLD = min(0.82, neutral_y + 0.12)


def get_eye_y(results):
    if not results or not results.pose_landmarks:
        return None

    left_eye_y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_EYE].y
    right_eye_y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EYE].y
    return (left_eye_y + right_eye_y) / 2


def detect_high_five(results):
    if not results or not results.pose_landmarks:
        return False

    landmarks = results.pose_landmarks.landmark
    nose_y = landmarks[mp_pose.PoseLandmark.NOSE].y
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

    left_high = (
        left_wrist.visibility > 0.5
        and left_wrist.y < nose_y - 0.05
        and abs(left_wrist.x - left_shoulder.x) > 0.05
    )
    right_high = (
        right_wrist.visibility > 0.5
        and right_wrist.y < nose_y - 0.05
        and abs(right_wrist.x - right_shoulder.x) > 0.05
    )
    return left_high or right_high


def get_camera_state():
    ret, frame = cap.read()
    camera_input = {pygame.K_UP: False, pygame.K_DOWN: False}

    if not ret:
        return {
            "camera_input": camera_input,
            "cam_surface": None,
            "eye_y": None,
            "neutral_ok": False,
            "high_five": False,
            "camera_ready": False,
        }

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)
    eye_y = get_eye_y(results)

    if eye_y is not None:
        if eye_y < JUMP_THRESHOLD:
            camera_input[pygame.K_UP] = True
        elif eye_y > DUCK_THRESHOLD:
            camera_input[pygame.K_DOWN] = True

    cam_surface = build_camera_surface(rgb_frame, results, eye_y)

    return {
        "camera_input": camera_input,
        "cam_surface": cam_surface,
        "eye_y": eye_y,
        "neutral_ok": eye_y is not None and JUMP_THRESHOLD <= eye_y <= DUCK_THRESHOLD,
        "high_five": detect_high_five(results),
        "camera_ready": True,
    }


def build_camera_surface(rgb_frame, results, eye_y):
    frame = cv2.resize(rgb_frame, (CAM_WIDTH, CAM_HEIGHT))
    overlay = frame.copy()

    jump_line_y = int(JUMP_THRESHOLD * CAM_HEIGHT)
    duck_line_y = int(DUCK_THRESHOLD * CAM_HEIGHT)
    zone_top = min(jump_line_y, duck_line_y)
    zone_bottom = max(jump_line_y, duck_line_y)

    cv2.rectangle(overlay, (0, zone_top), (CAM_WIDTH, zone_bottom), (255, 240, 170), -1)
    frame = cv2.addWeighted(overlay, 0.28, frame, 0.72, 0)

    if results and results.pose_landmarks:
        mp.solutions.drawing_utils.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
        )

    cv2.line(frame, (0, jump_line_y), (CAM_WIDTH, jump_line_y), GOLD, 2)
    cv2.line(frame, (0, duck_line_y), (CAM_WIDTH, duck_line_y), GOLD, 2)
    cv2.putText(frame, "Neutral Zone", (10, max(zone_top - 10, 18)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 60, 0), 1, cv2.LINE_AA)

    if eye_y is not None:
        cv2.circle(frame, (CAM_WIDTH - 16, int(eye_y * CAM_HEIGHT)), 7, RED, -1)

    frame = cv2.transpose(frame)
    return pygame.surfarray.make_surface(frame)


def draw_text(text, font, color, x, y):
    surface = font.render(text, True, color)
    SCREEN.blit(surface, (x, y))


def draw_camera_preview(cam_surface):
    if cam_surface is None:
        return
    SCREEN.blit(cam_surface, CAM_POS)
    pygame.draw.rect(SCREEN, BLACK, (CAM_POS[0], CAM_POS[1], CAM_WIDTH, CAM_HEIGHT), 2)


def show_start_ui(death_count):
    global points

    title_font = pygame.font.Font('freesansbold.ttf', 32)
    body_font = pygame.font.Font('freesansbold.ttf', 22)
    small_font = pygame.font.Font('freesansbold.ttf', 18)
    clock = pygame.time.Clock()

    stage = "calibrate"
    neutral_frames = 0
    high_five_frames = 0
    samples = []
    update_thresholds(0.5)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cleanup_and_exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    stage = "calibrate"
                    neutral_frames = 0
                    high_five_frames = 0
                    samples = []
                    update_thresholds(0.5)
                if event.key == pygame.K_SPACE and stage == "start":
                    return

        camera_state = get_camera_state()

        if stage == "calibrate":
            if camera_state["neutral_ok"]:
                neutral_frames += 1
                samples.append(camera_state["eye_y"])
            else:
                neutral_frames = 0
                samples = []

            if neutral_frames >= CALIBRATION_HOLD_FRAMES and samples:
                update_thresholds(sum(samples) / len(samples))
                stage = "start"
                high_five_frames = 0

        else:
            if camera_state["high_five"]:
                high_five_frames += 1
            else:
                high_five_frames = 0

            if high_five_frames >= HIGH_FIVE_HOLD_FRAMES:
                return

        SCREEN.fill(WHITE)
        pygame.draw.rect(SCREEN, PANEL, (310, 30, 760, 245), border_radius=18)
        pygame.draw.rect(SCREEN, PANEL, (310, 295, 760, 255), border_radius=18)

        if death_count > 0:
            draw_text("Your Score: " + str(points), body_font, BLACK, 340, 70)

        if stage == "calibrate":
            draw_text("Stay In The Neutral Zone", title_font, BLACK, 340, 110)
            draw_text("Keep your head between the gold lines to calibrate.", body_font, BLACK, 340, 165)
            draw_text("Hold still for a moment and the game will lock your neutral pose.", body_font, BLACK, 340, 200)

            progress = min(neutral_frames / CALIBRATION_HOLD_FRAMES, 1.0)
            pygame.draw.rect(SCREEN, WHITE, (340, 350, 420, 30), border_radius=12)
            pygame.draw.rect(SCREEN, BLACK, (340, 350, 420, 30), 2, border_radius=12)
            pygame.draw.rect(SCREEN, BLUE, (344, 354, int(412 * progress), 22), border_radius=10)

            status = "Good, hold still..." if camera_state["neutral_ok"] else "Move until your eyes are inside the neutral zone"
            color = GREEN if camera_state["neutral_ok"] else RED
            draw_text(status, body_font, color, 340, 400)
            draw_text("Press R to reset calibration", small_font, BLACK, 340, 445)
        else:
            draw_text("High Five To Start", title_font, BLACK, 340, 110)
            draw_text("Raise one hand above your head like a high five.", body_font, BLACK, 340, 165)
            draw_text("Press SPACE to skip the gesture or R to recalibrate.", body_font, BLACK, 340, 200)

            progress = min(high_five_frames / HIGH_FIVE_HOLD_FRAMES, 1.0)
            pygame.draw.rect(SCREEN, WHITE, (340, 350, 420, 30), border_radius=12)
            pygame.draw.rect(SCREEN, BLACK, (340, 350, 420, 30), 2, border_radius=12)
            pygame.draw.rect(SCREEN, GREEN, (344, 354, int(412 * progress), 22), border_radius=10)

            status = "High five detected" if camera_state["high_five"] else "Waiting for your high five"
            color = GREEN if camera_state["high_five"] else RED
            draw_text(status, body_font, color, 340, 400)

        if not camera_state["camera_ready"]:
            draw_text("Camera not available.", body_font, RED, 340, 500)

        draw_camera_preview(camera_state["cam_surface"])
        pygame.display.update()
        clock.tick(30)


# --- Main Game Functions ---
def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font('freesansbold.ttf', 20)
    obstacles = []
    death_count = 0

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1

        text = font.render("Points: " + str(points), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (1000, 40)
        SCREEN.blit(text, textRect)

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cleanup_and_exit()

        camera_state = get_camera_state()
        camera_input = camera_state["camera_input"]
        cam_surface = camera_state["cam_surface"]

        keys = pygame.key.get_pressed()
        camera_input[pygame.K_UP] = camera_input[pygame.K_UP] or keys[pygame.K_UP]
        camera_input[pygame.K_DOWN] = camera_input[pygame.K_DOWN] or keys[pygame.K_DOWN]

        SCREEN.fill(WHITE)

        player.draw(SCREEN)
        player.update(camera_input)

        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif random.randint(0, 2) == 2:
                obstacles.append(Bird(BIRD))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                pygame.time.delay(1000)
                death_count += 1
                menu(death_count)

        background()
        cloud.draw(SCREEN)
        cloud.update()
        score()

        draw_camera_preview(cam_surface)

        clock.tick(30)
        pygame.display.update()


def menu(death_count):
    show_start_ui(death_count)
    main()


def cleanup_and_exit():
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    raise SystemExit


if __name__ == "__main__":
    try:
        menu(death_count=0)
    finally:
        if cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()
