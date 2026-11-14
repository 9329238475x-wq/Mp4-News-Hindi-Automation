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

from story_metadata_helper import save_story_folder_metadata
from text_repair_helper import repair_hindi_tts_text, sanitize_headline_safety

def ensure_card_headline_entity_highlight(lines: list) -> list:
    """
    Ensures that Line 3 (index 2) of the 4-line broadcast card has **entity** marked
    for rendering in the iconic broadcast yellow highlight box.
    """
    if len(lines) < 3:
        return lines
    line3 = lines[2]
    if "**" in line3:
        return lines

    postpositions = [' की ', ' ने ', ' पर ', ' को ', ' से ', ' का ', ' के ', ' द्वारा ']
    for pp in postpositions:
        if pp in line3:
            parts = line3.split(pp, 1)
            entity_words = parts[0].strip().split()
            if 1 <= len(entity_words) <= 4:
                lines[2] = f"**{parts[0].strip()}**{pp}{parts[1].strip()}"
                return lines
    words = line3.strip().split()
    if len(words) >= 2:
        lines[2] = f"**{words[0]} {words[1]}** " + " ".join(words[2:])
    return lines

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


def fix_missing_ke_liye(text: str) -> str:
    """'मछुआरों लिए' -> 'मछुआरों के लिए' जैसी व्याकरण संबंधी त्रुटियों को सुधारना"""
    if not text:
        return ""
    pronoun_exceptions = {'इसके', 'उसके', 'किसके', 'जिसके', 'इनके', 'उनके', 'अपने', 'सबके', 'हमारे', 'तुम्हारे', 'मेरे', 'आपके', 'किसलिए', 'इसलिए', 'इसीलिये'}
    def repl(m):
        prev_word = m.group(1)
        if prev_word in pronoun_exceptions or prev_word.endswith('के') or prev_word.endswith('रे') or prev_word.endswith('ने'):
            return f"{prev_word} लिए"
        return f"{prev_word} के लिए"
    return re.sub(r'([\u0900-\u097F]+)\s+लिए(?![^\s])', repl, text)


def sanitize_headline_grammar(h: str) -> str:
    """हेडलाइंस और कार्ड टेक्स्ट में टूटी-फूटी हिंदी, छूटे हुए कारक व अधूरी क्रियाओं को सुधारना"""
    if not h:
        return ""
    h = fix_missing_ke_liye(h)

    # 1. 'गार्ड को' -> 'कोस्ट गार्ड को' (समुद्र/नाव/तटरक्षक संदर्भ)
    h = re.sub(r'(?<![^\s])ने\s+गार्ड\s+को(?![^\s])', 'ने कोस्ट गार्ड को', h)

    # 2. 'सुरक्षा आदेश दिया' -> 'सुरक्षा के आदेश दिए'
    h = re.sub(r'सुरक्षा\s+आदेश\s+(?:दिया|दिए)', 'सुरक्षा के आदेश दिए', h)

    # 3. 'सुधार कहा' -> 'सुधारने के निर्देश दिए'
    h = re.sub(r'(?<![^\s])सुधार\s+कहा(?![^\s])', 'सुधारने के निर्देश दिए', h)
    h = re.sub(r'(?<![^\s])कार्रवाई\s+कहा(?![^\s])', 'कार्रवाई के निर्देश दिए', h)
    h = re.sub(r'(?<![^\s])जांच\s+कहा(?![^\s])', 'जांच के आदेश दिए', h)
    h = re.sub(r'(?<![^\s])मंजूरी\s+कहा(?![^\s])', 'मंजूरी दी', h)
    h = re.sub(r'(?<![^\s])रोक\s+कहा(?![^\s])', 'रोकने के आदेश दिए', h)

    # 4. अन्य आदेश/निर्देश क्रियाएं
    h = re.sub(r'(?<![^\s])निगरानी\s+आदेश\s+(?:दिया|दिए)(?![^\s])', 'निगरानी के आदेश दिए', h)
    h = re.sub(r'(?<![^\s])राहत\s+आदेश\s+(?:दिया|दिए)(?![^\s])', 'राहत के आदेश दिए', h)

    return h


