#index_authorized_faces.py
import boto3

rekognition = boto3.client('rekognition', region_name='us-east-1')
bucket_name = 'face-rekognition-system-bucket'  # change if your bucket name is different

# List of authorized people: (image path inside S3, person name)
authorized_faces = [
    ("authorized/23P31A0504.jpg", "23P31A0504"),
    ("authorized/23P31A0556.jpg", "23P31A0556"),
    ("authorized/23P31A0549.jpg", "23P31A0549"),
    # Add more if needed
]

for image_name, person_name in authorized_faces:
    response = rekognition.index_faces(
        CollectionId='my-face-collection',
        Image={'S3Object': {'Bucket': bucket_name, 'Name': image_name}},
        ExternalImageId=person_name,
        DetectionAttributes=['DEFAULT']
    )
    print(f"✅ Indexed {person_name}")
