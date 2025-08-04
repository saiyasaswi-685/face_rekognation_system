#test_camera.py
import cv2

cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("❌ Could not open camera. Try a different index (1 or 2).")
else:
    print("✅ Camera opened successfully!")
    cam.release()
