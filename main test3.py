import os
import random

import cv2
import pygame

pygame.init()

# --- Camera Setup ---
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
background_subtractor = cv2.createBackgroundSubtractorMOG2(
    history=120, varThreshold=35, detectShadows=False
)

# --- Global Constants ---
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Motion Controlled Dino Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
GREEN = (75, 165, 95)
RED = (205, 75, 75)
BLUE = (75, 125, 210)
PANEL = (244, 244, 244)

CAM_WIDTH = 260
CAM_HEIGHT = 195
CAM_POS = (20, 20)
CALIBRATION_HOLD_FRAMES = 45
HIGH_FIVE_HOLD_FRAMES = 10
MIN_FACE_SIZE = 45
HIGH_FIVE_MOTION_AREA = 2500

neutral_y = 0.5
JUMP_THRESHOLD = 0.38
DUCK_THRESHOLD = 0.62

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

game_speed = 20
x_pos_bg = 0
y_pos_bg = 380
points = 0
obstacles = []


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

    def update(self, user_input):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if user_input[pygame.K_UP] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif user_input[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or user_input[pygame.K_DOWN]):
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
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, screen):
        screen.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


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

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, obstacle_type):
        self.image = image
        self.type = obstacle_type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width and self in obstacles:
            obstacles.remove(self)

    def draw(self, screen):
        screen.blit(self.image[self.type], self.rect)


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

    def draw(self, screen):
        if self.index >= 9:
            self.index = 0
        screen.blit(self.image[self.index // 5], self.rect)
        self.index += 1


def update_thresholds(new_neutral_y):
    global neutral_y, JUMP_THRESHOLD, DUCK_THRESHOLD
    neutral_y = max(0.28, min(0.72, new_neutral_y))
    JUMP_THRESHOLD = max(0.20, neutral_y - 0.12)
    DUCK_THRESHOLD = min(0.82, neutral_y + 0.12)


def detect_face(gray_frame):
    faces = face_cascade.detectMultiScale(
        gray_frame,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(MIN_FACE_SIZE, MIN_FACE_SIZE),
    )
    if len(faces) == 0:
        return None

    return max(faces, key=lambda box: box[2] * box[3])


def detect_high_five(gray_frame, face_box):
    if face_box is None:
        background_subtractor.apply(gray_frame, learningRate=0.05)
        return False, None

    x, y, w, _ = face_box
    mask = background_subtractor.apply(gray_frame, learningRate=0.01)
    _, mask = cv2.threshold(mask, 220, 255, cv2.THRESH_BINARY)
    mask = cv2.medianBlur(mask, 5)

    top_limit = max(0, y - 80)
    roi = mask[0:top_limit if top_limit > 0 else 1, :]
    if roi.size == 0:
        return False, mask

    left_bound = max(0, x - w)
    right_bound = min(mask.shape[1], x + (2 * w))
    side_roi = roi[:, left_bound:right_bound]
    motion_area = int(cv2.countNonZero(side_roi))
    return motion_area > HIGH_FIVE_MOTION_AREA, mask


def build_camera_surface(frame_bgr, face_box, face_y, motion_mask):
    frame = cv2.resize(frame_bgr, (CAM_WIDTH, CAM_HEIGHT))

    jump_line_y = int(JUMP_THRESHOLD * CAM_HEIGHT)
    duck_line_y = int(DUCK_THRESHOLD * CAM_HEIGHT)
    zone_top = min(jump_line_y, duck_line_y)
    zone_bottom = max(jump_line_y, duck_line_y)

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, zone_top), (CAM_WIDTH, zone_bottom), (180, 230, 255), -1)
    frame = cv2.addWeighted(overlay, 0.22, frame, 0.78, 0)

    if face_box is not None:
        x, y, w, h = face_box
        scale_x = CAM_WIDTH / frame_bgr.shape[1]
        scale_y = CAM_HEIGHT / frame_bgr.shape[0]
        cv2.rectangle(
            frame,
            (int(x * scale_x), int(y * scale_y)),
            (int((x + w) * scale_x), int((y + h) * scale_y)),
            (40, 160, 70),
            2,
        )

    cv2.line(frame, (0, jump_line_y), (CAM_WIDTH, jump_line_y), (0, 215, 255), 2)
    cv2.line(frame, (0, duck_line_y), (CAM_WIDTH, duck_line_y), (0, 215, 255), 2)
    cv2.putText(
        frame,
        "Neutral Zone",
        (8, max(zone_top - 10, 18)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 80, 120),
        1,
        cv2.LINE_AA,
    )

    if face_y is not None:
        cv2.circle(frame, (CAM_WIDTH - 16, int(face_y * CAM_HEIGHT)), 7, (50, 70, 220), -1)

    if motion_mask is not None:
        small_mask = cv2.resize(motion_mask, (CAM_WIDTH // 4, CAM_HEIGHT // 4))
        small_mask_bgr = cv2.cvtColor(small_mask, cv2.COLOR_GRAY2BGR)
        frame[CAM_HEIGHT - small_mask_bgr.shape[0]:CAM_HEIGHT, CAM_WIDTH - small_mask_bgr.shape[1]:CAM_WIDTH] = small_mask_bgr

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.transpose(frame)
    return pygame.surfarray.make_surface(frame)


def get_camera_state():
    ret, frame = cap.read()
    camera_input = {pygame.K_UP: False, pygame.K_DOWN: False}
    if not ret:
        return {
            "camera_input": camera_input,
            "cam_surface": None,
            "face_y": None,
            "neutral_ok": False,
            "high_five": False,
            "camera_ready": False,
        }

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    face_box = detect_face(gray)
    face_y = None
    if face_box is not None:
        _, y, _, h = face_box
        face_y = (y + (h / 2)) / gray.shape[0]

    if face_y is not None:
        if face_y < JUMP_THRESHOLD:
            camera_input[pygame.K_UP] = True
        elif face_y > DUCK_THRESHOLD:
            camera_input[pygame.K_DOWN] = True

    high_five, motion_mask = detect_high_five(gray, face_box)
    cam_surface = build_camera_surface(frame, face_box, face_y, motion_mask)

    return {
        "camera_input": camera_input,
        "cam_surface": cam_surface,
        "face_y": face_y,
        "neutral_ok": face_y is not None and JUMP_THRESHOLD <= face_y <= DUCK_THRESHOLD,
        "high_five": high_five,
        "camera_ready": True,
    }


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

    title_font = pygame.font.Font("freesansbold.ttf", 32)
    body_font = pygame.font.Font("freesansbold.ttf", 22)
    small_font = pygame.font.Font("freesansbold.ttf", 18)
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
                samples.append(camera_state["face_y"])
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
            draw_text("Keep your face inside the gold lines to calibrate.", body_font, BLACK, 340, 165)
            draw_text("Hold still for a second so the game learns your neutral position.", body_font, BLACK, 340, 200)

            progress = min(neutral_frames / CALIBRATION_HOLD_FRAMES, 1.0)
            pygame.draw.rect(SCREEN, WHITE, (340, 350, 420, 30), border_radius=12)
            pygame.draw.rect(SCREEN, BLACK, (340, 350, 420, 30), 2, border_radius=12)
            pygame.draw.rect(SCREEN, BLUE, (344, 354, int(412 * progress), 22), border_radius=10)

            status = "Good, hold still..." if camera_state["neutral_ok"] else "Move until your face is inside the neutral zone"
            color = GREEN if camera_state["neutral_ok"] else RED
            draw_text(status, body_font, color, 340, 400)
            draw_text("Press R to recalibrate", small_font, BLACK, 340, 445)
        else:
            draw_text("High Five To Start", title_font, BLACK, 340, 110)
            draw_text("Raise a hand near the top of the camera to start the game.", body_font, BLACK, 340, 165)
            draw_text("This version uses OpenCV motion, so bigger hand movement works best.", body_font, BLACK, 340, 200)

            progress = min(high_five_frames / HIGH_FIVE_HOLD_FRAMES, 1.0)
            pygame.draw.rect(SCREEN, WHITE, (340, 350, 420, 30), border_radius=12)
            pygame.draw.rect(SCREEN, BLACK, (340, 350, 420, 30), 2, border_radius=12)
            pygame.draw.rect(SCREEN, GREEN, (344, 354, int(412 * progress), 22), border_radius=10)

            status = "High five detected" if camera_state["high_five"] else "Waiting for hand motion near the top of the camera"
            color = GREEN if camera_state["high_five"] else RED
            draw_text(status, body_font, color, 340, 400)
            draw_text("Press SPACE to skip the gesture or R to recalibrate", small_font, BLACK, 340, 445)

        if not camera_state["camera_ready"]:
            draw_text("Camera not available.", body_font, RED, 340, 500)

        draw_camera_preview(camera_state["cam_surface"])
        pygame.display.update()
        clock.tick(30)


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
    obstacles = []
    death_count = 0
    font = pygame.font.Font("freesansbold.ttf", 20)

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1

        text = font.render("Points: " + str(points), True, BLACK)
        text_rect = text.get_rect()
        text_rect.center = (1000, 40)
        SCREEN.blit(text, text_rect)

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

        keys = pygame.key.get_pressed()
        camera_input[pygame.K_UP] = camera_input[pygame.K_UP] or keys[pygame.K_UP]
        camera_input[pygame.K_DOWN] = camera_input[pygame.K_DOWN] or keys[pygame.K_DOWN]

        SCREEN.fill(WHITE)

        player.draw(SCREEN)
        player.update(camera_input)

        if len(obstacles) == 0:
            obstacle_roll = random.randint(0, 2)
            if obstacle_roll == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif obstacle_roll == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            else:
                obstacles.append(Bird(BIRD))

        for obstacle in list(obstacles):
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                pygame.time.delay(1000)
                death_count += 1
                menu(death_count)
                return

        background()
        cloud.draw(SCREEN)
        cloud.update()
        score()
        draw_camera_preview(camera_state["cam_surface"])

        clock.tick(30)
        pygame.display.update()


def menu(death_count):
    show_start_ui(death_count)
    main()


def cleanup_and_exit():
    if cap.isOpened():
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
