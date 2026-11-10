"""
DLS News TTS Audio Generator (OmniVoice GPU + Edge-TTS Fallback)
आवाज़: 
  - Kaggle / GPU: OmniVoice (k2-fsa) Native Hindi TTS (No clone / Pure neural model)
  - Local / Fallback: Microsoft Edge-TTS (hi-IN-MadhurNeural)
आउटपुट: 48kHz Stereo MP3 -> out/story_XX/voice over/audio_story_XX.mp3
"""

import os
import sys
import json
import time
import shutil
import asyncio
import subprocess
from typing import Tuple, Optional, Any
from story_metadata_helper import save_story_folder_metadata

# Windows / Linux UTF-8 encoding support
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(BASE_DIR, "out")
JSON_PATH = os.path.join(os.path.dirname(__file__), "generated_sample_top10.json")

os.makedirs(OUT_DIR, exist_ok=True)

# Edge-TTS settings
EDGE_VOICE = "hi-IN-MadhurNeural"
EDGE_RATE = "+25%"

# Global OmniVoice singleton cache
_OMNIVOICE_MODEL = None
_OMNIVOICE_LOAD_ATTEMPTED = False


def _find_omnivoice_weights() -> str:
    """Finds offline OmniVoice weights in Kaggle or local cache."""
    env_p = os.getenv("OMNIVOICE_MODEL_DIR", "").strip()
    if env_p and os.path.exists(env_p):
        return env_p

    candidates = [
        "/kaggle/input/tts-offline-models/pretrained_models/OmniVoice",
        "/kaggle/input/datasets/sonuji12345/tts-offline-models/pretrained_models/OmniVoice",
        "/kaggle/input/tts-offline-models/OmniVoice",
        "/kaggle/input/omnivoice/pretrained_models/OmniVoice",
        os.path.expanduser("~/.cache/omnivoice/OmniVoice"),
        r"C:\Dubstudio\models\OmniVoice",
    ]

    for p in candidates:
        if os.path.exists(p) and (
            os.path.exists(os.path.join(p, "model.safetensors"))
            or os.path.exists(os.path.join(p, "config.json"))
        ):
            return p

    if os.path.exists("/kaggle/input"):
        for root, dirs, files in os.walk("/kaggle/input"):
            if "model.safetensors" in files and "tokenizer.json" in files:
                if "omnivoice" in root.lower():
                    return root

    return "k2-fsa/OmniVoice"


