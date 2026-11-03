"""
DLS News Visual Asset Downloader (100% Automated Autopilot Engine)
-----------------------------------------------------------------
1. 100% असली न्यूज़ फोटोज़ (Real News Photos) - वेब व प्रेस कवरेज से।
2. प्रति खबर 10 से 15 असली तस्वीरें स्वतः डाउनलोड करना।
3. स्मार्ट वॉटरमार्क क्रॉपिंग (Smart Watermark Cropping):
   - न्यूज़ साइट्स के बॉटम टिकर/लोगो स्ट्रिप (8-10%) को PIL से क्रॉप करके हटाना।
   - टॉप पब्लिशर बैनर स्ट्रिप को ट्रिम करना।
4. रेजोल्यूशन व क्वालिटी सत्यापन (PIL Verification).
5. ऑल-स्टोरीज़ ऑटोपायलट सपोर्ट (download_all_assets).
"""

import os
import sys
import json
import time
import re
import html
import requests
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(BASE_DIR, "out")
JSON_PATH = os.path.join(os.path.dirname(__file__), "generated_sample_top10.json")

os.makedirs(OUT_DIR, exist_ok=True)

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "hi,en-US;q=0.9,en;q=0.8",
}


COMMERCE_AND_SPAM_BLOCKLIST = [
    "vecteezy",
    "freepik",
    "istockphoto",
    "shutterstock",
    "dreamstime",
    "alamy",
    "amazon.",
    "flipkart.",
    "meesho.",
    "indiamart.",
    "aliexpress.",
    "shopify.",
    "myntra.",
    "nykaa.",
    "bigbasket.",
    "ebay.",
    "jpmorgan",
    "morgan",
    "chase",
    "streetfighter",
    "sf6",
    "clipart",
    "vector",
    "cartoon",
    "anime",
    "product",
    "shampoo",
    "hair-fall",
    "coaching",
    "combopack",
    "cleaning-products",
    "tile-cleaner",
    "soap",
    "courses",
    "admission",
    "books",
    "byjus",
    "vedantu",
    "unacademy",
    "doubtnut",
    "toppr",
    "brainly",
    "shaalaa",
    "cuemath",
    "testbook",
    "embibe",
    "careerpower",
    "careerlauncher",
    "sarthaks",
    "quora",
    "pinterest",
]


def search_web_real_images(query: str, is_meme: bool = False, max_results: int = 15) -> list[str]:
    """वेब से असली न्यूज़ व मीम तस्वीरों के डायरेक्ट लिंक खोजना (स्पैम व कॉमर्स फ़िल्टर्ड)"""
    clean_query = query.strip()
    if is_meme:
        search_term = clean_query if "meme" in clean_query.lower() else f"{clean_query} meme"
    else:
        # अगर क्वेरी छोटी है और 'news/rally' आदि नहीं है तो संदर्भ जोड़ें
        words = clean_query.split()
        if len(words) <= 2 and not any(w in clean_query.lower() for w in ["news", "rally", "speech", "police", "crime", "court", "bjp", "congress"]):
            search_term = f"{clean_query} news"
        else:
            search_term = clean_query

    encoded = requests.utils.quote(search_term)
    url = f"https://www.bing.com/images/search?q={encoded}&first=1"
    try:
        r = requests.get(url, headers=BROWSER_HEADERS, timeout=6)
        if r.status_code == 200:
            text = html.unescape(r.text)
            murls = re.findall(r'"murl":"(https?://[^"]+)"', text)
            if murls:
                filtered = []
                for u in murls:
                    u_lower = u.lower()
                    if not is_meme and any(bad in u_lower for bad in COMMERCE_AND_SPAM_BLOCKLIST):
                        continue
                    filtered.append(u)
                if filtered:
                    return filtered[:max_results]
    except Exception:
        pass

    try:
        from ddgs import DDGS
        with DDGS(timeout=6) as ddgs:
            results = list(ddgs.images(clean_query, max_results=max_results))
            raw_urls = [r.get("image") for r in results if r.get("image")]
            if not is_meme:
                return [u for u in raw_urls if not any(bad in u.lower() for bad in COMMERCE_AND_SPAM_BLOCKLIST)][:max_results]
            return raw_urls[:max_results]
    except Exception:
        pass

    return []


