#!/usr/bin/env python3
"""
🚀 High-Class VidIQ-Style Viral SEO Engine for MP4 NEWS Automated YouTube Broadcasts
-------------------------------------------------------------------------------------
1. High-Class Dynamic Title (< 95 chars, strictly according to that day's news, ZERO EMOJIS).
2. 5,000-Character Master Description (ZERO EMOJIS, ZERO TIMESTAMPS / TIME SLIPS).
3. VidIQ-Style Multi-Source Viral Keyword Harvester:
   - Real-time YouTube Autocomplete Suggestions (India / Hindi)
   - Competitor Tag Stealer (from top-ranking Hindi breaking news videos)
   - Dynamic Story-Specific Viral Tags (< 500 chars limit)
4. Dynamic Viral Hashtags (Story-specific + national news, ZERO EMOJIS).
"""

import os
import re
import json
import urllib.parse
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

HINDI_MONTHS = ["", "जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]
HINDI_DAYS = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]


# ═════════════════════════════════════════════════════════════════════════════
# 0. STRICT ZERO-EMOJI PURIFIER
# ═════════════════════════════════════════════════════════════════════════════

def clean_no_emojis(text: str) -> str:
    """
    Strips ALL Unicode emojis, pictographs, decorative dingbats, and symbols.
    Ensures 100% clean, high-class broadcast news typography.
    """
    if not text:
        return ""
    # Unicode emoji and symbol regex ranges
    emoji_pattern = re.compile(
        "["
        "\U00010000-\U0010ffff"
        "\u2600-\u27bf"
        "\ufe00-\ufe0f"
        "\u200d"
        "\u2300-\u23ff"
        "\u2b50\u2b55\u203c\u2049"
        "\u2190-\u21ff"
        "]+",
        flags=re.UNICODE
    )
    cleaned = emoji_pattern.sub("", text)
    # Remove awkward leftover double spaces
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r" *\n *", "\n", cleaned)
    return cleaned.strip()


# ═════════════════════════════════════════════════════════════════════════════
# 1. VIDIQ-STYLE LIVE KEYWORD & COMPETITOR TAG HARVESTER
# ═════════════════════════════════════════════════════════════════════════════

def get_youtube_autocomplete(seed_query: str, max_results: int = 10) -> list:
    """
    Fetches real-time search queries from YouTube's live autocomplete API.
    Reflects the exact phrases real viewers in India are typing right now.
    """
    url = f"https://suggestqueries.google.com/complete/search?client=youtube&ds=yt&hl=hi&gl=in&q={urllib.parse.quote(seed_query)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            match = re.search(r"window\.google\.ac\.h\((.*)\)", resp.text)
            if match:
                data = json.loads(match.group(1))
                if len(data) > 1 and isinstance(data[1], list):
                    return [item[0] for item in data[1][:max_results]]
    except Exception:
        pass
    return []


def scrape_competitor_tags(search_query: str = "आज की बड़ी खबरें 50", max_videos: int = 2) -> list:
    """
    Extracts hidden SEO tags from top-ranking competitor YouTube videos on breaking topics.
    """
    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_query)}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    tags = []
    try:
        resp = requests.get(search_url, headers=headers, timeout=7)
        video_ids = list(dict.fromkeys(re.findall(r"\"videoId\":\"([a-zA-Z0-9_-]{11})\"", resp.text)))[:max_videos]
        for vid in video_ids:
            try:
                watch_url = f"https://www.youtube.com/watch?v={vid}"
                w_resp = requests.get(watch_url, headers=headers, timeout=5)
                soup = BeautifulSoup(w_resp.text, "html.parser")
                meta = soup.find("meta", attrs={"name": "keywords"})
                if meta and meta.get("content"):
                    video_tags = [t.strip() for t in meta["content"].split(",") if t.strip()]
                    tags.extend(video_tags)
            except Exception:
                continue
    except Exception:
        pass
    return list(dict.fromkeys(tags))


