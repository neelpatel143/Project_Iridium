import cv2
import mediapipe as mp
from Backend.zoom_gesture import detect_zoom
from Backend.reaction import detect_rotation
from Backend.tcp_unity import send_command


# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)

def start_gesture_detection():
    cap = cv2.VideoCapture(0)

    # Rotation tracking variables
    prev_index_finger = None
    prev_vector = None
    rotation_start_time = None
    rotation_direction = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        # Detect zoom gesture
        zoom_action = detect_zoom(result, w, h)
        if zoom_action:
            send_command(zoom_action)
            print(f"Gesture detected: {zoom_action}")
            cv2.putText(frame, f"Gesture: {zoom_action}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        # Detect rotation gesture
        prev_index_finger, prev_vector, rotation_start_time, rotation_direction = detect_rotation(
            result, w, h, prev_index_finger, prev_vector, rotation_start_time, rotation_direction
        )

        # Display frame
        cv2.imshow("Gesture Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
