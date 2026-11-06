/**
 * DLS News – Broadcast Photo/Media Frame (Left Side)
 * Matches reference Image 6 (PM Modi) & user's requested layout:
 * - Bold Red Broadcast Border (3.5px solid #e50914) with rounded corners
 * - Animated entrance from left (slides in when text moves to right)
 * - Smooth Ken Burns zoom on authentic news image
 * - Bottom attribution pill tag
 */
import React from "react";
import {
  Img,
  Video,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { assetPath } from "../utils/assetHelper";

interface DLSVisualFrameProps {
  visualSrc: string;
  attributionTag?: string;
  revealStartFrame?: number;
}

export const DLSVisualFrame: React.FC<DLSVisualFrameProps> = ({
  visualSrc,
  attributionTag = "विशेष कवरेज | घटनास्थल",
  revealStartFrame = 42,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const isVideo =
    visualSrc.toLowerCase().endsWith(".mp4") ||
    visualSrc.toLowerCase().endsWith(".webm");

  // Entrance spring: slides in from left after initial headline hook (revealStartFrame)
  const enterSpring = spring({
    frame: Math.max(0, frame - revealStartFrame),
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 90 },
  });

  // Offscreen by 1000px so it's completely hidden before frame 42
  const translateX = interpolate(enterSpring, [0, 1], [-1000, 0]);
  const opacity = interpolate(enterSpring, [0, 1], [0, 1]);

  // Smooth subtle Ken Burns zoom
  const zoom = interpolate(frame, [0, durationInFrames], [1.0, 1.07], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        borderRadius: 18,
        overflow: "hidden",
        border: "3.5px solid #e50914",
        boxShadow:
          "0 14px 40px rgba(0, 0, 0, 0.8), 0 0 24px rgba(229, 9, 20, 0.45)",
        backgroundColor: "#030712",
        transform: `translateX(${translateX}px)`,
        opacity,
      }}
    >
      {/* ─── Media Container with Ken Burns ─── */}
      <div
        style={{
          width: "100%",
          height: "100%",
          overflow: "hidden",
          transform: `scale(${zoom})`,
          transformOrigin: "center center",
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

      {/* ─── Bottom Subtle Gradient Vignette ─── */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(180deg, transparent 65%, rgba(0,0,0,0.8) 100%)",
          pointerEvents: "none",
        }}
      />

          </div>
  );
};