def generate_vidiq_viral_tags(all_stories: list = None, max_chars: int = 495) -> list:
    """
    VidIQ-grade tag compiler:
    1. Extracts primary entities from today's top stories.
    2. Queries live YouTube autocomplete for today's breaking queries.
    3. Scrapes competitor video tags.
    4. Packs strictly under 500 characters comma-separated (ZERO EMOJIS).
    """
    # 1. Base Core Proven High-Velocity News Tags
    core_tags = [
        "आज की बड़ी खबरें",
        "50 बड़ी खबरें",
        "superfast news",
        "hindi news live",
        "breaking news hindi",
        "uncut bharat",
        "uncut bharat news",
        "ub news",
        "crime alert",
        "taza samachar",
        "top news hindi",
        "fatafat news",
        "aaj ki taza khabar"
    ]

    # 2. Extract entities and keywords from actual stories
    story_tags = []
    if all_stories:
        for s in all_stories[:6]:
            hl = s.get("screen_headline") or s.get("original_title") or ""
            for token in [
                "महादेव सट्टा", "सौरभ चंद्राकर", "पुलिस एनकाउंटर", "ED रेड",
                "CBI छापा", "सुप्रीम कोर्ट", "माफिया", "रिमांड", "बुलडोजर",
                "गिरफ्तारी", "शराब घोटाला", "बड़ा खुलासा"
            ]:
                if any(w in hl for w in token.split()) and token not in story_tags:
                    story_tags.append(token)

    # 3. Live YouTube Autocomplete harvest
    autocomplete_tags = []
    try:
        seed1 = story_tags[0] if story_tags else "50 बड़ी खबरें"
        auto1 = get_youtube_autocomplete(seed1, max_results=5)
        auto2 = get_youtube_autocomplete("आज की ताजा खबर", max_results=5)
        autocomplete_tags = auto1 + auto2
    except Exception:
        pass

    # 4. Competitor Tag harvest
    competitor_tags = []
    try:
        competitor_tags = scrape_competitor_tags("आज की ताजा खबर 50 बड़ी खबरें", max_videos=2)
    except Exception:
        pass

    # Combine, sanitize (ZERO EMOJIS), and deduplicate
    combined = []
    seen = set()
    for t in story_tags + core_tags + autocomplete_tags + competitor_tags:
        cleaned = clean_no_emojis(re.sub(r"[#,\n\r]", "", t)).strip()
        low = cleaned.lower()
        if cleaned and low not in seen and 2 <= len(cleaned) < 40:
            seen.add(low)
            combined.append(cleaned)

    # Pack into strict 500 characters
    final_tags = []
    current_length = 0
    for t in combined:
        if current_length + len(t) + 1 <= max_chars:
            final_tags.append(t)
            current_length += len(t) + 1
        else:
            break

    return final_tags


# ═════════════════════════════════════════════════════════════════════════════
# 2. HIGH-CLASS DYNAMIC TITLE GENERATOR (< 95 Chars, ZERO EMOJIS)
# ═════════════════════════════════════════════════════════════════════════════