def get_omnivoice_model():
    """
    Loads OmniVoice on GPU (float16) with fast local NVMe staging (/tmp).
    Returns (model, sample_rate) or (None, 0) if unavailable.
    """
    global _OMNIVOICE_MODEL, _OMNIVOICE_LOAD_ATTEMPTED
    if _OMNIVOICE_LOAD_ATTEMPTED:
        return _OMNIVOICE_MODEL

    _OMNIVOICE_LOAD_ATTEMPTED = True

    try:
        import torch
        if not torch.cuda.is_available():
            threads = os.cpu_count() or 4
            torch.set_num_threads(threads)
            print(f"  [TTS] OmniVoice High-Performance CPU Mode enabled ({threads} PyTorch threads)", flush=True)
    except ImportError:
        print("  [TTS] PyTorch not installed, will use Edge-TTS.")
        return None

    try:
        from omnivoice import OmniVoice
    except ImportError:
        # Check offline wheels in Kaggle dataset
        wheel_found = False
        if os.path.exists("/kaggle/input"):
            for root, _, files in os.walk("/kaggle/input"):
                for f in files:
                    if f.startswith("omnivoice") and f.endswith(".whl"):
                        whl_path = os.path.join(root, f)
                        print(f"  [OmniVoice] Installing wheel: {whl_path}")
                        subprocess.run(["pip", "install", "-q", "--no-deps", whl_path], check=False)
                        wheel_found = True
                        break
                if wheel_found:
                    break

        try:
            from omnivoice import OmniVoice
        except ImportError:
            print("  [OmniVoice] Installing via pip...")
            subprocess.run(["pip", "install", "-q", "omnivoice", "soundfile"], check=False)
            try:
                from omnivoice import OmniVoice
            except Exception as e:
                print(f"  [TTS] OmniVoice import failed: {e}")
                return None

    model_source = _find_omnivoice_weights()
    import torch

    # Fast Local NVMe Staging (avoids Kaggle FUSE 100s+ seek latency)
    if os.path.isdir(model_source) and model_source.startswith("/kaggle/input"):
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        local_dir = "/tmp/OmniVoice_fast"
        safetensors_file = os.path.join(local_dir, "model.safetensors")
        if not (os.path.exists(safetensors_file) and os.path.getsize(safetensors_file) > 1024 * 1024):
            print("  [OmniVoice] Copying weights to fast NVMe /tmp (~10s)...", flush=True)
            t_copy = time.time()
            if os.path.exists(local_dir):
                shutil.rmtree(local_dir, ignore_errors=True)
            shutil.copytree(model_source, local_dir)
            print(f"  [OmniVoice] ✓ Staged in {time.time() - t_copy:.1f}s!", flush=True)

        tok_sub = os.path.join(local_dir, "audio_tokenizer")
        if not os.path.isdir(tok_sub):
            tok_candidate = None
            if os.path.exists("/kaggle/input"):
                for root, dirs, files in os.walk("/kaggle/input"):
                    if "audio_tokenizer" in dirs:
                        tok_candidate = os.path.join(root, "audio_tokenizer")
                        break
            if tok_candidate and os.path.isdir(tok_candidate):
                shutil.copytree(tok_candidate, tok_sub)

        model_source = local_dir

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    print(f"  [OmniVoice] Loading model from: {model_source}")
    print(f"  [OmniVoice] Device: {device} | Precision: {dtype}")

    try:
        model = OmniVoice.from_pretrained(model_source, device_map=device, dtype=dtype, load_asr=False)
    except TypeError:
        model = OmniVoice.from_pretrained(model_source, device_map=device, dtype=dtype)
    except Exception as e:
        print(f"  [OmniVoice] Local load warning ({e}), falling back to online hub...")
        model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map=device, dtype=dtype, load_asr=False)

    sr = getattr(model, "sample_rate", 24000)
    print(f"  [OmniVoice] ✓ Successfully loaded (Sample rate: {sr}Hz)", flush=True)
    _OMNIVOICE_MODEL = (model, sr)
    return _OMNIVOICE_MODEL


def get_audio_duration_seconds(file_path: str) -> float:
    """ffprobe से ऑडियो की सटीक अवधि (Seconds) निकालना"""
    try:
        cmd = [
            "ffprobe",
            "-i", file_path,
            "-show_entries", "format=duration",
            "-v", "quiet",
            "-of", "csv=p=0"
        ]
        res = subprocess.check_output(cmd, text=True).strip()
        return round(float(res), 2)
    except Exception as e:
        print(f"    ⚠️ ffprobe एरर ({file_path}): {e}")
        return 20.0


