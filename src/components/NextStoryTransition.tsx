/**
 * Master TV News – "अगली बड़ी ख़बर" Stinger Transition Bumper
 * Broadcast Stinger Specifications:
 * - Placed behind Top Header (Channel Name) and Bottom Ticker (z-index: 40)
 * - Slide-in choreography: "अगली" slides from LEFT, "बड़ी ख़बर" slides from RIGHT
 * - Forward 3D Pop-up bounce into center view
 * - Exit: Zoom-out backwards into 3D depth and fade out ("पीछे जाकर गायब")
 * - Number badge completely removed (Only "अगली बड़ी ख़बर")
 * - Extra large font size, generous padding and gap so Devanagari matras never clip
 */
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

interface NextStoryTransitionProps {
  nextStoryNumber?: number;
  channelName?: string;
}

export const NextStoryTransition: React.FC<NextStoryTransitionProps> = ({
  channelName = "Uncut भारत",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // ─── 1. POP-UP ENTRANCE SPRING (Forward 3D Zoom & Punchy Bounce) ───
  const popSpring = spring({
    frame,
    fps,
    config: { damping: 11, mass: 0.55, stiffness: 130 },
  });
  const popScale = interpolate(popSpring, [0, 1], [0.55, 1.0]);
  const popTranslateY = interpolate(popSpring, [0, 1], [40, 0]);

  // ─── 2. "अगली" SLIDE FROM LEFT ───
  const leftSpring = spring({
    frame,
    fps,
    config: { damping: 12, mass: 0.6, stiffness: 135 },
  });
  const agliTranslateX = interpolate(leftSpring, [0, 1], [-800, 0]);
  const agliOpacity = interpolate(leftSpring, [0, 0.3, 1], [0, 1, 1]);

  // ─── 3. "बड़ी ख़बर" SLIDE FROM RIGHT ───
  const rightSpring = spring({
    frame,
    fps,
    config: { damping: 12, mass: 0.6, stiffness: 135 },
  });
  const badiTranslateX = interpolate(rightSpring, [0, 1], [800, 0]);
  const badiOpacity = interpolate(rightSpring, [0, 0.3, 1], [0, 1, 1]);

  // ─── 4. EXIT: "पीछे जाकर गायब हो जाना" (Zoom-Out into Depth & Fade Out) ───
  // Active in the final 9 frames of the transition (frames 21 to 30)
  const exitProgress = interpolate(
    frame,
    [21, 29],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  // Zoom backwards into 3D space: 1.0 -> 0.22 (deep perspective zoom out)
  const exitScale = interpolate(exitProgress, [0, 1], [1.0, 0.22]);
  const exitOpacity = interpolate(exitProgress, [0, 1], [1, 0]);

  // Solid studio background throughout transition
  const bgTotalOpacity = 1;

  // ─── 5. SHIMMER & FLARE LIGHT RAY (Across both words during peak impact) ───
  const shimmerX = interpolate(frame, [8, 21], [-220, 320], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const shimmerOpacity = interpolate(frame, [8, 11, 17, 21], [0, 0.95, 0.95, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ─── 6. Subtle Ambient Zoom for Studio Background ───
  const bgScale = 1 + frame * 0.004;

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
        zIndex: 40, // Behind Top Header (zIndex 90) and Bottom Ticker (zIndex 100)
        perspective: 1200,
        pointerEvents: "none",
      }}
    >
      {/* ─── Background: Deep Crimson Radial Studio Gradient ─── */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse at 50% 50%, #ba0606 0%, #730000 45%, #380000 80%, #150000 100%)",
          opacity: bgTotalOpacity,
          transform: `scale(${bgScale})`,
        }}
      />

      {/* ─── Watermark Pattern (Diagonal repeating channel name) ─── */}
      <div
        style={{
          position: "absolute",
          inset: -120,
          opacity: 0.08 * bgTotalOpacity,
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
              fontSize: 34,
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

      {/* ─── Radial Center Glow Flare ─── */}
      <div
        style={{
          position: "absolute",
          width: 900,
          height: 520,
          borderRadius: "50%",
          background:
            "radial-gradient(ellipse at center, rgba(255, 140, 0, 0.48) 0%, rgba(220, 20, 20, 0.28) 50%, transparent 80%)",
          filter: "blur(48px)",
          opacity: bgTotalOpacity,
          pointerEvents: "none",
        }}
      />

      {/* ─── Center 3D Content Wrapper (Pops up, then zooms back into depth) ─── */}
      <div
        style={{
          position: "relative",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 10,
          transform: `translateY(${popTranslateY}px) scale(${popScale * exitScale})`,
          opacity: exitOpacity,
          transformOrigin: "center center",
          overflow: "visible",
        }}
      >
        {/* Shimmer Light Ray across the 3D Title */}
        <div
          style={{
            position: "absolute",
            top: -80,
            bottom: -80,
            left: "50%",
            width: 160,
            transform: `translateX(${shimmerX}%) skewX(-25deg)`,
            background:
              "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.18) 20%, rgba(255, 255, 255, 0.95) 50%, rgba(255, 255, 255, 0.18) 80%, transparent 100%)",
            opacity: shimmerOpacity,
            pointerEvents: "none",
            zIndex: 35,
            mixBlendMode: "screen",
          }}
        />

        {/* ─── TOP WORD: "अगली" (Slides from LEFT, Pure White with 3D Deep Extrusion) ─── */}
        <div
          style={{
            fontFamily: "'Noto Sans Devanagari', 'Impact', sans-serif",
            fontSize: 140,
            fontWeight: 900,
            color: "#ffffff",
            letterSpacing: "4px",
            lineHeight: 1.15,
            padding: "8px 24px",
            transform: `translateX(${agliTranslateX}px)`,
            opacity: agliOpacity,
            textShadow:
              "0 2px 0 #b30000, 0 4px 0 #900000, 0 7px 0 #680000, 0 10px 0 #450000, 0 14px 28px rgba(0, 0, 0, 0.95)",
            filter: "drop-shadow(0 0 24px rgba(255, 255, 255, 0.45))",
            overflow: "visible",
          }}
        >
          अगली
        </div>

        {/* ─── BOTTOM WORD: "बड़ी ख़बर" (Slides from RIGHT, Golden 3D Bevel with generous padding so matras NEVER clip) ─── */}
        <div
          style={{
            fontFamily: "'Noto Sans Devanagari', 'Impact', sans-serif",
            fontSize: 175,
            fontWeight: 950,
            marginTop: 14, // Clean positive gap so 'बड़ी' की मात्रा never touches or collides
            letterSpacing: "3px",
            lineHeight: 1.28,
            padding: "24px 44px", // Generous padding to prevent WebkitBackgroundClip text-box clipping
            transform: `translateX(${badiTranslateX}px)`,
            opacity: badiOpacity,
            background: "linear-gradient(180deg, #fff9c4 0%, #ffca28 40%, #ff8f00 80%, #e65100 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            filter:
              "drop-shadow(0 4px 0 #8b4e00) drop-shadow(0 8px 0 #5a2e00) drop-shadow(0 16px 32px rgba(0,0,0,0.95))",
            overflow: "visible",
          }}
        >
          बड़ी ख़बर
        </div>
      </div>
    </div>
  );
};
