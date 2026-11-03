"""
Master Pipeline Runner for 'DLS News - हर खबर काम की' (niches/01-daily-top10)
-------------------------------------------------------------------------
यह सिंगल-कमांड मास्टर कंट्रोलर है जो पूरे ऑटोमेशन को 3 चरणों में चलाता है:
  1. ताज़ा समाचार फेचिंग और 120B AI स्क्रिप्ट जनरेशन (generate_bulletin.py)
  2. रियल न्यूज़ इमेजेस और 1080p HD B-Roll वीडियो डाउनलोड (download_assets.py)
  3. Edge-TTS प्राकृतिक हिंदी वॉइसओवर + ऑडियो सिंक (generate_audio.py)

उपयोग:
  python run_pipeline.py           # पूरा 3-चरण ऑटोमेशन चलाएँ
  python run_pipeline.py --status  # वर्तमान बुलेटिन का डैशबोर्ड देखें
  python run_pipeline.py --news    # केवल ताज़ा खबरें व AI स्क्रिप्ट बनाएं
  python run_pipeline.py --assets  # केवल B-Roll और इमेजेस डाउनलोड करें
  python run_pipeline.py --audio   # केवल वॉइसओवर ऑडियो बनाएं
  python run_pipeline.py --preview # Remotion स्टूडियो प्रीव्यू खोलें
  python run_pipeline.py --render  # फाइनल 1080p वीडियो रेंडर करें
"""

import os
import sys
import json
import time
import argparse
import asyncio
import subprocess

# UTF-8 एनकोडिंग सपोर्ट (Windows)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURR_DIR, "..", ".."))
JSON_PATH = os.path.join(CURR_DIR, "generated_sample_top10.json")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

from generate_bulletin import generate_dls_bulletin
from download_assets import download_all_assets
from generate_audio import generate_all_audios
from extract_waveform import process_audio_waveforms_and_metadata


def print_banner(title: str):
    print("\n" + "═" * 74)
    print(f"  📢  {title}")
    print("═" * 74)