def build_high_class_viral_title(all_stories: list = None, bottom_number: str = "50") -> str:
    """
    Constructs an algorithmic, high-class, Prime-Time news title strictly according
    to the actual news stories of that run.
    STRICT RULES:
    1. Maximum 95 characters (well under YouTube 100 char limit).
    2. ZERO EMOJIS.
    3. Incorporates exact date & today's top 2 breaking incidents.
    """
    now = datetime.now()
    day = now.day
    month = HINDI_MONTHS[now.month] if 1 <= now.month <= 12 else "नवंबर"
    year = now.year

    # Extract 2 primary story entity hooks dynamically from the actual stories
    entity1 = "महादेव सट्टा"
    entity2 = "बड़ा एनकाउंटर"

    if all_stories and len(all_stories) > 0:
        # Story 1 entity/action extraction
        s1_hl = all_stories[0].get("screen_headline") or all_stories[0].get("original_title") or ""
        # Clean headline into punchy 2-4 words
        s1_clean = re.sub(r"[\n\r\*।:!]", " ", s1_hl).strip()
        parts1 = s1_clean.split()
        if len(parts1) >= 3:
            entity1 = " ".join(parts1[:3])
        elif len(parts1) > 0:
            entity1 = s1_clean

        # Story 2 entity/action extraction
        if len(all_stories) > 1:
            s2_hl = all_stories[1].get("screen_headline") or all_stories[1].get("original_title") or ""
            s2_clean = re.sub(r"[\n\r\*।:!]", " ", s2_hl).strip()
            parts2 = s2_clean.split()
            if len(parts2) >= 3:
                entity2 = " ".join(parts2[:3])
            elif len(parts2) > 0:
                entity2 = s2_clean

    # Try Groq AI Editor for prime-time broadcast title if available
    try:
        from groq_engine import GroqEngine
        engine = GroqEngine()
        if engine.keys:
            prompt = (
                f"आज की तारीख: {day} {month} {year}\n"
                f"प्रमुख खबर 1: {entity1}\n"
                f"प्रमुख खबर 2: {entity2}\n"
                f"बुलेटिन: {bottom_number} बड़ी खबरें\n"
                "एक अत्यंत हाई-क्लास, गंभीर और वायरल यूट्यूब न्यूज़ टाइटल बनाओ।\n"
                "सख्त नियम:\n"
                "1. कोई इमोजी नहीं (ZERO EMOJIS).\n"
                "2. अधिकतम 92 अक्षर.\n"
                "3. फॉर्मेट: Today Breaking News ! आज की तारीख | मुख्य खबर | 50 बड़ी खबरें.\n"
                "JSON format: {\"title\": \"...\"}"
            )
            res = engine.chat_json("You are a senior national TV news editor. Output clean JSON only.", prompt)
            ai_title = res.get("title", "").strip() if res else ""
            ai_title = clean_no_emojis(ai_title)
            if ai_title and 40 <= len(ai_title) <= 95:
                return ai_title
    except Exception:
        pass

    # High-Class Algorithmic Template Fallback
    # Pattern: Today Breaking News ! आज 13 नवंबर के मुख्य समाचार | महादेव सट्टा, UP एनकाउंटर | 50 बड़ी खबरें
    title = f"Today Breaking News ! आज {day} {month} के मुख्य समाचार | {entity1}, {entity2} | {bottom_number} बड़ी खबरें"

    # Enforce strict character limits (< 95)
    title = clean_no_emojis(title)
    if len(title) > 95:
        title = f"Today Breaking News ! {day} {month} के मुख्य समाचार | {entity1} | {bottom_number} बड़ी खबरें"
    if len(title) > 95:
        title = title[:92] + "..."

    return title


# ═════════════════════════════════════════════════════════════════════════════
# 3. 5,000-CHARACTER MASTER DESCRIPTION (ZERO EMOJIS, ZERO TIMESTAMPS)
# ═════════════════════════════════════════════════════════════════════════════

