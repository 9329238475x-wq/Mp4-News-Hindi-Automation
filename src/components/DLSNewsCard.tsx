/**
 * DLS News – Master Animated Sequential Broadcast Chyron Card
 * 
 * Features:
 * 1. Sequential Multi-Headline Rotation:
 *    - Instead of cramming all 4 headlines together, displays ONE headline at a time!
 *    - Sequentially transitions across 3 to 4 distinct headlines throughout the story.
 * 2. Dynamic 4-Theme Broadcast Palette:
 *    - Headline 1: Crimson Ruby Red with Red/White [BREAKING | NEWS]
 *    - Headline 2: Royal Cobalt Blue with Blue/Yellow [ताज़ा | अपडेट]
 *    - Headline 3: Regal Royal Purple with Purple/Gold [बड़ा | खुलासा]
 *    - Headline 4: Emerald Forest Green with Green/White [मुख्य | बिंदु]
 * 3. 3D Flip & Pop Phase Animation:
 *    - Smooth 3D perspective tumble, spring pop, and live glow transition on each headline change.
 *    - Real-time Hindi typewriter text reveal with blinking cursor.
 * 4. Center-to-Right Broadcast Choreography:
 *    - Center Entrance (Frames 0-165): 960px width, 485px height (Dominant headline)
 *    - Right Docking (Frames 165+): 730px width, 551px height (Balanced with Left Media Showcase)
 * 5. Taraju (Seesaw) Orchestration:
 *    - Dims and scales back when media showcase expands, returns crisp on focus.
 */
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { DLSBreakingBadge } from "./DLSBreakingBadge";

export interface BroadcastCardTheme {
  name: string;
  gradient: string;
  borderColor: string;
  innerBorderColor: string;
  boxShadow: string;
  glowColor: string;
  badgeLeftBg: string;
  badgeLeftText: string;
  badgeLeftLabel: string;
  badgeRightBg: string;
  badgeRightText: string;
  badgeRightLabel: string;
  accentPillBg: string;
  accentPillText: string;
  highlightBg: string;
  highlightText: string;
}

