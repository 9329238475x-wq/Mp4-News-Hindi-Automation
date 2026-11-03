"""
Groq AI Engine with Multi-Key Failover (Python 3)
मॉडल: openai/gpt-oss-120b
"""

import os
import sys
import json
import re
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
        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self.keys = []
        self.current_key_index = 0

        # GROQ_API_KEYS (कॉमा-सेपरेटेड लिस्ट)
        raw_keys = os.getenv("GROQ_API_KEYS", "")
        if raw_keys:
            self.keys = [k.strip() for k in raw_keys.split(",") if k.strip()]

        # बैकअप व्यक्तिगत Keys
        if not self.keys:
            for i in range(1, 11):
                k = os.getenv(f"GROQ_API_KEY_{i}")
                if k:
                    self.keys.append(k.strip())

        if not self.keys:
            print("⚠️ चेतावनी: कोई भी Groq API Key नहीं मिली! कृपया .env फ़ाइल चेक करें।")
        else:
            print(f"🤖 Groq Python इंजन तैयार: {len(self.keys)} सक्रिय Keys लोड की गईं (Model: {self.model})")

    def _get_active_key(self) -> str:
        return self.keys[self.current_key_index]

    def _rotate_key(self):
        prev = self.current_key_index
        self.current_key_index = (self.current_key_index + 1) % len(self.keys)
        print(f"🔄 Groq Key स्विच: Key #{prev + 1} ➡️ Key #{self.current_key_index + 1}")

    def chat_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.6) -> dict:
        """
        Groq API को कॉल करके सीधा वैध JSON डिक्शनरी लौटाता है
        """
        if not self.keys:
            raise ValueError("कोई Groq API Key उपलब्ध नहीं है।")

        attempts = 0
        max_attempts = len(self.keys)

        while attempts < max_attempts:
            key = self._get_active_key()
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt + "\nCRITICAL: Keep internal reasoning brief (under 50 words) and immediately output the valid JSON."},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "max_completion_tokens": 6000
            }

            try:
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )

                # 429 = Rate Limit, 401 = Invalid Key
                if resp.status_code in (429, 401):
                    print(f"⚠️ Groq Key #{self.current_key_index + 1} पर स्टेटस {resp.status_code} मिला।")
                    self._rotate_key()
                    attempts += 1
                    continue

                if not resp.ok:
                    raise RuntimeError(f"Groq HTTP Error {resp.status_code}: {resp.text}")

                data = resp.json()
                raw_text = data["choices"][0]["message"]["content"].strip()

                # Robust JSON extractor (चाहे बैकग्राउंड टेक्स्ट हो या मार्कडाउन बैकटिक)
                parsed = None
                json_match = re.search(r"(\{.*\}|\[.*\])", raw_text, re.DOTALL)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        pass

                if parsed is None:
                    # फॉलबैक क्लीनिंग
                    cleaned = re.sub(r"```(?:json)?", "", raw_text).strip()
                    parsed = json.loads(cleaned)

                # हेडलाइन से किसी भी ** को हटाएँ
                if isinstance(parsed, dict) and "stories" in parsed and isinstance(parsed["stories"], list):
                    for s in parsed["stories"]:
                        if isinstance(s, dict) and "screen_headline" in s and isinstance(s["screen_headline"], str):
                            s["screen_headline"] = s["screen_headline"].replace("**", "").replace("*", "").strip()

                return parsed

            except requests.RequestException as e:
                print(f"❌ नेटवर्क त्रुटि (Key #{self.current_key_index + 1}): {e}")
                self._rotate_key()
                attempts += 1
            except json.JSONDecodeError as e:
                print(f"❌ JSON पार्सिंग त्रुटि: {e}")
                attempts += 1

        raise RuntimeError("सभी Groq API Keys समाप्त हो गईं या कनेक्शन में समस्या है।")
