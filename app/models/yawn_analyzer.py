import math

class YawnAnalyzer:
    TOP_LIP = 13
    BOTTOM_LIP = 14
    LEFT_MOUTH = 78
    RIGHT_MOUTH = 308

    def __init__(self, yawn_threshold=0.6, consecutive_frames=2):
        self.yawn_threshold = yawn_threshold
        self.consecutive_frames = consecutive_frames
        self.frame_counter = 0
        self.yawn_count = 0
        self.is_yawning = False

    def _euclidean_distance(self, p1, p2):
        x1, y1 = float(p1[0]), float(p1[1])
        x2, y2 = float(p2[0]), float(p2[1])
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def _mouth_aspect_ratio(self, landmarks_dict):
        vertical = self._euclidean_distance(landmarks_dict[self.TOP_LIP], landmarks_dict[self.BOTTOM_LIP])
        horizontal = self._euclidean_distance(landmarks_dict[self.LEFT_MOUTH], landmarks_dict[self.RIGHT_MOUTH])
        return vertical / horizontal if horizontal != 0 else 0

    def analyze(self, landmarks):
        landmarks_dict = {
            self.TOP_LIP: (float(landmarks[self.TOP_LIP][0]), float(landmarks[self.TOP_LIP][1])),
            self.BOTTOM_LIP: (float(landmarks[self.BOTTOM_LIP][0]), float(landmarks[self.BOTTOM_LIP][1])),
            self.LEFT_MOUTH: (float(landmarks[self.LEFT_MOUTH][0]), float(landmarks[self.LEFT_MOUTH][1])),
            self.RIGHT_MOUTH: (float(landmarks[self.RIGHT_MOUTH][0]), float(landmarks[self.RIGHT_MOUTH][1])),
        }

        mar = self._mouth_aspect_ratio(landmarks_dict)

        if mar > self.yawn_threshold:
            self.frame_counter += 1
        else:
            if self.frame_counter >= self.consecutive_frames:
                self.yawn_count += 1
                self.is_yawning = True
            else:
                self.is_yawning = False
            self.frame_counter = 0

        return self.is_yawning, self.yawn_count