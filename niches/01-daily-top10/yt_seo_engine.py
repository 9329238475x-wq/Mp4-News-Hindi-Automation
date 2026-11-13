#!/usr/bin/env python3
"""
🚀 VidIQ-Style Viral SEO Engine for MP4 NEWS Automated YouTube Broadcasts
-------------------------------------------------------------------------
1. Live YouTube Autocomplete Harvester (India/Hindi search intent)
2. Competitor Tag Extractor (Top viral Hindi news videos)
3. High-CTR Dynamic Title Generator (< 100 characters)
4. Full 5,000-Character 7-Zone Description with Dynamic Audio-Synced Chapters
5. Strict 500-Character Viral Tags Set (VidIQ/TubeBuddy alternative)
"""

import os
import re
import json
import urllib.parse
from datetime import datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
HINDI_MONTHS = ["", "जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]
HINDI_DAYS = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]


# ═════════════════════════════════════════════════════════════════════════════
# 1. VIDIQ-STYLE LIVE KEYWORD HARVESTER
# ═════════════════════════════════════════════════════════════════════════════

def get_youtube_autocomplete(seed_query: str, max_results: int = 10) -> list:
    """
    Fetches real-time search queries from YouTube's live autocomplete suggestions endpoint.
    This gives the exact search terms real viewers in India are typing right now.
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
    except Exception as e:
        pass
    return []


def scrape_competitor_tags(search_query: str = "आज की ताजा खबर 50 बड़ी खबरें", max_videos: int = 2) -> list:
    """
    Extracts hidden metadata tags from top-ranking competitor YouTube videos.
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


def generate_viral_tags(all_stories: list = None, max_chars: int = 495) -> list:
    """
    Combines:
    1. Real-time YouTube Autocomplete
    2. Competitor Viral Tags
    3. Category Hard News Triggers
    Ensures total comma-separated length <= max_chars (YouTube strict 500-char limit).
    """
    # 1. Base Core Channel & News Tags (Proven high-volume)
    core_tags = [
        "आज की बड़ी खबरें",
        "50 बड़ी खबरें",
        "superfast news",
        "hindi news live",
        "breaking news hindi",
        "mp4 news",
        "crime alert",
        "taza samachar",
        "top news hindi",
        "fatafat news",
        "aaj ki taza khabar"
    ]

    # 2. Extract entities from top stories
    story_tags = []
    if all_stories:
        for s in all_stories[:6]:
            hl = s.get("screen_headline") or s.get("original_title") or ""
            # Extract key nouns/entities
            for token in ["महादेव सट्टा", "सौरभ चंद्राकर", "एनकाउंटर", "ED रेड", "CBI", "सुप्रीम कोर्ट", "माफिया", "रिमांड"]:
                if token in hl and token not in story_tags:
                    story_tags.append(token)

    # 3. Harvest Live Autocomplete
    autocomplete_tags = []
    try:
        auto1 = get_youtube_autocomplete("50 बड़ी खबरें", max_results=5)
        auto2 = get_youtube_autocomplete("aaj ki taza khabar", max_results=5)
        autocomplete_tags = auto1 + auto2
    except Exception:
        pass

    # Combine & deduplicate
    combined = []
    seen = set()
    for t in story_tags + core_tags + autocomplete_tags:
        cleaned = re.sub(r"[#,\n\r]", "", t).strip()
        low = cleaned.lower()
        if cleaned and low not in seen and len(cleaned) < 40:
            seen.add(low)
            combined.append(cleaned)

    # Pack into strict 500 characters
    final_tags = []
    current_length = 0
    for t in combined:
        # Each tag adds len(t) + 1 comma
        if current_length + len(t) + 1 <= max_chars:
            final_tags.append(t)
            current_length += len(t) + 1
        else:
            break

    return final_tags


# ═════════════════════════════════════════════════════════════════════════════
# 2. DYNAMIC HIGH-CTR TITLE GENERATOR (< 100 Chars)
# ═════════════════════════════════════════════════════════════════════════════

