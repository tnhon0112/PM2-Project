import cv2
import mediapipe as mp
from pynput.keyboard import Key, Controller

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Initialize Keyboard Controller
keyboard = Controller()

# Start Video Capture (0 is usually your default laptop webcam)
cap = cv2.VideoCapture(0)

# State variables so we don't spam keys
is_jumping = False
is_crouching = False

print("Starting camera... Stand in front of the camera!")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
        
    # Flip image horizontally for a natural mirror-like view
    frame = cv2.flip(frame, 1)
    
    # Convert the BGR image to RGB as required by MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    # Draw a line on the screen to show the "neutral" zone
    height, width, _ = frame.shape
    cv2.line(frame, (0, int(height * 0.3)), (width, int(height * 0.3)), (0, 255, 0), 2)  # Jump line
    cv2.line(frame, (0, int(height * 0.7)), (width, int(height * 0.7)), (0, 0, 255), 2)  # Crouch line

    if results.pose_landmarks:
        # Draw skeleton on the camera feed
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        # Get the Y coordinate of the NOSE (0.0 is top of screen, 1.0 is bottom)
        nose = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
        y_pos = nose.y 

        # --- LOGIC FOR JUMPING AND CROUCHING ---
        # Adjust these thresholds based on how far back you stand from the camera
        JUMP_THRESHOLD = 0.3     # If nose goes above the top 30% of the screen
        CROUCH_THRESHOLD = 0.7   # If nose goes below the bottom 30% of the screen

        # Check for Jump
        if y_pos < JUMP_THRESHOLD and not is_jumping:
            print("JUMP!")
            keyboard.release(Key.down) # Release crouch just in case
            keyboard.press(Key.up)
            is_jumping = True
            is_crouching = False

        # Check for Crouch
        elif y_pos > CROUCH_THRESHOLD and not is_crouching:
            print("CROUCH!")
            keyboard.release(Key.up)
            keyboard.press(Key.down)
            is_crouching = True
            is_jumping = False

        # Reset to Neutral position (standing normally)
        elif JUMP_THRESHOLD <= y_pos <= CROUCH_THRESHOLD:
            if is_jumping:
                keyboard.release(Key.up)
                is_jumping = False
            if is_crouching:
                keyboard.release(Key.down)
                is_crouching = False

    # Show the camera feed
    cv2.imshow('T-Rex Motion Controller', frame)

    # Press 'q' to quit the camera window
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()