def show_bulletin_status():
    """वर्तमान बुलेटिन का विस्तृत स्टेटस डैशबोर्ड दिखाता है"""
    print_banner("DLS News बुलेटिन स्टेटस डैशबोर्ड")
    if not os.path.exists(JSON_PATH):
        print(f"❌ कोई बुलेटिन फाइल नहीं मिली: {JSON_PATH}")
        return

    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            stories = json.load(f)
    except Exception as e:
        print(f"❌ JSON लोड एरर: {e}")
        return

    print(f"📊 कुल खबरें: {len(stories)}\n")
    total_audio_sec = 0

    for s in stories:
        num = s.get("story_number", 0)
        cat = s.get("category", "सामान्य")
        hl = s.get("screen_headline", "शीर्षक अनुपलब्ध")
        dur = s.get("audio_duration", 0)
        total_audio_sec += dur
        v_asset = s.get("local_visual_asset", "अनुपलब्ध")
        a_asset = s.get("local_audio_asset", "अनुपलब्ध")

        # चेक करें कि फाइल्स डिस्क पर मौजूद हैं या नहीं
        v_exists = "✅" if v_asset and os.path.exists(os.path.join(BASE_DIR, v_asset)) else "⚠️"
        a_exists = "✅" if a_asset and os.path.exists(os.path.join(BASE_DIR, a_asset)) else "⚠️"

        print(f"[{num:02d}] 🏷️  {cat}")
        print(f"     📌 हेडलाइन: {hl}")
        print(f"     🎬 विजुअल : {v_exists} {v_asset}")
        print(f"     🎙️  ऑडियो  : {a_exists} {a_asset} ({dur}s)")
        print("     " + "─" * 66)

    mins = int(total_audio_sec // 60)
    secs = int(total_audio_sec % 60)
    print(f"\n⏱️  कुल वीडियो अवधि: ~{mins} मिनट {secs} सेकंड ({round(total_audio_sec, 1)}s)")
    print(f"📁 JSON पाथ: {JSON_PATH}\n")


def run_remotion_preview():
    """Remotion Studio चलाता है"""
    print_banner("Remotion Studio प्रीव्यू शुरू हो रहा है...")
    print("🌐 ब्राउज़र में http://localhost:3000 खुलेगा")
    print("रोकने के लिए Ctrl + C दबाएं।\n")
    try:
        subprocess.run(["npm", "run", "dev"], cwd=BASE_DIR, check=True, shell=True)
    except KeyboardInterrupt:
        print("\n🛑 स्टूडियो बंद किया गया।")
    except Exception as e:
        print(f"❌ एरर: {e}")


from verify_bulletin_qa import run_all_qa_checks


def clean_old_temp_files(keep_master: bool = False):
    """पुराने टेस्ट वीडियो और टेम्पररी फाइलों को हटाता है ताकि कोई कन्फ्यूजन न हो"""
    out_dir = os.path.join(BASE_DIR, "out")
    if not os.path.exists(out_dir):
        return

    print_banner("🧹 पुराने टेम्पररी फाइल्स की ऑटोमैटिक सफाई (Cleanup)...")
    seg_dir = os.path.join(out_dir, "segments")

    # 1. सेगमेंट्स डायरेक्टरी साफ करें
    if os.path.exists(seg_dir):
        for f in os.listdir(seg_dir):
            fp = os.path.join(seg_dir, f)
            try:
                if os.path.isfile(fp):
                    os.remove(fp)
            except Exception:
                pass
        print(f"  ✔ पुरानी सेगमेंट फाइल्स साफ की गईं: {seg_dir}")

    # 2. out फोल्डर में टेस्ट फाइल्स और पुरानी गैर-जरूरी फाइल्स साफ करें
    temp_prefixes = ("test-", "test_", "check_", "tmp_")
    removed_count = 0
    for f in os.listdir(out_dir):
        fp = os.path.join(out_dir, f)
        if not os.path.isfile(fp):
            continue
        if any(f.startswith(p) for p in temp_prefixes):
            try:
                os.remove(fp)
                removed_count += 1
            except Exception:
                pass

    print(f"  ✔ {removed_count} पुरानी टेस्ट फाइल्स सफलतापूर्वक हटाई गईं। अब केवल फाइनल मास्टर वीडियो रहेगा।\n")


def render_story_segment(story_num: int, total_stories: int = 10) -> str:
    """एक एकल स्टोरी कंपोज़िशन (DLSNewsStory-XX) को 1080p MP4 में रेंडर करता है"""
    comp_id = f"DLSNewsStory-{story_num:02d}"
    seg_dir = os.path.join(BASE_DIR, "out", "segments")
    os.makedirs(seg_dir, exist_ok=True)
    out_file = os.path.join(seg_dir, f"story_{story_num:02d}.mp4")

    print(f"🎬 [सेगमेंट {story_num:02d}/{total_stories:02d}] रेंडरिंग: {comp_id} -> {os.path.basename(out_file)}...")
    cmd = [
        "npx", "remotion", "render",
        comp_id,
        f"out/segments/story_{story_num:02d}.mp4",
        "--concurrency=1"
    ]
    subprocess.run(cmd, cwd=BASE_DIR, check=True, shell=True)
    return out_file


def concat_segments_lossless(segment_files: list, output_file: str) -> bool:
    """FFmpeg Concat प्रोटोकॉल द्वारा सभी सेगमेंट्स को बिना री-एन्कोडिंग के 2 सेकंड में जोड़ता है"""
    print_banner("FFmpeg Lossless Concat: सेगमेंट्स को मास्टर वीडियो में जोड़ना...")
    if not segment_files:
        print("❌ कोई सेगमेंट फाइल नहीं मिली!")
        return False

    seg_dir = os.path.dirname(segment_files[0])
    list_file = os.path.join(seg_dir, "concat_list.txt")

    with open(list_file, "w", encoding="utf-8") as f:
        for seg in segment_files:
            rel_name = os.path.basename(seg)
            f.write(f"file '{rel_name}'\n")

    print(f"📄 Concat लिस्ट बनाई गई: {list_file}")
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "warning",
        "-f", "concat",
        "-safe", "0",
        "-i", "concat_list.txt",
        "-c", "copy",
        "-y",
        os.path.abspath(output_file)
    ]
    print(f"🚀 Concat कमांड चालू: {' '.join(cmd)}")
    start_c = time.time()
    try:
        subprocess.run(cmd, cwd=seg_dir, check=True)
        dur_c = round(time.time() - start_c, 2)
        print(f"🎉 मास्टर बुलेटिन लॉसलेस जुड़ा! (समय: {dur_c}s) -> {output_file}\n")
        return True
    except Exception as e:
        print(f"❌ Concat एरर: {e}")
        return False


