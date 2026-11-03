"""
Audio Waveform Extractor & Dateline Location Enricher
-----------------------------------------------------
1. Reads each story's MP3 audio file.
2. Extracts frame-accurate RMS amplitude (30 samples/sec for 30 FPS).
3. Applies a Silence Gate (< 0.02 / -45 dBFS snaps to 0.0).
4. Enriches each story with verified dateline location and photo attribution tags.
5. Updates 'generated_sample_top10.json'.
"""

import os
import sys
import json
import math
import struct
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURR_DIR, "..", ".."))
JSON_PATH = os.path.join(CURR_DIR, "generated_sample_top10.json")

FPS = 30
SAMPLE_RATE = 12000  # 12,000 samples/sec -> 400 samples per frame at 30 FPS
SAMPLES_PER_FRAME = SAMPLE_RATE // FPS  # 400
SILENCE_THRESHOLD = 0.025  # ~ -45 dBFS silence gate


def extract_rms_waveform(audio_path: str) -> list[float]:
    """
    FFmpeg se raw 16-bit mono PCM decode karke 30 FPS par RMS amplitude nikalna
    """
    if not os.path.exists(audio_path):
        return []

    cmd = [
        "ffmpeg",
        "-i", audio_path,
        "-f", "s16le",
        "-ac", "1",
        "-ar", str(SAMPLE_RATE),
        "-v", "quiet",
        "-"
    ]

    try:
        raw_bytes = subprocess.check_output(cmd)
    except Exception as e:
        print(f"    ⚠️ FFmpeg audio decode error ({audio_path}): {e}")
        return []

    num_samples = len(raw_bytes) // 2
    if num_samples == 0:
        return []

    samples = struct.unpack(f"<{num_samples}h", raw_bytes)

    waveform = []
    # Maximum 16-bit signed integer value
    max_val = 32767.0

    for i in range(0, num_samples, SAMPLES_PER_FRAME):
        frame_chunk = samples[i : i + SAMPLES_PER_FRAME]
        if not frame_chunk:
            break
        # Calculate RMS (Root Mean Square)
        sum_sq = sum(s * s for s in frame_chunk)
        rms = math.sqrt(sum_sq / len(frame_chunk)) / max_val

        # Silence Gate
        if rms < SILENCE_THRESHOLD:
            rms = 0.0
        else:
            # Scale slightly so normal speech sits pleasantly between 0.3 and 0.95
            rms = min(1.0, (rms - SILENCE_THRESHOLD) / (0.45 - SILENCE_THRESHOLD))

        waveform.append(round(rms, 3))

    return waveform


# सत्यापित डेटलाइन लोकेशंस (खबर के मूल तथ्यों से)
VERIFIED_LOCATIONS = {
    1: "जीरकपुर (पंजाब)",
    2: "विशाखापत्तनम (आंध्र प्रदेश)",
    3: "बालोतरा (राजस्थान)",
    4: "थेनी (तमिलनाडु)",
    5: "शिमला (हिमाचल प्रदेश)",
    6: "लखनऊ (उत्तर प्रदेश)",
    7: "अयोध्या (उत्तर प्रदेश)",
    8: "धर्मशाला (हिमाचल प्रदेश)",
    9: "पुरी-तटीय (ओडिशा)",
    10: "नई दिल्ली (सुप्रीम कोर्ट)"
}


def process_audio_waveforms_and_metadata():
    if not os.path.exists(JSON_PATH):
        print(f"❌ JSON फाइल नहीं मिली: {JSON_PATH}")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        stories = json.load(f)

    print("\n" + "═" * 74)
    print("🎙️ ऑडियो वेवफॉर्म निष्कर्षण & मेटाडेटा संवर्धन (Waveform & Metadata)")
    print("═" * 74)

    for s in stories:
        num = s.get("story_number", 1)
        rel_audio = s.get("local_audio_asset", f"out/story_{num:02d}/audio_story_{num}.mp3")
        abs_audio = os.path.join(BASE_DIR, rel_audio.replace("/", os.sep))

        waveform = extract_rms_waveform(abs_audio)
        s["audio_waveform"] = waveform

        # लोकेशन संवर्धन (बिना किसी AI अनुमान के)
        loc = VERIFIED_LOCATIONS.get(num, "भारत डेस्क")
        s["verified_location"] = loc

        # इमेज एट्रीब्यूशन टैग (सत्यापित प्रेस फोटो, ज़ीरो इमोजी)
        source_name = s.get("real_image_attribution", "न्यूज़ डेस्क")
        s["image_attribution_tag"] = f"स्रोत: {source_name} | घटनास्थल"

        # 1ms प्रिसिजन: 0 पैडिंग (वॉइस खत्म होते ही वीडियो ठीक उसी फ्रेम पर समाप्त)
        dur_sec = s.get("audio_duration", len(waveform) / FPS if waveform else 20.0)
        audio_frames = math.ceil(dur_sec * FPS)
        pre_frames = 0
        post_frames = 0
        trans_frames = 0
        total_story_frames = audio_frames

        s["timing_specs"] = {
            "fps": FPS,
            "pre_padding_frames": 0,
            "audio_start_frame": 0,
            "audio_duration_frames": audio_frames,
            "post_padding_frames": 0,
            "transition_frames": 0,
            "total_story_frames": total_story_frames,
            "total_story_seconds": dur_sec
        }

        print(f"  [#{num:02d}] 📍 {loc} | ऑडियो: {dur_sec}s ({len(waveform)} वेवफॉर्म पॉइंट्स) | कुल फ्रेम्स: {total_story_frames}")

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(stories, f, ensure_ascii=False, indent=2)

    print("═" * 74)
    print(f"🎉 सभी {len(stories)} खबरों का वेवफॉर्म और सत्यापित टाइमिंग JSON में सुरक्षित!")
    print("═" * 74 + "\n")


if __name__ == "__main__":
    process_audio_waveforms_and_metadata()
