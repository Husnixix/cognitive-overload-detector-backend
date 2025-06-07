from deepface import DeepFace
import cv2

class ExpressionAnalyzer:
    def __init__(self):
        self.last_expression = "neutral"
        self.expression_counts = {
            "happy": 0,
            "sad": 0,
            "angry": 0,
            "surprise": 0,
            "neutral": 0,
            "disgust": 0,
            "fear": 0
        }

    def detect_expression(self, frame):
        try:
            # Analyze only emotion from DeepFace
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            if isinstance(result, list):
                result = result[0]

            emotion = result["dominant_emotion"]
            emotion = emotion.lower()

            if emotion in self.expression_counts:
                self.expression_counts[emotion] += 1
                self.last_expression = emotion

        except Exception as e:
            print(f"[ExpressionAnalyzer] Error: {e}")
            self.last_expression = "neutral"

        return self.last_expression, self.expression_counts
