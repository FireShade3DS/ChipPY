from pygame import mixer
import numpy as np

class Speaker:
    def __init__(self, wave_type = "sine") -> None:
        self.wave_type = wave_type
        mixer.init()
        self.sample_rate = 44100
        self.volume = 1.0
        self.buffer = np.zeros((self.sample_rate,), dtype=np.float32)
        self.sound = None
        self.channel = None
    def generate_wave(self, frequency, duration) -> np.ndarray:
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        if self.wave_type == "sine":
            wave = np.sin(2 * np.pi * frequency * t)
        elif self.wave_type == "square":
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        elif self.wave_type == "triangle":
            wave = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
        elif self.wave_type == "sawtooth":
            wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        else:
            raise ValueError("Unsupported wave type")
        return wave.astype(np.float32)
    def play_tone(self, frequency, duration) -> None:
        wave = self.generate_wave(frequency, duration)
        self.sound = mixer.Sound(wave * self.volume)
        self.channel = self.sound.play()
    def stop_tone(self) -> None:
        if self.channel:
            self.channel.stop()
    def set_volume(self, volume) -> None:
        self.volume = max(0.0, min(1.0, volume))
        if self.sound:
            self.sound.set_volume(self.volume)
    def set_wave_type(self, wave_type) -> None:
        self.wave_type = wave_type
    def is_playing(self) -> bool:
        return self.channel.get_busy() if self.channel else False
    def cleanup(self) -> None:
        mixer.quit()