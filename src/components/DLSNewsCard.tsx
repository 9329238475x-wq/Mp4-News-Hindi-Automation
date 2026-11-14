/**
 * DLS News – Master Sleek Broadcast Headline Card
 * 
 * 100% Television Broadcast Quality:
 * 1. Glossy Crimson Red Theme ("ताज़ा अपडेट्स" Style):
 *    - Main Body: linear-gradient(180deg, #C80000 0%, #8B0000 55%, #520000 100%)
 *    - Border: 2px solid #FF5555 with vibrant broadcast glow
 *    - Header Bar: Deep Maroon-Black (linear-gradient(90deg, #2A0000 0%, #1A0000 100%))
 * 2. Slim & Tall Vertical Dimensions:
 *    - Width: 550px (Leaves 63% screen for expansive media showcase on Left)
 *    - Height: 540px (Vertical tall broadcast chyron card)
 * 3. Perfect Center Alignment:
 *    - display: flex, flexDirection: column, justifyContent: center, alignItems: center, textAlign: center
 *    - 40px bold white typography with soft black shadow (0 3px 10px rgba(0,0,0,0.65))
 * 4. 100% Clean Location Badge:
 *    - Zero emojis or broken characters, clean Devanagari city name (e.g. "नई दिल्ली")
 */
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

interface DLSNewsCardProps {
  headline: string;
  headlines?: string[];
  category?: string;
  location?: string;
  bulletPoints?: string[];
  expandProgress?: number;
  totalStoryDurationFrames?: number;
}

