/**
 * DLS News – Animated Studio Background
 * Dark purple/blue gradient with animated light streaks (exactly like DLS News reference video)
 */
import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { DLS_COLORS } from "../types";

export const DLSBackground: React.FC = () => {
  const frame = useCurrentFrame();

  // Slow pulsing glow
  const glowOpacity = interpolate(
    Math.sin(frame * 0.03),
    [-1, 1],
    [0.15, 0.35]
  );

  // Diagonal light streak position (loops)
  const streakX = interpolate(
    frame % 180,
    [0, 180],
    [-400, 2400]
  );

  // Second streak (offset)
  const streakX2 = interpolate(
    (frame + 90) % 240,
    [0, 240],
    [-400, 2400]
  );

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: `linear-gradient(135deg, ${DLS_COLORS.bgDark1} 0%, ${DLS_COLORS.bgDark2} 50%, ${DLS_COLORS.bgDark3} 100%)`,
        overflow: "hidden",
      }}
    >
      {/* Radial glow center pulse */}
      <div
        style={{
          position: "absolute",
          top: "30%",
          left: "50%",
          width: 900,
          height: 900,
          borderRadius: "50%",
          background: `radial-gradient(circle, rgba(100, 50, 200, ${glowOpacity}) 0%, transparent 70%)`,
          transform: "translate(-50%, -50%)",
          pointerEvents: "none",
        }}
      />

      {/* Diagonal light streak 1 */}
      <div
        style={{
          position: "absolute",
          top: -100,
          left: streakX,
          width: 3,
          height: 1400,
          background: "linear-gradient(180deg, transparent 0%, rgba(150, 100, 255, 0.4) 50%, transparent 100%)",
          transform: "rotate(25deg)",
          filter: "blur(2px)",
          pointerEvents: "none",
        }}
      />

      {/* Diagonal light streak 2 */}
      <div
        style={{
          position: "absolute",
          top: -100,
          left: streakX2,
          width: 2,
          height: 1400,
          background: "linear-gradient(180deg, transparent 0%, rgba(200, 150, 255, 0.3) 50%, transparent 100%)",
          transform: "rotate(20deg)",
          filter: "blur(3px)",
          pointerEvents: "none",
        }}
      />

      {/* Subtle horizontal glow bar (mid-screen) */}
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: 0,
          right: 0,
          height: 200,
          background: `linear-gradient(180deg, transparent 0%, rgba(80, 40, 180, ${glowOpacity * 0.5}) 50%, transparent 100%)`,
          transform: "translateY(-50%)",
          pointerEvents: "none",
        }}
      />

      {/* Bottom edge gradient (blending into ticker area) */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: 120,
          background: "linear-gradient(180deg, transparent 0%, rgba(10, 22, 40, 0.8) 100%)",
          pointerEvents: "none",
        }}
      />
    </div>
  );
};
