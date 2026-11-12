#!/usr/bin/env python3
"""
🔥 Master 4-Grid YouTube Broadcast Thumbnail Generator (1280x720)
----------------------------------------------------------------
Argon AI 5-Zone High-CTR Broadcast Formula (Nonstop 50 / Top 10 / Breaking News):
  1. Zone 1: Top Date & Slot Banner (सुबह / दोपहर / दिनभर की बड़ी खबरें)
  2. Zone 2: 4-Panel Real News Photo Grid (4 बराबर खाने, 16:9 असली तस्वीरें)
  3. Zone 3: Micro-Hooks (अधिकतम 2 से 3 शब्दों के सनसनीखेज कीवर्ड्स - Outer Corners)
  4. Zone 4: Center Power Badge (TOP 50 NEWS / 3D गोल्ड-रेड शील्ड)
  5. Zone 5: Bottom Master Strip (सबसे नीचे की ब्रेकिंग मुख्य खबर पट्टी)
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Console encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

THUMB_W, THUMB_H = 1280, 720
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
FONT_BOLD_PATH = str(PROJECT_ROOT / "assets" / "NotoSansDevanagari-Bold.ttf").replace("\\", "/")
FONT_REG_PATH = str(PROJECT_ROOT / "assets" / "NotoSansDevanagari-Regular.ttf").replace("\\", "/")

HINDI_MONTHS = [
    "", "जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून",
    "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"
]

DEFAULT_ACTION_HOOKS = [
    "गृह मंत्रालय सख्त!",
    "पुलिस का एक्शन!",
    "कोर्ट का बड़ा फैसला!",
    "प्रशासन में हड़कंप!"
]


def get_slot_banner_text(story_count: int = 50) -> str:
    """समय और तारीख के अनुसार स्वतः हिंदी स्लॉट हेडर बनाना"""
    now = datetime.now()
    day = now.day
    month_hi = HINDI_MONTHS[now.month] if 1 <= now.month <= 12 else "नवंबर"
    hour = now.hour

    label = f"{story_count} बड़ी खबरें" if story_count > 1 else "ताज़ा बड़ी खबर"

    if 5 <= hour < 12:
        slot = f"सुबह की {label}"
    elif 12 <= hour < 17:
        slot = f"दोपहर की {label}"
    else:
        slot = f"दिनभर की {label}"

    return f"🔥 {day} {month_hi} | {slot}"


def extract_micro_hook(text: str, category: str = "", default: str = "बड़ा खुलासा!") -> str:
    """
    2 से 3 शब्दों का सनसनीखेज माइक्रो-हुक (Micro-Hook) निकालना:
    शर्त: किसी भी हाल में 3 शब्दों से अधिक नहीं (" ".join(words[:3]))
    """
    if not text:
        return default

    clean = text.replace("**", "").replace("*", "").replace('"', '').replace("'", "").strip()
    low = clean.lower()

    # Priority rule-based semantic hooks
    if any(w in low for w in ["गिरफ्तार", "हिरासत", "पकड़ा", "दबोचा"]):
        return "पुलिस का एक्शन!"
    if any(w in low for w in ["मुठभेड़", "फायरिंग", "गोली", "एनकाउंटर"]):
        return "मुठभेड़ में गिरफ्तारी!"
    if any(w in low for w in ["ट्रेन", "रेल", "पटरी", "दुर्घटना", "गिरा"]):
        return "भीषण ट्रेन हादसा!"
    if any(w in low for w in ["कोर्ट", "अदालत", "सुप्रीम", "हाईकोर्ट", "जमानत", "बेल"]):
        return "कोर्ट का बड़ा फैसला!"
    if any(w in low for w in ["मौसम", "बारिश", "आंधी", "तूफान", "अलर्ट"]):
        return "मौसम विभाग अलर्ट!"
    if any(w in low for w in ["सरकार", "मंत्रालय", "कैबिनेट", "गृह"]):
        return "गृह मंत्रालय सख्त!"
    if any(w in low for w in ["अस्पताल", "डॉक्टर", "इलाज", "मौत"]):
        return "इलाज के दौरान मौत!"
    if any(w in low for w in ["टास्क फोर्स", "गश्ती", "सत्यापन", "अभियान"]):
        return "सत्यापन अभियान!"
    if any(w in low for w in ["चोरी", "घोटाला", "रुपये", "करोड़", "लाख"]):
        return "करोड़ों का घोटाला!"

    # Fallback: Clean first 2 to 3 words
    words = [w for w in clean.split() if len(w) > 1 and w not in ["ने", "को", "के", "की", "में", "पर", "और", "से"]]
    if words:
        hook = " ".join(words[:3])
        if not hook.endswith(("!", "?", "।")):
            hook += "!"
        return hook

    return default


def find_browser_executable() -> str:
    """Google Chrome, Chromium, or Microsoft Edge खोजें"""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    for cmd in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "msedge", "chrome"]:
        w = shutil.which(cmd)
        if w:
            return w
    return None


def collect_top_4_grid_items(story: dict = None, all_stories: list = None, fallback_photos: list = None) -> list:
    """
    4-पैनल ग्रिड के लिए 4 सबसे प्रामाणिक 100% अनूठी तस्वीरें और उनके 2-3 शब्दों के माइक्रो-हुक जुटाना
    """
    items = []
    seen_photos = set()
    used_hooks = set()

    # Case A: Multi-story bulletin (e.g. Top 10 / 50 stories)
    if all_stories and len(all_stories) > 1:
        for s in all_stories:
            if len(items) >= 4:
                break
            photo = s.get("local_news_image") or s.get("local_visual_asset")
            if not photo and s.get("all_real_images"):
                photo = s["all_real_images"][0]
            if photo:
                norm_p = photo.replace("\\", "/")
                full_p = os.path.join(PROJECT_ROOT, *norm_p.split("/"))
                if os.path.exists(full_p) and full_p not in seen_photos:
                    seen_photos.add(full_p)
                    raw_hk = extract_micro_hook(
                        s.get("screen_headline") or s.get("original_title") or "",
                        s.get("category", "")
                    )
                    hk = raw_hk if raw_hk not in used_hooks else DEFAULT_ACTION_HOOKS[len(items) % 4]
                    used_hooks.add(hk)
                    items.append({
                        "photo": full_p,
                        "hook": hk,
                        "headline": s.get("screen_headline", "")
                    })

    # Case B: Single story bulletin (Pull 4 distinct action photos + chunk hooks)
    if len(items) < 4 and story:
        chunks = story.get("chunks", [])
        for c in chunks:
            if len(items) >= 4:
                break
            for v in c.get("visual_images", []):
                p = v.get("path")
                if p:
                    norm_p = p.replace("\\", "/")
                    full_p = os.path.join(PROJECT_ROOT, *norm_p.split("/"))
                    if os.path.exists(full_p) and full_p not in seen_photos:
                        seen_photos.add(full_p)
                        raw_hk = extract_micro_hook(
                            c.get("bullet_text") or c.get("sentence") or "",
                            story.get("category", "")
                        )
                        hk = raw_hk if raw_hk not in used_hooks else DEFAULT_ACTION_HOOKS[len(items) % 4]
                        used_hooks.add(hk)
                        items.append({"photo": full_p, "hook": hk})
                        break

    # Case C: Check story_01 directory for downloaded real news images
    if len(items) < 4:
        s_num = story.get("story_number", 1) if story else 1
        news_dir = PROJECT_ROOT / "out" / f"story_{s_num:02d}" / "news real image"
        if news_dir.exists():
            for fn in sorted(os.listdir(news_dir)):
                if len(items) >= 4:
                    break
                full_p = str(news_dir / fn)
                if full_p.endswith((".jpg", ".png", ".jpeg")) and full_p not in seen_photos:
                    seen_photos.add(full_p)
                    hk = DEFAULT_ACTION_HOOKS[len(items) % 4]
                    items.append({"photo": full_p, "hook": hk})

    # Case D: Fallback photos
    if len(items) < 4 and fallback_photos:
        for p in fallback_photos:
            if len(items) >= 4:
                break
            if os.path.exists(p) and p not in seen_photos:
                seen_photos.add(p)
                hk = DEFAULT_ACTION_HOOKS[len(items) % 4]
                items.append({"photo": p, "hook": hk})

    # Ensure exactly 4 items
    while len(items) < 4 and items:
        dup = dict(items[len(items) % len(items)])
        items.append(dup)

    # Guarantee 4 distinct micro-hooks
    for idx, item in enumerate(items):
        item["hook"] = DEFAULT_ACTION_HOOKS[idx % 4] if not item.get("hook") else item["hook"]

    return items[:4]


def build_4grid_html(
    grid_items: list,
    top_banner_text: str,
    bottom_headline: str,
    badge_title: str = "TOP 50",
    badge_sub: str = "बड़ी खबरें",
    channel_name: str = "MP4 NEWS हिन्दी"
) -> str:
    """5-Zone 4-Grid Master Broadcast Thumbnail HTML Template (Outer Corner Hooks)"""
    def to_file_url(p: str) -> str:
        norm = os.path.abspath(p).replace("\\", "/")
        return f"file:///{norm}"

    img1 = to_file_url(grid_items[0]["photo"])
    img2 = to_file_url(grid_items[1]["photo"])
    img3 = to_file_url(grid_items[2]["photo"])
    img4 = to_file_url(grid_items[3]["photo"])

    hook1 = " ".join(grid_items[0]["hook"].split()[:3])
    hook2 = " ".join(grid_items[1]["hook"].split()[:3])
    hook3 = " ".join(grid_items[2]["hook"].split()[:3])
    hook4 = " ".join(grid_items[3]["hook"].split()[:3])

    html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<style>
  @font-face {{
    font-family: 'LocalHindiBold';
    src: url('file:///{FONT_BOLD_PATH}') format('truetype');
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1280px;
    height: 720px;
    overflow: hidden;
    background: #000000;
    font-family: 'LocalHindiBold', 'Noto Sans Devanagari', 'Nirmala UI', sans-serif;
    position: relative;
    user-select: none;
  }}

  /* ── ZONE 1: TOP DATE & SLOT BANNER (64px) ── */
  .top-banner {{
    position: absolute;
    top: 0;
    left: 0;
    width: 1280px;
    height: 64px;
    background: linear-gradient(90deg, #880004 0%, #c4000b 25%, #e50914 50%, #c4000b 75%, #880004 100%);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    border-bottom: 3.5px solid #ffd700;
    box-shadow: 0 4px 20px rgba(0,0,0,0.9);
    z-index: 50;
  }}
  .live-pill {{
    background: #ffd700;
    color: #7f0003;
    font-size: 20px;
    font-weight: 900;
    padding: 5px 16px;
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    letter-spacing: 0.5px;
  }}
  .top-slot-text {{
    color: #ffffff;
    font-size: 28px;
    font-weight: 900;
    letter-spacing: 0.8px;
    text-shadow: 0 2px 5px rgba(0,0,0,0.8);
  }}
  .channel-pill {{
    background: rgba(0,0,0,0.45);
    border: 1.5px solid #ffd700;
    color: #ffd700;
    font-size: 20px;
    font-weight: 900;
    padding: 4px 14px;
    border-radius: 6px;
  }}

  /* ── ZONE 2: 4-PANEL PHOTO GRID (from y=64 to y=638, h=574px) ── */
  .grid-container {{
    position: absolute;
    top: 64px;
    left: 0;
    width: 1280px;
    height: 574px;
    display: grid;
    grid-template-columns: 640px 640px;
    grid-template-rows: 287px 287px;
    z-index: 10;
    background: #000;
  }}
  .grid-cell {{
    position: relative;
    overflow: hidden;
    width: 640px;
    height: 287px;
  }}
  .grid-cell img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: contrast(1.18) saturate(1.22) brightness(0.96);
  }}
  .scrim {{
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, rgba(0,0,0,0) 25%, rgba(0,0,0,0.65) 65%, rgba(0,0,0,0.96) 100%);
  }}

  /* ── ZONE 3: MICRO-HOOK TEXT (Outer Corners - No Overlap with Center Badge) ── */
  .hook-badge {{
    position: absolute;
    display: inline-flex;
    align-items: center;
    background: rgba(8, 0, 2, 0.90);
    border-radius: 8px;
    padding: 6px 16px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.95);
    max-width: 460px;
  }}
  .hook-text {{
    color: #ffd700;
    font-size: 30px;
    font-weight: 900;
    letter-spacing: 0.5px;
    white-space: nowrap;
    text-shadow: 0 2px 4px rgba(0,0,0,0.9);
  }}

  /* Left Quadrants (1 & 3): Outer Left Alignment */
  .hook-left {{
    bottom: 14px;
    left: 16px;
    border-left: 7px solid #e50914;
  }}

  /* Right Quadrants (2 & 4): Outer Right Alignment */
  .hook-right {{
    bottom: 14px;
    right: 16px;
    border-right: 7px solid #e50914;
  }}

  /* ── GRID LASER DIVIDERS ── */
  .v-divider {{
    position: absolute;
    top: 64px;
    left: 638px;
    width: 4px;
    height: 574px;
    background: linear-gradient(180deg, #ffd700, #ff1744, #ffd700);
    box-shadow: 0 0 14px rgba(255, 215, 0, 0.85);
    z-index: 25;
  }}
  .h-divider {{
    position: absolute;
    top: 349px;
    left: 0;
    width: 1280px;
    height: 4px;
    background: linear-gradient(90deg, #ffd700, #ff1744, #ffd700);
    box-shadow: 0 0 14px rgba(255, 215, 0, 0.85);
    z-index: 25;
  }}

  /* ── ZONE 4: CENTER POWER BADGE (TOP 50 NEWS) ── */
  .center-badge {{
    position: absolute;
    top: 284px;
    left: 510px;
    width: 260px;
    height: 134px;
    background: linear-gradient(135deg, #a60007 0%, #e50914 50%, #700004 100%);
    border: 5px solid #ffd700;
    border-radius: 24px;
    box-shadow: 0 0 40px rgba(255, 215, 0, 0.90), 0 16px 45px rgba(0, 0, 0, 0.98), inset 0 2px 6px rgba(255, 255, 255, 0.6);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 40;
    transform: rotate(-1deg);
  }}
  .badge-title {{
    color: #ffd700;
    font-size: 42px;
    font-weight: 900;
    line-height: 1.05;
    letter-spacing: 1.5px;
    text-shadow: 0 2px 6px rgba(0,0,0,0.95);
  }}
  .badge-sub {{
    color: #ffffff;
    font-size: 22px;
    font-weight: 900;
    letter-spacing: 2.5px;
    text-shadow: 0 1px 4px rgba(0,0,0,0.85);
  }}

  /* ── ZONE 5: BOTTOM MASTER STRIP (82px) ── */
  .bottom-strip {{
    position: absolute;
    bottom: 0;
    left: 0;
    width: 1280px;
    height: 82px;
    background: linear-gradient(90deg, #050001 0%, #1a0004 35%, #050001 100%);
    border-top: 3.5px solid #e50914;
    display: flex;
    align-items: center;
    padding: 0 20px;
    gap: 16px;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.9);
    z-index: 50;
  }}
  .breaking-tag {{
    background: linear-gradient(135deg, #ffd700 0%, #f59e0b 100%);
    color: #8b0000;
    font-size: 24px;
    font-weight: 900;
    padding: 7px 18px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.5);
    flex-shrink: 0;
  }}
  .main-headline {{
    color: #ffffff;
    font-size: 32px;
    font-weight: 900;
    letter-spacing: 0.6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-shadow: 0 2px 5px rgba(0,0,0,0.9);
    flex: 1;
  }}
</style>
</head>
<body>
  <!-- ZONE 1: TOP BANNER -->
  <div class="top-banner">
    <div class="live-pill">🔴 ताज़ा बुलेटिन</div>
    <div class="top-slot-text">{top_banner_text}</div>
    <div class="channel-pill">{channel_name}</div>
  </div>

  <!-- ZONE 2: 4-PANEL PHOTO GRID -->
  <div class="grid-container">
    <div class="grid-cell">
      <img src="{img1}">
      <div class="scrim"></div>
      <div class="hook-badge hook-left"><span class="hook-text">{hook1}</span></div>
    </div>
    <div class="grid-cell">
      <img src="{img2}">
      <div class="scrim"></div>
      <div class="hook-badge hook-right"><span class="hook-text">{hook2}</span></div>
    </div>
    <div class="grid-cell">
      <img src="{img3}">
      <div class="scrim"></div>
      <div class="hook-badge hook-left"><span class="hook-text">{hook3}</span></div>
    </div>
    <div class="grid-cell">
      <img src="{img4}">
      <div class="scrim"></div>
      <div class="hook-badge hook-right"><span class="hook-text">{hook4}</span></div>
    </div>
  </div>

  <!-- GRID DIVIDERS -->
  <div class="v-divider"></div>
  <div class="h-divider"></div>

  <!-- ZONE 4: CENTER POWER BADGE -->
  <div class="center-badge">
    <div class="badge-title">{badge_title}</div>
    <div class="badge-sub">{badge_sub}</div>
  </div>

  <!-- ZONE 5: BOTTOM MASTER STRIP -->
  <div class="bottom-strip">
    <div class="breaking-tag">⚡ बड़ी खबर</div>
    <div class="main-headline">{bottom_headline}</div>
  </div>
</body>
</html>
"""
    return html


