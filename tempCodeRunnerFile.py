 def draw(self, screen):
        # Reset the animation loop after enough frames have passed.
        if self.index >= 9:
            self.index = 0
        # Use pygame blit syntax to draw the current bird flap frame.
        screen.blit(self.image[(self.index // 5) % len(self.image)], self.rect)
        self.index += 1