def build_master_description(
    all_stories: list = None,
    channel_name: str = "Uncut भारत",
    bottom_number: str = "50"
) -> str:
    """
    Generates a structured, high-class broadcast description up to 5,000 characters:
    - ZERO EMOJIS.
    - ZERO TIMESTAMPS / TIME SLIPS (no 00:00).
    - Comprehensive news index for maximum search visibility.
    - High-intent search queries.
    - Legal fair use journalism disclaimer.
    - Clean viral hashtags.
    """
    now = datetime.now()
    day = now.day
    month = HINDI_MONTHS[now.month] if 1 <= now.month <= 12 else "नवंबर"
    year = now.year
    weekday = HINDI_DAYS[now.weekday()]

    stories = all_stories or []

    # ZONE 1: High-Class Opening Hook & Overview (NO EMOJIS, ZERO LINKS)
    zone1 = (
        f"Today Breaking News - आज {day} {month} {year} ({weekday}) के दिनभर के सभी मुख्य समाचार और देश की {bottom_number} बड़ी खबरें।\n\n"
        f"इस विशेष बुलेटिन में देखिए क्राइम, प्रशासन की सख्त कार्रवाई, सुप्रीम कोर्ट के बड़े फैसले, "
        f"ED और CBI की छापेमारी, और सनसनीखेज मामलों की निष्पक्ष, तथ्यपरक और तेज रिपोर्टिंग सिर्फ {channel_name} पर।\n\n"
        f"ताज़ा खबरों के नियमित अपडेट्स के लिए {channel_name} चैनल को अभी सब्सक्राइब करें।\n\n"
        "==================================================\n"
    )

    # ZONE 2: Key News Coverage Highlights (NO TIMESTAMPS / TIME SLIPS!)
    zone2_lines = [
        f"प्रमुख समाचार एवं बड़ी कवरेज सूची ({bottom_number} मुख्य खबरें):",
        "--------------------------------------------------"
    ]

    for idx, s in enumerate(stories, start=1):
        hl = s.get("screen_headline") or s.get("original_title") or f"बड़ी खबर {idx}"
        clean_hl = clean_no_emojis(re.sub(r"[\n\r\*]", "", hl)).strip()
        cat = s.get("category", "")
        cat_str = f"[{cat}] " if cat else ""
        zone2_lines.append(f"{idx:02d}. {cat_str}{clean_hl}")

    zone2_lines.append("--------------------------------------------------\n")
    zone2 = "\n".join(zone2_lines)

    # ZONE 3: Related Search Queries / High-Intent SEO Clusters (NO EMOJIS)
    zone3 = (
        "संबंधित सर्च कीवर्ड्स एवं ट्रेंडिंग विषय:\n"
        f"- Today Breaking News in Hindi Live {day} {month}\n"
        f"- Aaj Ki Taza Khabar {day} {month} {year}\n"
        f"- {bottom_number} Badi Khabrein Superfast News\n"
        "- Crime Alert Hindi News Today Update\n"
        "- Today News Headlines in Hindi Live\n"
        "- Fatafat Samachar Breaking News Today\n"
        f"- {channel_name} Live Hindi Broadcast\n"
        "- Desh Duniya Ki Badi Khabrein Today\n\n"
    )

    # ZONE 4: Channel Info & Contact (NO LINKS, NO EMOJIS)
    zone4 = (
        "चैनल एवं संपर्क विवरण:\n"
        f"• चैनल: {channel_name}\n"
        "• यूट्यूब हैंडल: @UncutBharat\n"
        "• ईमेल संपर्क: 9329238475x@gmail.com\n\n"
    )

    # ZONE 5: Journalism & Legal Fair Use Disclaimer (NO EMOJIS)
    zone5 = (
        "पत्रकारिता एवं कानूनी डिस्क्लेमर (Fair Use Notice):\n"
        "Under Section 107 of the Copyright Act 1976, allowance is made for 'fair use' for purposes "
        "such as criticism, comment, news reporting, teaching, scholarship, and research. "
        "All visual press materials and public coverage references are used strictly for legitimate "
        "news reporting, public information, and journalistic integrity.\n\n"
    )

    # ZONE 6: Viral Hashtags (Dynamic + Broad, NO EMOJIS)
    hashtags = [
        "#HindiNews",
        "#BreakingNews",
        "#SuperfastNews",
        f"#{bottom_number}BadiKhabrein",
        "#UncutBharat",
        "#CrimeAlert",
        "#TodayNewsHindi",
        "#TazaKhabar",
        "#TopHeadlines"
    ]
    # Add dynamic story hashtags if available
    if stories:
        for s in stories[:4]:
            hl = s.get("screen_headline") or s.get("original_title") or ""
            for tag in ["#MahadevSatta", "#Encounter", "#EDRaid", "#SupremeCourt"]:
                if any(w.lower() in hl.lower() for w in tag[1:].split()):
                    if tag not in hashtags:
                        hashtags.append(tag)

    zone6 = " ".join(hashtags)

    full_desc = zone1 + zone2 + zone3 + zone4 + zone5 + zone6

    # Strict emoji cleanse
    full_desc = clean_no_emojis(full_desc)

    # STRICT ZERO-LINK ENFORCEMENT: Remove all URLs / web links (as requested by user)
    full_desc = re.sub(r"https?://\S+", "", full_desc)
    full_desc = re.sub(r"www\.\S+", "", full_desc)
    full_desc = re.sub(r"\b\w+\.(?:com|org|net|in|io|me|co)\b/\S*", "", full_desc)

    # Enforce strictly <= 4,950 characters (YouTube allows 5,000 max)
    if len(full_desc) > 4950:
        allowed_len = 4950 - len(zone1 + zone3 + zone4 + zone5 + zone6)
        truncated_zone2 = zone2[:allowed_len] + "\n... (सभी खबरें बुलेटिन में उपलब्ध)\n\n"
        full_desc = zone1 + truncated_zone2 + zone3 + zone4 + zone5 + zone6

    return full_desc


