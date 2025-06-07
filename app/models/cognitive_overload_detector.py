class CognitiveOverloadDetector:
    def __init__(self):
        self.score = 0
        self.label = "normal"

    def calculate_score(self, data):
        # Weights for each cue (tune these empirically or from research)
        weights = {
            "blink": 1,
            "yawn": 2,
            "gaze": 1,
            "expression": 2,
            "typing_speed": -1,
            "backspace": 1,
            "error": 1
        }

        # Score components
        blink_score = data.blink_count * weights["blink"]
        yawn_score = data.yawn_count * weights["yawn"]
        gaze_score = 1 if data.gaze_direction != "Center" else 0
        expression_score = 0 if data.current_expression == "neutral" else weights["expression"]
        backspace_score = data.backspace_count * weights["backspace"]
        error_score = data.error_count * weights["error"]

        # Typing speed penalty (if it's too slow)
        typing_penalty = weights["typing_speed"] if data.typing_speed < 100 else 0

        # Total cognitive score
        self.score = (
            blink_score +
            yawn_score +
            gaze_score +
            expression_score +
            backspace_score +
            error_score +
            typing_penalty
        )

        # Label based on thresholds
        if self.score < 3:
            self.label = "normal"
        elif 3 <= self.score < 6:
            self.label = "moderate"
        else:
            self.label = "overload"

        return self.score, self.label
