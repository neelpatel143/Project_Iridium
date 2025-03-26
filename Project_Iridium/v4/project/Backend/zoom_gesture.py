import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from tcp_unity import send_command  # Replace with actual function call

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Zoom tracking variables
prev_distances = deque(maxlen=5)  # Moving average filter (last 5 distances)

# Start capturing video
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    isCheck = False
    fist_detected = False
    index_finger_detected = False

    if result.multi_hand_landmarks and len(result.multi_hand_landmarks) == 2:
        hand1, hand2 = result.multi_hand_landmarks

        # Convert landmarks to pixel coordinates
        landmarks1 = [(lm.x * w, lm.y * h) for lm in hand1.landmark]
        landmarks2 = [(lm.x * w, lm.y * h) for lm in hand2.landmark]

        def is_fist(landmarks):
            """Checks if a hand is making a fist."""
            finger_tips = [
                landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP.value],
                landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP.value],
                landmarks[mp_hands.HandLandmark.RING_FINGER_TIP.value],
                landmarks[mp_hands.HandLandmark.PINKY_TIP.value]
            ]
            avg_x = np.mean([ft[0] for ft in finger_tips])
            avg_y = np.mean([ft[1] for ft in finger_tips])
            return all(abs(ft[0] - avg_x) < 30 and abs(ft[1] - avg_y) < 30 for ft in finger_tips)

        def is_index_finger(landmarks):
            """Checks if only the index finger is extended."""
            index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP.value]
            index_mcp = landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP.value]
            middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP.value]

            return index_tip[1] < index_mcp[1] and middle_tip[1] > index_mcp[1]

        # Detect which hand is making a fist or showing index finger
        if is_fist(landmarks1):
            fist_detected = True
            zoom_hand = landmarks2  # Other hand controls zoom
        elif is_fist(landmarks2):
            fist_detected = True
            zoom_hand = landmarks1
        elif is_index_finger(landmarks1):
            index_finger_detected = True
            zoom_hand = landmarks2
        elif is_index_finger(landmarks2):
            index_finger_detected = True
            zoom_hand = landmarks1
        else:
            zoom_hand = None

        # If one hand is a fist or index finger, the other hand controls zoom
        if (fist_detected or index_finger_detected) and zoom_hand:
            thumb_tip = zoom_hand[mp_hands.HandLandmark.THUMB_TIP.value]
            index_tip = zoom_hand[mp_hands.HandLandmark.INDEX_FINGER_TIP.value]

            # Calculate distance between thumb and index finger
            distance = np.linalg.norm(np.array(index_tip) - np.array(thumb_tip))

            # Apply moving average filter for smoother detection
            prev_distances.append(distance)
            smoothed_distance = np.mean(prev_distances)

            if len(prev_distances) > 1:
                distance_change = smoothed_distance - prev_distances[-2]

                if abs(distance_change) > 10:  # Ignore small changes
                    if fist_detected and distance_change > 0:
                        direction = "zoom_in"
                    elif index_finger_detected and distance_change < 0:
                        direction = "zoom_out"
                    else:
                        direction = None

                    if direction:
                        send_command(direction)
                        print(f"Gesture detected: {direction}")
                        cv2.putText(frame, f"Gesture: {direction}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        isCheck = True

    # Display status
    cv2.putText(frame, f"isCheck: {isCheck}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if isCheck else (0, 0, 255), 2)
    cv2.putText(frame, f"Fist: {fist_detected}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0) if fist_detected else (0, 0, 255), 2)
    cv2.putText(frame, f"Index: {index_finger_detected}", (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0) if index_finger_detected else (0, 0, 255), 2)

    cv2.imshow("Zoom Gesture Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
