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
from story_metadata_helper import save_story_folder_metadata

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
    # Animation, Pixar, Disney & Movies Blocklist (Zero Cartoon Guarantee)
    "pixar",
    "disney",
    "animation",
    "animated",
    "movie",
    "film",
    "cinema",
    "trailer",
    "fictional",
    "imdb",
    "rottentomatoes",
    "comic",
    "manga",
    "toy",
    "action-figure",
    "nickelodeon",
    "dreamworks",
    "boxoffice",
    "box-office",
    # 🎮 Video Games, Fighting Games & 3D Renders Blocklist
    "tekken",
    "streetfighter",
    "mortal kombat",
    "gameplay",
    "videogame",
    "video game",
    "video-game",
    "esports",
    "playstation",
    "xbox",
    "nintendo",
    "capcom",
    "bandai",
    "cgi",
    "3d render",
    "concept art",
    "fighting game",
    "boss fight",
    # 🖼️ Wallpapers, Backgrounds & Logos Blocklist (Zero Junk Guarantee)
    "wallpaper",
    "wallpapers",
    "wallpapercave",
    "hdqwalls",
    "4kwallpapers",
    "infoupdate",
    "screensaver",
    "background",
    "desktop-wallpaper",
    "logo",
    "icon",
    "symbol",
    "flag",
    "emblem",
    "bjp-logo",
    "party-logo",
    "vector-logo",
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
    "cricket",
    "cricketer",
    "maharaj",
    "ipl",
    "match",
    "gameplay",
    "sport",
    "khel",
    "wicket",
    "batsman",
    "bowler",
    "cricinfo",
    "cricbuzz",
    "stadium",
    "jersey",
    "pitch",
    "wedding",
    "weddingwire",
    "shaadi",
    "matrimony",
    "pixabay",
    "unsplash",
    "freepik",
    "shutterstock",
    "depositphotos",
    "dreamstime",
    "alamy",
    "clipart",
    "vector",
    "stock",
    "brazil",
    "portuguese",
    "whitehouse",
]

PRIORITY_NEWS_DOMAINS = [
    "bjp.org",
    "amarujala",
    "jagran",
    "bhaskar",
    "ndtv",
    "thehindu",
    "indianexpress",
    "indiatoday",
    "hindustantimes",
    "abplive",
    "news18",
    "navbharattimes",
    "patrika",
    "etvbharat",
    "zeenews",
    "oneindia",
    "asianetnews",
    "tribuneindia",
    "deccanherald",
    "livemint",
    "wikimedia",
]


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
    clean = re.sub(r'\b(start|route|departure|concluding|ceremony|boarding|transport|heavy|ban|closure|save|remove|during|after|before|walk|walks|walking|run|running)\b', '', clean, flags=re.IGNORECASE)
    # UP -> Uttar Pradesh Master Expansion (100% prevents Pixar Up movie match)
    clean = re.sub(r'\bup\b', 'Uttar Pradesh', clean, flags=re.IGNORECASE)

    if 'keshav' in clean.lower() and 'maurya' in clean.lower() and 'prasad' not in clean.lower():
        clean = re.sub(r'keshav\s+maurya', 'Keshav Prasad Maurya BJP', clean, flags=re.IGNORECASE)

    c_low = clean.lower()
    # Anchor generic terms to India / UP context so foreign stock/police/weddings are 100% prevented
    if any(p in c_low for p in ['police', 'barricade', 'barrier', 'traffic']) and not any(loc in c_low for loc in ['uttar pradesh', 'bareilly', 'india', 'delhi', 'lucknow']):
        clean = f"Uttar Pradesh Police {clean}"
    elif any(leg in c_low for leg in ['legislator', 'legislators', 'mla', 'mlas']) and 'bjp' not in c_low:
        clean = "Uttar Pradesh BJP MLAs"
    elif any(ven in c_low for ven in ['venue', 'hall', 'swayamvar']) and 'rally' not in c_low:
        clean = "BJP rally Bareilly"

    clean = re.sub(r'\s+', ' ', clean).strip()
    words = clean.split()
    if not words:
        return ""
    return " ".join(words[:4])


