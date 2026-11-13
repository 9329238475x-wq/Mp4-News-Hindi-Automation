#!/usr/bin/env python3
"""
🚀 Automated YouTube Resumable Video & Thumbnail Uploader
---------------------------------------------------------
1. OAuth 2.0 Auth Flow with persistent 'token.json' caching.
2. Resumable Chunked Video Upload (4MB chunks) with exponential backoff.
3. High-Definition Custom Thumbnail Attachment (youtube.thumbnails.set).
4. Automatic Instant Email Notification to 9329238475x@gmail.com with direct watch links.
"""

import os
import sys
import time
import json
import http.client
from pathlib import Path

# Google API Client & OAuth Libraries
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

CURR_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURR_DIR.parent.parent

# Sibling module imports
from yt_seo_engine import generate_youtube_seo_package
from email_notifier import send_upload_notification

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]
CLIENT_SECRETS_FILE = str(PROJECT_ROOT / "YT-API-KEY.json")
TOKEN_FILE = str(PROJECT_ROOT / "token.json")

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
RETRIABLE_EXCEPTIONS = (
    IOError, http.client.NotConnected,
    http.client.IncompleteRead, http.client.ImproperConnectionState,
    http.client.CannotSendRequest, http.client.CannotSendHeader,
    http.client.ResponseNotReady, http.client.BadStatusLine
)


# ═════════════════════════════════════════════════════════════════════════════
# 1. OAUTH 2.0 AUTHENTICATION & TOKEN CACHING
# ═════════════════════════════════════════════════════════════════════════════

def get_authenticated_youtube_service(
    client_secrets_file: str = CLIENT_SECRETS_FILE,
    token_file: str = TOKEN_FILE
):
    """
    Handles Google OAuth 2.0 authentication:
    - If token.json exists: loads & auto-refreshes credentials silently.
    - If first time: opens browser authorization flow, then caches token.json.
    """
    creds = None

    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        except Exception as e:
            print(f"  ⚠️ Existing token.json invalid, re-authorizing: {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("  🔄 Refreshing expired OAuth token...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"  ⚠️ Token refresh failed: {e}. Starting fresh auth flow...")
                creds = None

        if not creds:
            if not os.path.exists(client_secrets_file):
                raise FileNotFoundError(f"OAuth credentials file not found: {client_secrets_file}")

            print(f"  🔐 Launching Google OAuth 2.0 Authorization Flow using: {client_secrets_file}...")
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            try:
                # Try port 8000 first (matching YT-API-KEY.json redirect URI)
                creds = flow.run_local_server(port=8000, open_browser=True)
            except Exception:
                # Fallback to dynamic port
                creds = flow.run_local_server(port=0, open_browser=True)

        # Cache credentials for unattended future uploads
        with open(token_file, "w", encoding="utf-8") as tf:
            tf.write(creds.to_json())
        print(f"  ✓ OAuth credentials successfully cached to: {token_file}")

    return build("youtube", "v3", credentials=creds)


# ═════════════════════════════════════════════════════════════════════════════
# 2. RESUMABLE VIDEO UPLOAD ENGINE
# ═════════════════════════════════════════════════════════════════════════════

