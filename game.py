# To get access to the assets folder
import os 
# To get random numbers for obstacle generation
import random
# Import `pygame` so this file can use pygame syntax for windows, images, input, and drawing.
import pygame

# Get the camera controller class
from camera_logic import CameraController
# Get the UI Functions and constants
from ui import BLACK, WHITE, draw_camera_preview, show_start_ui

# `pygame.init()` is pygame syntax that starts the modules used by the game.
pygame.init()
# Create one shared camera controller for the whole game session.
camera_controller = CameraController()

# Global Constants ( Adjust how big and how long the screen is )
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
# `pygame.display.set_mode(...)` is pygame syntax for creating the game window.
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# `pygame.display.set_caption(...)` is pygame syntax for naming the window.
pygame.display.set_caption("Motion Controlled Horse Game")

# --- Asset Loading ---
# `pygame.image.load(...)` is pygame syntax for loading image files into surfaces.
# This list stores the running animation frames for the horse.
RUNNING = [ pygame.image.load(os.path.join("Assets/Horse", "run1.png")),
            pygame.image.load(os.path.join("Assets/Horse", "run2.png")),
            pygame.image.load(os.path.join("Assets/Horse", "run3.png")),
            pygame.image.load(os.path.join("Assets/Horse", "run4.png")),
            pygame.image.load(os.path.join("Assets/Horse", "run5.png")),
            pygame.image.load(os.path.join("Assets/Horse", "run6.png")),
            pygame.image.load(os.path.join("Assets/Horse", "run7.png")),
            pygame.image.load(os.path.join("Assets/Horse", "run8.png")),
            pygame.image.load(os.path.join("Assets/Horse", "run9.png")),
            pygame.image.load(os.path.join("Assets/Horse", "run10.png")),
            pygame.image.load(os.path.join("Assets/Horse", "run11.png")),
            pygame.image.load(os.path.join("Assets/Horse", "run12.png")),
            pygame.image.load(os.path.join("Assets/Horse", "run13.png")),
            pygame.image.load(os.path.join("Assets/Horse", "run14.png")),]

# More pygame image-loading syntax for the jump animation frames.
JUMPING = [pygame.image.load(os.path.join("Assets/Horse", "run3.png")),
           pygame.image.load(os.path.join("Assets/Horse", "run4.png")),
           pygame.image.load(os.path.join("Assets/Horse", "run13.png"))]
# More pygame image-loading syntax for the duck animation frames.
DUCKING = [pygame.image.load(os.path.join("Assets/Horse", "duck1.png")),
           pygame.image.load(os.path.join("Assets/Horse", "duck2.png"))] 

# More pygame image-loading syntax for obstacle sprite variations.
SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

# These are also pygame surfaces loaded from image files.
CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))
BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

# Shared game state values that are reset each run.
game_speed = 20
x_pos_bg = 0
y_pos_bg = 380
points = 0
obstacles = []
# Range used when placing new obstacles off-screen.
OBSTACLE_SPAWN_DISTANCE_MIN = 280
OBSTACLE_SPAWN_DISTANCE_MAX = 420



