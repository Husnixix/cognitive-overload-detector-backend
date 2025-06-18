import cv2
import mediapipe as mp

class FaceDetector:
    def __init__(self, max_faces=1):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=max_faces,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

    def get_landmarks(self, frame_rgb):
        """
        Detects facial landmarks from an RGB frame.
        Returns: (face_landmarks, results)
        """
        results = self.face_mesh.process(frame_rgb)
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0], results  # First face only
        return None, results

    def draw_landmarks(self, frame_bgr, face_landmarks):
        """
        Draws facial landmarks on the frame (for visualization).
        """
        self.mp_drawing.draw_landmarks(
            image=frame_bgr,
            landmark_list=face_landmarks,
            connections=self.mp_face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=self.drawing_spec,
            connection_drawing_spec=self.drawing_spec
        )
