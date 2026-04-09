# `os` is Python's standard library for file and folder paths.
import os 
# `random` is Python's standard library for choosing random values.
import random    
# `pygame` is the game library used for windows, images, input, fonts, timing, and drawing.
import pygame

# Import the custom camera controller class from your own project file.
from camera_logic import CameraController
# Import UI helpers and shared colors from your own project file.
from ui import BLACK, WHITE, draw_camera_preview, show_start_ui

# `pygame.init()` is pygame syntax that starts the pygame modules used by the game.
pygame.init()

# Create one camera controller object so the whole game can share the webcam logic.
camera_controller = CameraController()

# Global constants that control the size of the game window.
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
# `pygame.display.set_mode(...)` is pygame syntax for creating the main game window.
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# `pygame.display.set_caption(...)` is pygame syntax for naming the window.
pygame.display.set_caption("Motion Controlled Horse Game")


# Global game-state variables that get reset when a new run starts.
game_speed = 20
x_pos_bg = 0
y_pos_bg = 380
points = 0
obstacles = []
# Random distance range used when placing new obstacles off-screen.
OBSTACLE_SPAWN_DISTANCE_MIN = 280
OBSTACLE_SPAWN_DISTANCE_MAX = 420


# --- Asset Loading ---
# `pygame.image.load(...)` is pygame syntax for loading an image file into a surface.
# This list holds the running animation frames for the horse.
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

# More pygame image-loading syntax for the jump frames.
JUMPING = [pygame.image.load(os.path.join("Assets/Horse", "run3.png")),
           pygame.image.load(os.path.join("Assets/Horse", "run4.png")),
           pygame.image.load(os.path.join("Assets/Horse", "run13.png"))]
# More pygame image-loading syntax for the duck frames.
DUCKING = [pygame.image.load(os.path.join("Assets/Horse", "duck1.png")),
           pygame.image.load(os.path.join("Assets/Horse", "duck2.png"))] 

# Pygame image-loading syntax for the small cactus obstacle variations.
SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
# Pygame image-loading syntax for the large cactus obstacle variations.
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

# Pygame image-loading syntax for the bird flap animation.
BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

# Background decoration images loaded as pygame surfaces.
CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))
BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))





