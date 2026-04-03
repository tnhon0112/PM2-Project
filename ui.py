import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (75, 165, 95)
RED = (205, 75, 75)
BLUE = (75, 125, 210)
PANEL = (244, 244, 244)

CAM_WIDTH = 260
CAM_HEIGHT = 195
CAM_POS = (20, 20)
CALIBRATION_HOLD_FRAMES = 45
HIGH_FIVE_HOLD_FRAMES = 10


def draw_text(screen, text, font, color, x, y):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def draw_camera_preview(screen, cam_surface):
    if cam_surface is None:
        return
    screen.blit(cam_surface, CAM_POS)
    pygame.draw.rect(screen, BLACK, (CAM_POS[0], CAM_POS[1], CAM_WIDTH, CAM_HEIGHT), 2)


def show_start_ui(
    screen,
    death_count,
    points,
    get_camera_state,
    update_thresholds,
    cleanup_and_exit,
):
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

        screen.fill(WHITE)
        pygame.draw.rect(screen, PANEL, (310, 30, 760, 245), border_radius=18)
        pygame.draw.rect(screen, PANEL, (310, 295, 760, 255), border_radius=18)

        if death_count > 0:
            draw_text(screen, "Your Score: " + str(points), body_font, BLACK, 340, 70)

        if stage == "calibrate":
            draw_text(screen, "Stay In The Neutral Zone", title_font, BLACK, 340, 110)
            draw_text(screen, "Keep your face inside the gold lines to calibrate.", body_font, BLACK, 340, 165)
            draw_text(screen, "Hold still for a second so the game learns your neutral position.", body_font, BLACK, 340, 200)

            progress = min(neutral_frames / CALIBRATION_HOLD_FRAMES, 1.0)
            pygame.draw.rect(screen, WHITE, (340, 350, 420, 30), border_radius=12)
            pygame.draw.rect(screen, BLACK, (340, 350, 420, 30), 2, border_radius=12)
            pygame.draw.rect(screen, BLUE, (344, 354, int(412 * progress), 22), border_radius=10)

            status = "Good, hold still..." if camera_state["neutral_ok"] else "Move until your face is inside the neutral zone"
            color = GREEN if camera_state["neutral_ok"] else RED
            draw_text(screen, status, body_font, color, 340, 400)
            draw_text(screen, "Press R to recalibrate", small_font, BLACK, 340, 445)
        else:
            draw_text(screen, "High Five To Start", title_font, BLACK, 340, 110)
            draw_text(screen, "Raise a hand near the top of the camera to start the game.", body_font, BLACK, 340, 165)
            draw_text(screen, "This version uses OpenCV motion, so bigger hand movement works best.", body_font, BLACK, 340, 200)

            progress = min(high_five_frames / HIGH_FIVE_HOLD_FRAMES, 1.0)
            pygame.draw.rect(screen, WHITE, (340, 350, 420, 30), border_radius=12)
            pygame.draw.rect(screen, BLACK, (340, 350, 420, 30), 2, border_radius=12)
            pygame.draw.rect(screen, GREEN, (344, 354, int(412 * progress), 22), border_radius=10)

            status = "High five detected" if camera_state["high_five"] else "Waiting for hand motion near the top of the camera"
            color = GREEN if camera_state["high_five"] else RED
            draw_text(screen, status, body_font, color, 340, 400)
            draw_text(screen, "Press SPACE to skip the gesture or R to recalibrate", small_font, BLACK, 340, 445)

        if not camera_state["camera_ready"]:
            draw_text(screen, "Camera not available.", body_font, RED, 340, 500)

        draw_camera_preview(screen, camera_state["cam_surface"])
        pygame.display.update()
        clock.tick(30)