def upload_video_resumable(
    youtube,
    video_path: str,
    title: str,
    description: str,
    tags: list,
    category_id: str = "25",
    privacy_status: str = "unlisted"
) -> str:
    """
    Executes a high-performance resumable video upload in 4MB chunks with exponential backoff.
    Returns the uploaded YouTube Video ID.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"\n🚀 [YouTube Upload] Starting upload of: {video_path} ({file_size_mb:.1f} MB)")
    print(f"  📌 Title: {title}")
    print(f"  🔒 Privacy: {privacy_status.upper()}")

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": [],  # Intentionally kept completely empty as per user request
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    # 4MB chunks (must be multiple of 256KB)
    media = MediaFileUpload(
        video_path,
        chunksize=4 * 1024 * 1024,
        resumable=True
    )

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    retry = 0
    max_retries = 10

    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"  📤 Upload Progress: {progress}%", end="\r", flush=True)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                print(f"\n  ⚠️ Retriable HTTP error {e.resp.status}: {e}. Retrying...")
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            print(f"\n  ⚠️ Network error: {e}. Retrying...")

        if response is None:
            retry += 1
            if retry > max_retries:
                raise RuntimeError("Maximum upload retries exceeded. Check internet connection.")
            sleep_sec = 2 ** retry
            print(f"  ⏳ Waiting {sleep_sec}s before retry {retry}/{max_retries}...")
            time.sleep(sleep_sec)

    video_id = response.get("id")
    print(f"\n  ✅ Video Upload Completed! YouTube Video ID: {video_id}")
    return video_id


# ═════════════════════════════════════════════════════════════════════════════
# 3. CUSTOM THUMBNAIL ATTACHMENT
# ═════════════════════════════════════════════════════════════════════════════

def attach_custom_thumbnail(youtube, video_id: str, thumbnail_path: str) -> bool:
    """
    Attaches custom master HD thumbnail to the uploaded YouTube video.
    """
    if not os.path.exists(thumbnail_path):
        print(f"  ⚠️ Thumbnail file not found: {thumbnail_path}. Skipping thumbnail.")
        return False

    print(f"  🖼️ Attaching custom master thumbnail: {thumbnail_path}...")
    try:
        req = youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        )
        res = req.execute()
        print("  ✓ Custom thumbnail successfully attached to video!")
        return True
    except HttpError as e:
        print(f"  ⚠️ Failed to attach thumbnail: {e}")
        return False


# ═════════════════════════════════════════════════════════════════════════════
# 4. MASTER END-TO-END PUBLISH PIPELINE
# ═════════════════════════════════════════════════════════════════════════════

def publish_broadcast_to_youtube(
    video_path: str,
    thumbnail_path: str,
    all_stories: list = None,
    privacy_status: str = "unlisted",
    client_secrets_file: str = CLIENT_SECRETS_FILE,
    token_file: str = TOKEN_FILE,
    notify_email: bool = True
) -> dict:
    """
    High-level entrypoint for the pipeline:
    1. Generates VidIQ-style Title, 5K Description & Tags.
    2. Uploads video via resumable chunked stream.
    3. Attaches custom thumbnail.
    4. Sends instant notification to user's Gmail with clickable links.
    """
    print("\n" + "═" * 70)
    print("🚀 [MP4 NEWS] INITIATING AUTOMATED YOUTUBE UPLOAD & PUBLISH")
    print("═" * 70)

    # 1. Generate SEO Metadata Package
    seo_pkg = generate_youtube_seo_package(all_stories=all_stories, bottom_number="50")
    print(f"  ✓ SEO Package Ready: '{seo_pkg['title']}'")
    print(f"  ✓ Video Upload Tags Box: KEPT EMPTY (as instructed)")
    print(f"  ✓ Description: {seo_pkg['desc_length']} chars (Zero Emojis, Zero Timestamps)")

    # 2. Authenticate
    youtube = get_authenticated_youtube_service(client_secrets_file, token_file)

    # 3. Resumable Upload (tags box kept 100% empty)
    video_id = upload_video_resumable(
        youtube=youtube,
        video_path=video_path,
        title=seo_pkg["title"],
        description=seo_pkg["description"],
        tags=[],
        category_id=seo_pkg["categoryId"],
        privacy_status=privacy_status
    )

    # 4. Attach Thumbnail
    thumb_ok = attach_custom_thumbnail(youtube, video_id, thumbnail_path)
    thumb_status = "Attached ✅" if thumb_ok else "Not attached ⚠️"

    watch_url = f"https://youtu.be/{video_id}"
    studio_url = f"https://studio.youtube.com/video/{video_id}/edit"

    print("\n" + "═" * 70)
    print("🎉 YOUTUBE PUBLISH SUCCESSFUL!")
    print(f"  🔗 Watch URL:       {watch_url}")
    print(f"  🛠️ Studio Edit URL: {studio_url}")
    print("═" * 70 + "\n")

    # 5. Instant Gmail Notification
    if notify_email:
        send_upload_notification(
            video_id=video_id,
            title=seo_pkg["title"],
            privacy_status=privacy_status,
            thumbnail_status=thumb_status,
            tags_count=seo_pkg["tags_count"],
            chapters_count=len(all_stories) if all_stories else 50,
            video_path=video_path
        )

    return {
        "success": True,
        "video_id": video_id,
        "watch_url": watch_url,
        "studio_url": studio_url,
        "title": seo_pkg["title"],
        "privacy_status": privacy_status
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube Automated Uploader")
    parser.add_argument("--auth-only", action="store_true", help="Authorize OAuth and cache token.json without uploading")
    parser.add_argument("--video", type=str, default="", help="Path to MP4 video file to upload")
    parser.add_argument("--thumbnail", type=str, default="", help="Path to JPG thumbnail file")
    parser.add_argument("--privacy", type=str, default="unlisted", choices=["private", "unlisted", "public"], help="Privacy status")
    args = parser.parse_args()

    if args.auth_only:
        print("Authorizing YouTube API...")
        get_authenticated_youtube_service()
        print("✓ Authorization complete and cached to token.json!")
    elif args.video:
        publish_broadcast_to_youtube(
            video_path=args.video,
            thumbnail_path=args.thumbnail,
            privacy_status=args.privacy
        )
    else:
        print("Usage:")
        print("  python youtube_uploader.py --auth-only")
        print("  python youtube_uploader.py --video <path_to.mp4> --thumbnail <path_to.jpg> --privacy unlisted")

