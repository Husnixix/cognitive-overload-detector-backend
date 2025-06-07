from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime

@dataclass
class SessionData:
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None

    # Facial cues
    blink_count: int = 0
    is_blinking: bool = False

    yawn_count: int = 0
    is_yawning: bool = False

    gaze_direction: str = "Center"  # Left / Right / Center

    current_expression: str = "Neutral"
    expression_counts: Dict[str, int] = field(default_factory=lambda: {
        "happy": 0,
        "sad": 0,
        "angry": 0,
        "surprise": 0,
        "neutral": 0,
        "disgust": 0,
        "fear": 0
    })

    # Keyboard metrics
    typing_speed: float = 0.0  # characters per minute
    error_count: int = 0
    backspace_count: int = 0

    # Cognitive overload analysis
    cognitive_score: float = 0.0
    overload_label: str = "Normal"  # Normal / Mild / High

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "blink_count": self.blink_count,
            "is_blinking": self.is_blinking,
            "yawn_count": self.yawn_count,
            "is_yawning": self.is_yawning,
            "gaze_direction": self.gaze_direction,
            "current_expression": self.current_expression,
            "expression_counts": self.expression_counts,
            "typing_speed": self.typing_speed,
            "error_count": self.error_count,
            "backspace_count": self.backspace_count,
            "cognitive_score": self.cognitive_score,
            "overload_label": self.overload_label
        }

    @staticmethod
    def from_dict(data):
        return SessionData(
            session_id=data["session_id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
            blink_count=data.get("blink_count", 0),
            is_blinking=data.get("is_blinking", False),
            yawn_count=data.get("yawn_count", 0),
            is_yawning=data.get("is_yawning", False),
            gaze_direction=data.get("gaze_direction", "Center"),
            current_expression=data.get("current_expression", "Neutral"),
            expression_counts=data.get("expression_counts", {}),
            typing_speed=data.get("typing_speed", 0.0),
            error_count=data.get("error_count", 0),
            backspace_count=data.get("backspace_count", 0),
            cognitive_score=data.get("cognitive_score", 0.0),
            overload_label=data.get("overload_label", "Normal")
        )