def build_viral_news_title(all_stories: list = None, bottom_number: str = "50") -> str:
    """
    Constructs an algorithmic, high-CTR YouTube video title strictly under 100 chars:
    Formula: [Date & Slot] + [Top 2 Story Shockers] + [Channel / Category Hook]
    """
    now = datetime.now()
    day = now.day
    month = HINDI_MONTHS[now.month] if 1 <= now.month <= 12 else "नवंबर"
    year = now.year

    # Extract 2 primary story entity hooks
    entity1 = "महादेव सट्टा"
    entity2 = "बड़ा एनकाउंटर"
    if all_stories:
        found_entities = []
        for s in all_stories:
            hl = s.get("screen_headline") or s.get("original_title") or ""
            for e in ["महादेव सट्टा", "सौरभ चंद्राकर", "UP एनकाउंटर", "ED की रेड", "CBI का छापा", "सुप्रीम कोर्ट सख्त", "माफिया पर बुलडोजर", "बड़ी गिरफ्तारी"]:
                if any(w in hl for w in e.split()) and e not in found_entities:
                    found_entities.append(e)
            if len(found_entities) >= 2:
                break
        if len(found_entities) >= 1:
            entity1 = found_entities[0]
        if len(found_entities) >= 2:
            entity2 = found_entities[1]

    # Pattern A: Primary Breaking Hard News
    title = f"Today Breaking News ! आज {day} {month} {year} के मुख्य समाचार | {entity1}, {entity2} | {bottom_number} बड़ी खबरें"

    # Strict YouTube Safety Check: Must be <= 95 characters
    if len(title) > 95:
        title = f"Today Breaking News ! {day} {month} के मुख्य समाचार | {entity1} | {bottom_number} बड़ी खबरें"
    if len(title) > 95:
        title = title[:92] + "..."

    return title


# ═════════════════════════════════════════════════════════════════════════════
# 3. 5,000-CHARACTER MASTER DESCRIPTION GENERATOR
# ═════════════════════════════════════════════════════════════════════════════

