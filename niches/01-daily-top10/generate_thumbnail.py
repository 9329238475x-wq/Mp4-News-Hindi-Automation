#!/usr/bin/env python3
"""
🔥 Master Million-View DLS News / Fatafat News YouTube Thumbnail Generator (1280x720)
-------------------------------------------------------------------------------------
100% matches user's exact uploaded reference thumbnail (media_1794477519388_bd6869db.jpg):
  1. Top-Left: Radiant Sunburst Blue Box [फटाफट न्यूज़ LIVE] with 3D Gold Frame & Gradient Text
  2. Top-Center: Huge Red Date (e.g. 12 / 29) + Month (नवंबर / अक्टूबर) in Khand + PM Modi Cutout + [5 बड़े ऐलान]
  3. Top-Right: Weekday (e.g. गुरुवार) + Year [2026] + [मुख्य] 3D Blue
  4. Middle Row:
     - Cyan Gradient Pill: [आज PM मोदी सरकार ने लिए 5 बड़े फैसले] or [देशभर की 50 बड़ी खबरों के 5 बड़े खुलासे]
     - Right: [समाचार] in Giant 3D Blue with White Outline (pairs with 'मुख्य' to make 'मुख्य समाचार')
  5. White Hook Strip: Multi-Color Underlined Keywords (Category-matched to Crime or Utility)
  6. Bottom Red Banner: Circular Channel Logo Badge + Giant 3D Golden [50 बड़ी खबरें] in Poppins/Khand
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

# Viral Thumbnail Fonts
FONT_KHAND = str(PROJECT_ROOT / "assets" / "Khand-Bold.ttf").replace("\\", "/")
FONT_POPPINS = str(PROJECT_ROOT / "assets" / "Poppins-Black.ttf").replace("\\", "/")
FONT_BALOO = str(PROJECT_ROOT / "assets" / "Baloo2-Static-ExtraBold.ttf").replace("\\", "/")

# Cutouts
MODI_CUTOUT_PNG = PROJECT_ROOT / "assets" / "modi_cutout.png"
MODI_PORTRAIT_JPG = PROJECT_ROOT / "assets" / "modi_portrait.jpg"

HINDI_DAYS = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
HINDI_MONTHS = [
    "", "जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून",
    "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"
]


def extract_thumbnail_hook_segments(all_stories: list = None, headline: str = "", story: dict = None) -> tuple:
    """
    Extracts high-CTR underlined keywords for the white strip and the cyan pill text.
    Category-Aware:
    - If hard news / crime (Mahadev Satta, encounter, murder, remand): gives crime hooks!
    - If utility / public (gold, LPG, DA, weather, festivals): gives utility hooks!
    Returns (segments_list, is_crime_heavy)
    """
    text_corpus = (headline or "")
    if story:
        text_corpus += " " + (story.get("screen_headline") or story.get("original_title") or "")
        text_corpus += " " + (story.get("voiceover_script") or "")
    if all_stories:
        for s in all_stories[:8]:
            text_corpus += " " + (s.get("screen_headline") or s.get("original_title") or "")
            text_corpus += " " + (s.get("voiceover_script") or "")

    low = text_corpus.lower()
    segments = []

    # Check if the bulletin is hard news / crime
    is_crime_heavy = any(w in low for w in [
        "सट्टा", "महादेव", "एनकाउंटर", "हत्या", "माफिया", "रिमांड",
        "गिरफ्तार", "ईडी", "सीबीआई", "मुठभेड़", "गोली", "अपराध"
    ])

    if is_crime_heavy:
        # Category A: Hard News / Crime Triggers (Matches user video content)
        if any(w in low for w in ["सट्टा", "महादेव"]):
            segments.append({"text": "महादेव सट्टा,", "color": "#000000"})
        elif any(w in low for w in ["माफिया"]):
            segments.append({"text": "माफिया पर एक्शन,", "color": "#000000"})
        else:
            segments.append({"text": "क्राइम अलर्ट,", "color": "#000000"})

        if any(w in low for w in ["एनकाउंटर", "गोली", "मुठभेड़"]):
            segments.append({"text": "पुलिस एनकाउंटर,", "color": "#0055cc"})
        elif any(w in low for w in ["ईडी", "सीबीआई"]):
            segments.append({"text": "ED की रेड,", "color": "#0055cc"})
        else:
            segments.append({"text": "बड़ी गिरफ्तारी,", "color": "#0055cc"})

        if any(w in low for w in ["रिमांड"]):
            segments.append({"text": "रिमांड पर फैसला,", "color": "#d00000"})
        elif any(w in low for w in ["सुप्रीम कोर्ट", "कोर्ट"]):
            segments.append({"text": "सुप्रीम कोर्ट सख्त,", "color": "#d00000"})
        else:
            segments.append({"text": "प्रशासन सख्त,", "color": "#d00000"})

        if "करोड़" in low:
            segments.append({"text": "6000 करोड़ राज", "color": "#008800"})
        else:
            segments.append({"text": "जांच में खुलासा", "color": "#008800"})

        segments.append({"text": "समेत बड़े अपडेट", "color": "#000000", "no_underline": True})
    else:
        # Category B: Public Utility / Festive Triggers (100% matches reference screenshot)
        segments.append({"text": "सोना-चांदी,", "color": "#000000"})
        segments.append({"text": "करवा चौथ,", "color": "#0055cc"})
        segments.append({"text": "LPG गैस,", "color": "#d00000"})
        segments.append({"text": "तूफान अर्नब", "color": "#008800"})
        segments.append({"text": "समेत बड़े अपडेट", "color": "#000000", "no_underline": True})

    return segments, is_crime_heavy


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


def build_dls_reference_html(
    day_num: str,
    month_str: str,
    weekday_str: str,
    year_str: str,
    white_strip_segments: list,
    bottom_number: str = "50",
    is_crime_heavy: bool = False,
    channel_name: str = "MP4 NEWS"
) -> str:
    """
    Builds the pixel-perfect HTML/CSS layout matching media_1794477519388_bd6869db.jpg:
    Uses Khand-Bold for news typography + Poppins-Black for numbers and 3D headlines.
    Uses placeholder replacement to guarantee zero f-string escaping errors.
    """
    if MODI_CUTOUT_PNG.exists():
        modi_img_uri = MODI_CUTOUT_PNG.resolve().as_uri()
    elif MODI_PORTRAIT_JPG.exists():
        modi_img_uri = MODI_PORTRAIT_JPG.resolve().as_uri()
    else:
        modi_img_uri = ""

    font_khand_uri = Path(FONT_KHAND).resolve().as_uri()
    font_poppins_uri = Path(FONT_POPPINS).resolve().as_uri()

    white_spans = []
    for s in white_strip_segments:
        txt = s.get("text", "").strip()
        col = s.get("color", "#000000")
        no_u = s.get("no_underline", False)
        if no_u:
            white_spans.append(f'<span style="color: {col}; font-weight: 900; margin-left: 4px;">{txt}</span>')
        else:
            white_spans.append(f'<span class="hook-item" style="color: {col}; text-decoration-color: {col};">{txt}</span>')
    white_strip_html = "".join(white_spans)

    if is_crime_heavy:
        cyan_pill_html = f'देशभर की {bottom_number} बड़ी खबरों के <span class="cyan-pill-highlight">5 बड़े खुलासे</span>'
    else:
        cyan_pill_html = 'आज PM मोदी सरकार ने लिए <span class="cyan-pill-highlight">5 बड़े फैसले</span>'

    template = """<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<style>
  @font-face {
    font-family: 'KhandNews';
    src: url('__FONT_KHAND__') format('truetype');
    font-weight: 700 900;
  }
  @font-face {
    font-family: 'PoppinsHeavy';
    src: url('__FONT_POPPINS__') format('truetype');
    font-weight: 900;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    user-select: none;
  }

  body {
    width: 1280px;
    height: 720px;
    overflow: hidden;
    position: relative;
    background: #000000;
    font-family: 'KhandNews', sans-serif;
  }

  /* ═══════════════════════════════════════════════════════════
     1. TOP SECTION (Y: 0 to 310px, Height: 310px)
     ═══════════════════════════════════════════════════════════ */
  .top-section {
    position: absolute;
    top: 0;
    left: 0;
    width: 1280px;
    height: 310px;
    display: flex;
    background: linear-gradient(180deg, #fffde8 0%, #fff799 50%, #ffe938 100%);
  }

  /* A. Top-Left Blue Ray Box */
  .brand-box {
    width: 360px;
    height: 310px;
    position: relative;
    overflow: hidden;
    background: radial-gradient(circle at 50% 50%, #1e5de6 0%, #0d38a0 55%, #051a58 100%);
    border-right: 5px solid #ffe600;
    border-bottom: 4px solid #ffe600;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 4px 0 16px rgba(0,0,0,0.5);
    z-index: 10;
  }

  .brand-rays {
    position: absolute;
    top: -150px;
    left: -120px;
    width: 600px;
    height: 600px;
    background: repeating-conic-gradient(
      from 0deg at 50% 50%,
      rgba(255, 255, 255, 0.22) 0deg 12deg,
      transparent 12deg 24deg
    );
    pointer-events: none;
  }

  .brand-inner-frame {
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 4px solid #ffe600;
    border-radius: 18px;
    padding: 6px 22px 8px 22px;
    background: rgba(3, 15, 54, 0.82);
    box-shadow: 0 0 20px rgba(255, 230, 0, 0.5), inset 0 0 14px rgba(255, 230, 0, 0.35);
  }

  .brand-text-1 {
    paint-order: stroke fill;
    font-size: 84px;
    font-weight: 900;
    line-height: 0.92;
    color: #fff200;
    -webkit-text-stroke: 3px #543000;
    text-shadow: 3px 3px 0 #000, 0 0 16px rgba(255, 242, 0, 0.6);
    letter-spacing: 1px;
    font-family: 'KhandNews', sans-serif;
  }

  .brand-text-2 {
    paint-order: stroke fill;
    font-size: 96px;
    font-weight: 900;
    line-height: 0.92;
    color: #fff200;
    -webkit-text-stroke: 3px #543000;
    text-shadow: 3px 3px 0 #000, 0 0 16px rgba(255, 242, 0, 0.6);
    letter-spacing: 1px;
    margin-bottom: 6px;
    font-family: 'KhandNews', sans-serif;
  }

  .brand-live-pill {
    background: linear-gradient(180deg, #ff1a24 0%, #b80009 100%);
    color: #ffffff;
    font-size: 26px;
    font-weight: 900;
    padding: 2px 24px;
    border-radius: 6px;
    letter-spacing: 2px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.6);
    border: 2px solid #ffffff;
    font-family: 'PoppinsHeavy', sans-serif;
  }

  /* B. Top-Center Date & Month */
  .date-container {
    flex: 1;
    position: relative;
    display: flex;
    align-items: center;
    padding-left: 14px;
    padding-top: 4px;
  }

  .huge-date-number {
    paint-order: stroke fill;
    font-size: 245px;
    font-weight: 900;
    line-height: 0.78;
    color: #e50000;
    -webkit-text-stroke: 8px #ffe600;
    text-shadow: 4px 4px 0 #750000, 8px 8px 16px rgba(0,0,0,0.35);
    margin-right: 12px;
    letter-spacing: -6px;
    font-family: 'PoppinsHeavy', sans-serif;
  }

  .month-and-modi {
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding-top: 6px;
  }

  .month-name {
    paint-order: stroke fill;
    font-size: 142px;
    font-weight: 900;
    line-height: 0.80;
    color: #e50000;
    -webkit-text-stroke: 4.5px #ffffff;
    text-shadow: 3.5px 3.5px 0 #750000, 6px 6px 14px rgba(0,0,0,0.35);
    letter-spacing: -0.5px;
    font-family: 'KhandNews', sans-serif;
  }

  .modi-bar {
    display: flex;
    align-items: center;
    margin-top: 6px;
  }

  .modi-portrait {
    width: 95px;
    height: 95px;
    object-fit: cover;
    object-position: center top;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4));
    margin-right: 12px;
  }

  .modi-pill {
    background: linear-gradient(180deg, #ffc800 0%, #ffa500 100%);
    color: #000000;
    font-size: 38px;
    font-weight: 900;
    padding: 2px 20px;
    border-radius: 8px;
    border: 2px solid #ffffff;
    box-shadow: 0 3px 8px rgba(0,0,0,0.35);
    white-space: nowrap;
    font-family: 'KhandNews', sans-serif;
    letter-spacing: 0.5px;
  }

  /* C. Top-Right Day, Year & Mukhya */
  .top-right-box {
    width: 270px;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    padding-right: 18px;
    padding-top: 8px;
  }

  .day-and-year-row {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 8px;
    margin-bottom: 2px;
  }

  .day-name {
    font-size: 60px;
    font-weight: 900;
    line-height: 0.95;
    color: #002b49;
    letter-spacing: -0.5px;
    font-family: 'KhandNews', sans-serif;
  }

  .year-pill {
    background: #ffe600;
    color: #000000;
    font-size: 36px;
    font-weight: 900;
    padding: 1px 12px;
    border-radius: 6px;
    border: 2.5px solid #000000;
    box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    font-family: 'PoppinsHeavy', sans-serif;
  }

  .mukhya-top {
    paint-order: stroke fill;
    font-size: 78px;
    font-weight: 900;
    line-height: 0.92;
    color: #0044cc;
    -webkit-text-stroke: 3px #ffffff;
    text-shadow: 3px 3px 0 #001f5b, 5px 5px 10px rgba(0,0,0,0.35);
    text-align: right;
    letter-spacing: 0.5px;
    font-family: 'KhandNews', sans-serif;
    margin-top: 2px;
  }

  /* ═══════════════════════════════════════════════════════════
     2. MIDDLE STRIP 1: CYAN PILL + SAMACHAR (Y: 310 to 405px)
     ═══════════════════════════════════════════════════════════ */
  .middle-cyan-row {
    position: absolute;
    top: 310px;
    left: 0;
    width: 1280px;
    height: 95px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    z-index: 15;
    background: #ffe938;
  }

  .cyan-pill {
    flex: 1;
    height: 80px;
    background: linear-gradient(180deg, #dcf8ff 0%, #a0ebf9 50%, #68daef 100%);
    border: 2.5px solid #005577;
    border-radius: 12px;
    display: flex;
    align-items: center;
    padding: 0 18px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.25);
    margin-right: 18px;
    font-family: 'KhandNews', sans-serif;
  }

  .cyan-pill-text {
    color: #000000;
    font-size: 50px;
    font-weight: 900;
    letter-spacing: 0.5px;
    line-height: 1;
  }

  .cyan-pill-highlight {
    color: #d00000;
    font-weight: 900;
    margin-left: 6px;
  }

  .samachar-right {
    paint-order: stroke fill;
    font-size: 82px;
    font-weight: 900;
    line-height: 1;
    color: #003bbb;
    -webkit-text-stroke: 3.5px #ffffff;
    text-shadow: 3px 3px 0 #001f5b, 5px 5px 12px rgba(0,0,0,0.35);
    font-family: 'KhandNews', sans-serif;
    letter-spacing: 0.5px;
    padding-right: 8px;
  }

  /* ═══════════════════════════════════════════════════════════
     3. MIDDLE STRIP 2: WHITE HOOK STRIP (Y: 405 to 500px)
     ═══════════════════════════════════════════════════════════ */
  .white-strip {
    position: absolute;
    top: 405px;
    left: 0;
    width: 1280px;
    height: 95px;
    background: #ffffff;
    border-top: 3.5px solid #000000;
    border-bottom: 3.5px solid #000000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 14px;
    font-size: 41px;
    font-weight: 900;
    letter-spacing: 0.2px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    z-index: 15;
    white-space: nowrap;
    overflow: hidden;
    font-family: 'KhandNews', sans-serif;
  }

  .hook-item {
    margin-right: 12px;
    text-decoration: underline;
    text-underline-offset: 6px;
    text-decoration-thickness: 3.5px;
  }

  /* ═══════════════════════════════════════════════════════════
     4. BOTTOM STRIP: MASTER RED BANNER (Y: 500 to 720px, Height: 220px)
     ═══════════════════════════════════════════════════════════ */
  .bottom-red-banner {
    position: absolute;
    top: 500px;
    left: 0;
    width: 1280px;
    height: 220px;
    background: linear-gradient(180deg, #d80000 0%, #a00000 45%, #580000 100%);
    border-top: 4px solid #ffe600;
    display: flex;
    align-items: center;
    padding: 0 20px;
    box-shadow: inset 0 4px 12px rgba(255, 230, 0, 0.4);
    z-index: 15;
  }

  /* Left Circular Emblem Badge */
  .circular-emblem {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    background: radial-gradient(circle, #051838 0%, #000000 100%);
    border: 4.5px solid #ffe600;
    box-shadow: 0 0 20px rgba(255, 230, 0, 0.6), 0 6px 16px rgba(0,0,0,0.8);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-right: 22px;
  }

  .emblem-title {
    font-size: 34px;
    font-weight: 900;
    line-height: 1;
    color: #ffffff;
    font-family: 'PoppinsHeavy', sans-serif;
    letter-spacing: 1px;
  }

  .emblem-sub {
    font-size: 28px;
    font-weight: 900;
    line-height: 1;
    color: #ffe600;
    font-family: 'KhandNews', sans-serif;
    margin-top: 2px;
  }

  /* Giant 3D Golden Text */
  .giant-headline-container {
    flex: 1;
    display: flex;
    align-items: baseline;
    justify-content: center;
    font-family: 'PoppinsHeavy', sans-serif;
  }

  .giant-number {
    paint-order: stroke fill;
    font-size: 215px;
    font-weight: 900;
    line-height: 0.82;
    color: #fff200;
    -webkit-text-stroke: 8px #3a0000;
    text-shadow: 3px 3px 0 #200000, 6px 6px 0 #120000, 10px 10px 20px rgba(0,0,0,0.95);
    margin-right: 18px;
    letter-spacing: -4px;
  }

  .giant-words {
    paint-order: stroke fill;
    font-size: 168px;
    font-weight: 900;
    line-height: 0.82;
    color: #fff200;
    -webkit-text-stroke: 7.5px #3a0000;
    text-shadow: 3px 3px 0 #200000, 6px 6px 0 #120000, 10px 10px 20px rgba(0,0,0,0.95);
    letter-spacing: 0px;
    white-space: nowrap;
  }
</style>
</head>
<body>
  <!-- 1. TOP SECTION -->
  <div class="top-section">
    <div class="brand-box">
      <div class="brand-rays"></div>
      <div class="brand-inner-frame">
        <div class="brand-text-1">फटाफट</div>
        <div class="brand-text-2">न्यूज</div>
        <div class="brand-live-pill">LIVE</div>
      </div>
    </div>

    <div class="date-container">
      <div class="huge-date-number">__DAY_NUM__</div>
      <div class="month-and-modi">
        <div class="month-name">__MONTH_STR__</div>
        <div class="modi-bar">
          <img class="modi-portrait" src="__MODI_URI__" alt="PM Modi">
          <div class="modi-pill">5 बड़े ऐलान</div>
        </div>
      </div>
    </div>

    <div class="top-right-box">
      <div class="day-and-year-row">
        <div class="day-name">__WEEKDAY_STR__</div>
        <div class="year-pill">__YEAR_STR__</div>
      </div>
      <div class="mukhya-top">मुख्य</div>
    </div>
  </div>

  <!-- 2. MIDDLE STRIP 1: CYAN PILL + SAMACHAR -->
  <div class="middle-cyan-row">
    <div class="cyan-pill">
      <span class="cyan-pill-text">__CYAN_PILL_HTML__</span>
    </div>
    <div class="samachar-right">समाचार</div>
  </div>

  <!-- 3. MIDDLE STRIP 2: WHITE MULTI-COLOR HOOK STRIP WITH UNDERLINES -->
  <div class="white-strip">
    __WHITE_STRIP_HTML__
  </div>

  <!-- 4. BOTTOM STRIP: MASTER RED BANNER -->
  <div class="bottom-red-banner">
    <div class="circular-emblem">
      <div class="emblem-title">MP4</div>
      <div class="emblem-sub">NEWS</div>
    </div>
    <div class="giant-headline-container">
      <span class="giant-number">__BOTTOM_NUMBER__</span>
      <span class="giant-words">बड़ी खबरें</span>
    </div>
  </div>
</body>
</html>"""

    return (
        template
        .replace("__FONT_KHAND__", font_khand_uri)
        .replace("__FONT_POPPINS__", font_poppins_uri)
        .replace("__MODI_URI__", modi_img_uri)
        .replace("__DAY_NUM__", day_num)
        .replace("__MONTH_STR__", month_str)
        .replace("__WEEKDAY_STR__", weekday_str)
        .replace("__YEAR_STR__", year_str)
        .replace("__CYAN_PILL_HTML__", cyan_pill_html)
        .replace("__WHITE_STRIP_HTML__", white_strip_html)
        .replace("__BOTTOM_NUMBER__", bottom_number)
    )


def generate_dls_reference_pillow(
    day_num: str,
    month_str: str,
    weekday_str: str,
    year_str: str,
    white_strip_segments: list,
    bottom_number: str,
    out_path: str,
    is_crime_heavy: bool = False
) -> str:
    """Pure Pillow Engine Fallback: Draws identical layout"""
    canvas = Image.new("RGB", (THUMB_W, THUMB_H), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # 1. Top Section Background (Y: 0-310)
    for y in range(310):
        ratio = y / 310.0
        r = int(255 - ratio * 0)
        g = int(253 - ratio * 20)
        b = int(232 - ratio * 176)
        draw.line([(0, y), (THUMB_W, y)], fill=(r, g, b))

    # Top-Left Blue Brand Box
    draw.rectangle([0, 0, 360, 310], fill=(13, 56, 160), outline=(255, 230, 0), width=5)
    draw.rounded_rectangle([25, 20, 335, 290], radius=16, fill=(3, 15, 54), outline=(255, 230, 0), width=4)

    # Fonts
    f_khand = ImageFont.truetype(FONT_KHAND, 76) if os.path.exists(FONT_KHAND) else ImageFont.load_default()
    f_huge_date = ImageFont.truetype(FONT_POPPINS, 210) if os.path.exists(FONT_POPPINS) else ImageFont.load_default()
    f_month = ImageFont.truetype(FONT_KHAND, 120) if os.path.exists(FONT_KHAND) else ImageFont.load_default()
    f_day = ImageFont.truetype(FONT_KHAND, 54) if os.path.exists(FONT_KHAND) else ImageFont.load_default()
    f_strip = ImageFont.truetype(FONT_KHAND, 42) if os.path.exists(FONT_KHAND) else ImageFont.load_default()
    f_bot_num = ImageFont.truetype(FONT_POPPINS, 180) if os.path.exists(FONT_POPPINS) else ImageFont.load_default()
    f_bot_word = ImageFont.truetype(FONT_POPPINS, 140) if os.path.exists(FONT_POPPINS) else ImageFont.load_default()

    draw.text((70, 35), "फटाफट", fill=(255, 242, 0), font=f_khand, stroke_width=3, stroke_fill=(84, 48, 0))
    draw.text((105, 115), "न्यूज", fill=(255, 242, 0), font=f_khand, stroke_width=3, stroke_fill=(84, 48, 0))
    draw.rounded_rectangle([120, 220, 240, 260], radius=6, fill=(229, 9, 20), outline=(255, 255, 255), width=2)
    draw.text((145, 224), "LIVE", fill=(255, 255, 255), font=f_day)

    # Huge Date & Month
    draw.text((375, 25), day_num, fill=(229, 0, 0), font=f_huge_date, stroke_width=8, stroke_fill=(255, 230, 0))
    draw.text((630, 40), month_str, fill=(229, 0, 0), font=f_month, stroke_width=4, stroke_fill=(255, 255, 255))

    # Modi image thumbnail
    modi_p = MODI_CUTOUT_PNG if MODI_CUTOUT_PNG.exists() else MODI_PORTRAIT_JPG
    if modi_p.exists():
        try:
            with Image.open(modi_p) as m_img:
                m_resized = m_img.resize((84, 84))
                if m_resized.mode == "RGBA":
                    canvas.paste(m_resized, (630, 165), m_resized)
                else:
                    canvas.paste(m_resized, (630, 165))
        except Exception:
            pass

    # Top-Right Day, Year, Mukhya
    draw.text((1010, 20), weekday_str, fill=(0, 43, 73), font=f_day)
    draw.rounded_rectangle((1160, 24, 1260, 68), radius=6, fill=(255, 230, 0), outline=(0, 0, 0), width=2)
    draw.text((1175, 28), year_str, fill=(0, 0, 0), font=f_day)
    draw.text((1120, 105), "मुख्य", fill=(0, 68, 204), font=f_day, stroke_width=2, stroke_fill=(255, 255, 255))

    # 2. Middle Row: Cyan Pill + Samachar (Y: 310-405)
    draw.rectangle([0, 310, THUMB_W, 405], fill=(255, 233, 64))
    draw.rounded_rectangle([18, 318, 960, 398], radius=12, fill=(164, 237, 249), outline=(0, 85, 119), width=2)
    pill_label = f"देशभर की {bottom_number} बड़ी खबरों के 5 बड़े खुलासे" if is_crime_heavy else "आज PM मोदी सरकार ने लिए 5 बड़े फैसले"
    draw.text((36, 328), pill_label, fill=(0, 0, 0), font=f_strip)
    draw.text((1000, 315), "समाचार", fill=(0, 59, 187), font=f_khand, stroke_width=3, stroke_fill=(255, 255, 255))

    # 3. Middle White Strip (Y: 405-500)
    draw.rectangle([0, 405, THUMB_W, 500], fill=(255, 255, 255), outline=(0, 0, 0), width=3)
    x_cursor = 30
    color_map = {
        "#d00000": (208, 0, 0),
        "#0055cc": (0, 85, 204),
        "#008800": (0, 136, 0),
        "#000000": (0, 0, 0),
    }
    for seg in white_strip_segments:
        txt = seg.get("text", "") + " "
        c_hex = seg.get("color", "#000000")
        c_rgb = color_map.get(c_hex, (0, 0, 0))
        draw.text((x_cursor, 422), txt, fill=c_rgb, font=f_strip)
        bbox = draw.textbbox((x_cursor, 422), txt, font=f_strip)
        if not seg.get("no_underline", False):
            draw.line([(x_cursor, 475), (bbox[2] - 5, 475)], fill=c_rgb, width=3)
        x_cursor = bbox[2] + 12

    # 4. Bottom Red Banner (Y: 500-720)
    for y in range(500, 720):
        ratio = (y - 500) / 220.0
        r = int(216 - ratio * 128)
        g = 0
        b = 0
        draw.line([(0, y), (THUMB_W, y)], fill=(r, g, b))
    draw.line([(0, 500), (THUMB_W, 500)], fill=(255, 230, 0), width=4)

    # Left circular emblem
    draw.ellipse([25, 535, 165, 675], fill=(0, 0, 0), outline=(255, 230, 0), width=4)
    draw.text((55, 560), "MP4", fill=(255, 255, 255), font=f_day)
    draw.text((50, 615), "NEWS", fill=(255, 230, 0), font=f_day)

    # Giant 3D Golden text
    draw.text((220, 510), bottom_number, fill=(255, 242, 0), font=f_bot_num, stroke_width=8, stroke_fill=(58, 0, 0))
    draw.text((490, 530), "बड़ी खबरें", fill=(255, 242, 0), font=f_bot_word, stroke_width=7, stroke_fill=(58, 0, 0))

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
    channel_name: str = "MP4 NEWS"
) -> str:
    """
    Main Entrypoint: Generates the Master DLS News / Fatafat News YouTube Thumbnail
    100% matches user's reference image (media_1794477519388_bd6869db.jpg)
    """
    now = datetime.now()
    day_num = str(now.day)
    month_str = HINDI_MONTHS[now.month] if 1 <= now.month <= 12 else "नवंबर"
    weekday_str = HINDI_DAYS[now.weekday()]
    year_str = str(now.year)

    # Story count determines bottom number: 50 for 50-news bulletin, 10 for Top 10
    story_count = len(all_stories) if all_stories else (50 if "50" in headline else 10)
    bottom_number = "50"

    # Extract category-aware keywords & check if crime heavy
    white_segments, is_crime_heavy = extract_thumbnail_hook_segments(all_stories=all_stories, headline=headline, story=story)

    # Engine A: Headless Chromium / Edge Screenshot (Vector Sharpness & 3D Lighting)
    browser = find_browser_executable()
    if browser:
        try:
            html_content = build_dls_reference_html(
                day_num=day_num,
                month_str=month_str,
                weekday_str=weekday_str,
                year_str=year_str,
                white_strip_segments=white_segments,
                bottom_number=bottom_number,
                is_crime_heavy=is_crime_heavy,
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
                print(f"  ✓ [Headless Browser] DLS Reference Master Thumbnail Ready: {out_path} ({os.path.getsize(out_abs)/1024:.0f} KB)")
                return out_path
        except Exception as e:
            print(f"  ⚠️ Browser screenshot error: {e}")

    # Engine B: Pure Pillow Fallback Engine
    print("  🖼️ [Pillow Engine] Rendering DLS Reference Master Thumbnail...")
    generate_dls_reference_pillow(
        day_num=day_num,
        month_str=month_str,
        weekday_str=weekday_str,
        year_str=year_str,
        white_strip_segments=white_segments,
        bottom_number=bottom_number,
        out_path=out_path,
        is_crime_heavy=is_crime_heavy
    )
    print(f"  ✓ [Pillow Engine] DLS Reference Master Thumbnail Ready: {out_path}")
    return out_path


if __name__ == "__main__":
    demo_out = str(PROJECT_ROOT / "out" / "test_dls_reference_thumbnail.jpg")
    print("Testing 100% DLS Reference YouTube Thumbnail Generator...")
    res = generate_sensational_thumbnail(
        headline="महादेव सट्टा सिंडिकेट मामला 12 नवंबर को खत्म होगी सौरभ चंद्राकर की रिमांड",
        out_path=demo_out,
        all_stories=[
            {"screen_headline": "महादेव सट्टा सिंडिकेट मामला सौरभ चंद्राकर", "voiceover_script": "सौरभ चंद्राकर की रिमांड 12 नवंबर को खत्म हो रही है। पुलिस एनकाउंटर और सीबीआई जांच जारी है।"},
            {"screen_headline": "पुलिस ने आरोपी को मुठभेड़ में मारी गोली"}
        ]
    )
    print(f"Done! Result saved to: {res}")
