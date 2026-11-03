"""
MP4 News Hindi - Automated Kaggle GPU Trigger & Video Fetcher
Triggers the Kaggle GPU kernel, monitors progress, and downloads the rendered broadcast video.
"""
import os
import sys
import time
import json
import shutil
import zipfile
from pathlib import Path

# Ensure UTF-8 stdout across all operating systems
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent

print("=" * 65)
print("🚀 [MP4 NEWS HINDI] KAGGLE GPU BROADCAST ENGINE TRIGGER")
print("=" * 65)

# 1. Configure Kaggle Credentials from env or file
kaggle_user = os.environ.get("KAGGLE_USERNAME", "")
kaggle_key = os.environ.get("KAGGLE_KEY", "")

kaggle_dir = Path.home() / ".kaggle"
kaggle_json = kaggle_dir / "kaggle.json"
local_creds = ROOT / "News Kaggle.json"

if not (kaggle_user and kaggle_key):
    if local_creds.exists():
        with open(local_creds, "r", encoding="utf-8") as f:
            c = json.load(f)
            kaggle_user = c.get("username", "")
            kaggle_key = c.get("key", "")

if kaggle_user and kaggle_key:
    kaggle_dir.mkdir(parents=True, exist_ok=True)
    with open(kaggle_json, "w", encoding="utf-8") as f:
        json.dump({"username": kaggle_user, "key": kaggle_key}, f)
    print(f"✓ Kaggle authenticated as: {kaggle_user}")

# Initialize Kaggle API
from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi()
api.authenticate()

kernel_slug = "mp4-news-hindi-omnivoice-pipeline"
kernel_id = f"{kaggle_user}/{kernel_slug}"

print(f"🚀 Deploying kernel to Kaggle GPU ({kernel_id})...")
try:
    push_res = api.kernels_push(str(ROOT))
    print(f"✓ Kernel push result: versionNumber={getattr(push_res, 'versionNumber', 'unknown')}")
except Exception as e:
    print(f"❌ Failed to push kernel via SDK: {e}")
    sys.exit(1)

print("\n🎉 KERNEL TRIGGERED ON KAGGLE GPU!")
print(f"🔗 Live Progress: https://www.kaggle.com/code/{kernel_id}")
print("\n⏳ Monitoring execution status (typically takes 3-5 minutes on GPU)...")

# Poll until completion
max_wait = 900  # 15 minutes max
start_time = time.time()
last_status = ""

while time.time() - start_time < max_wait:
    time.sleep(15)
    try:
        st_res = api.kernels_status(kernel_id)
        current_status = str(st_res.get("status", "")).upper()
        fail_msg = st_res.get("failureMessage")
        elapsed = int(time.time() - start_time)
        print(f"[{elapsed:3d}s] Status: {current_status}")

        if "COMPLETE" in current_status:
            print("\n✅ KAGGLE GPU PIPELINE COMPLETED SUCCESSFULLY!")
            break
        elif "ERROR" in current_status or fail_msg:
            print(f"\n⚠️ Kernel ended with ERROR: {fail_msg}")
            break
        elif "CANCEL" in current_status:
            print("\n⚠️ Kernel execution was CANCELLED.")
            break
    except Exception as e:
        print(f"  [Notice] Status check retry: {e}")

# Download output artifacts
out_dir = ROOT / "out"
out_dir.mkdir(parents=True, exist_ok=True)
print("\n📥 Fetching output files from Kaggle...")

try:
    files, _ = api.kernels_output(kernel_id, path=str(out_dir), force=True, quiet=False)
    print(f"✓ Downloaded {len(files) if files else 0} output files to {out_dir}")
except Exception as e:
    print(f"Notice during download: {e}")

# If output zip exists, unpack it into out_dir
zip_files = list(out_dir.glob("*.zip"))
for z in zip_files:
    print(f"📦 Extracting archive: {z.name}...")
    try:
        with zipfile.ZipFile(z, "r") as zf:
            zf.extractall(out_dir)
        print(f"✓ Extracted {z.name}")
    except Exception as e:
        print(f"Extract error: {e}")

# Check for rendered video
mp4_files = list(out_dir.rglob("*.mp4"))
if mp4_files:
    for mp4 in mp4_files:
        print(f"\n🎬 RENDERED BROADCAST VIDEO: {mp4}")
        print(f"📊 Size: {mp4.stat().st_size / (1024*1024):.2f} MB")
else:
    print("\nℹ️ No .mp4 found directly. Listing downloaded files:")
    for f in out_dir.iterdir():
        print(f" - {f.name} ({f.stat().st_size} bytes)")