def crop_watermarks_smart(img: Image.Image, bottom_crop_ratio: float = 0.08, top_crop_ratio: float = 0.04) -> Image.Image:
    """
    स्मार्ट वॉटरमार्क & बैनर क्रॉपिंग:
    1. न्यूज़ पोर्टल्स (अमर उजाला, भास्कर, आज तक आदि) के निचले टिकर/लोगो/वॉटरमार्क को हटाना।
    2. ऊपरी पब्लिशर बैनर / टेक्स्ट स्ट्रिप्स (White headline banner) का स्वतः पता लगाकर क्रॉप करना।
    """
    w, h = img.size
    actual_top_crop = int(h * top_crop_ratio)

    try:
        import numpy as np
        arr = np.array(img)
        if arr.ndim >= 3:
            # 1. ऊपरी 35% हिस्से में पब्लिशर बैनर या टेक्स्ट स्ट्रिप (सफेद पट्टी) का सटीक पता लगाना
            top_limit = int(h * 0.35)
            last_banner_y = 0
            for y in range(top_limit):
                row = arr[y, :, :3]
                white_ratio = (row > 215).all(axis=-1).mean()
                if white_ratio > 0.45:
                    last_banner_y = y + 4

            if last_banner_y > 0:
                actual_top_crop = max(actual_top_crop, last_banner_y)
    except Exception:
        pass

    actual_bottom_crop = int(h * (1.0 - bottom_crop_ratio))

    # यदि तस्वीर पर्याप्त बड़ी है तभी क्रॉप करें
    if (actual_bottom_crop - actual_top_crop) >= 200:
        return img.crop((0, actual_top_crop, w, actual_bottom_crop))
    return img


def download_and_verify_image(img_url: str, dest_path: str, min_width: int = 380, min_height: int = 220, is_meme: bool = False) -> bool:
    """इमेज डाउनलोड, स्मार्ट वॉटरमार्क क्रॉपिंग और PIL सत्यापन"""
    if not img_url or not img_url.startswith("http"):
        return False

    try:
        req_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        }
        domain = img_url.split('/')[2] if len(img_url.split('/')) > 2 else ""
        if domain:
            req_headers["Referer"] = f"https://{domain}/"

        res = requests.get(img_url, headers=req_headers, timeout=10, stream=True)
        if res.status_code == 200:
            content = res.content
            if len(content) > 3000:
                img = Image.open(BytesIO(content))
                if img.width >= min_width and img.height >= min_height:
                    is_png = dest_path.lower().endswith(".png")
                    
                    if is_meme:
                        # पारदर्शी मीम के लिए अल्फा चैनल (Transparency) बनाए रखें
                        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                            img = img.convert("RGBA")
                            img.save(dest_path, "PNG")
                            return True
                        elif is_png:
                            img = img.convert("RGBA")
                            img.save(dest_path, "PNG")
                            return True
                        else:
                            if img.mode != "RGB":
                                img = img.convert("RGB")
                            img.save(dest_path, "JPEG", quality=92)
                            return True
                    else:
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        
                        # 🚫 सफेद बैकग्राउंड वाले डॉक्यूमेंट्स / होमवर्क शीट्स / टेक्स्टबुक्स को अस्वीकार करें
                        try:
                            import numpy as np
                            arr = np.array(img)
                            if arr.ndim >= 3:
                                white_pixels = (arr[:, :, 0] > 235) & (arr[:, :, 1] > 235) & (arr[:, :, 2] > 235)
                                white_ratio = white_pixels.mean()
                                if white_ratio > 0.50:
                                    # 50% से अधिक सफेद बैकग्राउंड = डॉक्यूमेंट/किताब/होमवर्क, न्यूज़ फोटो नहीं
                                    return False
                        except Exception:
                            pass

                        # ✂️ वॉटरमार्क और टिकर स्ट्रिप को क्रॉप करें (केवल असली न्यूज़ तस्वीरों पर)
                        clean_img = crop_watermarks_smart(img, bottom_crop_ratio=0.08, top_crop_ratio=0.02)
                        clean_img.save(dest_path, "JPEG", quality=92)
                        return True
    except Exception:
        pass
    return False


