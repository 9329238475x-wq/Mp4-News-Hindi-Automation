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
EDGE_RATE = "+6%"

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
            print("  [TTS] CUDA/GPU not available, will use Edge-TTS.")
            return None
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


def synthesize_omnivoice(text: str, output_mp3_path: str) -> bool:
    """OmniVoice GPU से बिना क्लोन के शुद्ध हिंदी ऑडियो तैयार करना"""
    ov_data = get_omnivoice_model()
    if not ov_data:
        return False

    model, sr = ov_data
    import numpy as np
    import soundfile as sf
    import torch

    print(f"  🎙️ [OmniVoice GPU] सिंथेसाइजिंग ({len(text.split())} शब्द, भाषा: Hindi)...", flush=True)
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

        # Convert to 48kHz Stereo broadcast MP3
        cmd = [
            "ffmpeg", "-y",
            "-i", temp_wav,
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


async def generate_audio_for_story(story: dict, force: bool = False) -> tuple[str, float]:
    """एक खबर के लिए ऑडियो जनरेट करना (OmniVoice GPU या Edge-TTS फॉलबैक)"""
    story_num = story.get("story_number", 1)
    script = story.get("voiceover_script", "").strip()

    if not script:
        hl = story.get("screen_headline", "")
        bp = "। ".join(story.get("bullet_points", []))
        script = f"{hl}। {bp}"

    clean_text = script.replace("**", "").replace("*", "").replace('"', '').strip()

    story_dir_name = f"story_{story_num:02d}"
    story_dir = os.path.join(OUT_DIR, story_dir_name)
    voice_dir = os.path.join(story_dir, "voice over")
    os.makedirs(story_dir, exist_ok=True)
    os.makedirs(voice_dir, exist_ok=True)

    script_filename = f"script_{story_num}.txt"
    script_path = os.path.join(story_dir, script_filename)
    try:
        with open(script_path, "w", encoding="utf-8") as sf:
            sf.write(f"शीर्षक: {story.get('screen_headline', '')}\n")
            sf.write(f"श्रेणी: {story.get('category', 'न्यूज़')}\n")
            sf.write("═" * 50 + "\n\n")
            sf.write("वॉइसओवर स्क्रिप्ट:\n")
            sf.write(clean_text + "\n")
    except Exception as e:
        print(f"    ⚠️ स्क्रिप्ट फाइल सेव एरर: {e}")

    output_filename = f"audio_story_{story_num}.mp3"
    output_path = os.path.join(voice_dir, output_filename)

    if not force and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        dur = get_audio_duration_seconds(output_path)
        print(f"  ✔ [खबर {story_num}] ऑडियो पहले से मौजूद है: {output_filename} ({dur}s)")
        return f"out/{story_dir_name}/voice over/{output_filename}", dur

    # 1. First attempt: OmniVoice GPU TTS
    success = synthesize_omnivoice(clean_text, output_path)

    # 2. Fallback attempt: Edge-TTS
    if not success or not os.path.exists(output_path) or os.path.getsize(output_path) < 5000:
        print(f"  🎙️ [खबर {story_num}] Edge-TTS बैकअप वॉइसओवर ({len(clean_text.split())} शब्द)...")
        try:
            import edge_tts
            for attempt in range(1, 4):
                try:
                    comm = edge_tts.Communicate(clean_text, EDGE_VOICE, rate=EDGE_RATE)
                    await comm.save(output_path)
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 5000:
                        break
                except Exception as e:
                    print(f"    ⚠️ [कोशिश {attempt}/3] Edge-TTS एरर: {e}")
                    await asyncio.sleep(1.5)
        except ImportError:
            print("  ❌ Edge-TTS not installed!")

    dur = get_audio_duration_seconds(output_path)
    print(f"  ✔ [खबर {story_num}] पूर्ण अवधि: {dur}s | {output_filename}")
    return f"out/{story_dir_name}/voice over/{output_filename}", dur


async def generate_all_bulletin_audio(force: bool = False):
    """सभी 10 खबरों का वॉइसओवर तैयार करना और JSON को अपडेट करना"""
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

    print(f"कुल खबरें: {len(stories)}")
    for story in stories:
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
    force_run = "--force" in sys.argv
    asyncio.run(generate_all_bulletin_audio(force=force_run))