export const DLSNewsCard: React.FC<DLSNewsCardProps> = ({
  headline,
  headlines = [],
  category = "विशेष बुलेटिन",
  location,
  bulletPoints = [],
  expandProgress = 0,
  totalStoryDurationFrames = 750,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // ─── 1. RESOLVE ACTIVE SEQUENTIAL HEADLINES (3 TO 4 SEPARATE HEADLINES) ───
  let activeHeadlines: string[] = [];
  if (Array.isArray(headlines) && headlines.length > 0) {
    activeHeadlines = headlines
      .map((h) => (h || "").replace(/\*\*/g, "").replace(/\*/g, "").trim())
      .filter((h) => h.length > 0);
  }

  if (activeHeadlines.length === 0) {
    if (headline && headline.trim()) {
      activeHeadlines = [headline.replace(/\*\*/g, "").replace(/\*/g, "").trim()];
    } else if (bulletPoints && bulletPoints.length > 0) {
      activeHeadlines = bulletPoints
        .map((bp) => (bp || "").replace(/\*\*/g, "").replace(/\*/g, "").trim())
        .filter(Boolean);
    } else {
      activeHeadlines = [
        "भारत व्यापार मेले का भव्य शुभारंभ आज से शुरू",
        "दिल्ली पुलिस ने प्रमुख मार्गों पर ट्रैफिक एडवाइजरी जारी की",
        "मथुरा रोड और भैरों मार्ग पर रहेगा भारी यातायात",
        "सुबह 9 से शाम 7 बजे तक विशेष पार्किंग व्यवस्था",
      ];
    }
  }

  const numHeadlines = activeHeadlines.length;
  const totalFrames = Math.max(200, totalStoryDurationFrames);
  // Ensure the final headline appears at least 90 frames (~3.0s) before story ends
  const effectiveFrames = Math.max(120, totalFrames - 90);
  const phaseDuration = Math.max(1, Math.floor(effectiveFrames / numHeadlines));

  // Determine current active headline index
  const currentIdx = Math.min(
    numHeadlines - 1,
    Math.floor(frame / phaseDuration)
  );
  const phaseFrame = frame - currentIdx * phaseDuration;
  const currentHeadline = activeHeadlines[currentIdx] || "";

  // ─── 2. INSTANT BROADCAST REVEAL ANIMATION (Smooth Slide-Up & Fade-In) ───
  const phaseSpring = spring({
    frame: phaseFrame,
    fps,
    config: { damping: 14, mass: 0.7, stiffness: 130 },
  });
  const phaseTranslateY = interpolate(phaseSpring, [0, 1], [16, 0]);
  const phaseOpacity = interpolate(phaseSpring, [0, 1], [0, 1]);

  // ─── 3. RIGHT DOCKED BROADCAST GEOMETRY (Width 550px, Height 540px) ───
  // Right Card: left 1310px, top 180px, width 550px, height 540px
  const entranceSpring = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 90 },
  });
  const entranceTranslateX = interpolate(entranceSpring, [0, 1], [60, 0]);
  const entranceOpacity = interpolate(entranceSpring, [0, 1], [0, 1]);

  // Dynamic Font Size tailored to headline length
  const textLength = currentHeadline.length;
  const cardFontSize = textLength > 60 ? 34 : textLength > 45 ? 37 : 40;

  // Clean location / category badge (e.g. नई दिल्ली, zero broken unicode or emoji)
  let rawBadge = location || (category && category !== "जनहित" ? category : "") || "नई दिल्ली";
  rawBadge = rawBadge.replace(/[^a-zA-Z0-9\u0900-\u097F\s]/g, "").trim();
  const displayBadge = rawBadge || "नई दिल्ली";

  // ─── 4. TARAJU (SEESAW) FOCUS ORCHESTRATION ───
  const tarajuOpacity = interpolate(expandProgress, [0, 0.35, 1], [1, 0, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const tarajuScale = interpolate(expandProgress, [0, 1], [1, 0.94], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        top: 180,
        left: 1310,
        width: 550,
        transform: `translateX(${entranceTranslateX}px) scale(${tarajuScale})`,
        opacity: entranceOpacity * tarajuOpacity,
        zIndex: 40,
        display: "flex",
        flexDirection: "column",
        alignItems: "stretch",
        fontFamily: "'Noto Sans Devanagari', 'Segoe UI', sans-serif",
        pointerEvents: tarajuOpacity < 0.1 ? "none" : "auto",
      }}
    >
      {/* ─── 1. TOP LOCATION / CATEGORY BAR (Deep Maroon #2A0000) ─── */}
      <div
        style={{
          background: "linear-gradient(90deg, #2A0000 0%, #1A0000 100%)",
          borderTopLeftRadius: 14,
          borderTopRightRadius: 14,
          padding: "11px 22px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          border: "2px solid #FF5555",
          borderBottom: "none",
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.5)",
        }}
      >
        <div
          style={{
            color: "#ffffff",
            fontSize: 20,
            fontWeight: 900,
            letterSpacing: "0.8px",
            display: "flex",
            alignItems: "center",
            gap: 8,
            textTransform: "uppercase",
            textShadow: "0 1px 3px rgba(0, 0, 0, 0.8)",
          }}
        >
          <span style={{ color: "#FF5555", fontSize: 18, lineHeight: 1 }}>●</span>
          <span>{displayBadge}</span>
        </div>
        <div
          style={{
            background: "#D90429",
            color: "#ffffff",
            fontSize: 13,
            fontWeight: 900,
            letterSpacing: "1.2px",
            padding: "3px 10px",
            borderRadius: 6,
            textTransform: "uppercase",
            boxShadow: "0 2px 6px rgba(0, 0, 0, 0.4)",
          }}
        >
          BREAKING
        </div>
      </div>

      {/* ─── 2. MAIN BROADCAST CARD BODY (Glossy Crimson Red Gradient) ─── */}
      <div
        style={{
          width: "100%",
          height: 485,
          background: "linear-gradient(180deg, #C80000 0%, #8B0000 55%, #520000 100%)",
          border: "2px solid #FF5555",
          borderTop: "none",
          borderBottomLeftRadius: 16,
          borderBottomRightRadius: 16,
          boxShadow:
            "0 18px 48px rgba(0, 0, 0, 0.88), 0 0 24px rgba(200, 0, 0, 0.4), inset 0 2px 0 rgba(255, 255, 255, 0.25)",
          padding: "24px 28px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          textAlign: "center",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Subtle Diagonal Gloss Reflection */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: "45%",
            background:
              "linear-gradient(180deg, rgba(255, 255, 255, 0.18) 0%, transparent 100%)",
            pointerEvents: "none",
          }}
        />

        {/* ─── 3. THE ACTIVE HEADLINE (Centered Horizontally & Vertically, 40px Bold) ─── */}
        <div
          key={`headline-${currentIdx}`}
          style={{
            transform: `translateY(${phaseTranslateY}px)`,
            opacity: phaseOpacity,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: "100%",
          }}
        >
          <div
            style={{
              color: "#ffffff",
              fontSize: cardFontSize,
              fontWeight: 900,
              lineHeight: 1.35,
              letterSpacing: "0.2px",
              textAlign: "center",
              wordBreak: "break-word",
              textShadow:
                "0 3px 10px rgba(0, 0, 0, 0.65), 0 2px 4px rgba(0, 0, 0, 0.9)",
            }}
          >
            {currentHeadline}
          </div>
        </div>
      </div>
    </div>
  );
};