def run_segmented_render(max_stories: int = None):
    """सभी या चुनिंदा सेगमेंट्स रेंडर करके उन्हें 100% लॉसलेस जोड़ता है"""
    print_banner("मास्टर टीवी न्यूज़: सेगमेंटेड रेंडरिंग & लॉसलेस Concat")
    clean_old_temp_files()

    if not os.path.exists(JSON_PATH):
        print(f"❌ JSON डेटा नहीं मिला: {JSON_PATH}")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        stories = json.load(f)

    if max_stories:
        stories = stories[:max_stories]

    total_count = len(stories)
    print(f"📊 कुल रेंडर होने वाले सेगमेंट्स: {total_count}\n")

    segment_files = []
    render_start = time.time()

    for idx, s in enumerate(stories, start=1):
        num = s.get("story_number", idx)
        try:
            seg_path = render_story_segment(num, total_stories=total_count)
            segment_files.append(seg_path)
        except Exception as e:
            print(f"❌ सेगमेंट #{num} रेंडर में एरर: {e}")
            return

    render_dur = round(time.time() - render_start, 2)
    print(f"\n✅ सभी {len(segment_files)} सेगमेंट्स रेंडर हुए! (कुल रेंडर समय: {render_dur}s)")

    # लॉसलेस Concat
    out_master = os.path.join(BASE_DIR, "out", "Mp4_News_Hindi_Bulletin_Full.mp4")
    concat_success = concat_segments_lossless(segment_files, out_master)

    if concat_success and os.path.exists(out_master):
        # स्वचालित 7-पॉइंट QA टेस्ट रन
        print_banner("स्वचालित 7-Point QA वेरिफिकेशन शुरू...")
        run_all_qa_checks(target_video=out_master)


def run_remotion_render():
    """फाइनल वीडियो MP4 रेंडर करता है (सिंगल कंपोजिशन मोड)"""
    print_banner("डायरेक्ट 1080p MP4 वीडियो रेंडर शुरू हो रहा है...")
    clean_old_temp_files()
    out_dir = os.path.join(BASE_DIR, "out")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "Mp4_News_Hindi_Bulletin_Full.mp4")

    cmd = [
        "npx", "remotion", "render",
        "DLSNewsBulletin",
        "out/Mp4_News_Hindi_Bulletin_Full.mp4",
        "--concurrency=1"
    ]
    print(f"🚀 कमांड: {' '.join(cmd)}")
    print(f"📁 आउटपुट फाइल: {out_file}\n")
    try:
        subprocess.run(cmd, cwd=BASE_DIR, check=True, shell=True)
        print(f"\n🎉 वीडियो रेंडरिंग सफल! फाइल यहाँ सेव हुई: {out_file}")
        # स्वचालित QA चेक
        run_all_qa_checks(target_video=out_file)
    except Exception as e:
        print(f"❌ रेंडरिंग एरर: {e}")


def run_full_pipeline(max_stories: int = None, auto_render: bool = False):
    """पूरे चरणों के ऑटोमेशन को क्रमबद्ध तरीके से चलाता है"""
    start_time = time.time()
    count_str = f"{max_stories} खबरें" if max_stories else "सभी खबरें"
    print_banner(f"DLS News मास्टर ऑटोमेशन पाइपलाइन चालू ({count_str})")

    # चरण 1: ताज़ा खबरें व AI स्क्रिप्ट
    print(f"\n🟢 [चरण 1/3] ताज़ा समाचार व Groq 120B AI स्क्रिप्टिंग ({count_str})...")
    stories = generate_dls_bulletin(max_stories=max_stories)
    if not stories:
        print("❌ चरण 1 में समस्या आई। पाइपलाइन रोकी जा रही है।")
        return

    # चरण 2: 100% असली विजुअल एसेट्स डाउनलोड
    print("\n🟢 [चरण 2/3] 100% असली न्यूज़ फोटोज़ वेब डाउनलोड...")
    download_all_assets(max_stories=max_stories)

    # चरण 3: Edge-TTS वॉइसओवर & टाइमिंग संवर्धन
    print("\n🟢 [चरण 3/3] Microsoft Edge-TTS हिंदी वॉइसओवर व टाइमिंग संवर्धन...")
    asyncio.run(generate_all_audios(max_stories=max_stories))
    process_audio_waveforms_and_metadata()

    total_time = round(time.time() - start_time, 2)
    print_banner(f"🎉 100% डेटा व एसेट्स पाइपलाइन पूर्ण! कुल समय: {total_time} सेकंड")
    show_bulletin_status()

    # चरण 4: स्वचालित 1080p वीडियो रेंडरिंग
    if auto_render:
        print_banner("🎬 स्वचालित 1080p वीडियो रेंडरिंग & लॉसलेस Concat शुरू...")
        run_segmented_render(max_stories=max_stories)
    else:
        print("👉 अगला कदम:")
        print("   1. प्रीव्यू देखने के लिए:     python run_pipeline.py --preview")
        print(f"   2. सेगमेंटेड रेंडर (सुरक्षित): python run_pipeline.py --segments {max_stories or 10}")
        print("   3. 7-पॉइंट QA टेस्ट रन:      python run_pipeline.py --qa\n")


