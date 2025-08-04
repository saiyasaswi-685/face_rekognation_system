import base64
import boto3
import os
import time
from flask import Flask, render_template, request, jsonify, session , redirect , send_from_directory
from PIL import Image
from io import BytesIO
from aws_voice import speak_text_aws
from local_voice import speak_text_local
from twilio.rest import Client
import qrcode
from datetime import datetime
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import smtplib
from email.mime.application import MIMEApplication
import decimal
from dateutil import parser
from decimal import Decimal

AWS_REGION = "us-east-1"  # or your actual region
AWS_BUCKET = "face-rekognition-system"



# 🔁 NEW: Initialize Flask
app = Flask(__name__)
app.secret_key = "mysecret"

# 🔁 NEW: AWS Setup
s3 = boto3.client('s3', region_name='us-east-1')
rekognition = boto3.client('rekognition', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')

# ✅ NEW: DynamoDB Setup
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # replace with your region

# 🔁 Constants
AUTHORIZED_FOLDER = "authorized/"
UNAUTHORIZED_FOLDER = "unauthorized/"
BUCKET_NAME = "face-rekognition-system"
COLLECTION_ID = 'my-face-collection'
SMS_TOPIC_ARN = 'arn:aws:sns:us-east-1:107548170409:Unauthorized_alert'

@app.route('/gate_scan')
def gate_scan():
    return render_template('scan_qr.html')


@app.route('/verify_qr/<token>')
def verify_qr(token):
    # Extract visitor_id from token
    try:
        visitor_id = token.split("_")[0]
    except IndexError:
        return "❌ Invalid QR Code", 400

    # Fetch the visitor record from DynamoDB
    table = dynamodb.Table('Visitors')
    response = table.get_item(Key={'visitor_id': visitor_id})

    if 'Item' not in response:
        return "❌ Visitor not found", 404

    visitor = response['Item']

    # Check if the visitor is approved
    if visitor.get('status') == 'Approved':
        return render_template("access_granted.html", visitor_id=visitor_id)
    else:
        return render_template("access_denied.html", visitor_id=visitor_id)



@app.route("/")
def home():
    return render_template("index.html")

# ... all your imports and setup remain unchanged ...

import uuid  # ✅ needed for unique visitor_id

# ... your AWS & Flask setup code ...

@app.route("/scan", methods=["POST"])
def scan():
    data = request.get_json()
    image_data = data.get('image')
    voice_mode = data.get('voice_mode', 'offline')
    email = data.get('email')
    name = data.get('name', 'Unknown')  # 🆕 Allow optional name from user
    visitor_id = str(uuid.uuid4())  # ✅ Unique visitor ID for this scan


    if not image_data or not email:
        return jsonify({"message": "❌ Missing image or email"}), 400

    session["visitor_email"] = email

    try:
        image_data = image_data.split(",")[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))

        os.makedirs("uploads", exist_ok=True)
        timestamp = int(time.time())
        filename = f"{email.replace('@', '_at_')}_{visitor_id}.jpg"
        visitor_image_path = os.path.join("uploads", filename)
        image.save(visitor_image_path)

        with open(visitor_image_path, "rb") as f:
            s3.upload_fileobj(f, BUCKET_NAME, f"uploads/{filename}")
        with open(visitor_image_path, "rb") as f:
            s3.upload_fileobj(f, BUCKET_NAME, "uploads/visitor.jpg")


        response = rekognition.search_faces_by_image(
            CollectionId=COLLECTION_ID,
            Image={'S3Object': {'Bucket': BUCKET_NAME, 'Name': f'uploads/{filename}'}},
            FaceMatchThreshold=90,
            MaxFaces=1
        )

        if response['FaceMatches']:
            match = response['FaceMatches'][0]
            rekog_name = match["Face"]["ExternalImageId"]
            confidence = round(match["Similarity"], 2)

            s3.upload_file(visitor_image_path, BUCKET_NAME, AUTHORIZED_FOLDER + "visitor.jpg")

            if voice_mode == "aws":
                speak_text_aws(f"Welcome {rekog_name}")
            else:
                speak_text_local(f"Welcome {rekog_name}")

            # ✅ Store to DynamoDB
            store_visitor(rekog_name, email, "Pending", filename, visitor_id)



            return jsonify({
                "status": "success",
                "name": rekog_name,
                "confidence": confidence,
                "message": f"✅ Access Granted to {rekog_name} ({confidence}%)"
            })

        else:
            timestamp = int(time.time())
            unauthorized_image_name = f"{UNAUTHORIZED_FOLDER}visitor_{timestamp}.jpg"
            s3.upload_file(visitor_image_path, BUCKET_NAME, unauthorized_image_name)

            image_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{unauthorized_image_name}"
            send_alert_sms("Unknown Visitor", image_url)

            if voice_mode == "aws":
                speak_text_aws("Unauthorized visitor detected.")
            else:
                speak_text_local("Unauthorized visitor detected.")

            # ✅ Store with provided name or fallback
            store_visitor(name, email, "Pending", filename, visitor_id)



            return jsonify({
                "status": "unauthorized",
                "message": "❌ No match found. Alert sent.",
                "image_url": image_url
            })

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"message": "❌ Internal server error"}), 500

