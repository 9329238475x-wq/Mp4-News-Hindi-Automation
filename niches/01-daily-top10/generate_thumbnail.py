#!/usr/bin/env python3
"""
🔥 Master Million-View Fatafat / DLS News YouTube Thumbnail Generator (1280x720)
--------------------------------------------------------------------------------
100% matches Indian YouTube viral formula (DLS News / Fatafat News, 1M+ views/video):
  1. Top-Left: Radiant Sunburst Blue Box [फटाफट न्यूज LIVE] with 3D Gold Frame
  2. Top-Center: Huge Red Date (e.g. 12) + Month (नवंबर) + PM Modi Portrait + [5 बड़े ऐलान] Pill
  3. Top-Right: Weekday (e.g. गुरुवार) + Year [2026] + [मुख्य समाचार] 3D Blue
  4. Middle Yellow Bar: आज PM मोदी सरकार ने लिए 5 बड़े फैसले | समाचार
  5. Middle White Bar: Multi-Color Dynamic Aam-Aadmi Utility Triggers (Bank, Ration, DA, Festivals)
  6. Bottom Red Banner: [मौसम / नौकरियां] Badge + Giant 3D Golden [50 / 10 बड़ी खबरें]
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
MODI_PORTRAIT_PATH = PROJECT_ROOT / "assets" / "modi_portrait.jpg"

HINDI_DAYS = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
HINDI_MONTHS = [
    "", "जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून",
    "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"
]

DEFAULT_UTILITY_SEGMENTS = [
    {"text": "बैंक लोन,", "color": "#d00000"},
    {"text": "फ्री राशन,", "color": "#800080"},
    {"text": "DA / NPS,", "color": "#008000"},
    {"text": "समेत 10 बड़े फैसले", "color": "#000000"}
]


def extract_smart_utility_segments(all_stories: list = None, headline: str = "") -> list:
    """
    Extracts high-CTR public utility & festive keywords for the white strip:
    Never crime/violence; strictly citizen pocket triggers (Bank, Ration, DA, Weather, Gold, Rail).
    """
    full_text = headline or ""
    if all_stories:
        for s in all_stories:
            full_text += " " + (s.get("screen_headline") or s.get("original_title") or "")
            full_text += " " + (s.get("voiceover_script") or "")

    low = full_text.lower()
    segments = []

    # Priority 1: Festivals & Panchang
    if any(w in low for w in ["दिवाली", "दीपावली"]):
        segments.append({"text": "दिवाली शुभ मुहूर्त,", "color": "#d00000"})
    elif any(w in low for w in ["धनतेरस"]):
        segments.append({"text": "धनतेरस शुभ मुहूर्त,", "color": "#d00000"})
    elif any(w in low for w in ["छठ", "छठ पूजा"]):
        segments.append({"text": "छठ पूजा अर्घ्य समय,", "color": "#d00000"})
    elif any(w in low for w in ["होली"]):
        segments.append({"text": "होली शुभ मुहूर्त,", "color": "#d00000"})
    elif any(w in low for w in ["त्योहार", "मुहूर्त"]):
        segments.append({"text": "शुभ मुहूर्त नियम,", "color": "#d00000"})
    else:
        segments.append({"text": "बैंक लोन नियम,", "color": "#d00000"})

    # Priority 2: Pocket / Welfare triggers
    if any(w in low for w in ["राशन", "अनाज", "कोटेदार"]):
        segments.append({"text": "फ्री राशन योजना,", "color": "#800080"})
    elif any(w in low for w in ["सोना", "चांदी", "गोल्ड"]):
        segments.append({"text": "सोने-चांदी का भाव,", "color": "#800080"})
    elif any(w in low for w in ["पेट्रोल", "डीजल", "गैस", "सिलेंडर"]):
        segments.append({"text": "गैस सिलेंडर दाम,", "color": "#800080"})
    else:
        segments.append({"text": "फ्री राशन,", "color": "#800080"})

    # Priority 3: Employees / Allowances / Rail
    if any(w in low for w in ["da", "डीए", "महंगाई", "वेतन"]):
        segments.append({"text": "DA में बढ़ोतरी,", "color": "#008000"})
    elif any(w in low for w in ["nps", "ops", "पेंशन"]):
        segments.append({"text": "NPS / पेंशन फैसला,", "color": "#008000"})
    elif any(w in low for w in ["ट्रेन", "रेलवे", "आईआरसीटीसी"]):
        segments.append({"text": "रेलवे का बड़ा ऐलान,", "color": "#008000"})
    elif any(w in low for w in ["स्कूल", "कॉलेज", "छुट्टी"]):
        segments.append({"text": "स्कूलों की छुट्टी,", "color": "#008000"})
    else:
        segments.append({"text": "DA / NPS,", "color": "#008000"})

    # Ending anchor
    segments.append({"text": "समेत 10 बड़े फैसले", "color": "#000000"})
    return segments


def find_browser_executable() -> str:
    """Find local Chrome, Chromium, or Edge binary for headless rendering"""
    candidates = [
        shutil.which("chrome"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        shutil.which("msedge"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return ""


def build_fatafat_html(
    day_num: str,
    month_str: str,
    weekday_str: str,
    year_str: str,
    white_strip_segments: list,
    bottom_number: str = "50",
    modi_badge_text: str = "5 बड़े ऐलान"
) -> str:
    """
    Builds the pixel-perfect HTML/CSS layout matching the million-view DLS News screenshot
    """
    modi_img_uri = MODI_PORTRAIT_PATH.resolve().as_uri() if MODI_PORTRAIT_PATH.exists() else ""

    white_spans = []
    for s in white_strip_segments:
        txt = s.get("text", "").strip()
        col = s.get("color", "#000000")
        white_spans.append(f'<span style="color: {col}; font-weight: 900; margin-right: 10px;">{txt}</span>')
    white_strip_html = "".join(white_spans)

    html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Khand:wght@700;800;900&family=Noto+Sans+Devanagari:wght@700;800;900&display=swap');

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    user-select: none;
  }}

  body {{
    width: {THUMB_W}px;
    height: {THUMB_H}px;
    overflow: hidden;
    position: relative;
    background: #000000;
    font-family: 'Khand', 'Noto Sans Devanagari', sans-serif;
  }}

  /* ═══════════════════════════════════════════════════════════
     1. TOP SECTION (Y: 0 to 295px)
     ═══════════════════════════════════════════════════════════ */
  .top-section {{
    position: absolute;
    top: 0;
    left: 0;
    width: 1280px;
    height: 295px;
    display: flex;
    background: linear-gradient(180deg, #fffde6 0%, #fff7a8 55%, #ffea60 100%);
  }}

  /* A. Top-Left Blue Ray Box (फटाफट न्यूज LIVE) */
  .brand-box {{
    width: 370px;
    height: 295px;
    position: relative;
    overflow: hidden;
    background: radial-gradient(circle at 50% 50%, #2968f0 0%, #103ea8 55%, #071f63 100%);
    border-right: 5px solid #ffe600;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 4px 0 15px rgba(0,0,0,0.5);
    z-index: 10;
  }}

  .brand-rays {{
    position: absolute;
    top: -150px;
    left: -110px;
    width: 600px;
    height: 600px;
    background: repeating-conic-gradient(
      from 0deg at 50% 50%,
      rgba(255, 255, 255, 0.16) 0deg 12deg,
      transparent 12deg 24deg
    );
    pointer-events: none;
  }}

  .brand-inner-frame {{
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 4px solid #ffe600;
    border-radius: 18px;
    padding: 8px 24px 10px 24px;
    background: rgba(4, 18, 64, 0.72);
    box-shadow: 0 0 20px rgba(255, 230, 0, 0.4), inset 0 0 14px rgba(255, 230, 0, 0.3);
  }}

  .brand-text-1 {{
    font-size: 76px;
    font-weight: 900;
    line-height: 0.95;
    color: #fff200;
    -webkit-text-stroke: 3px #593500;
    text-shadow: 3px 3px 0 #000, 0 0 15px rgba(255, 242, 0, 0.6);
    letter-spacing: 1px;
  }}

  .brand-text-2 {{
    font-size: 86px;
    font-weight: 900;
    line-height: 0.95;
    color: #fff200;
    -webkit-text-stroke: 3px #593500;
    text-shadow: 3px 3px 0 #000, 0 0 15px rgba(255, 242, 0, 0.6);
    letter-spacing: 1px;
    margin-bottom: 6px;
  }}

  .brand-live-pill {{
    background: linear-gradient(180deg, #ff1a24 0%, #b80009 100%);
    color: #ffffff;
    font-size: 26px;
    font-weight: 900;
    padding: 2px 24px;
    border-radius: 6px;
    letter-spacing: 2px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.6);
    border: 2px solid #ffffff;
  }}

  /* B. Top-Center Date & Month */
  .date-container {{
    flex: 1;
    position: relative;
    display: flex;
    align-items: flex-start;
    padding-left: 18px;
    padding-top: 6px;
  }}

  .huge-date-number {{
    font-size: 228px;
    font-weight: 900;
    line-height: 0.82;
    color: #e50000;
    -webkit-text-stroke: 7.5px #ffe600;
    text-shadow: 4px 4px 0 #8b0000, 8px 8px 14px rgba(0,0,0,0.35);
    margin-right: 10px;
    letter-spacing: -2px;
  }}

  .month-and-modi {{
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    padding-top: 6px;
  }}

  .month-name {{
    font-size: 114px;
    font-weight: 900;
    line-height: 0.9;
    color: #e50000;
    -webkit-text-stroke: 3.5px #ffffff;
    text-shadow: 3px 3px 0 #8b0000, 6px 6px 12px rgba(0,0,0,0.3);
    letter-spacing: 1px;
  }}

  .modi-bar {{
    display: flex;
    align-items: center;
    margin-top: 10px;
  }}

  .modi-portrait {{
    width: 90px;
    height: 90px;
    border-radius: 50%;
    object-fit: cover;
    object-position: center 20%;
    border: 3.5px solid #ffe600;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    background: #ffffff;
    margin-right: 12px;
  }}

  .modi-pill {{
    background: linear-gradient(180deg, #00f0ff 0%, #00b4d8 100%);
    color: #000000;
    font-size: 34px;
    font-weight: 900;
    padding: 3px 16px;
    border-radius: 6px;
    border: 2px solid #ffffff;
    box-shadow: 0 3px 8px rgba(0,0,0,0.35);
    white-space: nowrap;
  }}

  /* C. Top-Right Day, Year & Mukhya Samachar */
  .top-right-box {{
    width: 270px;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    padding-right: 18px;
    padding-top: 10px;
  }}

  .day-and-year-row {{
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 8px;
    margin-bottom: 6px;
  }}

  .day-name {{
    font-size: 50px;
    font-weight: 900;
    line-height: 1;
    color: #002266;
    letter-spacing: 0.5px;
  }}

  .year-pill {{
    background: #ffe600;
    color: #000000;
    font-size: 34px;
    font-weight: 900;
    padding: 1px 12px;
    border-radius: 6px;
    border: 2px solid #000000;
    box-shadow: 0 2px 6px rgba(0,0,0,0.25);
  }}

  .mukhya-samachar {{
    font-size: 56px;
    font-weight: 900;
    line-height: 0.95;
    color: #0044cc;
    -webkit-text-stroke: 2.5px #ffffff;
    text-shadow: 2px 2px 0 #001f5b, 4px 4px 8px rgba(0,0,0,0.3);
    text-align: right;
    letter-spacing: 0.5px;
  }}

  /* ═══════════════════════════════════════════════════════════
     2. MIDDLE STRIP 1: YELLOW BAR (Y: 295 to 395px, Height: 100px)
     ═══════════════════════════════════════════════════════════ */
  .yellow-bar {{
    position: absolute;
    top: 295px;
    left: 0;
    width: 1280px;
    height: 100px;
    background: linear-gradient(180deg, #fff000 0%, #ffd000 100%);
    border-top: 4px solid #d50000;
    border-bottom: 4px solid #d50000;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    z-index: 15;
  }}

  .yellow-bar-left {{
    display: flex;
    align-items: center;
  }}

  .badge-aaj {{
    color: #d50000;
    font-size: 56px;
    font-weight: 900;
    margin-right: 10px;
    text-shadow: 1px 1px 0 #ffffff;
  }}

  .yellow-bar-text {{
    color: #000000;
    font-size: 50px;
    font-weight: 900;
    letter-spacing: 0.5px;
  }}

  .highlight-5decisions {{
    color: #d50000;
    font-weight: 900;
  }}

  .yellow-bar-right {{
    color: #0033aa;
    font-size: 50px;
    font-weight: 900;
    -webkit-text-stroke: 1.5px #ffffff;
    text-shadow: 2px 2px 0 #001f5b;
  }}

  /* ═══════════════════════════════════════════════════════════
     3. MIDDLE STRIP 2: WHITE MULTI-COLOR HOOK (Y: 395 to 495px, Height: 100px)
     ═══════════════════════════════════════════════════════════ */
  .white-strip {{
    position: absolute;
    top: 395px;
    left: 0;
    width: 1280px;
    height: 100px;
    background: #ffffff;
    border-bottom: 4px solid #d50000;
    display: flex;
    align-items: center;
    padding: 0 16px;
    font-size: 42px;
    font-weight: 900;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    z-index: 15;
    white-space: nowrap;
    overflow: hidden;
  }}

  /* ═══════════════════════════════════════════════════════════
     4. BOTTOM STRIP: MASTER RED BANNER (Y: 495 to 720px, Height: 225px)
     ═══════════════════════════════════════════════════════════ */
  .bottom-red-banner {{
    position: absolute;
    top: 495px;
    left: 0;
    width: 1280px;
    height: 225px;
    background: linear-gradient(180deg, #e60000 0%, #aa0000 45%, #660000 100%);
    border-top: 4px solid #ffe600;
    display: flex;
    align-items: center;
    padding: 0 20px;
    box-shadow: inset 0 4px 12px rgba(255, 230, 0, 0.4);
    z-index: 15;
  }}

  /* Left Badge: मौसम / नौकरियां */
  .bottom-left-box {{
    width: 220px;
    height: 185px;
    background: linear-gradient(180deg, #103282 0%, #061845 100%);
    border: 3.5px solid #ffe600;
    border-radius: 14px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 16px rgba(0,0,0,0.6);
    flex-shrink: 0;
    margin-right: 24px;
  }}

  .weather-text {{
    font-size: 64px;
    font-weight: 900;
    line-height: 1;
    color: #00ffff;
    -webkit-text-stroke: 2px #002266;
    text-shadow: 2px 2px 0 #000;
  }}

  .jobs-text {{
    font-size: 58px;
    font-weight: 900;
    line-height: 1;
    color: #fff200;
    -webkit-text-stroke: 2px #593500;
    text-shadow: 2px 2px 0 #000;
    margin-top: 4px;
  }}

  /* Giant 3D Golden Text: 50 बड़ी खबरें */
  .giant-headline-container {{
    flex: 1;
    display: flex;
    align-items: baseline;
    justify-content: center;
  }}

  .giant-number {{
    font-size: 200px;
    font-weight: 900;
    line-height: 0.88;
    color: #fff200;
    -webkit-text-stroke: 7px #4a0000;
    text-shadow: 4px 4px 0 #300000, 8px 8px 0 #200000, 12px 12px 24px rgba(0,0,0,0.9);
    margin-right: 18px;
    letter-spacing: -2px;
  }}

  .giant-words {{
    font-size: 168px;
    font-weight: 900;
    line-height: 0.88;
    color: #fff200;
    -webkit-text-stroke: 6px #4a0000;
    text-shadow: 4px 4px 0 #300000, 8px 8px 0 #200000, 12px 12px 24px rgba(0,0,0,0.9);
    letter-spacing: 1px;
    white-space: nowrap;
  }}
</style>
</head>
<body>
  <!-- 1. TOP SECTION -->
  <div class="top-section">
    <!-- Brand Box -->
    <div class="brand-box">
      <div class="brand-rays"></div>
      <div class="brand-inner-frame">
        <div class="brand-text-1">फटाफट</div>
        <div class="brand-text-2">न्यूज</div>
        <div class="brand-live-pill">LIVE</div>
      </div>
    </div>

    <!-- Date, Month, Modi -->
    <div class="date-container">
      <div class="huge-date-number">{day_num}</div>
      <div class="month-and-modi">
        <div class="month-name">{month_str}</div>
        <div class="modi-bar">
          <img class="modi-portrait" src="{modi_img_uri}" alt="PM Modi">
          <div class="modi-pill">{modi_badge_text}</div>
        </div>
      </div>
    </div>

    <!-- Top Right (Day, Year, Mukhya Samachar) -->
    <div class="top-right-box">
      <div class="day-and-year-row">
        <div class="day-name">{weekday_str}</div>
        <div class="year-pill">{year_str}</div>
      </div>
      <div class="mukhya-samachar">मुख्य समाचार</div>
    </div>
  </div>

  <!-- 2. MIDDLE STRIP 1: YELLOW BAR -->
  <div class="yellow-bar">
    <div class="yellow-bar-left">
      <span class="badge-aaj">आज</span>
      <span class="yellow-bar-text">PM मोदी सरकार ने लिए <span class="highlight-5decisions">5 बड़े फैसले</span></span>
    </div>
    <div class="yellow-bar-right">समाचार</div>
  </div>

  <!-- 3. MIDDLE STRIP 2: WHITE MULTI-COLOR HOOK STRIP -->
  <div class="white-strip">
    {white_strip_html}
  </div>

  <!-- 4. BOTTOM STRIP: MASTER RED BANNER -->
  <div class="bottom-red-banner">
    <div class="bottom-left-box">
      <div class="weather-text">मौसम</div>
      <div class="jobs-text">नौकरियां</div>
    </div>
    <div class="giant-headline-container">
      <span class="giant-number">{bottom_number}</span>
      <span class="giant-words">बड़ी खबरें</span>
    </div>
  </div>
</body>
</html>
"""
    return html


