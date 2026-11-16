#!/usr/bin/env python3
"""
🌐 MP4 NEWS - YouTube Channel Login & OAuth 2.0 Web Portal
-----------------------------------------------------------
Starts a local web server at http://localhost:8000 so the user can
click a button, log in with their Google/YouTube account, and generate
the cached 'token.json' with zero manual copy-pasting.
"""

import os
import sys
import json
import webbrowser
from pathlib import Path
from flask import Flask, redirect, request, render_template_string, jsonify, flash
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Allow HTTP on localhost for OAuth callback
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

PROJECT_ROOT = Path(__file__).resolve().parent
CLIENT_SECRETS_FILE = str(PROJECT_ROOT / "YT-API-KEY.json")
TOKEN_FILE = str(PROJECT_ROOT / "token.json")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube"
]

REDIRECT_URI = "http://localhost:8000/api/channels/oauth2callback"

app = Flask(__name__)
app.secret_key = "mp4_news_super_secret_session_key"


def get_existing_channel_info():
    """Checks if token.json exists and returns channel info if available"""
    if not os.path.exists(TOKEN_FILE):
        return None
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        youtube = build("youtube", "v3", credentials=creds)
        res = youtube.channels().list(mine=True, part="snippet,statistics").execute()
        items = res.get("items", [])
        if items:
            ch = items[0]
            return {
                "title": ch["snippet"]["title"],
                "avatar": ch["snippet"]["thumbnails"]["default"]["url"],
                "subscribers": ch["statistics"].get("subscriberCount", "N/A"),
                "videos": ch["statistics"].get("videoCount", "0"),
                "custom_url": ch["snippet"].get("customUrl", "")
            }
    except Exception:
        pass
    return None