class Horse:
    # Class constants that define the player's starting position and hitbox tuning.
    X_POS = 80
    Y_POS = 225
    JUMP_VEL = 8.0
    RUN_HITBOX = (18, 12, 10)
    DUCK_HITBOX = (20, 18, 8)

    def __init__(self):
        # Save the animation frame lists that this player object will use.
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        # Booleans that track the current movement state.
        self.horse_duck = False
        self.horse_run = True
        self.horse_jump = False

        # Variables that track animation progress and jump physics.
        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        # `.get_rect()` is pygame surface syntax that creates a rectangle for positioning and collisions.
        self.horse_rect = self.image.get_rect()
        self.horse_rect.x = self.X_POS
        self.horse_rect.y = self.Y_POS
        # Save the bottom y-position so run and duck can snap back to the ground cleanly.
        self.ground_y = self.Y_POS + self.image.get_height()

    def update(self, user_input):
        # Run the animation and movement for whichever state is currently active.
        if self.horse_duck:
            self.duck()
        if self.horse_run:
            self.run()
        if self.horse_jump:
            self.jump()

        # Loop the animation counter so frame selection keeps repeating smoothly.
        if self.step_index >= 28:
            self.step_index = 0

        # Change state based on keyboard or camera input.
        # `pygame.K_UP` and `pygame.K_DOWN` are pygame key constants.
        if user_input[pygame.K_UP] and not self.horse_jump:
            self.horse_duck = False
            self.horse_run = False
            self.horse_jump = True
        elif user_input[pygame.K_DOWN] and not self.horse_jump:
            self.horse_duck = True
            self.horse_run = False
            self.horse_jump = False
        elif not (self.horse_jump or user_input[pygame.K_DOWN]):
            self.horse_duck = False
            self.horse_run = True
            self.horse_jump = False
            

    def duck(self):
        # Alternate between ducking sprites for a short looping animation.
        self.image = self.duck_img[(self.step_index // 2) % len(self.duck_img)]
        self.horse_rect = self.image.get_rect()
        self.horse_rect.x = self.X_POS
        # Keep the horse aligned with the ground even though the sprite height changes.
        self.horse_rect.bottom = self.ground_y
        self.step_index += 1

    def run(self):
        # Choose a running frame based on the animation counter.
        self.image = self.run_img[(self.step_index // 2) % len(self.run_img)]
        # `.get_rect()` is pygame syntax for getting a rectangle that matches the image size.
        self.horse_rect = self.image.get_rect()
        self.horse_rect.x = self.X_POS
        # Keep the running sprite aligned with the ground.
        self.horse_rect.bottom = self.ground_y
        self.step_index += 1

    def jump(self):
        # Pick a jump frame based on how far the jump animation has progressed.
        self.image = self.jump_img[min(self.step_index // 10, len(self.jump_img) - 1)]
        if self.horse_jump:
            # Move the player up or down by changing the pygame rect's y-position.
            self.horse_rect.y -= self.jump_vel * 4
            # Decrease jump velocity each frame to create gravity-like motion.
            self.jump_vel -= 0.8
        # Reset jump values after the player lands.
        if self.jump_vel < -self.JUMP_VEL:
            self.horse_jump = False
            self.jump_vel = self.JUMP_VEL
            self.step_index = 0

    def draw(self, screen):
        # `screen.blit(...)` is pygame drawing syntax for drawing the player image.
        screen.blit(self.image, (self.horse_rect.x, self.horse_rect.y))

    def _inset_rect(self, rect, hitbox):
        # Unpack the hitbox tuple into left/right and top/bottom inset values.
        inset_x, inset_top, inset_bottom = hitbox
        # `pygame.Rect(...)` is pygame syntax for making a smaller collision rectangle.
        return pygame.Rect(
            rect.x + inset_x,
            rect.y + inset_top,
            max(1, rect.width - (inset_x * 2)),
            max(1, rect.height - inset_top - inset_bottom),
        )

    def get_collision_rect(self):
        # Use the duck hitbox when crouching, otherwise use the run hitbox.
        hitbox = self.DUCK_HITBOX if self.horse_duck and not self.horse_jump else self.RUN_HITBOX
        return self._inset_rect(self.horse_rect, hitbox)


class Cloud:
    def __init__(self):
        # Start the cloud off-screen to the right with a random height.
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        # Move the cloud left as the world scrolls.
        self.x -= game_speed
        if self.x < -self.width:
            # When the cloud leaves the screen, recycle it farther to the right.
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, screen):
        # Draw the cloud image using pygame blit syntax.
        screen.blit(self.image, (self.x, self.y))


class Obstacle:
    # Default hitbox tuple; subclasses override this to better match their shape.
    HITBOX = (0, 0, 0)

    def __init__(self, image, obstacle_type):
        # Save the sprite list and selected sprite index for this obstacle object.
        self.image = image
        self.type = obstacle_type
        # `.get_rect()` creates a pygame rectangle for positioning the obstacle.
        self.rect = self.image[self.type].get_rect()
        # Spawn each obstacle a little off-screen so it scrolls in naturally.
        self.rect.x = SCREEN_WIDTH + random.randint(
            OBSTACLE_SPAWN_DISTANCE_MIN,
            OBSTACLE_SPAWN_DISTANCE_MAX,
        )

    def update(self):
        # Move the obstacle left by the current game speed.
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width and self in obstacles:
            # Remove it from the obstacle list once it has fully left the screen.
            obstacles.remove(self)

    def draw(self, screen):
        # Draw the selected obstacle image using pygame blit syntax.
        screen.blit(self.image[self.type], self.rect)

    def get_collision_rect(self):
        # Create a smaller collision box than the full sprite rectangle.
        inset_x, inset_top, inset_bottom = self.HITBOX
        return pygame.Rect(
            self.rect.x + inset_x,
            self.rect.y + inset_top,
            max(1, self.rect.width - (inset_x * 2)),
            max(1, self.rect.height - inset_top - inset_bottom),
        )


class SmallCactus(Obstacle):
    # Hitbox values tuned for the small cactus sprite.
    HITBOX = (14, 8, 6)

    def __init__(self, image):
        # Pick one of the three small cactus images at random.
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        # Place the cactus on the ground line.
        self.rect.y = 325


class LargeCactus(Obstacle):
    # Hitbox values tuned for the large cactus sprite.
    HITBOX = (18, 10, 8)

    def __init__(self, image):
        # Pick one of the three large cactus images at random.
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        # Place the taller cactus slightly higher.
        self.rect.y = 300


class Bird(Obstacle):
    # Hitbox values tuned for the bird sprite.
    HITBOX = (12, 10, 10)

    def __init__(self, image):
        # Start with the first bird image frame.
        self.type = 0
        super().__init__(image, self.type)
        # Position the bird in the air.
        self.rect.y = 235
        # Animation counter used to alternate wing frames.
        self.index = 0

    def draw(self, screen):
        # Reset the animation loop after enough frames have passed.
        if self.index >= 9:
            self.index = 0
        # Use pygame blit syntax to draw the current bird flap frame.
        screen.blit(self.image[(self.index // 5) % len(self.image)], self.rect)
        self.index += 1


def main():
    # These globals are shared outside the function, so we reset them at the start of each run.
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    # `pygame.time.Clock()` is pygame syntax for controlling frame timing.
    clock = pygame.time.Clock()
    # Create the main objects used during gameplay.
    player = Horse()
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
        # This nested function updates the score and slowly increases difficulty.
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1

        # `font.render(...)` makes a pygame text surface, then `blit` draws it.
        text = font.render("Points: " + str(points), True, BLACK)
        text_rect = text.get_rect()
        text_rect.center = (1000, 40)
        SCREEN.blit(text, text_rect)

    def background():
        # This nested function scrolls the track image to create an endless ground effect.
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        # `SCREEN.blit(...)` is pygame syntax for drawing the background images.
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            # Reset the background once one full image has moved off-screen.
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    while run:
        # `pygame.event.get()` is pygame syntax for reading window events like quitting.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cleanup_and_exit()

        #collect data from camera.
        camera_state = camera_controller.get_camera_state()
        camera_input = camera_state["camera_input"] 

        # collect data from keyboard.
        keys = pygame.key.get_pressed()
        # Combine camera input with keyboard input so both control methods work.
        camera_input[pygame.K_UP] = camera_input[pygame.K_UP] or keys[pygame.K_UP]
        camera_input[pygame.K_DOWN] = camera_input[pygame.K_DOWN] or keys[pygame.K_DOWN]

        # `SCREEN.fill(...)` is pygame syntax for clearing the window before redrawing.
        SCREEN.fill(WHITE)

        # Draw and update the player every frame.
        player.draw(SCREEN)
        player.update(camera_input)
        # `pygame.draw.rect(...)` here draws a red debug outline around the player's collision box.
        #pygame.draw.rect(SCREEN, (255, 0, 0), player.get_collision_rect(), 2)

        # Only create a new obstacle when there are currently none on screen.
        if len(obstacles) == 0:
            obstacle_roll = random.randint(0, 2)
            if obstacle_roll == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif obstacle_roll == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            else:
                obstacles.append(Bird(BIRD))

        # Update every obstacle and check for collisions with the player.
        for obstacle in list(obstacles):
            obstacle.draw(SCREEN)
            obstacle.update()
            # This blue rectangle is another debug hitbox outline for the obstacle.

            #pygame.draw.rect(SCREEN, (0, 0, 255), obstacle.get_collision_rect(), 2)
            
            # `.colliderect(...)` is pygame rectangle syntax for collision detection.
            if player.get_collision_rect().colliderect(obstacle.get_collision_rect()):
                # Pause briefly, count the death, then go back to the menu.
                pygame.time.delay(1000)
                death_count += 1
                menu(death_count)
                return

        # Draw the rest of the scene and UI after gameplay objects update.
        background()
        cloud.draw(SCREEN)
        cloud.update()
        score()
        draw_camera_preview(SCREEN, camera_state["cam_surface"])

        # `clock.tick(30)` limits the loop to about 30 frames per second.
        clock.tick(30)
        # `pygame.display.update()` shows the finished frame on screen.
        pygame.display.update()


def menu(death_count):
    # Show the start/calibration screen, then begin the main game loop.
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
    # Clean up both the camera resource and pygame before exiting the program.
    camera_controller.cleanup()
    pygame.quit()
    raise SystemExit


if __name__ == "__main__":
    # Start the game from the menu, and always release the camera when the program ends.
    try:
        menu(death_count=0)
    finally:
        camera_controller.cleanup()
