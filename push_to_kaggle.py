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

print("=" * 65, flush=True)
print("🚀 [MP4 NEWS HINDI] KAGGLE HIGH-PERFORMANCE BROADCAST ENGINE TRIGGER", flush=True)
print("=" * 65, flush=True)

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
    print(f"✓ Kaggle authenticated as: {kaggle_user}", flush=True)

# Initialize Kaggle API
from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi()
api.authenticate()

kernel_slug = "mp4-news-hindi-omnivoice-pipeline"
kernel_id = f"{kaggle_user}/{kernel_slug}"

print(f"🚀 Deploying kernel to Kaggle ({kernel_id})...", flush=True)
try:
    push_res = api.kernels_push(str(ROOT))
    print(f"✓ Kernel push result: versionNumber={getattr(push_res, 'versionNumber', 'unknown')}", flush=True)
except Exception as e:
    print(f"❌ Failed to push kernel via SDK: {e}", flush=True)
    sys.exit(1)

print("\n🎉 KERNEL TRIGGERED ON KAGGLE!", flush=True)
print(f"🔗 Live Progress: https://www.kaggle.com/code/{kernel_id}", flush=True)
print("\n⏳ Monitoring execution status...", flush=True)

# Poll until completion
max_wait = 2400  # 40 minutes max
start_time = time.time()
last_status = ""

while time.time() - start_time < max_wait:
    time.sleep(15)
    try:
        st_res = api.kernels_status(kernel_id)
        if isinstance(st_res, dict):
            raw_status = st_res.get("status", "")
            fail_msg = st_res.get("failureMessage") or st_res.get("failure_message")
        else:
            raw_status = getattr(st_res, "status", "")
            fail_msg = getattr(st_res, "failure_message", None) or getattr(st_res, "failureMessage", None)
        current_status = str(raw_status).upper()
        elapsed = int(time.time() - start_time)
        print(f"[{elapsed:3d}s] Status: {current_status}", flush=True)

        if "COMPLETE" in current_status:
            print("\n✅ KAGGLE PIPELINE COMPLETED SUCCESSFULLY!", flush=True)
            break
        elif "ERROR" in current_status or fail_msg:
            print(f"\n⚠️ Kernel ended with ERROR: {fail_msg}", flush=True)
            try:
                print("\n📋 Fetching Kaggle execution error logs...", flush=True)
                k_logs = api.kernels_logs(kernel_id)
                if k_logs:
                    import json as _js
                    parsed_logs = _js.loads(k_logs) if isinstance(k_logs, str) else k_logs
                    for entry in parsed_logs[-30:]:
                        stream = entry.get("stream_name", "")
                        data = entry.get("data", "")
                        if stream == "stderr" or "error" in data.lower() or "exception" in data.lower():
                            print(f"  [{stream}] {data.strip()}", flush=True)
            except Exception as _log_e:
                print(f"  (Could not fetch logs: {_log_e})", flush=True)
            break
        elif "CANCEL" in current_status:
            print("\n⚠️ Kernel execution was CANCELLED.", flush=True)
            break
    except Exception as e:
        print(f"  [Notice] Status check retry: {e}", flush=True)

# Download output artifacts
out_dir = ROOT / "out"
out_dir.mkdir(parents=True, exist_ok=True)
print("\n📥 Fetching output files from Kaggle...", flush=True)

for attempt in range(1, 4):
    try:
        import builtins, contextlib, io
        _orig_open = builtins.open

        def _safe_open(*args, **kwargs):
            mode = args[1] if len(args) > 1 else kwargs.get("mode", "r")
            if "b" not in mode and "encoding" not in kwargs:
                kwargs["encoding"] = "utf-8"
                kwargs["errors"] = "replace"
            return _orig_open(*args, **kwargs)

        builtins.open = _safe_open
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                files, _ = api.kernels_output(kernel_id, path=str(out_dir), force=True, quiet=True)
        finally:
            builtins.open = _orig_open

        print(f"✓ Downloaded {len(files) if files else 0} output files to {out_dir}", flush=True)
        break
    except Exception as e:
        print(f"Notice during download (attempt {attempt}/3): {e}", flush=True)
        if attempt < 3:
            time.sleep(10)

# Clean up any residual or stale zip archives (User requested: zero zip files)
for z in out_dir.glob("*.zip"):
    try:
        z.unlink(missing_ok=True)
    except Exception:
        pass

# Sync root artifacts into out/story_01/ so user opening out/story_01/script_1.txt sees latest
story_01_dir = out_dir / "story_01"
story_01_dir.mkdir(parents=True, exist_ok=True)
for item_name in ["script_1.txt", "story_1_data.json", "thumbnail_01.jpg"]:
    src_item = out_dir / item_name
    dst_item = story_01_dir / item_name
    if src_item.exists():
        shutil.copy2(src_item, dst_item)

# Check for rendered video
mp4_files = list(out_dir.rglob("*.mp4"))
if mp4_files:
    for mp4 in mp4_files:
        print(f"\n🎬 RENDERED BROADCAST VIDEO: {mp4}", flush=True)
        print(f"📊 Size: {mp4.stat().st_size / (1024*1024):.2f} MB", flush=True)
else:
    print("\nℹ️ No .mp4 found directly. Listing downloaded files:", flush=True)
    for f in out_dir.iterdir():
        print(f" - {f.name} ({f.stat().st_size} bytes)", flush=True)
