#compare_faces.py
import boto3

def compare_faces(visitor_image="uploads/visitor.jpg"):
    bucket_name = "face-rekognition-system-bucket"  # 🔁 Your actual bucket
    reference_images = [
        "authorized/23P31A0504.jpg",
        "authorized/23P31A0556.jpg",
        "authorized/23P31A0549.jpg"
    ]

    rekognition = boto3.client("rekognition", region_name="us-east-1")

    for ref_image in reference_images:
        try:
            response = rekognition.compare_faces(
                SourceImage={"S3Object": {"Bucket": bucket_name, "Name": visitor_image}},
                TargetImage={"S3Object": {"Bucket": bucket_name, "Name": ref_image}},
                SimilarityThreshold=90
            )

            if response["FaceMatches"]:
                match = response["FaceMatches"][0]
                confidence = round(match["Similarity"], 2)
                name = ref_image.split("/")[-1].split(".")[0]

                return {
                    "name": name,
                    "confidence": confidence,
                    "image_url": f"https://{bucket_name}.s3.amazonaws.com/{ref_image}"
                }

        except Exception as e:
            print(f"❌ Error comparing with {ref_image}: {e}")
            continue

    return None