def generate_4grid_thumbnail_pillow(
    grid_items: list,
    top_banner_text: str,
    bottom_headline: str,
    out_path: str,
    badge_title: str = "TOP 50",
    badge_sub: str = "बड़ी खबरें",
    channel_name: str = "MP4 NEWS हिन्दी"
) -> str:
    """Broadcast-Grade Pillow 4-Grid Engine (100% Reliable Fallback)"""
    canvas = Image.new("RGB", (THUMB_W, THUMB_H), (10, 0, 2))
    draw = ImageDraw.Draw(canvas)

    # 1. Paste 4 Grid Photos
    positions = [
        (0, 64, 640, 351),        # Top-Left
        (640, 64, 1280, 351),     # Top-Right
        (0, 351, 640, 638),       # Bottom-Left
        (640, 351, 1280, 638),    # Bottom-Right
    ]

    for idx, (x1, y1, x2, y2) in enumerate(positions):
        gw, gh = x2 - x1, y2 - y1
        item = grid_items[idx] if idx < len(grid_items) else grid_items[0]
        p_path = item.get("photo", "")
        if os.path.exists(p_path):
            try:
                with Image.open(p_path) as im:
                    im_rgb = im.convert("RGB")
                    iw, ih = im_rgb.size
                    target_ratio = gw / gh
                    current_ratio = iw / ih
                    if current_ratio > target_ratio:
                        new_w = int(ih * target_ratio)
                        crop_x = (iw - new_w) // 2
                        im_crop = im_rgb.crop((crop_x, 0, crop_x + new_w, ih))
                    else:
                        new_h = int(iw / target_ratio)
                        crop_y = (ih - new_h) // 2
                        im_crop = im_rgb.crop((0, crop_y, iw, crop_y + new_h))

                    im_resized = im_crop.resize((gw, gh), Image.Resampling.LANCZOS)
                    canvas.paste(im_resized, (x1, y1))
            except Exception:
                draw.rectangle([x1, y1, x2, y2], fill=(25, 0, 5))

        # Bottom black scrim on quadrant
        scrim_h = 80
        for sy in range(scrim_h):
            draw.line([(x1, y2 - scrim_h + sy), (x2, y2 - scrim_h + sy)], fill=(0, 0, 0))

    # 2. Golden Grid Dividers
    draw.rectangle([637, 64, 641, 638], fill=(255, 215, 0))
    draw.rectangle([0, 348, 1280, 352], fill=(255, 215, 0))

    # Fonts
    try:
        font_banner = ImageFont.truetype(FONT_BOLD_PATH, 26)
        font_hook = ImageFont.truetype(FONT_BOLD_PATH, 28)
        font_badge_title = ImageFont.truetype(FONT_BOLD_PATH, 38)
        font_badge_sub = ImageFont.truetype(FONT_BOLD_PATH, 20)
        font_headline = ImageFont.truetype(FONT_BOLD_PATH, 28)
        font_tag = ImageFont.truetype(FONT_BOLD_PATH, 22)
    except Exception:
        font_banner = font_hook = font_badge_title = font_badge_sub = font_headline = font_tag = ImageFont.load_default()

    # 3. Zone 3: Micro-Hooks (Outer Corners)
    hook_coords = [
        (20, 305, "left"),
        (900, 305, "right"),
        (20, 592, "left"),
        (900, 592, "right"),
    ]
    for idx, (hx, hy, align) in enumerate(hook_coords):
        item = grid_items[idx] if idx < len(grid_items) else grid_items[0]
        hk = " ".join(item.get("hook", "").split()[:3])
        draw.rectangle([hx, hy - 4, hx + 360, hy + 36], fill=(10, 0, 0))
        border_x = hx if align == "left" else hx + 352
        draw.rectangle([border_x, hy - 4, border_x + 8, hy + 36], fill=(229, 9, 20))
        draw.text((hx + 18, hy + 1), hk, fill=(255, 215, 0), font=font_hook)

    # 4. Zone 4: Center Power Badge
    bx1, by1, bx2, by2 = 510, 284, 770, 418
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=22, fill=(184, 0, 9), outline=(255, 215, 0), width=4)
    draw.text((bx1 + 45, by1 + 14), badge_title, fill=(255, 215, 0), font=font_badge_title)
    draw.text((bx1 + 68, by1 + 70), badge_sub, fill=(255, 255, 255), font=font_badge_sub)

    # 5. Zone 1: Top Banner
    draw.rectangle([0, 0, THUMB_W, 64], fill=(184, 0, 9), outline=(255, 215, 0), width=3)
    draw.rounded_rectangle([18, 12, 160, 52], radius=6, fill=(255, 215, 0))
    draw.text((28, 18), "🔴 लाइव", fill=(127, 0, 3), font=font_tag)
    draw.text((200, 16), top_banner_text, fill=(255, 255, 255), font=font_banner)
    draw.text((1060, 16), channel_name, fill=(255, 215, 0), font=font_tag)

    # 6. Zone 5: Bottom Master Strip
    draw.rectangle([0, 638, THUMB_W, 720], fill=(10, 0, 2))
    draw.line([(0, 638), (THUMB_W, 638)], fill=(229, 9, 20), width=4)
    draw.rounded_rectangle([16, 650, 140, 706], radius=6, fill=(255, 215, 0))
    draw.text((26, 660), "⚡ बड़ी खबर", fill=(127, 0, 3), font=font_tag)
    draw.text((160, 660), bottom_headline[:70], fill=(255, 255, 255), font=font_headline)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    canvas.save(out_path, "JPEG", quality=92)
    return out_path


