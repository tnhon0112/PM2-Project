import pygame

# Basic colors used across the game's interface.
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (75, 165, 95)
RED = (205, 75, 75)
BLUE = (75, 125, 210)
PANEL = (244, 244, 244)

# Camera preview panel layout and gesture timing settings.
CAM_WIDTH = 260
CAM_HEIGHT = 195
CAM_POS = (20, 20)
CALIBRATION_HOLD_FRAMES = 45
HIGH_FIVE_HOLD_FRAMES = 10


def draw_text(screen, text, font, color, x, y):
    # `font.render(...)` and `screen.blit(...)` are pygame syntax for drawing text.
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def draw_camera_preview(screen, cam_surface):
    # Skip drawing if the camera preview is not available.
    if cam_surface is None:
        return
    # `blit` and `pygame.draw.rect(...)` are pygame drawing syntax.
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
    # `pygame.font.Font(...)` and `pygame.time.Clock()` are pygame setup syntax for UI text and timing.
    title_font = pygame.font.Font("freesansbold.ttf", 32)
    body_font = pygame.font.Font("freesansbold.ttf", 22)
    small_font = pygame.font.Font("freesansbold.ttf", 18)
    clock = pygame.time.Clock()

    # Start in calibration mode so the game can learn the player's neutral pose.
    stage = "calibrate"
    neutral_frames = 0
    high_five_frames = 0
    samples = []
    # Reset thresholds to their default values before recalibrating.
    update_thresholds(0.5)

    while True:
        # `pygame.event.get()` and the event constants below are pygame event-handling syntax.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cleanup_and_exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Restart calibration from scratch.
                    stage = "calibrate"
                    neutral_frames = 0
                    high_five_frames = 0
                    samples = []
                    update_thresholds(0.5)
                if event.key == pygame.K_SPACE and stage == "start":
                    # Let the player skip the gesture once calibration is complete.
                    return

        # Pull the latest camera information from the game camera controller.
        camera_state = get_camera_state()

        if stage == "calibrate":
            # Count how long the player's face stays inside the neutral zone.
            if camera_state["neutral_ok"]:
                neutral_frames += 1
                samples.append(camera_state["face_y"])
            else:
                # Reset progress if the player moves outside the target area.
                neutral_frames = 0
                samples = []

            if neutral_frames >= CALIBRATION_HOLD_FRAMES and samples:
                # Use the average captured face position as the calibrated neutral line.
                update_thresholds(sum(samples) / len(samples))
                stage = "start"
                high_five_frames = 0
        else:
            # After calibration, wait until the player holds a high-five gesture long enough.
            if camera_state["high_five"]:
                high_five_frames += 1
            else:
                high_five_frames = 0

            if high_five_frames >= HIGH_FIVE_HOLD_FRAMES:
                # Start the game once the gesture is confirmed.
                return

        # `screen.fill(...)` and `pygame.draw.rect(...)` are pygame drawing syntax for the menu panels.
        screen.fill(WHITE)
        pygame.draw.rect(screen, PANEL, (310, 30, 760, 245), border_radius=18)
        pygame.draw.rect(screen, PANEL, (310, 295, 760, 255), border_radius=18)

        # Show the previous score after a death.
        if death_count > 0:
            draw_text(screen, "Your Score: " + str(points), body_font, BLACK, 340, 70)

        if stage == "calibrate":
            # The rectangles below are pygame shape-drawing syntax used for the progress bar.
            draw_text(screen, "Stay In The Neutral Zone", title_font, BLACK, 340, 110)
            draw_text(screen, "Keep your face inside the gold lines to calibrate.", body_font, BLACK, 340, 165)
            draw_text(screen, "Hold still for a second so the game learns your neutral position.", body_font, BLACK, 340, 200)

            progress = min(neutral_frames / CALIBRATION_HOLD_FRAMES, 1.0)
            pygame.draw.rect(screen, WHITE, (340, 350, 420, 30), border_radius=12)
            pygame.draw.rect(screen, BLACK, (340, 350, 420, 30), 2, border_radius=12)
            pygame.draw.rect(screen, BLUE, (344, 354, int(412 * progress), 22), border_radius=10)

            # Update the status message based on whether the player is correctly positioned.
            status = "Good, hold still..." if camera_state["neutral_ok"] else "Move until your face is inside the neutral zone"
            color = GREEN if camera_state["neutral_ok"] else RED
            draw_text(screen, status, body_font, color, 340, 400)
            draw_text(screen, "Press R to recalibrate", small_font, BLACK, 340, 445)
        else:
            # This screen also uses pygame rectangle-drawing syntax for the gesture progress bar.
            draw_text(screen, "High Five To Start", title_font, BLACK, 340, 110)
            draw_text(screen, "Raise a hand near the top of the camera to start the game.", body_font, BLACK, 340, 165)
            draw_text(screen, "This version uses OpenCV motion, so bigger hand movement works best.", body_font, BLACK, 340, 200)

            progress = min(high_five_frames / HIGH_FIVE_HOLD_FRAMES, 1.0)
            pygame.draw.rect(screen, WHITE, (340, 350, 420, 30), border_radius=12)
            pygame.draw.rect(screen, BLACK, (340, 350, 420, 30), 2, border_radius=12)
            pygame.draw.rect(screen, GREEN, (344, 354, int(412 * progress), 22), border_radius=10)

            # Let the player know whether the gesture is currently being detected.
            status = "High five detected" if camera_state["high_five"] else "Waiting for hand motion near the top of the camera"
            color = GREEN if camera_state["high_five"] else RED
            draw_text(screen, status, body_font, color, 340, 400)
            draw_text(screen, "Press SPACE to skip the gesture or R to recalibrate", small_font, BLACK, 340, 445)

        # Warn the player if the camera is unavailable.
        if not camera_state["camera_ready"]:
            draw_text(screen, "Camera not available.", body_font, RED, 340, 500)

        # `pygame.display.update()` and `clock.tick(...)` are pygame syntax for presenting frames at a steady rate.
        draw_camera_preview(screen, camera_state["cam_surface"])
        pygame.display.update()
        clock.tick(30)
