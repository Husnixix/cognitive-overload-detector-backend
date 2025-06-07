import math


class EyeAnalyzer:
    LEFT_EYE_LANDMARKS = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE_LANDMARKS = [362, 385, 387, 263, 373, 380]

    def __init__(self, blink_threshold=0.21, consecutive_frames=2):
        self.blink_threshold = blink_threshold
        self.consecutive_frames = consecutive_frames
        self.frame_counter = 0
        self.blink_count = 0
        self.is_blinking = False

    def _euclidean_distance(self, p1, p2):
        x1, y1 = float(p1[0]), float(p1[1])
        x2, y2 = float(p2[0]), float(p2[1])
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def _calculate_ear(self, eye_landmarks):
        A = self._euclidean_distance(eye_landmarks[1], eye_landmarks[5])
        B = self._euclidean_distance(eye_landmarks[2], eye_landmarks[4])
        C = self._euclidean_distance(eye_landmarks[0], eye_landmarks[3])
        ear = (A + B) / (2.0 * C)
        return ear

    def analyze(self, landmarks):
        left_eye = [(float(landmarks[i][0]), float(landmarks[i][1])) for i in self.LEFT_EYE_LANDMARKS]
        right_eye = [(float(landmarks[i][0]), float(landmarks[i][1])) for i in self.RIGHT_EYE_LANDMARKS]

        left_ear = self._calculate_ear(left_eye)
        right_ear = self._calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0

        if avg_ear < self.blink_threshold:
            self.frame_counter += 1
        else:
            if self.frame_counter >= self.consecutive_frames:
                self.blink_count += 1
                self.is_blinking = True
            else:
                self.is_blinking = False
            self.frame_counter = 0

        return self.is_blinking, self.blink_count