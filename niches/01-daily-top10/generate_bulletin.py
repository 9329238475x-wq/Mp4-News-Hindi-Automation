"""
Master 7-Pillar TV Bulletin Script Generator (Decoupled 4-Stage Groq 120B Model)
-------------------------------------------------------------------------------
1. Stage 1: विशुद्ध एंकर वॉइसओवर स्क्रिप्ट & 5-7 चंक्स (Zero Slang, हिंदी शब्द संख्याएं).
2. Stage 2: 3-4 डायनामिक स्क्रीन हेडलाइंस (स्क्रीन पर 2, 3, 4 बार बदलने वाली हेडलाइंस).
3. Stage 3: चंक-दर-चंक 100% इंग्लिश रियल प्रेस इमेज सर्च कीवर्ड्स (सटीक व्यक्ति, स्थान, वाहन, कार्रवाई).
4. Stage 4: डायनामिक प्रासंगिक ट्रेंडिंग मीम कीवर्ड्स (100% इंग्लिश, नो हार्डकोडिंग, नो ट्रैजेडी).
5. आउटपुट को 'generated_sample_top10.json', 'bulletin_scripts.txt' और 'out/story_XX/script_XX.txt' में सेव करना।
"""

import os
import sys
import re
import json
import time
import datetime
from dotenv import load_dotenv

# Windows UTF-8 एनकोडिंग सपोर्ट
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

from groq_engine import GroqEngine
from prompts import (
    STAGE1_SCRIPT_SYSTEM_PROMPT,
    build_stage1_script_prompt,
    STAGE2_HEADLINES_SYSTEM_PROMPT,
    build_stage2_headlines_prompt,
    STAGE3_IMAGE_KEYWORDS_SYSTEM_PROMPT,
    build_stage3_image_prompt,
    STAGE4_MEME_KEYWORDS_SYSTEM_PROMPT,
    build_stage4_meme_prompt,
)

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURR_DIR, "..", ".."))
INPUT_JSON_PATH = os.path.join(CURR_DIR, "latest_24h_full_news.json")
OUTPUT_JSON_PATH = os.path.join(CURR_DIR, "generated_sample_top10.json")
OUTPUT_TXT_PATH = os.path.join(CURR_DIR, "bulletin_scripts.txt")
OUT_DIR = os.path.join(BASE_DIR, "out")


def sanitize_anchor_text(t: str) -> str:
    """अनौपचारिक व बचकाने शब्दों (जैसे 'भाई', 'अरे भाई', 'यार') को सख्ती से हटाना"""
    if not t:
        return ""
    t = re.sub(r'\b(अरे भाई|भाई साहब|भाई,|भाई|यार|भैया|दोस्त|अपन)\b', '', t)
    return re.sub(r'\s+', ' ', t).strip()


def sanitize_keyword_master(kw: str) -> str:
    """
    मास्टर कीवर्ड सैनिटाइज़र:
    1. किसी भी साल (1900-2099) को हटाना।
    2. किसी भी समय (12:30 PM, 3:30, AM, PM, baje) को हटाना।
    3. कोट्स, ब्रैकेट्स, स्पेशल कैरेक्टर्स हटाना।
    4. 2 से 4 शब्दों का छोटा, हाई-इम्पैक्ट सर्च कीवर्ड बनाना।
    """
    if not kw:
        return ""
    clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', str(kw))
    clean = re.sub(r'\b(19\d\d|20\d\d)\b', '', clean)
    clean = re.sub(r'\b\d{1,2}(:\d{2})?\s*(am|pm|a\.m\.|p\.m\.|baje|hrs|hours)?\b', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\b(start|route|departure|concluding|ceremony|boarding|transport|heavy|ban|closure|save|remove|during|after|before)\b', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\s+', ' ', clean).strip()
    words = clean.split()
    if not words:
        return ""
    return " ".join(words[:4])


