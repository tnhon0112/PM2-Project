import cv2
import pygame

from ui import CAM_HEIGHT, CAM_WIDTH

# Smallest face size the detector should treat as a valid face (Increase to be more precise)
MIN_FACE_SIZE = 45
# Minimum detected motion area needed to count as a high-five gesture
HIGH_FIVE_MOTION_AREA = 2500


class CameraController:
    def __init__(self, camera_index = 0):
        # syntax for opening a camera stream.
        self.cap = cv2.VideoCapture(camera_index)
        # syntax for loading a face-detection model (pretrained model)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        # syntax for motion detection
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(history = 120, varThreshold = 35, detectShadows = False)
        # default face height
        self.neutral_y = 0.5
        # default thresholds for jump and duck relative to the camera view
        self.jump_threshold = 0.38
        self.duck_threshold = 0.62

    def update_thresholds(self, new_neutral_y):
        # Let the neutral zone move up and down with the player's face, but keep it within reason so the game remains playable
        self.neutral_y = max(0.28, min(0.72, new_neutral_y))
        # Place the jump line a little above neutral
        self.jump_threshold = max(0.20, self.neutral_y - 0.12)
        # Place the duck line a little below neutral
        self.duck_threshold = min(0.82, self.neutral_y + 0.12)

    def detect_face(self, gray_frame):
        # syntax that returns matching rectangles around the face, return (x,y,w,h)
        faces = self.face_cascade.detectMultiScale(gray_frame , scaleFactor = 1.1 , minNeighbors = 5, minSize = (MIN_FACE_SIZE, MIN_FACE_SIZE))
        # Return nothing if no face is currently visible
        if len(faces) == 0:
            return None
        # Use the largest detected face, which is usually the player closest to the camera
        return max(faces, key=lambda box: box[2] * box[3])
    def detect_high_five(self, gray_frame, face_box):
        # If no face is found, only update the background model and skip gesture detection.
        if face_box is None:
            # `.apply(...)` is OpenCV background-subtractor syntax for updating the motion model.
            self.background_subtractor.apply(gray_frame, learningRate=0.05)
            return False, None

        # Unpack the face position so we can search for motion above and beside it.
        x, y, w, _ = face_box
        # This OpenCV call builds a foreground mask that highlights recent motion.
        mask = self.background_subtractor.apply(gray_frame, learningRate=0.01)
        # `cv2.threshold(...)` is OpenCV image-processing syntax for binarizing the mask.
        _, mask = cv2.threshold(mask, 220, 255, cv2.THRESH_BINARY)
        # `cv2.medianBlur(...)` is OpenCV syntax for reducing noise in the image.
        mask = cv2.medianBlur(mask, 5)

        # Focus on the area above the face where a raised hand is expected.
        top_limit = max(0, y - 80)
        roi = mask[0:top_limit if top_limit > 0 else 1, :]
        # If there is no usable region above the face, return early.
        if roi.size == 0:
            return False, mask

        # Count moving pixels in the full region above the face.
        motion_area = int(cv2.countNonZero(roi))
        return motion_area > HIGH_FIVE_MOTION_AREA, mask

    def build_camera_surface(self, frame_bgr, face_box, face_y, motion_mask):
        # OpenCV syntax for scaling the camera frame
        frame = cv2.resize(frame_bgr, (CAM_WIDTH, CAM_HEIGHT))

        # Convert normalized thresholds into actual y-coordinates on screen
        jump_line_y = int(self.jump_threshold * CAM_HEIGHT)
        duck_line_y = int(self.duck_threshold * CAM_HEIGHT)
        zone_top = min(jump_line_y, duck_line_y)
        zone_bottom = max(jump_line_y, duck_line_y)

        # `frame.copy()` and the OpenCV drawing calls below are used to build the camera overlay.
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, zone_top), (CAM_WIDTH, zone_bottom), (180, 230, 255), -1)
        # `cv2.addWeighted(...)` is OpenCV syntax for blending the overlay with the frame.
        frame = cv2.addWeighted(overlay, 0.22, frame, 0.78, 0)

        # `cv2.rectangle(...)` is OpenCV drawing syntax for the face box.
        if face_box is not None:
            x, y, w, h = face_box
            scale_x = CAM_WIDTH / frame_bgr.shape[1]
            scale_y = CAM_HEIGHT / frame_bgr.shape[0]
            cv2.rectangle(
                frame,
                (int(x * scale_x), int(y * scale_y)),
                (int((x + w) * scale_x), int((y + h) * scale_y)),
                (40, 160, 70),
                2,
            )

        # `cv2.line(...)` and `cv2.putText(...)` are OpenCV drawing/text syntax.
        cv2.line(frame, (0, jump_line_y), (CAM_WIDTH, jump_line_y), (0, 215, 255), 2)
        cv2.line(frame, (0, duck_line_y), (CAM_WIDTH, duck_line_y), (0, 215, 255), 2)
        cv2.putText(
            frame,
            "Neutral Zone",
            (8, max(zone_top - 10, 18)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 80, 120),
            1,
            cv2.LINE_AA,
        )

        # `cv2.circle(...)` is OpenCV drawing syntax for the face-position marker.
        if face_y is not None:
            cv2.circle(frame, (CAM_WIDTH - 16, int(face_y * CAM_HEIGHT)), 7, (50, 70, 220), -1)

        # `cv2.cvtColor(...)` converts the grayscale mask into a color image for display.
        if motion_mask is not None:
            small_mask = cv2.resize(motion_mask, (CAM_WIDTH // 4, CAM_HEIGHT // 4))
            small_mask_bgr = cv2.cvtColor(small_mask, cv2.COLOR_GRAY2BGR)
            frame[
                CAM_HEIGHT - small_mask_bgr.shape[0]:CAM_HEIGHT,
                CAM_WIDTH - small_mask_bgr.shape[1]:CAM_WIDTH,
            ] = small_mask_bgr

        # These OpenCV conversions prepare the image, then `pygame.surfarray.make_surface(...)`
        # is pygame syntax that turns the processed frame into something pygame can draw.
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.transpose(frame)
        return pygame.surfarray.make_surface(frame)

    def get_camera_state(self):
        # `.read()` is OpenCV camera syntax for grabbing the newest frame.
        ret, frame = self.cap.read()
        # `pygame.K_UP` and `pygame.K_DOWN` are pygame key constants used by the rest of the game.
        camera_input = {pygame.K_UP: False, pygame.K_DOWN: False}
        # If the camera fails, return a safe fallback state.
        if not ret:
            return {
                "camera_input": camera_input,
                "cam_surface": None,
                "face_y": None,
                "neutral_ok": False,
                "high_five": False,
                "camera_ready": False,
            }

        # `cv2.flip(...)` is OpenCV syntax for mirroring the camera image.
        frame = cv2.flip(frame, 1)
        # `cv2.cvtColor(...)` and `cv2.equalizeHist(...)` are OpenCV preprocessing syntax.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        # Detect the player's face in the current frame.
        face_box = self.detect_face(gray)
        face_y = None
        # Convert the face center into a normalized vertical position from 0 to 1.
        if face_box is not None:
            _, y, _, h = face_box
            face_y = (y + (h / 2)) / gray.shape[0]

        # Trigger movement keys when the face moves above or below the neutral zone.
        if face_y is not None:
            if face_y < self.jump_threshold:
                camera_input[pygame.K_UP] = True
            elif face_y > self.duck_threshold:
                camera_input[pygame.K_DOWN] = True

        # Check for a high-five gesture and generate the debug motion mask.
        high_five, motion_mask = self.detect_high_five(gray, face_box)
        # Build the annotated camera preview used by the UI.
        cam_surface = self.build_camera_surface(frame, face_box, face_y, motion_mask)

        # Return the full camera state needed by the rest of the game.
        return {
            "camera_input": camera_input,
            "cam_surface": cam_surface,
            "face_y": face_y,
            "neutral_ok": face_y is not None and self.jump_threshold <= face_y <= self.duck_threshold,
            "high_five": high_five,
            "camera_ready": True,
        }

    def cleanup(self):
        # `.release()` is OpenCV camera syntax for freeing the webcam device.
        if self.cap.isOpened():
            self.cap.release()
        # `cv2.destroyAllWindows()` is OpenCV syntax for closing any OpenCV windows.
        cv2.destroyAllWindows()