def build_master_description(
    all_stories: list = None,
    channel_name: str = "MP4 NEWS हिन्दी",
    bottom_number: str = "50"
) -> tuple:
    """
    Generates a structured, 7-Zone broadcast description up to 5,000 characters:
    Zone 1: Top 3 Lines (Above-the-fold hook & CTA)
    Zone 2: Dynamic Chapters / Timestamps (Calculated from audio durations)
    Zone 3: Top Headlines Index (Full stories summary for search indexers)
    Zone 4: Related Search Queries / Viral SEO Keyword clusters
    Zone 5: Channel Bio & Social Media Links
    Zone 6: Copyright Fair Use & Journalism Disclaimer
    Zone 7: Viral Hashtags
    """
    now = datetime.now()
    day = now.day
    month = HINDI_MONTHS[now.month] if 1 <= now.month <= 12 else "नवंबर"
    year = now.year
    weekday = HINDI_DAYS[now.weekday()]

    stories = all_stories or []

    # ZONE 1: Above-the-fold Hook (First 2-3 lines)
    zone1 = (
        f"Today Breaking News ! आज {day} {month} {year} ({weekday}) के दिनभर के सभी मुख्य समाचार और देश-दुनिया की {bottom_number} बड़ी खबरें। "
        f"देखिए क्राइम, प्रशासन, सुप्रीम कोर्ट, ED-CBI छापों और सनसनीखेज खुलासों की सबसे तेज और सटीक कवरेज सिर्फ {channel_name} पर।\n\n"
        f"🔴 ताज़ा खबरों के लिए चैनल को तुरंत सब्सक्राइब करें: https://youtube.com/@MP4NEWS\n"
    )

    # ZONE 2: Dynamic Video Chapters / Timestamps (Calculated from actual audio lengths)
    zone2_lines = [
        "--------------------------------------------------",
        "📌 इस वीडियो के मुख्य टाइमस्टैम्प (Video Chapters):",
        "00:00 - परिचय एवं मुख्य सुर्खियां (Intro)"
    ]

    current_seconds = 20.0  # Approx intro bumper time
    chapters_count = 1

    for idx, s in enumerate(stories, start=1):
        # Format MM:SS
        minutes = int(current_seconds // 60)
        seconds = int(current_seconds % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"

        hl = s.get("screen_headline") or s.get("original_title") or f"बड़ी खबर {idx}"
        # Keep chapter title concise
        clean_hl = re.sub(r"[\n\r\*]", "", hl).strip()
        if len(clean_hl) > 45:
            clean_hl = clean_hl[:42] + "..."

        zone2_lines.append(f"{time_str} - {idx:02d}. {clean_hl}")
        chapters_count += 1

        # Increment with actual audio duration or default 25s
        dur = float(s.get("audio_duration") or s.get("timing_specs", {}).get("total_story_seconds", 25.0))
        current_seconds += dur

    zone2_lines.append("--------------------------------------------------\n")
    zone2 = "\n".join(zone2_lines)

    # ZONE 3: Top Headlines Covered (Full Index for Google/YT search bot indexing)
    zone3_lines = [
        f"📰 इस बुलेटिन में शामिल {bottom_number} मुख्य बड़ी खबरें:"
    ]
    for idx, s in enumerate(stories, start=1):
        hl = s.get("screen_headline") or s.get("original_title") or f"खबर {idx}"
        clean_hl = re.sub(r"[\n\r\*]", "", hl).strip()
        zone3_lines.append(f"• {idx:02d}: {clean_hl}")

    zone3_lines.append("\n")
    zone3 = "\n".join(zone3_lines)

    # ZONE 4: Related Search Queries / High-Intent SEO Keywords
    zone4 = (
        "🔍 Related Search Queries / Top Search Terms:\n"
        "- Today Breaking News in Hindi Live\n"
        f"- Aaj Ki Taza Khabar {day} {month} {year}\n"
        f"- {bottom_number} Badi Khabrein Superfast News\n"
        "- Crime Alert Hindi News Today\n"
        "- Today News Headlines in Hindi\n"
        "- Fatafat Samachar Breaking News\n"
        f"- {channel_name} Live Broadcast\n\n"
    )

    # ZONE 5: Channel Info & Social Links
    zone5 = (
        "🌐 हमारे साथ सोशल मीडिया पर जुड़ें:\n"
        "• YouTube: https://youtube.com/@MP4NEWS\n"
        "• WhatsApp Channel: https://whatsapp.com/channel/MP4NEWS\n"
        "• Telegram: https://t.me/MP4NewsHindi\n"
        "• Business & Press Inquiry: 9329238475x@gmail.com\n\n"
    )

    # ZONE 6: Copyright Fair Use & Journalism Disclaimer
    zone6 = (
        "⚖️ Copyright & Journalism Disclaimer:\n"
        "Under Section 107 of the Copyright Act 1976, allowance is made for 'fair use' for purposes "
        "such as criticism, comment, news reporting, teaching, scholarship, and research. "
        "All visual press materials and references are used strictly for legitimate news reporting "
        "and informational public interest purposes.\n\n"
    )

    # ZONE 7: Viral Hashtags
    zone7 = (
        "#HindiNews #BreakingNews #SuperfastNews #50BadiKhabrein #MP4News "
        "#CrimeAlert #TazaKhabar #TodayNewsHindi #TopHeadlines"
    )

    full_desc = zone1 + zone2 + zone3 + zone4 + zone5 + zone6 + zone7

    # Ensure strictly <= 4,950 characters (YouTube allows 5,000 max)
    if len(full_desc) > 4950:
        # If stories list is huge, truncate zone 3 slightly to stay within limits
        allowed_len = 4950 - len(zone1 + zone2 + zone4 + zone5 + zone6 + zone7)
        truncated_zone3 = zone3[:allowed_len] + "\n... (सभी खबरें बुलेटिन में उपलब्ध)\n\n"
        full_desc = zone1 + zone2 + truncated_zone3 + zone4 + zone5 + zone6 + zone7

    return full_desc, chapters_count


# ═════════════════════════════════════════════════════════════════════════════
# 4. MASTER SEO PACKAGE BUNDLER
# ═════════════════════════════════════════════════════════════════════════════

def generate_youtube_seo_package(all_stories: list = None, bottom_number: str = "50") -> dict:
    """
    Main entrypoint: Generates the full SEO metadata package for YouTube upload:
    - title (< 100 chars)
    - description (<= 5,000 chars with chapters)
    - tags (<= 500 chars)
    - categoryId ('25' = News & Politics)
    """
    title = build_viral_news_title(all_stories=all_stories, bottom_number=bottom_number)
    description, chapters_count = build_master_description(all_stories=all_stories, bottom_number=bottom_number)
    tags = generate_viral_tags(all_stories=all_stories, max_chars=495)

    return {
        "title": title,
        "description": description,
        "tags": tags,
        "categoryId": "25",  # 25 = News & Politics in YouTube Data API
        "chapters_count": chapters_count,
        "title_length": len(title),
        "desc_length": len(description),
        "tags_char_count": sum(len(t) for t in tags) + len(tags) - 1
    }


if __name__ == "__main__":
    print("Testing VidIQ-Style Viral SEO Engine...")
    sample_stories = [
        {"screen_headline": "महादेव सट्टा सिंडिकेट मामला: सौरभ चंद्राकर की रिमांड पर फैसला", "audio_duration": 28.5},
        {"screen_headline": "रांची पुलिस ने बेल पर छूटे अपराधियों की निगरानी शुरू की", "audio_duration": 31.0},
        {"screen_headline": "ED की बड़ी रेड: शराब घोटाले में कई ठिकानों पर छापेमारी", "audio_duration": 29.0},
        {"screen_headline": "UP पुलिस का बड़ा एनकाउंटर: 50 हजार का इनामी बदमाश ढेर", "audio_duration": 27.5}
    ]
    pkg = generate_youtube_seo_package(all_stories=sample_stories, bottom_number="50")
    print(f"\n✓ Generated Title ({pkg['title_length']} chars):\n  {pkg['title']}")
    print(f"\n✓ Generated Tags ({len(pkg['tags'])} tags, {pkg['tags_char_count']} chars):\n  {', '.join(pkg['tags'])}")
    print(f"\n✓ Description Length: {pkg['desc_length']} / 5000 chars (Chapters: {pkg['chapters_count']})")
    print("\n--- Description Preview (First 500 chars) ---")
    print(pkg["description"][:500] + "...")
