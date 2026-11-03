/**
 * Master TV News Bottom Ticker
 * Matches user's exact specifications:
 * - Elevated above bottom: bottom: 26px
 * - Height: 76px
 * - Left Red Box: [ताज़ा अपडेट्स] (ZERO EMOJIS as explicitly requested)
 * - Scrolling Marquee: Crisp broadcast dots ● separating news headlines with 26px bold text
 */
import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { TV_COLORS } from "../types";

interface NewsTickerProps {
  headlines: string[];
  channelName?: string;
  globalFrameOffset?: number;
}

export const NewsTicker: React.FC<NewsTickerProps> = ({
  headlines = [],
  channelName = "IN News 24",
  globalFrameOffset = 0,
}) => {
  const frame = useCurrentFrame();
  const absoluteFrame = frame + globalFrameOffset;

  // Build the ticker text with separators
  const cta = `${channelName} को सब्सक्राइब करें और हर खबर पर रखें सीधी नज़र`;
  const headlinesList =
    headlines.length > 0 ? headlines : ["देश की हर बड़ी और ताज़ा खबर पर नज़र"];
  const formattedItems = [...headlinesList, cta];

  // Continuous linear scroll: approx 2.8 pixels per frame
  const scrollSpeed = 2.8;
  const loopWidth = 5200;
  const scrollOffset = -((absoluteFrame * scrollSpeed) % loopWidth);

  // ─── Animations ───
  // 1. Shimmer glint on the badge
  const shimmerCycle = frame % 70;
  const shimmerX = interpolate(shimmerCycle, [10, 42], [-140, 260], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const shimmerOpacity = interpolate(
    shimmerCycle,
    [10, 18, 34, 42],
    [0, 0.95, 0.95, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // 2. Neon pulse
  const pulse = Math.sin((frame / 16) * Math.PI * 2);
  const badgeGlow = 0.4 + 0.35 * (0.5 + 0.5 * pulse);

  // 3. Subtle 3D breathing text scale
  const textScale = 1 + 0.03 * Math.sin((frame / 22) * Math.PI * 2);

  return (
    <div
      style={{
        position: "absolute",
        bottom: 26,
        left: 28,
        right: 28,
        height: 76,
        display: "flex",
        alignItems: "stretch",
        zIndex: 100,
        overflow: "hidden",
        borderRadius: 14,
        border: "2.5px solid rgba(255, 255, 255, 0.3)",
        boxShadow:
          "0 10px 36px rgba(0, 0, 0, 0.88), 0 0 24px rgba(229, 9, 20, 0.35)",
      }}
    >
      {/* ─── LEFT: ANIMATED TV NEWS BADGE [ताज़ा अपडेट्स] (100% CLEAN - ZERO EMOJIS) ─── */}
      <div
        style={{
          position: "relative",
          overflow: "hidden",
          background:
            "linear-gradient(135deg, #e50914 0%, #b80009 50%, #850005 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 38px",
          flexShrink: 0,
          boxShadow: `4px 0 24px rgba(229, 9, 20, ${badgeGlow}), inset 0 1px 0 rgba(255, 255, 255, 0.5)`,
          zIndex: 10,
          borderRight: "2.5px solid rgba(255, 255, 255, 0.4)",
        }}
      >
        {/* Metallic Light Sweep Glint Ray */}
        <div
          style={{
            position: "absolute",
            top: -20,
            bottom: -20,
            left: 0,
            width: 50,
            transform: `translateX(${shimmerX}px) skewX(-25deg)`,
            background:
              "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.3) 25%, rgba(255, 255, 255, 0.95) 50%, rgba(255, 255, 255, 0.3) 75%, transparent 100%)",
            opacity: shimmerOpacity,
            pointerEvents: "none",
            zIndex: 15,
          }}
        />

        {/* Animated Text: 'ताज़ा अपडेट्स' with Broadcast Shadow (NO EMOJI) */}
        <span
          style={{
            color: "#ffffff",
            fontSize: 27,
            fontWeight: 900,
            fontFamily: "'Noto Sans Devanagari', sans-serif",
            letterSpacing: "1px",
            whiteSpace: "nowrap",
            transform: `scale(${textScale})`,
            transformOrigin: "center center",
            display: "inline-block",
            textShadow:
              "0 2px 8px rgba(0, 0, 0, 0.9), 0 0 14px rgba(255, 255, 255, 0.4)",
            zIndex: 2,
          }}
        >
          ताज़ा अपडेट्स
        </span>
      </div>

      {/* ─── SCROLLING MARQUEE TRACK ─── */}
      <div
        style={{
          flex: 1,
          background: TV_COLORS.tickerTrackBg,
          display: "flex",
          alignItems: "center",
          overflow: "hidden",
          position: "relative",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            whiteSpace: "nowrap",
            transform: `translateX(${scrollOffset}px)`,
            willChange: "transform",
            fontSize: 26,
            fontWeight: 800,
            fontFamily: "'Noto Sans Devanagari', 'Segoe UI', sans-serif",
            color: TV_COLORS.tickerTextWhite,
          }}
        >
          {[0, 1, 2, 3].map((cycle) => (
            <React.Fragment key={cycle}>
              {formattedItems.map((item, i) => (
                <div
                  key={`${cycle}-${i}`}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 16,
                    paddingRight: 36,
                  }}
                >
                  <span
                    style={{
                      color: TV_COLORS.tickerStarYellow,
                      fontSize: 16,
                      filter: "drop-shadow(0 0 6px rgba(255, 215, 0, 0.85))",
                    }}
                  >
                    ●
                  </span>
                  <span>{item}</span>
                </div>
              ))}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};
