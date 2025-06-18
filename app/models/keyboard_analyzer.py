from pynput import keyboard
from datetime import datetime

class KeyboardAnalyzer:
    def __init__(self):
        self.keystrokes = []
        self.start_time = datetime.now()
        self.backspace_count = 0
        self.error_count = 0  # placeholder: define your own logic later
        self.typing_speed = 0.0  # chars per minute

        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.start()

    def _on_press(self, key):
        try:
            now = datetime.now()
            self.keystrokes.append((key.char, now))
        except AttributeError:
            if key == keyboard.Key.backspace:
                self.backspace_count += 1
                now = datetime.now()
                self.keystrokes.append(('Backspace', now))

    def analyze(self):
        elapsed_seconds = (datetime.now() - self.start_time).total_seconds()
        if elapsed_seconds == 0:
            self.typing_speed = 0
        else:
            valid_keys = [k for k, _ in self.keystrokes if len(k) == 1 and k.isprintable()]
            self.typing_speed = (len(valid_keys) / elapsed_seconds) * 60  # CPM

        return {
            "typing_speed": round(self.typing_speed, 2),
            "backspace_count": self.backspace_count,
            "error_count": self.error_count  # You can customize this with more rules
        }

    def reset(self):
        self.keystrokes.clear()
        self.backspace_count = 0
        self.error_count = 0
        self.start_time = datetime.now()

    def stop(self):
        self.listener.stop()
