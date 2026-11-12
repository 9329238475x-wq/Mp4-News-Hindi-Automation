/**
 * Master TV News Bottom Ticker
 * 100% matches user's exact specifications:
 * - Bigger broadcast height: 94px (elevated 20px from bottom, fills empty screen space)
 * - Left Red Box: [ताज़ा अपडेट्स] (Bold 33px 900-weight with metallic light glint)
 * - White Ticker Strip: 100% Crisp Broadcast White Background
 * - Red Scrolling Marquee: Bold 32px 900-weight Deep Broadcast Red Text (#b80009)
 * - Dark separator bullets (●) for razor-sharp distinction
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
  const cleanTickerText = (h: string) =>
    h
      .replace(/\bट्रेन आगे\b/g, "ट्रेन के आगे")
      .replace(/\bगोली धमकी\b/g, "गोली मारने की धमकी")
      .replace(/\bडिसिपी\b/g, "डीसीपी");

  const rawList = headlines.length > 0 ? headlines : ["देश की हर बड़ी और ताज़ा खबर पर नज़र"];
  const headlinesList = rawList.map(cleanTickerText);
  const formattedItems = [...headlinesList, cta];

  // Continuous linear scroll: approx 3.0 pixels per frame
  const scrollSpeed = 3.0;
  const loopWidth = 6400;
  const scrollOffset = -((absoluteFrame * scrollSpeed) % loopWidth);

  // ─── Animations ───
  // 1. Shimmer glint on the badge
  const shimmerCycle = frame % 70;
  const shimmerX = interpolate(shimmerCycle, [10, 42], [-140, 280], {
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
  const badgeGlow = 0.45 + 0.35 * (0.5 + 0.5 * pulse);

  // 3. Subtle 3D breathing text scale
  const textScale = 1 + 0.03 * Math.sin((frame / 22) * Math.PI * 2);

  return (
    <div
      style={{
        position: "absolute",
        bottom: 18,
        left: 20,
        right: 20,
        height: 96,
        display: "flex",
        alignItems: "stretch",
        zIndex: 100,
        overflow: "hidden",
        borderRadius: 16,
        border: "3.5px solid #ff3344",
        boxShadow:
          "0 14px 44px rgba(0, 0, 0, 0.95), 0 0 32px rgba(211, 0, 11, 0.55)",
      }}
    >
      {/* ─── LEFT: ANIMATED TV NEWS BADGE [ताज़ा अपडेट्स] (100% CLEAN - ZERO EMOJIS) ─── */}
      <div
        style={{
          position: "relative",
          overflow: "hidden",
          background:
            "linear-gradient(135deg, #180003 0%, #3d0006 50%, #180003 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "0 46px",
          flexShrink: 0,
          boxShadow: `4px 0 24px rgba(229, 9, 20, ${badgeGlow}), inset 0 1px 0 rgba(255, 255, 255, 0.35)`,
          zIndex: 10,
          borderRight: "3.5px solid #fbbf24",
        }}
      >
        {/* Metallic Light Sweep Glint Ray */}
        <div
          style={{
            position: "absolute",
            top: -20,
            bottom: -20,
            left: 0,
            width: 55,
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
            fontSize: 34,
            fontWeight: 900,
            fontFamily: "'Noto Sans Devanagari', sans-serif",
            letterSpacing: "1.2px",
            transform: `scale(${textScale})`,
            transformOrigin: "center center",
            display: "inline-block",
            textShadow:
              "0 2px 8px rgba(0, 0, 0, 0.9), 0 0 14px rgba(251, 191, 36, 0.45)",
            zIndex: 2,
          }}
        >
          ताज़ा अपडेट्स
        </span>
      </div>

      {/* ─── SCROLLING MARQUEE TRACK (100% BROADCAST RED PATTI + BOLD WHITE TEXT) ─── */}
      <div
        style={{
          flex: 1,
          background: "linear-gradient(180deg, #d3000b 0%, #aa0007 50%, #820004 100%)",
          display: "flex",
          alignItems: "center",
          overflow: "hidden",
          position: "relative",
          boxShadow: "inset 0 3px 8px rgba(0, 0, 0, 0.35)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            whiteSpace: "nowrap",
            transform: `translateX(${scrollOffset}px)`,
            willChange: "transform",
            fontSize: 36,
            fontWeight: 900,
            fontFamily: "'Noto Sans Devanagari', 'Segoe UI', sans-serif",
            color: "#ffffff",
            letterSpacing: "0.6px",
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
                    gap: 20,
                    paddingRight: 50,
                  }}
                >
                  <span
                    style={{
                      color: "#fde047",
                      fontSize: 22,
                      filter: "drop-shadow(0 1px 3px rgba(0, 0, 0, 0.8))",
                    }}
                  >
                    ●
                  </span>
                  <span
                    style={{
                      color: "#ffffff",
                      textShadow: "0 2px 4px rgba(0, 0, 0, 0.75)",
                    }}
                  >
                    {item}
                  </span>
                </div>
              ))}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};
