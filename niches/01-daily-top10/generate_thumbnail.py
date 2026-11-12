#!/usr/bin/env python3
"""
🔥 Master Million-View Hard News / Crime YouTube Thumbnail Generator (1280x720)
--------------------------------------------------------------------------------
100% matches Indian YouTube viral formula (DLS News / Fatafat News, 1M+ views/video),
tailored specifically for Hard News, Crime, Mafia, Police Encounters, and Political Breaking News:
  1. Top-Left: Radiant Sunburst Blue Box [MP4 NEWS हिन्दी LIVE] with 3D Gold Frame
  2. Top-Center: Huge Red Date (e.g. 12) + Month (नवंबर) in Khand-Bold + PM Modi + [5 बड़े फैसले] Pill
  3. Top-Right: Weekday (e.g. गुरुवार) + Year [2026] + [मुख्य समाचार] 3D Blue
  4. Middle Yellow Bar: 🚨 आज की 10 सबसे बड़ी खबरें | पुलिस-प्रशासन अलर्ट! | स्पेशल बुलेटिन
  5. Middle White Bar: Multi-Color Hard-News / Crime Hooks (सट्टा सिंडिकेट, एनकाउंटर, सुप्रीम कोर्ट सख्त, खुलासे)
  6. Bottom Red Banner: [क्राइम / अलर्ट] Badge + Giant 3D Golden [10 / 50 बड़ी खबरें] in Khand-Bold
"""

import os
import sys
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

# High-Grade Devanagari Display Fonts
FONT_KHAND_BOLD = str(PROJECT_ROOT / "assets" / "Khand-Bold.ttf").replace("\\", "/")
FONT_TEKO_BOLD = str(PROJECT_ROOT / "assets" / "Teko-Bold.ttf").replace("\\", "/")
FONT_NOTO_BOLD = str(PROJECT_ROOT / "assets" / "NotoSansDevanagari-Bold.ttf").replace("\\", "/")
MODI_PORTRAIT_PATH = PROJECT_ROOT / "assets" / "modi_portrait.jpg"

HINDI_DAYS = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
HINDI_MONTHS = [
    "", "जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून",
    "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"
]