export const BROADCAST_THEMES: BroadcastCardTheme[] = [
  // 1. Ruby / Crimson Red (Classic Breaking News)
  {
    name: "Crimson Red",
    gradient: "linear-gradient(180deg, #ba0009 0%, #8b0004 50%, #590002 100%)",
    borderColor: "#ffffff",
    innerBorderColor: "rgba(255, 255, 255, 0.85)",
    boxShadow:
      "0 18px 48px rgba(0, 0, 0, 0.88), 0 0 36px rgba(186, 0, 9, 0.7), inset 0 2px 0 rgba(255, 255, 255, 0.45)",
    glowColor: "rgba(186, 0, 9, 0.75)",
    badgeLeftBg: "linear-gradient(180deg, #ff1a1a 0%, #cc0000 60%, #990000 100%)",
    badgeLeftText: "#ffffff",
    badgeLeftLabel: "BREAKING",
    badgeRightBg: "linear-gradient(180deg, #ffffff 0%, #f0f0f0 100%)",
    badgeRightText: "#cc0000",
    badgeRightLabel: "NEWS",
    accentPillBg: "rgba(255, 204, 0, 0.22)",
    accentPillText: "#ffd700",
    highlightBg: "#ffcc00",
    highlightText: "#000000",
  },
  // 2. Royal Electric Navy / Cobalt Blue
  {
    name: "Cobalt Blue",
    gradient: "linear-gradient(180deg, #0d47a1 0%, #002171 50%, #00103a 100%)",
    borderColor: "#00f0ff",
    innerBorderColor: "rgba(0, 240, 255, 0.8)",
    boxShadow:
      "0 18px 48px rgba(0, 0, 0, 0.88), 0 0 36px rgba(13, 71, 161, 0.8), inset 0 2px 0 rgba(0, 240, 255, 0.55)",
    glowColor: "rgba(0, 240, 255, 0.7)",
    badgeLeftBg: "linear-gradient(180deg, #002b55 0%, #001224 100%)",
    badgeLeftText: "#00f0ff",
    badgeLeftLabel: "ताज़ा",
    badgeRightBg: "linear-gradient(180deg, #ffcc00 0%, #e6b800 100%)",
    badgeRightText: "#00103a",
    badgeRightLabel: "अपडेट",
    accentPillBg: "rgba(0, 240, 255, 0.22)",
    accentPillText: "#00f0ff",
    highlightBg: "#00f0ff",
    highlightText: "#00103a",
  },
  // 3. Regal Purple / Dark Violet
  {
    name: "Regal Purple",
    gradient: "linear-gradient(180deg, #6a1b9a 0%, #4a148c 50%, #2a0845 100%)",
    borderColor: "#ffd700",
    innerBorderColor: "rgba(255, 215, 0, 0.85)",
    boxShadow:
      "0 18px 48px rgba(0, 0, 0, 0.88), 0 0 36px rgba(106, 27, 154, 0.8), inset 0 2px 0 rgba(255, 215, 0, 0.5)",
    glowColor: "rgba(255, 215, 0, 0.7)",
    badgeLeftBg: "linear-gradient(180deg, #4a148c 0%, #2a0845 100%)",
    badgeLeftText: "#ffffff",
    badgeLeftLabel: "बड़ा",
    badgeRightBg: "linear-gradient(180deg, #ffd700 0%, #ffaa00 100%)",
    badgeRightText: "#2a0845",
    badgeRightLabel: "खुलासा",
    accentPillBg: "rgba(255, 215, 0, 0.22)",
    accentPillText: "#ffd700",
    highlightBg: "#ffd700",
    highlightText: "#2a0845",
  },
  // 4. Emerald Forest / Dark Jade
  {
    name: "Emerald Green",
    gradient: "linear-gradient(180deg, #00695c 0%, #004d40 50%, #00251a 100%)",
    borderColor: "#69f0ae",
    innerBorderColor: "rgba(105, 240, 174, 0.85)",
    boxShadow:
      "0 18px 48px rgba(0, 0, 0, 0.88), 0 0 36px rgba(0, 105, 92, 0.8), inset 0 2px 0 rgba(105, 240, 174, 0.5)",
    glowColor: "rgba(105, 240, 174, 0.7)",
    badgeLeftBg: "linear-gradient(180deg, #004d40 0%, #00251a 100%)",
    badgeLeftText: "#69f0ae",
    badgeLeftLabel: "मुख्य",
    badgeRightBg: "linear-gradient(180deg, #ffffff 0%, #e0e0e0 100%)",
    badgeRightText: "#004d40",
    badgeRightLabel: "बिंदु",
    accentPillBg: "rgba(105, 240, 174, 0.22)",
    accentPillText: "#69f0ae",
    highlightBg: "#69f0ae",
    highlightText: "#00251a",
  },
];

interface DLSNewsCardProps {
  headline: string;
  headlines?: string[];
  category?: string;
  bulletPoints?: string[];
  expandProgress?: number;
  totalStoryDurationFrames?: number;
}

// Unicode grapheme segmenter for authentic Hindi text splitting without breaking matras
const getHindiGraphemes = (text: string): string[] => {
  if (typeof Intl !== "undefined" && Intl.Segmenter) {
    const segmenter = new Intl.Segmenter("hi", { granularity: "grapheme" });
    return Array.from(segmenter.segment(text), (s) => s.segment);
  }
  return Array.from(text);
};