def fetch_10_to_15_images_for_story(story: dict, target_count: int = 12) -> list[str]:
    """
    एक खबर के लिए 10 से 15 असली तस्वीरें व 2-3 मीम्स डाउनलोड करना:
    - 100% ENGLISH SEARCH QUERIES ONLY
    - चंक-दर-चंक विजुअल सिंक (जो बोला जा रहा है वही इमेज)
    - आउटपुट फोल्डर: out/story_XX/news real image & out/story_XX/meems image
    - फ़ॉरवर्ड स्लैश (/) पाथ ताकि Linux / Kaggle / Remotion में 100% काम करे
    """
    story_num = story.get("story_number", 1)
    original_img_url = story.get("real_image_url")
    chunks = story.get("chunks", [])

    story_dir_name = f"story_{story_num:02d}"
    story_dir = os.path.join(OUT_DIR, story_dir_name)
    news_dir = os.path.join(story_dir, "news real image")
    meems_dir = os.path.join(story_dir, "meems image")
    os.makedirs(news_dir, exist_ok=True)
    os.makedirs(meems_dir, exist_ok=True)

    downloaded_real_images = []
    downloaded_memes = []
    seen_urls = set()

    # 1. यदि मूल न्यूज़ आर्टिकल की पहली ओरिजिनल फोटो उपलब्ध है
    primary_filename = f"news_img_{story_num}_01.jpg"
    primary_path = os.path.join(news_dir, primary_filename)
    root_primary_path = os.path.join(story_dir, primary_filename)
    rel_primary = f"out/{story_dir_name}/news real image/{primary_filename}"

    if original_img_url and original_img_url.startswith("http"):
        if download_and_verify_image(original_img_url, primary_path):
            downloaded_real_images.append(rel_primary)
            seen_urls.add(original_img_url)
            try:
                import shutil
                shutil.copyfile(primary_path, root_primary_path)
            except Exception:
                pass

    # 2. सर्च क्वेरीज़ तैयार करना (सरल, प्रभावी 2-4 शब्दों वाली क्वेरीज़)
    real_queries = []
    # चंक्स से कीवर्ड्स
    for c in chunks:
        for kw in c.get("image_keywords_en", []):
            if kw and len(kw.strip()) > 3:
                clean_kw = kw.strip()
                real_queries.append(clean_kw)
                # यदि कीवर्ड बहुत लंबा है (>4 शब्द), तो छोटे 2-3 शब्दों के वेरिएंट्स भी बनाएं
                words = clean_kw.split()
                if len(words) > 4:
                    real_queries.append(" ".join(words[:3]))
                    real_queries.append(" ".join(words[-3:]))

    for skw in story.get("visual_keywords_en", []) or story.get("visual_keywords", []):
        if skw and len(skw.strip()) > 3:
            real_queries.append(skw.strip())

    # सामान्य बैकअप क्वेरीज़
    headline = story.get("screen_headline", "")
    entities = re.findall(r"[A-Za-z0-9]+", headline)
    entity_str = " ".join(entities[:3]) if entities else "political rally crowd"
    real_queries.extend([
        f"{entity_str} speech",
        f"{entity_str} crowd",
        f"{entity_str} rally Bareilly",
        "BJP rally stage speech India",
        "BJP Bareilly rally crowd workers",
        "JP Nadda speech BJP rally",
        "Keshav Prasad Maurya UP speech",
        "BJP workers public meeting UP",
        "political rally crowd flags UP India"
    ])

    # विशिष्ट क्रम बनाए रखें और डुप्लिकेट्स हटाएं
    dedup_queries = []
    for q in real_queries:
        q_norm = q.lower().strip()
        if q_norm and q_norm not in [x.lower() for x in dedup_queries]:
            dedup_queries.append(q.strip())

    # 3. असली न्यूज़ फोटोज़ डाउनलोडिंग लूप (लक्ष्य: 10 से 14 तस्वीरें)
    target_news = max(12, target_count)
    for q in dedup_queries:
        if len(downloaded_real_images) >= target_news:
            break

        candidate_urls = search_web_real_images(q, is_meme=False, max_results=12)
        images_from_this_query = 0

        for u in candidate_urls:
            if len(downloaded_real_images) >= target_news:
                break
            if u in seen_urls:
                continue
            seen_urls.add(u)

            img_idx = len(downloaded_real_images) + 1
            filename = f"news_img_{story_num}_{img_idx:02d}.jpg"
            dest_path = os.path.join(news_dir, filename)
            rel_path = f"out/{story_dir_name}/news real image/{filename}"

            if download_and_verify_image(u, dest_path, min_width=350, min_height=200, is_meme=False):
                downloaded_real_images.append(rel_path)
                images_from_this_query += 1
                if img_idx == 1 and not os.path.exists(root_primary_path):
                    try:
                        import shutil
                        shutil.copyfile(dest_path, root_primary_path)
                    except Exception:
                        pass
                # प्रत्येक क्वेरी से अधिकतम 3 उच्च-गुणवत्ता वाली तस्वीरें
                if images_from_this_query >= 3:
                    break

        time.sleep(0.1)

    # 4. मीम डाउनलोडिंग (कम से कम 2-3 ट्रेंडिंग रिएक्शन मीम्स)
    meme_queries = []
    for c in chunks:
        if c.get("visual_intent") == "MEME_REACTION" and c.get("meme_keyword_en"):
            meme_queries.append(c.get("meme_keyword_en"))
    meme_queries.extend([
        "confused reaction meme transparent png",
        "shocked face meme transparent png",
        "thinking face meme transparent png",
        "laughing reaction meme transparent png",
    ])

    target_memes = 2
    for mq in meme_queries:
        if len(downloaded_memes) >= target_memes:
            break
        cand_memes = search_web_real_images(mq, is_meme=True, max_results=10)
        for mu in cand_memes:
            if len(downloaded_memes) >= target_memes:
                break
            if mu in seen_urls:
                continue
            seen_urls.add(mu)

            m_idx = len(downloaded_memes) + 1
            m_ext = ".png" if ".png" in mu.lower() else ".jpg"
            m_filename = f"meme_{story_num}_{m_idx:02d}{m_ext}"
            m_dest = os.path.join(meems_dir, m_filename)
            m_rel = f"out/{story_dir_name}/meems image/{m_filename}"

            if download_and_verify_image(mu, m_dest, min_width=200, min_height=150, is_meme=True):
                downloaded_memes.append(m_rel)
                break

    # 5. चंक-टू-इमेज सटीक मैपिंग
    meme_cursor = 0
    real_cursor = 0
    for c in chunks:
        if c.get("visual_intent") == "MEME_REACTION" and downloaded_memes:
            c["local_visual_path"] = downloaded_memes[meme_cursor % len(downloaded_memes)]
            meme_cursor += 1
        elif downloaded_real_images:
            c["local_visual_path"] = downloaded_real_images[real_cursor % len(downloaded_real_images)]
            real_cursor += 1

    return downloaded_real_images