# ✅ Function to insert into DynamoDB
def store_visitor(name, email, status, image_filename=None, visitor_id=None):
    if not visitor_id:
        visitor_id = str(uuid.uuid4())
 # ✅ Unique ID
    timestamp = Decimal(str(time.time()))   # store as float


    item = {
        'visitor_id': visitor_id,
        'name': name,
        'email': email,
        'status': status,
        'timestamp': timestamp
    }

    if image_filename:
        item['image'] = image_filename

    table = dynamodb.Table('Visitors')
    table.put_item(Item=item)



# ... your other routes and logic remain unchanged ...


@app.route("/admin")
def admin_dashboard():
    try:
        objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="uploads/")
        image_urls = []

        for obj in objects.get('Contents', []):
            key = obj['Key']
            if key.endswith(('.jpg', '.png', '.jpeg')) and "visitor" in key:
                url = s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': BUCKET_NAME, 'Key': key},
                    ExpiresIn=3600
                )
                image_urls.append({"key": key, "url": url})

        return render_template("admin.html", image_urls=image_urls)

    except Exception as e:
        return f"Error loading dashboard: {e}"

@app.route('/approve', methods=['POST'])
def approve():
    image_key = request.form.get("image_key")
    if not image_key:
        return "Image key not found", 400

    visitor_email = session.get("visitor_email")
    if not visitor_email:
        return "❌ Visitor email not found in session.", 400

    visitor_id = os.path.basename(image_key).split('.')[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    access_token = f"{visitor_id}_{timestamp}"

    # ✅ Store token in memory (optional for now)

    # Generate and save QR code locally
    qr = qrcode.make(access_token)
    qr_folder = os.path.join("static", "qr_codes")
    os.makedirs(qr_folder, exist_ok=True)
    qr_filename = f"{visitor_id}.png"
    qr_path = os.path.join(qr_folder, qr_filename)
    qr.save(qr_path)

    # Get QR code URL
    qr_code_url = f"/static/qr_codes/{qr_filename}"

    # Move image from unauthorized to authorized in S3
    copy_source = {'Bucket': BUCKET_NAME, 'Key': image_key}
    new_key = image_key.replace("unauthorized/", "authorized/")
    s3.copy_object(Bucket=BUCKET_NAME, CopySource=copy_source, Key=new_key)
    s3.delete_object(Bucket=BUCKET_NAME, Key=image_key)

    # Email the QR code with verify link (using localhost for demo)
    subject = "Your Access QR Code"
    body = f"""
    Dear Visitor,

    Your QR Code is attached below. Please scan it at the security gate.

    Or click this link to verify access:
    http://localhost:5000/verify_qr/{access_token}

    Thanks,
    Admin
    """
    send_email_with_attachment(visitor_email, subject, body, qr_path)

    # ✅ Update status in DynamoDB
    table = dynamodb.Table('Visitors')
    table.update_item(
        Key={'visitor_id': visitor_id},
        UpdateExpression="SET #s = :val",
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={':val': 'Approved'}
    )

    # Render confirmation page
    return render_template("qr_confirmation.html", visitor_id=visitor_id, qr_image=qr_filename, qr_code_url=qr_code_url)


@app.route("/visitor")
def visitor():
    s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/uploads/visitor.jpg"
    return render_template("visitor.html", image_url=s3_url)

def send_email_with_attachment(receiver_email, subject, body, attachment_path):
    sender_email = "bandarusaiyasaswi@gmail.com"
    app_password = "wxtxmtpjqdndpkvw"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with open(attachment_path, "rb") as f:
        part = MIMEApplication(f.read(), Name="QR_Code.png")
        part['Content-Disposition'] = 'attachment; filename="QR_Code.png"'
        msg.attach(part)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Error sending email:", str(e))


# ✅ NEW: Route to show all visitors in a table
@app.route('/visitors')
def show_visitors():
    visitors = get_all_visitors()
    return render_template('visitors.html', visitors=visitors)

# ✅ NEW: Function to fetch all visitor records from DynamoDB
def get_all_visitors():
    table = dynamodb.Table('Visitors')
    response = table.scan()
    visitors = response['Items']

    for visitor in visitors:
        if 'timestamp' in visitor:
            timestamp_value = visitor.get('timestamp', '')
            try:
                # Try parsing as float (UNIX timestamp)
                visitor['formatted_time'] = datetime.fromtimestamp(float(timestamp_value)).strftime("%d-%m-%Y %I:%M %p")
            except ValueError:
                try:
                    # If not a float, parse as datetime string
                    dt = parser.parse(timestamp_value)
                    visitor['formatted_time'] = dt.strftime("%d-%m-%Y %I:%M %p")
                except:
                    visitor['formatted_time'] = "Invalid timestamp"
        else:
            visitor['formatted_time'] = "No time"

    return visitors  # ✅ just return data, don't render template here



@app.route('/main_dashboard')
def main_dashboard():
    total_visitors = get_total_visitors()
    authorized = get_authorized_visitors()
    unauthorized = get_unauthorized_visitors()
    alerts_sent = get_alerts_sent()
    
    visitors = get_all_visitors()  # 🆕 This fetches data from DynamoDB

    return render_template('main_dashboard.html',
                           total_visitors=total_visitors,
                           authorized=authorized,
                           unauthorized=unauthorized,
                           alerts_sent=alerts_sent,
                           visitors=visitors)  # 🆕 Pass to template


s3 = boto3.client('s3')
bucket_name = 'face-rekognition-system'
folder_prefix = 'uploads/'

def get_total_visitors():
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)
    total = len([obj for obj in response.get('Contents', []) if obj['Key'] != folder_prefix])
    return total

