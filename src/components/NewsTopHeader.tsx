/**
 * Master TV Broadcast Top Header
 * Enlarged & high-impact TV broadcast branding:
 * - 100% PURE VECTOR / TEXT: Zero image dependency for razor-sharp 1080p broadcast quality
 * - Enlarged & authoritative broadcast pill badge:
 *     * Left Tab: [ MP4 NEWS ] in pure white 900 ultra-bold on glossy red gradient with diagonal gloss gleam
 *     * Right Tab: [ हिन्दी ] in crimson red 900 ultra-bold on enamel white gradient
 * - 3D "Ulat-Palat" Television Animation (identical to Breaking News Badge):
 *     * Frame 0-32: 3D tumble flip (rotateX: -360 -> 0) snapping straight upright with spring physics
 *     * Every 150 frames (~5s): Periodic 360-degree 3D flip & snap straight
 *     * Metallic light sweep glint ray
 * - Zero big glowing haze (clean, realistic broadcast drop-shadow)
 * - Tagline: [देश का नंबर 1 बुलेटिन / सच्चाई सबसे पहले] enlarged to 30px bold font
 * - 100% Clean: ZERO EMOJIS
 */
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

interface NewsTopHeaderProps {
  channelName?: string;
  tagline?: string;
  location?: string;
  globalFrameOffset?: number;
}