def main():
    parser = argparse.ArgumentParser(
        description="DLS News 'हर खबर काम की' मास्टर पाइपलाइन रनर",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
उदाहरण:
  python run_pipeline.py              # पूरी 3-चरणीय पाइपलाइन चलाएं
  python run_pipeline.py --status     # वर्तमान बुलेटिन का डैशबोर्ड देखें
  python run_pipeline.py --news       # केवल AI से ताज़ा खबरें व स्क्रिप्ट बनाएं
  python run_pipeline.py --assets     # केवल B-Roll और इमेजेस डाउनलोड करें
  python run_pipeline.py --audio      # केवल वॉइसओवर ऑडियो बनाएं
  python run_pipeline.py --preview    # Remotion स्टूडियो चलाएं
  python run_pipeline.py --segments 3 # पहले 3 सेगमेंट्स का टेस्ट रेंडर + Concat
  python run_pipeline.py --segments   # सभी 10 सेगमेंट्स रेंडर + Concat + QA
  python run_pipeline.py --render     # डायरेक्ट फुल कंपोजिशन रेंडर
  python run_pipeline.py --qa         # 7-पॉइंट QA टेस्ट चलाएं
        """
    )
    parser.add_argument("-s", "--status", action="store_true", help="वर्तमान बुलेटिन स्टेटस देखें")
    parser.add_argument("-n", "--news", action="store_true", help="केवल चरण 1 चलाएं: ताज़ा खबरें + AI स्क्रिप्ट")
    parser.add_argument("-a", "--assets", action="store_true", help="केवल चरण 2 चलाएं: B-Roll व इमेजेस डाउनलोड")
    parser.add_argument("-v", "--audio", action="store_true", help="केवल चरण 3 चलाएं: Edge-TTS वॉइसओवर जनरेट")
    parser.add_argument("-p", "--preview", action="store_true", help="Remotion स्टूडियो प्रीव्यू चालू करें")
    parser.add_argument("-r", "--render", action="store_true", help="डायरेक्ट फुल वीडियो MP4 रेंडर करें")
    parser.add_argument("--segments", nargs="?", const=10, type=int, help="सेगमेंटेड रेंडर + FFmpeg Concat (वैकल्पिक: स्टोरी संख्या, जैसे --segments 3)")
    parser.add_argument("--count", type=int, default=None, help="खबरों की संख्या निर्धारित करें (उदा: --count 5)")
    parser.add_argument("--auto-render", action="store_true", help="पाइपलाइन के तुरंत बाद स्वचालित 1080p वीडियो रेंडर करें")
    parser.add_argument("--autopilot", action="store_true", help="100% स्वायत्त ऑटोपायलट: AI स्क्रिप्ट, 10-15 इमेजेस (वॉटरमार्क क्रॉप्ड), TTS, रेंडर और QA")
    parser.add_argument("--qa", action="store_true", help="7-पॉइंट QA क्वालिटी टेस्ट चलाएं")
    parser.add_argument("--clean", action="store_true", help="सभी पुरानी टेस्ट व टेम्पररी फाइल्स को डिलीट करें")

    args = parser.parse_args()

    if args.status:
        show_bulletin_status()
    elif args.clean:
        clean_old_temp_files()
    elif args.news:
        print_banner("केवल समाचार व AI स्क्रिप्टिंग")
        generate_dls_bulletin(max_stories=args.count)
    elif args.assets:
        print_banner("केवल मीडिया एसेट्स डाउनलोड")
        download_all_assets(max_stories=args.count)
    elif args.audio:
        print_banner("केवल वॉइसओवर ऑडियो जेनरेशन")
        asyncio.run(generate_all_audios(max_stories=args.count))
    elif args.preview:
        run_remotion_preview()
    elif args.segments is not None:
        run_segmented_render(max_stories=args.segments)
    elif args.render:
        run_remotion_render()
    elif args.qa:
        run_all_qa_checks()
    elif args.autopilot:
        run_full_pipeline(max_stories=args.count, auto_render=True)
    else:
        run_full_pipeline(max_stories=args.count, auto_render=args.auto_render)


if __name__ == "__main__":
    main()
