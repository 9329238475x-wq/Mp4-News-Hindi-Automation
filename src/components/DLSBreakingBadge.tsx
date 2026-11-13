/**
 * DLS News – Iconic [ BREAKING | NEWS ] Broadcast Badge
 * With 3D "Ulat-Palat" (Flip & Snap Straight) Television Animation:
 * - Frames 0 to 30: Dramatic 3D tumble flip (rotateX: -360deg -> 0deg) snapping straight upright with spring physics
 * - Periodic Flip: Every 150 frames (~5s) does a crisp 360-degree 3D flip & locks straight
 * - High-Gloss Metallic sweep glint ray + Live pulsing red glow
 * - Left Tab: Red background with bold white 'BREAKING'
 * - Right Tab: White background with bold red 'NEWS'
 */
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

interface DLSBreakingBadgeProps {
  leftText?: string;
  rightText?: string;
  leftBg?: string;
  leftColor?: string;
  rightBg?: string;
  rightColor?: string;
}

export const DLSBreakingBadge: React.FC<DLSBreakingBadgeProps> = ({
  leftText = "BREAKING",
  rightText = "NEWS",
  leftBg = "linear-gradient(180deg, #ff1a1a 0%, #cc0000 60%, #990000 100%)",
  leftColor = "#ffffff",
  rightBg = "linear-gradient(180deg, #ffffff 0%, #f0f0f0 100%)",
  rightColor = "#cc0000",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // ─── 1. INITIAL 3D "ULAT-PALAT" ENTRANCE FLIP (Frames 0 to 32) ───
  // Badge tumbles in 3D (flips 360 degrees on X-axis) and snaps straight upright!
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
  // Every 5 seconds after entrance, badge does a fast 360-degree flip & locks straight
  const cyclePeriod = 150;
  const cycleFrame = frame % cyclePeriod;

  // Trigger periodic flip after initial entrance has settled (frame > 50)
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

  // ─── 3. SHIMMER LIGHT RAY SWEEP (Synced to landing straight) ───
  const shimmerCycle = frame % 60;
  const shimmerX = interpolate(shimmerCycle, [10, 40], [-140, 320], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const shimmerOpacity = interpolate(
    shimmerCycle,
    [10, 18, 32, 40],
    [0, 0.95, 0.95, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // ─── 4. PULSE / HEARTBEAT GLOW ───
  const pulse = Math.sin((frame / 15) * Math.PI * 2);
  const glow = 0.4 + 0.35 * (0.5 + 0.5 * pulse);

  return (
    <div
      style={{
        position: "relative",
        display: "inline-flex",
        alignItems: "stretch",
        borderRadius: 12,
        overflow: "hidden",
        boxShadow: `0 8px 28px rgba(229, 9, 20, ${glow}), 0 6px 16px rgba(0,0,0,0.8)`,
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
          width: 55,
          transform: `translateX(${shimmerX}px) skewX(-25deg)`,
          background:
            "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.35) 30%, rgba(255, 255, 255, 1) 50%, rgba(255, 255, 255, 0.35) 70%, transparent 100%)",
          opacity: shimmerOpacity,
          pointerEvents: "none",
          zIndex: 10,
        }}
      />

      {/* LEFT TAB: BREAKING / DYNAMIC LABEL */}
      <div
        style={{
          background: leftBg,
          color: leftColor,
          fontWeight: 900,
          fontSize: 30,
          padding: "10px 32px",
          letterSpacing: "2px",
          display: "flex",
          alignItems: "center",
          fontFamily: "'Noto Sans Devanagari', 'Segoe UI', 'Impact', sans-serif",
          textShadow: "0 2px 6px rgba(0,0,0,0.8)",
        }}
      >
        {leftText}
      </div>

      {/* RIGHT TAB: NEWS / DYNAMIC LABEL */}
      <div
        style={{
          background: rightBg,
          color: rightColor,
          fontWeight: 900,
          fontSize: 30,
          padding: "10px 32px",
          letterSpacing: "2px",
          display: "flex",
          alignItems: "center",
          fontFamily: "'Noto Sans Devanagari', 'Segoe UI', 'Impact', sans-serif",
          textShadow: "none",
        }}
      >
        {rightText}
      </div>
    </div>
  );
};
