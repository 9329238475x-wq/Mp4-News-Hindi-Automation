"""
Groq AI Engine with Multi-Key Failover & Round-Robin Load Balancing (Python 3)
मॉडल: openai/gpt-oss-20b (Ultra-Fast 1.8s Response & High Throughput)
"""

import os
import sys
import json
import re
import time
import requests
from dotenv import load_dotenv

# Windows UTF-8 एनकोडिंग सपोर्ट
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# .env फ़ाइल लोड करें
load_dotenv()


class GroqEngine:
    def __init__(self, model: str = None):
        self.model = model or os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
        self.keys = []
        self.current_key_index = 0

        # GROQ_API_KEYS (कॉमा-सेपरेटेड लिस्ट)
        raw_keys = os.getenv("GROQ_API_KEYS", "") or os.getenv("GROQ_API_KEY", "")
        if raw_keys:
            self.keys = [k.strip() for k in raw_keys.split(",") if k.strip()]

        # बैकअप व्यक्तिगत Keys
        if not self.keys:
            for i in range(1, 11):
                k = os.getenv(f"GROQ_API_KEY_{i}")
                if k:
                    self.keys.append(k.strip())

        if not self.keys:
            print("⚠️ चेतावनी: कोई भी Groq API Key नहीं मिली! कृपया .env फ़ाइल चेक करें।", flush=True)
        else:
            print(f"🤖 Groq Python इंजन तैयार: {len(self.keys)} सक्रिय Keys लोड की गईं (Model: {self.model})", flush=True)

    def _get_active_key(self) -> tuple:
        """Round-robin key selector to distribute load evenly across all keys"""
        idx = self.current_key_index
        key = self.keys[idx]
        self.current_key_index = (self.current_key_index + 1) % len(self.keys)
        return idx, key

    def _rotate_key(self):
        prev = self.current_key_index
        self.current_key_index = (self.current_key_index + 1) % len(self.keys)
        print(f"🔄 Groq Key स्विच: Key #{prev + 1} ➡️ Key #{self.current_key_index + 1}", flush=True)

    def chat_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.6) -> dict:
        """
        Groq API को कॉल करके सीधा वैध JSON डिक्शनरी लौटाता है (Round-robin distributed)
        """
        if not self.keys:
            raise ValueError("कोई Groq API Key उपलब्ध नहीं है।")

        attempts = 0
        max_attempts = max(len(self.keys) * 4, 20)

        while attempts < max_attempts:
            key_idx, key = self._get_active_key()
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt + "\nCRITICAL: Output strictly a single valid JSON object. No preamble, no postamble."},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "max_completion_tokens": 2048
            }

            try:
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=(8, 25)
                )

                # 429 = Rate Limit, 401 = Invalid Key
                if resp.status_code in (429, 401):
                    cooldown = 1.0
                    try:
                        err_msg = resp.json().get("error", {}).get("message", "")
                        match_t = re.search(r"try again in ([\d\.]+)s", err_msg)
                        if match_t:
                            cooldown = min(float(match_t.group(1)), 5.0)
                    except Exception:
                        pass
                    if "retry-after" in resp.headers:
                        try:
                            cooldown = min(float(resp.headers["retry-after"]), 5.0)
                        except Exception:
                            pass
                    # If whole round of keys completed, add extra breathing room
                    if attempts > 0 and (attempts % len(self.keys) == 0):
                        cooldown = max(cooldown, 2.5)

                    print(f"⚠️ Groq Key #{key_idx + 1} पर स्टेटस {resp.status_code} मिला, {cooldown:.1f}s इंतज़ार के बाद अगली Key...", flush=True)
                    time.sleep(cooldown)
                    attempts += 1
                    continue

                if not resp.ok:
                    raise RuntimeError(f"Groq HTTP Error {resp.status_code}: {resp.text}")

                data = resp.json()
                raw_text = data["choices"][0]["message"]["content"].strip()

                # Robust JSON parser
                parsed = None
                try:
                    parsed = json.loads(raw_text)
                except Exception:
                    json_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", raw_text)
                    if json_match:
                        try:
                            parsed = json.loads(json_match.group(1))
                        except Exception:
                            pass
                    if parsed is None:
                        cleaned = re.sub(r"```(?:json)?", "", raw_text).strip()
                        parsed = json.loads(cleaned)

                # हेडलाइन से किसी भी ** को हटाएँ
                if isinstance(parsed, dict) and "stories" in parsed and isinstance(parsed["stories"], list):
                    for s in parsed["stories"]:
                        if isinstance(s, dict) and "screen_headline" in s and isinstance(s["screen_headline"], str):
                            s["screen_headline"] = s["screen_headline"].replace("**", "").replace("*", "").strip()

                return parsed

            except requests.RequestException as e:
                print(f"❌ नेटवर्क नोटिस (Key #{key_idx + 1}): {e}, अगली Key पर स्विच...", flush=True)
                time.sleep(1.0)
                attempts += 1
            except json.JSONDecodeError as e:
                print(f"❌ JSON पार्सिंग त्रुटि: {e}", flush=True)
                time.sleep(0.5)
                attempts += 1

        raise RuntimeError("सभी Groq API Keys समाप्त हो गईं या कनेक्शन में समस्या है।")