class Dinosaur:
    # Base position and collision tuning for the player character.
    X_POS = 80
    Y_POS = 225
    JUMP_VEL = 8.0
    RUN_HITBOX = (18, 12, 10)
    DUCK_HITBOX = (20, 18, 8)

    def __init__(self):
        # Store animation frame lists for each movement state.
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        # Track which movement state is active right now.
        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        # Animation and physics state for the current run.
        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        # `.get_rect()` is pygame surface syntax that creates a rectangle for positioning and collisions.
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        # Save the bottom y-position so run and duck can snap back to the ground cleanly.
        self.ground_y = self.Y_POS + self.image.get_height()

    def update(self, user_input):
        # Run the animation and movement for whichever state is currently active.
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        # Loop the animation counter so frame selection keeps repeating smoothly.
        if self.step_index >= 28:
            self.step_index = 0

        # Change state based on keyboard or camera input.
        # `pygame.K_UP` and `pygame.K_DOWN` are pygame key constants.
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
        # Alternate between ducking sprites for a short looping animation.
        self.image = self.duck_img[(self.step_index // 2) % len(self.duck_img)]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        # Keep the horse aligned with the ground even though the sprite height changes.
        self.dino_rect.bottom = self.ground_y
        self.step_index += 1

    def run(self):
        # Cycle through the running frames.
        self.image = self.run_img[(self.step_index // 2) % len(self.run_img)]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        # Keep the running sprite on the ground.
        self.dino_rect.bottom = self.ground_y
        self.step_index += 1

    def jump(self):
        # Swap jump frames as the horse moves through the jump arc.
        self.image = self.jump_img[min(self.step_index // 10, len(self.jump_img) - 1)]
        if self.dino_jump:
            # Move upward at first, then downward as velocity decreases past zero.
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        # Once the full arc is complete, reset to a neutral running state.
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL
            self.step_index = 0

    def draw(self, screen):
        # Draw the current player sprite at its current location.
        # `screen.blit(...)` is pygame drawing syntax for placing an image on the screen.
        screen.blit(self.image, (self.dino_rect.x, self.dino_rect.y))

    def _inset_rect(self, rect, hitbox):
        # Shrink the visible sprite rectangle to a tighter gameplay hitbox.
        inset_x, inset_top, inset_bottom = hitbox
        # `pygame.Rect(...)` is pygame syntax for a rectangle used in layout and collision checks.
        return pygame.Rect(
            rect.x + inset_x,
            rect.y + inset_top,
            max(1, rect.width - (inset_x * 2)),
            max(1, rect.height - inset_top - inset_bottom),
        )

    def get_collision_rect(self):
        # Use a smaller ducking hitbox when the horse is crouched.
        hitbox = self.DUCK_HITBOX if self.dino_duck and not self.dino_jump else self.RUN_HITBOX
        return self._inset_rect(self.dino_rect, hitbox)


class Cloud:
    def __init__(self):
        # Start each cloud off-screen to the right at a random height.
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        # Move the cloud left to create a sense of motion.
        self.x -= game_speed
        if self.x < -self.width:
            # Recycle the cloud once it leaves the screen.
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, screen):
        # Draw the cloud in the background.
        screen.blit(self.image, (self.x, self.y))


class Obstacle:
    # Default hitbox is the full rectangle unless a subclass overrides it.
    HITBOX = (0, 0, 0)

    def __init__(self, image, obstacle_type):
        # Save the sprite set and chosen variant for this obstacle.
        self.image = image
        self.type = obstacle_type
        # This pygame rect tracks the obstacle's position and size.
        self.rect = self.image[self.type].get_rect()
        # Spawn just off-screen so the obstacle scrolls into view naturally.
        self.rect.x = SCREEN_WIDTH + random.randint(
            OBSTACLE_SPAWN_DISTANCE_MIN,
            OBSTACLE_SPAWN_DISTANCE_MAX,
        )

    def update(self):
        # Move the obstacle left as the world scrolls.
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width and self in obstacles:
            # Remove it once it has fully passed the player.
            obstacles.remove(self)

    def draw(self, screen):
        # Draw the obstacle's current sprite.
        # Pygame uses `blit` to draw the selected obstacle image.
        screen.blit(self.image[self.type], self.rect)

    def get_collision_rect(self):
        # Use a tuned hitbox so collisions feel more fair than the raw image bounds.
        inset_x, inset_top, inset_bottom = self.HITBOX
        # Another pygame rectangle used for obstacle collision tuning.
        return pygame.Rect(
            self.rect.x + inset_x,
            self.rect.y + inset_top,
            max(1, self.rect.width - (inset_x * 2)),
            max(1, self.rect.height - inset_top - inset_bottom),
        )


class SmallCactus(Obstacle):
    # Slightly shrink the hitbox to better match the visible cactus shape.
    HITBOX = (14, 8, 6)

    def __init__(self, image):
        # Randomly pick one cactus variation.
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        # Place small cacti on the ground line.
        self.rect.y = 325


class LargeCactus(Obstacle):
    # Slightly shrink the hitbox to better match the visible cactus shape.
    HITBOX = (18, 10, 8)

    def __init__(self, image):
        # Randomly pick one cactus variation.
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        # Place large cacti a little higher because the sprite is taller.
        self.rect.y = 300


class Bird(Obstacle):
    # Tune the bird hitbox so the wings do not feel unfairly wide.
    HITBOX = (12, 10, 10)

    def __init__(self, image):
        # Birds always start with the first flap frame.
        self.type = 0
        super().__init__(image, self.type)
        # Position the bird in the air where the player must react differently.
        self.rect.y = 235
        self.index = 0

    def draw(self, screen):
        # Loop between the bird flap frames as it flies.
        if self.index >= 9:
            self.index = 0
        screen.blit(self.image[(self.index // 5) % len(self.image)], self.rect)
        self.index += 1


def main():
    # Reset all shared run state before starting a new game.
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
    # `pygame.font.Font(...)` is pygame syntax for creating a font object.
    font = pygame.font.Font("freesansbold.ttf", 20)

    def score():
        # Increase score over time and gradually raise the game speed.
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1

        # Render the live points counter in the top-right corner.
        # `font.render(...)` is pygame text-rendering syntax that returns a drawable surface.
        text = font.render("Points: " + str(points), True, BLACK)
        text_rect = text.get_rect()
        text_rect.center = (1000, 40)
        SCREEN.blit(text, text_rect)

    def background():
        # Scroll two copies of the ground image to create an endless track effect.
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        # These `blit` calls are pygame syntax for drawing the scrolling background images.
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            # Reset once the first image has fully moved off-screen.
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    while run:
        # Allow the player to close the game window at any time.
        # `pygame.event.get()` is pygame syntax for reading the event queue.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cleanup_and_exit()

        # Get movement input from the camera each frame.
        camera_state = camera_controller.get_camera_state()
        camera_input = camera_state["camera_input"]

        # Let keyboard controls work alongside the camera controls.
        # `pygame.key.get_pressed()` is pygame syntax for checking held keyboard keys.
        keys = pygame.key.get_pressed()
        camera_input[pygame.K_UP] = camera_input[pygame.K_UP] or keys[pygame.K_UP]
        camera_input[pygame.K_DOWN] = camera_input[pygame.K_DOWN] or keys[pygame.K_DOWN]

        # Clear the screen before drawing the next frame.
        SCREEN.fill(WHITE)

        # Update and draw the player.
        player.draw(SCREEN)
        player.update(camera_input)

        # Only keep one active obstacle at a time, chosen randomly.
        if len(obstacles) == 0:
            obstacle_roll = random.randint(0, 2)
            if obstacle_roll == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif obstacle_roll == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            else:
                obstacles.append(Bird(BIRD))

        # Draw each obstacle, move it, and check for collisions with the player.
        for obstacle in list(obstacles):
            obstacle.draw(SCREEN)
            obstacle.update()
            # `.colliderect(...)` is pygame rect syntax for collision detection.
            if player.get_collision_rect().colliderect(obstacle.get_collision_rect()):
                # Pause briefly, count the death, and send the player back to the menu.
                # `pygame.time.delay(...)` is pygame timing syntax for a short pause.
                pygame.time.delay(1000)
                death_count += 1
                menu(death_count)
                return

        # Draw the moving world and HUD elements.
        background()
        cloud.draw(SCREEN)
        cloud.update()
        score()
        draw_camera_preview(SCREEN, camera_state["cam_surface"])

        # Cap the frame rate and show the finished frame.
        # `clock.tick(30)` is pygame timing syntax to cap the loop at about 30 FPS.
        clock.tick(30)
        # `pygame.display.update()` is pygame syntax that shows the finished frame.
        pygame.display.update()


def menu(death_count):
    # Show the calibration / start screen before each run.
    show_start_ui(
        SCREEN,
        death_count,
        points,
        camera_controller.get_camera_state,
        camera_controller.update_thresholds,
        cleanup_and_exit,
    )
    main()


def cleanup_and_exit():
    # Release camera resources and close pygame cleanly.
    camera_controller.cleanup()
    # `pygame.quit()` is pygame syntax that shuts pygame down cleanly.
    pygame.quit()
    raise SystemExit


if __name__ == "__main__":
    # Start the menu, and make sure the camera is released even if the game exits unexpectedly.
    try:
        menu(death_count=0)
    finally:
        camera_controller.cleanup()
