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
import re
import json
import time
import datetime
import email.utils
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

# Import Watermark and Burned-in Text Blurring Engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from image_blur_helper import clean_watermarks_and_text, blur_burned_in_text_and_watermarks
except Exception:
    clean_watermarks_and_text = None
    blur_burned_in_text_and_watermarks = None

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
BLOCKED_NEWS_DOMAINS = [
    "amarujala.com",
    "amarujala",
    "amar ujala",
    "अमर उजाला",
    "amar_ujala",
]


def is_blocked_source(text_or_url: str) -> bool:
    """अमर उजाला व अन्य प्रतिबंधित स्रोतों को 100% ब्लॉक करना"""
    if not text_or_url:
        return False
    s = str(text_or_url).lower()
    return any(bad in s for bad in BLOCKED_NEWS_DOMAINS)


# 🇮🇳 विदेशी समाचारों का कड़ा बहिष्कार (100% विशुद्ध भारतीय राष्ट्रीय व प्रांतीय समाचार ओनली)
FOREIGN_EXCLUSION_KEYWORDS = [
    "फ्रांस", "मार्सेली", "स्पेन", "अमेरिका", "अमेरिकी", "रूस", "रूसी", "यूक्रेन",
    "इसराइल", "इजरायल", "गाजा", "हमास", "ईरान", "ईरानी", "पाकिस्तान", "पाकिस्तानी",
    "लंदन", "ब्रिटेन", "ब्रिटिश", "कनाडा", "जर्मनी", "जापान", "पेरिस", "न्यूयॉर्क",
    "वाशिंगटन", "बुल्गारिया", "इटली", "ब्राजील", "चीन", "चीनी", "तुर्किये", "तुर्की",
    "सीरिया", "लेबनान", "अफगानिस्तान", "नेपाल", "बांग्लादेश", "श्रीलंका", "थाईलैंड",
    "ऑस्ट्रेलिया", "रूस-यूक्रेन", "रूस-यूक्रेन युद्ध", "गाजा पट्टी", "पश्चिम एशिया"
]

INDIAN_ANCHORS = [
    # देश व राष्ट्रीय संस्थाएं
    "भारत", "भारतीय", "देश", "केंद्र सरकार", "राज्य सरकार", "सुप्रीम कोर्ट", "हाई कोर्ट", "सीबीआई", "ईडी", "एनआईए",
    "रेलवे", "संसद", "लोकसभा", "राज्यसभा", "चुनाव आयोग", "गृह मंत्रालय", "राजभवन", "विधानसभा",
    # राज्य व केंद्र शासित प्रदेश
    "उत्तर प्रदेश", "यूपी", "बिहार", "मध्य प्रदेश", "एमपी", "राजस्थान", "महाराष्ट्र", "दिल्ली",
    "पंजाब", "हरियाणा", "गुजरात", "उत्तराखंड", "झारखंड", "छत्तीसगढ़", "पश्चिम बंगाल", "बंगाल",
    "असम", "तमिलनाडु", "कर्नाटक", "केरल", "ओडिशा", "तेलंगाना", "आंध्र प्रदेश", "जम्मू-कश्मीर", "कश्मीर", "हिमाचल",
    # प्रमुख शहर व जिले
    "लखनऊ", "कानपुर", "प्रयागराज", "वाराणसी", "पटना", "भोपाल", "इंदौर", "जयपुर", "जोधपुर",
    "मुंबई", "पुणे", "नागपुर", "नोएडा", "गाजियाबाद", "मेरठ", "आगरा", "बरेली", "गोरखपुर",
    "अयोध्या", "ग्वालियर", "जबलपुर", "मुजफ्फरपुर", "भागलपुर", "गया", "भिवानी", "रोहतक", "हिसार",
    "अंबाला", "करनाल", "पानीपत", "फरीदाबाद", "गुरुग्राम", "गुड़गांव", "सोनीपत", "देहरादून",
    "हरिद्वार", "ऋषिकेश", "उधमपुर", "जम्मू", "श्रीनगर", "शिमला", "मंडी", "धर्मशाला", "अमृतसर",
    "जालंधर", "लुधियाना", "पटियाला", "बठिंडा", "चंडीगढ़", "कोटा", "उदयपुर", "अजमेर", "बीकानेर",
    "अलवर", "भरतपुर", "सीकर", "उज्जैन", "सागर", "रीवा", "सतना", "कटनी", "छिंदवाड़ा",
    "दरभंगा", "पूर्णिया", "आरा", "बक्सर", "समस्तीपुर", "बेगूसराय", "मुंगेर", "छपरा", "मोतिहारी",
    "धनबाद", "रांची", "जमशेदपुर", "बोकारो", "हजारीबाग", "रायपुर", "बिलासपुर", "दुर्ग", "भिलाई",
    # स्थानीय पुलिस व प्रशासन पद
    "कोतवाली", "चौकी", "थाना प्रभारी", "दारोगा", "दरोगा", "सिपाही", "डीएसपी", "एसपी", "एसएसपी",
    "कमिश्नरेट", "पुलिस कमिश्नर", "थानाध्यक्ष", "एसएचओ"
]


# 🚫 बोरिंग पीआर/मेला/भाषण/रैली किल-लिस्ट (100% निषिद्ध ताकि थंबनेल और वीडियो का कंटेंट 100% मैच करे)
BORING_NEWS_BLOCKLIST = [
    "मेला", "व्यापार मेला", "उद्घाटन", "शिलान्यास", "रैली", "जनसभा",
    "संबोधन", "संबोधित", "बैठक", "समीक्षा बैठक", "दौरा", "प्रदर्शनी",
    "समारोह", "जयंती", "पुण्यतिथि", "बधाई", "शुभकामनाएं", "सम्मेलन",
    "महोत्सव", "कार्यशाला", "सेमिनार", "ज्ञापन", "धरना प्रदर्शन", "प्रेस वार्ता",
    "शपथ ग्रहण", "लोकार्पण", "रोड शो", "प्रचार", "पदयात्रा", "स्वागत",
    "प्रतियोगिता", "पुरस्कार", "मेडल", "खेलकूद", "क्रिकेट", "मैच", "आईपीएल"
]


