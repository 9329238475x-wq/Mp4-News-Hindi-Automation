/**
 * Master Newsroom Card (Right Side)
 * Exactly matches 'news-preview.png':
 * - Top Badge: [🚨 BREAKING NEWS • बड़ी खबर]
 * - Headline: Large, auto-clamped bold Hindi text (Never overflows screen)
 * - Subtitle: Cyan/Blue Category Highlight
 * - 2 Sleek Dark Glass Bullet Points with Staggered Spring Entrance
 * - Bottom Bar: [🎙️ विशेष संवाददाता | स्रोत] + [AUDIO |||||||| Equalizer]
 */
import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { TV_COLORS } from "../types";
import { AudioEqualizer } from "./AudioEqualizer";

interface NewsroomCardProps {
  headline: string;
  category: string;
  bulletPoints: string[];
  reporterSource?: string;
  audioWaveform?: number[];
  audioStartFrame?: number;
}

export const NewsroomCard: React.FC<NewsroomCardProps> = ({
  headline,
  category,
  bulletPoints = [],
  reporterSource = "विशेष संवाददाता | AI न्यूज़रूम",
  audioWaveform = [],
  audioStartFrame = 15,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring for main card container
  const cardEnter = spring({
    frame,
    fps,
    from: 0.92,
    to: 1,
    config: { damping: 14, mass: 0.8 },
  });

  const cardOpacity = spring({
    frame,
    fps,
    from: 0,
    to: 1,
    config: { damping: 18 },
  });

  // Staggered spring animations for bullet points
  // Point 1 enters right when voiceover starts (audioStartFrame)
  const bp1Progress = spring({
    frame: Math.max(0, frame - audioStartFrame),
    fps,
    from: 0,
    to: 1,
    config: { damping: 14, mass: 0.7 },
  });

  // Point 2 enters 25 frames (~0.8s) after voiceover starts
  const bp2Progress = spring({
    frame: Math.max(0, frame - (audioStartFrame + 25)),
    fps,
    from: 0,
    to: 1,
    config: { damping: 14, mass: 0.7 },
  });

  // Limit to max 2 bullet points on screen as agreed in plan to avoid crowding
  const displayPoints = bulletPoints.slice(0, 2);

  // Auto-calculated dynamic font size based on length
  const headlineLength = headline.length;
  let headlineFontSize = 32;
  if (headlineLength > 65) {
    headlineFontSize = 25;
  } else if (headlineLength > 45) {
    headlineFontSize = 28;
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 16,
        transform: `scale(${cardEnter})`,
        opacity: cardOpacity,
        width: "100%",
        fontFamily: "'Noto Sans Devanagari', 'Segoe UI', sans-serif",
      }}
    >
      {/* ─── TOP BADGE: [🚨 BREAKING NEWS • बड़ी खबर] ─── */}
      <div style={{ display: "flex", justifyContent: "flex-start" }}>
        <div
          style={{
            background: TV_COLORS.breakingBadgeGradient,
            padding: "8px 24px",
            borderRadius: 8,
            boxShadow: "0 4px 18px rgba(255, 23, 68, 0.45)",
            border: "1px solid rgba(255, 100, 140, 0.4)",
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <span style={{ fontSize: 16 }}>🚨</span>
          <span
            style={{
              color: "#ffffff",
              fontSize: 18,
              fontWeight: 900,
              letterSpacing: "1px",
              textTransform: "uppercase",
            }}
          >
            BREAKING NEWS • बड़ी खबर
          </span>
        </div>
      </div>

      {/* ─── MAIN GLASS PANEL ─── */}
      <div
        style={{
          background: TV_COLORS.glassCardBg,
          backdropFilter: "blur(14px)",
          border: `1.5px solid ${TV_COLORS.glassCardBorder}`,
          borderRadius: 12,
          padding: "26px 30px",
          boxShadow: "0 10px 40px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(0, 240, 255, 0.2)",
          display: "flex",
          flexDirection: "column",
          gap: 16,
        }}
      >
        {/* Main Screen Headline (Safe line-clamping & Auto-Sized) */}
        <h1
          style={{
            margin: 0,
            color: TV_COLORS.headlineWhite,
            fontSize: headlineFontSize,
            fontWeight: 900,
            lineHeight: 1.28,
            letterSpacing: "0.2px",
            textShadow: "0 2px 8px rgba(0,0,0,0.85)",
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
            maxHeight: "84px",
          }}
        >
          {headline}
        </h1>

        {/* Sub-headline / Category Glow Line */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            color: TV_COLORS.categoryCyan,
            fontSize: 18,
            fontWeight: 700,
            letterSpacing: "0.3px",
            textShadow: `0 0 10px ${TV_COLORS.neonCyanGlow}`,
          }}
        >
          <span style={{ color: TV_COLORS.categoryBlue }}>{category}</span>
          <span style={{ color: "rgba(255,255,255,0.4)" }}>|</span>
          <span style={{ color: "#e0f2fe" }}>विशेष रिपोर्ट & संपूर्ण कवरेज</span>
        </div>

        {/* ─── 2 DARK GLASS BULLET POINTS CONTAINER ─── */}
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {displayPoints.map((point, idx) => {
            const progress = idx === 0 ? bp1Progress : bp2Progress;
            // Clean markdown ** for display while preserving text
            const cleanText = point.replace(/\*\*/g, "").trim();

            return (
              <div
                key={idx}
                style={{
                  background: TV_COLORS.bulletPillBg,
                  border: `1px solid ${TV_COLORS.bulletPillBorder}`,
                  borderRadius: 8,
                  padding: "12px 18px",
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 12,
                  boxShadow: "0 3px 12px rgba(0, 0, 0, 0.3)",
                  transform: `translateX(${(1 - progress) * 24}px)`,
                  opacity: progress,
                  transition: "transform 0.1s ease, opacity 0.1s ease",
                }}
              >
                {/* Gold Arrow Bullet */}
                <span
                  style={{
                    color: TV_COLORS.bulletArrowGold,
                    fontSize: 16,
                    lineHeight: "24px",
                    flexShrink: 0,
                  }}
                >
                  ▶
                </span>

                {/* Point Text (Line clamped to max 2 lines) */}
                <div
                  style={{
                    color: TV_COLORS.bulletTextWhite,
                    fontSize: 18,
                    fontWeight: 600,
                    lineHeight: 1.35,
                    display: "-webkit-box",
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: "vertical",
                    overflow: "hidden",
                  }}
                >
                  {cleanText}
                </div>
              </div>
            );
          })}
        </div>

        {/* ─── CARD BOTTOM BAR: REPORTER + EQUALIZER ─── */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            paddingTop: 8,
            borderTop: "1px solid rgba(255, 255, 255, 0.08)",
            marginTop: 4,
          }}
        >
          {/* Reporter Source Attribution */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              color: "#94a3b8",
              fontSize: 14,
              fontWeight: 600,
            }}
          >
            <span>🎙️</span>
            <span>{reporterSource}</span>
          </div>

          {/* Real Audio-Synced Equalizer */}
          <AudioEqualizer
            waveform={audioWaveform}
            currentFrame={frame}
            audioStartFrame={audioStartFrame}
          />
        </div>
      </div>
    </div>
  );
};
