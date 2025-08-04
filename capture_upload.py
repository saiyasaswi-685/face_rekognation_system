#capture_upload.py
import cv2
import boto3
import uuid
import os

aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
     # Replace with your IAM User Secret Key
BUCKET_NAME = "svtd80" # Replace with your bucket name
REGION_NAME = "ap-east-1"           # Your AWS region (like ap-south-1)

# --- AWS Client ---
s3 = boto3.client(
    "s3",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION_NAME
)

# --- Always save to the root folder ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_FILE = os.path.join(ROOT_DIR, "temp.jpg")

# --- Capture from Webcam ---
cam = cv2.VideoCapture(0)  # 0 = default webcam
print("Press SPACE to capture the image...")
while True:
    ret, frame = cam.read()
    cv2.imshow("Webcam", frame)

    key = cv2