# ═════════════════════════════════════════════════════════════════════════════
# 4. MASTER SEO PACKAGE BUNDLER
# ═════════════════════════════════════════════════════════════════════════════

def generate_youtube_seo_package(all_stories: list = None, bottom_number: str = "50") -> dict:
    """
    Main entrypoint: Generates the full SEO metadata package for YouTube upload:
    - title (< 95 chars, zero emojis, dynamic to actual news)
    - description (<= 5,000 chars, zero emojis, zero timestamps)
    - tags (<= 500 chars, VidIQ-style live autocomplete + competitor tags, zero emojis)
    - categoryId ('25' = News & Politics)
    """
    title = build_high_class_viral_title(all_stories=all_stories, bottom_number=bottom_number)
    description = build_master_description(all_stories=all_stories, bottom_number=bottom_number)
    tags = generate_vidiq_viral_tags(all_stories=all_stories, max_chars=495)

    return {
        "title": title,
        "description": description,
        "tags": tags,
        "categoryId": "25",  # 25 = News & Politics in YouTube Data API
        "title_length": len(title),
        "desc_length": len(description),
        "tags_count": len(tags),
        "tags_char_count": sum(len(t) for t in tags) + len(tags) - 1
    }


if __name__ == "__main__":
    print("Testing High-Class VidIQ-Style Viral SEO Engine (Zero Emojis, Zero Timestamps)...")
    sample_stories = [
        {"screen_headline": "महादेव सट्टा सिंडिकेट मामला: सौरभ चंद्राकर की रिमांड पर फैसला", "category": "क्राइम व कानून"},
        {"screen_headline": "रांची पुलिस ने बेल पर छूटे अपराधियों की निगरानी शुरू की", "category": "क्राइम व कानून"},
        {"screen_headline": "ED की बड़ी रेड: शराब घोटाले में कई ठिकानों पर छापेमारी", "category": "जांच व छापे"},
        {"screen_headline": "UP पुलिस का बड़ा एनकाउंटर: 50 हजार का इनामी बदमाश ढेर", "category": "क्राइम व कानून"}
    ]
    pkg = generate_youtube_seo_package(all_stories=sample_stories, bottom_number="50")
    print(f"\n✓ Generated Title ({pkg['title_length']} chars, Zero Emojis):\n  {pkg['title']}")
    print(f"\n✓ Generated Tags ({pkg['tags_count']} tags, {pkg['tags_char_count']} chars, Zero Emojis):\n  {', '.join(pkg['tags'])}")
    print(f"\n✓ Description Length: {pkg['desc_length']} / 5000 chars (Zero Emojis, Zero Timestamps)")
    print("\n--- Description Preview (First 600 chars) ---")
    print(pkg["description"][:600] + "...")
