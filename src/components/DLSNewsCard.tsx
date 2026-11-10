/**
 * DLS News – Master Animated Broadcast Card
 * 100% matches user's uploaded reference images & requested layout:
 * 1. Initial Hook (Frames 0-42): Card is mathematically centered on screen (left: 480px, width: 960px)
 * 2. Transition (Frames 42-65): Card animates & slides to the Right side (left: 980px, width: 850px)
 * 3. Taraju (Seesaw) Focus Orchestration:
 *    - When Media Showcase expands, Card gracefully recedes to background
 *    - When Card returns to foreground, the NEXT bullet point types out live in 2.0s!
 * 4. Text Live-Typing Animation:
 *    - Card appears EMPTY initially (no pre-written text)
 *    - Text types out live over exact 2.0 seconds (60 frames) using Unicode grapheme segmentation
 *    - Dynamic blinking broadcast cursor while typing
 * 5. Text Styling:
 *    - ONLY Pure White text (#ffffff)
 *    - Ultra Bold 900 weight (60px short, 52px medium) with crisp broadcast shadow
 * 6. Pinned on Top Center: [ BREAKING | NEWS ] Animated Badge with 3D Ulat-Palat flip
 */
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { DLSBreakingBadge } from "./DLSBreakingBadge";

interface DLSNewsCardProps {
  headline: string;
  headlines?: string[];
  category: string;
  bulletPoints: string[];
  expandProgress?: number;
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
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // ─── 1. CENTER-TO-RIGHT CHOREOGRAPHY ANIMATION (CENTER NORMAL -> SIDE 5:6) ───
  // A. Initial Center Entrance: Exact previous size (Width: 960, Height: 390, Centered at X=480, Y=320)
  const entranceSpring = spring({
    frame,
    fps,
    config: { damping: 13, mass: 0.7 },
  });
  const entranceOpacity = interpolate(entranceSpring, [0, 1], [0, 1]);
  const entranceScale = interpolate(entranceSpring, [0, 1], [0.9, 1.0]);