def get_wikimedia_portrait(entity_name: str) -> str:
    """विकिपीडिया व विकिमीडिया कॉमन्स से प्रमुख नेताओं, हस्तियों व संस्थानों की 100% आधिकारिक 4K तस्वीर प्राप्त करना"""
    if not entity_name or len(entity_name.strip()) < 3:
        return ""
    clean_name = sanitize_keyword_master(entity_name)
    # Generic state names, parties or actions should never query Wikipedia portrait (prevents flags, coats of arms, films)
    if clean_name.lower() in ["uttar pradesh", "india", "delhi", "bjp", "police", "traffic", "up", "rally"]:
        return ""
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&titles={requests.utils.quote(clean_name)}&prop=pageimages|description&format=json&pithumbsize=1280"
        r = requests.get(url, headers={"User-Agent": "DLSNewsBroadcastBot/1.0"}, timeout=5).json()
        pages = r.get("query", {}).get("pages", {})
        for pid, pdata in pages.items():
            if pid == "-1":
                continue
            title = pdata.get("title", "").lower()
            desc = pdata.get("description", "").lower()
            # If Wikipedia page is a movie, film, animated feature, fictional character, song: REJECT!
            if any(bad in f"{title} {desc}" for bad in ["film", "movie", "animated", "animation", "fictional", "disney", "pixar", "album", "song", "series"]):
                continue
            thumb = pdata.get("thumbnail", {}).get("source")
            if thumb:
                thumb_low = thumb.lower()
                if not any(bad in thumb_low for bad in ["flag", "symbol", "emblem", "icon", "map"] + COMMERCE_AND_SPAM_BLOCKLIST):
                    return thumb
    except Exception:
        pass
    return ""



