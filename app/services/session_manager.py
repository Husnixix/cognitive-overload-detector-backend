import cv2
import threading
import time
import json
import logging
from app.models.face_detector import FaceDetector
from app.models.session_data import SessionData
from app.models.eye_analyzer import EyeAnalyzer
from app.models.yawn_analyzer import YawnAnalyzer
from app.models.gaze_analyzer import GazeAnalyzer
from app.models.expression_analyzer import ExpressionAnalyzer
from app.models.keyboard_analyzer import KeyboardAnalyzer
from app.models.cognitive_overload_detector import CognitiveOverloadDetector
from app.visualizers.overlay import draw_overlays
from datetime import datetime
import uuid
logging.basicConfig(level=logging.INFO)

class SessionManager:
    def __init__(self, json_path="session_data.json"):
        self.face_detector = FaceDetector()
        self.eye_analyzer = EyeAnalyzer()
        self.yawn_analyzer = YawnAnalyzer()
        self.gaze_analyzer = GazeAnalyzer()
        self.expression_analyzer = ExpressionAnalyzer()
        self.keyboard_analyzer = KeyboardAnalyzer()
        self.cognitive_detector = CognitiveOverloadDetector()

        self.session_data = []
        self.is_running = False
        self.thread = None
        self.json_path = json_path

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            logging.error("Cannot open webcam")
            raise RuntimeError("Cannot open webcam")

    def start(self):
        if self.is_running:
            logging.warning("Session already running")
            return
        self.is_running = True
        self.keyboard_analyzer.reset()
        self.thread = threading.Thread(target=self._run)
        self.thread.start()
        logging.info("Session started")

    def stop(self):
        if not self.is_running:
            logging.warning("Session not running")
            return
        self.is_running = False
        self.thread.join()
        self.cap.release()
        self.keyboard_analyzer.stop()
        cv2.destroyAllWindows()
        self._save_session()
        logging.info("Session stopped and data saved")

    def _save_session(self):
        try:
            with open(self.json_path, "w") as f:
                json.dump([data.__dict__ for data in self.session_data], f, indent=4)
            logging.info(f"Session data saved to {self.json_path}")
        except Exception as e:
            logging.error(f"Error saving session data: {e}")

    def _run(self):
        prev_second = -1
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                logging.error("Failed to read frame")
                break

            timestamp = time.time()
            current_second = int(timestamp)
            if current_second != prev_second:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_landmarks, _ = self.face_detector.get_landmarks(rgb_frame)

                if face_landmarks:
                    h, w, _ = frame.shape
                    landmarks = []
                    for lm in face_landmarks.landmark:
                        landmarks.append([lm.x * w, lm.y * h, lm.z * w])  # scale x,y,z

                    session_data = SessionData(
                        session_id=str(uuid.uuid4()),
                        start_time=datetime.fromtimestamp(timestamp)
                    )

                    # Pass landmarks (list of [x,y,z]) to analyzers
                    session_data.is_blinking, session_data.blink_count = self.eye_analyzer.analyze(landmarks)
                    session_data.is_yawning, session_data.yawn_count = self.yawn_analyzer.analyze(landmarks)
                    session_data.gaze_direction = self.gaze_analyzer.analyze(landmarks)

                    # Expression analyzer works on raw frame
                    expr, expr_counts = self.expression_analyzer.detect_expression(frame)
                    session_data.current_expression = expr
                    session_data.expression_counts = expr_counts

                    keyboard_metrics = self.keyboard_analyzer.analyze()
                    session_data.typing_speed = keyboard_metrics["typing_speed"]
                    session_data.backspace_count = keyboard_metrics["backspace_count"]
                    session_data.error_count = keyboard_metrics["error_count"]

                    score, label = self.cognitive_detector.calculate_score(session_data)
                    session_data.score = score
                    session_data.label = label

                    self.session_data.append(session_data)

                    display_frame = frame.copy()
                    # Optionally draw landmarks for debugging
                    self.face_detector.draw_landmarks(display_frame, face_landmarks)
                    draw_overlays(display_frame, session_data)
                    cv2.imshow("Cognitive Overload Detection", display_frame)

                else:
                    logging.warning("No face detected in frame")

                prev_second = current_second

            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("Quit signal received")
                self.is_running = False
                break

        self.cap.release()
        cv2.destroyAllWindows()
        self.keyboard_analyzer.stop()
        self._save_session()
