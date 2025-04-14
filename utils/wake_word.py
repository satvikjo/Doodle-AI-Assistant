import pvporcupine
import pyaudio
import struct
import os

class WakeWordDetector:
    def __init__(self):
        self.porcupine = pvporcupine.create(
            access_key=os.getenv("PORCUPINE_ACCESS_KEY"),
            keyword_paths=[r"C:\Users\satvik\Desktop\Doodle\Hey-Doodle_en_windows_v3_0_0.ppn"]
        )
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length,
            start=True  # keep stream running
        )

    def listen_for_wake_word(self, non_blocking=False):
        try:
            pcm = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            result = self.porcupine.process(pcm)
            return result >= 0
        except Exception as e:
            print(f"❌ Wake word error: {e}")
            return False
