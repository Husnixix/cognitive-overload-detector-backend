import cv2

def draw_overlays(frame, session_data, gaze_analyzer=None):
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.7
    thickness = 2
    color_white = (255, 255, 255)
    color_red = (0, 0, 255)
    color_green = (0, 255, 0)
    color_yellow = (0, 255, 255)
    color_blue = (255, 128, 0)
    color_cyan = (255, 255, 0)

    # Text positions
    x, y = 10, 35
    line_height = 30

    # Display counts and states
    # Blinking state and count
    blink_state = 'Yes' if getattr(session_data, 'is_blinking', False) else 'No'
    blink_color = color_green if blink_state == 'Yes' else color_white
    cv2.putText(frame, f"Blink Count: {session_data.blink_count}   Blinking: {blink_state}", (x, y), font, scale, blink_color, thickness)
    y += line_height
    # Yawning state and count
    yawn_state = 'Yes' if getattr(session_data, 'is_yawning', False) else 'No'
    yawn_color = color_green if yawn_state == 'Yes' else color_white
    cv2.putText(frame, f"Yawning Count: {session_data.yawn_count}   Yawning: {yawn_state}", (x, y), font, scale, yawn_color, thickness)
    y += line_height
    
    # Gaze direction and cumulative gaze counts
    if gaze_analyzer is not None:
        cv2.putText(frame, f"Gaze: {session_data.gaze_direction}", (x, y), font, scale, color_cyan, thickness)
        y += line_height
        cv2.putText(frame, f"Gaze Left: {gaze_analyzer.left_count}", (x+20, y), font, scale, color_cyan, thickness)
        y += line_height
        cv2.putText(frame, f"Gaze Right: {gaze_analyzer.right_count}", (x+20, y), font, scale, color_cyan, thickness)
        y += line_height
        cv2.putText(frame, f"Gaze Center: {gaze_analyzer.center_count}", (x+20, y), font, scale, color_cyan, thickness)
        y += line_height
    else:
        cv2.putText(frame, f"Gaze: {session_data.gaze_direction}", (x, y), font, scale, color_cyan, thickness)
        y += line_height

    cv2.putText(frame, f"Expression: {session_data.current_expression}", (x, y), font, scale, color_white, thickness)
    y += line_height
    cv2.putText(frame, f"Typing Speed (CPM): {session_data.typing_speed:.2f}", (x, y), font, scale, color_white, thickness)
    y += line_height
    cv2.putText(frame, f"Backspace Count: {session_data.backspace_count}", (x, y), font, scale, color_white, thickness)
    y += line_height
    cv2.putText(frame, f"Error Count: {session_data.error_count}", (x, y), font, scale, color_white, thickness)
    y += line_height

    # Cognitive load score and label
    label_color = color_green
    if session_data.overload_label.lower() == "moderate":
        label_color = color_yellow
    elif session_data.overload_label.lower() in ["overload", "high"]:
        label_color = color_red

    cv2.putText(frame, f"Cog Load Score: {session_data.cognitive_score:.2f}", (x, y), font, scale, color_white, thickness)
    y += line_height
    cv2.putText(frame, f"Label: {session_data.overload_label}", (x, y), font, scale, label_color, thickness)

    # Optionally: add a subtle border or background for better visibility (optional, not implemented here)
