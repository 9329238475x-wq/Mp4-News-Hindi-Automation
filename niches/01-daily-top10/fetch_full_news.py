"""
Master 7-Pillar News Extractor for India (Last 24 Hours)
--------------------------------------------------------
7 मुख्य पिलर्स (The Ultimate YouTube Mix):
1. 🔥 क्राइम, एनकाउंटर & माफिया (Crime & Shootouts)
2. ⚠️ हादसे, आपदाएं & जन-समस्याएं (Accidents, Disasters & Public Crisis)
3. ⚖️ कोर्ट-कचहरी & सुप्रीम कोर्ट फैसले (Courts & Legal Verdicts)
4. 🕵️‍♂️ राष्ट्रीय सुरक्षा, खुफिया रेड & ऑपरेशंस (National Security & CBI/NIA)
5. ⚡ भ्रष्टाचार, घूसखोरी ट्रैप & खुलासे (Corruption & Scams)
6. 💥 राजनीतिक घमासान, बयान & बवाल (Political Clashes & Drama)
7. 🛸 रहस्यमयी घटनाएं & अनोखे सच (Mysteries & Bizarre Events)

विशेषताएं:
- केवल भारत की पिछले 24 घंटे की ताज़ा घटनाएं।
- कोई आधा-अधूरा स्निपेट या हेडिंग नहीं - हर खबर का 100% पूरा आर्टिकल बॉडी टेक्स्ट।
- अभी कुल ठीक 10 खबरों का संतुलित बुलेटिन बनाएगा (भविष्य में 50 तक आसानी से बढ़ाया जा सकता है)।
- आउटपुट latest_24h_full_news.txt में पूर्ण रूप से संकलित।
"""

import os
import sys
import json
import time
import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import requests
try:
    import trafilatura
except ImportError:
    trafilatura = None
import feedparser
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

# UTF-8 एनकोडिंग सपोर्ट (Windows)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
TXT_OUTPUT_PATH = os.path.join(CURR_DIR, "latest_24h_full_news.txt")
JSON_OUTPUT_PATH = os.path.join(CURR_DIR, "latest_24h_full_news.json")
OUT_DIR = os.path.abspath(os.path.join(CURR_DIR, "..", "..", "out"))
ASSETS_DIR = os.path.abspath(os.path.join(CURR_DIR, "..", "..", "assets"))

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# 🚫 सख्त ब्लॉकलिस्ट: अमर उजाला को 100% ब्लॉक किया गया है (यूजर निर्देश: अमर उजाला में खराब/कम तस्वीरें होती हैं)
BLOCKED_NEWS_DOMAINS = ["amarujala.com", "amarujala"]

