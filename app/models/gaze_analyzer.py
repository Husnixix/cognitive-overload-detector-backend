import cv2


class GazeAnalyzer:
    # Correct MediaPipe FaceMesh landmarks for eye analysis
    LEFT_EYE_OUTER = 33
    LEFT_EYE_INNER = 133
    LEFT_EYE_TOP = 159
    LEFT_EYE_BOTTOM = 145

    RIGHT_EYE_INNER = 362
    RIGHT_EYE_OUTER = 263
    RIGHT_EYE_TOP = 386
    RIGHT_EYE_BOTTOM = 374

    def __init__(self, threshold=0.05):
        self.threshold = threshold
        self.gaze_direction = "Center"
        self.left_count = 0
        self.right_count = 0
        self.center_count = 0

    def _calculate_eye_center(self, eye_landmarks):
        """Calculate the center of an eye from corner landmarks"""
        # eye_landmarks is a list of [x, y, z] coordinates
        center_x = sum(point[0] for point in eye_landmarks) / len(eye_landmarks)  # x coordinate
        center_y = sum(point[1] for point in eye_landmarks) / len(eye_landmarks)  # y coordinate
        return center_x, center_y

    def analyze(self, landmarks):
        try:
            # Check if we have enough landmarks
            if len(landmarks) < 400:
                print(f"Warning: Only {len(landmarks)} landmarks available, need at least 400")
                self.gaze_direction = "Center"
                self.center_count += 1
                return self.gaze_direction

            # Get left eye landmarks - landmarks[index] returns [x, y, z]
            left_eye_points = [
                landmarks[self.LEFT_EYE_OUTER],  # 33
                landmarks[self.LEFT_EYE_INNER],  # 133
                landmarks[self.LEFT_EYE_TOP],  # 159
                landmarks[self.LEFT_EYE_BOTTOM]  # 145
            ]

            # Get right eye landmarks
            right_eye_points = [
                landmarks[self.RIGHT_EYE_INNER],  # 362
                landmarks[self.RIGHT_EYE_OUTER],  # 263
                landmarks[self.RIGHT_EYE_TOP],  # 386
                landmarks[self.RIGHT_EYE_BOTTOM]  # 374
            ]

            # Calculate eye centers
            left_center_x, left_center_y = self._calculate_eye_center(left_eye_points)
            right_center_x, right_center_y = self._calculate_eye_center(right_eye_points)

            # For gaze detection, we'll use the relative position of eye corners
            left_inner = landmarks[self.LEFT_EYE_INNER]  # [x, y, z]
            left_outer = landmarks[self.LEFT_EYE_OUTER]  # [x, y, z]
            right_inner = landmarks[self.RIGHT_EYE_INNER]  # [x, y, z]
            right_outer = landmarks[self.RIGHT_EYE_OUTER]  # [x, y, z]

            # Calculate eye width ratio as a proxy for gaze direction
            left_eye_width = abs(left_inner[0] - left_outer[0])  # x difference
            right_eye_width = abs(right_inner[0] - right_outer[0])  # x difference

            # Simple gaze estimation based on eye asymmetry
            eye_ratio = left_eye_width / right_eye_width if right_eye_width > 0 else 1

            if eye_ratio < (1 - self.threshold):
                self.gaze_direction = "Right"
                self.right_count += 1
            elif eye_ratio > (1 + self.threshold):
                self.gaze_direction = "Left"
                self.left_count += 1
            else:
                self.gaze_direction = "Center"
                self.center_count += 1

        except (IndexError, ZeroDivisionError) as e:
            print(f"Error in gaze analysis: {e}")
            self.gaze_direction = "Center"

        return self.gaze_direction

    def reset_counters(self):
        self.left_count = 0
        self.right_count = 0
        self.center_count = 0

    def draw_gaze_line(self, frame, landmarks, width, height):
        try:
            # Get eye corner landmarks - each is [x, y, z] in pixel coordinates
            left_inner = landmarks[self.LEFT_EYE_INNER]
            left_outer = landmarks[self.LEFT_EYE_OUTER]
            right_inner = landmarks[self.RIGHT_EYE_INNER]
            right_outer = landmarks[self.RIGHT_EYE_OUTER]

            # Convert to integer pixel coordinates (they're already scaled)
            left_inner_px = (int(left_inner[0]), int(left_inner[1]))
            left_outer_px = (int(left_outer[0]), int(left_outer[1]))
            right_inner_px = (int(right_inner[0]), int(right_inner[1]))
            right_outer_px = (int(right_outer[0]), int(right_outer[1]))

            # Draw eye landmarks
            cv2.circle(frame, left_inner_px, 3, (0, 255, 0), -1)
            cv2.circle(frame, left_outer_px, 3, (0, 255, 0), -1)
            cv2.circle(frame, right_inner_px, 3, (0, 255, 0), -1)
            cv2.circle(frame, right_outer_px, 3, (0, 255, 0), -1)

            # Draw gaze direction text
            cv2.putText(frame, f"Gaze: {self.gaze_direction}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        except (IndexError, TypeError) as e:
            print(f"Error drawing gaze line: {e}")