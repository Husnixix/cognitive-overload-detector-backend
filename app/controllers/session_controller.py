from threading import Lock
from app.repositary.session_repository import SessionRepository
from app.services.session_manager import SessionManager

class SessionController:
    def __init__(self):
        self.session_manager = None
        self.session_repo = SessionRepository()
        self.lock = Lock()

    def start_session(self):
        with self.lock:
            if self.session_manager and self.session_manager.is_running:
                return {"status": "error", "message": "Session already running"}

            self.session_manager = SessionManager()
            self.session_manager.start()
            return {"status": "success", "message": "Session started"}

    def stop_session(self):
        with self.lock:
            if not self.session_manager or not self.session_manager.is_running:
                return {"status": "error", "message": "No active session to stop"}

            self.session_manager.stop()
            return {"status": "success", "message": "Session stopped"}

    def get_session_data(self):
        # For now retrieve last saved session from JSON repo
        data = self.session_repo.load_session()
        return data
