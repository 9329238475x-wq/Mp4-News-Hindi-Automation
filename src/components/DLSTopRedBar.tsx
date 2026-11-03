/**
 * DLS News – Top Red Headline Bar
 * Full-width red strip at the very top with bold white Hindi headline text
 * Exactly like DLS News: solid red, white bold text, stays persistent
 */
import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { DLS_COLORS } from "../types";

interface DLSTopRedBarProps {
  headline: string;
}

export const DLSTopRedBar: React.FC<DLSTopRedBarProps> = ({ headline }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Slide down entrance
  const translateY = spring({
    frame,
    fps,
    from: -80,
    to: 0,
    config: { damping: 14, mass: 0.8 },
  });

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        height: 64,
        background: `linear-gradient(90deg, ${DLS_COLORS.topBarRed} 0%, ${DLS_COLORS.topBarRedDark} 100%)`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 100,
        transform: `translateY(${translateY}px)`,
        boxShadow: "0 4px 20px rgba(200, 0, 0, 0.6)",
      }}
    >
      <div
        style={{
          color: DLS_COLORS.textWhite,
          fontSize: 32,
          fontWeight: 900,
          textAlign: "center",
          padding: "0 40px",
          lineHeight: 1.2,
          letterSpacing: "0.5px",
          textShadow: "2px 2px 4px rgba(0,0,0,0.5)",
          whiteSpace: "nowrap",
          overflow: "hidden",
          textOverflow: "ellipsis",
          maxWidth: "100%",
        }}
      >
        {headline}
      </div>
    </div>
  );
};
