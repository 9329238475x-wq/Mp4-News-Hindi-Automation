/**
 * Master Cyber Visual Frame (Left Side)
 * Exactly matches 'news-preview.png':
 * - Glowing Neon Cyan corner brackets: ┌ ┐ └ ┘
 * - Top-Left Badge: [⚡ सुपर एक्सक्लूसिव]
 * - Bottom Attribution: [📷 स्रोत: {publisher} | घटनास्थल]
 * - Smooth Ken Burns zoom and slow pan
 */
import React from "react";
import { Img, Video, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { assetPath } from "../utils/assetHelper";
import { TV_COLORS } from "../types";

interface CyberVisualFrameProps {
  visualSrc: string;
  attributionTag?: string;
}

export const CyberVisualFrame: React.FC<CyberVisualFrameProps> = ({
  visualSrc,
  attributionTag = "📷 विशेष कवरेज | घटनास्थल",
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const isVideo =
    visualSrc.toLowerCase().endsWith(".mp4") ||
    visualSrc.toLowerCase().endsWith(".webm");

  // Ken Burns: Slow, smooth zoom from 1.0 to 1.08
  const zoom = interpolate(frame, [0, durationInFrames], [1.0, 1.08], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Slow subtle pan (X axis: 0px -> -15px)
  const panX = interpolate(frame, [0, durationInFrames], [0, -14], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        borderRadius: 12,
        overflow: "hidden",
        border: `1.5px solid ${TV_COLORS.neonCyanBorder}`,
        boxShadow: `0 0 25px ${TV_COLORS.neonCyanGlow}, 0 8px 30px rgba(0,0,0,0.7), inset 0 0 15px rgba(0, 240, 255, 0.15)`,
        backgroundColor: "#030712",
      }}
    >
      {/* ─── Media Container with Ken Burns ─── */}
      <div
        style={{
          width: "100%",
          height: "100%",
          overflow: "hidden",
          transform: `scale(${zoom}) translateX(${panX}px)`,
          transformOrigin: "center center",
          willChange: "transform",
        }}
      >
        {isVideo ? (
          <Video
            src={assetPath(visualSrc)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
            muted
            loop
          />
        ) : (
          <Img
            src={assetPath(visualSrc)}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        )}
      </div>

      {/* ─── Vignette Overlay ─── */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.35) 0%, transparent 35%, transparent 65%, rgba(0,0,0,0.65) 100%)",
          pointerEvents: "none",
        }}
      />

      {/* ─── TOP-LEFT BADGE: [⚡ सुपर एक्सक्लूसिव] ─── */}
      <div
        style={{
          position: "absolute",
          top: 14,
          left: 14,
          background: TV_COLORS.exclusiveBadgeGradient,
          padding: "5px 14px",
          borderRadius: 6,
          display: "flex",
          alignItems: "center",
          gap: 6,
          boxShadow: "0 3px 12px rgba(255, 110, 0, 0.55)",
          zIndex: 10,
        }}
      >
        <span style={{ fontSize: 13 }}>⚡</span>
        <span
          style={{
            color: "#ffffff",
            fontSize: 13,
            fontWeight: 900,
            fontFamily: "'Noto Sans Devanagari', sans-serif",
            letterSpacing: "0.4px",
          }}
        >
          सुपर एक्सक्लूसिव
        </span>
      </div>

      {/* ─── BOTTOM-LEFT ATTRIBUTION BADGE ─── */}
      <div
        style={{
          position: "absolute",
          bottom: 14,
          left: 14,
          background: "rgba(0, 0, 0, 0.78)",
          backdropFilter: "blur(6px)",
          border: "1px solid rgba(255, 255, 255, 0.2)",
          padding: "4px 12px",
          borderRadius: 4,
          color: "#e2e8f0",
          fontSize: 12,
          fontWeight: 700,
          fontFamily: "'Noto Sans Devanagari', sans-serif",
          zIndex: 10,
          boxShadow: "0 2px 8px rgba(0,0,0,0.6)",
        }}
      >
        {attributionTag}
      </div>

      {/* ─── NEON CYAN CORNER BRACKETS: ┌ ┐ └ ┘ ─── */}
      {/* Top-Left Bracket */}
      <div
        style={{
          position: "absolute",
          top: 8,
          left: 8,
          width: 24,
          height: 24,
          borderTop: `3px solid ${TV_COLORS.neonCyan}`,
          borderLeft: `3px solid ${TV_COLORS.neonCyan}`,
          boxShadow: `0 0 8px ${TV_COLORS.neonCyanGlow}`,
          pointerEvents: "none",
        }}
      />
      {/* Top-Right Bracket */}
      <div
        style={{
          position: "absolute",
          top: 8,
          right: 8,
          width: 24,
          height: 24,
          borderTop: `3px solid ${TV_COLORS.neonCyan}`,
          borderRight: `3px solid ${TV_COLORS.neonCyan}`,
          boxShadow: `0 0 8px ${TV_COLORS.neonCyanGlow}`,
          pointerEvents: "none",
        }}
      />
      {/* Bottom-Left Bracket */}
      <div
        style={{
          position: "absolute",
          bottom: 8,
          left: 8,
          width: 24,
          height: 24,
          borderBottom: `3px solid ${TV_COLORS.neonCyan}`,
          borderLeft: `3px solid ${TV_COLORS.neonCyan}`,
          boxShadow: `0 0 8px ${TV_COLORS.neonCyanGlow}`,
          pointerEvents: "none",
        }}
      />
      {/* Bottom-Right Bracket */}
      <div
        style={{
          position: "absolute",
          bottom: 8,
          right: 8,
          width: 24,
          height: 24,
          borderBottom: `3px solid ${TV_COLORS.neonCyan}`,
          borderRight: `3px solid ${TV_COLORS.neonCyan}`,
          boxShadow: `0 0 8px ${TV_COLORS.neonCyanGlow}`,
          pointerEvents: "none",
        }}
      />
    </div>
  );
};
