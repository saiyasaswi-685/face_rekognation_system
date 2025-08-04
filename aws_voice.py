#aws_voice.py

import boto3
import os
from playsound import playsound
import time

def speak_text_aws(text):
    polly = boto3.client('polly', region_name="us-east-1")

    response = polly.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId="Joanna")

    # ✅ Generate unique output filename to avoid PermissionError
    output_file = f"output_{int(time.time())}.mp3"

    with open(output_file, "wb") as file:
        file.write(response['AudioStream'].read())

    playsound(output_file)

    # ✅ OPTIONAL: Delete the file after playing to clean up
    os.remove(output_file)

def move_to_unauthorized(bucket, key):
    s3 = boto3.client('s3', region_name='us-east-1')
    target_key = 'unauthorized/visitor.jpg'

    # Copy the file
    s3.copy_object(
        Bucket=bucket,
        CopySource={'Bucket': bucket, 'Key': key},
        Key=target_key
    )

    # Delete the original from uploads
    s3.delete_object(Bucket=bucket, Key=key)

    print("📂 Visitor image moved to unauthorized folder.")

# Example call:
# recognize_face_from_s3()

# Voice message function

# Face match function
def match_face_in_visitor():
    rekognition = boto3.client('rekognition', region_name='us-east-1')
    s3 = boto3.client('s3')
    
    bucket_name = 'face-rekognition-system-bucket'  # 👉 Replace with your actual bucket
    visitor_image_key = 'uploads/visitor.jpg'

    try:
        response = rekognition.search_faces_by_image(
            CollectionId='my-face-collection',
            Image={'S3Object': {'Bucket': bucket_name, 'Name': visitor_image_key}},
            FaceMatchThreshold=90,
            MaxFaces=1
        )

        if response['FaceMatches']:
            match = response['FaceMatches'][0]
            name = match['Face']['ExternalImageId']
            print(f"✅ Face matched with: {name}")

            speak_text_aws(f"Access granted. Welcome {name}")
            return name
        else:
            print("❌ No face match found. Moving image to unauthorized.")
            move_key = 'unauthorized/visitor.jpg'
            s3.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': visitor_image_key}, Key=move_key)
            s3.delete_object(Bucket=bucket_name, Key=visitor_image_key)

            speak_text_aws("Access denied. You are not authorized.")
            return None

    except Exception as e:
        print("❌ Error in face match:", e)
        return None
