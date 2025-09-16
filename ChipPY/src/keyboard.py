import pygame

class Keyboard:
    def __init__(self) -> None:
        self.input_dir = {
            pygame.K_1: 0x1,
            pygame.K_2: 0x2,
            pygame.K_3: 0x3,
            pygame.K_4: 0xC,
            pygame.K_q: 0x4,
            pygame.K_w: 0x5,
            pygame.K_e: 0x6,
            pygame.K_r: 0xD,
            pygame.K_a: 0x7,
            pygame.K_s: 0x8,
            pygame.K_d: 0x9,
            pygame.K_f: 0xE,
            pygame.K_z: 0xA,
            pygame.K_x: 0x0,
            pygame.K_c: 0xB,
            pygame.K_v: 0xF
        }
        self.keys = [0] * 16  # State of each Chip-8 key (pressed or not)
        self.last_key = None  # Last key pressed

    def key_down(self, key) -> None:
        if key in self.input_dir:
            key_index = self.input_dir[key]
            self.keys[key_index] = 1
            self.last_key = key_index
            print(f"Key Down: {key} -> {key_index}")  # Debugging

    def key_up(self, key) -> None:
        if key in self.input_dir:
            key_index = self.input_dir[key]
            self.keys[key_index] = 0
            print(f"Key Up: {key} -> {key_index}")  # Debugging

    def is_key_pressed(self, key_index) -> bool:
        return self.keys[key_index] == 1

    def wait_for_keypress(self) -> int:
        print("Waiting for keypress...")  # Debugging
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key in self.input_dir:
                        key_index = self.input_dir[event.key]
                        print(f"Key Pressed: {key_index}")  # Debugging
                        return key_index

    def reset(self) -> None:
        self.keys = [0] * 16
        self.last_key = None