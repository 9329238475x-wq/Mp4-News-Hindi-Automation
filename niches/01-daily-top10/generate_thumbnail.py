#!/usr/bin/env python3
"""
🔥 सनसनी न्यूज़ Thumbnail Generator — Ultra-Sensational Indian News Channel Style
(Aaj Tak / ABP News / TV9 Bharatvarsh style)

Generates 1280×720 broadcast-grade thumbnails using Headless Chrome/Edge
with perfect Devanagari font shaping, glow effects, and sensational styling.
Falls back to Pillow if headless browser is unavailable.
"""

import os
import sys
import glob
import shutil
import tempfile
import subprocess
from pathlib import Path

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ─── Constants ───────────────────────────────────────────────────────────────
THUMB_W, THUMB_H = 1280, 720
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
FONT_BOLD_PATH = str(PROJECT_ROOT / "assets" / "NotoSansDevanagari-Bold.ttf").replace("\\", "/")


def find_browser_executable() -> str:
    """Find Google Chrome, Chromium, or Microsoft Edge executable."""
    candidates = [
        # Windows standard paths
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        # Linux / Kaggle paths
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p

    # Check system PATH
    for cmd in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "msedge", "chrome"]:
        w = shutil.which(cmd)
        if w:
            return w

    return None


def build_sensational_html(
    headline: str,
    photo_file_url: str,
    category: str = "क्राइम",
    channel_name: str = "MP4 NEWS हिन्दी",
) -> str:
    """
    Construct high-impact HTML/CSS template for the sensational thumbnail.
    """
    cat_badge = category if category else "सनसनीख़ेज़"
    shock_text = "⚠️ दिल दहलाने वाली वारदात"
    
    if "क्राइम" in cat_badge or "अपराध" in cat_badge or "हत्या" in headline:
        cat_badge = "🚨 क्राइम अलर्ट"
        shock_text = "⚠️ सनसनीख़ेज़ वारदात"
    elif "राजनीति" in cat_badge or "सियासत" in cat_badge:
        cat_badge = "🏛️ बड़ा सियासी उलटफेर"
        shock_text = "⚡ धमाकेदार खुलासा"
    elif "देश" in cat_badge or "भारत" in cat_badge:
        cat_badge = "🇮🇳 बड़ी राष्ट्रीय ख़बर"
        shock_text = "⚡ देश का बड़ा मुद्दा"
    elif not cat_badge.startswith(("🚨", "🔥", "⚡", "🔴", "🏛️", "🇮🇳")):
        cat_badge = f"⚡ {cat_badge}"

    # Auto font size calculation based on headline length
    text_len = len(headline)
    if text_len <= 35:
        font_size = "66px"
        line_height = "1.24"
    elif text_len <= 60:
        font_size = "58px"
        line_height = "1.26"
    elif text_len <= 85:
        font_size = "48px"
        line_height = "1.28"
    else:
        font_size = "42px"
        line_height = "1.30"

    html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<style>
  @font-face {{
    font-family: 'LocalHindiBold';
    src: url('file:///{FONT_BOLD_PATH}') format('truetype');
  }}

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    width: 1280px;
    height: 720px;
    overflow: hidden;
    background: #060000;
    font-family: 'LocalHindiBold', 'Nirmala UI', 'Segoe UI', sans-serif;
    position: relative;
    user-select: none;
  }}

  /* High Energy Crimson Atmosphere */
  .bg-glow {{
    position: absolute;
    inset: 0;
    background: 
      radial-gradient(circle at 78% 48%, rgba(230, 0, 0, 0.65) 0%, rgba(100, 0, 0, 0.9) 45%, rgba(8, 0, 0, 0.98) 85%),
      linear-gradient(135deg, #180000 0%, #060000 100%);
    z-index: 1;
  }}

  /* News Photo container with dynamic slant */
  .photo-container {{
    position: absolute;
    top: 0;
    left: 0;
    width: 590px;
    height: 720px;
    z-index: 2;
    overflow: hidden;
    clip-path: polygon(0 0, 100% 0, 82% 100%, 0 100%);
    background: #110000;
  }}

  .photo-img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    filter: contrast(1.32) saturate(1.3) brightness(0.92);
  }}

  .photo-overlay {{
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(0,0,0,0.1) 0%, rgba(160, 0, 0, 0.3) 65%, rgba(20, 0, 0, 0.96) 100%);
    mix-blend-mode: multiply;
  }}

  /* Laser neon divider */
  .laser-divider {{
    position: absolute;
    top: 0;
    left: 585px;
    width: 9px;
    height: 720px;
    background: linear-gradient(180deg, #ffea00, #ff0033, #ffea00);
    box-shadow: 0 0 25px #ff0000, 0 0 50px #ff3300, 0 0 12px #ffffff;
    transform: skewX(-10.5deg);
    transform-origin: top left;
    z-index: 3;
  }}

  /* Header Bar */
  .header-bar {{
    position: absolute;
    top: 20px;
    left: 25px;
    right: 25px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 10;
  }}

  .breaking-badge {{
    display: inline-flex;
    align-items: center;
    gap: 12px;
    background: linear-gradient(90deg, #d90429 0%, #ff0f38 100%);
    padding: 10px 26px;
    border-radius: 8px;
    border: 2px solid #ffffff;
    box-shadow: 0 6px 25px rgba(255, 15, 56, 0.75), inset 0 1px 0 rgba(255,255,255,0.4);
  }}

  .live-dot {{
    width: 18px;
    height: 18px;
    background: #ffffff;
    border-radius: 50%;
    box-shadow: 0 0 15px #ffffff;
  }}

  .breaking-text {{
    color: #ffffff;
    font-size: 28px;
    font-weight: 900;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    text-shadow: 0 2px 5px rgba(0, 0, 0, 0.6);
  }}

  .category-badge {{
    background: linear-gradient(90deg, #ffb703 0%, #fb8500 100%);
    color: #000000;
    font-size: 24px;
    font-weight: 900;
    padding: 9px 24px;
    border-radius: 8px;
    border: 2px solid #fff275;
    box-shadow: 0 5px 20px rgba(251, 133, 0, 0.7);
  }}

  /* Headline Zone (Bigger, bolder, more sensational!) */
  .headline-zone {{
    position: absolute;
    top: 100px;
    bottom: 75px;
    left: 550px;
    right: 30px;
    z-index: 10;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
  }}

  .headline-pill-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
  }}

  .headline-kicker {{
    background: #ffffff;
    color: #cc0000;
    font-size: 24px;
    font-weight: 900;
    padding: 5px 18px;
    border-radius: 4px;
    letter-spacing: 1px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    border-left: 6px solid #ffcc00;
  }}

  .shock-pill {{
    background: #e60000;
    color: #ffffff;
    font-size: 22px;
    font-weight: 900;
    padding: 5px 16px;
    border-radius: 4px;
    border: 1px solid #ff8080;
    box-shadow: 0 4px 12px rgba(230, 0, 0, 0.6);
  }}

  .headline-text {{
    font-size: {font_size};
    line-height: {line_height};
    font-weight: 900;
    color: #FFF000;
    -webkit-text-stroke: 3.5px #000000;
    text-shadow: 
      5px 5px 0 #000000,
      -3px -3px 0 #000000,
      4px -4px 0 #000000,
      -4px 4px 0 #000000,
      0 8px 25px rgba(0, 0, 0, 0.98),
      0 0 45px rgba(255, 30, 0, 0.9);
    word-break: break-word;
  }}

  /* Footer bar */
  .footer-bar {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 62px;
    background: linear-gradient(90deg, #0d0000 0%, #200000 45%, #050000 100%);
    border-top: 3px solid #ff0033;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 32px;
    z-index: 12;
    box-shadow: 0 -6px 25px rgba(0,0,0,0.85);
  }}

  .channel-logo {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  .logo-icon {{
    background: #ff0000;
    color: #ffffff;
    font-size: 22px;
    font-weight: 900;
    padding: 4px 12px;
    border-radius: 5px;
    border: 1.5px solid #ff9999;
  }}

  .logo-name {{
    color: #ffffff;
    font-size: 25px;
    font-weight: 900;
    letter-spacing: 0.5px;
  }}

  .logo-name span {{
    color: #fff000;
  }}

  .footer-tagline {{
    color: #ff4d4d;
    font-size: 21px;
    font-weight: 800;
    letter-spacing: 1px;
  }}

  .vignette {{
    position: absolute;
    inset: 0;
    box-shadow: inset 0 0 100px rgba(0, 0, 0, 0.85);
    pointer-events: none;
    z-index: 20;
  }}
</style>
</head>
<body>
  <div class="bg-glow"></div>

  <div class="photo-container">
    {f'<img class="photo-img" src="{photo_file_url}" alt="News Photo" />' if photo_file_url else ''}
    <div class="photo-overlay"></div>
  </div>

  <div class="laser-divider"></div>

  <div class="header-bar">
    <div class="breaking-badge">
      <div class="live-dot"></div>
      <div class="breaking-text">🔴 ब्रेकिंग न्यूज़</div>
    </div>
    <div class="category-badge">{cat_badge}</div>
  </div>

  <div class="headline-zone">
    <div class="headline-pill-row">
      <div class="headline-kicker">एक्सक्लूसिव रिपोर्ट</div>
      <div class="shock-pill">{shock_text}</div>
    </div>
    <h1 class="headline-text">{headline}</h1>
  </div>

  <div class="footer-bar">
    <div class="channel-logo">
      <div class="logo-icon">MP4</div>
      <div class="logo-name">NEWS <span>हिन्दी</span></div>
    </div>
    <div class="footer-tagline">देश का सबसे तेज़ और सटीक न्यूज़ नेटवर्क</div>
  </div>

  <div class="vignette"></div>
</body>
</html>
"""
    return html


def generate_sensational_thumbnail(
    headline: str,
    photo_path: str,
    out_path: str,
    category: str = "",
    channel_name: str = "MP4 NEWS हिन्दी",
) -> str:
    """
    Generate sensational 1280x720 thumbnail for Indian YouTube Hindi News.
    Uses Headless Chrome/Edge for flawless Devanagari text shaping and neon graphics.
    """
    clean_hl = headline.strip().rstrip("।.")
    if not clean_hl.endswith("!"):
        clean_hl += "!"

    print(f"🎨 Generating sensational thumbnail: {clean_hl[:45]}...")
    out_dir = os.path.dirname(out_path) or "."
    os.makedirs(out_dir, exist_ok=True)

    browser = find_browser_executable()
    photo_file_url = ""
    if photo_path and os.path.exists(photo_path):
        photo_file_url = "file:///" + os.path.abspath(photo_path).replace("\\", "/")

    if browser:
        # ─── Headless Browser Method ─────────────────────────────────────────
        html_content = build_sensational_html(
            headline=clean_hl,
            photo_file_url=photo_file_url,
            category=category,
            channel_name=channel_name,
        )

        tmp_html = os.path.join(out_dir, "_temp_thumbnail.html")
        with open(tmp_html, "w", encoding="utf-8") as f:
            f.write(html_content)

        user_data = tempfile.mkdtemp()
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--allow-file-access-from-files",
            f"--user-data-dir={user_data}",
            "--window-size=1280,720",
            f"--screenshot={out_path}",
            f"file:///{os.path.abspath(tmp_html).replace(os.sep, '/')}",
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            # Cleanup temp files
            try:
                os.remove(tmp_html)
                shutil.rmtree(user_data, ignore_errors=True)
            except Exception:
                pass

            if res.returncode == 0 and os.path.exists(out_path):
                size_kb = os.path.getsize(out_path) / 1024
                print(f"✅ Sensational Thumbnail Ready: {out_path} ({size_kb:.0f} KB, 1280×720)")
                return out_path
            else:
                print(f"⚠️ Browser screenshot returned {res.returncode}: {res.stderr}")
        except Exception as e:
            print(f"⚠️ Browser screenshot failed: {e}")

    # ─── Fallback (if browser fails) ─────────────────────────────────────────
    print("⚠️ Fallback: Generating with Pillow...")
    return _generate_with_pillow(clean_hl, photo_path, out_path)


def _generate_with_pillow(headline: str, photo_path: str, out_path: str) -> str:
    """Basic Pillow fallback when headless browser is not available."""
    from PIL import Image, ImageDraw, ImageFont

    canvas = Image.new("RGB", (THUMB_W, THUMB_H), (20, 0, 0))
    draw = ImageDraw.Draw(canvas)

    if photo_path and os.path.exists(photo_path):
        try:
            photo = Image.open(photo_path).convert("RGB")
            photo = photo.resize((540, 720))
            canvas.paste(photo, (0, 0))
        except Exception:
            pass

    font_path = str(PROJECT_ROOT / "assets" / "NotoSansDevanagari-Bold.ttf")
    try:
        font = ImageFont.truetype(font_path, 48)
    except Exception:
        font = ImageFont.load_default()

    draw.rectangle([0, 0, THUMB_W, 60], fill=(220, 0, 0))
    draw.text((20, 15), "ब्रेकिंग न्यूज़", fill=(255, 255, 255), font=font)
    draw.text((580, 200), headline[:80], fill=(255, 230, 0), font=font)

    canvas.save(out_path, "JPEG", quality=90)
    return out_path


# ─── CLI / Demo ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="🔥 Sensational Thumbnail Generator")
    parser.add_argument("--demo", action="store_true", help="Generate demo thumbnail for story_01")
    parser.add_argument("--headline", type=str, help="Hindi headline")
    parser.add_argument("--photo", type=str, help="News photo path")
    parser.add_argument("--category", type=str, default="क्राइम", help="Category")
    parser.add_argument("--out", type=str, help="Output path")
    args = parser.parse_args()

    if args.demo:
        out_dir = PROJECT_ROOT / "out" / "story_01"
        img_dir = out_dir / "news real image"

        images = sorted(
            img_dir.glob("*.jpg"),
            key=lambda p: p.stat().st_size,
            reverse=True,
        )
        best_photo = str(images[0]) if images else ""
        demo_headline = "बरेली के पैगा गांव में वृद्धा की गला दबाकर हत्या!"
        demo_out = str(out_dir / "thumbnail_01.jpg")

        generate_sensational_thumbnail(
            headline=demo_headline,
            photo_path=best_photo,
            out_path=demo_out,
            category="क्राइम",
        )
    elif args.headline and args.photo and args.out:
        generate_sensational_thumbnail(
            headline=args.headline,
            photo_path=args.photo,
            out_path=args.out,
            category=args.category,
        )
    else:
        parser.print_help()