export const NewsTopHeader: React.FC<NewsTopHeaderProps> = ({
  channelName = "Uncut भारत",
  tagline = "100% निडर • निष्पक्ष • सच",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // ─── 1. BREAKING-NEWS STYLE 3D "ULAT-PALAT" ENTRANCE FLIP (Frames 0 to 32) ───
  const entranceSpring = spring({
    frame,
    fps,
    config: { damping: 12, mass: 0.7, stiffness: 130 },
  });

  const entranceRotateX = interpolate(entranceSpring, [0, 1], [-360, 0]);
  const entranceScale = interpolate(entranceSpring, [0, 1], [0.65, 1]);
  const entranceTranslateY = interpolate(entranceSpring, [0, 1], [-30, 0]);
  const entranceOpacity = interpolate(entranceSpring, [0, 1], [0, 1]);

  // ─── 2. PERIODIC 3D "ULAT-PALAT" FLIP CYCLE (Every 150 frames = 5 seconds) ───
  const cyclePeriod = 150;
  const cycleFrame = frame % cyclePeriod;

  const isPeriodicFlip = frame > 50 && cycleFrame < 26;
  const periodicSpring = spring({
    frame: isPeriodicFlip ? cycleFrame : 0,
    fps,
    config: { damping: 14, mass: 0.65, stiffness: 140 },
  });
  const periodicRotateX = isPeriodicFlip
    ? interpolate(periodicSpring, [0, 1], [0, 360])
    : 0;
  const periodicScale = isPeriodicFlip
    ? interpolate(periodicSpring, [0, 0.5, 1], [1, 1.08, 1])
    : 1;

  const totalRotateX = frame <= 40 ? entranceRotateX : periodicRotateX;
  const totalScale = frame <= 40 ? entranceScale : periodicScale;
  const totalTranslateY = frame <= 40 ? entranceTranslateY : 0;
  const totalOpacity = frame <= 40 ? entranceOpacity : 1;

  // ─── 3. SHIMMER METALLIC LIGHT RAY SWEEP (Synced across badge) ───
  const shimmerCycle = frame % 60;
  const shimmerX = interpolate(shimmerCycle, [10, 40], [-160, 480], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const shimmerOpacity = interpolate(
    shimmerCycle,
    [10, 18, 32, 40],
    [0, 0.95, 0.95, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // ─── 4. Staggered Entrance for Tagline (starts at frame 8) ───
  const taglineSpring = spring({
    frame: Math.max(0, frame - 8),
    fps,
    config: { damping: 15, mass: 0.8 },
  });
  const taglineTranslateX = interpolate(taglineSpring, [0, 1], [-25, 0]);
  const taglineOpacity = interpolate(taglineSpring, [0, 1], [0, 1]);

  // ─── 5. Fixed Static Tagline (TV News Standard: 100% stable across entire video) ───
  const staticTagline = tagline || "हर खबर पर सबसे सटीक नज़र";

  return (
    <div
      style={{
        position: "absolute",
        top: 24,
        left: 44,
        right: 44,
        height: 80,
        display: "flex",
        alignItems: "center",
        justifyContent: "flex-start",
        zIndex: 90,
        perspective: 1000,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 26,
        }}
      >
        {/* ─── OFFICIAL [ MP4 NEWS | हिन्दी ] PURE-TEXT BROADCAST CAPSULE BADGE ─── */}
        <div
          style={{
            position: "relative",
            display: "inline-flex",
            alignItems: "stretch",
            borderRadius: 22,
            overflow: "hidden",
            boxShadow:
              "0 10px 28px rgba(0, 0, 0, 0.75), 0 3px 8px rgba(0, 0, 0, 0.5)",
            border: "3.5px solid #ffffff",
            transformOrigin: "center center",
            transformStyle: "preserve-3d",
            transform: `translateY(${totalTranslateY}px) scale(${totalScale}) rotateX(${totalRotateX}deg)`,
            opacity: totalOpacity,
            willChange: "transform, opacity",
          }}
        >
          {/* Metallic Light Glint Ray Sweep */}
          <div
            style={{
              position: "absolute",
              top: -20,
              bottom: -20,
              left: 0,
              width: 60,
              transform: `translateX(${shimmerX}px) skewX(-25deg)`,
              background:
                "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.35) 30%, rgba(255, 255, 255, 1) 50%, rgba(255, 255, 255, 0.35) 70%, transparent 100%)",
              opacity: shimmerOpacity,
              pointerEvents: "none",
              zIndex: 15,
            }}
          />

          {/* LEFT TAB: UNCUT (Red Glossy Background, Pure White Ultra-Bold Text) */}
          <div
            style={{
              position: "relative",
              background:
                "linear-gradient(180deg, #ff1a1a 0%, #d40000 55%, #990000 100%)",
              color: "#ffffff",
              fontWeight: 900,
              fontSize: 34,
              padding: "11px 28px",
              letterSpacing: "3px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: "'Segoe UI', 'Impact', 'Arial Black', sans-serif",
              textShadow: "0 2px 6px rgba(0,0,0,0.85)",
              overflow: "hidden",
            }}
          >
            {/* Top Gloss Sheen Curve */}
            <div
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                height: "48%",
                background:
                  "linear-gradient(180deg, rgba(255,255,255,0.45) 0%, rgba(255,255,255,0.06) 100%)",
                pointerEvents: "none",
              }}
            />
            {/* Diagonal Bevel Light Sheen at Divider */}
            <div
              style={{
                position: "absolute",
                top: -10,
                bottom: -10,
                right: -8,
                width: 32,
                transform: "skewX(-24deg)",
                background:
                  "linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.2) 40%, rgba(255,255,255,0.8) 85%, transparent 100%)",
                pointerEvents: "none",
              }}
            />
            {/* Mini 3D UB Brand Tag */}
            <span
              style={{
                background: "linear-gradient(135deg, #ffe600 0%, #ff9900 100%)",
                color: "#990000",
                fontSize: 20,
                fontWeight: 900,
                padding: "3px 9px",
                borderRadius: 7,
                letterSpacing: "0.5px",
                boxShadow: "0 2px 6px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.8)",
                fontFamily: "'Segoe UI', 'Impact', sans-serif",
                marginRight: 6,
                textShadow: "none",
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              UB
            </span>
            UNCUT
          </div>

          {/* RIGHT TAB: भारत (Enamel White Background, Deep Red Text) */}
          <div
            style={{
              position: "relative",
              background:
                "linear-gradient(180deg, #ffffff 0%, #f2f2f2 100%)",
              color: "#cc0000",
              fontWeight: 900,
              fontSize: 36,
              padding: "11px 30px",
              letterSpacing: "1px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: "'Noto Sans Devanagari', 'Segoe UI', sans-serif",
              textShadow: "0 1px 2px rgba(0,0,0,0.12)",
              overflow: "hidden",
            }}
          >
            {/* Subtle Pearl Gloss Sheen */}
            <div
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                height: "48%",
                background:
                  "linear-gradient(180deg, rgba(255,255,255,0.85) 0%, rgba(255,255,255,0.08) 100%)",
                pointerEvents: "none",
              }}
            />
            भारत
          </div>
        </div>

        {/* Static Stable Tagline (30px Bold, Zero Emojis) */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            transform: `translateX(${taglineTranslateX}px)`,
            opacity: taglineOpacity,
          }}
        >
          <span
            style={{
              color: "#ffffff",
              fontSize: 30,
              fontWeight: 800,
              fontFamily: "'Noto Sans Devanagari', sans-serif",
              letterSpacing: "0.5px",
              textShadow:
                "0 2px 5px #000000, 0 3px 14px rgba(0,0,0,0.95), 0 0 16px rgba(0,0,0,0.85)",
            }}
          >
            {staticTagline}
          </span>
        </div>
      </div>
    </div>
  );
};