def download_all_assets(max_stories: int = None, target_count: int = 12, force: bool = False):
    """
    ऑटोपायलट मास्टर कंट्रोलर:
    सभी खबरों के लिए 10-15 असली तस्वीरें ऑटोमैटिक डाउनलोड करना (वॉटरमार्क क्रॉप्ड)
    """
    if not os.path.exists(JSON_PATH):
        print(f"❌ एरर: बुलेटिन फाइल नहीं मिली: {JSON_PATH}")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        stories = json.load(f)

    if max_stories:
        target_stories = stories[:max_stories]
    else:
        target_stories = stories

    print("\n" + "═" * 78)
    print("🚀 DLS News Real Images Engine: 100% ऑटोपायलट असली न्यूज़ फोटोज़ डाउनलोडर")
    print(f"🎯 लक्ष्य: प्रति खबर {target_count} असली तस्वीरें | ऑटो वॉटरमार्क क्रॉपिंग")
    print("═" * 78)

    updated = False
    for idx, story in enumerate(target_stories, 1):
        num = story.get("story_number", idx)
        headline = story.get("screen_headline", "")[:50]
        print(f"\n▶️ [खबर {num:02d}] {headline}...")

        # यदि पहले से 10+ तस्वीरें हैं और force=False है, तो स्किप करें
        existing = story.get("all_real_images", [])
        valid_existing = [img for img in existing if os.path.exists(os.path.join(BASE_DIR, img))]
        if not force and len(valid_existing) >= target_count:
            print(f"  ✔ पहले से {len(valid_existing)} तस्वीरें मौजूद हैं, स्किप किया गया।")
            continue

        downloaded = fetch_10_to_15_images_for_story(story, target_count=target_count)
        if downloaded:
            norm_downloaded = [p.replace("\\", "/") for p in downloaded]
            story["local_news_image"] = norm_downloaded[0]
            story["local_visual_asset"] = norm_downloaded[0]
            story["all_real_images"] = norm_downloaded
            story["image_attribution_tag"] = f"स्रोत: असली प्रेस कवरेज / {story.get('real_image_attribution', 'न्यूज़ डेस्क')}"
            updated = True
            print(f"  🎉 खबर {num:02d} के लिए {len(norm_downloaded)} असली तस्वीरें डाउनलोड व क्रॉप हुईं!")
        else:
            print(f"  ⚠️ कोई नई फोटो नहीं मिली।")

        # 100% सुरक्षा: सुनिश्चित करें कि कोई भी चंक गायब फाइल की ओर संकेत न करे
        valid_local = [img.replace("\\", "/") for img in story.get("all_real_images", [])]
        fallback_img = valid_local[0] if valid_local else None
        for c in story.get("chunks", []):
            lvp = c.get("local_visual_path")
            if lvp:
                norm_lvp = lvp.replace("\\", "/")
                full_lvp = os.path.join(BASE_DIR, *norm_lvp.split("/"))
                if not os.path.exists(full_lvp):
                    c["local_visual_path"] = fallback_img
                else:
                    c["local_visual_path"] = norm_lvp
                updated = True

        time.sleep(0.3)

    if updated:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(stories, f, ensure_ascii=False, indent=2)

    print("\n" + "═" * 78)
    print("✅ सभी खबरों के लिए एसेट्स पूरी तरह तैयार हैं!")
    print("═" * 78 + "\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("count", nargs="?", type=int, default=None)
    parser.add_argument("--force", action="store_true", help="पहले से मौजूद इमेजेस को दोबारा डाउनलोड करें")
    args = parser.parse_args()
    download_all_assets(max_stories=args.count, target_count=12, force=args.force)