def process_single_story_multi_stage(engine: GroqEngine, story: dict) -> dict:
    """
    एक खबर के लिए 4-स्टेज डीकपल्ड Groq AI पाइपलाइन:
    1. स्टेज 1: वॉइसओवर स्क्रिप्ट & चंक्स
    2. स्टेज 2: स्क्रीन पर 2, 3, 4 बार बदलने वाली हेडलाइंस
    3. स्टेज 3: रियल न्यूज़ इमेज कीवर्ड्स (100% English)
    4. स्टेज 4: संदर्भानुसार ट्रेंडिंग मीम कीवर्ड्स (100% English)
    """
    s_num = story.get("story_number", 1)
    p_name = story.get("pillar_name", "देश की बड़ी खबर")
    title = story.get("title", "")

    print(f"\n" + "─" * 78, flush=True)
    print(f"🎬 [खबर #{s_num:02d}] {p_name}: {title[:60]}...", flush=True)

    # ──────────────────────────────────────────────────────────────────────────
    # स्टेज 1: वॉइसओवर स्क्रिप्ट & 5-7 वाक्य चंक्स
    # ──────────────────────────────────────────────────────────────────────────
    print(f"   🎙️  [स्टेज 1/4] एंकर वॉइसओवर स्क्रिप्ट और 5-7 चंक्स तैयार हो रहे हैं...", flush=True)
    stage1_prompt = build_stage1_script_prompt(story)
    try:
        stage1_resp = engine.chat_json(
            system_prompt=STAGE1_SCRIPT_SYSTEM_PROMPT,
            user_prompt=stage1_prompt,
            temperature=0.3
        )
    except Exception as e:
        print(f"   ⚠️ स्टेज 1 एरर: {e}", flush=True)
        stage1_resp = {}

    screen_hl = sanitize_anchor_text(stage1_resp.get("screen_headline", title[:50])).replace("**", "").replace("*", "")
    raw_chunks = stage1_resp.get("chunks", [])

    if not raw_chunks:
        # सेफ फॉलबैक
        raw_chunks = [
            {"chunk_index": 1, "sentence": f"**{title[:75]}**", "bullet_text": title[:75]},
            {"chunk_index": 2, "sentence": f"यह खबर **{story.get('source', 'प्रेस डेस्क')}** द्वारा सामने आई है।", "bullet_text": "प्रामाणिक रिपोर्ट"},
            {"chunk_index": 3, "sentence": "मामले में प्रशासनिक और कानूनी **जांच तेज** कर दी गई है।", "bullet_text": "जांच जारी"}
        ]

    # टेक्स्ट सैनिटाइजेशन
    cleaned_chunks = []
    bulletin_points = []
    for idx, c in enumerate(raw_chunks, 1):
        s_clean = sanitize_anchor_text(c.get("sentence", ""))
        b_clean = sanitize_anchor_text(c.get("bullet_text", s_clean))
        cleaned_chunks.append({
            "chunk_index": idx,
            "sentence": s_clean,
            "bullet_text": b_clean,
            "visual_intent": "REAL_PHOTO",
            "image_keywords_en": [],
            "meme_keyword_en": None
        })
        bulletin_points.append(b_clean)

    stage1_data = {
        "screen_headline": screen_hl,
        "category": stage1_resp.get("category", p_name),
        "chunks": cleaned_chunks
    }
    print(f"   ✅ [स्टेज 1 पूर्ण] {len(cleaned_chunks)} चंक्स तैयार! हेडलाइन: '{screen_hl[:45]}...'", flush=True)

    time.sleep(0.4)

    # ──────────────────────────────────────────────────────────────────────────
    # स्टेज 2: 3-4 डायनामिक स्क्रीन हेडलाइंस (स्क्रीन पर 2, 3, 4 बार बदलने वाली)
    # ──────────────────────────────────────────────────────────────────────────
    print(f"   📺 [स्टेज 2/4] स्क्रीन पर बदलने वाली 3-4 मुख्य हेडलाइंस तैयार हो रही हैं...", flush=True)
    stage2_prompt = build_stage2_headlines_prompt(story, stage1_data)
    try:
        stage2_resp = engine.chat_json(
            system_prompt=STAGE2_HEADLINES_SYSTEM_PROMPT,
            user_prompt=stage2_prompt,
            temperature=0.3
        )
    except Exception as e:
        print(f"   ⚠️ स्टेज 2 हेडलाइंस एरर: {e}", flush=True)
        stage2_resp = {}

    raw_headlines = stage2_resp.get("screen_headlines", [])
    if not raw_headlines:
        raw_headlines = [screen_hl]
        for bp in bulletin_points[:3]:
            raw_headlines.append(bp)

    cleaned_headlines = [sanitize_anchor_text(h).replace("**", "").replace("*", "") for h in raw_headlines if h]
    if len(cleaned_headlines) < 3:
        cleaned_headlines.append(screen_hl)

    print(f"   ✅ [स्टेज 2 पूर्ण] {len(cleaned_headlines)} स्क्रीन हेडलाइंस तैयार!", flush=True)
    for h_idx, h in enumerate(cleaned_headlines, 1):
        print(f"      🔹 [हेडलाइन {h_idx}] {h}", flush=True)

    time.sleep(0.4)

    # ──────────────────────────────────────────────────────────────────────────
    # स्टेज 3: 100% इंग्लिश रियल प्रेस इमेज सर्च कीवर्ड्स (मास्टर 2-4 शब्द, शून्य साल, शून्य समय)
    # ──────────────────────────────────────────────────────────────────────────
    print(f"   📸 [स्टेज 3/4] चंक-दर-चंक रियल प्रेस इमेज सर्च कीवर्ड्स (Master 2-4 Words, No Year/Time)...", flush=True)
    stage3_prompt = build_stage3_image_prompt(story, stage1_data, cleaned_headlines)
    try:
        stage3_resp = engine.chat_json(
            system_prompt=STAGE3_IMAGE_KEYWORDS_SYSTEM_PROMPT,
            user_prompt=stage3_prompt,
            temperature=0.2
        )
    except Exception as e:
        print(f"   ⚠️ स्टेज 3 एरर: {e}", flush=True)
        stage3_resp = {}

    chunk_img_kws = stage3_resp.get("chunk_image_keywords", [])
    raw_broad_kws = stage3_resp.get("broad_story_keywords_en", [])

    # चंक्स में मास्टर सैनिटाइज्ड इमेज कीवर्ड्स मैप करना (No years, No times, 2-4 words)
    kw_by_index = {item.get("chunk_index"): item.get("image_keywords_en", []) for item in chunk_img_kws}
    for c in cleaned_chunks:
        c_idx = c["chunk_index"]
        c_kws = kw_by_index.get(c_idx, [])
        sanitized_list = []
        for raw_k in c_kws:
            s_k = sanitize_keyword_master(raw_k)
            if s_k and s_k not in sanitized_list:
                sanitized_list.append(s_k)
        if not sanitized_list:
            sanitized_list = [f"{story.get('title', '')[:25]} news", "India press coverage"]
        c["image_keywords_en"] = sanitized_list[:3]
        c["visual_intent"] = "REAL_PHOTO"
        c["meme_keyword_en"] = None

    broad_kws = []
    for bk in raw_broad_kws:
        s_bk = sanitize_keyword_master(bk)
        if s_bk and s_bk not in broad_kws:
            broad_kws.append(s_bk)

    print(f"   ✅ [स्टेज 3 पूर्ण] सभी चंक्स को 100% असली व संक्षिप्त इमेज कीवर्ड्स मिले (+ {len(broad_kws)} ब्रॉड कीवर्ड्स)", flush=True)

    # ──────────────────────────────────────────────────────────────────────────
    # स्टेज 4: मीम्स 100% बंद (Broadcast Standards: Zero Memes, Pure Real News Photos)
    # ──────────────────────────────────────────────────────────────────────────
    print(f"   🛡️ [स्टेज 4/4] ब्रॉडकास्ट पॉलिसी: मीम्स 100% बंद (Strictly 100% Authentic News Photos Only)", flush=True)

    # ──────────────────────────────────────────────────────────────────────────
    # डेटा संकलन और फाइल्स निर्माण
    # ──────────────────────────────────────────────────────────────────────────
    story_dir_name = f"story_{s_num:02d}"
    story_dir = os.path.join(OUT_DIR, story_dir_name)
    news_dir = os.path.join(story_dir, "news real image")
    meems_dir = os.path.join(story_dir, "meems image")
    voice_dir = os.path.join(story_dir, "voice over")
    os.makedirs(news_dir, exist_ok=True)
    os.makedirs(meems_dir, exist_ok=True)
    os.makedirs(voice_dir, exist_ok=True)

    primary_img_rel = f"out/{story_dir_name}/news real image/news_img_{s_num}_01.jpg"
    primary_audio_rel = f"out/{story_dir_name}/voice over/audio_story_{s_num}.mp3"

    # सभी अंग्रेजी कीवर्ड्स संकलित करना (मास्टर क्लीन, शून्य मीम्स)
    all_kws_en = []
    for c in cleaned_chunks:
        for kw in c.get("image_keywords_en", []):
            if kw and kw not in all_kws_en:
                all_kws_en.append(kw)
    for bkw in broad_kws:
        if bkw and bkw not in all_kws_en:
            all_kws_en.append(bkw)

    clean_voiceover = " ".join([c["sentence"].replace("**", "").replace("*", "") for c in cleaned_chunks])

    # मुख्य स्क्रीन हेडलाइन (पहली हेडलाइन)
    primary_headline = cleaned_headlines[0] if cleaned_headlines else screen_hl

    # स्क्रिप्ट फाइल सेव करना: out/story_XX/script_XX.txt
    script_txt_path = os.path.join(story_dir, f"script_{s_num}.txt")
    with open(script_txt_path, "w", encoding="utf-8") as sf:
        sf.write(f"मुख्य स्क्रीन हेडलाइन: {primary_headline}\n")
        sf.write(f"श्रेणी: {stage1_data['category']}\n")
        sf.write("═" * 60 + "\n\n")
        sf.write("स्क्रीन पर बदलने वाली हेडलाइंस (CHANGING SCREEN HEADLINES):\n")
        for h_i, h_text in enumerate(cleaned_headlines, 1):
            sf.write(f"[{h_i}] {h_text}\n")
        sf.write("\n" + "═" * 60 + "\n\n")
        sf.write("एंकर वॉइसओवर स्क्रिप्ट (EDGE-TTS READY):\n")
        sf.write(clean_voiceover + "\n\n")
        sf.write("चंक-दर-चंक विवरण (CHUNKS & VISUAL KEYWORDS):\n")
        for c in cleaned_chunks:
            intent = "🤣 [MEME REACTION]" if c.get("visual_intent") == "MEME_REACTION" else "📸 [REAL PHOTO]"
            sf.write(f"[{c['chunk_index']}] {intent} {c['sentence']}\n")
            if c.get("image_keywords_en"):
                sf.write(f"    🔎 Image Query (EN): {', '.join(c['image_keywords_en'])}\n")
            if c.get("meme_keyword_en"):
                sf.write(f"    🎭 Meme Query (EN): {c['meme_keyword_en']}\n")

    merged_story = {
        "story_number": s_num,
        "category": stage1_data["category"],
        "screen_headline": primary_headline,
        "screen_headlines": cleaned_headlines,
        "chunks": cleaned_chunks,
        "bulletin_points": bulletin_points,
        "bullet_points": [p.replace("**", "").replace("*", "").strip() for p in bulletin_points],
        "voiceover_script": clean_voiceover,
        "visual_keywords": all_kws_en,
        "visual_keywords_en": all_kws_en,
        "primary_source_index": s_num - 1,
        "real_image_url": story.get("images", [{}])[0].get("url", None) if story.get("images") else None,
        "real_image_attribution": story.get("source", "न्यूज़ डेस्क"),
        "original_title": story.get("title", ""),
        "local_news_image": primary_img_rel,
        "local_visual_asset": primary_img_rel,
        "local_audio_asset": primary_audio_rel,
        "article_url": story.get("url", ""),
        "published_at": story.get("published_at", ""),
        "word_count_original": story.get("word_count", 0),
        "images": story.get("images", []),
        "videos": story.get("videos", [])
    }
    return merged_story


