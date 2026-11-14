/**
 * DLS News – Master Sleek Broadcast Headline Card
 * 
 * 100% Television Broadcast Quality:
 * 1. Single Authoritative Brand Color:
 *    - Deep Navy Blue Card (#0A192F) with crisp broadcast frame.
 *    - Crimson Red Category/Location Bar (#D90429) on top.
 * 2. Professional TV Typography & Alignment:
 *    - Left-aligned text (textAlign: "left") with comfortable padding.
 *    - Sleek height (380px) eliminating excessive empty space.
 * 3. Instant Broadcast Reveal (Zero AI Typewriter Glitch):
 *    - Entire headline renders immediately with a smooth slide & fade-in.
 * 4. Pacing & Timing:
 *    - Last headline transitions at least 3 seconds before voiceover ends.
 * 5. Screen Balance:
 *    - Starts from Frame 0 docked on Right (40% width), perfectly paired with Left Media (60% width).
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
  category = "विशेष रिपोर्ट",
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

  // ─── 3. RIGHT DOCKED BROADCAST GEOMETRY (Frame 0 Start, Sleek Height) ───
  // Right Card: left 1150px, top 200px, width 710px, height 380px (40% screen)
  const entranceSpring = spring({
    frame,
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 90 },
  });
  const entranceTranslateX = interpolate(entranceSpring, [0, 1], [60, 0]);
  const entranceOpacity = interpolate(entranceSpring, [0, 1], [0, 1]);

  // Dynamic Font Size tailored to headline length
  const textLength = currentHeadline.length;
  const cardFontSize = textLength > 55 ? 32 : textLength > 40 ? 36 : textLength > 28 ? 40 : 44;

  // Location / Category Label (e.g. नई दिल्ली or ट्रैफिक अलर्ट)
  const rawBadge = location || category || "विशेष बुलेटिन";
  const displayBadge = rawBadge.replace(/📍/g, "").trim();

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
        top: 200,
        left: 1150,
        width: 710,
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
      {/* ─── 1. TOP CATEGORY / LOCATION RED BAR (Official Crimson TV Red #D90429) ─── */}
      <div
        style={{
          background: "linear-gradient(90deg, #D90429 0%, #b8001f 100%)",
          borderTopLeftRadius: 14,
          borderTopRightRadius: 14,
          padding: "10px 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          border: "2px solid rgba(255, 255, 255, 0.25)",
          borderBottom: "none",
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.4)",
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
            textShadow: "0 1px 3px rgba(0, 0, 0, 0.6)",
          }}
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#ffffff"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ flexShrink: 0 }}
          >
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" fill="#ffffff" />
            <circle cx="12" cy="10" r="3" fill="#D90429" />
          </svg>
          <span>{displayBadge}</span>
        </div>
        <div
          style={{
            color: "rgba(255, 255, 255, 0.85)",
            fontSize: 15,
            fontWeight: 800,
            letterSpacing: "1px",
          }}
        >
          BREAKING
        </div>
      </div>

      {/* ─── 2. MAIN BROADCAST CARD BODY (Fixed Deep Navy Blue #0A192F) ─── */}
      <div
        style={{
          width: "100%",
          minHeight: 320,
          maxHeight: 380,
          background: "linear-gradient(180deg, #0f2744 0%, #0a192f 55%, #061120 100%)",
          border: "2.5px solid #1e3a5f",
          borderTop: "none",
          borderBottomLeftRadius: 16,
          borderBottomRightRadius: 16,
          boxShadow: "0 18px 45px rgba(0, 0, 0, 0.85), inset 0 1px 0 rgba(255, 255, 255, 0.15)",
          padding: "24px 28px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
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
            height: "40%",
            background: "linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, transparent 100%)",
            pointerEvents: "none",
          }}
        />

        {/* ─── 3. THE ACTIVE HEADLINE (Left-Aligned, Full Reveal, Sharp & Punchy) ─── */}
        <div
          key={`headline-${currentIdx}`}
          style={{
            transform: `translateY(${phaseTranslateY}px)`,
            opacity: phaseOpacity,
            display: "flex",
            alignItems: "center",
            width: "100%",
          }}
        >
          <div
            style={{
              color: "#ffffff",
              fontSize: cardFontSize,
              fontWeight: 900,
              lineHeight: 1.38,
              letterSpacing: "0.2px",
              textAlign: "left",
              wordBreak: "break-word",
              textShadow: "0 2px 8px rgba(0, 0, 0, 0.95), 0 4px 20px rgba(0, 0, 0, 0.7)",
            }}
          >
            {currentHeadline}
          </div>
        </div>
      </div>
    </div>
  );
};