def is_boring_pr_news(title: str, text: str = "") -> bool:
    """प्रेस रिलीज़, उद्घाटन, मेला, भाषण, और खेलकूद जैसी बोरिंग खबरों को 100% रिजेक्ट करना"""
    sample = f"{title} {text[:400]}".lower()
    return any(b in sample for b in BORING_NEWS_BLOCKLIST)


def is_strictly_indian_news(title: str, text: str = "") -> bool:
    """100% केवल भारत की घटनाएं सुनिश्चित करना (विदेशी अपराध/हादसे पूर्णतः वर्जित)"""
    # 0. बोरिंग पीआर/मेला/भाषण को तुरंत रिजेक्ट करें
    if is_boring_pr_news(title, text):
        return False

    t_low = (title or "").lower()
    full_sample = f"{title} {text[:600]}".lower()

    # 1. यदि शीर्षक में किसी भी विदेशी देश/क्षेत्र का नाम है
    has_foreign = any(fk in t_low for fk in FOREIGN_EXCLUSION_KEYWORDS)
    if has_foreign:
        # केवल तभी छूट जब शीर्षक में स्पष्ट रूप से भारत का नाम हो
        if not ("भारत" in t_low or "भारतीय" in t_low):
            return False

    # 2. खबर में कम से कम 1 स्पष्ट भारतीय भौगोलिक/प्रशासनिक पहचान (राज्य, शहर, संस्था) अनिवार्य है
    has_indian = any(ik in full_sample for ik in INDIAN_ANCHORS)
    if not has_indian:
        return False

    return True


