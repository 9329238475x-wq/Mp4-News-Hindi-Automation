/**
 * DLS News – Bottom Scrolling Ticker
 * Full-width bottom strip with:
 * - Left: "BREAKING NEWS" red box
 * - Right: Continuously scrolling Hindi headlines with emojis and subscribe CTA
 * Exactly like the DLS News reference video
 */
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { DLS_COLORS } from "../types";

interface DLSTickerProps {
  headlines: string[];
  channelName: string;
}

export const DLSTicker: React.FC<DLSTickerProps> = ({
  headlines,
  channelName,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Entrance from bottom
  const translateY = spring({
    frame,
    fps,
    from: 80,
    to: 0,
    config: { damping: 14 },
  });

  // Build the scrolling text
  const ctaText = `🔔 ${channelName} को सब्सक्राइब करें  •  👍 लाइक करें  •  शेयर करें`;
  const tickerContent = headlines
    .map((h, i) => `📌 ${h}`)
    .join("   •   ") + `   •   ${ctaText}   •   `;

  // Repeat for seamless scrolling
  const fullText = tickerContent + tickerContent + tickerContent;

  // Scroll speed: approx 3 pixels per frame
  const scrollOffset = interpolate(
    frame,
    [0, durationInFrames],
    [0, -fullText.length * 8],
    { extrapolateRight: "extend" }
  );

  return (
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        height: 56,
        display: "flex",
        alignItems: "stretch",
        zIndex: 100,
        transform: `translateY(${translateY}px)`,
        overflow: "hidden",
      }}
    >
      {/* BREAKING NEWS box (left) */}
      <div
        style={{
          background: `linear-gradient(135deg, #EE0000 0%, ${DLS_COLORS.breakingRed} 100%)`,
          display: "flex",
          alignItems: "center",
          padding: "0 16px",
          gap: 8,
          flexShrink: 0,
          boxShadow: "4px 0 12px rgba(200,0,0,0.4)",
          zIndex: 2,
        }}
      >
        <div
          style={{
            color: DLS_COLORS.textWhite,
            fontWeight: 900,
            fontSize: 14,
            letterSpacing: "1.5px",
            lineHeight: 1.2,
            textAlign: "center",
          }}
        >
          <div>BREAKING</div>
          <div>NEWS</div>
        </div>
      </div>

      {/* Scrolling ticker area */}
      <div
        style={{
          flex: 1,
          background: `linear-gradient(90deg, ${DLS_COLORS.tickerBg} 0%, #0d1e35 100%)`,
          borderTop: "2px solid rgba(255, 230, 0, 0.4)",
          display: "flex",
          alignItems: "center",
          overflow: "hidden",
          position: "relative",
        }}
      >
        <div
          style={{
            whiteSpace: "nowrap",
            fontSize: 22,
            fontWeight: 700,
            color: DLS_COLORS.tickerTextWhite,
            transform: `translateX(${scrollOffset}px)`,
            willChange: "transform",
          }}
        >
          {fullText.split("•").map((segment, i) => (
            <React.Fragment key={i}>
              {i > 0 && (
                <span style={{ color: DLS_COLORS.tickerTextYellow, margin: "0 8px" }}>•</span>
              )}
              <span
                style={{
                  color: segment.includes("सब्सक्राइब") || segment.includes("लाइक") || segment.includes("शेयर")
                    ? DLS_COLORS.tickerTextYellow
                    : DLS_COLORS.tickerTextWhite,
                }}
              >
                {segment}
              </span>
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};