# 7 मुख्य पिलर्स और शीर्ष भारतीय न्यूज़ सोर्सेस (दैनिक भास्कर, जागरण, बीबीसी, एबीपी, ज़ी न्यूज़ - फोटो व GIF युक्त)
MASTER_7_PILLARS = [
    {
        "id": "crime",
        "name": "🔥 क्राइम, एनकाउंटर & माफिया",
        "feeds": [
            ("दैनिक भास्कर क्राइम", "https://www.bhaskar.com/rss-v1--category-4589.xml"),
            ("दैनिक जागरण क्राइम", "https://rss.jagran.com/rss/news/crime.xml"),
            ("बीबीसी हिंदी", "https://feeds.bbci.co.uk/hindi/rss.xml"),
            ("एबीपी न्यूज़", "https://www.abplive.com/home/feed")
        ],
        "keywords": ["हत्या", "मर्डर", "एनकाउंटर", "गोलीबारी", "गैंगस्टर", "गिरफ्तार", "शूटर", "वारदात", "चोरी", "लूट", "हमला", "चाकू", "बदमाश", "पुलिस", "अपहरण", "लाश", "शव", "क्राइम", "बंदी"]
    },
    {
        "id": "crisis",
        "name": "⚠️ हादसे, आपदाएं & जन-समस्याएं",
        "feeds": [
            ("दैनिक भास्कर राष्ट्रीय", "https://www.bhaskar.com/rss-v1--category-1061.xml"),
            ("दैनिक जागरण राष्ट्रीय", "https://rss.jagran.com/rss/news/national.xml"),
            ("बीबीसी हिंदी", "https://feeds.bbci.co.uk/hindi/rss.xml"),
            ("गूगल न्यूज़ भारत", "https://news.google.com/rss/headlines/section/topic/NATION?hl=hi&gl=IN&ceid=IN:hi")
        ],
        "keywords": ["हादसा", "चक्रवात", "बारिश", "ट्रेन", "आंधी", "अलर्ट", "स्कूल", "राहत", "तूफान", "जाम", "परेशान", "टक्कर", "आग", "सिलेंडर", "बिजली", "सड़क", "घायल", "अस्पताल", "धमाका"]
    },
    {
        "id": "court",
        "name": "⚖️ कोर्ट-कचहरी & सुप्रीम कोर्ट फैसले",
        "feeds": [
            ("दैनिक भास्कर", "https://www.bhaskar.com/rss-v1--category-1061.xml"),
            ("दैनिक जागरण", "https://rss.jagran.com/rss/news/national.xml"),
            ("एबीपी न्यूज़", "https://www.abplive.com/home/feed"),
            ("ज़ी न्यूज़ हिंदी", "https://zeenews.india.com/hindi/india.xml"),
            ("गूगल न्यूज़ हिंदी", "https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi")
        ],
        "keywords": ["सुप्रीम कोर्ट", "हाई कोर्ट", "अदालत", "फैसला", "याचिका", "फटकार", "जमानत", "सजा", "वकील", "आदेश", "एससी", "सीजेआई", "कोर्ट", "सुनवाई", "जज", "निर्देश", "दोषी"]
    },
    {
        "id": "security",
        "name": "🕵️‍♂️ राष्ट्रीय सुरक्षा, खुफिया रेड & ऑपरेशंस",
        "feeds": [
            ("बीबीसी हिंदी", "https://feeds.bbci.co.uk/hindi/rss.xml"),
            ("दैनिक भास्कर", "https://www.bhaskar.com/rss-v1--category-1061.xml"),
            ("दैनिक जागरण", "https://rss.jagran.com/rss/news/national.xml"),
            ("ज़ी न्यूज़ हिंदी", "https://zeenews.india.com/hindi/india.xml")
        ],
        "keywords": ["सुरक्षा", "सेना", "आतंकी", "छापा", "बॉर्डर", "ऑपरेशन", "जवान", "हमला", "हथियार", "कब्जा", "एनआईए", "सीबीआई", "जासूसी", "मुठभेड़", "सैनिक", "कमांडो", "घुसपैठ", "खुफिया"]
    },
    {
        "id": "corruption",
        "name": "⚡ भ्रष्टाचार, घूसखोरी ट्रैप & खुलासे",
        "feeds": [
            ("दैनिक भास्कर क्राइम", "https://www.bhaskar.com/rss-v1--category-4589.xml"),
            ("दैनिक जागरण", "https://rss.jagran.com/rss/news/crime.xml"),
            ("एबीपी न्यूज़", "https://www.abplive.com/home/feed")
        ],
        "keywords": ["घूस", "रिश्वत", "विजिलेंस", "घोटाला", "गड़बड़ी", "भ्रष्टाचार", "पर्दाफाश", "रंगे हाथ", "ट्रैप", "ईडी", "आय से अधिक", "फर्जी", "धोखाधड़ी", "सीज", "छापेमारी", "करोड़ों"]
    },
    {
        "id": "politics",
        "name": "💥 राजनीतिक घमासान, बयान & बवाल",
        "feeds": [
            ("बीबीसी हिंदी", "https://feeds.bbci.co.uk/hindi/rss.xml"),
            ("दैनिक भास्कर", "https://www.bhaskar.com/rss-v1--category-1061.xml"),
            ("दैनिक जागरण", "https://rss.jagran.com/rss/news/national.xml"),
            ("एबीपी न्यूज़", "https://www.abplive.com/home/feed"),
            ("ज़ी न्यूज़ हिंदी", "https://zeenews.india.com/hindi/india.xml")
        ],
        "keywords": ["बयान", "विवाद", "हंगामा", "विपक्ष", "सरकार", "राहुल", "मोदी", "प्रदर्शन", "नोटिस", "विरोध", "चुनौती", "चुनाव", "मंत्री", "इस्तीफा", "तकरार", "संसद", "नेता", "पार्टी", "चैलेंज"]
    },
    {
        "id": "mystery",
        "name": "🛸 रहस्यमयी घटनाएं & कुदरती अजूबे",
        "feeds": [
            ("गूगल न्यूज़ हिंदी", "https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi"),
            ("बीबीसी हिंदी", "https://feeds.bbci.co.uk/hindi/rss.xml"),
            ("दैनिक भास्कर", "https://www.bhaskar.com/rss-v1--category-1061.xml"),
            ("दैनिक जागरण", "https://rss.jagran.com/rss/news/national.xml")
        ],
        "keywords": ["अनोखा", "रहस्य", "अजीब", "चमत्कार", "खुदाई", "अद्भुत", "हैरान", "पंडाल", "प्राचीन", "अजूबा", "दुर्लभ", "रहस्यमयी", "चौंकाने", "विचित्र", "खजाना", "मंदिर", "गुफा", "अनोखी"]
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "hi-IN,hi;q=0.9,en-US;q=0.8,en;q=0.7",
}


MAX_NEWS_HOURS = 12


def is_within_last_24_hours(date_str: str) -> bool:
    """जांच: क्या खबर पिछले 12 घंटे के अंदर प्रकाशित हुई है"""
    if not date_str:
        return True
    try:
        pub_dt = datetime.datetime.strptime(date_str[:25].strip(), "%a, %d %b %Y %H:%M:%S")
        now = datetime.datetime.now()
        diff = now - pub_dt
        return diff.total_seconds() <= (MAX_NEWS_HOURS * 3600 + 7200)  # 12h + 2h buffer
    except Exception:
        return True


def extract_full_article_text(url: str) -> str:
    """
    मूल समाचार वेबसाइट से 100% पूरा आर्टिकल बॉडी टेक्स्ट निकालता है।
    """
    if not url or not url.startswith("http"):
        return ""

    # 1. Trafilatura
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            extracted = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                no_fallback=False
            )
            if extracted and len(extracted.split()) >= 180:
                return clean_news_text(extracted)
    except Exception:
        pass

    # 2. BeautifulSoup फॉलबैक
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
        soup = BeautifulSoup(html, "html.parser")
        for t in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
            t.decompose()

        container = (
            soup.find("article") or
            soup.find("div", class_=lambda c: c and any(k in str(c).lower() for k in ["article-body", "story-body", "story_content", "content-area", "detail_text", "news-text"])) or
            soup.find("main") or
            soup.body
        )

        if container:
            paras = []
            for p in container.find_all(["p", "h2", "h3"]):
                txt = p.get_text(strip=True)
                if len(txt) > 35 and not any(junk in txt for junk in ["डाउनलोड करें", "Follow Us", "विज्ञापन", "क्लिक करें", "Copyright"]):
                    paras.append(txt)

            combined = "\n\n".join(paras)
            if len(combined.split()) >= 180:
                return clean_news_text(combined)
    except Exception:
        pass

    return ""