def get_authorized_visitors():
    return 5

def get_unauthorized_visitors():
    return 2

def get_alerts_sent():
    return 3

@app.route('/update_status', methods=['POST'])
def update_status():
    visitor_id = request.form['visitor_id']    # Visitor to update
    action = request.form['action']            # "approve" or "reject"

    new_status = "Approved" if action == "approve" else "Rejected"

    table = dynamodb.Table('Visitors')         # Connect to the Visitors table

    # Update expression to change the status only
    update_expr = "SET #s = :val"
    expr_attr_names = {'#s': 'status'}
    expr_attr_values = {':val': new_status}

    # Update the record in DynamoDB
    table.update_item(
        Key={'visitor_id': visitor_id},
        UpdateExpression=update_expr,
        ExpressionAttributeNames=expr_attr_names,
        ExpressionAttributeValues=expr_attr_values
    )

    return redirect('/main_dashboard')  # Redirect back to dashboard



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

def send_alert_sms(name, image_url):
    message = f"Alert! {name} detected.\nImage: {image_url}"
    try:
        sns.publish(
            TopicArn=SMS_TOPIC_ARN,
            Message=message,
            Subject="Unauthorized Access Alert"
        )
        print("✅ SMS alert sent via AWS SNS!")
    except Exception as e:
        print("❌ Failed to send SMS:", e)



# In-memory list to store approved access tokens (You can use DB instead)




if __name__ == "__main__":
    app.run(debug=True)
