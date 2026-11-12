/**
 * DLS News – Master Animated Broadcast Chyron Card
 * 100% matches user's reference image (media_1794475292981_0f8c9df6.jpg):
 * 1. 4-Line Full Vertical Layout: Fills the entire card with zero empty space
 *    - Line 1: Case / Context with colon (e.g. महादेव सट्टा सिंडिकेट मामला:)
 *    - Line 2: Timeline / Action (e.g. 12 नवंबर को खत्म होगी)
 *    - Line 3: Entity in Yellow Box + Action (e.g. [सौरभ चंद्राकर] की रिमांड,)
 *    - Line 4: Consequence / Big Number (e.g. खुलेंगे 6000 करोड़ के राज!)
 * 2. Visual Architecture:
 *    - Broadcast Deep Crimson Red Gradient (#ba0009 -> #8b0004 -> #630002)
 *    - Double White Border: Outer 4px solid #ffffff + Inner 2px solid rgba(255,255,255,0.85) frame
 *    - Top [ BREAKING | NEWS ] 3D Flip Badge
 * 3. Positioning & Choreography:
 *    - Center Entrance (Frames 0-165): left: 480px, top: 250px, width: 960px, height: 460px
 *    - Side Transition (Frames 165+): left: 1110px, top: 240px, width: 730px, height: 551px
 *      (Mathematically aligned with Media Showcase on left at top: 240px, height: 551px!)
 * 4. Staggered Typewriter Reveal:
 *    - Sequential line-by-line typing with Hindi grapheme preservation & blinking cursor
 * 5. Taraju (Seesaw) Orchestration:
 *    - Smoothly fades back when Media Showcase expands, returns sharp on focus
 */
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { DLSBreakingBadge } from "./DLSBreakingBadge";

