/**
 * Subscribe Video Intro Component
 * Plays 'assets/Subscribe-video.mp4' (3.1s = 93 frames) exclusively at the very start
 * of the bulletin / first news story, branded with the official channel watermark:
 * - Top-Left: Official [ MP4 | NEWS हिन्दी ] Broadcast Capsule Pill
 * - Top-Right: Broadcast Watermark Badge (Mp4 News हिन्दी)
 * - Seamless broadcast transition to newsroom at end of intro
 */
import React from "react";
import {
  OffthreadVideo,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { assetPath } from "../utils/assetHelper";

interface SubscribeIntroProps {
  channelName?: string;
  channelTagline?: string;
}

export const SubscribeIntro: React.FC<SubscribeIntroProps> = ({
  channelName = "Uncut भारत",
  channelTagline = "100% निडर • निष्पक्ष • सच",
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Subtle fade in (first 8 frames) & smooth cross-dissolve to newsroom (last 10 frames)
  const introFade = interpolate(
    frame,
    [0, 8, durationInFrames - 10, durationInFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Periodic metallic glint on watermark logo
  const shimmerCycle = frame % 60;
  const shimmerTranslateX = interpolate(
    shimmerCycle,
    [10, 45],
    [-150, 350],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const shimmerOpacity = interpolate(
    shimmerCycle,
    [10, 20, 35, 45],
    [0, 0.95, 0.95, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        width: 1920,
        height: 1080,
        backgroundColor: "#000000",
        overflow: "hidden",
        zIndex: 100,
      }}
    >
      {/* ─── 1. FULLSCREEN 1080p SUBSCRIBE VIDEO (with audio) ─── */}
      <OffthreadVideo
        src={assetPath("assets/Subscribe-video.mp4")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
        }}
      />

      {/* ─── 2. TOP-LEFT: OFFICIAL [ MP4 | NEWS हिन्दी ] BROADCAST WATERMARK ─── */}
      <div
        style={{
          position: "absolute",
          top: 32,
          left: 44,
          display: "flex",
          alignItems: "center",
          gap: 16,
          opacity: introFade,
          zIndex: 110,
        }}
      >
        <div
          style={{
            position: "relative",
            display: "inline-flex",
            alignItems: "stretch",
            borderRadius: 12,
            overflow: "hidden",
            border: "3px solid #ffffff",
            boxShadow:
              "0 6px 26px rgba(211, 0, 0, 0.6), 0 4px 14px rgba(0,0,0,0.85), inset 0 2px 0 rgba(255, 255, 255, 0.7)",
          }}
        >
          {/* Metallic Light Glint Ray */}
          <div
            style={{
              position: "absolute",
              top: -30,
              bottom: -30,
              left: 0,
              width: 60,
              transform: `translateX(${shimmerTranslateX}%) skewX(-25deg)`,
              background:
                "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.2) 20%, rgba(255, 255, 255, 0.95) 50%, rgba(255, 255, 255, 0.2) 80%, transparent 100%)",
              opacity: shimmerOpacity,
              pointerEvents: "none",
              zIndex: 10,
            }}
          />

          {/* Left Red Tab: UNCUT */}
          <div
            style={{
              background:
                "linear-gradient(180deg, #ff1a1a 0%, #d40000 55%, #990000 100%)",
              color: "#ffffff",
              fontWeight: 900,
              fontSize: 27,
              padding: "9px 20px",
              letterSpacing: "2px",
              display: "flex",
              alignItems: "center",
              fontFamily: "'Segoe UI', 'Impact', sans-serif",
              textShadow: "0 2px 5px rgba(0,0,0,0.8)",
              position: "relative",
              zIndex: 2,
            }}
          >
            <span
              style={{
                background: "linear-gradient(135deg, #ffe600 0%, #ff9900 100%)",
                color: "#990000",
                fontSize: 16,
                fontWeight: 900,
                padding: "2px 7px",
                borderRadius: 5,
                marginRight: 6,
                textShadow: "none",
              }}
            >
              UB
            </span>
            UNCUT
          </div>

          {/* Vertical Divider */}
          <div style={{ width: 1.5, background: "rgba(0,0,0,0.2)", zIndex: 3 }} />

          {/* Right White Tab: भारत */}
          <div
            style={{
              background: "linear-gradient(180deg, #ffffff 0%, #f0f0f0 100%)",
              color: "#cc0000",
              fontWeight: 900,
              fontSize: 27,
              padding: "9px 20px",
              letterSpacing: "1px",
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontFamily: "'Noto Sans Devanagari', 'Segoe UI', sans-serif",
              textShadow: "none",
              position: "relative",
              zIndex: 2,
            }}
          >
            भारत
          </div>
        </div>

        {/* Tagline Watermark */}
        <span
          style={{
            color: "#ffffff",
            fontSize: 22,
            fontWeight: 800,
            fontFamily: "'Noto Sans Devanagari', sans-serif",
            textShadow: "0 2px 10px rgba(0,0,0,0.9)",
            letterSpacing: 0.5,
          }}
        >
          {channelTagline}
        </span>
      </div>

      {/* ─── 3. TOP-RIGHT: ELEGANT BROADCAST WATERMARK PILL ─── */}
      <div
        style={{
          position: "absolute",
          top: 32,
          right: 44,
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "8px 20px",
          background: "rgba(10, 15, 28, 0.75)",
          backdropFilter: "blur(12px)",
          borderRadius: 30,
          border: "1.5px solid rgba(255, 255, 255, 0.25)",
          boxShadow: "0 8px 24px rgba(0,0,0,0.6)",
          opacity: introFade,
          zIndex: 110,
        }}
      >
        <div
          style={{
            width: 10,
            height: 10,
            borderRadius: "50%",
            backgroundColor: "#e50914",
            boxShadow: "0 0 10px #ff1a1a",
          }}
        />
        <span
          style={{
            color: "#ffffff",
            fontSize: 18,
            fontWeight: 800,
            fontFamily: "'Noto Sans Devanagari', 'Segoe UI', sans-serif",
            letterSpacing: "0.5px",
          }}
        >
          {channelName}
        </span>
      </div>

      {/* ─── 4. BOTTOM WATERMARK HINT ─── */}
      <div
        style={{
          position: "absolute",
          bottom: 28,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          opacity: introFade * 0.9,
          zIndex: 110,
        }}
      >
        <div
          style={{
            padding: "6px 24px",
            background: "rgba(0, 0, 0, 0.6)",
            borderRadius: 20,
            border: "1px solid rgba(255, 255, 255, 0.15)",
            color: "#e2e8f0",
            fontSize: 16,
            fontWeight: 700,
            fontFamily: "'Noto Sans Devanagari', sans-serif",
            letterSpacing: 0.5,
          }}
        >
          🔔 देश और दुनिया की ताज़ा खबरों के लिए चैनल को सब्सक्राइब करें
        </div>
      </div>
    </div>
  );
};

