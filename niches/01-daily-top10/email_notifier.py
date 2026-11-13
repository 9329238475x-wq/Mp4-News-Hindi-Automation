#!/usr/bin/env python3
"""
📧 Instant Gmail Notification Service for MP4 NEWS Automated YouTube Uploads
----------------------------------------------------------------------------
Sends a rich HTML notification email to 9329238475x@gmail.com whenever a video
is successfully uploaded to YouTube, complete with direct watch and Studio links.
"""

import os
import sys
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root .env is loaded
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def send_upload_notification(
    video_id: str,
    title: str,
    privacy_status: str = "unlisted",
    thumbnail_status: str = "Attached ✅",
    tags_count: int = 0,
    chapters_count: int = 0,
    video_path: str = ""
) -> bool:
    """
    Sends an instant email notification with clickable watch and studio edit links.
    """
    sender_email = os.environ.get("DUBSTUDIO_EMAIL", "9329238475x@gmail.com")
    recipient_email = os.environ.get("DUBSTUDIO_TO_EMAIL", "9329238475x@gmail.com")
    app_password = os.environ.get("DUBSTUDIO_APP_PASS", "ziqkkzjwffqnzrgn")

    if not app_password:
        print("  ⚠️ Email notification skipped: DUBSTUDIO_APP_PASS not configured.")
        return False

    watch_url = f"https://youtu.be/{video_id}"
    studio_url = f"https://studio.youtube.com/video/{video_id}/edit"
    now_str = datetime.now().strftime("%d %B %Y, %I:%M %p IST")

    subject = f"🚀 [MP4 NEWS] YouTube Video Uploaded Successfully! ({video_id})"

    # Plain-text version for basic email clients
    plain_text = f"""MP4 NEWS हिन्दी - YouTube Upload Report
==============================================
Status: Success ✅
Upload Time: {now_str}

Title: {title}
Privacy: {privacy_status.upper()}
Thumbnail: {thumbnail_status}
Chapters: {chapters_count}
Tags: {tags_count} tags included

Links:
- Watch Video: {watch_url}
- YouTube Studio Edit: {studio_url}

MP4 News Automated Broadcast Engine
"""

    # Rich HTML version for modern email clients / smartphone screens
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 20px;
      background-color: #0f172a;
      color: #ffffff;
    }}
    .container {{
      max-width: 600px;
      margin: 0 auto;
      background: #1e293b;
      border-radius: 14px;
      overflow: hidden;
      border: 1px solid #334155;
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    .header {{
      background: linear-gradient(135deg, #d80000 0%, #8b0000 100%);
      padding: 24px;
      text-align: center;
      border-bottom: 3px solid #ffe600;
    }}
    .header h1 {{
      margin: 0;
      font-size: 26px;
      font-weight: 900;
      color: #ffffff;
      letter-spacing: 0.5px;
    }}
    .header p {{
      margin: 6px 0 0 0;
      color: #ffe600;
      font-size: 14px;
      font-weight: 700;
    }}
    .content {{
      padding: 24px;
    }}
    .card {{
      background: #0f172a;
      border-radius: 10px;
      padding: 18px;
      margin-bottom: 20px;
      border: 1px solid #334155;
    }}
    .title-box {{
      font-size: 17px;
      font-weight: 700;
      color: #ffffff;
      line-height: 1.5;
      margin-bottom: 12px;
      border-left: 4px solid #ffe600;
      padding-left: 12px;
    }}
    .metric-row {{
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid #1e293b;
      font-size: 14px;
    }}
    .metric-label {{
      color: #94a3b8;
    }}
    .metric-value {{
      font-weight: 700;
      color: #f1f5f9;
    }}
    .btn-container {{
      display: flex;
      gap: 12px;
      margin-top: 24px;
      text-align: center;
    }}
    .btn {{
      display: inline-block;
      flex: 1;
      padding: 14px 20px;
      border-radius: 8px;
      font-size: 15px;
      font-weight: 800;
      text-decoration: none;
      text-align: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }}
    .btn-watch {{
      background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
      color: #ffffff !important;
      border: 1px solid #ff4d4d;
    }}
    .btn-studio {{
      background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
      color: #ffffff !important;
      border: 1px solid #38bdf8;
    }}
    .footer {{
      padding: 16px 24px;
      background: #0f172a;
      text-align: center;
      font-size: 12px;
      color: #64748b;
      border-top: 1px solid #334155;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🚀 MP4 NEWS हिन्दी</h1>
      <p>YouTube Video Successfully Uploaded & Published</p>
    </div>
    
    <div class="content">
      <div class="card">
        <div class="title-box">{title}</div>
        
        <div class="metric-row">
          <span class="metric-label">📺 Video ID:</span>
          <span class="metric-value"><code>{video_id}</code></span>
        </div>
        <div class="metric-row">
          <span class="metric-label">🔒 Privacy:</span>
          <span class="metric-value" style="color: #4ade80;">{privacy_status.upper()}</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">🖼️ Custom Thumbnail:</span>
          <span class="metric-value">{thumbnail_status}</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">📌 Chapters Created:</span>
          <span class="metric-value">{chapters_count} timestamps</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">🏷️ Viral SEO Tags:</span>
          <span class="metric-value">{tags_count} tags (VidIQ style)</span>
        </div>
        <div class="metric-row" style="border-bottom: none;">
          <span class="metric-label">⏰ Completed At:</span>
          <span class="metric-value">{now_str}</span>
        </div>
      </div>

      <div class="btn-container">
        <a href="{watch_url}" class="btn btn-watch" target="_blank">▶️ Watch on YouTube</a>
        <a href="{studio_url}" class="btn btn-studio" target="_blank">⚙️ Open in Studio</a>
      </div>
    </div>
    
    <div class="footer">
      Automated by MP4 News Hindi Broadcast Engine • Sicreat-automation
    </div>
  </div>
</body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"MP4 NEWS Bot <{sender_email}>"
    msg["To"] = recipient_email
    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        print(f"  📧 Sending upload notification email to {recipient_email}...")
        # Try SSL port 465 first
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
                server.login(sender_email, app_password)
                server.sendmail(sender_email, [recipient_email], msg.as_string())
        except Exception:
            # Fallback to STARTTLS port 587
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
                server.starttls()
                server.login(sender_email, app_password)
                server.sendmail(sender_email, [recipient_email], msg.as_string())

        print("  ✓ Notification email sent successfully!")
        return True
    except Exception as e:
        print(f"  ⚠️ Failed to send notification email: {e}")
        return False


if __name__ == "__main__":
    print("Testing Gmail upload notification...")
    test_id = "dQw4w9WgXcQ"
    res = send_upload_notification(
        video_id=test_id,
        title="Today Breaking News ! आज 13 नवंबर के 50 मुख्य समाचार बड़ी खबरें, महादेव सट्टा, UP एनकाउंटर",
        privacy_status="unlisted",
        thumbnail_status="Custom 3D Master Thumbnail Attached ✅",
        tags_count=24,
        chapters_count=50
    )
    print(f"Test result: {'SUCCESS ✅' if res else 'FAILED ❌'}")