interface DLSNewsCardProps {
  headline: string;
  headlines?: string[];
  category: string;
  bulletPoints?: string[];
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

// Auto-wrap entity in **...** if missing on Line 3
const ensureEntityHighlight = (text: string): string => {
  if (!text || text.includes("**")) return text;
  const postpositions = [" की ", " ने ", " पर ", " को ", " से ", " का ", " के ", " द्वारा "];
  for (const pp of postpositions) {
    if (text.includes(pp)) {
      const parts = text.split(pp);
      const words = parts[0].trim().split(/\s+/);
      if (words.length >= 1 && words.length <= 4) {
        return `**${parts[0].trim()}**${pp}${parts.slice(1).join(pp).trim()}`;
      }
    }
  }
  const words = text.trim().split(/\s+/);
  if (words.length >= 2) {
    return `**${words[0]} ${words[1]}** ` + words.slice(2).join(" ");
  }
  return text;
};

// Smart fallback splitter: splits single headline text into 4 broadcast-card lines
const splitTextInto4Lines = (rawText: string): string[] => {
  const clean = (rawText || "")
    .replace(/\n+/g, " ")
    .replace(/\bट्रेन आगे\b/g, "ट्रेन के आगे")
    .replace(/\bगोली धमकी\b/g, "गोली मारने की धमकी")
    .replace(/\bडिसिपी\b/g, "डीसीपी")
    .trim();

  if (!clean) {
    return ["ताज़ा बड़ी खबर:", "मुख्य घटनाक्रम जारी", "**प्रशासन** अलर्ट पर,", "जांच में बड़ा खुलासा!"];
  }

  // If text already has newlines
  if (rawText && rawText.includes("\n")) {
    const splitLines = rawText.split("\n").map((l) => l.trim()).filter(Boolean);
    if (splitLines.length >= 4) return splitLines.slice(0, 4);
    if (splitLines.length === 3) return [splitLines[0], splitLines[1], splitLines[2], ""];
  }

  // Check for colon (case / topic separator)
  let topic = "";
  let rest = clean;
  if (clean.includes(":")) {
    const idx = clean.indexOf(":");
    topic = clean.slice(0, idx + 1).trim();
    rest = clean.slice(idx + 1).trim();
  } else if (clean.includes(" - ")) {
    const idx = clean.indexOf(" - ");
    topic = clean.slice(0, idx).trim() + ":";
    rest = clean.slice(idx + 3).trim();
  } else if (clean.includes(" | ")) {
    const idx = clean.indexOf(" | ");
    topic = clean.slice(0, idx).trim() + ":";
    rest = clean.slice(idx + 3).trim();
  }

  const words = rest.split(/\s+/).filter(Boolean);

  if (topic) {
    const perLine = Math.max(2, Math.ceil(words.length / 3));
    const l2 = words.slice(0, perLine).join(" ");
    const l3 = words.slice(perLine, perLine * 2).join(" ");
    const l4 = words.slice(perLine * 2).join(" ");
    return [topic, l2, ensureEntityHighlight(l3), l4 || "बड़ा अपडेट जारी!"];
  }

  // No topic separator: partition all words into 4 lines
  const perLine = Math.max(2, Math.ceil(words.length / 4));
  const l1 = words.slice(0, perLine).join(" ") + ":";
  const l2 = words.slice(perLine, perLine * 2).join(" ");
  const l3 = words.slice(perLine * 2, perLine * 3).join(" ");
  const l4 = words.slice(perLine * 3).join(" ");
  return [l1, l2, ensureEntityHighlight(l3), l4 || "ताज़ा विवरण प्रतीक्षित!"];
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

  // ─── 1. CENTER-TO-RIGHT CHOREOGRAPHY ANIMATION ───
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
  // Center: left 480, top 250, width 960, height 460
  // Side:   left 1110, top 240, width 730, height 551 (Matches Media Showcase at top: 240, height: 551!)
  const currentLeft = interpolate(slideProgress, [0, 1], [480, 1110]);
  const currentTop = interpolate(slideProgress, [0, 1], [250, 240]);
  const currentWidth = interpolate(slideProgress, [0, 1], [960, 730]);
  const currentHeight = interpolate(slideProgress, [0, 1], [460, 551]);

  // ─── 2. TARAJU (SEESAW) FOCUS ORCHESTRATION ───
  const tarajuOpacity = interpolate(expandProgress, [0, 0.35, 1], [1, 0, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const tarajuScale = interpolate(expandProgress, [0, 1], [1, 0.94], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ─── 3. RESOLVE 4 BROADCAST LINES (Card Never Empty!) ───
  // Phase handling: if 8 headlines provided, switch to Set 2 after frame 620
  let raw4Lines: string[] = [];
  let typingStartFrame = 8;

  if (headlines && headlines.length >= 8) {
    if (frame >= 620) {
      raw4Lines = headlines.slice(4, 8);
      typingStartFrame = 630;
    } else {
      raw4Lines = headlines.slice(0, 4);
      typingStartFrame = 8;
    }
  } else if (headlines && headlines.length >= 3) {
    raw4Lines = headlines.slice(0, 4);
    while (raw4Lines.length < 4) raw4Lines.push("");
  } else if (headline && headline.trim()) {
    raw4Lines = splitTextInto4Lines(headline);
  } else if (bulletPoints && bulletPoints.length >= 3) {
    raw4Lines = [
      bulletPoints[0] + ":",
      bulletPoints[1] || "",
      bulletPoints[2] || "",
      bulletPoints[3] || "बड़ा खुलासा!",
    ];
  } else {
    raw4Lines = [
      "ताज़ा बड़ी खबर:",
      "मामले में नया मोड़ आया",
      "**पुलिस प्रशासन** अलर्ट पर,",
      "खुलेंगे बड़े राज!",
    ];
  }

  // Ensure Line 3 has yellow-highlight entity marker
  if (raw4Lines[2]) {
    raw4Lines[2] = ensureEntityHighlight(raw4Lines[2]);
  }

  // ─── 4. SEQUENTIAL HINDI TYPEWRITER ANIMATION ACROSS 4 LINES ───
  // Each line types out in succession (14 frames per line = 56 frames ~ 1.85s)
  const lineTypingDuration = 14;
  const cursorBlink = Math.floor(frame / 6) % 2 === 0;

  // Font size interpolation between Center & Side
  const fontSize1 = Math.round(interpolate(slideProgress, [0, 1], [46, 40]));
  const fontSize2 = Math.round(interpolate(slideProgress, [0, 1], [50, 44]));
  const fontSize3 = Math.round(interpolate(slideProgress, [0, 1], [50, 44]));
  const fontSize4 = Math.round(interpolate(slideProgress, [0, 1], [50, 44]));
  const fontSizes = [fontSize1, fontSize2, fontSize3, fontSize4];

  // Helper to render a single line with typing & yellow highlight box
  const renderLine = (lineIdx: number) => {
    const rawLine = raw4Lines[lineIdx] || "";
    if (!rawLine.trim()) return null;

    const lineStart = typingStartFrame + lineIdx * lineTypingDuration;
    const elapsed = Math.max(0, frame - lineStart);

    // Entity highlight parsing
    const match = rawLine.match(/\*\*([^*]+)\*\*/);
    const plainText = rawLine.replace(/\*\*/g, "").trim();
    const graphemes = getHindiGraphemes(plainText);
    const totalGraphemes = graphemes.length;

    const visibleCount = Math.min(
      totalGraphemes,
      Math.floor(
        interpolate(elapsed, [0, lineTypingDuration], [0, totalGraphemes], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })
      )
    );

    const isCurrentlyTyping = elapsed > 0 && elapsed < lineTypingDuration;
    const displayedGraphemes = graphemes.slice(0, visibleCount);
    const displayedText = displayedGraphemes.join("");
    const fSize = fontSizes[lineIdx] || 44;

    if (!match) {
      // Normal Line (Pure White Text)
      return (
        <div
          key={lineIdx}
          style={{
            color: "#ffffff",
            fontSize: fSize,
            fontWeight: 900,
            lineHeight: 1.28,
            letterSpacing: lineIdx === 0 ? "0.6px" : "0.3px",
            textShadow:
              "0 2px 10px rgba(0, 0, 0, 0.95), 0 0 20px rgba(0, 0, 0, 0.8)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: "100%",
            padding: "2px 8px",
            minHeight: fSize * 1.3,
            textAlign: "center",
          }}
        >
          <span>{displayedText}</span>
          {isCurrentlyTyping && (
            <span
              style={{
                display: "inline-block",
                width: 3.5,
                height: fSize * 0.85,
                backgroundColor: "#ffffff",
                marginLeft: 6,
                opacity: cursorBlink ? 1 : 0.1,
                boxShadow: "0 0 8px #ffffff, 0 0 16px rgba(255, 255, 255, 0.85)",
              }}
            />
          )}
        </div>
      );
    }

    // Line with Yellow Entity Highlight Box (matches media_1794475292981_0f8c9df6.jpg)
    const entityText = match[1];
    const entityIdx = plainText.indexOf(entityText);
    const prefix = entityIdx > 0 ? plainText.slice(0, entityIdx) : "";
    const suffix = plainText.slice(entityIdx + entityText.length);

    const prefixLen = getHindiGraphemes(prefix).length;
    const entityLen = getHindiGraphemes(entityText).length;

    const visiblePrefix = displayedGraphemes.slice(0, prefixLen).join("");
    const visibleEntity = displayedGraphemes
      .slice(prefixLen, prefixLen + entityLen)
      .join("");
    const visibleSuffix = displayedGraphemes
      .slice(prefixLen + entityLen)
      .join("");

    return (
      <div
        key={lineIdx}
        style={{
          color: "#ffffff",
          fontSize: fSize,
          fontWeight: 900,
          lineHeight: 1.28,
          letterSpacing: "0.3px",
          textShadow:
            "0 2px 10px rgba(0, 0, 0, 0.95), 0 0 20px rgba(0, 0, 0, 0.8)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexWrap: "wrap",
          width: "100%",
          padding: "2px 8px",
          minHeight: fSize * 1.3,
          textAlign: "center",
        }}
      >
        {visiblePrefix && <span>{visiblePrefix}</span>}
        {visibleEntity && (
          <span
            style={{
              backgroundColor: "#ffcc00", // Vibrant Broadcast Yellow
              color: "#000000",           // Jet Black Text
              padding: "2px 12px",
              borderRadius: 5,
              fontWeight: 900,
              margin: "0 6px",
              display: "inline-block",
              boxShadow: "0 3px 10px rgba(0, 0, 0, 0.5)",
              lineHeight: 1.15,
              textShadow: "none",
            }}
          >
            {visibleEntity}
          </span>
        )}
        {visibleSuffix && <span>{visibleSuffix}</span>}
        {isCurrentlyTyping && (
          <span
            style={{
              display: "inline-block",
              width: 3.5,
              height: fSize * 0.85,
              backgroundColor: "#ffffff",
              marginLeft: 6,
              opacity: cursorBlink ? 1 : 0.1,
              boxShadow: "0 0 8px #ffffff, 0 0 16px rgba(255, 255, 255, 0.85)",
            }}
          />
        )}
      </div>
    );
  };

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
      }}
    >
      {/* ─── 1. TOP [ BREAKING | NEWS ] BADGE ─── */}
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

      {/* ─── 2. MAIN BROADCAST CARD CONTAINER (Deep Crimson Red Gradient + Double Border) ─── */}
      <div
        style={{
          width: "100%",
          height: currentHeight,
          background:
            "linear-gradient(180deg, #ba0009 0%, #8b0004 50%, #630002 100%)",
          border: "4px solid #ffffff",
          borderRadius: 18,
          boxShadow:
            "0 16px 44px rgba(0, 0, 0, 0.85), 0 0 32px rgba(186, 0, 9, 0.65), inset 0 2px 0 rgba(255, 255, 255, 0.45)",
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
            background:
              "linear-gradient(180deg, rgba(255, 255, 255, 0.16) 0%, transparent 100%)",
            pointerEvents: "none",
            zIndex: 2,
          }}
        />

        {/* ─── 3. INNER INSET FRAMED BORDER (100% Matches Reference Screenshot) ─── */}
        <div
          style={{
            position: "absolute",
            top: 12,
            left: 12,
            right: 12,
            bottom: 12,
            border: "2px solid rgba(255, 255, 255, 0.85)",
            borderRadius: 12,
            padding: "8px 14px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-evenly",
            alignItems: "center",
            textAlign: "center",
            zIndex: 5,
          }}
        >
          {/* 4 Stacked Lines Filling the Entire Vertical Height */}
          {renderLine(0)}
          {renderLine(1)}
          {renderLine(2)}
          {renderLine(3)}
        </div>
      </div>
    </div>
  );
};
