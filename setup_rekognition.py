#setup_rekognition.py
import boto3

# Initialize Rekognition client
rekognition = boto3.client('rekognition', region_name='us-east-1')

# ✅ 1. Create collection (Run only once)
collection_id = 'my-face-collection'

def create_collection():
    try:
        response = rekognition.create_collection(CollectionId=collection_id)
        print("Collection created:", response['StatusCode'])
    except rekognition.exceptions.ResourceAlreadyExistsException:
        print("Collection already exists.")

# ✅ 2. Index faces from authorized folder in S3
def index_authorized_faces():
    bucket = 'face-rekognition-system-bucket'  # 🔁 Replace with your actual bucket name
    authorized_people = ['23P31A0501.jpg', '23P31A0549.jpg' , '23P31A0556.jpg' , '23P31A0504.jpg']  # Add more as needed

    for filename in authorized_people:
        person_name = filename.split('.')[0]  # This becomes ExternalImageId
        response = rekognition.index_faces(
            CollectionId=collection_id,
            Image={'S3Object': {'Bucket': bucket, 'Name': f'authorized/{filename}'}},
            ExternalImageId=person_name,
            DetectionAttributes=['DEFAULT']
        )
        print(f"Indexed: {person_name} - Faces found: {len(response['FaceRecords'])}")

if __name__ == '__main__':
    create_collection()
    index_authorized_faces()
