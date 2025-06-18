import json
import os
from typing import List
from app.models.session_data import SessionData

class SessionRepository:
    def __init__(self, json_path="session_data.json"):
        self.json_path = json_path

    def save_session(self, session_data: List[SessionData]):
        try:
            with open(self.json_path, "w") as f:
                json.dump([data.__dict__ for data in session_data], f, indent=4)
        except Exception as e:
            print(f"Error saving session: {e}")

    def load_session(self) -> List[dict]:
        if not os.path.exists(self.json_path):
            return []

        try:
            with open(self.json_path, "r") as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading session: {e}")
            return []
