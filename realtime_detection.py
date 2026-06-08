import cv2
import os
from datetime import datetime
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from ultralytics import YOLO
from pose_classifier import classify_pose
import smtplib
from email.message import EmailMessage

import threading
from send_email import send_fall_email


def send_email_async(image_path):
    threading.Thread(
        target=send_fall_email,
        args=(image_path,),
        daemon=True
    ).start()

# ==========================
# CHỌN VIDEO
# ==========================
root = Tk()
root.withdraw()

video_path = askopenfilename(
    title="Chọn video",
    filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")]
)

if not video_path:
    exit()

# ==========================
# THƯ MỤC LƯU ẢNH NGÃ
# ==========================
os.makedirs("fall_snapshots", exist_ok=True)

# ==========================
# LOAD MODEL
# ==========================
model = YOLO("models/yolov8n-pose.pt")

cap = cv2.VideoCapture(video_path)

# Tránh lưu nhiều ảnh cho cùng một lần ngã
fall_saved = False

while True:

    ret, frame = cap.read()

    if not ret:
        break

    results = model(frame, verbose=False)

    fall_detected = False

    if len(results):

        result = results[0]

        if result.keypoints is not None:

            persons = result.keypoints.xy.cpu().numpy()

            for person in persons:

                status = classify_pose(person)

                valid = person[
                    (person[:, 0] > 0) &
                    (person[:, 1] > 0)
                ]

                if len(valid) < 5:
                    continue

                min_x = int(valid[:, 0].min())
                min_y = int(valid[:, 1].min())
                max_x = int(valid[:, 0].max())
                max_y = int(valid[:, 1].max())

                # ==========================
                # CHỌN MÀU
                # ==========================
                if status == "STANDING":
                    color = (0, 255, 0)

                elif status == "BENDING":
                    color = (0, 165, 255)

                elif status == "SITTING":
                    color = (0, 255, 255)

                elif status == "FALL":
                    color = (0, 0, 255)

                else:
                    color = (255, 255, 255)

                # ==========================
                # BOX
                # ==========================
                cv2.rectangle(
                    frame,
                    (min_x, min_y),
                    (max_x, max_y),
                    color,
                    2
                )

                # ==========================
                # LABEL
                # ==========================
                cv2.putText(
                    frame,
                    str(status),
                    (min_x, min_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    color,
                    2
                )

                # ==========================
                # KEYPOINTS
                # ==========================
                for px, py in valid:

                    cv2.circle(
                        frame,
                        (int(px), int(py)),
                        4,
                        (0, 0, 255),
                        -1
                    )

                # ==========================
                # FALL DETECTION
                # ==========================
                if status == "FALL":

                    fall_detected = True

                    cv2.putText(
                        frame,
                        "FALL DETECTED!",
                        (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2,
                        (0, 0, 255),
                        3
                    )

                    # Snapshot chỉ 1 lần
                    if not fall_saved:

                        timestamp = datetime.now().strftime(
                            "%Y%m%d_%H%M%S"
                        )

                        filename = (
                            f"fall_snapshots/"
                            f"FALL_{timestamp}.jpg"
                        )

                        snapshot = frame.copy()

                        cv2.imwrite(
                            filename,
                            snapshot
                        )

                        print(
                            f"[ALERT] Fall detected! "
                            f"Saved: {filename}"
                        )
                        send_email_async(filename)
                        fall_saved = True

    # Reset khi không còn ai ngã
    if not fall_detected:
        fall_saved = False

    # ==========================
    # HIỂN THỊ VIDEO
    # ==========================
    cv2.imshow(
        "Pose Detection & Fall Detection",
        frame
    )

    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# ==========================
# GIẢI PHÓNG
# ==========================
cap.release()
cv2.destroyAllWindows()