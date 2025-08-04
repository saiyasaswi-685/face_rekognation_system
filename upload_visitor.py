#upload_visitor.py
import boto3
import uuid

# AWS credentials (replace with your actual keys)
import os
aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

BUCKET_NAME = 'svtd80'  # your bucket name

# Connect to S3
s3 = boto3.client('s3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

# Generate unique name for visitor image
visitor_image_key = f"visitor_uploads/{uuid.uuid4()}.jpg"

# Upload local visitor.jpg to S3
s3.upload_file("visitor.jpg", BUCKET_NAME, visitor_image_key)

print(f"✅ Visitor image uploaded to S3 as: {visitor_image_key}")

# Save the S3 path for the comparison step
with open("last_visitor_key.txt", "w") as f:
    f.write(visitor_image_key)