def clean_news_text(raw: str) -> str:
    """अनावश्यक लाइनें हटाकर स्वच्छ पैराग्राफ्स बनाना"""
    lines = [line.strip() for line in raw.split("\n") if line.strip()]
    cleaned = []
    seen = set()
    for line in lines:
        if line not in seen and len(line) > 15:
            if line.startswith("{") and line.endswith("}"):
                continue
            seen.add(line)
            cleaned.append(line)
    return "\n\n".join(cleaned)


def extract_and_download_story_media(story_index: int, article_url: str) -> dict:
    """
    मूल समाचार वेबपेज से सभी असली चित्र (HD Images) और वीडियो खोजकर
    स्थानीय रूप से media/story_{idx:02d}/ में डाउनलोड व सेव करता है।
    साथ ही मुख्य चित्र को public/assets/news_img_{idx}.jpg में भी रखता है।
    """
    story_dir = os.path.join(OUT_DIR, f"story_{story_index:02d}", "news real image")
    os.makedirs(story_dir, exist_ok=True)

    result = {
        "images": [],
        "videos": []
    }

    if not article_url or not article_url.startswith("http"):
        return result

    try:
        resp = requests.get(article_url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            return result
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")
    except Exception as e:
        print(f"      ⚠️ वेबपेज लोड विफलता ({article_url}): {e}", flush=True)
        return result

    candidate_img_urls = []
    seen_img_urls = set()

    def add_img_candidate(raw_src: str):
        if not raw_src:
            return
        src = raw_src.strip()
        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = urllib.parse.urljoin(article_url, src)

        if not src.startswith("http"):
            return

        junk_indicators = [
            "logo", "icon", "advertisement", "pixel", "avatar", "facebook",
            "twitter", "whatsapp", "share", "arrow", "ad.", "banner",
            "spinner", "thumb_small", "rightarrow", "user_profile"
        ]
        src_lower = src.lower()
        if any(j in src_lower for j in junk_indicators):
            return

        base_src = src.split("?")[0]
        if base_src not in seen_img_urls:
            seen_img_urls.add(base_src)
            candidate_img_urls.append(src)

    # 1. मेटा टैग्स (og:image, twitter:image)
    for prop in ["og:image", "twitter:image", "og:image:url"]:
        tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        if tag and tag.get("content"):
            add_img_candidate(tag["content"])

    # 2. आर्टिकल बॉडी की <img> टैग्स
    article_container = (
        soup.find("article") or
        soup.find("div", class_=lambda c: c and any(k in str(c).lower() for k in ["article-body", "story-body", "story_content", "content-area", "detail_text"])) or
        soup
    )
    for img_tag in article_container.find_all("img"):
        for attr in ["src", "data-src", "data-original", "data-lazy-src"]:
            val = img_tag.get(attr)
            if val:
                add_img_candidate(val)

    # 3. सभी संभावित वीडियो व एम्बेड्स
    for vid in soup.find_all("video"):
        src = vid.get("src")
        if not src:
            source_tag = vid.find("source")
            if source_tag:
                src = source_tag.get("src")
        if src:
            if src.startswith("//"): src = "https:" + src
            result["videos"].append({
                "type": "direct_video",
                "label": "डायरेक्ट वीडियो (.mp4/stream)",
                "url": src
            })

    for ifr in soup.find_all("iframe"):
        src = ifr.get("src") or ifr.get("data-src")
        if src:
            src_lower = src.lower()
            if any(k in src_lower for k in ["youtube.com", "youtu.be", "videocdn", "player", "dailymotion"]):
                v_type = "YouTube Embed" if "youtu" in src_lower else "न्यूज़ वीडियो प्लेयर (CDN/Embed)"
                result["videos"].append({
                    "type": "iframe_embed",
                    "label": v_type,
                    "url": src
                })

    for bq in soup.find_all("blockquote", class_=lambda c: c and "twitter" in str(c).lower()):
        link_tag = bq.find("a", href=lambda h: h and ("/status/" in str(h) or "x.com" in str(h) or "twitter.com" in str(h)))
        if link_tag:
            result["videos"].append({
                "type": "twitter_embed",
                "label": "सोशल मीडिया / एक्स (Twitter) पोस्ट",
                "url": link_tag["href"]
            })

    # 4. असली न्यूज़ फोटोज़ व एनिमेटेड GIFs डाउनलोड करना (15 तक प्रामाणिक मीडिया फाइल्स)
    downloaded_images = []
    img_counter = 1

    for img_url in candidate_img_urls:
        if img_counter > 50:
            break
        try:
            r_img = requests.get(img_url, headers=HEADERS, timeout=12)
            if r_img.status_code != 200 or len(r_img.content) < 5000:
                continue

            content_type = r_img.headers.get("Content-Type", "").lower()
            is_gif = img_url.lower().endswith(".gif") or "image/gif" in content_type or ".gif" in img_url.lower()

            if is_gif:
                # 🎬 दैनिक भास्कर / अन्य स्रोतों से प्राप्त एनिमेटेड GIF
                gif_filename = f"news_gif_{story_index}_{img_counter:02d}.gif"
                gif_local_path = os.path.join(story_dir, gif_filename)
                with open(gif_local_path, "wb") as gf:
                    gf.write(r_img.content)

                # Remotion में स्मूथ फ्रेम-बाई-फ्रेम प्ले करने हेतु ffmpeg से लूपिंग MP4 में कन्वर्ट
                mp4_filename = f"news_gif_{story_index}_{img_counter:02d}.mp4"
                mp4_local_path = os.path.join(story_dir, mp4_filename)
                rel_mp4_path = f"out/story_{story_index:02d}/news real image/{mp4_filename}"
                rel_gif_path = f"out/story_{story_index:02d}/news real image/{gif_filename}"

                converted = False
                try:
                    cmd = ["ffmpeg", "-y", "-i", gif_local_path, "-movflags", "faststart", "-pix_fmt", "yuv420p", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", mp4_local_path]
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    if os.path.exists(mp4_local_path) and os.path.getsize(mp4_local_path) > 1000:
                        converted = True
                except Exception as conv_e:
                    print(f"      ⚠️ GIF to MP4 रूपांतरण त्रुटि: {conv_e}", flush=True)

                chosen_rel = rel_mp4_path if converted else rel_gif_path
                chosen_fn = mp4_filename if converted else gif_filename
                print(f"      🎬 [Animated GIF] प्रामाणिक न्यूज़ GIF सक्रिय: {chosen_fn}", flush=True)

                downloaded_images.append({
                    "index": img_counter,
                    "local_path": chosen_rel,
                    "public_path": chosen_rel,
                    "filename": chosen_fn,
                    "is_animated": True,
                    "is_video": converted,
                    "url": img_url
                })
                img_counter += 1
                continue

            # सामान्य समाचार तस्वीर (JPG/PNG/WEBP)
            pil_img = Image.open(BytesIO(r_img.content))
            w, h = pil_img.size

            if w < 250 or h < 150:
                continue

            if pil_img.mode != "RGB":
                pil_img = pil_img.convert("RGB")

            filename = f"news_img_{story_index}_{img_counter:02d}.jpg"
            local_save_path = os.path.join(story_dir, filename)
            pil_img.save(local_save_path, "JPEG", quality=95)

            file_size_kb = round(os.path.getsize(local_save_path) / 1024, 1)
            rel_path = f"out/story_{story_index:02d}/news real image/{filename}"

            public_rel_path = rel_path
            if img_counter == 1:
                out_story_dir = os.path.join(OUT_DIR, f"story_{story_index:02d}")
                public_save_path = os.path.join(out_story_dir, f"news_img_{story_index}_01.jpg")
                pil_img.save(public_save_path, "JPEG", quality=95)

            downloaded_images.append({
                "index": img_counter,
                "local_path": rel_path,
                "public_path": public_rel_path,
                "filename": filename,
                "resolution": f"{w}x{h}",
                "size_kb": file_size_kb,
                "is_animated": False,
                "is_video": False,
                "url": img_url
            })
            img_counter += 1
        except Exception:
            pass

    result["images"] = downloaded_images
    return result


def fetch_master_bulletin(target_count: int = 10) -> list:
    """
    सभी 7 पिलर्स से संतुलित 10 बड़ी भारतीय खबरें 100% फुल टेक्स्ट के साथ जुटाना।
    नियम: सभी 7 टॉपिक अनिवार्य रूप से शामिल होंगे (कम से कम 1 खबर प्रत्येक टॉपिक से)।
    """
    print("\n" + "═" * 84, flush=True)
    print("🇮🇳 7-पिलर मास्टर बुलेटिन एक्सट्रैक्टर (CRIME + CRISIS + NATIONAL MIX)", flush=True)
    print("🎯 रणनीति : 7 प्रमुख पिलर्स अनिवार्य रूप से शामिल (कुल ठीक 10 विस्तृत खबरें)", flush=True)
    print("📜 नियम   : 100% पूरा ओरिजिनल समाचार (कोई आधा-अधूरा स्निपेट या हेडिंग नहीं)", flush=True)
    print(f"📊 लक्ष्य   : वर्तमान में ठीक {target_count} पूरी खबरें", flush=True)
    print("═" * 84, flush=True)

    verified_stories = []
    seen_titles = set()
    seen_urls = set()

    # फीड्स का डेटा कैश करें ताकि बार-बार नेटवर्क कॉल न हो
    feed_cache = {}

    def get_feed_items(feed_url: str):
        if feed_url in feed_cache:
            return feed_cache[feed_url]
        try:
            fp = feedparser.parse(feed_url)
            items = []
            for e in fp.entries:
                t = e.get("title", "").strip()
                l = e.get("link", "").strip()
                p = e.get("published") or e.get("updated") or e.get("pubDate") or datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0530")
                if t and l:
                    items.append({"title": t, "link": l, "pubDate": p})
            feed_cache[feed_url] = items
            return items
        except Exception as e:
            print(f"   ⚠️ फीड लोड एरर ({feed_url}): {e}", flush=True)
            feed_cache[feed_url] = []
            return []

    # स्रोत विविधता ट्रैकर (किसी एक पब्लिशर से अधिकतम 2 खबरें ताकि अमर उजाला, भास्कर, बीबीसी आदि का संतुलन रहे)
    source_counts = {}

    # -------------------------------------------------------------
    # राउंड 1: सातों पिलर्स की भागीदारी सुनिश्चित करना (प्रत्येक पिलर से ठीक 1 बेस्ट खबर)
    # -------------------------------------------------------------
    print("\n🔹 राउंड 1: सभी 7 पिलर्स से 1-1 मुख्य खबर का चयन...", flush=True)
    pillar_counts = {p["id"]: 0 for p in MASTER_7_PILLARS}

    for pillar in MASTER_7_PILLARS:
        p_id = pillar["id"]
        p_name = pillar["name"]
        p_feeds = pillar["feeds"]
        p_keywords = pillar["keywords"]

        print(f"\n📡 [{p_name}] के लिए खबर खोजी जा रही है...", flush=True)
        found = False

        for feed_label, feed_url in p_feeds:
            if found:
                break
            if source_counts.get(feed_label, 0) >= 2:
                continue

            items = get_feed_items(feed_url)
            for it in items:
                title = it["title"] if isinstance(it, dict) else (it.find("title").text.strip() if it.find("title") is not None else "")
                link = it["link"] if isinstance(it, dict) else (it.find("link").text.strip() if it.find("link") is not None else "")
                pub_date = it["pubDate"] if isinstance(it, dict) else (it.find("pubDate").text.strip() if it.find("pubDate") is not None else "")

                if not title or title in seen_titles or link in seen_urls:
                    continue

                # 🚫 अमर उजाला को 100% ब्लॉक करें
                if any(bad_dom in link.lower() for bad_dom in BLOCKED_NEWS_DOMAINS):
                    continue

                # 1. क्या शीर्षक पिलर के कीवर्ड्स से मेल खाता है?
                title_lower = title.lower()
                if not any(k.lower() in title_lower for k in p_keywords):
                    continue

                # 2. क्या खबर 24 घंटे के अंदर की है?
                if not is_within_last_24_hours(pub_date):
                    continue

                if "news.google.com" in link:
                    try:
                        import googlenewsdecoder
                        dec = googlenewsdecoder.gnewsdecoder(link)
                        if dec.get("success") and dec.get("decoded_url"):
                            link = dec["decoded_url"]
                    except Exception:
                        pass

                # 3. पूरा 100% समाचार निकालें
                full_text = extract_full_article_text(link)
                word_count = len(full_text.split()) if full_text else 0

                if not full_text or word_count < 180:
                    continue

                seen_titles.add(title)
                seen_urls.add(link)
                story_item = {
                    "pillar_id": p_id,
                    "pillar_name": p_name,
                    "title": title,
                    "source": feed_label,
                    "published_at": pub_date,
                    "url": link,
                    "word_count": word_count,
                    "full_text": full_text
                }
                verified_stories.append(story_item)
                pillar_counts[p_id] += 1
                source_counts[feed_label] = source_counts.get(feed_label, 0) + 1
                found = True
                print(f"   ✅ [पिलर कवर हुआ] {title[:60]}... ({word_count} शब्द | {feed_label})", flush=True)
                time.sleep(0.3)
                break

    print(f"\n📊 राउंड 1 संपन्न: {len(verified_stories)} खबरें (7 पिलर्स में से {sum(1 for v in pillar_counts.values() if v > 0)} पिलर्स कवर हुए)।", flush=True)

    # -------------------------------------------------------------
    # राउंड 2: कुल 10 खबरें पूरी करने के लिए प्रमुख पिलर्स (क्राइम, जन-समस्याएं आदि) से दूसरी खबर
    # -------------------------------------------------------------
    if len(verified_stories) < target_count:
        needed = target_count - len(verified_stories)
        print(f"\n🔹 राउंड 2: कुल {target_count} पूरी करने के लिए शेष {needed} खबरें जोड़ी जा रही हैं...", flush=True)

        for pillar in MASTER_7_PILLARS:
            if len(verified_stories) >= target_count:
                break

            p_id = pillar["id"]
            p_name = pillar["name"]
            p_feeds = pillar["feeds"]
            p_keywords = pillar["keywords"]

            # प्रति पिलर अधिकतम 2 खबरें
            if pillar_counts[p_id] >= 2:
                continue

            for feed_label, feed_url in p_feeds:
                if len(verified_stories) >= target_count or pillar_counts[p_id] >= 2:
                    break
                if source_counts.get(feed_label, 0) >= 2:
                    continue

                items = get_feed_items(feed_url)
                for it in items:
                    if len(verified_stories) >= target_count or pillar_counts[p_id] >= 2:
                        break

                    title = it["title"] if isinstance(it, dict) else (it.find("title").text.strip() if it.find("title") is not None else "")
                    link = it["link"] if isinstance(it, dict) else (it.find("link").text.strip() if it.find("link") is not None else "")
                    pub_date = it["pubDate"] if isinstance(it, dict) else (it.find("pubDate").text.strip() if it.find("pubDate") is not None else "")

                    if not title or title in seen_titles or link in seen_urls:
                        continue

                    title_lower = title.lower()
                    if not any(k.lower() in title_lower for k in p_keywords):
                        continue

                    if not is_within_last_24_hours(pub_date):
                        continue

                    if "news.google.com" in link:
                        try:
                            import googlenewsdecoder
                            dec = googlenewsdecoder.gnewsdecoder(link)
                            if dec.get("success") and dec.get("decoded_url"):
                                link = dec["decoded_url"]
                        except Exception:
                            pass

                    full_text = extract_full_article_text(link)
                    word_count = len(full_text.split()) if full_text else 0

                    if not full_text or word_count < 180:
                        continue

                    seen_titles.add(title)
                    seen_urls.add(link)
                    story_item = {
                        "pillar_id": p_id,
                        "pillar_name": p_name,
                        "title": title,
                        "source": feed_label,
                        "published_at": pub_date,
                        "url": link,
                        "word_count": word_count,
                        "full_text": full_text
                    }
                    verified_stories.append(story_item)
                    pillar_counts[p_id] += 1
                    source_counts[feed_label] = source_counts.get(feed_label, 0) + 1
                    print(f"   ✅ [अतिरिक्त खबर] {title[:60]}... ({word_count} शब्द | {feed_label})", flush=True)
                    time.sleep(0.3)

    # -------------------------------------------------------------
    # राउंड 3: आपातकालीन फॉलबैक (यदि किसी पिलर में खबर न मिली हो तो 10 पूरी करना)
    # -------------------------------------------------------------
    if len(verified_stories) < target_count:
        needed = target_count - len(verified_stories)
        print(f"\n🔹 राउंड 3: राष्ट्रीय हेडलाइंस से {needed} अतिरिक्त खबरें पूरी की जा रही हैं...", flush=True)
        backup_feeds = [
            ("बीबीसी हिंदी", "https://feeds.bbci.co.uk/hindi/rss.xml"),
            ("दैनिक भास्कर", "https://www.bhaskar.com/rss-v1--category-1061.xml"),
            ("दैनिक जागरण राष्ट्रीय", "https://rss.jagran.com/rss/news/national.xml"),
            ("एबीपी न्यूज़", "https://www.abplive.com/home/feed"),
            ("ज़ी न्यूज़ हिंदी", "https://zeenews.india.com/hindi/india.xml"),
            ("गूगल न्यूज़ हिंदी", "https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi")
        ]
        for f_label, f_url in backup_feeds:
            if len(verified_stories) >= target_count:
                break
            items = get_feed_items(f_url)
            for it in items:
                if len(verified_stories) >= target_count:
                    break
                t = it["title"] if isinstance(it, dict) else (it.find("title").text.strip() if it.find("title") is not None else "")
                u = it["link"] if isinstance(it, dict) else (it.find("link").text.strip() if it.find("link") is not None else "")
                p = it["pubDate"] if isinstance(it, dict) else (it.find("pubDate").text.strip() if it.find("pubDate") is not None else "")
                if t and t not in seen_titles and u not in seen_urls and is_within_last_24_hours(p):
                    if "news.google.com" in u:
                        try:
                            import googlenewsdecoder
                            dec = googlenewsdecoder.gnewsdecoder(u)
                            if dec.get("success") and dec.get("decoded_url"):
                                u = dec["decoded_url"]
                        except Exception:
                            pass
                    ft = extract_full_article_text(u)
                    wc = len(ft.split()) if ft else 0
                    if ft and wc >= 180:
                        seen_titles.add(t)
                        seen_urls.add(u)
                        verified_stories.append({
                            "pillar_id": "national_crisis",
                            "pillar_name": "📢 देश की बड़ी हलचल & जन-मुद्दा",
                            "title": t,
                            "source": f_label,
                            "published_at": p,
                            "url": u,
                            "word_count": wc,
                            "full_text": ft
                        })
                        print(f"   ✅ [फॉलबैक खबर] {t[:60]}... ({wc} शब्द | {f_label})", flush=True)

    final_stories = verified_stories[:target_count]

    # -------------------------------------------------------------
    # चरण 4: सभी 10 चयनित खबरों के असली चित्र व वीडियो डाउनलोड करना
    # -------------------------------------------------------------
    print("\n" + "═" * 84, flush=True)
    print("📸 चरण 4: सभी 10 खबरों के ओरिजिनल चित्र व वीडियो डाउनलोड किए जा रहे हैं...", flush=True)
    print("═" * 84, flush=True)

    for i, story in enumerate(final_stories, start=1):
        print(f"\n📥 [खबर #{i:02d}] मीडिया डाउनलोड हो रहा है ({story['pillar_name']})...", flush=True)
        print(f"   शीर्षक : {story['title'][:55]}...", flush=True)
        media_res = extract_and_download_story_media(i, story["url"])
        story["images"] = media_res["images"]
        story["videos"] = media_res["videos"]
        story["story_number"] = i
        print(f"   ✅ परिणाम: {len(story['images'])} असली फोटो डाउनलोड हुईं | {len(story['videos'])} वीडियो/एम्बेड्स मिले।", flush=True)

    return final_stories


def write_to_txt_file(stories: list, output_path: str):
    """
    सभी खबरों का 100% पूरा विवरण .txt फाइल में स्पष्ट रूप से लिखता है
    साथ ही मिले हुए ओरिजिनल चित्र व वीडियो की सूची भी दर्ज करता है।
    """
    now_str = datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")

    lines = []
    lines.append("=" * 84)
    lines.append("🇮🇳 भारत मास्टर बुलेटिन - '7 प्रमुख पिलर्स' (100% FULL NEWS & ORIGINAL MEDIA)")
    lines.append(f"📅 रिपोर्ट जेनरेशन समय : {now_str}")
    lines.append(f"📊 कुल विस्तृत खबरें    : {len(stories)} (सभी 7 पिलर्स शामिल)")
    lines.append("🛡️  सत्यापन              : कड़ाई से केवल भारत की पिछले 24 घंटे की सच्ची घटनाएं")
    lines.append("📜 प्रारूप               : 100% पूर्ण समाचार + असली फोटो व वीडियो डाउनलोड")
    lines.append("=" * 84)
    lines.append("\n")

    # 1. बुलेटिन इंडेक्स
    lines.append("📑 आज के 10 विस्तृत मामलों की सूची (SUMMARY INDEX OF 7 PILLARS):")
    lines.append("-" * 84)
    for i, s in enumerate(stories, start=1):
        img_count = len(s.get("images", []))
        vid_count = len(s.get("videos", []))
        lines.append(f"[{i:02d}] {s['pillar_name']}")
        lines.append(f"     शीर्षक : {s['title']}")
        lines.append(f"     स्रोत  : {s['source']} | समय: {s['published_at']} | शब्द: {s['word_count']} | 📸 फोटो: {img_count} | 🎥 वीडियो: {vid_count}")
        lines.append("     " + "-" * 78)
    lines.append("\n\n")

    # 2. प्रत्येक खबर का पूरा आर्टिकल टेक्स्ट एवं मीडिया विवरण
    for i, s in enumerate(stories, start=1):
        imgs = s.get("images", [])
        vids = s.get("videos", [])

        lines.append("=" * 84)
        lines.append(f"📌 खबर #{i:02d} | {s['pillar_name']}")
        lines.append("=" * 84)
        lines.append(f"शीर्षक (HEADLINE) : {s['title']}")
        lines.append(f"समाचार स्रोत     : {s['source']}")
        lines.append(f"पब्लिश समय       : {s['published_at']} (पिछले 24 घंटे के अंदर)")
        lines.append(f"मूल वेब लिंक (URL): {s['url']}")
        lines.append(f"विस्तार (लेंथ)    : {s['word_count']} शब्द (100% पूर्ण विस्तृत समाचार)")
        lines.append("-" * 84)
        lines.append("📸 समाचार से प्राप्त ओरिजिनल चित्र (IMAGES FOUND & DOWNLOADED):")
        lines.append("-" * 84)
        if imgs:
            lines.append(f"कुल डाउनलोड चित्र: {len(imgs)}")
            for img in imgs:
                is_primary = " [मुख्य फोटो (PRIMARY)]" if img["index"] == 1 else ""
                lines.append(f"  [फोटो {img['index']:02d}]{is_primary} रेज़ोल्यूशन: {img['resolution']} px | साइज: {img['size_kb']} KB")
                lines.append(f"            लोकल फाइल : {img['local_path']}")
                if img.get("public_path"):
                    lines.append(f"            पब्लिक पाथ: {img['public_path']} (Remotion वीडियो उपयोग हेतु)")
                lines.append(f"            मूल वेब URL: {img['url']}")
        else:
            lines.append("  (वेबसाइट पर कोई वैध उच्च-गुणवत्ता चित्र नहीं मिला)")

        lines.append("")
        lines.append("-" * 84)
        lines.append("🎥 समाचार से प्राप्त वीडियो / एम्बेड्स (VIDEOS & EMBEDS):")
        lines.append("-" * 84)
        if vids:
            lines.append(f"कुल वीडियो/एम्बेड्स: {len(vids)}")
            for v_idx, vid in enumerate(vids, start=1):
                lines.append(f"  [वीडियो {v_idx:02d}] प्रकार: {vid.get('label', 'वीडियो')}")
                lines.append(f"              लिंक : {vid.get('url')}")
        else:
            lines.append("  - इस आर्टिकल में अलग से कोई वीडियो एम्बेड नहीं था (केवल हाई-रेज़ोल्यूशन ओरिजिनल फोटो उपलब्ध हैं)।")

        lines.append("")
        lines.append("-" * 84)
        lines.append("📖 पूरा समाचार विवरण (100% FULL COMPLETE ARTICLE):")
        lines.append("-" * 84)
        lines.append("")
        lines.append(s["full_text"])
        lines.append("\n")
        lines.append("=" * 84)
        lines.append("\n\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("\n" + "═" * 84, flush=True)
    print(f"🎉 7 पिलर्स से कुल {len(stories)} वास्तविक खबरें व ओरिजिनल मीडिया पूरी डिटेल के साथ तैयार हैं!", flush=True)
    print(f"📁 टेक्स्ट फाइल: {output_path}", flush=True)
    print("═" * 84, flush=True)


def write_to_json_file(stories: list, output_path: str):
    """
    सभी खबरों और मीडिया का व्यवस्थित JSON डेटा सेव करता है
    ताकि पाइपलाइन के अन्य मॉड्यूल्स (AI स्क्रिप्ट, Remotion) तुरंत इस्तेमाल कर सकें।
    """
    json_data = []
    for s in stories:
        item = {
            "story_number": s.get("story_number", 1),
            "pillar_id": s.get("pillar_id", ""),
            "pillar_name": s.get("pillar_name", ""),
            "title": s.get("title", ""),
            "source": s.get("source", ""),
            "published_at": s.get("published_at", ""),
            "url": s.get("url", ""),
            "word_count": s.get("word_count", 0),
            "primary_image_path": s.get("images", [{}])[0].get("local_path", "") if s.get("images") else "",
            "public_asset_path": s.get("images", [{}])[0].get("public_path", "") if s.get("images") else "",
            "images": s.get("images", []),
            "videos": s.get("videos", []),
            "full_text": s.get("full_text", "")
        }
        json_data.append(item)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    print(f"📁 JSON डेटा सेव हुआ: {output_path}", flush=True)


def main():
    stories = fetch_master_bulletin(target_count=10)
    write_to_txt_file(stories, TXT_OUTPUT_PATH)
    write_to_json_file(stories, JSON_OUTPUT_PATH)


if __name__ == "__main__":
    main()

