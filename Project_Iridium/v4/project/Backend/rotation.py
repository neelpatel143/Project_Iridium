import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque
from tcp_unity import send_command  # Replace with actual function call

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)
mp_draw = mp.solutions.drawing_utils

# Video Capture (Single instance for both functionalities)
cap = cv2.VideoCapture(0)

# Zoom tracking variables
prev_distances = deque(maxlen=5)
last_zoom_command = None  # Track last zoom command to avoid sending opposite commands

# Rotation tracking variables
prev_index_finger = None
prev_vector = None
rotation_start_time = None
rotation_direction = None

def is_fist(landmarks, w, h):
    """Checks if a hand is making a fist."""
    finger_tips = [
        landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP.value],
        landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP.value],
        landmarks[mp_hands.HandLandmark.RING_FINGER_TIP.value],
        landmarks[mp_hands.HandLandmark.PINKY_TIP.value]
    ]
    avg_x = np.mean([ft.x * w for ft in finger_tips])
    avg_y = np.mean([ft.y * h for ft in finger_tips])
    return all(abs(ft.x * w - avg_x) < 30 and abs(ft.y * h - avg_y) < 30 for ft in finger_tips)

def is_index_finger(landmarks):
    """Checks if only the index finger is extended."""
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP.value]
    index_mcp = landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP.value]
    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP.value]
    return index_tip.y < index_mcp.y and middle_tip.y > index_mcp.y

def is_peace_sign(hand_landmarks):
    """Checks if a hand is making a peace sign (Index & Middle fingers up, others down)."""
    finger_tips = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
    ]
    folded_fingers = [
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP,
        mp_hands.HandLandmark.THUMB_TIP,
    ]
    tip_positions = [hand_landmarks.landmark[tip].y for tip in finger_tips]
    folded_positions = [hand_landmarks.landmark[tip].y for tip in folded_fingers]
    return all(tip < min(folded_positions) for tip in tip_positions)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    zoom_hand = None
    rotating_hand = None
    gesture_detected = "None"

    if result.multi_hand_landmarks and len(result.multi_hand_landmarks) == 2:
        hand1, hand2 = result.multi_hand_landmarks
        
        # Detect zoom gestures
        if is_fist(hand1.landmark, w, h):
            zoom_hand = hand2.landmark
        elif is_fist(hand2.landmark, w, h):
            zoom_hand = hand1.landmark
        elif is_index_finger(hand1.landmark):
            zoom_hand = hand2.landmark
        elif is_index_finger(hand2.landmark):
            zoom_hand = hand1.landmark
        
        if zoom_hand:
            thumb_tip = zoom_hand[mp_hands.HandLandmark.THUMB_TIP.value]
            index_tip = zoom_hand[mp_hands.HandLandmark.INDEX_FINGER_TIP.value]
            distance = np.linalg.norm(np.array([index_tip.x * w, index_tip.y * h]) - np.array([thumb_tip.x * w, thumb_tip.y * h]))
            prev_distances.append(distance)
            smoothed_distance = np.mean(prev_distances)
            if len(prev_distances) > 1 and abs(smoothed_distance - prev_distances[-2]) > 10:
                if smoothed_distance > prev_distances[-2] and last_zoom_command != "zoom_in":
                    send_command("zoom_in")
                    gesture_detected = "Zoom In"
                    last_zoom_command = "zoom_in"
                elif smoothed_distance < prev_distances[-2] and last_zoom_command != "zoom_out":
                    send_command("zoom_out")
                    gesture_detected = "Zoom Out"
                    last_zoom_command = "zoom_out"
        
        # Detect reaction gestures
        if is_peace_sign(hand1):
            rotating_hand = hand2
        elif is_peace_sign(hand2):
            rotating_hand = hand1
        
        if rotating_hand:
            index_finger = rotating_hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_finger_base = rotating_hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
            palm_center = np.array([middle_finger_base.x * w, middle_finger_base.y * h])
            index_finger_pos = np.array([index_finger.x * w, index_finger.y * h])
            if prev_index_finger is not None:
                movement_vector = index_finger_pos - prev_index_finger
                cross_product = np.cross(prev_vector, index_finger_pos - palm_center)
                if cross_product > 0:
                    if rotation_direction == "clockwise" and time.time() - rotation_start_time >= 1.5:
                        send_command("rotate_clockwise")
                        gesture_detected = "Rotate Clockwise"
                    rotation_direction = "clockwise"
                elif cross_product < 0:
                    if rotation_direction == "anticlockwise" and time.time() - rotation_start_time >= 1.5:
                        send_command("rotate_anticlockwise")
                        gesture_detected = "Rotate Anti-clockwise"
                    rotation_direction = "anticlockwise"
                rotation_start_time = time.time()
            prev_index_finger = index_finger_pos
            prev_vector = index_finger_pos - palm_center
    
    # Display gestures detected
    cv2.putText(frame, f"Gesture: {gesture_detected}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Hand Gesture Detection", frame)
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()