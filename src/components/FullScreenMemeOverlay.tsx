/**
 * Master TV News – Full Screen Meme Reaction Overlay
 * Specifications (User Refinements):
 * - ZERO borders, ZERO shadows, ZERO card frames (clean raw transparent meme)
 * - NO text / badge (No "[ 😂 वायरल मीम / REACTION ]" - completely clean)
 * - HUGE scale ("स्क्रीन में बहुत बड़ा होकर फ़्लैश हो")
 * - Punchy white flash pop-in on entrance
 * - Behind Top Header (Channel Name, zIndex: 90) and Bottom Ticker (zIndex: 100)
 * - Quick exit back into standard news layout
 */
import React from "react";
import {
  Img,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { assetPath } from "../utils/assetHelper";

interface FullScreenMemeOverlayProps {
  imageSrc: string;
  caption?: string;
  channelName?: string;
  durationInFrames: number;
}

export const FullScreenMemeOverlay: React.FC<FullScreenMemeOverlayProps> = ({
  imageSrc,
  channelName = "Uncut भारत",
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // ─── 1. PUNCHY POP-IN & SLAM ENTRANCE (Aggressive Comic Bounce) ───
  const popSpring = spring({
    frame,
    fps,
    config: { damping: 9, mass: 0.4, stiffness: 160 },
  });
  const popScale = interpolate(popSpring, [0, 1], [0.4, 1.0]);
  const popOpacity = interpolate(popSpring, [0, 0.25, 1], [0, 1, 1]);

  // ─── 2. INSTANT WHITE FLASH BURST (2-4 frames impact) ───
  const flashOpacity = interpolate(frame, [0, 1, 5], [0, 0.75, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ─── 3. EXIT POP-OUT (Last 6 frames) ───
  const exitStart = Math.max(10, durationInFrames - 6);
  const exitProgress = interpolate(
    frame,
    [exitStart, durationInFrames],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const exitScale = interpolate(exitProgress, [0, 1], [1.0, 0.25]);
  const exitOpacity = interpolate(exitProgress, [0, 1], [1, 0]);

  // Combined scale & opacity
  const totalScale = popScale * exitScale;
  const totalOpacity = popOpacity * exitOpacity;

  // ─── 4. SUBTLE COMIC PULSE (Very subtle energetic vibration) ───
  const pulse = 1 + 0.015 * Math.sin((frame / 8) * Math.PI * 2);

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        overflow: "hidden",
        zIndex: 45, // Strictly BEHIND Top Header (90) and Bottom Ticker (100)
        opacity: totalOpacity,
        pointerEvents: "none",
      }}
    >
      {/* ─── Studio Dark Backdrop (covers previous news card cleanly) ─── */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(circle at 50% 50%, rgba(25, 3, 3, 0.94) 0%, rgba(8, 1, 1, 0.98) 75%, #000000 100%)",
        }}
      />

      {/* ─── Repeating Channel Watermark Grid ─── */}
      <div
        style={{
          position: "absolute",
          inset: -120,
          opacity: 0.05,
          display: "flex",
          flexDirection: "column",
          gap: 48,
          transform: "rotate(-12deg)",
          pointerEvents: "none",
          userSelect: "none",
        }}
      >
        {Array.from({ length: 12 }).map((_, rIdx) => (
          <div
            key={rIdx}
            style={{
              display: "flex",
              gap: 55,
              whiteSpace: "nowrap",
              fontSize: 32,
              fontWeight: 900,
              fontFamily: "'Segoe UI', 'Noto Sans Devanagari', sans-serif",
              color: "#ffffff",
              letterSpacing: "4px",
            }}
          >
            {Array.from({ length: 8 }).map((_, cIdx) => (
              <span key={cIdx}>{channelName.toUpperCase()}</span>
            ))}
          </div>
        ))}
      </div>

      {/* ─── Flash Light Burst Overlay ─── */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.95) 0%, rgba(255, 220, 150, 0.6) 40%, transparent 80%)",
          opacity: flashOpacity,
          pointerEvents: "none",
          zIndex: 30,
        }}
      />

      {/* ─── HUGE RAW MEME IMAGE (NO BORDER, NO SHADOW, NO TEXT) ─── */}
      <div
        style={{
          position: "relative",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transform: `scale(${totalScale * pulse})`,
          transformOrigin: "center center",
          zIndex: 10,
          maxHeight: 820,
          maxWidth: 1350,
          width: "100%",
          height: "100%",
        }}
      >
        <Img
          src={assetPath(imageSrc)}
          style={{
            maxHeight: 820,
            maxWidth: 1350,
            objectFit: "contain",
            display: "block",
            border: "none",
            boxShadow: "none",
            outline: "none",
            filter: "none",
          }}
        />
      </div>
    </div>
  );
};
