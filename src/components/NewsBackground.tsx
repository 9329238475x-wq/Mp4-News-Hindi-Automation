/**
 * Master TV Studio Background (100% Broadcast Motion Video Loop)
 * Plays the user's authentic 'News-background.mp4' on a continuous seamless loop!
 */
import React from "react";
import { Loop, OffthreadVideo } from "remotion";
import { assetPath } from "../utils/assetHelper";

export const NewsBackground: React.FC = () => {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        backgroundColor: "#000000",
        overflow: "hidden",
      }}
    >
      {/* ─── Authentic 1080p News Background Motion Video Loop ─── */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
        }}
      >
        <Loop durationInFrames={300}>
          <OffthreadVideo
            src={assetPath("assets/News-background.mp4")}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
            muted
          />
        </Loop>
      </div>

      {/* ─── Soft Vignette for Border Contrast ─── */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse at center, transparent 65%, rgba(0, 0, 0, 0.4) 100%)",
          pointerEvents: "none",
        }}
      />
    </div>
  );
};