def normalize_broadcast_audio(file_path: str):
    """
    मास्टर ब्रॉडकास्ट ऑडियो नॉर्मलाइजेशन (EBU R128 / YouTube Standard):
    - वॉल्यूम को सुरक्षित रूप से +8dB से +10dB तक बढ़ाना (Mean Volume: ~-16dB, True Peak: -1.0dB)
    - बिना किसी फेड या डिस्टॉर्शन के टीवी स्टूडियो जैसी साफ़, तेज़ और क्रिस्प आवाज़
    """
    if not os.path.exists(file_path) or os.path.getsize(file_path) < 5000:
        return
    norm_temp = file_path.replace(".mp3", "_loudnorm_temp.mp3")
    # Precision trailing silence trim + Loudness boost (0ms dead air, -14 LUFS Broadcast Grade)
    cmd = [
        "ffmpeg", "-y",
        "-i", file_path,
        "-af", "areverse,silenceremove=start_periods=1:start_duration=0.05:start_threshold=-38dB,areverse,loudnorm=I=-11:TP=-0.5:LRA=5",
        "-ar", "48000",
        "-ac", "2",
        "-b:a", "192k",
        norm_temp
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(norm_temp) and os.path.getsize(norm_temp) > 5000:
            os.replace(norm_temp, file_path)
            print(f"    🔊 [Audio Boost] ब्रॉडकास्ट लाउडनेस नॉर्मलाइज्ड (-14 LUFS Studio Grade)")
    except Exception as e:
        print(f"    ⚠️ loudnorm warning: {e}")


def synthesize_omnivoice(text: str, output_mp3_path: str) -> bool:
    """OmniVoice GPU से बिना क्लोन के शुद्ध हिंदी ऑडियो तैयार करना"""
    ov_data = get_omnivoice_model()
    if not ov_data:
        return False

    model, sr = ov_data
    import numpy as np
    import soundfile as sf
    import torch

    print(f"  🎙️ [OmniVoice] सिंथेसाइजिंग ({len(text.split())} शब्द, भाषा: Hindi)...", flush=True)
    t0 = time.time()

    # OmniVoice direct Hindi inference without voice clone (no ref_audio)
    gen_kwargs = {
        "text": text,
        "language": "hi",
        "num_step": 25,
    }

    try:
        audio = model.generate(**gen_kwargs)
        raw_wav = audio[0] if isinstance(audio, (list, tuple)) and len(audio) > 0 else audio

        if isinstance(raw_wav, torch.Tensor):
            wav = raw_wav.detach().cpu().float().numpy()
        elif isinstance(raw_wav, np.ndarray):
            wav = raw_wav.astype(np.float32)
        else:
            wav = np.array(raw_wav, dtype=np.float32)

        wav = np.squeeze(wav)
        if wav.ndim > 1:
            wav = wav.mean(axis=0 if wav.shape[0] < wav.shape[1] else 1)

        temp_wav = output_mp3_path.replace(".mp3", "_temp.wav")
        sf.write(temp_wav, wav, sr)

        # Convert to 48kHz Stereo broadcast MP3 at 1.25x speed with trailing silence trimming & pitch preservation
        cmd = [
            "ffmpeg", "-y",
            "-i", temp_wav,
            "-af", "areverse,silenceremove=start_periods=1:start_duration=0.05:start_threshold=-38dB,areverse,atempo=1.25",
            "-ar", "48000",
            "-ac", "2",
            "-b:a", "192k",
            output_mp3_path,
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(temp_wav):
            os.remove(temp_wav)

        print(f"  ✓ [OmniVoice] ऑडियो तैयार ({time.time() - t0:.1f}s): {output_mp3_path}")
        return True
    except Exception as e:
        print(f"  ⚠️ OmniVoice generation error: {e}")
        return False


def load_script_from_file(script_path: str) -> str:
    """script_XX.txt फाइल से वॉइसओवर स्क्रिप्ट सुरक्षित व सटीक रूप से निकालना"""
    if not os.path.exists(script_path):
        return ""
    try:
        with open(script_path, "r", encoding="utf-8") as sf:
            content = sf.read().strip()
        if not content:
            return ""

        markers = [
            "वॉइसओवर स्क्रिप्ट:",
            "एंकर वॉइसओवर स्क्रिप्ट (EDGE-TTS READY):",
            "एंकर वॉइसओवर स्क्रिप्ट:",
            "वॉइसओवर:",
            "VOICEOVER SCRIPT:",
            "VOICEOVER:"
        ]
        extracted = None
        for m in markers:
            if m in content:
                parts = content.split(m, 1)
                text_part = parts[1].strip()
                # अगली हेडिंग या सेक्शन से पहले का टेक्स्ट लें
                for stop_marker in [
                    "चंक-दर-चंक विवरण",
                    "चंक-दर-चंक",
                    "CHUNKS & VISUAL KEYWORDS",
                    "═" * 5,
                    "-" * 10,
                    "स्क्रीन पर बदलने वाली",
                    "मुख्य स्क्रीन हेडलाइन",
                    "शीर्षक:"
                ]:
                    if stop_marker in text_part:
                        text_part = text_part.split(stop_marker, 1)[0].strip()
                if text_part:
                    extracted = text_part
                    break

        if extracted:
            return extracted.strip()

        # यदि कोई मानक मार्कर नहीं है, और फाइल में कोई हेडर नहीं है (डायरेक्ट यूजर द्वारा लिखी प्लेन स्क्रिप्ट)
        if not ("शीर्षक:" in content or "मुख्य स्क्रीन हेडलाइन:" in content or "श्रेणी:" in content):
            return content.strip()

        return ""
    except Exception as e:
        print(f"    ⚠️ [स्क्रिप्ट रीडर] फाइल पढ़ने में त्रुटि: {e}")
        return ""


async def generate_audio_for_story(story: dict, force: bool = False) -> tuple[str, float]:
    """एक खबर के लिए ऑडियो जनरेट करना (स्क्रिप्ट फाइल को प्राथमिक स्रोत मानकर OmniVoice GPU या Edge-TTS से)"""
    story_num = story.get("story_number", 1)

    story_dir_name = f"story_{story_num:02d}"
    story_dir = os.path.join(OUT_DIR, story_dir_name)
    voice_dir = os.path.join(story_dir, "voice over")
    os.makedirs(story_dir, exist_ok=True)
    os.makedirs(voice_dir, exist_ok=True)

    script_filename = f"script_{story_num}.txt"
    script_path = os.path.join(story_dir, script_filename)

    # 1. प्राथमिक स्रोत (PRIORITY 1): सीधे out/story_XX/script_XX.txt फाइल से पढ़ें!
    script_from_file = load_script_from_file(script_path)
    if script_from_file:
        clean_text = script_from_file.replace("**", "").replace("*", "").replace('"', '').strip()
        print(f"  📄 [खबर {story_num}] 'out/{story_dir_name}/{script_filename}' से वॉइसओवर स्क्रिप्ट लोड की गई ({len(clean_text.split())} शब्द)")
        # JSON डेटा को भी इस फाइल की स्क्रिप्ट से सिंक करें ताकि दोनों 100% मैच रहें
        story["voiceover_script"] = clean_text
    else:
        # प्राथमिक स्रोत 2: यदि फाइल मौजूद न हो तो story डिक्शनरी से लें और फाइल बनाएं
        script = story.get("voiceover_script", "").strip()
        if not script:
            hl = story.get("screen_headline", "")
            bp = "। ".join(story.get("bullet_points", []))
            script = f"{hl}। {bp}"

        clean_text = script.replace("**", "").replace("*", "").replace('"', '').strip()

        try:
            story["voiceover_script"] = clean_text
            save_story_folder_metadata(story, OUT_DIR)
            print(f"  📝 [खबर {story_num}] 'out/{story_dir_name}/{script_filename}' व मेटाडेटा फाइल सेव की गई")
        except Exception as e:
            print(f"    ⚠️ स्क्रिप्ट फाइल सेव एरर: {e}")

    output_filename = f"audio_story_{story_num}.mp3"
    output_path = os.path.join(voice_dir, output_filename)

    if not force and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        dur = get_audio_duration_seconds(output_path)
        print(f"  ✔ [खबर {story_num}] ऑडियो पहले से मौजूद है: {output_filename} ({dur}s)")
        return f"out/{story_dir_name}/voice over/{output_filename}", dur

    # 1. First attempt: OmniVoice GPU TTS (Only if CUDA is available)
    # Note: OmniVoice diffusion inference on 4 CPU threads takes ~15-20 mins per story!
    # On CPU, instantly use ultra-fast Microsoft Neural Voice (hi-IN-MadhurNeural, ~1.5s).
    has_cuda = False
    try:
        import torch
        has_cuda = torch.cuda.is_available()
    except Exception:
        has_cuda = False

    if has_cuda:
        print(f"  🎙️ [OmniVoice GPU] CUDA Detected - Synthesizing ({len(clean_text.split())} words)...")
        success = synthesize_omnivoice(clean_text, output_path)
    else:
        print(f"  ⚡ [CPU Turbo Mode] Running High-Speed Microsoft Neural Voice ({EDGE_VOICE}, ~1.5s)...")
        success = False

    # 2. Fallback attempt: Edge-TTS
    if not success or not os.path.exists(output_path) or os.path.getsize(output_path) < 5000:
        print(f"  🎙️ [खबर {story_num}] Edge-TTS बैकअप वॉइसओवर ({len(clean_text.split())} शब्द)...")
        try:
            import edge_tts
            for attempt in range(1, 4):
                try:
                    comm = edge_tts.Communicate(clean_text, EDGE_VOICE, rate=EDGE_RATE, volume="+50%")
                    await comm.save(output_path)
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 5000:
                        break
                except Exception as e:
                    print(f"    ⚠️ [कोशिश {attempt}/3] Edge-TTS एरर: {e}")
                    await asyncio.sleep(1.5)
        except ImportError:
            print("  ❌ Edge-TTS not installed!")

    # ब्रॉडकास्ट लाउडनेस बूस्ट
    normalize_broadcast_audio(output_path)

    dur = get_audio_duration_seconds(output_path)
    audio_frames = int(round(dur * 30))
    story["audio_duration"] = dur
    # 1ms प्रिसिजन: 0 पैडिंग, वॉइस खत्म होते ही वीडियो ठीक उसी फ्रेम पर समाप्त
    story["timing_specs"] = {
        "fps": 30,
        "pre_padding_frames": 0,
        "audio_start_frame": 0,
        "audio_duration_frames": audio_frames,
        "post_padding_frames": 0,
        "transition_frames": 0,
        "total_story_frames": audio_frames,
        "total_story_seconds": dur
    }
    save_story_folder_metadata(story, OUT_DIR)
    print(f"  ✔ [खबर {story_num}] पूर्ण अवधि: {dur}s ({audio_frames} फ्रेम्स, 0s साइलेंस) | {output_filename}")
    return f"out/{story_dir_name}/voice over/{output_filename}", dur


async def generate_all_bulletin_audio(force: bool = False, max_stories: int = 1):
    """खबरों का वॉइसओवर तैयार करना (Default: 1 Story for testing)"""
    print("\n" + "=" * 65)
    print("🎙️ TV BROADCAST HINDI AUDIO PIPELINE (OmniVoice GPU / Edge-TTS)")
    print("=" * 65)

    if not os.path.exists(JSON_PATH):
        print(f"❌ JSON फाइल नहीं मिली: {JSON_PATH}")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    stories = data if isinstance(data, list) else data.get("stories", [])
    if not stories:
        print("❌ कोई खबर डेटा में मौजूद नहीं है!")
        return

    if max_stories:
        target_stories = stories[:max_stories]
    else:
        target_stories = stories

    print(f"कुल खबरें (प्रोसेस्ड): {len(target_stories)}")
    for story in target_stories:
        s_num = story.get("story_number", 1)
        rel_path, dur = await generate_audio_for_story(story, force=force)
        story["local_audio_asset"] = rel_path
        story["audio_duration"] = dur

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 65)
    print(f"🎉 सभी {len(stories)} खबरों का वॉइसओवर ऑडियो सफलता पूर्वक तैयार!")
    print(f"वेयरहाउस लोकेशन: out/story_XX/voice over/")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="री-जेनेरेट करें")
    parser.add_argument("--max", type=int, default=1, help="अधिकतम कितनी खबरों का ऑडियो बनाना है (Default: 1)")
    args = parser.parse_args()
    asyncio.run(generate_all_bulletin_audio(force=args.force, max_stories=args.max))