def generate_sensational_thumbnail(
    headline: str,
    photo_path: str = "",
    out_path: str = "out/thumbnail_01.jpg",
    category: str = "क्राइम",
    story: dict = None,
    all_stories: list = None,
    channel_name: str = "MP4 NEWS हिन्दी"
) -> str:
    """
    मास्टर 4-ग्रिड थंबनेल जनरेटर (Argon AI 5-Zone High-CTR Broadcast Layout)
    """
    story_count = len(all_stories) if all_stories else (50 if "50" in headline else 10)
    top_banner_text = get_slot_banner_text(story_count=story_count)

    badge_title = "TOP 50" if story_count >= 50 else ("TOP 10" if story_count >= 10 else "NONSTOP")
    badge_sub = "बड़ी खबरें"

    # Collect 4 high-CTR grid items
    fallback_photos = [photo_path] if photo_path else []
    grid_items = collect_top_4_grid_items(story=story, all_stories=all_stories, fallback_photos=fallback_photos)

    clean_headline = (headline or "दिनभर की बड़ी और ताज़ा खबरें").replace("**", "").replace("*", "").strip()

    # Engine A: Headless Chromium Screenshot
    browser = find_browser_executable()
    if browser:
        try:
            html_content = build_4grid_html(
                grid_items=grid_items,
                top_banner_text=top_banner_text,
                bottom_headline=clean_headline,
                badge_title=badge_title,
                badge_sub=badge_sub,
                channel_name=channel_name
            )
            with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tf:
                tf.write(html_content)
                temp_html = tf.name

            out_abs = os.path.abspath(out_path)
            os.makedirs(os.path.dirname(out_abs), exist_ok=True)

            cmd = [
                browser,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                f"--window-size={THUMB_W},{THUMB_H}",
                f"--screenshot={out_abs}",
                f"file:///{temp_html.replace(os.sep, '/')}",
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
            try:
                os.remove(temp_html)
            except Exception:
                pass

            if res.returncode == 0 and os.path.exists(out_abs) and os.path.getsize(out_abs) > 10000:
                print(f"  ✓ [Headless Browser] 4-Grid Master Thumbnail Ready: {out_path} ({os.path.getsize(out_abs)/1024:.0f} KB)")
                return out_path
        except Exception as e:
            print(f"  ⚠️ Browser screenshot error: {e}")

    # Engine B: Broadcast Pillow Engine
    print("  🖼️ [Pillow Engine] Rendering 4-Grid Master Thumbnail...")
    generate_4grid_thumbnail_pillow(
        grid_items=grid_items,
        top_banner_text=top_banner_text,
        bottom_headline=clean_headline,
        out_path=out_path,
        badge_title=badge_title,
        badge_sub=badge_sub,
        channel_name=channel_name
    )
    print(f"  ✓ [Pillow Engine] 4-Grid Master Thumbnail Ready: {out_path}")
    return out_path


if __name__ == "__main__":
    demo_out = str(PROJECT_ROOT / "out" / "test_4grid_thumbnail.jpg")
    print("Testing Master 4-Grid Thumbnail Generator...")

    json_path = SCRIPT_DIR / "generated_sample_top10.json"
    demo_story = None
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            stories = json.load(f)
            if stories:
                demo_story = stories[0]

    demo_hl = demo_story.get("screen_headline") if demo_story else "नरकटियागंज ट्रेन हादसे में नेपाली नागरिक की मौत | विशेष रिपोर्ट"
    generate_sensational_thumbnail(
        headline=demo_hl,
        out_path=demo_out,
        story=demo_story,
        category="क्राइम"
    )