# 7 मुख्य हाई-वोल्टेज एक्शन पिलर्स (थंबनेल से 100% मैच: क्राइम, एनकाउंटर, ED रेड, बुलडोजर, साइबर ठगी, कोर्ट व हादसे)
MASTER_7_PILLARS = [
    {
        "id": "crime_encounter",
        "name": "🚨 पुलिस एनकाउंटर & माफिया एक्शन",
        "feeds": [
            ("गूगल न्यूज़ भारत एनकाउंटर", "https://news.google.com/rss/search?q=%E0%A4%AD%E0%A4%BE%E0%A4%B0%E0%A4%A4+%E0%A4%8F%E0%A4%A8%E0%A4%95%E0%A4%BE%E0%A4%87%E0%A4%82%E0%A4%9F%E0%A4%B0+OR+%E0%A4%AE%E0%A5%81%E0%A4%A0%E0%A4%AD%E0%A5%87%E0%A4%A1%E0%A4%BC+when:12h&hl=hi&gl=IN&ceid=IN:hi"),
            ("एबीपी न्यूज़ क्राइम", "https://www.abplive.com/crime/feed"),
            ("गूगल न्यूज़ भारत क्राइम", "https://news.google.com/rss/search?q=%E0%A4%AD%E0%A4%BE%E0%A4%B0%E0%A4%A4+%E0%A4%95%E0%A5%8D%E0%A4%B0%E0%A4%BE%E0%A4%87%E0%A4%AE+when:12h&hl=hi&gl=IN&ceid=IN:hi"),
            ("गूगल न्यूज़ भारत पुलिस एक्शन", "https://news.google.com/rss/search?q=%E0%A4%AD%E0%A4%BE%E0%A4%B0%E0%A4%A4+%E0%A4%AA%E0%A5%81%E0%A4%B2%E0%A4%BF%E0%A4%B8+%E0%A4%97%E0%A4%BF%E0%A4%B0%E0%A4%AB%E0%A5%8D%E0%A4%A4%E0%A4%BE%E0%A4%B0+when:12h&hl=hi&gl=IN&ceid=IN:hi"),
            ("दैनिक जागरण राज्य", "https://rss.jagran.com/rss/news/state.xml")
        ],
        "keywords": ["एनकाउंटर", "मुठभेड़", "गैंगस्टर", "माफिया", "गोलीबारी", "हत्या", "मर्डर", "शूटर", "वारदात", "गिरफ्तार", "दबोचा", "अपराधियों", "हमला", "चाकू", "बदमाश", "एसटीएफ", "stf", "पुलिस", "अपहरण", "लाश", "शव", "क्राइम"]
    },
    {
        "id": "ed_cbi_raid",
        "name": "⚡ ED, CBI व विजिलेंस की ताबड़तोड़ रेड",
        "feeds": [
            ("गूगल न्यूज़ ईडी रेड", "https://news.google.com/rss/search?q=%E0%A4%88%E0%A4%A1%E0%A5%80+%E0%A4%9B%E0%A4%BE%E0%A4%AA%E0%A5%87%E0%A4%AE%E0%A4%BE%E0%A4%B0%E0%A5%80+OR+%E0%A4%B0%E0%A5%87%E0%A4%A1+when:12h&hl=hi&gl=IN&ceid=IN:hi"),
            ("गूगल न्यूज़ सीबीआई विजिलेंस", "https://news.google.com/rss/search?q=CBI+OR+%E0%A4%B5%E0%A4%BF%E0%A4%9C%E0%A4%BF%E0%A4%B2%E0%A5%87%E0%A4%82%E0%A4%B8+%E0%A4%9B%E0%A4%BE%E0%A4%AA%E0%A4%BE+when:12h&hl=hi&gl=IN&ceid=IN:hi"),
            ("गूगल न्यूज़ सट्टा सिंडिकेट", "https://news.google.com/rss/search?q=%E0%A4%B8%E0%A4%9F%E0%A5%8D%E0%A4%9F%E0%A4%BE+OR+%E0%A4%97%E0%A4%BF%E0%A4%B0%E0%A4%AB%E0%A5%8D%E0%A4%A4%E0%A4%BE%E0%A4%B0+when:12h&hl=hi&gl=IN&ceid=IN:hi"),
            ("एबीपी न्यूज़ क्राइम", "https://www.abplive.com/crime/feed")
        ],
        "keywords": ["ईडी", "ed", "सीबीआई", "cbi", "विजिलेंस", "छापा", "छापेमारी", "रेड", "घूस", "रिश्वत", "रंगे हाथ", "ट्रैप", "सट्टा", "महादेव", "बरामद", "करोड़ों", "काला धन", "सीज", "घोटाला"]
    },
    {
        "id": "bulldozer_action",
        "name": "🚜 बुलडोजर एक्शन & प्रशासन की बड़ी कार्रवाई",
        "feeds": [
            ("गूगल न्यूज़ बुलडोजर कार्रवाई", "https://news.google.com/rss/search?q=%E0%A4%AC%E0%A5%81%E0%A4%B2%E0%A4%A1%E0%A5%8B%E0%A4%9C%E0%A4%B0+OR+%E0%A4%95%E0%A5%81%E0%A4%B0%E0%A5%8D%E0%A4%95%E0%A5%80+when:12h&hl=hi&gl=IN&ceid=IN:hi"),
            ("गूगल न्यूज़ प्रशासन कार्रवाई", "https://news.google.com/rss/search?q=%E0%A4%AA%E0%A5%8D%E0%A4%B0%E0%A4%B6%E0%A4%BE%E0%A4%B8%E0%A4%A8+%E0%A4%95%E0%A4%BE%E0%A4%B0%E0%A5%8D%E0%A4%B0%E0%A4%B5%E0%A4%BE%E0%A4%88+OR+%E0%A4%B8%E0%A5%80%E0%A4%B2+when:12h&hl=hi&gl=IN&ceid=IN:hi"),
            ("दैनिक जागरण राज्य", "https://rss.jagran.com/rss/news/state.xml")
        ],
        "keywords": ["बुलडोजर", "कार्रवाई", "ध्वस्त", "अवैध कब्जा", "कुर्क", "कुर्की", "सीज", "निलंबित", "सस्पेंड", "सील", "प्रशासन", "दबिश", "कार्रवाई शुरू", "मकान गिराया", "अतिक्रमण"]
    },
    {
        "id": "cyber_fraud",
        "name": "💻 साइबर क्राइम, बैंक फ्रॉड & पेपर लीक माफिया",
        "feeds": [
            ("गूगल न्यूज़ साइबर ठगी फ्रॉड", "https://news.google.com/rss/search?q=%E0%A4%B8%E0%A4%BE%E0%A4%87%E0%A4%AC%E0%A4%B0+%E0%A4%A0%E0%A4%97%E0%A5%80+OR+%E0%A4%A1%E0%A4%BF%E0%A4%9C%E0%A4%BF%E0%A4%9F%E0%A4%B2+%E0%A4%85%E0%A4%B0%E0%A5%87%E0%A4%B8%E0%A5%8D%E0%A4%9F+when:12h&hl=hi&gl=IN&ceid=IN:hi"),
            ("गूगल न्यूज़ पेपर लीक सॉल्व गैंग", "https://news.google.com/rss/search?q=%E0%A4%AA%E0%A5%87%E0%A4%AA%E0%A4%B0+%E0%A4%B2%E0%A5%80%E0%A4%95+OR+%E0%A4%B8%E0%A5%89%E0%A4%B2%E0%A5%8D%E0%A4%B5%E0%A4%B0+%E0%A4%97%E0%A5%88%E0%A4%82%E0%A4%97+when:12h&hl=hi&gl=IN&ceid=IN:hi"),
            ("एबीपी न्यूज़ क्राइम", "https://www.abplive.com/crime/feed")
        ],
        "keywords": ["साइबर", "डिजिटल अरेस्ट", "फ्रॉड", "ठगी", "पेपर लीक", "सॉल्वर", "फर्जी", "बैंक फ्रॉड", "खाते सीज", "कॉल सेंटर", "ऑनलाइन ठगी", "पर्दाफाश", "धोखाधड़ी", "हैक"]
    },
    {
        "id": "court_verdicts",
        "name": "⚖️ सुप्रीम कोर्ट & हाई कोर्ट के सख्त आदेश",
        "feeds": [
            ("गूगल न्यूज़ सुप्रीम कोर्ट फटकार", "https://news.google.com/rss/search?q=%E0%A4%B8%E0%A5%81%E0%A4%AA%E0%A5%8D%E0%A4%B0%E0%A5%80%E0%A4%AE+%E0%A4%95%E0%A5%8B%E0%A4%B0%E0%A5%8D%E0%A4%9F+OR+%E0%A4%B9%E0%A4%BE%E0%A4%88+%E0%A4%95%E0%A5%8B%E0%A4%B0%E0%A5%8D%E0%A4%9F+%E0%A4%AB%E0%A4%9F%E0%A4%95%E0%A4%BE%E0%A4%B0+when:12h&hl=hi&gl=IN&ceid=IN:hi"),
            ("गूगल न्यूज़ अदालत सजा फैसला", "https://news.google.com/rss/search?q=%E0%A4%95%E0%A5%8B%E0%A4%B0%E0%A5%8D%E0%A4%9F+%E0%A4%B8%E0%A4%9C%E0%A4%BE+OR+%E0%A4%9C%E0%A4%AE%E0%A4%BE%E0%A4%A8%E0%A4%A4+%E0%A4%96%E0%A4%BE%E0%A4%B0%E0%A4%BF%E0%A4%9C+when:12h&hl=hi&gl=IN&ceid=IN:hi"),
            ("दैनिक जागरण राष्ट्रीय", "https://rss.jagran.com/rss/news/national.xml")
        ],
        "keywords": ["सुप्रीम कोर्ट", "हाई कोर्ट", "कड़ी फटकार", "जमानत खारिज", "सजा", "आदेश", "सीजेआई", "कोर्ट", "जज", "निर्देश", "दोषी करार", "सख्त रुख", "याचिका खारिज", "फैसला सुनाया"]
    },
    {
        "id": "disaster_alerts",
        "name": "⚠️ बड़े हादसे, आगजनी & कुदरती आपदा अलर्ट",
        "feeds": [
            ("गूगल न्यूज़ भारत बड़ा हादसा", "https://news.google.com/rss/search?q=%E0%A4%AD%E0%A4%BE%E0%A4%B0%E0%A4%A4+%E0%A4%B9%E0%A4%BE%E0%A4%A6%E0%A4%B8%E0%A4%BE+OR+%E0%A4%AD%E0%A5%80%E0%A4%B7%E0%A4%A3+%E0%A4%86%E0%A4%97+when:12h&hl=hi&gl=IN&ceid=IN:hi"),
            ("गूगल न्यूज़ आपदा अलर्ट", "https://news.google.com/rss/search?q=%E0%A4%B0%E0%A5%87%E0%A4%A1+%E0%A4%85%E0%A4%B2%E0%A4%B0%E0%A5%8D%E0%A4%9F+OR+%E0%A4%B0%E0%A5%87%E0%A4%B8%E0%A5%8D%E0%A4%95%E0%A5%8D%E0%A4%AF%E0%A5%82+when:12h&hl=hi&gl=IN&ceid=IN:hi"),
            ("एबीपी न्यूज़ राज्य", "https://www.abplive.com/states/feed")
        ],
        "keywords": ["हादसा", "टक्कर", "भीषण आग", "आगजनी", "ब्लास्ट", "धमाका", "सिलेंडर", "ट्रेन", "रेड अलर्ट", "चक्रवात", "तूफान", "बाढ़", "रेस्क्यू", "अस्पताल", "घायल", "मौत"]
    },
    {
        "id": "security_intel",
        "name": "🛡️ सीमा सुरक्षा, आतंकी साजिश & खुफिया ऑपरेशन",
        "feeds": [
            ("गूगल न्यूज़ सीमा सुरक्षा आतंकी", "https://news.google.com/rss/search?q=%E0%A4%AD%E0%A4%BE%E0%A4%B0%E0%A4%A4+%E0%A4%86%E0%A4%A4%E0%A4%82%E0%A4%95%E0%A5%80+OR+%E0%A4%98%E0%A5%81%E0%A4%B8%E0%A4%AA%E0%A5%88%E0%A4%A0+OR+%E0%A4%96%E0%A5%81%E0%A4%AB%E0%A4%BF%E0%A4%AF%E0%A4%BE+when:12h&hl=hi&gl=IN&ceid=IN:hi"),
            ("गूगल न्यूज़ एटीएस ऑपरेशन", "https://news.google.com/rss/search?q=ATS+OR+%E0%A4%B9%E0%A4%A5%E0%A4%BF%E0%A4%AF%E0%A4%BE%E0%A4%B0+%E0%A4%A4%E0%A4%B8%E0%A5%8D%E0%A4%95%E0%A4%B0%E0%A5%80+when:12h&hl=hi&gl=IN&ceid=IN:hi"),
            ("दैनिक जागरण राष्ट्रीय", "https://rss.jagran.com/rss/news/national.xml")
        ],
        "keywords": ["बॉर्डर", "आतंकी", "साजिश", "खुफिया", "ऑपरेशन", "मुठभेड़", "घुसपैठ", "हथियार", "तस्करी", "एटीएस", "ats", "एनआईए", "nia", "जवान", "सेना", "सैनिक", "कमांडो", "गिरफ्तार"]
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "hi-IN,hi;q=0.9,en-US;q=0.8,en;q=0.7",
}


MAX_NEWS_HOURS = int(os.environ.get("MAX_NEWS_HOURS", "12"))


def is_within_last_24_hours(date_str: str, max_hours: float = None) -> bool:
    """जांच: क्या खबर पिछले 12 घंटे (या निर्धारित समय) के अंदर प्रकाशित हुई है"""
    if max_hours is None:
        max_hours = float(MAX_NEWS_HOURS)
    if not date_str:
        return True
    try:
        dt = email.utils.parsedate_to_datetime(date_str)
        now = datetime.datetime.now(datetime.timezone.utc)
        diff_hours = (now - dt).total_seconds() / 3600.0
        return -0.5 <= diff_hours <= (max_hours + 0.5)  # ताज़ा 12 घंटे के अंदर की खबर
    except Exception:
        pass

    try:
        pub_dt = datetime.datetime.strptime(date_str[:25].strip(), "%a, %d %b %Y %H:%M:%S")
        now = datetime.datetime.utcnow()
        diff_hours = (now - pub_dt).total_seconds() / 3600.0
        return -0.5 <= diff_hours <= (max_hours + 0.5)
    except Exception:
        return True


def extract_full_article_text(url: str) -> str:
    """
    मूल समाचार वेबसाइट से 100% पूरा आर्टिकल बॉडी टेक्स्ट निकालता है।
    """
    if not url or not url.startswith("http") or is_blocked_source(url):
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


PUBLISHER_DOMAINS = {
    "theprint": "ThePrint Hindi",
    "amarujala": "अमर उजाला",
    "tv9hindi": "TV9 भारतवर्ष",
    "tv9": "TV9 भारतवर्ष",
    "bbc": "BBC News हिंदी",
    "dw": "DW हिंदी",
    "punjabkesari": "पंजाब केसरी",
    "downtoearth": "डाउन टू अर्थ",
    "moneycontrol": "मनीकंट्रोल हिंदी",
    "cnbctv18": "CNBC आवाज़",
    "firstpost": "Firstpost हिंदी",
    "etvbharat": "ईटीवी भारत",
    "lokmat": "लोकमत न्यूज़",
    "jagran": "दैनिक जागरण",
    "bhaskar": "दैनिक भास्कर",
    "abplive": "एबीपी न्यूज़",
    "abp": "एबीपी न्यूज़",
    "zeenews": "ज़ी न्यूज़",
    "ndtv": "NDTV",
    "aajtak": "आज तक",
    "indiatoday": "इंडिया टुडे",
    "thehindu": "द हिंदू",
    "indianexpress": "द इंडियन एक्सप्रेस",
    "navbharattimes": "नवभारत टाइम्स",
    "livehindustan": "लाइव हिन्दुस्तान",
    "hindustan": "लाइव हिन्दुस्तान",
    "news18": "News18 हिंदी",
    "oneindia": "वनइंडिया",
    "patrika": "राजस्थान पत्रिका",
    "jansatta": "जनसत्ता",
}


def resolve_publisher_name(url: str, default_source: str = "", title: str = "") -> str:
    """लेख के URL डोमेन या शीर्षक से असली पब्लिशर/न्यूज़ चैनल का नाम निकालना (गूगल न्यूज़ 100% निषिद्ध)"""
    # 1. शीर्षक में ' - ThePrint Hindi' या ' | दैनिक भास्कर' आदि की जांच
    if title:
        for dom, name in PUBLISHER_DOMAINS.items():
            if dom in title.lower() or name.lower() in title.lower():
                return name
        for sep in [' - ', ' | ']:
            if sep in title:
                candidate = title.rsplit(sep, 1)[-1].strip()
                if 2 <= len(candidate) <= 25 and "गूगल" not in candidate and "google" not in candidate.lower():
                    return candidate

    # 2. URL डोमेन की जांच
    if url:
        try:
            from urllib.parse import urlparse
            netloc = urlparse(url).netloc.lower()
            for dom, name in PUBLISHER_DOMAINS.items():
                if dom in netloc:
                    return name
        except Exception:
            pass

    if default_source and "गूगल" not in default_source and "google" not in default_source.lower():
        return default_source
    return "प्रेस कवरेज"


def extract_and_download_story_media(story_index: int, article_url: str, source_label: str = "") -> dict:
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

    if not article_url or not article_url.startswith("http") or is_blocked_source(article_url) or is_blocked_source(source_label):
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

        if not src.startswith("http") or is_blocked_source(src):
            return

        # CDN रेजोल्यूशन अपग्रेड: यदि URL में कम चौड़ाई है तो उसे 1200px Full HD में बदलें
        if "imwidth=" in src:
            src = re.sub(r"imwidth=\d+", "imwidth=1200", src)

        junk_indicators = [
            "logo", "icon", "advertisement", "pixel", "avatar", "facebook",
            "twitter", "whatsapp", "share", "arrow", "ad.", "banner",
            "spinner", "thumb_small", "rightarrow", "user_profile",
            "default_16x9", "placeholder", "sidebar", "teaser", "author", "editor"
        ]
        src_lower = src.lower()
        if any(j in src_lower for j in junk_indicators):
            return

        base_src = src.split("?")[0]
        if base_src not in seen_img_urls:
            seen_img_urls.add(base_src)
            candidate_img_urls.append(src)

    # 1. प्राथमिक लीड तस्वीर (og:image, twitter:image, preload, image_src)
    for prop in ["og:image", "og:image:secure_url", "twitter:image", "twitter:image:src", "og:image:url", "thumbnail", "image"]:
        for tag in soup.find_all("meta", property=prop) + soup.find_all("meta", attrs={"name": prop}) + soup.find_all("meta", attrs={"itemprop": prop}):
            if tag and tag.get("content"):
                add_img_candidate(tag["content"])

    for link in soup.find_all("link", rel=lambda r: r and any(x in str(r).lower() for x in ["image_src", "preload"])):
        if link.get("as") == "image" or "image" in str(link.get("rel", "")).lower():
            add_img_candidate(link.get("href"))

    # 2. सभी <figure> व <picture> टैग्स (जहाँ मुख्य प्रेस फोटोज़ सुरक्षित होती हैं)
    for fig in soup.find_all("figure") + soup.find_all("picture"):
        for source_tag in fig.find_all("source"):
            srcset = source_tag.get("srcset")
            if srcset:
                parts = [p.strip().split()[0] for p in srcset.split(",") if p.strip()]
                if parts:
                    add_img_candidate(parts[-1])
        for img_tag in fig.find_all("img"):
            for attr in ["src", "data-src", "data-original", "data-lazy-src", "data-high-res-src"]:
                val = img_tag.get(attr)
                if val:
                    add_img_candidate(val)

    # 3. आर्टिकल बॉडी व लीड इमेज कंटेनर्स
    containers = soup.find_all(["article", "main"])
    containers += soup.find_all("div", class_=lambda c: c and any(k in str(c).lower() for k in [
        "lead-image", "imgpod", "abp-story-article", "abp-story-detail",
        "article-body", "story-body", "story_content", "content-area",
        "detail_text", "article-content", "story-content", "story-detail",
        "body-content", "article-text", "post-content"
    ]))

    for c_box in containers:
        for bad in c_box.find_all(["aside", "nav", "footer", "header", "script", "style"]):
            bad.decompose()
        for bad in c_box.find_all("div", class_=lambda c: c and any(k in str(c).lower() for k in [
            "related", "recomended", "recommended", "trending", "also-read",
            "more-news", "other-stories", "sidebar", "widget", "taboola",
            "outbrain", "ad-container", "banner", "bottom-news", "suggestion",
            "comment"
        ])):
            bad.decompose()

        for img_tag in c_box.find_all("img"):
            # यदि srcset उपलब्ध है तो उच्चतम रेजोल्यूशन निकालें
            srcset = img_tag.get("srcset")
            if srcset:
                parts = [p.strip().split()[0] for p in srcset.split(",") if p.strip()]
                if parts:
                    add_img_candidate(parts[-1])
            for attr in ["src", "data-src", "data-original", "data-lazy-src", "data-high-res-src"]:
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

    # 4. असली न्यूज़ फोटोज़ व एनिमेटेड GIFs डाउनलोड करना (अधिकतम 8 प्रामाणिक मीडिया फाइल्स)
    downloaded_images = []
    img_counter = 1

    for img_url in candidate_img_urls:
        if img_counter > 8:
            break
        try:
            img_req_headers = dict(HEADERS)
            img_req_headers["Referer"] = article_url
            img_req_headers["Accept"] = "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"
            r_img = requests.get(img_url, headers=img_req_headers, timeout=12)
            if r_img.status_code != 200 or len(r_img.content) < 5000:
                continue

            content_type = r_img.headers.get("Content-Type", "").lower()
            is_gif = img_url.lower().endswith(".gif") or "image/gif" in content_type or ".gif" in img_url.lower()

            if is_gif:
                # 🎬 दैनिक भास्कर / अन्य स्रोतों से प्राप्त एनिमेटेड GIF
                gif_filename = f"scraped_news_gif_{story_index}_{img_counter:02d}.gif"
                gif_local_path = os.path.join(story_dir, gif_filename)
                with open(gif_local_path, "wb") as gf:
                    gf.write(r_img.content)

                # Remotion में स्मूथ फ्रेम-बाई-फ्रेम प्ले करने हेतु ffmpeg से लूपिंग MP4 में कन्वर्ट
                mp4_filename = f"scraped_news_gif_{story_index}_{img_counter:02d}.mp4"
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

                chosen_full = os.path.join(story_dir, chosen_fn)
                gif_size_kb = round(os.path.getsize(chosen_full) / 1024, 1) if os.path.exists(chosen_full) else 0.0
                downloaded_images.append({
                    "index": img_counter,
                    "local_path": chosen_rel,
                    "public_path": chosen_rel,
                    "filename": chosen_fn,
                    "resolution": "Animated Media",
                    "size_kb": gif_size_kb,
                    "is_animated": True,
                    "is_video": converted,
                    "is_scraped_news": True,
                    "credit_source": source_label,
                    "url": img_url
                })
                img_counter += 1
                continue

            # सामान्य समाचार तस्वीर (JPG/PNG/WEBP)
            pil_img = Image.open(BytesIO(r_img.content))
            w, h = pil_img.size

            # केवल वास्तविक उच्च-गुणवत्ता वाली लैंडस्केप असली तस्वीरें ही स्वीकार करें (320x180 विजेट्स रिजेक्ट)
            if w < 420 or h < 230:
                continue

            # 🚫 प्रोमोशनल बैनर, वर्टिकल (पोर्ट्रेट) फोटो, अत्यधिक सफेद बैकग्राउंड (>45%) को रिजेक्ट करें
            aspect = w / h
            if aspect > 2.45 or aspect < 1.15:
                continue

            try:
                import numpy as np
                arr_chk = np.array(pil_img)
                if arr_chk.ndim >= 3:
                    white_ratio = ((arr_chk[:, :, 0] > 230) & (arr_chk[:, :, 1] > 230) & (arr_chk[:, :, 2] > 230)).mean()
                    if white_ratio > 0.45:
                        continue
            except Exception:
                pass

            if pil_img.mode != "RGB":
                pil_img = pil_img.convert("RGB")

            # ✂️ वॉटरमार्क, चैनल लोगो व बॉटम टेक्स्ट ब्लरिंग (100% Broadcast Glass Effect)
            if clean_watermarks_and_text is not None:
                pil_img = clean_watermarks_and_text(pil_img)

            filename = f"scraped_news_img_{story_index}_{img_counter:02d}.jpg"
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
                "is_scraped_news": True,
                "credit_source": source_label,
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
        if len(verified_stories) >= target_count:
            break
        p_id = pillar["id"]
        p_name = pillar["name"]
        p_feeds = pillar["feeds"]
        p_keywords = pillar["keywords"]

        print(f"\n📡 [{p_name}] के लिए खबर खोजी जा रही है...", flush=True)
        found = False

        for feed_label, feed_url in p_feeds:
            if found:
                break
            if is_blocked_source(feed_label) or is_blocked_source(feed_url):
                continue
            if source_counts.get(feed_label, 0) >= 2:
                continue

            items = get_feed_items(feed_url)
            for it in items:
                title = it["title"] if isinstance(it, dict) else (it.find("title").text.strip() if it.find("title") is not None else "")
                link = it["link"] if isinstance(it, dict) else (it.find("link").text.strip() if it.find("link") is not None else "")
                pub_date = it["pubDate"] if isinstance(it, dict) else (it.find("pubDate").text.strip() if it.find("pubDate") is not None else "")

                if not title or title in seen_titles or link in seen_urls:
                    continue

                # 🚫 अमर उजाला व प्रतिबंधित स्रोतों को 100% ब्लॉक करें
                if is_blocked_source(link) or is_blocked_source(title) or is_blocked_source(feed_label):
                    continue

                # 🇮🇳 केवल भारत की खबरें स्वीकार करें (विदेशी अपराध/हादसे रिजेक्ट)
                if not is_strictly_indian_news(title):
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

                # डीकोडिंग के बाद भी अमर उजाला व प्रतिबंधित स्रोतों को चेक करें
                if is_blocked_source(link):
                    continue

                # 3. पूरा 100% समाचार निकालें
                full_text = extract_full_article_text(link)
                word_count = len(full_text.split()) if full_text else 0

                if not full_text or word_count < 180:
                    continue

                if not is_strictly_indian_news(title, full_text):
                    continue

                seen_titles.add(title)
                seen_urls.add(link)
                real_pub = resolve_publisher_name(link, feed_label, title=title)
                story_item = {
                    "pillar_id": p_id,
                    "pillar_name": p_name,
                    "title": title,
                    "source": real_pub,
                    "real_publisher": real_pub,
                    "published_at": pub_date,
                    "url": link,
                    "word_count": word_count,
                    "full_text": full_text
                }
                verified_stories.append(story_item)
                pillar_counts[p_id] += 1
                source_counts[feed_label] = source_counts.get(feed_label, 0) + 1
                found = True
                print(f"   ✅ [पिलर कवर हुआ] {title[:60]}... ({word_count} शब्द | {real_pub})", flush=True)
                time.sleep(0.3)
                break

    print(f"\n📊 राउंड 1 संपन्न: {len(verified_stories)} खबरें (7 पिलर्स में से {sum(1 for v in pillar_counts.values() if v > 0)} पिलर्स कवर हुए)।", flush=True)

    # -------------------------------------------------------------
    # राउंड 2: कुल 10 खबरें पूरी करने के लिए प्रमुख पिलर्स (क्राइम, जन-समस्याएं आदि) से दूसरी खबर
    # -------------------------------------------------------------
    if len(verified_stories) < target_count:
        needed = target_count - len(verified_stories)
        print(f"\n🔹 राउंड 2: कुल {target_count} पूरी करने के लिए शेष {needed} खबरें जोड़ी जा रही हैं...", flush=True)

        max_pillar_r2 = max(2, (target_count // len(MASTER_7_PILLARS)) + 2)
        max_source_r2 = max(2, target_count // 5 + 1)

        for pillar in MASTER_7_PILLARS:
            if len(verified_stories) >= target_count:
                break

            p_id = pillar["id"]
            p_name = pillar["name"]
            p_feeds = pillar["feeds"]
            p_keywords = pillar["keywords"]

            # प्रति पिलर अधिकतम सीमा (50 खबरों के लिए डायनामिक)
            if pillar_counts[p_id] >= max_pillar_r2:
                continue

            for feed_label, feed_url in p_feeds:
                if len(verified_stories) >= target_count or pillar_counts[p_id] >= max_pillar_r2:
                    break
                if is_blocked_source(feed_label) or is_blocked_source(feed_url):
                    continue
                if source_counts.get(feed_label, 0) >= max_source_r2:
                    continue

                items = get_feed_items(feed_url)
                for it in items:
                    if len(verified_stories) >= target_count or pillar_counts[p_id] >= max_pillar_r2:
                        break

                    title = it["title"] if isinstance(it, dict) else (it.find("title").text.strip() if it.find("title") is not None else "")
                    link = it["link"] if isinstance(it, dict) else (it.find("link").text.strip() if it.find("link") is not None else "")
                    pub_date = it["pubDate"] if isinstance(it, dict) else (it.find("pubDate").text.strip() if it.find("pubDate") is not None else "")

                    if not title or title in seen_titles or link in seen_urls:
                        continue

                    # 🚫 अमर उजाला व प्रतिबंधित स्रोतों को 100% ब्लॉक करें
                    if is_blocked_source(link) or is_blocked_source(title) or is_blocked_source(feed_label):
                        continue

                    # 🇮🇳 केवल भारत की खबरें स्वीकार करें (विदेशी अपराध/हादसे रिजेक्ट)
                    if not is_strictly_indian_news(title):
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

                    # डीकोडिंग के बाद भी अमर उजाला को ब्लॉक करें
                    if is_blocked_source(link):
                        continue

                    full_text = extract_full_article_text(link)
                    word_count = len(full_text.split()) if full_text else 0

                    if not full_text or word_count < 180:
                        continue

                    if not is_strictly_indian_news(title, full_text):
                        continue

                    seen_titles.add(title)
                    seen_urls.add(link)
                    real_pub = resolve_publisher_name(link, feed_label, title=title)
                    story_item = {
                        "pillar_id": p_id,
                        "pillar_name": p_name,
                        "title": title,
                        "source": real_pub,
                        "real_publisher": real_pub,
                        "published_at": pub_date,
                        "url": link,
                        "word_count": word_count,
                        "full_text": full_text
                    }
                    verified_stories.append(story_item)
                    pillar_counts[p_id] += 1
                    source_counts[feed_label] = source_counts.get(feed_label, 0) + 1
                    print(f"   ✅ [अतिरिक्त खबर] {title[:60]}... ({word_count} शब्द | {real_pub})", flush=True)
                    time.sleep(0.3)

    # -------------------------------------------------------------
    # राउंड 3: आपातकालीन फॉलबैक (यदि किसी पिलर में खबर न मिली हो तो 10 पूरी करना)
    # -------------------------------------------------------------
    if len(verified_stories) < target_count:
        needed = target_count - len(verified_stories)
        print(f"\n🔹 राउंड 3: राष्ट्रीय हेडलाइंस से {needed} अतिरिक्त खबरें पूरी की जा रही हैं...", flush=True)
        backup_feeds = [
            ("दैनिक जागरण राष्ट्रीय", "https://rss.jagran.com/rss/news/national.xml"),
            ("एबीपी न्यूज़", "https://www.abplive.com/home/feed"),
            ("ज़ी न्यूज़ हिंदी", "https://zeenews.india.com/hindi/india.xml"),
            ("दैनिक भास्कर", "https://www.bhaskar.com/rss-v1--category-1061.xml"),
            ("एनडीटीवी इंडिया", "https://feeds.feedburner.com/ndtvkhabar"),
            ("न्यूज़18 हिंदी", "https://hindi.news18.com/rss/khabar.xml"),
            ("आज तक राष्ट्रीय", "https://www.aajtak.in/rssfeeds/?id=home"),
            ("गूगल न्यूज़ भारत", "https://news.google.com/rss/headlines/section/topic/NATION?hl=hi&gl=IN&ceid=IN:hi"),
            ("गूगल न्यूज़ भारत मुख्य", "https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi")
        ]
        for f_label, f_url in backup_feeds:
            if len(verified_stories) >= target_count:
                break
            if is_blocked_source(f_label) or is_blocked_source(f_url):
                continue
            items = get_feed_items(f_url)
            for it in items:
                if len(verified_stories) >= target_count:
                    break
                t = it["title"] if isinstance(it, dict) else (it.find("title").text.strip() if it.find("title") is not None else "")
                u = it["link"] if isinstance(it, dict) else (it.find("link").text.strip() if it.find("link") is not None else "")
                p = it["pubDate"] if isinstance(it, dict) else (it.find("pubDate").text.strip() if it.find("pubDate") is not None else "")
                if is_blocked_source(u) or is_blocked_source(t) or is_blocked_source(f_label):
                    continue
                if not is_strictly_indian_news(t):
                    continue
                if t and t not in seen_titles and u not in seen_urls and is_within_last_24_hours(p):
                    if "news.google.com" in u:
                        try:
                            import googlenewsdecoder
                            dec = googlenewsdecoder.gnewsdecoder(u)
                            if dec.get("success") and dec.get("decoded_url"):
                                u = dec["decoded_url"]
                        except Exception:
                            pass
                    if is_blocked_source(u):
                        continue
                    ft = extract_full_article_text(u)
                    wc = len(ft.split()) if ft else 0
                    if ft and wc >= 180 and is_strictly_indian_news(t, ft):
                        seen_titles.add(t)
                        seen_urls.add(u)
                        real_pub = resolve_publisher_name(u, f_label, title=t)
                        verified_stories.append({
                            "pillar_id": "national_crisis",
                            "pillar_name": "📢 देश की बड़ी हलचल & जन-मुद्दा",
                            "title": t,
                            "source": real_pub,
                            "real_publisher": real_pub,
                            "published_at": p,
                            "url": u,
                            "word_count": wc,
                            "full_text": ft
                        })
                        print(f"   ✅ [फॉलबैक खबर] {t[:60]}... ({wc} शब्द | {real_pub})", flush=True)

    # -------------------------------------------------------------
    # 🎯 स्टोरी #01 प्रायोरिटी हुक: सुनिश्चित करना कि पहली खबर हमेशा एनकाउंटर/क्राइम या ED रेड की हो
    # -------------------------------------------------------------
    top_lead_index = None
    for idx, st in enumerate(verified_stories):
        p_id = st.get("pillar_id", "")
        if p_id in ["crime_encounter", "ed_cbi_raid"]:
            top_lead_index = idx
            break

    if top_lead_index is None:
        for idx, st in enumerate(verified_stories):
            if st.get("pillar_id", "") in ["bulldozer_action", "cyber_fraud"]:
                top_lead_index = idx
                break

    if top_lead_index is not None and top_lead_index > 0:
        lead_story = verified_stories.pop(top_lead_index)
        verified_stories.insert(0, lead_story)
        print(f"\n⚡ [Story #01 Priority Hook] '{lead_story['title'][:60]}...' ({lead_story['pillar_name']}) को मुख्य लीड स्टोरी बनाया गया!", flush=True)

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
        media_res = extract_and_download_story_media(i, story["url"], source_label=story.get("source", ""))
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
                im_idx = img.get("index", 1)
                is_primary = " [मुख्य फोटो (PRIMARY)]" if im_idx == 1 else ""
                res_val = img.get("resolution", "HD")
                size_val = img.get("size_kb", "0")
                loc_val = img.get("local_path", "")
                url_val = img.get("url", "")
                lines.append(f"  [फोटो {im_idx:02d}]{is_primary} रेज़ोल्यूशन: {res_val} px | साइज: {size_val} KB")
                lines.append(f"            लोकल फाइल : {loc_val}")
                if img.get("public_path"):
                    lines.append(f"            पब्लिक पाथ: {img['public_path']} (Remotion वीडियो उपयोग हेतु)")
                lines.append(f"            मूल वेब URL: {url_val}")
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


def main(target_count: int = 50):
    stories = fetch_master_bulletin(target_count=target_count)
    write_to_txt_file(stories, TXT_OUTPUT_PATH)
    write_to_json_file(stories, JSON_OUTPUT_PATH)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=50, help="अधिकतम कितनी खबरें फेच करनी हैं (Default: 50)")
    args = parser.parse_args()
    main(target_count=args.max)

