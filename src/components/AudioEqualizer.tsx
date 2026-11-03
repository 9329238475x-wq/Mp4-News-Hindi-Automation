/**
 * Real-Time Audio-Synced Equalizer
 * - Directly reads frame-accurate waveform amplitude extracted from actual MP3 audio.
 * - Silence Gate: If audio is silent/paused, bars collapse to 0%.
 * - 12-Band Spectral Shaper: Simulates natural human voice frequency distribution.
 * - Matches the bottom-right equalizer in 'news-preview.png'.
 */
import React from "react";
import { TV_COLORS } from "../types";

interface AudioEqualizerProps {
  waveform?: number[];
  currentFrame: number;
  audioStartFrame: number;
}

// 12-band spectral multipliers mimicking voice EQ (peaks around 300Hz-2.5kHz)
const FREQUENCY_CURVE = [
  0.42, 0.65, 0.88, 1.0, 0.95, 0.92, 0.85, 0.78, 0.65, 0.52, 0.40, 0.30
];

export const AudioEqualizer: React.FC<AudioEqualizerProps> = ({
  waveform = [],
  currentFrame,
  audioStartFrame,
}) => {
  // Relative frame inside audio playback
  const audioFrame = currentFrame - audioStartFrame;

  // Retrieve current RMS amplitude
  let baseAmp = 0;
  if (audioFrame >= 0 && audioFrame < waveform.length) {
    baseAmp = waveform[audioFrame] || 0;
  }

  // Silence Gate threshold check: Below 0.02 is absolute zero
  const isSilent = baseAmp < 0.02;
  const activeAmp = isSilent ? 0 : baseAmp;

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 8,
        background: "rgba(3, 8, 20, 0.85)",
        border: "1px solid rgba(0, 240, 255, 0.25)",
        borderRadius: 6,
        padding: "4px 10px",
        boxShadow: "0 0 12px rgba(0, 240, 255, 0.15)",
      }}
    >
      {/* 'AUDIO' Tag */}
      <span
        style={{
          color: TV_COLORS.neonCyan,
          fontSize: 11,
          fontWeight: 900,
          letterSpacing: "1.2px",
          fontFamily: "'Segoe UI', sans-serif",
          textShadow: `0 0 8px ${TV_COLORS.neonCyanGlow}`,
        }}
      >
        AUDIO
      </span>

      {/* 12 Vertical Bars */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          gap: 2.5,
          height: 18,
          width: 52,
        }}
      >
        {FREQUENCY_CURVE.map((curveWeight, i) => {
          // Dynamic jitter simulation across frequencies based on baseAmp
          const phase = (audioFrame * 0.4 + i * 1.5);
          const jitter = isSilent ? 0 : Math.sin(phase) * 0.15;
          const barHeightRatio = Math.max(
            0.08,
            Math.min(1.0, (activeAmp + jitter) * curveWeight)
          );
          const barHeightPx = isSilent ? 2 : Math.round(barHeightRatio * 18);

          // Color calculation: Cyan at bottom, yellow at mid, red at top peak
          let barBg = TV_COLORS.equalizerCyan;
          if (barHeightRatio > 0.75) {
            barBg = TV_COLORS.equalizerRed;
          } else if (barHeightRatio > 0.45) {
            barBg = TV_COLORS.equalizerYellow;
          }

          return (
            <div
              key={i}
              style={{
                width: 2.5,
                height: barHeightPx,
                background: barBg,
                borderRadius: 1,
                boxShadow: isSilent ? "none" : `0 0 4px ${barBg}`,
                transition: "height 0.04s ease",
              }}
            />
          );
        })}
      </div>
    </div>
  );
};
