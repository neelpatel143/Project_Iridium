import cv2
import mediapipe as mp
import numpy as np
import time
    
from tcp_unity import send_command  # Replace with actual function call

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.95, min_tracking_confidence=0.95)
mp_draw = mp.solutions.drawing_utils

# Variables for rotation tracking
prev_index_finger = None
prev_vector = None
rotation_start_time = None
rotation_direction = None

# Start capturing video
cap = cv2.VideoCapture(0)

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

    isCheck = False
    peace_sign_detected = False
    rotating_hand_detected = False

    if result.multi_hand_landmarks and len(result.multi_hand_landmarks) == 2:
        hand1, hand2 = result.multi_hand_landmarks
        
        if is_peace_sign(hand1):
            peace_hand, rotating_hand = hand1, hand2
        elif is_peace_sign(hand2):
            peace_hand, rotating_hand = hand2, hand1
        else:
            peace_hand, rotating_hand = None, None
        
        if peace_hand:
            peace_sign_detected = True
        
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
                    direction = "Rotate_Clockwise"
                elif cross_product < 0:
                    direction = "Rotate_Anticlockwise"
                else:
                    direction = "Stationary"
                
                if direction != "Stationary":
                    if rotation_direction == direction:
                        if time.time() - rotation_start_time >= 1.5:
                            send_command(direction.lower())
                            rotation_start_time = time.time()
                    else:
                        rotation_start_time = time.time()
                    rotation_direction = direction
                
                cv2.putText(frame, f"Rotation: {direction}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                rotating_hand_detected = True
            
            prev_index_finger = index_finger
            prev_vector = index_finger - palm_center
        
        if peace_sign_detected and rotating_hand_detected:
            isCheck = True
    
    cv2.putText(frame, f"isCheck: {isCheck}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if isCheck else (0, 0, 255), 2)
    cv2.imshow("Hand Rotation Detection", frame)
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
