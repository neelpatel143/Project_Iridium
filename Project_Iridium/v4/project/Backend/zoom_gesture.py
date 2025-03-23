import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from .tcp_unity import send_command  # Replace with actual function call

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Zoom tracking variables
prev_distances = deque(maxlen=5)  # Moving average filter (last 5 distances)

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

def detect_zoom(result, w, h):
    """
    Detects zoom gestures based on hand positions.
    Returns 'zoom_in', 'zoom_out', or None.
    """
    zoom_hand = None
    zoom_type = None

    if result.multi_hand_landmarks and len(result.multi_hand_landmarks) == 2:
        hand1, hand2 = result.multi_hand_landmarks

        if is_fist(hand1.landmark, w, h):
            zoom_hand = hand2.landmark  # Other hand controls zoom
            zoom_type = "zoom_in"
        elif is_fist(hand2.landmark, w, h):
            zoom_hand = hand1.landmark
            zoom_type = "zoom_in"
        elif is_index_finger(hand1.landmark):
            zoom_hand = hand2.landmark
            zoom_type = "zoom_out"
        elif is_index_finger(hand2.landmark):
            zoom_hand = hand1.landmark
            zoom_type = "zoom_out"

        if zoom_hand:
            thumb_tip = zoom_hand[mp_hands.HandLandmark.THUMB_TIP.value]
            index_tip = zoom_hand[mp_hands.HandLandmark.INDEX_FINGER_TIP.value]

            # Calculate distance between thumb and index finger
            distance = np.linalg.norm(np.array([index_tip.x * w, index_tip.y * h]) - 
                                      np.array([thumb_tip.x * w, thumb_tip.y * h]))

            # Apply moving average filter for smoother detection
            prev_distances.append(distance)
            smoothed_distance = np.mean(prev_distances)

            if len(prev_distances) > 1:
                distance_change = smoothed_distance - prev_distances[-2]

                # Fist gesture should always zoom in (increase distance)
                if zoom_type == "zoom_in" and distance_change > 10:
                    return "zoom_in"
                # Index finger gesture should always zoom out (decrease distance)
                elif zoom_type == "zoom_out" and distance_change < -10:
                    return "zoom_out"

    return None
