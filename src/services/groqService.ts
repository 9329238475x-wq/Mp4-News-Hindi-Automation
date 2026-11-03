import dotenv from "dotenv";
dotenv.config();

/**
 * Groq AI Client with Automatic Key Rotation & Failover
 * मॉडल: openai/gpt-oss-120b
 */
export class GroqService {
  private keys: string[] = [];
  private currentKeyIndex: number = 0;
  private model: string;

  constructor() {
    this.model = process.env.GROQ_MODEL || "openai/gpt-oss-120b";
    
    // Get keys from comma-separated list or individual variables
    if (process.env.GROQ_API_KEYS) {
      this.keys = process.env.GROQ_API_KEYS.split(",")
        .map((k) => k.trim())
        .filter(Boolean);
    }

    if (this.keys.length === 0) {
      // Fallback to individual keys
      for (let i = 1; i <= 10; i++) {
        const k = process.env[`GROQ_API_KEY_${i}`];
        if (k) this.keys.push(k.trim());
      }
    }

    if (this.keys.length === 0) {
      console.warn("⚠️ चेतावनी: कोई भी Groq API Key नहीं मिली!");
    } else {
      console.log(`🤖 Groq Service चालू: ${this.keys.length} सक्रिय Keys लोड की गईं (Model: ${this.model})`);
    }
  }

  /**
   * वर्तमान सक्रिय API Key प्राप्त करें
   */
  private getCurrentKey(): string {
    return this.keys[this.currentKeyIndex];
  }

  /**
   * अगली Key पर स्विच करें (अगर लिमिट खत्म हो या एरर आए)
   */
  private rotateKey(): void {
    const prevIndex = this.currentKeyIndex;
    this.currentKeyIndex = (this.currentKeyIndex + 1) % this.keys.length;
    console.warn(`🔄 Groq Key स्विच की गई: Key #${prevIndex + 1} ➡️ Key #${this.currentKeyIndex + 1}`);
  }

  /**
   * चैट पूर्णता (Chat Completion) कॉल - ऑटो-रोटेशन के साथ
   */
  public async chat(
    messages: Array<{ role: "system" | "user" | "assistant"; content: string }>,
    temperature: number = 0.7
  ): Promise<string> {
    if (this.keys.length === 0) {
      throw new Error("कोई Groq API Key उपलब्ध नहीं है। कृपया .env फ़ाइल चेक करें।");
    }

    let attempts = 0;
    const maxAttempts = this.keys.length;

    while (attempts < maxAttempts) {
      const activeKey = this.getCurrentKey();
      try {
        const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${activeKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            model: this.model,
            messages,
            temperature,
          }),
        });

        // 429 = Rate limit exceeded, 401 = Invalid key
        if (response.status === 429 || response.status === 401) {
          console.warn(`⚠️ Groq Key #${this.currentKeyIndex + 1} पर रिस्पॉन्स ${response.status} मिला। अगली Key पर जा रहे हैं...`);
          this.rotateKey();
          attempts++;
          continue;
        }

        if (!response.ok) {
          const errText = await response.text();
          throw new Error(`Groq API Error (${response.status}): ${errText}`);
        }

        const data = await response.json();
        return data.choices?.[0]?.message?.content || "";
      } catch (err: any) {
        console.error(`❌ एरर (Key #${this.currentKeyIndex + 1}):`, err.message);
        this.rotateKey();
        attempts++;
      }
    }

    throw new Error("सभी 5 Groq API Keys की लिमिट समाप्त हो चुकी है या कनेक्शन में समस्या है।");
  }

  /**
   * ताज़ा खबर से हिंदी न्यूज़ बुलेटिन और बुलेट पॉइंट्स तैयार करना
   */
  public async formatNewsStory(rawTitle: string, rawDescription: string) {
    const prompt = `
आप एक प्रमुख भारतीय टीवी न्यूज़ चैनल के सीनियर न्यूज़ एडिटर हैं।
नीचे दी गई खबर को टीवी न्यूज़ वीडियो के लिए आकर्षक, सटीक और शुद्ध हिंदी में बदलें।

मूल खबर:
शीर्षक: ${rawTitle}
विवरण: ${rawDescription}

कृपया केवल वैध JSON आउटपुट दें जिसमें निम्नलिखित फ़ील्ड्स हों:
{
  "headline": "अधिकतम 10-12 शब्दों की दमदार ब्रेकिंग हेडलाइन",
  "bulletPoints": [
    "मुख्य बात 1 (सरल और प्रभावी)",
    "मुख्य बात 2 (महत्वपूर्ण तथ्य)",
    "मुख्य बात 3 (आगे क्या होगा)"
  ],
  "visualKeyword": "Pexels पर वीडियो खोजने के लिए 2-3 अंग्रेजी शब्द (जैसे: indian parliament, solar energy, cricket stadium)",
  "category": "राजनीति / व्यापार / खेल / डिफ़ेंस / तकनीक"
}
`;

    const response = await this.chat([
      { role: "system", content: "आप केवल वैध JSON लौटाने वाले न्यूज़ ऑटोमेशन एडिटर हैं।" },
      { role: "user", content: prompt },
    ]);

    try {
      // Clean potential markdown backticks
      const cleanJson = response.replace(/```json/g, "").replace(/```/g, "").trim();
      return JSON.parse(cleanJson);
    } catch {
      return {
        headline: rawTitle,
        bulletPoints: [rawDescription],
        visualKeyword: "breaking news",
        category: "ताज़ा खबर",
      };
    }
  }
}

export const groq = new GroqService();