INDEX_HTML = """<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MP4 NEWS - YouTube Channel Login Portal</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: radial-gradient(circle at 50% 20%, #1e1b4b 0%, #0f172a 60%, #020617 100%);
      color: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .panel {
      background: rgba(30, 41, 59, 0.7);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      max-width: 580px;
      width: 100%;
      padding: 40px;
      text-align: center;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(99, 102, 241, 0.2);
    }
    .logo-badge {
      display: inline-block;
      background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
      color: #fff;
      font-weight: 900;
      font-size: 15px;
      padding: 6px 18px;
      border-radius: 30px;
      letter-spacing: 1.5px;
      margin-bottom: 20px;
      box-shadow: 0 4px 14px rgba(239, 68, 68, 0.4);
    }
    h1 {
      font-size: 28px;
      font-weight: 900;
      margin-bottom: 10px;
      background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    p.subtitle {
      color: #94a3b8;
      font-size: 15px;
      line-height: 1.5;
      margin-bottom: 25px;
    }
    .status-card {
      background: #0f172a;
      border-radius: 14px;
      padding: 22px;
      margin-bottom: 25px;
      border: 1px solid #334155;
      text-align: left;
    }
    .status-header {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .avatar {
      width: 56px;
      height: 56px;
      border-radius: 50%;
      border: 2px solid #38bdf8;
      object-fit: cover;
    }
    .ch-name {
      font-size: 18px;
      font-weight: 800;
      color: #f8fafc;
    }
    .ch-handle {
      font-size: 13px;
      color: #38bdf8;
      margin-top: 2px;
    }
    .stats-row {
      display: flex;
      gap: 20px;
      margin-top: 16px;
      padding-top: 14px;
      border-top: 1px solid #1e293b;
      font-size: 13px;
      color: #94a3b8;
    }
    .stats-row span b {
      color: #f1f5f9;
    }
    .badge-connected {
      display: inline-block;
      background: rgba(34, 197, 94, 0.15);
      color: #4ade80;
      border: 1px solid #22c55e;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 700;
      margin-bottom: 12px;
    }
    .badge-disconnected {
      display: inline-block;
      background: rgba(239, 68, 68, 0.15);
      color: #f87171;
      border: 1px solid #ef4444;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 700;
      margin-bottom: 12px;
    }
    .badge-warning {
      display: inline-block;
      background: rgba(245, 158, 11, 0.15);
      color: #fbbf24;
      border: 1px solid #f59e0b;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 700;
      margin-bottom: 12px;
    }
    .btn-login {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      width: 100%;
      background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
      color: #ffffff;
      padding: 16px 24px;
      border-radius: 12px;
      font-size: 17px;
      font-weight: 800;
      text-decoration: none;
      box-shadow: 0 10px 25px rgba(239, 68, 68, 0.4);
      transition: all 0.2s ease;
      cursor: pointer;
      border: none;
    }
    .btn-login:hover {
      transform: translateY(-2px);
      box-shadow: 0 14px 30px rgba(239, 68, 68, 0.55);
    }
    .upload-box {
      background: #0f172a;
      border: 2px dashed #475569;
      border-radius: 14px;
      padding: 20px;
      margin-top: 15px;
      text-align: left;
    }
    textarea {
      width: 100%;
      height: 100px;
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 8px;
      color: #f1f5f9;
      padding: 10px;
      font-family: monospace;
      font-size: 12px;
      resize: vertical;
      margin-top: 10px;
    }
    .btn-submit {
      margin-top: 12px;
      background: #3b82f6;
      color: #fff;
      border: none;
      padding: 10px 20px;
      border-radius: 8px;
      font-weight: 700;
      cursor: pointer;
      width: 100%;
    }
    .btn-submit:hover {
      background: #2563eb;
    }
    .footer {
      margin-top: 24px;
      font-size: 12px;
      color: #64748b;
    }
  </style>
</head>
<body>
  <div class="panel">
    <div class="logo-badge">MP4 NEWS AUTOMATION</div>
    <h1>YouTube चैनल लिंकर</h1>
    <p class="subtitle">अपने YouTube चैनल को सुरक्षित रूप से कनेक्ट करें ताकि वीडियो और थंबनेल सीधे ऑटोमैटिक अपलोड हो सकें।</p>

    {% if channel %}
      <div class="status-card">
        <span class="badge-connected">चैनल कनेक्टेड है (Active)</span>
        <div class="status-header">
          <img src="{{ channel.avatar }}" class="avatar" alt="Channel Logo">
          <div>
            <div class="ch-name">{{ channel.title }}</div>
            <div class="ch-handle">{{ channel.custom_url }}</div>
          </div>
        </div>
        <div class="stats-row">
          <span>सब्सक्राइबर्स: <b>{{ channel.subscribers }}</b></span>
          <span>अपलोड वीडियो: <b>{{ channel.videos }}</b></span>
          <span>टोकन: <b>token.json सुरक्षित</b></span>
        </div>
      </div>
      <a href="/login" class="btn-login" style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);">
        🔄 चैनल दोबारा कनेक्ट / स्विच करें
      </a>
    {% elif not has_client_secrets %}
      <div class="status-card">
        <span class="badge-warning">YT-API-KEY.json (OAuth Credentials) की आवश्यकता है</span>
        <p style="color: #cbd5e1; font-size: 14px; margin-top: 8px; line-height: 1.5;">
          Google Cloud Console से डाउनलोड किया गया OAuth Client JSON फाइल पेस्ट या अपलोड करें:
        </p>

        <form action="/save_client_secret" method="POST" enctype="multipart/form-data" class="upload-box">
          <label style="font-size: 13px; color: #94a3b8; display: block; margin-bottom: 6px;">
            विकल्प 1: client_secret.json फाइल चुनें
          </label>
          <input type="file" name="secret_file" accept=".json" style="color: #cbd5e1; font-size: 13px; margin-bottom: 12px;">
          
          <label style="font-size: 13px; color: #94a3b8; display: block; margin-bottom: 6px;">
            विकल्प 2: या JSON सामग्री यहाँ पेस्ट करें:
          </label>
          <textarea name="secret_text" placeholder='{"installed": {"client_id": "...", "client_secret": "..."}}'></textarea>
          
          <button type="submit" class="btn-submit">💾 सेव करें और लॉगिन शुरू करें</button>
        </form>
      </div>
    {% else %}
      <div class="status-card" style="text-align: center;">
        <span class="badge-disconnected">कोई चैनल कनेक्टेड नहीं है</span>
        <p style="color: #cbd5e1; font-size: 14px; margin-top: 8px;">
          'token.json' उपलब्ध नहीं है। नीचे दिए गए बटन पर क्लिक करके अपना चैनल ऑथराइज़ करें।
        </p>
      </div>
      <a href="/login" class="btn-login">
        ▶️ YouTube चैनल लॉगिन करें (Google Sign-In)
      </a>
    {% endif %}

    <div class="footer">
      प्रोटोकॉल: Google OAuth 2.0 (Port 8000) • Sicreat-automation
    </div>
  </div>
</body>
</html>
"""

