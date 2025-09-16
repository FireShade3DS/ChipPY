class CPU:
    def __init__(self, display, speaker, keyboard) -> None:
        self.display = display
        self.speaker = speaker
        self.keyboard = keyboard
        self.memory = bytearray(4096)  # 4KB of memory
        self.V = bytearray(16)  # 16 registers
        self.I = 0  # Index register
        self.pc = 0x200  # Program counter starts at 0x200
        self.stack = []
        self.delay_timer = 0
        self.sound_timer = 0
        self.draw_flag = False
        self.load_fontset()
    def load_fontset(self) -> None:
        fontset = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]
        for i in range(len(fontset)):
            self.memory[i] = fontset[i] # Load fontset into memory
    def load_rom(self, rom) -> None:
        for i in range(len(rom)):
            self.memory[0x200 + i] = rom[i]  # Load ROM into memory starting at 0x200   
    def cycle(self) -> None:
        opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
        self.execute_opcode(opcode)
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            if self.sound_timer == 1:
                self.speaker.play_tone(440, 0.1)  # Play a tone when sound timer reaches zero
            self.sound_timer -= 1
    def execute_opcode(self, opcode) -> None:
        self.pc += 2
        match opcode & 0xF000:
            case 0x0000:
                match opcode & 0x00FF:
                    case 0x00E0:  # CLS
                        self.display.clear()
                    case 0x00EE:  # RET
                        self.pc = self.stack.pop()
                    case 0x0:  # SYS addr (ignored)
                        print(f"Doing the sys thingy idk bruh {opcode & 0x0FFF:03X}")
            case 0x1000:  # JP addr
                self.pc = opcode & 0x0FFF
            case 0x2000:  # CALL addr
                self.stack.append(self.pc)
                self.pc = opcode & 0x0FFF
            case 0x3000:  # SE Vx, byte
                x = (opcode & 0x0F00) >> 8
                kk = opcode & 0x00FF
                if self.V[x] == kk:
                    self.pc += 2
            case 0x4000:  # SNE Vx, byte
                x = (opcode & 0x0F00) >> 8
                kk = opcode & 0x00FF
                if self.V[x] != kk:
                    self.pc += 2
            case 0x5000:  # SE Vx, Vy
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                if self.V[x] == self.V[y]:
                    self.pc += 2
            case 0x6000:  # LD Vx, byte
                x = (opcode & 0x0F00) >> 8
                kk = opcode & 0x00FF
                self.V[x] = kk
            case 0x7000:  # ADD Vx, byte
                x = (opcode & 0x0F00) >> 8
                kk = opcode & 0x00FF
                self.V[x] = (self.V[x] + kk) & 0xFF
            case 0x8000:  # LD Vx, Vy and other 0x8XY_ opcodes
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                match opcode & 0x000F:
                    case 0x0:  # LD Vx, Vy
                        self.V[x] = self.V[y]
                    case 0x1:  # OR Vx, Vy
                        self.V[x] |= self.V[y]
                        self.V[0xF] = 0  # Reset VF
                    case 0x2:  # AND Vx, Vy
                        self.V[x] &= self.V[y]
                        self.V[0xF] = 0  # Reset VF
                    case 0x3:  # XOR Vx, Vy
                        self.V[x] ^= self.V[y]
                        self.V[0xF] = 0  # Reset VF
                    case 0x4:  # ADD Vx, Vy
                        result = self.V[x] + self.V[y]  # Calculate the result first
                        self.V[x] = result & 0xFF  # Update Vx with the lower 8 bits of the result
                        self.V[0xF] = 1 if result > 0xFF else 0  # Update VF after the calculation
                    case 0x5:  # SUB Vx, Vy
                        borrow = 1 if self.V[x] >= self.V[y] else 0  # Calculate the borrow flag first
                        self.V[x] = (self.V[x] - self.V[y]) & 0xFF  # Perform the subtraction
                        self.V[0xF] = borrow  # Update VF after the subtraction
                    case 0x6:  # SHR Vx {, Vy}
                        lsb = self.V[x] & 0x1  # Store the least significant bit of Vx
                        self.V[x] >>= 1  # Shift Vx right by 1
                        self.V[0xF] = lsb  # Update VF after the shift
                    case 0x7:  # SUBN Vx, Vy
                        borrow = 1 if self.V[y] >= self.V[x] else 0  # Calculate the borrow flag first
                        self.V[x] = (self.V[y] - self.V[x]) & 0xFF  # Perform the subtraction
                        self.V[0xF] = borrow  # Update VF after the subtraction
                    case 0xE:  # SHL Vx {, Vy}
                        msb = (self.V[x] & 0x80) >> 7  # Store the most significant bit of Vx
                        self.V[x] = (self.V[x] << 1) & 0xFF  # Shift Vx left by 1
                        self.V[0xF] = msb  # Update VF after the shift
                    case _:
                        pass  # Ignore other 0x8XY_ opcodes
            case 0x9000:  # SNE Vx, Vy
                x = (opcode & 0x0F00) >> 8
                y = (opcode & 0x00F0) >> 4
                if self.V[x] != self.V[y]:
                    self.pc += 2
            case 0xA000:  # LD I, addr
                self.I = opcode & 0x0FFF
            case 0xB000:  # JP V0, addr
                self.pc = (opcode & 0x0FFF) + self.V[0]
            case 0xC000:  # RND Vx, byte
                import random
                x = (opcode & 0x0F00) >> 8
                kk = opcode & 0x00FF
                self.V[x] = random.randint(0, 255) & kk

            case 0xD000:  # DRW Vx, Vy, nibble
                x = self.V[(opcode & 0x0F00) >> 8]
                y = self.V[(opcode & 0x00F0) >> 4]
                nibble = opcode & 0x000F
                sprite = self.memory[self.I:self.I + nibble]
                self.V[0xF] = 1 if self.display.draw_sprite(x, y, sprite) else 0  # Set VF based on collision
                self.draw_flag = True
            case 0xE000:  # Key opcodes
                x = (opcode & 0x0F00) >> 8
                match opcode & 0x00FF:
                    case 0x9E:  # SKP Vx
                        print(f"Checking if key {self.V[x]} is pressed...")
                        if self.keyboard.is_key_pressed(self.V[x]):
                            print(f"Key {self.V[x]} is pressed. Skipping next instruction.")
                            self.pc += 2
                    case 0xA1:  # SKNP Vx
                        if not self.keyboard.is_key_pressed(self.V[x]):
                            self.pc += 2

            case 0xF000:  # Misc opcodes
                x = (opcode & 0x0F00) >> 8
                match opcode & 0x00FF:
                    case 0x07:  # LD Vx, DT
                        self.V[x] = self.delay_timer
                    case 0x0A:  # LD Vx, K
                        self.V[x] = self.keyboard.wait_for_keypress()
                    case 0x15:  # LD DT, Vx
                        self.delay_timer = self.V[x]
                    case 0x18:  # LD ST, Vx
                        self.sound_timer = self.V[x]
                    case 0x1E:  # ADD I, Vx
                        self.I = (self.I + self.V[x]) & 0xFFF
                    case 0x29:  # LD F, Vx
                        self.I = self.V[x] * 5  # Each font character is 5 bytes
                    case 0x33:  # LD B, Vx
                        value = self.V[x]
                        self.memory[self.I] = value // 100
                        self.memory[self.I + 1] = (value // 10) % 10
                        self.memory[self.I + 2] = value % 10
                    case 0x55:  # LD [I], Vx
                        for i in range(x + 1):
                            self.memory[self.I + i] = self.V[i]
                        self.I += x + 1  # Increment I after saving

                    case 0x65:  # LD Vx, [I]
                        for i in range(x + 1):
                            self.V[i] = self.memory[self.I + i]
                        self.I += x + 1  # Increment I after loading
                    case _:
                        pass  # Ignore other 0xFX__ opcodes
            case _:
                raise ValueError(f"Unknown opcode: {opcode:04X}")
        print(f"Executed opcode: {opcode:04X}, PC: {self.pc:03X}")