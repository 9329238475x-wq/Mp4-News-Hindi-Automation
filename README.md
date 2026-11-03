# 📺 MP4 NEWS हिन्दी — Automated TV News Video Production Engine

> **100% Automated Cloud Broadcast Pipeline:** Groq AI 4-Stage Scripting & Real Photo Sourcing + OmniVoice (k2-fsa) Native Neural Hindi Voiceover on Kaggle GPU + Remotion 1080p Broadcast Master Renderer.

---

## 🚀 मुख्य विशेषताएं (Key Features)

1. **🎙️ OmniVoice GPU TTS (Zero-Shot Native Hindi):**
   - माइक्रोसॉफ्ट Edge-TTS को हटाकर अत्याधुनिक न्यूरल मॉडल **OmniVoice (k2-fsa)** का उपयोग।
   - बिना वॉइस क्लोनिंग के मॉडल की ओरिजिनल, क्रिस्टल-क्लियर हिंदी आवाज़ (`language="hi"`, `float16` GPU VRAM)।
   - ऑफ़लाइन मॉडल लोड (`sonuji12345/tts-offline-models`) और फास्ट NVMe `/tmp/OmniVoice_fast` स्टेजिंग।

2. **📰 4-Stage Groq AI News Pipeline:**
   - **Stage 1 (Voiceover):** 100% शुद्ध हिंदी देवनागरी वॉइसओवर (संख्याओं का शब्दों में रूपांतरण, जैसे "२५ हजार")।
   - **Stage 2 (Headlines):** 3 से 4 डायनामिक ब्रेकिंग हेडलाइंस जो स्क्रीन पर चरणबद्ध तरीके से बदलती हैं।
   - **Stage 3 (Real Photos):** घटना और प्रेस कवरेज से 10-15 प्रामाणिक वास्तविक न्यूज़ तस्वीरें।
   - **Stage 4 (Reaction Memes):** संदर्भ के अनुसार एक्सप्रेशन व रिएक्शन मीम कीवर्ड्स।

3. **🎨 Broadcast-Quality Remotion Graphics (MP4 NEWS हिन्दी):**
   - **100% Pure HTML/CSS Vector Typography:** नो-पिक्सेलेशन, अल्ट्रा-शार्प `MP4 NEWS` (गहरा लाल बैकग्राउंड) + `हिन्दी` (सफ़ेद बैकग्राउंड)।
   - **3D Breaking News Ulat-Palat Flip & Shimmer:** टीवी चैनलों जैसा स्मूथ 3D फ्लिप और मेटैलिक लाइट पास।
   - **डायनामिक न्यूज़ टिकर, ऑडियो इक्वलाइज़र, और फुल-स्क्रीन मीम रिएक्शन पॉप-इन।**

4. **⚡ GitHub Actions 1-Click Automation:**
   - GitHub के **Actions** टैब में जाकर **"Run workflow"** बटन दबाते ही यह पाइपलाइन सीधे Kaggle GPU पर शुरू हो जाती है और रेंडर होने के बाद वीडियो GitHub Artifacts में डाउनलोड के लिए तैयार मिलता है।

---

## 🕹️ 1-Click GitHub Actions से वीडियो कैसे बनाएं (How to Run)

1. इस रिपॉजिटरी के **[Actions](https://github.com/9329238475x-wq/Mp4-News-Hindi-Automation/actions)** टैब पर जाएं।
2. बाईं तरफ **"🎬 Generate MP4 News Hindi Video (Kaggle GPU)"** पर क्लिक करें।
3. दाईं तरफ **"Run workflow"** बटन पर क्लिक करें:
   - **Story Number:** `1` (या `all`)
   - **Force Refresh News:** लाइव वेब से ताज़ा ब्रेकिंग न्यूज़ लाने के लिए टिक करें।
4. **"Run workflow"** पर क्लिक करें। पाइपलाइन Kaggle GPU पर चलेगी और पूरा होने पर MP4 वीडियो `Artifacts` में उपलब्ध होगा।

---

## 💻 लोकल या क्लाउड स्क्रिप्ट से रन करना (Run via CLI)

```bash
# Kaggle GPU पर नोटबुक डिप्लॉय और मॉनिटर करना
python push_to_kaggle.py
```

रेंडर हुआ वीडियो सीधे `out/Mp4_News_Hindi_Story_01.mp4` में सेव हो जाएगा।

---

## 📂 डायरेक्टरी संरचना (Directory Structure)

```text
├── .github/workflows/
│   └── generate_news_video.yml   # 1-Click GitHub Action Workflow
├── assets/                       # बैकग्राउंड वीडियो, ऑडियो व साउंडट्रैक
├── niches/01-daily-top10/        # न्यूज़ स्क्रैपिंग, AI स्क्रिप्टिंग और OmniVoice ऑडियो
│   ├── fetch_full_news.py        # लाइव न्यूज़ फेचर
│   ├── generate_bulletin.py      # Groq 4-Stage AI जनरेटर
│   ├── generate_audio.py         # OmniVoice GPU TTS इंजन
│   └── download_assets.py        # ऑटोपायलट रियल फोटो व मीम डाउनलोडर
├── src/                          # Remotion React ब्रॉडकास्ट ग्राफिक्स
│   ├── DLSNewsStory.tsx          # मास्टर स्टोरी कम्पोज़ीशन
│   ├── components/
│   │   ├── NewsTopHeader.tsx     # MP4 NEWS हिन्दी 3D वेक्टर लोगो व फ्लिप
│   │   ├── DLSTicker.tsx         # बॉटम ब्रेकिंग टिकर
│   │   ├── FullScreenMemeOverlay.tsx # फुल-स्क्रीन वायरल मीम पॉप-इन
│   │   └── AudioEqualizer.tsx    # लाइव ऑडियो वेवफ़ॉर्म
├── Mp4_News_Hindi_Pipeline.ipynb # Kaggle GPU पर रन होने वाली प्रोडक्शन नोटबुक
└── push_to_kaggle.py             # ऑटोमेटेड क्लाउड ट्रिगर व वीडियो फेचर
```
