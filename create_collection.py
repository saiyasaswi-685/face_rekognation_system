#create_collection.py
import boto3

# Initialize Rekognition client
rekognition = boto3.client('rekognition', region_name='us-east-1')

# Collection name
collection_id = 'my-face-collection'

# Create collection
response = rekognition.create_collection(CollectionId=collection_id)

print("✅ Collection created:", response)
