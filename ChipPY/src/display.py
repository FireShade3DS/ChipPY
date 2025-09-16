import pygame

class Display:
    def __init__(self, scale = 10, bg_color = (0, 0, 0), fg_color = (255, 255, 255)) -> None:
        pygame.init()
        self.scale = scale
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.clock = pygame.time.Clock()
        self.rows = 32
        self.cols = 64
        self.width = self.cols * self.scale
        self.height = self.rows * self.scale
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.display = [0] * (self.rows * self.cols)
        self.clear()
    def clear(self) -> None:
        self.display = [0] * (self.rows * self.cols)
        pygame.display.flip()
    def draw_sprite(self, x, y, sprite) -> bool:
        collision = False
        for row_index, byte in enumerate(sprite):
            for bit_index in range(8):
                if byte & (0x80 >> bit_index):
                    pixel_x = (x + bit_index) % self.cols
                    pixel_y = (y + row_index) % self.rows
                    pixel_index = pixel_y * self.cols + pixel_x
                    if self.display[pixel_index] == 1:
                        collision = True
                    self.display[pixel_index] ^= 1
        self.update_screen()
        return collision
    def update_screen(self) -> None:
        for row in range(self.rows):
            for col in range(self.cols):
                color = self.fg_color if self.display[row * self.cols + col] else self.bg_color
                pygame.draw.rect(self.screen, color, (col * self.scale, row * self.scale, self.scale, self.scale))
        pygame.display.flip()
        self.clock.tick(60)
    def get_display_buffer(self):
        return self.display