def extract_hard_news_utility_segments(all_stories: list = None, headline: str = "", story: dict = None) -> list:
    """
    Extracts high-impact, sensational Hard-News & Crime triggers for the white strip:
    Matches channel category (Crime, Mafia, Police, Supreme Court, Government Action, High-Stakes Scams).
    """
    text_corpus = (headline or "")
    if story:
        text_corpus += " " + (story.get("screen_headline") or story.get("original_title") or "")
        text_corpus += " " + (story.get("voiceover_script") or "")
    if all_stories:
        for s in all_stories[:6]:
            text_corpus += " " + (s.get("screen_headline") or s.get("original_title") or "")
            text_corpus += " " + (s.get("voiceover_script") or "")

    low = text_corpus.lower()
    segments = []

    # Segment 1: Main Case / Syndicate / Mafia (Red #d00000)
    if any(w in low for w in ["सट्टा", "महादेव", "सिंडिकेट"]):
        segments.append({"text": "महादेव सट्टा सिंडिकेट,", "color": "#d00000"})
    elif any(w in low for w in ["माफिया", "गैंगस्टर", "गुर्गे"]):
        segments.append({"text": "माफिया पर बड़ा एक्शन,", "color": "#d00000"})
    elif any(w in low for w in ["घोटाला", "करोड़", "रिश्वत"]):
        segments.append({"text": "करोड़ों का बड़ा घोटाला,", "color": "#d00000"})
    elif any(w in low for w in ["हत्या", "मर्डर", "कांड"]):
        segments.append({"text": "सनसनीखेज हत्याकांड,", "color": "#d00000"})
    else:
        segments.append({"text": "बड़ा आपराधिक मामला,", "color": "#d00000"})

    # Segment 2: Police / Investigation / Agency (Purple #7b0099)
    if any(w in low for w in ["एनकाउंटर", "मुठभेड़", "गोली"]):
        segments.append({"text": "पुलिस एनकाउंटर,", "color": "#7b0099"})
    elif any(w in low for w in ["ईडी", "ed", "छापेमारी", "रेड"]):
        segments.append({"text": "ED की ताबड़तोड़ रेड,", "color": "#7b0099"})
    elif any(w in low for w in ["सीबीआई", "cbi"]):
        segments.append({"text": "CBI जांच शुरू,", "color": "#7b0099"})
    elif any(w in low for w in ["गिरफ्तार", "हिरासत", "दबोचा"]):
        segments.append({"text": "मुख्य आरोपी गिरफ्तार,", "color": "#7b0099"})
    else:
        segments.append({"text": "पुलिस-प्रशासन अलर्ट,", "color": "#7b0099"})

    # Segment 3: Judiciary / Govt Orders (Green #008800)
    if any(w in low for w in ["सुप्रीम कोर्ट", "कोर्ट", "अदालत"]):
        segments.append({"text": "सुप्रीम कोर्ट सख्त,", "color": "#008800"})
    elif any(w in low for w in ["हाईकोर्ट"]):
        segments.append({"text": "हाईकोर्ट का कड़ा आदेश,", "color": "#008800"})
    elif any(w in low for w in ["गृह मंत्रालय", "अमित शाह"]):
        segments.append({"text": "गृह मंत्रालय सख्त,", "color": "#008800"})
    elif any(w in low for w in ["रिमांड", "जेल", "बेल"]):
        segments.append({"text": "आरोपी की रिमांड खत्म,", "color": "#008800"})
    else:
        segments.append({"text": "कड़े निर्देश जारी,", "color": "#008800"})

    # Segment 4: High-Stakes Consequence / Big Number (Black #000000)
    if "करोड़" in low:
        segments.append({"text": "खुलेंगे 6000 करोड़ के राज!", "color": "#000000"})
    elif any(w in low for w in ["खुलासा", "राज", "सबूत"]):
        segments.append({"text": "जांच में सबसे बड़ा खुलासा!", "color": "#000000"})
    else:
        segments.append({"text": "खुलेंगे बड़े राज!", "color": "#000000"})

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


