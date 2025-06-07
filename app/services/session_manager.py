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
        if self.thread:
            self.thread.join()
        self.cap.release()
        self.keyboard_analyzer.stop()
        cv2.destroyAllWindows()
        self._save_session()
        logging.info("Session stopped and data saved")

    def _save_session(self):
        try:
            # Use the to_dict() method for proper serialization
            serializable_data = [data.to_dict() for data in self.session_data]

            with open(self.json_path, "w") as f:
                json.dump(serializable_data, f, indent=4)
            logging.info(f"Session data saved to {self.json_path}")
        except Exception as e:
            logging.error(f"Error saving session data: {e}")

    def load_session(self):
        """Load session data from JSON file"""
        try:
            with open(self.json_path, "r") as f:
                data_list = json.load(f)

            self.session_data = [SessionData.from_dict(data) for data in data_list]
            logging.info(f"Loaded {len(self.session_data)} session records")
            return self.session_data
        except FileNotFoundError:
            logging.warning(f"Session file {self.json_path} not found")
            return []
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON: {e}")
            return []
        except Exception as e:
            logging.error(f"Error loading session: {e}")
            return []

    def _run(self):
        prev_second = -1
        # --- Cumulative metrics for 60s interval ---
        cumulative_blinks = 0
        cumulative_yawns = 0
        cumulative_typing_speed = 0.0
        cumulative_backspace = 0
        cumulative_error = 0
        cumulative_frames = 0
        interval_start_time = time.time()
        last_score = 0.0
        last_label = "Normal"

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

                    # Update analyzers and accumulate metrics
                    is_blinking, blink_count = self.eye_analyzer.analyze(landmarks)
                    is_yawning, yawn_count = self.yawn_analyzer.analyze(landmarks)
                    gaze_direction = self.gaze_analyzer.analyze(landmarks)

                    expr, expr_counts = self.expression_analyzer.detect_expression(frame)
                    keyboard_metrics = self.keyboard_analyzer.analyze()

                    cumulative_blinks = blink_count
                    cumulative_yawns = yawn_count
                    cumulative_typing_speed += keyboard_metrics["typing_speed"]
                    cumulative_backspace += keyboard_metrics["backspace_count"]
                    cumulative_error += keyboard_metrics["error_count"]
                    cumulative_frames += 1

                    # Score and reset every 60 seconds
                    if timestamp - interval_start_time >= 60 or cumulative_frames == 1:
                        avg_typing_speed = cumulative_typing_speed / max(1, cumulative_frames)
                        # Create a session data snapshot for scoring
                        session_data = SessionData(
                            session_id=str(uuid.uuid4()),
                            start_time=datetime.fromtimestamp(interval_start_time),
                            end_time=datetime.fromtimestamp(timestamp),
                            blink_count=cumulative_blinks,
                            is_blinking=is_blinking,
                            yawn_count=cumulative_yawns,
                            is_yawning=is_yawning,
                            gaze_direction=gaze_direction,
                            current_expression=expr,
                            expression_counts=expr_counts,
                            typing_speed=avg_typing_speed,
                            error_count=cumulative_error,
                            backspace_count=cumulative_backspace,
                            cognitive_score=last_score,
                            overload_label=last_label
                        )
                        # Add gaze counts
                        session_data.gaze_left_count = self.gaze_analyzer.left_count
                        session_data.gaze_right_count = self.gaze_analyzer.right_count
                        session_data.gaze_center_count = self.gaze_analyzer.center_count

                        # Calculate cognitive overload score and label
                        score, label = self.cognitive_detector.calculate_score(session_data)
                        last_score = score
                        last_label = label
                        session_data.cognitive_score = score
                        session_data.overload_label = label
                        self.session_data.append(session_data)

                        # Reset interval counters
                        cumulative_blinks = 0
                        cumulative_yawns = 0
                        cumulative_typing_speed = 0.0
                        cumulative_backspace = 0
                        cumulative_error = 0
                        cumulative_frames = 0
                        interval_start_time = timestamp
                        self.eye_analyzer.blink_count = 0
                        self.yawn_analyzer.yawn_count = 0
                        self.gaze_analyzer.reset_counters()

                    # Prepare display overlay with current values
                    display_frame = frame.copy()
                    # Draw only minimal landmarks (eyes and mouth) for clarity
                    # (Optional: implement minimal landmark drawing in FaceDetector)
                    # self.face_detector.draw_landmarks(display_frame, face_landmarks, minimal=True)
                    draw_overlays(display_frame, session_data, gaze_analyzer=self.gaze_analyzer)
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