def generate_dls_bulletin(batch_size: int = 1, max_stories: int = None) -> list:
    """
    मास्टर 4-स्टेज टीवी बुलेटिन जेनेरेटर:
    हर खबर को अलग-अलग 4 केंद्रित Groq AI अनुरोधों (Script -> Dynamic Headlines -> Press Image KWs -> Dynamic Memes) से प्रोसेस करता है।
    """
    if not os.path.exists(INPUT_JSON_PATH):
        print(f"ℹ️ {INPUT_JSON_PATH} नहीं मिली। स्वचालित रूप से 'fetch_full_news.py' चला रहे हैं...", flush=True)
        fetch_script = os.path.join(CURR_DIR, "fetch_full_news.py")
        if os.path.exists(fetch_script):
            subprocess.run([sys.executable, fetch_script], check=True)
        if not os.path.exists(INPUT_JSON_PATH):
            raise FileNotFoundError(f"इनपुट फाइल नहीं मिली: {INPUT_JSON_PATH}।")

    with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
        full_stories = json.load(f)

    if max_stories:
        full_stories = full_stories[:max_stories]

    total_stories = len(full_stories)
    print("\n" + "═" * 84, flush=True)
    print(f"🎬 डीकपल्ड 4-स्टेज टीवी बुलेटिन जेनेरेटर (Groq 120B Model)", flush=True)
    print(f"🎯 इनपुट  : {total_stories} पूर्ण समाचार (latest_24h_full_news.json)", flush=True)
    print(f"✨ नियम   : 4 अलग-अलग केंद्रित अनुरोध (Script ➡️ Screen Headlines ➡️ Press Image KWs ➡️ Dynamic Memes)", flush=True)
    print("═" * 84, flush=True)

    engine = GroqEngine()
    final_bulletin_stories = []

    for idx, story in enumerate(full_stories, 1):
        story["story_number"] = idx
        processed = process_single_story_multi_stage(engine, story)
        final_bulletin_stories.append(processed)
        time.sleep(0.5)

    # 1. JSON फाइल में सेव करें
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(final_bulletin_stories, f, ensure_ascii=False, indent=2)

    # 2. संपूर्ण बुलेटिन रिपोर्ट टेक्स्ट फाइल में सेव करें
    write_bulletin_txt_report(final_bulletin_stories, OUTPUT_TXT_PATH)

    print("\n" + "═" * 84, flush=True)
    print(f"🎉 सभी {len(final_bulletin_stories)} खबरों का डीकपल्ड 4-स्टेज बुलेटिन सफलतापूर्वक तैयार!", flush=True)
    print(f"📁 मुख्य JSON डेटा : {OUTPUT_JSON_PATH}", flush=True)
    print(f"📄 बुलेटिन स्क्रिप्ट: {OUTPUT_TXT_PATH}", flush=True)
    print("═" * 84, flush=True)

    return final_bulletin_stories


