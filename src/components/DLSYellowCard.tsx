/**
 * DLS News – Yellow Headline Card (Right Side)
 * Bright yellow card with bold black Hindi text and red border
 * Shows the main story detail/bullet points in ultra-bold text
 * Exactly matches the DLS News reference video
 */
import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { DLS_COLORS } from "../types";
import { DLSBreakingBadge } from "./DLSBreakingBadge";

interface DLSYellowCardProps {
  bulletPoints: string[];
  category: string;
}

export const DLSYellowCard: React.FC<DLSYellowCardProps> = ({
  bulletPoints,
  category,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Card slides in from right
  const translateX = spring({
    frame,
    fps,
    from: 400,
    to: 0,
    config: { damping: 14, mass: 0.8 },
    delay: 3,
  });

  const opacity = spring({
    frame,
    fps,
    from: 0,
    to: 1,
    config: { damping: 20 },
    delay: 3,
  });

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 16,
        transform: `translateX(${translateX}px)`,
        opacity,
      }}
    >
      {/* Breaking News Badge */}
      <div style={{ display: "flex", justifyContent: "flex-start" }}>
        <DLSBreakingBadge />
      </div>

      {/* Category pill */}
      <div
        style={{
          display: "inline-flex",
          alignSelf: "flex-start",
          background: "rgba(255,255,255,0.15)",
          border: "1px solid rgba(255,255,255,0.3)",
          color: DLS_COLORS.textWhite,
          fontSize: 16,
          fontWeight: 700,
          padding: "4px 14px",
          borderRadius: 4,
          letterSpacing: "0.5px",
        }}
      >
        ⚡ {category}
      </div>

      {/* Main Yellow Card */}
      <div
        style={{
          background: DLS_COLORS.yellowCard,
          border: `3px solid ${DLS_COLORS.yellowCardBorder}`,
          borderRadius: 10,
          padding: "28px 32px",
          boxShadow: "0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.3)",
        }}
      >
        {/* Render each bullet point as a separate line */}
        {bulletPoints.map((point, i) => (
          <div
            key={i}
            style={{
              color: DLS_COLORS.textBlack,
              fontSize: 34,
              fontWeight: 900,
              lineHeight: 1.35,
              marginBottom: i < bulletPoints.length - 1 ? 12 : 0,
              letterSpacing: "0.3px",
            }}
          >
            {point}
          </div>
        ))}
      </div>
    </div>
  );
};