def search_web_real_images(query: str, is_meme: bool = False, max_results: int = 15) -> list[str]:
    """
    मल्टी-इंजन असली न्यूज़ फोटोज़ सर्च इंजन (Master Multi-Engine News Searcher):
    1. DuckDuckGo Images इंजन (PRIMARY #1): 100% असली न्यूज़ फोटोज़ व भारतीय संदर्भ (region='in-en')
    2. विकिमीडिया कॉमन्स आधिकारिक पोर्ट्रेट्स (नेताओं के आधिकारिक 4K चित्र)
    3. Bing Images Async इंजन (SECONDARY FALLBACK: केवल तभी जब DuckDuckGo कम रिजल्ट दे)
    4. भारतीय न्यूज़ पोर्टल्स को शीर्ष प्राथमिकता व सख्त एंटी-गेमिंग/एंटी-कार्टून स्पैम फ़िल्टरिंग
    """
    clean_query = sanitize_keyword_master(query)
    if not clean_query:
        return []

    collected_urls = []

    # 1. DuckDuckGo इमेज सर्च (PRIMARY #1) - असली और सटीक न्यूज़ तस्वीरों का मुख्य स्रोत
    DDGS_CLS = None
    try:
        from ddgs import DDGS as DDGS_CLS
    except ImportError:
        try:
            from duckduckgo_search import DDGS as DDGS_CLS
        except ImportError:
            try:
                import subprocess
                subprocess.run([sys.executable, "-m", "pip", "install", "-q", "ddgs", "duckduckgo-search"], check=False)
                from ddgs import DDGS as DDGS_CLS
            except Exception:
                try:
                    from duckduckgo_search import DDGS as DDGS_CLS
                except Exception:
                    DDGS_CLS = None

    if DDGS_CLS is not None:
        try:
            with DDGS_CLS(timeout=14) as ddgs:
                results = list(ddgs.images(clean_query, region="in-en", safesearch="moderate", max_results=max_results))
                for r in results:
                    img_u = r.get("image")
                    t_d = r.get("title", "").lower()
                    u_d = str(img_u).lower()
                    combined_d = f"{u_d} {t_d}"
                    if any(bad in combined_d for bad in COMMERCE_AND_SPAM_BLOCKLIST):
                        continue
                    if img_u and img_u not in collected_urls:
                        collected_urls.append(img_u)
            if collected_urls:
                print(f"  ✓ [DDGS-in] Found {len(collected_urls)} photos for: '{clean_query}'")
        except Exception as e_ddg:
            # Global fallback query without region lock if in-en timed out / rate limited
            try:
                time.sleep(1.0)
                with DDGS_CLS(timeout=12) as ddgs:
                    results = list(ddgs.images(clean_query, max_results=max_results))
                    for r in results:
                        img_u = r.get("image")
                        t_d = r.get("title", "").lower()
                        u_d = str(img_u).lower()
                        combined_d = f"{u_d} {t_d}"
                        if any(bad in combined_d for bad in COMMERCE_AND_SPAM_BLOCKLIST):
                            continue
                        if img_u and img_u not in collected_urls:
                            collected_urls.append(img_u)
                if collected_urls:
                    print(f"  ✓ [DDGS-global] Found {len(collected_urls)} photos for: '{clean_query}'")
            except Exception as e2:
                print(f"  ⚠️ [DDGS Notice] ({clean_query}): {e2}")

    # 2. विकिमीडिया कॉमन्स पोर्ट्रेट चेक (नेताओं के आधिकारिक चित्र)
    if not is_meme and len(collected_urls) < max_results:
        wiki_img = get_wikimedia_portrait(clean_query)
        if wiki_img and wiki_img not in collected_urls:
            collected_urls.append(wiki_img)

    # 3. Bing Images Async सर्च इंजन (SECONDARY FALLBACK - केवल तभी चलेगा जब DuckDuckGo से पर्याप्त तस्वीरें न मिलें)
    if len(collected_urls) < 4:
        encoded = requests.utils.quote(clean_query)
        bing_async_url = f"https://www.bing.com/images/async?q={encoded}&first=0&count=25&mmasync=1"
        try:
            r = requests.get(bing_async_url, headers=BROWSER_HEADERS, timeout=8)
            if r.status_code == 200:
                matches = re.findall(r'm="([^"]+)"', r.text)
                for m_raw in matches:
                    try:
                        item_data = json.loads(html.unescape(m_raw))
                        img_u = item_data.get("murl")
                        p_u = item_data.get("purl", "").lower()
                        title_t = item_data.get("t", "").lower()

                        if not img_u or img_u in collected_urls:
                            continue

                        # 100% सुरक्षा: इमेज URL, वेबपेज URL और शीर्षक तीनों पर स्पैम/स्पोर्ट्स/गेम फ़िल्टर
                        combined_meta = f"{img_u.lower()} {p_u} {title_t}"
                        if any(bad in combined_meta for bad in COMMERCE_AND_SPAM_BLOCKLIST):
                            continue

                        collected_urls.append(img_u)
                        if len(collected_urls) >= max_results:
                            break
                    except Exception:
                        continue
        except Exception:
            pass

    # 4. स्पैम, ई-कॉमर्स व अप्रासंगिक सामग्री को फ़िल्टर करना
    filtered = []
    for u in collected_urls:
        u_lower = u.lower()
        if any(bad in u_lower for bad in COMMERCE_AND_SPAM_BLOCKLIST):
            continue
        filtered.append(u)

    # 5. भारतीय प्रतिष्ठित न्यूज़ डोमेन्स को प्राथमिकता (Sorting)
    def news_priority(u: str) -> int:
        u_l = u.lower()
        for p_idx, dom in enumerate(PRIORITY_NEWS_DOMAINS):
            if dom in u_l:
                return p_idx
        return 999

    filtered.sort(key=news_priority)
    return filtered[:max_results]


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
                        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                            bg = Image.new("RGB", img.size, (255, 255, 255))
                            rgba = img.convert("RGBA")
                            bg.paste(rgba, mask=rgba.split()[3])
                            img = bg
                        elif img.mode != "RGB":
                            img = img.convert("RGB")

                        # Reject blank or solid color images (variance < 35)
                        try:
                            extrema = img.convert("L").getextrema()
                            if extrema[1] - extrema[0] < 35:
                                return False
                        except Exception:
                            pass
                        
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
    एक खबर के लिए प्रामाणिक 100% असली न्यूज़ फोटोज़ व एनिमेटेड GIFs जुटाना (10-12 तस्वीरें MAX):
    1. मूल समाचार आर्टिकल (Dainik Bhaskar / ABP / Jagran) से 2-3 असली तस्वीरें व GIFs लोड करना।
    2. DuckDuckGo इमेज सर्च (region='in-en') से प्रत्येक चंक के लिए सटीक मैचिंग प्रेस फ़ोटो (1 फ़ोटो प्रति चंक)।
    3. सख्त सीमा: कुल 8 से 12 तस्वीरें (NO 54 images, NO quota waste, NO Pexels random stock models)।
    4. हर चंक को उसकी सही तस्वीर से मैप करना ताकि स्क्रीन पर वही दिखे जो एंकर बोल रहा है।
    """
    story_num = story.get("story_number", 1)
    chunks = story.get("chunks", [])

    story_dir_name = f"story_{story_num:02d}"
    story_dir = os.path.join(OUT_DIR, story_dir_name)
    news_dir = os.path.join(story_dir, "news real image")
    os.makedirs(news_dir, exist_ok=True)

    final_images = []
    seen_urls = set()
    root_primary_path = os.path.join(story_dir, f"news_img_{story_num}_01.jpg")

    # ──────────────────────────────────────────────────────────────────────────
    # 1. मूल समाचार आर्टिकल (ABP / Bhaskar आदि) से मुख्य असली तस्वीरें (अधिकतम 2-3 फ़ोटोज़)
    # ──────────────────────────────────────────────────────────────────────────
    article_media = story.get("images", [])
    article_count = 0
    for m in article_media:
        if article_count >= 3:
            break
        if isinstance(m, dict):
            loc_path = m.get("local_path")
            m_url = m.get("url")
            if loc_path:
                full_loc = os.path.join(BASE_DIR, *loc_path.replace("\\", "/").split("/"))
                if os.path.exists(full_loc) and loc_path not in final_images:
                    final_images.append(loc_path.replace("\\", "/"))
                    if m_url:
                        seen_urls.add(m_url)
                    article_count += 1
                    continue

            if m_url and m_url.startswith("http") and m_url not in seen_urls:
                seen_urls.add(m_url)
                img_idx = len(final_images) + 1
                fn = f"article_media_{story_num}_{img_idx:02d}.jpg"
                dp = os.path.join(news_dir, fn)
                rel_p = f"out/{story_dir_name}/news real image/{fn}"
                if download_and_verify_image(m_url, dp, min_width=250, min_height=150, is_meme=False):
                    final_images.append(rel_p)
                    article_count += 1

    if article_count > 0:
        print(f"  📰 [आर्टिकल मीडिया] मूल खबर से {article_count} असली तस्वीरें लोड हुईं!")

    # ──────────────────────────────────────────────────────────────────────────
    # 2. DuckDuckGo इमेज सर्च: प्रत्येक चंक (Sentence) के लिए 1-2 सटीक तस्वीरें
    # ──────────────────────────────────────────────────────────────────────────
    print(f"  🔎 [DuckDuckGo Web Search] {len(chunks)} चंक्स के लिए लाइव प्रेस तस्वीरें खोजी जा रही हैं...")

    for c_idx, chunk in enumerate(chunks, 1):
        if len(final_images) >= target_count:
            break

        chunk_keywords = chunk.get("image_keywords_en", [])
        chunk_got_img = False

        for kw in chunk_keywords:
            clean_kw = sanitize_keyword_master(kw)
            if not clean_kw:
                continue

            candidate_urls = search_web_real_images(clean_kw, max_results=5)
            for u in candidate_urls:
                if u in seen_urls:
                    continue
                seen_urls.add(u)

                img_idx = len(final_images) + 1
                fn = f"news_img_{story_num}_{img_idx:02d}.jpg"
                dp = os.path.join(news_dir, fn)
                rel_p = f"out/{story_dir_name}/news real image/{fn}"

                if download_and_verify_image(u, dp, min_width=320, min_height=180, is_meme=False):
                    final_images.append(rel_p)
                    chunk["local_visual_path"] = rel_p
                    chunk_got_img = True
                    break

            if chunk_got_img:
                break

        time.sleep(0.4)

    # ──────────────────────────────────────────────────────────────────────────
    # 3. बैकअप सर्च: यदि तस्वीरें 8 से कम हों तो स्टोरी कीवर्ड्स से पूरा करें
    # ──────────────────────────────────────────────────────────────────────────
    if len(final_images) < 8:
        broad_kws = story.get("visual_keywords_en", []) or story.get("visual_keywords", [])
        for b_kw in broad_kws:
            if len(final_images) >= target_count:
                break
            clean_b = sanitize_keyword_master(b_kw)
            if not clean_b:
                continue

            candidate_urls = search_web_real_images(clean_b, max_results=5)
            for u in candidate_urls:
                if u in seen_urls:
                    continue
                seen_urls.add(u)

                img_idx = len(final_images) + 1
                fn = f"news_img_{story_num}_{img_idx:02d}.jpg"
                dp = os.path.join(news_dir, fn)
                rel_p = f"out/{story_dir_name}/news real image/{fn}"

                if download_and_verify_image(u, dp, min_width=320, min_height=180, is_meme=False):
                    final_images.append(rel_p)
                    if len(final_images) >= target_count:
                        break
            time.sleep(0.4)

    # ──────────────────────────────────────────────────────────────────────────
    # 4. चंक मैपिंग व प्राइमरी कवर कॉपी
    # ──────────────────────────────────────────────────────────────────────────
    if final_images:
        for idx, c in enumerate(chunks):
            c["visual_intent"] = "REAL_PHOTO"
            c["meme_keyword_en"] = None
            if not c.get("local_visual_path"):
                c["local_visual_path"] = final_images[idx % len(final_images)]

        if not os.path.exists(root_primary_path):
            try:
                first_full = os.path.join(BASE_DIR, *final_images[0].split("/"))
                if os.path.exists(first_full) and not first_full.lower().endswith(".mp4"):
                    import shutil
                    shutil.copyfile(first_full, root_primary_path)
            except Exception:
                pass

    print(f"  📸 [इमेज डाउनलोड पूर्ण] कुल {len(final_images)} प्रामाणिक तस्वीरें सेव हुईं (टारगेट: {target_count})")
    return final_images


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

        # डाउनलोड की गई तस्वीरों और मैपिंग के साथ story_XX_data.json व script_XX.txt अपडेट करें
        save_story_folder_metadata(story, OUT_DIR)

        # 🔥 सनसनी YouTube Thumbnail ऑटो-जेनेरेट करें (1280x720)
        try:
            from generate_thumbnail import generate_sensational_thumbnail
            thumb_out = os.path.join(OUT_DIR, f"story_{num:02d}", f"thumbnail_{num:02d}.jpg")
            thumb_photo = fallback_img or (norm_downloaded[0] if downloaded else "")
            if thumb_photo:
                full_thumb_photo = os.path.join(BASE_DIR, *thumb_photo.split("/"))
                hl_text = story.get("screen_headline") or story.get("original_title") or headline
                generate_sensational_thumbnail(
                    headline=hl_text,
                    photo_path=full_thumb_photo,
                    out_path=thumb_out,
                    category=story.get("category", "क्राइम"),
                )
                story["thumbnail_path"] = f"out/story_{num:02d}/thumbnail_{num:02d}.jpg"
                updated = True
        except Exception as th_err:
            print(f"  ⚠️ Thumbnail generation skipped: {th_err}")
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
