import cv2
import mediapipe as mp
import numpy as np
import time
from .tcp_unity import send_command  # Replace with actual function call

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)

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

def detect_rotation(result, w, h, prev_index_finger, prev_vector, rotation_start_time, rotation_direction):
    """
    Detects rotation gestures when a peace sign is held and the other hand rotates.
    Returns updated tracking values and the detected direction ('rotate_clockwise', 'rotate_anticlockwise', or None).
    """
    if result.multi_hand_landmarks and len(result.multi_hand_landmarks) == 2:
        hand1, hand2 = result.multi_hand_landmarks

        # Identify Peace Sign and Rotating Hand
        if is_peace_sign(hand1):
            peace_hand, rotating_hand = hand1, hand2
        elif is_peace_sign(hand2):
            peace_hand, rotating_hand = hand2, hand1
        else:
            peace_hand, rotating_hand = None, None

        if rotating_hand:
            wrist = rotating_hand.landmark[mp_hands.HandLandmark.WRIST]
            index_finger = rotating_hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_finger_base = rotating_hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
            
            wrist = np.array([int(wrist.x * w), int(wrist.y * h)])
            index_finger = np.array([int(index_finger.x * w), int(index_finger.y * h)])
            palm_center = np.array([int(middle_finger_base.x * w), int(middle_finger_base.y * h)])

            if prev_index_finger is not None:
                movement_vector = index_finger - prev_index_finger
                relative_vector = index_finger - palm_center
                cross_product = np.cross(prev_vector, relative_vector)
                
                if cross_product > 0:
                    direction = "rotate_clockwise"
                elif cross_product < 0:
                    direction = "rotate_anticlockwise"
                else:
                    direction = None

                if direction:
                    if rotation_direction == direction:
                        if time.time() - rotation_start_time >= 0.5:
                            send_command(direction)
                            rotation_start_time = time.time()
                    else:
                        rotation_start_time = time.time()
                    rotation_direction = direction

            prev_index_finger = index_finger
            prev_vector = index_finger - palm_center

    return prev_index_finger, prev_vector, rotation_start_time, rotation_direction