  // B. Stay 3 seconds in Center (Frames 70 to 165), THEN slide to Right Side (at Frame 165)
  // "pehle jitna hi aur usi size me hona chahiye bhai jab ye side me jaye tab ye 5:6 size me ho jana chahiye"
  const slideProgress = spring({
    frame: Math.max(0, frame - 165),
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 90 },
  });

  // Center: Width 960, Height 390, Top 300, Left 480
  // Side: Compact box (Width: 640, Height: 520, Top 210, Left 1110)
  // Perfectly matches user's red box and aligns with 16:9 media showcase!
  const currentLeft = interpolate(slideProgress, [0, 1], [480, 1110]);
  const currentWidth = interpolate(slideProgress, [0, 1], [960, 640]);
  const currentTop = interpolate(slideProgress, [0, 1], [300, 210]);
  const cardHeight = interpolate(slideProgress, [0, 1], [390, 520]);
  const sizeScale = entranceScale;

  // ─── 2. TARAJU (SEESAW) CARD VISIBILITY ───
  // When Media Panel expands (expandProgress -> 1), Card steps back smoothly
  const tarajuOpacity = interpolate(expandProgress, [0, 0.35, 1], [1, 0, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const tarajuScale = interpolate(expandProgress, [0, 1], [1, 0.92], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ─── 3. DYNAMIC PHASE SYNCHRONIZATION WITH TARAJU RHYTHM ───
  // Phase 0: Frames 0-620 (Headline 1, types live at frame 10)
  // Phase 1: Frames 620-1100 (Headline 2, types live at frame 630 on Taraju return)
  // Phase 2: Frames 1100-1580 (Headline 3, types live at frame 1110 on Taraju return)
  // Phase 3: Frames 1580+ (Headline 4, types live at frame 1590 on Taraju return)
  let currentPhase = 0;
  let typingStartFrame = 10;

  if (frame >= 1580) {
    currentPhase = 3;
    typingStartFrame = 1590;
  } else if (frame >= 1100) {
    currentPhase = 2;
    typingStartFrame = 1110;
  } else if (frame >= 620) {
    currentPhase = 1;
    typingStartFrame = 630;
  } else {
    currentPhase = 0;
    typingStartFrame = 10;
  }

  // ─── CARD THEMES DEFINITION (Dark/Rich backgrounds for 100% White Text Contrast) ───
  interface CardTheme {
    bgGradient: string;
    borderColor: string;
    shadowColor: string;
  }

  const themes: CardTheme[] = [
    // Phase 0: Deep Royal Blue Card
    {
      bgGradient: "linear-gradient(180deg, #001f7a 0%, #001247 100%)",
      borderColor: "#ffffff",
      shadowColor: "rgba(0, 31, 122, 0.75)",
    },
    // Phase 1: Deep Crimson Red Card
    {
      bgGradient: "linear-gradient(180deg, #b80000 0%, #750000 100%)",
      borderColor: "#ffffff",
      shadowColor: "rgba(184, 0, 0, 0.75)",
    },
    // Phase 2: Deep Midnight Navy Card
    {
      bgGradient: "linear-gradient(180deg, #0a2569 0%, #051336 100%)",
      borderColor: "#ffffff",
      shadowColor: "rgba(10, 37, 105, 0.75)",
    },
    // Phase 3: Deep Maroon / Ruby Card
    {
      bgGradient: "linear-gradient(180deg, #8a0024 0%, #540016 100%)",
      borderColor: "#ffffff",
      shadowColor: "rgba(138, 0, 36, 0.75)",
    },
  ];

  const currentTheme = themes[currentPhase % themes.length];

  // Determine what text to display in this phase (Sequential Changing Headlines)
  let phaseText = headline;
  if (headlines && headlines.length > 0) {
    if (currentPhase === 0) {
      phaseText = headlines[0] || headline;
    } else if (currentPhase === 1) {
      phaseText = headlines[1] || headlines[0] || headline;
    } else if (currentPhase === 2) {
      phaseText = headlines[2] || headlines[1] || headline;
    } else if (currentPhase >= 3) {
      phaseText = headlines[3] || headlines[2] || headline;
    }
  } else {
    if (currentPhase === 1 && bulletPoints.length > 0) {
      phaseText = bulletPoints[0];
    } else if (currentPhase === 2 && bulletPoints.length > 1) {
      phaseText = bulletPoints[1];
    } else if (currentPhase === 3 && bulletPoints.length > 2) {
      phaseText = bulletPoints[2];
    }
  }

  phaseText = phaseText
    .replace(/\bट्रेन आगे\b/g, "ट्रेन के आगे")
    .replace(/\bगोली धमकी\b/g, "गोली मारने की धमकी")
    .replace(/\bडिसिपी\b/g, "डीसीपी");

  // ─── 4. LIVE TYPEWRITER / TELEPRINTER ANIMATION (Exact 2.0s = 60 Frames) ───
  const typingDurationFrames = 60; // 2.0 seconds at 30 fps
  const graphemes = getHindiGraphemes(phaseText);
  const totalGraphemes = graphemes.length;

  const elapsedTyping = Math.max(0, frame - typingStartFrame);
  const visibleCount = Math.min(
    totalGraphemes,
    Math.floor(
      interpolate(elapsedTyping, [0, typingDurationFrames], [0, totalGraphemes], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    )
  );

  const displayedText = graphemes.slice(0, visibleCount).join("");
  const isTyping = elapsedTyping > 0 && elapsedTyping < typingDurationFrames;
  const cursorBlink = Math.floor(frame / 6) % 2 === 0;

  // Dynamic Font Sizing: Morphs smoothly from Center size (56-60px) to Side 5:6 size (44-48px)
  const isShortText = phaseText.length <= 50;
  const isMidText = phaseText.length <= 80;
  const isLongText = phaseText.length <= 110;

  const centerFontSize = isShortText ? 60 : isMidText ? 52 : isLongText ? 44 : 38;
  const sideFontSize = isShortText ? 48 : isMidText ? 42 : isLongText ? 36 : 32;
  const fontSize = Math.round(interpolate(slideProgress, [0, 1], [centerFontSize, sideFontSize]));

  const centerLineHeight = 1.34;
  const sideLineHeight = 1.36;
  const lineHeight = interpolate(slideProgress, [0, 1], [centerLineHeight, sideLineHeight]);

  // Helper to parse **bold** highlights while strictly maintaining pure white text color
  const renderHighlightedText = (text: string) => {
    if (!text.includes("**")) {
      return text;
    }
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, idx) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        const clean = part.slice(2, -2);
        return (
          <span
            key={idx}
            style={{
              color: "#ffffff",
              backgroundColor: "rgba(255, 255, 255, 0.18)",
              borderBottom: "3px solid #ffffff",
              padding: "2px 8px",
              borderRadius: 4,
              margin: "0 4px",
              display: "inline-block",
            }}
          >
            {clean}
          </span>
        );
      }
      return <span key={idx}>{part}</span>;
    });
  };

  return (
    <div
      style={{
        position: "absolute",
        top: currentTop,
        left: `${currentLeft}px`,
        width: `${currentWidth}px`,
        transform: `scale(${sizeScale * tarajuScale})`,
        opacity: entranceOpacity * tarajuOpacity,
        zIndex: 40,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        fontFamily: "'Noto Sans Devanagari', 'Segoe UI', sans-serif",
        pointerEvents: tarajuOpacity < 0.1 ? "none" : "auto",
        transition: "opacity 0.25s ease, transform 0.25s ease",
      }}
    >
      {/* ─── 1. TOP [ BREAKING | NEWS ] BADGE (Horizontally centered above card) ─── */}
      <div
        style={{
          width: "100%",
          display: "flex",
          justifyContent: "center",
          marginBottom: -14,
          position: "relative",
          zIndex: 20,
          perspective: 1200,
        }}
      >
        <DLSBreakingBadge />
      </div>

      {/* ─── 2. MAIN COMPACT VIBRANT CARD (Smoothly shrinks from 430px to 390px) ─── */}
      <div
        style={{
          width: "100%",
          height: cardHeight,
          background: currentTheme.bgGradient,
          border: `4px solid ${currentTheme.borderColor}`,
          borderRadius: 18,
          padding: "32px 38px 24px 38px",
          boxShadow: `0 16px 44px rgba(0, 0, 0, 0.75), 0 0 28px ${currentTheme.shadowColor}, inset 0 2px 0 rgba(255, 255, 255, 0.45)`,
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

        {/* Live Typing Big Bold Text - ONLY PURE WHITE (#ffffff), Bold 900 */}
        <div
          style={{
            color: "#ffffff",
            fontSize,
            fontWeight: 900,
            lineHeight,
            letterSpacing: "0.5px",
            textShadow:
              "0 3px 12px rgba(0, 0, 0, 0.95), 0 0 22px rgba(0, 0, 0, 0.75)",
            zIndex: 5,
            padding: "0 12px",
            minHeight: fontSize * 1.5,
            display: "inline-block",
          }}
        >
          {renderHighlightedText(displayedText)}

          {/* Live Teleprinter Blinking Cursor */}
          {isTyping && (
            <span
              style={{
                display: "inline-block",
                width: 4,
                height: fontSize * 0.85,
                backgroundColor: "#ffffff",
                marginLeft: 6,
                verticalAlign: "middle",
                opacity: cursorBlink ? 1 : 0.1,
                boxShadow:
                  "0 0 10px #ffffff, 0 0 18px rgba(255, 255, 255, 0.85)",
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};
