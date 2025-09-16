from matplotlib import scale
from src.cpu import CPU
from src.display import Display 
from src.keyboard import Keyboard
from src.sound import Speaker
import pygame
import sys
import time
import os
class ChipPY:
    def __init__(self, rom_path, scale=10, wave_type="sine") -> None:
        pygame.init()
        self.display = Display(scale=scale)
        self.speaker = Speaker(wave_type=wave_type)
        self.keyboard = Keyboard()
        self.cpu = CPU(self.display, self.speaker, self.keyboard)
        self.rom_path = rom_path  # Store the ROM file path
        self.load_rom(rom_path)
        self.running = True
    def load_rom(self, rom_path) -> None:
        with open(rom_path, 'rb') as f:
            self.rom = f.read()
        self.cpu.load_rom(self.rom)
    def run(self) -> None:
        clock = pygame.time.Clock()  # Pygame clock for precise timing
        cpu_speed = 500  # Target CPU speed in instructions per second
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    print(f"Key Down Event: {event.key}")  # Debugging
                    self.keyboard.key_down(event.key)
                elif event.type == pygame.KEYUP:
                    print(f"Key Up Event: {event.key}")  # Debugging
                    self.keyboard.key_up(event.key)

            # Run enough CPU cycles to match the target speed
            for _ in range(cpu_speed // 60):  # Run multiple cycles per frame
                self.cpu.cycle()

            # Update the display at 60 FPS
            if self.cpu.draw_flag:
                self.display.update_screen()
                self.cpu.draw_flag = False

            clock.tick(60)  # Limit the loop to 60 iterations per second

        pygame.quit()
        sys.exit()
    def reset(self) -> None:
        self.cpu = CPU(self.display, self.speaker, self.keyboard)
        self.load_rom(self.rom_path)  # Use the stored ROM file path
        self.running = True
    def drop_in_rom(self):
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        rom_path = filedialog.askopenfilename(title="Select ROM", filetypes=[("Chip-8 ROMs", "*.ch8"), ("All Files", "*.*")])
        if rom_path:
            self.rom_path = rom_path  # Update the stored ROM file path
            self.load_rom(rom_path)
            self.reset()
            self.run()
        else:
            print("No ROM selected. Exiting.")
            pygame.quit()
            sys.exit()
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    roms_dir = str(os.path.join(current_dir, 'roms', '1-chip8-logo.ch8'))
    chip8 = ChipPY(rom_path=roms_dir)
    chip8.drop_in_rom()