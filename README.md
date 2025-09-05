# 📌 Smart Visitor & Threat Detection System using AWS

## 📖 Project Overview

The **Smart Visitor & Threat Detection System** is a **face-recognition-based security solution** built using **AWS services** to automate visitor identification and access control.

* ✅ **Authorized Visitors** → Recognized automatically and granted access.
* ❌ **Unauthorized Visitors** → Must enter name & email → Admin receives a request → If approved, visitor gets an **email with QR code** for entry.
* 🔊 **Voice Feedback** → Status announced as *"Access Granted"* or *"Access Denied"*.



## 🎯 Objectives

* Automate visitor identification and access control.
* Instantly notify the admin when unauthorized visitors arrive.
* Provide **QR code-based secure one-time access**.
* Maintain a detailed **visitor log in DynamoDB**.


## 💡 Use Cases

This system can be used in:

* 🏢 Office entrances
* 🏠 Residential apartments
* 🎉 Private events
* 🛡️ Secure facilities



## 🛠️ Prerequisites

### Basic Requirements

* AWS Account
* Basic knowledge of **Python & Flask**
* Laptop/PC with internet access

### AWS Services Used

* **S3** → Store visitor images (authorized + new uploads)
* **Rekognition** → Face detection & matching
* **Polly** → Voice feedback (*Access Granted/Denied*)
* **SNS** → Send alerts to the admin
* **SES** → Email with QR codes to approved visitors
* **DynamoDB** → Store visitor logs
* **Lambda** → Trigger automated actions
* **EC2** → Host Flask web application



## ⚙️ Project Workflow

### 🔹 Step 1: Face Capture & Upload

* Capture visitor face using **OpenCV**
* Upload to **S3 bucket**

### 🔹 Step 2: Voice Feedback (AWS Polly)

* Announce *“Authorized”* or *“Unauthorized”*

### 🔹 Step 3: Unauthorized Visitor Alert (SNS + Flask)

* Unauthorized visitor details → Sent to **Admin via SNS**
* Admin dashboard shows visitor info → Approve / Deny

### 🔹 Step 4: Admin Dashboard

* Displays **visitor photo, name, email**
* Approve/Deny buttons for quick decision

### 🔹 Step 5: Email with QR Code (AWS SES)

* If approved → Visitor receives email with:

  * Unique **QR code**
  * Verification link

### 🔹 Step 6: QR Code Verification

* Visitor scans QR at entry point
* If valid → **Access Granted**

### 🔹 Step 7: Visitor Data Storage (DynamoDB)

Stored fields:

* Visitor ID (Unique)
* Name
* Email
* Photo URL (S3 link)
* Timestamp
* Status (Approved / Rejected)

---

## 📂 Project Structure

```
smart-visitor-system/
│-- app/                 # Flask app
│-- static/              # CSS, JS, QR codes
│-- templates/           # HTML pages (Dashboard, Alerts, etc.)
│-- visitor_logs/        # DynamoDB records
│-- requirements.txt     # Dependencies
│-- README.md            # Project documentation
```


## ⚡ Installation & Setup

1️⃣ Clone the repo

```bash
git clone https://github.com/username/smart-visitor-system.git
cd smart-visitor-system
```

2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

3️⃣ Run Flask app

```bash
python app.py
```

4️⃣ Access Dashboard

```
http://localhost:5000
```

---

## 🎯 Future Enhancements

* 🔐 Role-based authentication for multiple admins
* 📊 Analytics dashboard with visitor statistics
* 📱 Mobile app integration for admin approvals
* 🤖 AI-based **threat detection (suspicious behavior recognition)**

