# To get access to the assets folder
import os 
# To get random numbers for obstacle generation
import random
# To create the game window and use the pygame library
import pygame

# Get the camera controller class
from camera_logic import CameraController
# Get the UI Functions and constants
from ui import BLACK, WHITE, draw_camera_preview, show_start_ui
# Initialize Pygame and the camera controller
pygame.init()

camera_controller = CameraController()

# Global Constants ( Adjust how big and how long the screen is )
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Motion Controlled Horse Game")

# --- Asset Loading ---
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

JUMPING = [pygame.image.load(os.path.join("Assets/Horse", "run3.png")),
           pygame.image.load(os.path.join("Assets/Horse", "run4.png")),
           pygame.image.load(os.path.join("Assets/Horse", "run13.png"))]
DUCKING = [pygame.image.load(os.path.join("Assets/Horse", "duck1.png")),
           pygame.image.load(os.path.join("Assets/Horse", "duck2.png"))] 

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
OBSTACLE_SPAWN_DISTANCE_MIN = 280
OBSTACLE_SPAWN_DISTANCE_MAX = 420



class Dinosaur:
    X_POS = 80
    Y_POS = 225
    JUMP_VEL = 8.0
    RUN_HITBOX = (18, 12, 10)
    DUCK_HITBOX = (20, 18, 8)

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
        self.ground_y = self.Y_POS + self.image.get_height()

    def update(self, user_input):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 28:
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
        self.image = self.duck_img[(self.step_index // 2) % len(self.duck_img)]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.bottom = self.ground_y
        self.step_index += 1

    def run(self):
        self.image = self.run_img[(self.step_index // 2) % len(self.run_img)]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.bottom = self.ground_y
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img[min(self.step_index // 10, len(self.jump_img) - 1)]
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL
            self.step_index = 0

    def draw(self, screen):
        screen.blit(self.image, (self.dino_rect.x, self.dino_rect.y))

    def _inset_rect(self, rect, hitbox):
        inset_x, inset_top, inset_bottom = hitbox
        return pygame.Rect(
            rect.x + inset_x,
            rect.y + inset_top,
            max(1, rect.width - (inset_x * 2)),
            max(1, rect.height - inset_top - inset_bottom),
        )

    def get_collision_rect(self):
        hitbox = self.DUCK_HITBOX if self.dino_duck and not self.dino_jump else self.RUN_HITBOX
        return self._inset_rect(self.dino_rect, hitbox)


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
    HITBOX = (0, 0, 0)

    def __init__(self, image, obstacle_type):
        self.image = image
        self.type = obstacle_type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH + random.randint(
            OBSTACLE_SPAWN_DISTANCE_MIN,
            OBSTACLE_SPAWN_DISTANCE_MAX,
        )

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width and self in obstacles:
            obstacles.remove(self)

    def draw(self, screen):
        screen.blit(self.image[self.type], self.rect)

    def get_collision_rect(self):
        inset_x, inset_top, inset_bottom = self.HITBOX
        return pygame.Rect(
            self.rect.x + inset_x,
            self.rect.y + inset_top,
            max(1, self.rect.width - (inset_x * 2)),
            max(1, self.rect.height - inset_top - inset_bottom),
        )


class SmallCactus(Obstacle):
    HITBOX = (14, 8, 6)

    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    HITBOX = (18, 10, 8)

    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    HITBOX = (12, 10, 10)

    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 235
        self.index = 0

    def draw(self, screen):
        if self.index >= 9:
            self.index = 0
        screen.blit(self.image[(self.index // 5) % len(self.image)], self.rect)
        self.index += 1


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

        camera_state = camera_controller.get_camera_state()
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
            if player.get_collision_rect().colliderect(obstacle.get_collision_rect()):
                pygame.time.delay(1000)
                death_count += 1
                menu(death_count)
                return


        background()
        cloud.draw(SCREEN)
        cloud.update()
        score()
        draw_camera_preview(SCREEN, camera_state["cam_surface"])

        clock.tick(30)
        pygame.display.update()


def menu(death_count):
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
    camera_controller.cleanup()
    pygame.quit()
    raise SystemExit


if __name__ == "__main__":
    try:
        menu(death_count=0)
    finally:
        camera_controller.cleanup()