def write_bulletin_txt_report(stories: list, output_path: str):
    """उपयोगकर्ता के पढ़ने और जांचने के लिए सुंदर टेक्स्ट रिपोर्ट बनाना"""
    now_str = datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")
    lines = []
    lines.append("=" * 84)
    lines.append("🎙️ डीकपल्ड 4-स्टेज मास्टर टीवी बुलेटिन स्क्रिप्ट्स (GROQ 120B DECOUPLED PIPELINE)")
    lines.append(f"📅 रिपोर्ट जेनरेशन समय: {now_str}")
    lines.append(f"📊 कुल बुलेटिन खबरें : {len(stories)}")
    lines.append("🛡️  फॉर्मूला             : 4-स्टेज अलग अनुरोध | चेंजिंग हेडलाइंस (2,3,4 बार) | 100% इंग्लिश कीवर्ड्स | नो स्लैंग | डायनामिक मीम्स")
    lines.append("=" * 84)
    lines.append("\n")

    for s in stories:
        lines.append("=" * 84)
        lines.append(f"📌 बुलेटिन खबर #{s['story_number']:02d} | {s['category']}")
        lines.append("=" * 84)
        lines.append(f"मूल समाचार शीर्षक : {s['original_title']}")
        lines.append(f"स्रोत & समय       : {s['real_image_attribution']} ({s['published_at']})")
        lines.append(f"ओरिजिनल फोटो     : {s['local_news_image']}")
        lines.append("-" * 84)
        lines.append(f"🔴 मुख्य टीवी स्क्रीन हेडलाइन:")
        lines.append(f"   ▶ {s['screen_headline']}")
        lines.append("")
        lines.append(f"📺 स्क्रीन पर बदलने वाली 3-4 हेडलाइंस (SEQUENTIAL SCREEN HEADLINES):")
        for h_i, h_text in enumerate(s.get("screen_headlines", []), 1):
            lines.append(f"   [{h_i}] {h_text}")
        lines.append("")
        lines.append(f"🎙️ एंकर वॉइसओवर (VOICEOVER SCRIPT):")
        lines.append(f"   \"{s['voiceover_script']}\"")
        lines.append("")
        lines.append(f"🔍 चंक-दर-चंक विजुअल व मीम्स मैपिंग (100% ENGLISH SEARCH KEYWORDS):")
        for c in s.get("chunks", []):
            intent_icon = "🤣 [MEEM REACTION]" if c.get("visual_intent") == "MEME_REACTION" else "📸 [REAL PHOTO]"
            lines.append(f"   [{c.get('chunk_index', 0)}] {intent_icon} {c.get('sentence', '')}")
            if c.get("image_keywords_en"):
                lines.append(f"       🔎 Press Image Queries (EN): {', '.join(c.get('image_keywords_en', []))}")
            if c.get("meme_keyword_en"):
                lines.append(f"       🎭 Contextual Meme Query (EN): {c['meme_keyword_en']}")
        lines.append("=" * 84)
        lines.append("\n\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=None, help="अधिकतम खबरों की संख्या")
    args = parser.parse_args()
    generate_dls_bulletin(max_stories=args.max)


if __name__ == "__main__":
    main()
