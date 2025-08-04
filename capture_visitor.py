#capture_visitor.py
import cv2
import boto3
import uuid
import os

# --- AWS S3 Configuration ---
BUCKET_NAME = "face-rekognition-system"  # 🔁 Replace with your actual bucket name
UPLOAD_FOLDER = "uploads/"  # Folder path in S3 bucket

# --- Initialize Boto3 S3 client ---
s3 = boto3.client('s3')

# --- Create Local Save Directory (Optional) ---
os.makedirs("authorized_faces", exist_ok=True)

# --- Load Haar Cascade Classifier ---
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# --- Start Webcam ---
cap = cv2.VideoCapture(0)

print("✅ Press 'c' to capture faces, 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to read frame from webcam.")
        break

    # Detect faces
    faces = face_cascade.detectMultiScale(frame, scaleFactor=1.2, minNeighbors=5)

    # Draw rectangle around detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display frame
    cv2.imshow("Smart Visitor Face Capture", frame)

    key = cv2.waitKey(1)

    if key == ord('c'):
        if len(faces) == 0:
            print("⚠ No face detected. Try again.")
        else:
            print(f"🔍 Detected {len(faces)} face(s). Uploading...")
            for i, (x, y, w, h) in enumerate(faces):
                face_crop = frame[y:y+h, x:x+w]
                filename = f"{uuid.uuid4()}.jpg"
                local_path = os.path.join("authorized_faces", filename)

                # Save locally
                cv2.imwrite(local_path, face_crop)

                # Upload to S3
                try:
                    with open(local_path, "rb") as f:
                        s3.upload_fileobj(f, BUCKET_NAME, UPLOAD_FOLDER + filename)
                    print(f"✅ Uploaded face {i+1} as {filename} to S3 → {UPLOAD_FOLDER}")
                except Exception as e:
                    print(f"❌ Failed to upload to S3: {e}")

    elif key == ord('q'):
        print("🔒 Exiting capture session.")
        break

cap.release()
cv2.destroyAllWindows()
