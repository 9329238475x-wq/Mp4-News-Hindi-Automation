"""
Story Folder Metadata Helper
----------------------------
Saves all story artifacts directly into each story's folder (out/story_XX/):
1. story_XX_data.json: Complete raw and structured JSON with all keywords, headlines, news link, audio, and images.
2. script_XX.txt: Beautiful human-readable broadcast report with headlines, TTS voiceover script, English image search keywords, chunk-by-chunk visual mapping, and source attribution.
"""
import os
import json


def save_story_folder_metadata(story: dict, out_dir: str):
    """
    प्रत्येक खबर के फोल्डर (out/story_XX/) में उसका संपूर्ण डेटा सेव करना
    """
    s_num = story.get("story_number", 1)
    story_dir_name = f"story_{s_num:02d}"
    story_dir = os.path.join(out_dir, story_dir_name)
    os.makedirs(story_dir, exist_ok=True)

    # 1. story_XX_data.json सेव करना (100% संपूर्ण कच्चा व संरचित डेटा)
    json_path = os.path.join(story_dir, f"story_{s_num}_data.json")
    try:
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(story, jf, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"    ⚠️ [Metadata] story_{s_num}_data.json save error: {e}")

    # 2. script_XX.txt सेव करना (विस्तृत मानव-पठनीय रिपोर्ट)
    script_txt_path = os.path.join(story_dir, f"script_{s_num}.txt")
    lines = []
    lines.append("═" * 84)
    lines.append(f"📌 बुलेटिन खबर #{s_num:02d}: {story.get('screen_headline', '')}")
    source_name = story.get("real_image_attribution") or story.get("source") or "न्यूज़ डेस्क"
    pub_time = story.get("published_at") or "24 घंटे के भीतर"
    lines.append(f"📂 श्रेणी: {story.get('category', 'न्यूज़')} | स्रोत: {source_name} | समय: {pub_time}")
    if story.get("article_url"):
        lines.append(f"🔗 मूल समाचार लिंक (URL): {story.get('article_url')}")
    if story.get("original_title"):
        lines.append(f"📰 मूल समाचार शीर्षक: {story.get('original_title')}")
    lines.append("═" * 84)
    lines.append("")

    lines.append("📺 मुख्य स्क्रीन हेडलाइन (PRIMARY SCREEN HEADLINE):")
    lines.append(f"   ▶ {story.get('screen_headline', '')}")
    lines.append("")

    if story.get("screen_headlines"):
        lines.append("📺 स्क्रीन पर बदलने वाली हेडलाइंस (SEQUENTIAL SCREEN HEADLINES):")
        for h_i, h_text in enumerate(story.get("screen_headlines", []), 1):
            lines.append(f"   [{h_i}] {h_text}")
        lines.append("")

    lines.append("═" * 84)
    lines.append("🎙️ वॉइसओवर स्क्रिप्ट:")
    lines.append(story.get("voiceover_script", ""))
    lines.append("")
    lines.append("═" * 84)

    # All English image search queries
    all_kws = story.get("visual_keywords_en") or story.get("visual_keywords") or []
    if all_kws:
        lines.append("🔎 फोटो सर्च कीवर्ड्स (ENGLISH IMAGE SEARCH KEYWORDS FOR DUCKDUCKGO / WEB):")
        for k_i, kw in enumerate(all_kws, 1):
            lines.append(f"   [{k_i:02d}] {kw}")
        lines.append("")
        lines.append("═" * 84)

    # Chunks and visual mapping
    chunks = story.get("chunks", [])
    if chunks:
        lines.append("📸 चंक-दर-चंक विवरण (CHUNKS, SEARCH KEYWORDS & MAPPED PHOTOS):")
        for c in chunks:
            c_idx = c.get("chunk_index", 1)
            sent = c.get("sentence", "").replace("**", "")
            lines.append(f"   [चंक {c_idx}] 📸 {sent}")
            kws = c.get("image_keywords_en", [])
            if kws:
                lines.append(f"       🔎 Search Keywords : {', '.join(kws)}")
            if c.get("local_visual_path"):
                lines.append(f"       📁 Mapped Photo     : {c.get('local_visual_path')}")
            lines.append("")
        lines.append("═" * 84)

    # Downloaded images if present
    all_imgs = story.get("all_real_images", [])
    if all_imgs:
        lines.append(f"🌐 डाउनलोड की गई कुल {len(all_imgs)} असली तस्वीरों की सूची (REAL PHOTOS):")
        for im_i, im_p in enumerate(all_imgs, 1):
            lines.append(f"   [{im_i:02d}] {im_p}")
        lines.append("═" * 84)

    try:
        with open(script_txt_path, "w", encoding="utf-8") as sf:
            sf.write("\n".join(lines) + "\n")
    except Exception as e:
        print(f"    ⚠️ [Metadata] script_{s_num}.txt save error: {e}")