SUCCESS_HTML = """<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="utf-8">
  <title>चैनल सफलतापूर्वक कनेक्ट हो गया!</title>
  <style>
    body {
      background: radial-gradient(circle at 50% 20%, #14532d 0%, #0f172a 60%, #020617 100%);
      color: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .panel {
      background: rgba(30, 41, 59, 0.85);
      border: 1px solid rgba(74, 222, 128, 0.3);
      border-radius: 20px;
      max-width: 580px;
      width: 100%;
      padding: 40px;
      text-align: center;
      box-shadow: 0 20px 50px rgba(0,0,0,0.7), 0 0 30px rgba(34, 197, 94, 0.25);
    }
    .check-icon {
      font-size: 50px;
      margin-bottom: 16px;
    }
    h1 {
      font-size: 26px;
      color: #4ade80;
      margin-bottom: 12px;
    }
    p {
      color: #cbd5e1;
      font-size: 15px;
      line-height: 1.6;
      margin-bottom: 24px;
    }
    .details {
      background: #0f172a;
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 20px;
      font-size: 14px;
      color: #94a3b8;
      text-align: left;
    }
    .token-box {
      background: #090d16;
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 12px;
      font-family: monospace;
      font-size: 11px;
      color: #38bdf8;
      max-height: 120px;
      overflow-y: auto;
      text-align: left;
      white-space: pre-wrap;
      word-break: break-all;
      margin-bottom: 16px;
    }
    .btn {
      display: inline-block;
      background: #22c55e;
      color: #000;
      font-weight: 800;
      padding: 12px 28px;
      border-radius: 10px;
      text-decoration: none;
      cursor: pointer;
      border: none;
    }
    .btn-copy {
      background: #3b82f6;
      color: #fff;
      font-size: 13px;
      padding: 8px 16px;
      margin-bottom: 20px;
    }
  </style>
</head>
<body>
  <div class="panel">
    <div class="check-icon">🎉</div>
    <h1>चैनल सफलतापूर्वक लिंक हो गया!</h1>
    <p>
      बधाई हो! आपका YouTube चैनल ऑथेंटिकेट हो गया है और नया <b>token.json</b> सुरक्षित रूप से सेव कर दिया गया है।
    </p>
    <div class="details">
      <div>चैनल: <b style="color: #fff;">{{ title }}</b></div>
      <div style="margin-top: 6px;">सब्सक्राइबर्स: <b style="color: #fff;">{{ subscribers }}</b></div>
      <div style="margin-top: 6px;">पाथ: <b style="color: #38bdf8;">{{ token_path }}</b></div>
    </div>

    <div style="text-align: left; font-size: 12px; color: #94a3b8; margin-bottom: 6px;">
      📋 Kaggle / GitHub Secret (YOUTUBE_TOKEN_JSON) के लिए टोकन:
    </div>
    <div class="token-box" id="tokenBox">{{ token_content }}</div>
    <button class="btn btn-copy" onclick="copyToken()">📋 टोकन कॉपी करें</button>
    <br>
    <a href="/" class="btn">डैशबोर्ड पर वापस जाएं</a>
  </div>

  <script>
    function copyToken() {
      const text = document.getElementById('tokenBox').innerText;
      navigator.clipboard.writeText(text).then(() => {
        alert('टोकन क्लिपबोर्ड पर कॉपी हो गया!');
      });
    }
  </script>
</body>
</html>
"""


FLOW_CACHE = {}


@app.route("/")
def index():
    has_client_secrets = os.path.exists(CLIENT_SECRETS_FILE)
    channel = get_existing_channel_info()
    return render_template_string(INDEX_HTML, channel=channel, has_client_secrets=has_client_secrets)


@app.route("/save_client_secret", methods=["POST"])
def save_client_secret():
    content = None
    if "secret_file" in request.files and request.files["secret_file"].filename != "":
        content = request.files["secret_file"].read().decode("utf-8")
    elif request.form.get("secret_text", "").strip():
        content = request.form.get("secret_text").strip()

    if not content:
        return "<h3>कृपया फाइल अपलोड करें या JSON पेस्ट करें।</h3><a href='/'>वापस जाएं</a>", 400

    try:
        parsed = json.loads(content)
        with open(CLIENT_SECRETS_FILE, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)
    except Exception as e:
        return f"<h3>अमान्य JSON प्रारूप: {e}</h3><a href='/'>वापस जाएं</a>", 400

    return redirect("/login")


@app.route("/login")
def login():
    if not os.path.exists(CLIENT_SECRETS_FILE):
        return redirect("/")

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"  # Forces refresh_token delivery
    )

    FLOW_CACHE[state] = flow
    return redirect(auth_url)


@app.route("/api/channels/oauth2callback")
def oauth2callback():
    code = request.args.get("code")
    state = request.args.get("state")
    if not code:
        return "<h3>एरर: Google से कोई ऑथराइजेशन कोड प्राप्त नहीं हुआ।</h3>", 400

    flow = FLOW_CACHE.pop(state, None)
    if not flow:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            state=state,
            redirect_uri=REDIRECT_URI
        )

    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    creds_json = credentials.to_json()

    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(creds_json)

    niche_token = PROJECT_ROOT / "niches" / "01-daily-top10" / "token.json"
    try:
        with open(niche_token, "w", encoding="utf-8") as f:
            f.write(creds_json)
    except Exception:
        pass

    print(f"\n✓ OAuth Token successfully saved to: {TOKEN_FILE}")

    ch_title = "YouTube Channel"
    sub_count = "N/A"
    try:
        youtube = build("youtube", "v3", credentials=credentials)
        res = youtube.channels().list(mine=True, part="snippet,statistics").execute()
        items = res.get("items", [])
        if items:
            ch_title = items[0]["snippet"]["title"]
            sub_count = items[0]["statistics"].get("subscriberCount", "N/A")
    except Exception:
        pass

    return render_template_string(
        SUCCESS_HTML,
        title=ch_title,
        subscribers=sub_count,
        token_path=TOKEN_FILE,
        token_content=creds_json
    )


def start_server():
    print("\n" + "═" * 70)
    print("🚀 MP4 NEWS YOUTUBE CHANNEL LOGIN PORTAL IS READY")
    print("🌐 Opening Browser: http://localhost:8000")
    print("═" * 70 + "\n")
    try:
        webbrowser.open("http://localhost:8000")
    except Exception:
        pass
    app.run(host="localhost", port=8000, debug=False)


if __name__ == "__main__":
    start_server()