def build_hard_news_html(
    day_num: str,
    month_str: str,
    weekday_str: str,
    year_str: str,
    white_strip_segments: list,
    bottom_number: str = "10",
    modi_badge_text: str = "5 बड़े फैसले",
    channel_brand: str = "MP4 NEWS"
) -> str:
    """
    Builds the pixel-perfect HTML/CSS layout matching the million-view DLS News screenshot,
    rendered with Khand-Bold and Teko-Bold for 100% authentic TV broadcast impact.
    """
    modi_img_uri = MODI_PORTRAIT_PATH.resolve().as_uri() if MODI_PORTRAIT_PATH.exists() else ""
    khand_uri = Path(FONT_KHAND_BOLD).resolve().as_uri()
    teko_uri = Path(FONT_TEKO_BOLD).resolve().as_uri()

    white_spans = []
    for s in white_strip_segments:
        txt = s.get("text", "").strip()
        col = s.get("color", "#000000")
        white_spans.append(f'<span style="color: {col}; font-weight: 900; margin-right: 12px;">{txt}</span>')
    white_strip_html = "".join(white_spans)

    html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<style>
  @font-face {{
    font-family: 'KhandLocal';
    src: url('{khand_uri}') format('truetype');
    font-weight: 700 900;
  }}
  @font-face {{
    font-family: 'TekoLocal';
    src: url('{teko_uri}') format('truetype');
    font-weight: 700 900;
  }}

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
    font-family: 'KhandLocal', 'TekoLocal', sans-serif;
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
    background: linear-gradient(180deg, #fffde6 0%, #fff7a8 55%, #ffe850 100%);
  }}

  /* A. Top-Left Blue Ray Box (MP4 NEWS हिन्दी LIVE) */
  .brand-box {{
    width: 360px;
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
    left: -120px;
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
    padding: 6px 20px 8px 20px;
    background: rgba(4, 18, 64, 0.75);
    box-shadow: 0 0 20px rgba(255, 230, 0, 0.4), inset 0 0 14px rgba(255, 230, 0, 0.3);
  }}

  .brand-text-1 {{
    font-size: 64px;
    font-weight: 900;
    line-height: 0.95;
    color: #fff200;
    -webkit-text-stroke: 2.5px #593500;
    text-shadow: 3px 3px 0 #000, 0 0 15px rgba(255, 242, 0, 0.6);
    letter-spacing: 1px;
    font-family: 'KhandLocal', sans-serif;
  }}

  .brand-text-2 {{
    font-size: 72px;
    font-weight: 900;
    line-height: 0.95;
    color: #ffffff;
    -webkit-text-stroke: 2.5px #b80009;
    text-shadow: 3px 3px 0 #000, 0 0 15px rgba(255, 255, 255, 0.6);
    letter-spacing: 1px;
    margin-bottom: 4px;
    font-family: 'KhandLocal', sans-serif;
  }}

  .brand-live-pill {{
    background: linear-gradient(180deg, #ff1a24 0%, #b80009 100%);
    color: #ffffff;
    font-size: 24px;
    font-weight: 900;
    padding: 2px 22px;
    border-radius: 6px;
    letter-spacing: 2px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.6);
    border: 2px solid #ffffff;
    font-family: 'KhandLocal', sans-serif;
  }}

  /* B. Top-Center Date & Month (Tight, Bold, No Gap!) */
  .date-container {{
    flex: 1;
    position: relative;
    display: flex;
    align-items: center;
    padding-left: 14px;
    padding-top: 4px;
  }}

  .huge-date-number {{
    font-size: 250px;
    font-weight: 900;
    line-height: 0.78;
    color: #e50000;
    -webkit-text-stroke: 8px #ffe600;
    text-shadow: 4px 4px 0 #700000, 8px 8px 14px rgba(0,0,0,0.35);
    margin-right: 18px;
    letter-spacing: -6px;
    font-family: 'KhandLocal', sans-serif;
  }}

  .month-and-modi {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding-top: 2px;
  }}

  .month-name {{
    font-size: 135px;
    font-weight: 900;
    line-height: 0.85;
    color: #e50000;
    -webkit-text-stroke: 4px #ffffff;
    text-shadow: 3px 3px 0 #700000, 6px 6px 12px rgba(0,0,0,0.3);
    letter-spacing: -1px;
    font-family: 'KhandLocal', sans-serif;
  }}

  .modi-bar {{
    display: flex;
    align-items: center;
    margin-top: 6px;
  }}

  .modi-portrait {{
    width: 86px;
    height: 86px;
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
    font-size: 36px;
    font-weight: 900;
    padding: 2px 16px;
    border-radius: 6px;
    border: 2px solid #ffffff;
    box-shadow: 0 3px 8px rgba(0,0,0,0.35);
    white-space: nowrap;
    font-family: 'KhandLocal', sans-serif;
  }}

  /* C. Top-Right Day, Year & Mukhya Samachar (Tight, 3D Punchy!) */
  .top-right-box {{
    width: 280px;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    padding-right: 16px;
    padding-top: 10px;
  }}

  .day-and-year-row {{
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 8px;
    margin-bottom: 2px;
  }}

  .day-name {{
    font-size: 58px;
    font-weight: 900;
    line-height: 0.95;
    color: #002266;
    letter-spacing: -0.5px;
    font-family: 'KhandLocal', sans-serif;
  }}

  .year-pill {{
    background: #ffe600;
    color: #000000;
    font-size: 36px;
    font-weight: 900;
    padding: 1px 12px;
    border-radius: 6px;
    border: 2.5px solid #000000;
    box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    font-family: 'KhandLocal', sans-serif;
  }}

  .mukhya-samachar {{
    font-size: 64px;
    font-weight: 900;
    line-height: 0.92;
    color: #0044cc;
    -webkit-text-stroke: 3px #ffffff;
    text-shadow: 3px 3px 0 #001f5b, 5px 5px 10px rgba(0,0,0,0.35);
    text-align: right;
    letter-spacing: 0.5px;
    font-family: 'KhandLocal', sans-serif;
    margin-top: 2px;
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
    padding: 0 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    z-index: 15;
  }}

  .yellow-bar-left {{
    display: flex;
    align-items: center;
    font-family: 'KhandLocal', sans-serif;
  }}

  .yellow-bar-text {{
    color: #000000;
    font-size: 54px;
    font-weight: 900;
    letter-spacing: 0.5px;
    line-height: 1;
  }}

  .highlight-action {{
    color: #d50000;
    font-weight: 900;
    margin-left: 8px;
    text-shadow: 1px 1px 0 #ffffff;
  }}

  .yellow-bar-right {{
    color: #0033aa;
    font-size: 52px;
    font-weight: 900;
    -webkit-text-stroke: 1.8px #ffffff;
    text-shadow: 2px 2px 0 #001f5b;
    font-family: 'KhandLocal', sans-serif;
  }}

  /* ═══════════════════════════════════════════════════════════
     3. MIDDLE STRIP 2: WHITE MULTI-COLOR HOOK (Y: 395 to 495px)
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
    justify-content: center;
    padding: 0 16px;
    font-size: 44px;
    font-weight: 900;
    letter-spacing: 0.2px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    z-index: 15;
    white-space: nowrap;
    overflow: hidden;
    font-family: 'KhandLocal', sans-serif;
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
    padding: 0 18px;
    box-shadow: inset 0 4px 12px rgba(255, 230, 0, 0.4);
    z-index: 15;
  }}

  /* Left Badge: क्राइम / अलर्ट (Hard News Category Badge!) */
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
    margin-right: 18px;
    font-family: 'KhandLocal', sans-serif;
  }}

  .crime-tag {{
    font-size: 72px;
    font-weight: 900;
    line-height: 0.9;
    color: #00ffff;
    -webkit-text-stroke: 2.5px #002266;
    text-shadow: 2px 2px 0 #000;
    letter-spacing: 0.5px;
  }}

  .alert-tag {{
    font-size: 68px;
    font-weight: 900;
    line-height: 0.9;
    color: #fff200;
    -webkit-text-stroke: 2.5px #593500;
    text-shadow: 2px 2px 0 #000;
    margin-top: 4px;
    letter-spacing: 0.5px;
  }}

  /* Giant 3D Golden Text: 10 / 50 बड़ी खबरें (Tight, Massive, Cohesive!) */
  .giant-headline-container {{
    flex: 1;
    display: flex;
    align-items: baseline;
    justify-content: center;
    font-family: 'KhandLocal', sans-serif;
  }}

  .giant-number {{
    font-size: 225px;
    font-weight: 900;
    line-height: 0.82;
    color: #fff200;
    -webkit-text-stroke: 8px #450000;
    text-shadow: 4px 4px 0 #280000, 8px 8px 0 #180000, 12px 12px 24px rgba(0,0,0,0.95);
    margin-right: 20px;
    letter-spacing: -6px;
  }}

  .giant-words {{
    font-size: 190px;
    font-weight: 900;
    line-height: 0.82;
    color: #fff200;
    -webkit-text-stroke: 7px #450000;
    text-shadow: 4px 4px 0 #280000, 8px 8px 0 #180000, 12px 12px 24px rgba(0,0,0,0.95);
    letter-spacing: 0px;
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
        <div class="brand-text-1">MP4 NEWS</div>
        <div class="brand-text-2">हिन्दी</div>
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
      <span class="yellow-bar-text">🚨 आज की {bottom_number} सबसे बड़ी खबरें <span class="highlight-action">| पुलिस-प्रशासन अलर्ट!</span></span>
    </div>
    <div class="yellow-bar-right">स्पेशल बुलेटिन</div>
  </div>

  <!-- 3. MIDDLE STRIP 2: WHITE MULTI-COLOR HOOK STRIP (PURE CRIME / HARD NEWS HOOKS) -->
  <div class="white-strip">
    {white_strip_html}
  </div>

  <!-- 4. BOTTOM STRIP: MASTER RED BANNER -->
  <div class="bottom-red-banner">
    <div class="bottom-left-box">
      <div class="crime-tag">क्राइम</div>
      <div class="alert-tag">अलर्ट</div>
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


def generate_hard_news_thumbnail_pillow(
    day_num: str,
    month_str: str,
    weekday_str: str,
    year_str: str,
    white_strip_segments: list,
    bottom_number: str,
    out_path: str
) -> str:
    """Pure Pillow Engine Fallback: Draws identical Hard News layout using local Khand font"""
    canvas = Image.new("RGB", (THUMB_W, THUMB_H), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # 1. Top Section Background (Y: 0-295)
    for y in range(295):
        ratio = y / 295.0
        r = int(255 - ratio * 0)
        g = int(253 - ratio * 21)
        b = int(230 - ratio * 150)
        draw.line([(0, y), (THUMB_W, y)], fill=(r, g, b))

    # Top-Left Blue Brand Box
    draw.rectangle([0, 0, 360, 295], fill=(16, 62, 168), outline=(255, 230, 0), width=5)
    draw.rounded_rectangle([25, 20, 335, 275], radius=16, fill=(4, 18, 64), outline=(255, 230, 0), width=4)

    # Fonts
    font_path = FONT_KHAND_BOLD if os.path.exists(FONT_KHAND_BOLD) else FONT_NOTO_BOLD
    f_brand1 = ImageFont.truetype(font_path, 58) if os.path.exists(font_path) else ImageFont.load_default()
    f_brand2 = ImageFont.truetype(font_path, 66) if os.path.exists(font_path) else ImageFont.load_default()
    f_live = ImageFont.truetype(font_path, 22) if os.path.exists(font_path) else ImageFont.load_default()
    f_huge_date = ImageFont.truetype(font_path, 210) if os.path.exists(font_path) else ImageFont.load_default()
    f_month = ImageFont.truetype(font_path, 110) if os.path.exists(font_path) else ImageFont.load_default()
    f_day = ImageFont.truetype(font_path, 52) if os.path.exists(font_path) else ImageFont.load_default()
    f_strip = ImageFont.truetype(font_path, 42) if os.path.exists(font_path) else ImageFont.load_default()
    f_bot_num = ImageFont.truetype(font_path, 180) if os.path.exists(font_path) else ImageFont.load_default()
    f_bot_word = ImageFont.truetype(font_path, 150) if os.path.exists(font_path) else ImageFont.load_default()

    draw.text((70, 35), "MP4 NEWS", fill=(255, 242, 0), font=f_brand1, stroke_width=2, stroke_fill=(89, 53, 0))
    draw.text((120, 105), "हिन्दी", fill=(255, 255, 255), font=f_brand2, stroke_width=2, stroke_fill=(184, 0, 9))
    draw.rounded_rectangle([115, 215, 245, 255], radius=6, fill=(229, 9, 20), outline=(255, 255, 255), width=2)
    draw.text((145, 220), "LIVE", fill=(255, 255, 255), font=f_live)

    # Huge Date & Month
    draw.text((385, 25), day_num, fill=(229, 0, 0), font=f_huge_date, stroke_width=7, stroke_fill=(255, 230, 0))
    draw.text((630, 40), month_str, fill=(229, 0, 0), font=f_month, stroke_width=4, stroke_fill=(255, 255, 255))

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
    draw.text((1010, 20), weekday_str, fill=(0, 34, 102), font=f_day)
    draw.rounded_rectangle((1160, 24, 1260, 68), radius=6, fill=(255, 230, 0), outline=(0, 0, 0), width=2)
    draw.text((1175, 28), year_str, fill=(0, 0, 0), font=f_day)
    draw.text((1020, 105), "मुख्य समाचार", fill=(0, 68, 204), font=f_day, stroke_width=2, stroke_fill=(255, 255, 255))

    # 2. Middle Yellow Bar (Y: 295-395)
    draw.rectangle([0, 295, THUMB_W, 395], fill=(255, 224, 0), outline=(213, 0, 0), width=4)
    draw.text((25, 312), f"🚨 आज की {bottom_number} सबसे बड़ी खबरें | पुलिस-प्रशासन अलर्ट!", fill=(0, 0, 0), font=f_strip)
    draw.text((1060, 312), "स्पेशल बुलेटिन", fill=(0, 51, 170), font=f_strip)

    # 3. Middle White Bar (Y: 395-495)
    draw.rectangle([0, 395, THUMB_W, 495], fill=(255, 255, 255), outline=(213, 0, 0), width=4)
    x_cursor = 25
    color_map = {
        "#d00000": (208, 0, 0),
        "#7b0099": (123, 0, 153),
        "#008800": (0, 136, 0),
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

    # Left box: क्राइम / अलर्ट
    draw.rounded_rectangle([20, 515, 240, 700], radius=14, fill=(6, 24, 69), outline=(255, 230, 0), width=4)
    draw.text((45, 530), "क्राइम", fill=(0, 255, 255), font=f_day, stroke_width=2, stroke_fill=(0, 34, 102))
    draw.text((40, 615), "अलर्ट", fill=(255, 242, 0), font=f_day, stroke_width=2, stroke_fill=(89, 53, 0))

    # Giant 3D Golden text: 10 / 50 बड़ी खबरें
    draw.text((280, 505), bottom_number, fill=(255, 242, 0), font=f_bot_num, stroke_width=7, stroke_fill=(74, 0, 0))
    draw.text((540, 525), "बड़ी खबरें", fill=(255, 242, 0), font=f_bot_word, stroke_width=6, stroke_fill=(74, 0, 0))

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
    Main Entrypoint: Generates the Master Hard-News / Crime Broadcast Thumbnail
    (100% matches user's channel category and viral million-view formula)
    """
    now = datetime.now()
    day_num = str(now.day)
    month_str = HINDI_MONTHS[now.month] if 1 <= now.month <= 12 else "नवंबर"
    weekday_str = HINDI_DAYS[now.weekday()]
    year_str = str(now.year)

    # Story count determines bottom number: 50 for 50-news bulletin, 10 for Top 10
    story_count = len(all_stories) if all_stories else (50 if "50" in headline else 10)
    bottom_number = "50" if story_count >= 50 else "10"

    # Extract dynamic citizen utility triggers for the white strip (Pure Hard News & Crime)
    white_segments = extract_hard_news_utility_segments(all_stories=all_stories, headline=headline, story=story)

    # Engine A: Headless Chromium / Edge Screenshot (Vector Sharpness & 3D Lighting)
    browser = find_browser_executable()
    if browser:
        try:
            html_content = build_hard_news_html(
                day_num=day_num,
                month_str=month_str,
                weekday_str=weekday_str,
                year_str=year_str,
                white_strip_segments=white_segments,
                bottom_number=bottom_number,
                modi_badge_text="5 बड़े फैसले",
                channel_brand="MP4 NEWS"
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
                print(f"  ✓ [Headless Browser] Hard News Master Thumbnail Ready: {out_path} ({os.path.getsize(out_abs)/1024:.0f} KB)")
                return out_path
        except Exception as e:
            print(f"  ⚠️ Browser screenshot error: {e}")

    # Engine B: Pure Pillow Fallback Engine
    print("  🖼️ [Pillow Engine] Rendering Hard News Master Thumbnail...")
    generate_hard_news_thumbnail_pillow(
        day_num=day_num,
        month_str=month_str,
        weekday_str=weekday_str,
        year_str=year_str,
        white_strip_segments=white_segments,
        bottom_number=bottom_number,
        out_path=out_path
    )
    print(f"  ✓ [Pillow Engine] Hard News Master Thumbnail Ready: {out_path}")
    return out_path


if __name__ == "__main__":
    demo_out = str(PROJECT_ROOT / "out" / "test_hard_news_master_thumbnail.jpg")
    print("Testing Master Hard News / Crime YouTube Thumbnail Generator...")
    res = generate_sensational_thumbnail(
        headline="महादेव सट्टा सिंडिकेट में बड़ा एक्शन",
        out_path=demo_out,
        all_stories=[
            {"screen_headline": "महादेव सट्टा सिंडिकेट: सौरभ चंद्राकर की रिमांड खत्म"},
            {"screen_headline": "पुलिस एनकाउंटर में कुख्यात अपराधी गिरफ्तार"}
        ]
    )
    print(f"Done! Result saved to: {res}")
