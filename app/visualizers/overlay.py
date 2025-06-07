import cv2

def draw_overlays(frame, session_data):
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.6
    thickness = 2
    color_white = (255, 255, 255)
    color_red = (0, 0, 255)
    color_green = (0, 255, 0)
    color_yellow = (0, 255, 255)

    # Text positions
    x, y = 10, 30
    line_height = 25

    # Display counts and states
    cv2.putText(frame, f"Blink Count: {session_data.blink_count}", (x, y), font, scale, color_white, thickness)
    y += line_height
    cv2.putText(frame, f"Yawning Count: {session_data.yawn_count}", (x, y), font, scale, color_white, thickness)
    y += line_height
    cv2.putText(frame, f"Gaze Direction: {session_data.gaze_direction}", (x, y), font, scale, color_white, thickness)
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
    if session_data.label == "moderate":
        label_color = color_yellow
    elif session_data.label == "overload":
        label_color = color_red

    cv2.putText(frame, f"Cog Load Score: {session_data.score:.2f}", (x, y), font, scale, color_white, thickness)
    y += line_height
    cv2.putText(frame, f"Label: {session_data.label}", (x, y), font, scale, label_color, thickness)