def generate_fatafat_thumbnail_pillow(
    day_num: str,
    month_str: str,
    weekday_str: str,
    year_str: str,
    white_strip_segments: list,
    bottom_number: str,
    out_path: str
) -> str:
    """Pure Pillow Engine Fallback: Draws identical Fatafat News layout"""
    canvas = Image.new("RGB", (THUMB_W, THUMB_H), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # 1. Top Section Background (Y: 0-295)
    for y in range(295):
        ratio = y / 295.0
        r = int(255 - ratio * 0)
        g = int(253 - ratio * 19)
        b = int(230 - ratio * 134)
        draw.line([(0, y), (THUMB_W, y)], fill=(r, g, b))

    # Top-Left Blue Brand Box
    draw.rectangle([0, 0, 370, 295], fill=(16, 62, 168), outline=(255, 230, 0), width=5)
    draw.rounded_rectangle([30, 25, 340, 270], radius=16, fill=(4, 18, 64), outline=(255, 230, 0), width=4)

    # Fonts
    f_brand = ImageFont.truetype(FONT_BOLD_PATH, 70) if os.path.exists(FONT_BOLD_PATH) else ImageFont.load_default()
    f_live = ImageFont.truetype(FONT_BOLD_PATH, 24) if os.path.exists(FONT_BOLD_PATH) else ImageFont.load_default()
    f_huge_date = ImageFont.truetype(FONT_BOLD_PATH, 190) if os.path.exists(FONT_BOLD_PATH) else ImageFont.load_default()
    f_month = ImageFont.truetype(FONT_BOLD_PATH, 90) if os.path.exists(FONT_BOLD_PATH) else ImageFont.load_default()
    f_day = ImageFont.truetype(FONT_BOLD_PATH, 46) if os.path.exists(FONT_BOLD_PATH) else ImageFont.load_default()
    f_strip = ImageFont.truetype(FONT_BOLD_PATH, 44) if os.path.exists(FONT_BOLD_PATH) else ImageFont.load_default()
    f_bot_num = ImageFont.truetype(FONT_BOLD_PATH, 160) if os.path.exists(FONT_BOLD_PATH) else ImageFont.load_default()
    f_bot_word = ImageFont.truetype(FONT_BOLD_PATH, 130) if os.path.exists(FONT_BOLD_PATH) else ImageFont.load_default()

    draw.text((85, 45), "फटाफट", fill=(255, 242, 0), font=f_brand, stroke_width=3, stroke_fill=(89, 53, 0))
    draw.text((105, 125), "न्यूज", fill=(255, 242, 0), font=f_brand, stroke_width=3, stroke_fill=(89, 53, 0))
    draw.rounded_rectangle([120, 215, 250, 255], radius=6, fill=(229, 9, 20), outline=(255, 255, 255), width=2)
    draw.text((150, 222), "LIVE", fill=(255, 255, 255), font=f_live)

    # Huge Date & Month
    draw.text((395, 30), day_num, fill=(229, 0, 0), font=f_huge_date, stroke_width=7, stroke_fill=(255, 230, 0))
    draw.text((630, 45), month_str, fill=(229, 0, 0), font=f_month, stroke_width=4, stroke_fill=(255, 255, 255))

    # Modi image thumbnail in circle
    if MODI_PORTRAIT_PATH.exists():
        try:
            with Image.open(MODI_PORTRAIT_PATH) as m_img:
                m_resized = m_img.resize((84, 84))
                canvas.paste(m_resized, (630, 165))
                draw.rectangle([628, 163, 716, 251], outline=(255, 230, 0), width=3)
        except Exception:
            pass

    # Top-Right Day & Year
    draw.text((1020, 25), weekday_str, fill=(0, 34, 102), font=f_day)
    draw.rounded_rectangle((1160, 28, 1260, 72), radius=6, fill=(255, 230, 0), outline=(0, 0, 0), width=2)
    draw.text((1175, 32), year_str, fill=(0, 0, 0), font=f_day)
    draw.text((1030, 110), "मुख्य समाचार", fill=(0, 68, 204), font=f_day, stroke_width=2, stroke_fill=(255, 255, 255))

    # 2. Middle Yellow Bar (Y: 295-395)
    draw.rectangle([0, 295, THUMB_W, 395], fill=(255, 224, 0), outline=(213, 0, 0), width=4)
    draw.text((25, 312), "आज", fill=(213, 0, 0), font=f_strip, stroke_width=1, stroke_fill=(255, 255, 255))
    draw.text((115, 312), "PM मोदी सरकार ने लिए 5 बड़े फैसले", fill=(0, 0, 0), font=f_strip)
    draw.text((1120, 312), "समाचार", fill=(0, 51, 170), font=f_strip)

    # 3. Middle White Bar (Y: 395-495)
    draw.rectangle([0, 395, THUMB_W, 495], fill=(255, 255, 255), outline=(213, 0, 0), width=4)
    x_cursor = 30
    color_map = {
        "#d00000": (208, 0, 0),
        "#800080": (128, 0, 128),
        "#008000": (0, 128, 0),
        "#000000": (0, 0, 0),
    }
    for seg in white_strip_segments:
        txt = seg.get("text", "") + " "
        c_hex = seg.get("color", "#000000")
        c_rgb = color_map.get(c_hex, (0, 0, 0))
        draw.text((x_cursor, 415), txt, fill=c_rgb, font=f_strip)
        bbox = draw.textbbox((x_cursor, 415), txt, font=f_strip)
        x_cursor = bbox[2] + 10

    # 4. Bottom Red Banner (Y: 495-720)
    for y in range(495, 720):
        ratio = (y - 495) / 225.0
        r = int(230 - ratio * 128)
        g = 0
        b = 0
        draw.line([(0, y), (THUMB_W, y)], fill=(r, g, b))
    draw.line([(0, 495), (THUMB_W, 495)], fill=(255, 230, 0), width=4)

    # Left box: मौसम / नौकरियां
    draw.rounded_rectangle([20, 515, 240, 700], radius=14, fill=(6, 24, 69), outline=(255, 230, 0), width=4)
    draw.text((45, 530), "मौसम", fill=(0, 255, 255), font=f_day, stroke_width=2, stroke_fill=(0, 34, 102))
    draw.text((40, 615), "नौकरियां", fill=(255, 242, 0), font=f_day, stroke_width=2, stroke_fill=(89, 53, 0))

    # Giant 3D Golden text: 50 बड़ी खबरें
    draw.text((290, 505), bottom_number, fill=(255, 242, 0), font=f_bot_num, stroke_width=7, stroke_fill=(74, 0, 0))
    draw.text((560, 530), "बड़ी खबरें", fill=(255, 242, 0), font=f_bot_word, stroke_width=6, stroke_fill=(74, 0, 0))

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    canvas.save(out_path, "JPEG", quality=95)
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
    Main Entrypoint: Generates the Master Million-View Fatafat / DLS News Thumbnail
    (100% matches user's uploaded million-view screenshot)
    """
    now = datetime.now()
    day_num = str(now.day)
    month_str = HINDI_MONTHS[now.month] if 1 <= now.month <= 12 else "नवंबर"
    weekday_str = HINDI_DAYS[now.weekday()]
    year_str = str(now.year)

    # Story count determines bottom number: 50 for 50-news bulletin, 10 for Top 10
    story_count = len(all_stories) if all_stories else (50 if "50" in headline else 10)
    bottom_number = "50" if story_count >= 50 else "10"

    # Extract dynamic citizen utility triggers for the white strip
    white_segments = extract_smart_utility_segments(all_stories=all_stories, headline=headline)

    # Engine A: Headless Chromium / Edge Screenshot (Vector Sharpness & 3D Lighting)
    browser = find_browser_executable()
    if browser:
        try:
            html_content = build_fatafat_html(
                day_num=day_num,
                month_str=month_str,
                weekday_str=weekday_str,
                year_str=year_str,
                white_strip_segments=white_segments,
                bottom_number=bottom_number,
                modi_badge_text="5 बड़े ऐलान"
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
                print(f"  ✓ [Headless Browser] Fatafat Master Thumbnail Ready: {out_path} ({os.path.getsize(out_abs)/1024:.0f} KB)")
                return out_path
        except Exception as e:
            print(f"  ⚠️ Browser screenshot error: {e}")

    # Engine B: Pure Pillow Fallback Engine
    print("  🖼️ [Pillow Engine] Rendering Fatafat Master Thumbnail...")
    generate_fatafat_thumbnail_pillow(
        day_num=day_num,
        month_str=month_str,
        weekday_str=weekday_str,
        year_str=year_str,
        white_strip_segments=white_segments,
        bottom_number=bottom_number,
        out_path=out_path
    )
    print(f"  ✓ [Pillow Engine] Fatafat Master Thumbnail Ready: {out_path}")
    return out_path


if __name__ == "__main__":
    demo_out = str(PROJECT_ROOT / "out" / "test_fatafat_master_thumbnail.jpg")
    print("Testing Million-View Fatafat / DLS News Master Thumbnail Generator...")
    res = generate_sensational_thumbnail(
        headline="आज के मुख्य समाचार बड़ी खबरें PM Modi",
        out_path=demo_out,
        all_stories=[{"screen_headline": "बैंक लोन पर बड़ा फैसला"}, {"screen_headline": "राशन वितरण में नया नियम"}]
    )
    print(f"Done! Result saved to: {res}")
