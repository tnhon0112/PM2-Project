import cv2
import pygame

from ui import CAM_HEIGHT, CAM_WIDTH

MIN_FACE_SIZE = 45
HIGH_FIVE_MOTION_AREA = 2500


class CameraController:
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=120, varThreshold=35, detectShadows=False
        )
        self.neutral_y = 0.5
        self.jump_threshold = 0.38
        self.duck_threshold = 0.62

    def update_thresholds(self, new_neutral_y):
        self.neutral_y = max(0.28, min(0.72, new_neutral_y))
        self.jump_threshold = max(0.20, self.neutral_y - 0.12)
        self.duck_threshold = min(0.82, self.neutral_y + 0.12)

    def detect_face(self, gray_frame):
        faces = self.face_cascade.detectMultiScale(
            gray_frame,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(MIN_FACE_SIZE, MIN_FACE_SIZE),
        )
        if len(faces) == 0:
            return None

        return max(faces, key=lambda box: box[2] * box[3])

    def detect_high_five(self, gray_frame, face_box):
        if face_box is None:
            self.background_subtractor.apply(gray_frame, learningRate=0.05)
            return False, None

        x, y, w, _ = face_box
        mask = self.background_subtractor.apply(gray_frame, learningRate=0.01)
        _, mask = cv2.threshold(mask, 220, 255, cv2.THRESH_BINARY)
        mask = cv2.medianBlur(mask, 5)

        top_limit = max(0, y - 80)
        roi = mask[0:top_limit if top_limit > 0 else 1, :]
        if roi.size == 0:
            return False, mask

        left_bound = max(0, x - w)
        right_bound = min(mask.shape[1], x + (2 * w))
        side_roi = roi[:, left_bound:right_bound]
        motion_area = int(cv2.countNonZero(side_roi))
        return motion_area > HIGH_FIVE_MOTION_AREA, mask

    def build_camera_surface(self, frame_bgr, face_box, face_y, motion_mask):
        frame = cv2.resize(frame_bgr, (CAM_WIDTH, CAM_HEIGHT))

        jump_line_y = int(self.jump_threshold * CAM_HEIGHT)
        duck_line_y = int(self.duck_threshold * CAM_HEIGHT)
        zone_top = min(jump_line_y, duck_line_y)
        zone_bottom = max(jump_line_y, duck_line_y)

        overlay = frame.copy()
        cv2.rectangle(overlay, (0, zone_top), (CAM_WIDTH, zone_bottom), (180, 230, 255), -1)
        frame = cv2.addWeighted(overlay, 0.22, frame, 0.78, 0)

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

        if face_y is not None:
            cv2.circle(frame, (CAM_WIDTH - 16, int(face_y * CAM_HEIGHT)), 7, (50, 70, 220), -1)

        if motion_mask is not None:
            small_mask = cv2.resize(motion_mask, (CAM_WIDTH // 4, CAM_HEIGHT // 4))
            small_mask_bgr = cv2.cvtColor(small_mask, cv2.COLOR_GRAY2BGR)
            frame[
                CAM_HEIGHT - small_mask_bgr.shape[0]:CAM_HEIGHT,
                CAM_WIDTH - small_mask_bgr.shape[1]:CAM_WIDTH,
            ] = small_mask_bgr

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.transpose(frame)
        return pygame.surfarray.make_surface(frame)

    def get_camera_state(self):
        ret, frame = self.cap.read()
        camera_input = {pygame.K_UP: False, pygame.K_DOWN: False}
        if not ret:
            return {
                "camera_input": camera_input,
                "cam_surface": None,
                "face_y": None,
                "neutral_ok": False,
                "high_five": False,
                "camera_ready": False,
            }

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        face_box = self.detect_face(gray)
        face_y = None
        if face_box is not None:
            _, y, _, h = face_box
            face_y = (y + (h / 2)) / gray.shape[0]

        if face_y is not None:
            if face_y < self.jump_threshold:
                camera_input[pygame.K_UP] = True
            elif face_y > self.duck_threshold:
                camera_input[pygame.K_DOWN] = True

        high_five, motion_mask = self.detect_high_five(gray, face_box)
        cam_surface = self.build_camera_surface(frame, face_box, face_y, motion_mask)

        return {
            "camera_input": camera_input,
            "cam_surface": cam_surface,
            "face_y": face_y,
            "neutral_ok": face_y is not None and self.jump_threshold <= face_y <= self.duck_threshold,
            "high_five": high_five,
            "camera_ready": True,
        }

    def cleanup(self):
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
