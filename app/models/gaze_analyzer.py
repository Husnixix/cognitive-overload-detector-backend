import cv2

class GazeAnalyzer:
    # Iris and eye corner landmarks (MediaPipe FaceMesh)
    LEFT_IRIS = 468
    RIGHT_IRIS = 473
    LEFT_EYE_CENTER = 133  # inner corner
    RIGHT_EYE_CENTER = 362  # outer corner

    def __init__(self, threshold=0.05):
        self.threshold = threshold
        self.gaze_direction = "Center"

    def analyze(self, frame, landmarks):
        # Get landmark positions
        left_iris = landmarks[self.LEFT_IRIS]
        right_iris = landmarks[self.RIGHT_IRIS]
        left_corner = landmarks[self.LEFT_EYE_CENTER]
        right_corner = landmarks[self.RIGHT_EYE_CENTER]

        # Average iris center
        iris_x = (left_iris.x + right_iris.x) / 2
        eye_center_x = (left_corner.x + right_corner.x) / 2

        diff = iris_x - eye_center_x

        if diff < -self.threshold:
            self.gaze_direction = "Left"
        elif diff > self.threshold:
            self.gaze_direction = "Right"
        else:
            self.gaze_direction = "Center"

        return self.gaze_direction

    def draw_gaze_line(self, frame, landmarks, width, height):
        left_iris = landmarks[self.LEFT_IRIS]
        right_iris = landmarks[self.RIGHT_IRIS]
        left_corner = landmarks[self.LEFT_EYE_CENTER]
        right_corner = landmarks[self.RIGHT_EYE_CENTER]

        # Convert to pixel coordinates
        iris_x = int((left_iris.x + right_iris.x) * width / 2)
        iris_y = int((left_iris.y + right_iris.y) * height / 2)
        eye_x = int((left_corner.x + right_corner.x) * width / 2)
        eye_y = int((left_corner.y + right_corner.y) * height / 2)

        # Draw a line from eye to iris
        cv2.line(frame, (eye_x, eye_y), (iris_x, iris_y), (0, 255, 255), 2)
        cv2.putText(frame, f"Gaze: {self.gaze_direction}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