def sanitize_anchor_text(t: str) -> str:
    """अनौपचारिक व बचकाने शब्दों को हटाना और मानक हिंदी व्याकरण सुधारना"""
    if not t:
        return ""
    # Note: 'अपन' कभी न डालें क्योंकि वह 'अपनी', 'अपने' को 'ी', 'े' में काट देता है!
    t = re.sub(r'\b(अरे भाई|भाई साहब|भाई,|भाई|यार|भैया|दोस्त)\b', '', t)
    # व्याकरण, कारक और वर्तनी सुधार:
    t = fix_missing_ke_liye(t)
    t = sanitize_headline_grammar(t)
    t = re.sub(r'\bट्रेन आगे\b', 'ट्रेन के आगे', t)
    t = re.sub(r'\bगोली धमकी\b', 'गोली मारने की धमकी', t)
    t = re.sub(r'\bडिसिपी\b', 'डीसीपी', t)
    t = re.sub(r'\bपरिवार को माफी मांगी\b', 'परिवार से माफी मांगी', t)
    return re.sub(r'\s+', ' ', t).strip()


def sanitize_keyword_master(kw: str) -> str:
    """
    मास्टर कीवर्ड सैनिटाइज़र:
    1. किसी भी साल (1900-2099) को हटाना।
    2. किसी भी समय (12:30 PM, 3:30, AM, PM, baje) को हटाना।
    3. कोट्स, ब्रैकेट्स, स्पेशल कैरेक्टर्स हटाना।
    4. 2 से 6 शब्दों का छोटा, हाई-इम्पैक्ट सर्च कीवर्ड बनाना।
    """
    if not kw:
        return ""
    clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', str(kw))
    clean = re.sub(r'\b(19\d\d|20\d\d)\b', '', clean)
    clean = re.sub(r'\b\d{1,2}(:\d{2})?\s*(am|pm|a\.m\.|p\.m\.|baje|hrs|hours)?\b', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\b(start|route|departure|concluding|ceremony|boarding|transport|heavy|ban|closure|save|remove|during|after|before|walk|walks|walking|run|running)\b', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\bup\b', 'Uttar Pradesh', clean, flags=re.IGNORECASE)

    if 'keshav' in clean.lower() and 'maurya' in clean.lower() and 'prasad' not in clean.lower():
        clean = re.sub(r'keshav\s+maurya', 'Keshav Prasad Maurya BJP', clean, flags=re.IGNORECASE)

    # 0. YOUTUBE MONETIZATION GUARD: 100% Violent/Graphic/Anatomical Keyword Replacement
    VIOLENT_KEYWORDS_MAP = {
        r'\b(crime\s+scene|crime-scene)\b': 'police investigation barricade',
        r'\b(suspect\s+leg|injured\s+leg|broken\s+leg|gunshot\s+leg|bullet\s+leg|\blegs?\b)\b': 'police station building',
        r'\b(killings|killing|dead\s+body|dead\s+bodies|corpse|cadaver|laash|massacre|murder|murders)\b': 'police patrolling vehicle',
        r'\b(blood|bloody|bloodstain|bloodstained)\b': 'police checkpoint barricade',
        r'\b(shooting|gunshot|gunfight|encounter)\b': 'police barricade checkpoint',
        r'\b(suicide|hanging)\b': 'police station exterior',
    }
    for v_pat, v_sub in VIOLENT_KEYWORDS_MAP.items():
        clean = re.sub(v_pat, v_sub, clean, flags=re.IGNORECASE)

    c_low = clean.lower()

    # केवल यदि शाहदरा का ज़िक्र हो और लखनऊ का मामला हो
    if 'shahdara' in c_low and 'lucknow' not in c_low and 'delhi' not in c_low:
        clean = f'{clean} Lucknow'
        c_low = clean.lower()

    # प्राइवेट नागरिकों / पीड़ितों के नामों को सामान्य आधिकारिक इन्वेस्टिगेशन से बदलना
    if any(re.search(rf'\b{w}\b', c_low) for w in ['neha', 'sapna', 'pooja', 'priya', 'victim', 'accused']):
        clean = 'Police investigation file photo'
        c_low = clean.lower()
    elif any(re.search(rf'\b{w}\b', c_low) for w in ['suicide', 'scandal']):
        clean = 'Official investigation file photo'
        c_low = clean.lower()
    elif re.search(r'\b(train|railway|railways)\b', c_low):
        clean = 'Indian Railways train tracks generic'
        c_low = clean.lower()

    clean = re.sub(r'\s+', ' ', clean).strip()
    words = clean.split()
    if not words:
        return ""
    result = " ".join(words[:6])
    if result.endswith(" Uttar"):
        result += " Pradesh"
    return result


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

    screen_hl = sanitize_headline_safety(sanitize_anchor_text(stage1_resp.get("screen_headline", title[:50]))).replace("**", "").replace("*", "")
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
        s_clean = repair_hindi_tts_text(sanitize_anchor_text(c.get("sentence", "")))
        b_clean = repair_hindi_tts_text(sanitize_anchor_text(c.get("bullet_text", s_clean)))
        cleaned_chunks.append({
            "chunk_index": idx,
            "sentence": s_clean,
            "bullet_text": b_clean,
            "visual_intent": "REAL_PHOTO",
            "image_keywords_en": [],
            "meme_keyword_en": None
        })
        bulletin_points.append(b_clean)

    is_suicide = bool(stage1_resp.get("is_suicide_story", False)) or bool(re.search(r"आत्महत्या|खुदकुशी|suicide", str(story.get("title", "")) + " " + str(story.get("full_text", "")), re.IGNORECASE))
    stage1_data = {
        "screen_headline": screen_hl,
        "category": stage1_resp.get("category", p_name),
        "is_suicide_story": is_suicide,
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

    # Sanitize headlines: 100% clean, remove all markdown asterisks (**), trailing colons and punctuation
    cleaned_headlines = []
    for h in raw_headlines:
        if not h:
            continue
        clean_h = sanitize_headline_safety(h)
        clean_h = sanitize_headline_grammar(clean_h)
        clean_h = clean_h.replace("**", "").replace("*", "").rstrip(":").rstrip("।").strip()
        if clean_h:
            cleaned_headlines.append(clean_h)

    if len(cleaned_headlines) < 4:
        clean_screen_hl = sanitize_headline_grammar(sanitize_headline_safety(screen_hl)).replace("**", "").replace("*", "").rstrip(":").rstrip("।").strip()
        while len(cleaned_headlines) < 4:
            cleaned_headlines.append(clean_screen_hl)

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
    kw_by_index = {}
    for item in chunk_img_kws:
        if isinstance(item, dict):
            idx_val = item.get("chunk_index")
            kws_val = item.get("image_keywords_en", [])
            if idx_val is not None:
                kw_by_index[idx_val] = kws_val
                kw_by_index[str(idx_val)] = kws_val

    # Extract dynamic story topic and location for smart contextual fallbacks
    story_loc = story.get("location") or story.get("verified_location") or "India"
    story_cat = story.get("category", "")
    story_combined = f"{story.get('title', '')} {story_cat} {story.get('full_text', '')[:500]}".lower()

    # Clean broad keywords first so they can serve as primary context fallbacks
    broad_kws = []
    for bk in raw_broad_kws:
        s_bk = sanitize_keyword_master(bk)
        if s_bk and len(s_bk.split()) >= 2 and s_bk not in broad_kws:
            broad_kws.append(s_bk)

    for c_i, c in enumerate(cleaned_chunks):
        c_idx = c.get("chunk_index", c_i + 1)
        c_kws = (
            kw_by_index.get(c_idx) or
            kw_by_index.get(str(c_idx)) or
            kw_by_index.get(c_i) or
            kw_by_index.get(str(c_i))
        )
        if not c_kws and c_i < len(chunk_img_kws) and isinstance(chunk_img_kws[c_i], dict):
            c_kws = chunk_img_kws[c_i].get("image_keywords_en", [])
        if not c_kws:
            c_kws = []

        sanitized_list = []
        for raw_k in c_kws:
            s_k = sanitize_keyword_master(raw_k)
            # Never allow single-word garbage like 'news'
            if s_k and len(s_k.split()) >= 2 and s_k not in sanitized_list:
                sanitized_list.append(s_k)

        # 1. Use broad story-specific keywords as primary fallback (matches exact topic, never hardcoded generic words!)
        for bk in broad_kws:
            if len(sanitized_list) >= 3:
                break
            if bk not in sanitized_list and len(bk.split()) >= 2:
                sanitized_list.append(bk)

        # 2. Dynamic contextual fallbacks based on actual story category and topic (Zero generic secretariat/archive words!)
        context_fallbacks = []

        # Category A: Cyclone, Weather, Flood, Rain, Storm, Sea, Coast Guard, Boats, Fishermen
        if any(w in story_combined for w in ["चक्रवात", "मौसम", "आपदा", "तूफान", "बारिश", "बाढ़", "समुद्र", "नाव", "मछुआरे", "मछुआरों", "तटरक्षक", "गार्ड", "कोस्ट गार्ड", "नौसेना", "cyclone", "sea", "boat", "coast guard", "flood", "rain"]):
            context_fallbacks = [
                f"{story_loc} Coast Guard ship rescue sea",
                f"{story_loc} cyclone satellite weather radar",
                f"{story_loc} fishing boats coastal harbor",
                f"{story_loc} fishermen coastal search operation",
                f"{story_loc} disaster response team rescue"
            ]
        # Category B: Accidents, Fire, Explosion, Tragedy
        elif any(w in story_combined for w in ["हादसा", "टक्कर", "आग", "आगजनी", "ब्लास्ट", "धमाका", "सिलेंडर", "ट्रेन", "accident", "fire"]):
            context_fallbacks = [
                f"{story_loc} emergency rescue disaster site",
                f"{story_loc} fire brigade emergency operation",
                f"{story_loc} district hospital trauma building",
                f"{story_loc} national highway emergency team"
            ]
        # Category C: ED, CBI, Vigilance, Income Tax, Raid, Mahadev Satta
        elif any(w in story_combined for w in ["ईडी", "सीबीआई", "विजिलेंस", "छापा", "छापेमारी", "रेड", "सट्टा", "महादेव", "घोटाला", "ed", "cbi"]):
            context_fallbacks = [
                f"Enforcement Directorate ED office {story_loc}",
                f"CBI investigation headquarters {story_loc}",
                f"{story_loc} police cyber crime cell",
                f"{story_loc} income tax search operation"
            ]
        # Category D: Bulldozer, Demolition, Encroachment
        elif any(w in story_combined for w in ["बुलडोजर", "ध्वस्त", "अवैध", "कब्जा", "कुर्क", "सील"]):
            context_fallbacks = [
                f"{story_loc} bulldozer demolition action",
                f"{story_loc} municipal anti encroachment drive",
                f"{story_loc} district administration office"
            ]
        # Category E: Crime, Encounter, Mafia, Police, Gangster
        elif any(w in story_combined for w in ["क्राइम", "अपराध", "कानून", "पुलिस", "एनकाउंटर", "मुठभेड़", "गैंगस्टर", "माफिया", "हत्या", "गिरफ्तार"]):
            context_fallbacks = [
                f"{story_loc} police administration office",
                f"{story_loc} police barricade checkpoint",
                f"{story_loc} district court justice building",
                f"{story_loc} police patrolling vehicle"
            ]
        # Category F: Court, Supreme Court, High Court, Verdicts
        elif any(w in story_combined for w in ["कोर्ट", "अदालत", "सुप्रीम कोर्ट", "हाई कोर्ट", "जज", "सजा", "जमानत"]):
            context_fallbacks = [
                f"{story_loc} High Court building exterior",
                f"Supreme Court of India New Delhi",
                f"{story_loc} district legal courtroom"
            ]
        # Default Broadcast Fallback (Clean real news, ZERO 'administrative secretariat' or 'press conference' or 'public event archive')
        else:
            context_fallbacks = [
                f"{story_loc} breaking news broadcast coverage",
                f"{story_loc} district administration headquarters",
                f"{story_loc} official government briefing"
            ]

        fb_i = 0
        while len(sanitized_list) < 3 and fb_i < len(context_fallbacks):
            fb_kw = sanitize_keyword_master(context_fallbacks[fb_i])
            if fb_kw and len(fb_kw.split()) >= 2 and fb_kw not in sanitized_list:
                sanitized_list.append(fb_kw)
            fb_i += 1

        c["image_keywords_en"] = sanitized_list[:3]
        c["visual_intent"] = "REAL_PHOTO"
        c["meme_keyword_en"] = None

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

    images_list = story.get("images", [])
    if images_list and isinstance(images_list[0], dict) and images_list[0].get("local_path"):
        primary_img_rel = images_list[0]["local_path"].replace("\\", "/")
    elif os.path.exists(os.path.join(OUT_DIR, story_dir_name, f"news_img_{s_num}_01.jpg")):
        primary_img_rel = f"out/{story_dir_name}/news_img_{s_num}_01.jpg"
    else:
        primary_img_rel = f"out/{story_dir_name}/news real image/scraped_news_img_{s_num}_01.jpg"
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

    clean_voiceover = repair_hindi_tts_text(" ".join([c["sentence"].replace("**", "").replace("*", "") for c in cleaned_chunks]))

    # मुख्य स्क्रीन हेडलाइन (पहली हेडलाइन)
    primary_headline = sanitize_headline_safety(cleaned_headlines[0] if cleaned_headlines else screen_hl)

    # संपूर्ण मेटाडेटा और विस्तृत स्क्रिप्ट सेव करना: out/story_XX/
    # (story_XX_data.json और script_XX.txt को एक साथ सुरक्षित रूप से लिखना)

    merged_story = {
        "story_number": s_num,
        "category": stage1_data["category"],
        "is_suicide_story": stage1_data.get("is_suicide_story", False),
        "source": story.get("source", "न्यूज़ डेस्क"),
        "real_publisher": story.get("real_publisher", story.get("source", "न्यूज़ डेस्क")),
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
    # प्रत्येक खबर के फोल्डर (out/story_XX/) में संपूर्ण JSON डेटा व विस्तृत स्क्रिप्ट सेव करें
    save_story_folder_metadata(merged_story, OUT_DIR)
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