export const DLSNewsCard: React.FC<DLSNewsCardProps> = ({
  headline,
  headlines = [],
  category: _category,
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
        "भारत व्यापार मेले का भव्य उद्घाटन आज से शुरू",
        "दिल्ली पुलिस ने प्रमुख मार्गों पर ट्रैफिक एडवाइजरी जारी की",
        "मथुरा रोड और भैरों मार्ग पर रहेगा भारी जाम",
        "व्यावसायिक आगंतुकों के लिए विशेष गेट और पार्किंग व्यवस्था",
      ];
    }
  }

  const numHeadlines = activeHeadlines.length;
  const totalFrames = Math.max(200, totalStoryDurationFrames);
  const phaseDuration = Math.max(1, Math.floor(totalFrames / numHeadlines));

  // Determine current active headline index (0, 1, 2, or 3)
  const currentIdx = Math.min(
    numHeadlines - 1,
    Math.floor(frame / phaseDuration)
  );
  const phaseFrame = frame - currentIdx * phaseDuration;
  const currentHeadline = activeHeadlines[currentIdx] || "";
  const currentTheme = BROADCAST_THEMES[currentIdx % BROADCAST_THEMES.length];

  // ─── 2. HEADLINE TRANSITION ANIMATION (Smooth 3D Flip & Spring Pop on Phase Change) ───
  const phaseSpring = spring({
    frame: phaseFrame,
    fps,
    config: { damping: 13, mass: 0.7, stiffness: 120 },
  });

  const phaseRotateX = interpolate(phaseSpring, [0, 1], [-22, 0]);
  const phaseScale = interpolate(phaseSpring, [0, 1], [0.91, 1.0]);
  const phaseOpacity = interpolate(phaseSpring, [0, 1], [0.25, 1.0]);

  // Typewriter animation within current phase (types out over 24 frames ~ 0.8s)
  const typingDuration = 24;
  const graphemes = getHindiGraphemes(currentHeadline);
  const totalGraphemes = graphemes.length;
  const visibleCount = Math.min(
    totalGraphemes,
    Math.floor(
      interpolate(phaseFrame, [2, 2 + typingDuration], [0, totalGraphemes], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    )
  );
  const isTyping = phaseFrame >= 2 && phaseFrame < 2 + typingDuration;
  const cursorBlink = Math.floor(phaseFrame / 6) % 2 === 0;
  const displayedText = graphemes.slice(0, visibleCount).join("");

  // ─── 3. CENTER-TO-RIGHT CHOREOGRAPHY ANIMATION ───
  // A. Initial Center Entrance (Frames 0 to 30)
  const entranceSpring = spring({
    frame,
    fps,
    config: { damping: 13, mass: 0.7 },
  });
  const entranceOpacity = interpolate(entranceSpring, [0, 1], [0, 1]);
  const entranceScale = interpolate(entranceSpring, [0, 1], [0.92, 1.0]);

  // B. Stay in Center for ~5.5s, then at Frame 165 smoothly slide & dock on Right Side
  const slideProgress = spring({
    frame: Math.max(0, frame - 165),
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 90 },
  });

  // Geometry:
  // Center: left 480, top 235, width 960, height 485
  // Side:   left 1110, top 240, width 730, height 551 (Matches Left Media Showcase!)
  const currentLeft = interpolate(slideProgress, [0, 1], [480, 1110]);
  const currentTop = interpolate(slideProgress, [0, 1], [235, 240]);
  const currentWidth = interpolate(slideProgress, [0, 1], [960, 730]);
  const currentHeight = interpolate(slideProgress, [0, 1], [485, 551]);

  // Dynamic Font Size: Center is larger, Side is slightly more compact
  const heroFontSize = Math.round(
    interpolate(
      slideProgress,
      [0, 1],
      [
        currentHeadline.length > 35 ? 46 : 52,
        currentHeadline.length > 35 ? 38 : 44,
      ]
    )
  );

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
        top: currentTop,
        left: `${currentLeft}px`,
        width: `${currentWidth}px`,
        transform: `scale(${entranceScale * tarajuScale})`,
        opacity: entranceOpacity * tarajuOpacity,
        zIndex: 40,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        fontFamily: "'Noto Sans Devanagari', 'Segoe UI', sans-serif",
        pointerEvents: tarajuOpacity < 0.1 ? "none" : "auto",
        perspective: 1200,
      }}
    >
      {/* ─── 1. TOP DYNAMIC 3D BADGE (Flips & Updates Colors with Each Headline) ─── */}
      <div
        style={{
          width: "100%",
          display: "flex",
          justifyContent: "center",
          marginBottom: -16,
          position: "relative",
          zIndex: 20,
        }}
      >
        <DLSBreakingBadge
          key={`badge-${currentIdx}`}
          leftText={currentTheme.badgeLeftLabel}
          rightText={currentTheme.badgeRightLabel}
          leftBg={currentTheme.badgeLeftBg}
          leftColor={currentTheme.badgeLeftText}
          rightBg={currentTheme.badgeRightBg}
          rightColor={currentTheme.badgeRightText}
        />
      </div>

      {/* ─── 2. MAIN BROADCAST CARD CONTAINER (Dynamic Theme Gradient + Double Frame) ─── */}
      <div
        style={{
          width: "100%",
          height: currentHeight,
          background: currentTheme.gradient,
          border: `4px solid ${currentTheme.borderColor}`,
          borderRadius: 20,
          boxShadow: currentTheme.boxShadow,
          position: "relative",
          overflow: "hidden",
          transform: `scale(${phaseScale}) rotateX(${phaseRotateX}deg)`,
          opacity: phaseOpacity,
          transition: "background 0.5s ease, border 0.5s ease, box-shadow 0.5s ease",
        }}
      >
        {/* Subtle Diagonal Gloss Reflection */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: "42%",
            background:
              "linear-gradient(180deg, rgba(255, 255, 255, 0.18) 0%, transparent 100%)",
            pointerEvents: "none",
            zIndex: 2,
          }}
        />

        {/* Dynamic Subtle Sweep Ray Light */}
        <div
          style={{
            position: "absolute",
            top: -50,
            bottom: -50,
            left: "-60%",
            width: "50%",
            background:
              "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.15) 50%, transparent 100%)",
            transform: `translateX(${(frame % 180) * 12}px) skewX(-25deg)`,
            pointerEvents: "none",
            zIndex: 3,
          }}
        />

        {/* ─── 3. INNER INSET FRAMED BORDER (100% Broadcast News Style) ─── */}
        <div
          style={{
            position: "absolute",
            top: 14,
            left: 14,
            right: 14,
            bottom: 14,
            border: `2px solid ${currentTheme.innerBorderColor}`,
            borderRadius: 14,
            padding: "16px 22px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            alignItems: "center",
            textAlign: "center",
            zIndex: 5,
          }}
        >
          {/* Top Status & Sequence Pill Indicator */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              width: "100%",
              padding: "4px 8px",
            }}
          >
            {/* Live Indicator Pill */}
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                backgroundColor: currentTheme.accentPillBg,
                border: `1.5px solid ${currentTheme.borderColor}`,
                borderRadius: 20,
                padding: "3px 14px",
                fontSize: 18,
                fontWeight: 800,
                color: currentTheme.accentPillText,
                letterSpacing: "1px",
              }}
            >
              <span
                style={{
                  width: 9,
                  height: 9,
                  borderRadius: "50%",
                  backgroundColor: currentTheme.borderColor,
                  boxShadow: `0 0 8px ${currentTheme.borderColor}`,
                  display: "inline-block",
                }}
              />
              अपडेट {currentIdx + 1} / {numHeadlines}
            </div>

            {/* Topic Category Tag */}
            <div
              style={{
                fontSize: 16,
                fontWeight: 800,
                color: "rgba(255, 255, 255, 0.75)",
                letterSpacing: "0.8px",
                textTransform: "uppercase",
              }}
            >
              {_category || "विशेष बुलेटिन"}
            </div>
          </div>

          {/* ─── 4. THE ACTIVE HEADLINE (Hero Typography, Full Centered, Non-Crammed!) ─── */}
          <div
            style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: "100%",
              padding: "8px 12px",
            }}
          >
            <div
              style={{
                color: "#ffffff",
                fontSize: heroFontSize,
                fontWeight: 900,
                lineHeight: 1.35,
                letterSpacing: "0.4px",
                textAlign: "center",
                wordBreak: "break-word",
                textShadow:
                  "0 4px 16px rgba(0, 0, 0, 0.95), 0 0 28px rgba(0, 0, 0, 0.85)",
              }}
            >
              <span>{displayedText}</span>
              {isTyping && (
                <span
                  style={{
                    display: "inline-block",
                    width: 4,
                    height: heroFontSize * 0.85,
                    backgroundColor: currentTheme.borderColor,
                    marginLeft: 6,
                    verticalAlign: "middle",
                    opacity: cursorBlink ? 1 : 0.1,
                    boxShadow: `0 0 10px ${currentTheme.borderColor}`,
                  }}
                />
              )}
            </div>
          </div>

          {/* Bottom Broadcast Progress Indicator Dots */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 10,
              paddingBottom: 4,
            }}
          >
            {activeHeadlines.map((_, hIdx) => {
              const isActive = hIdx === currentIdx;
              const isPast = hIdx < currentIdx;
              return (
                <div
                  key={hIdx}
                  style={{
                    width: isActive ? 28 : 10,
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: isActive
                      ? currentTheme.borderColor
                      : isPast
                      ? "rgba(255, 255, 255, 0.6)"
                      : "rgba(255, 255, 255, 0.2)",
                    boxShadow: isActive
                      ? `0 0 10px ${currentTheme.borderColor}`
                      : "none",
                    transition: "all 0.3s ease",
                  }}
                />
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
