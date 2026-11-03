import React from "react";

interface ChannelLogoProps {
  styleVariant?: "mp4-newshindi" | "mp4news-hindi";
  showHandle?: boolean;
  isSquareAvatar?: boolean;
  darkBg?: boolean;
}

export const ChannelLogo: React.FC<ChannelLogoProps> = ({
  styleVariant = "mp4-newshindi",
  isSquareAvatar = false,
  darkBg = false,
}) => {
  const isPill1 = styleVariant === "mp4-newshindi";

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        background: darkBg ? "#1f1f1f" : "transparent",
        fontFamily: "'Segoe UI', 'Impact', 'Arial Black', sans-serif",
        position: "relative",
        boxSizing: "border-box",
      }}
    >
      {/* ─── MAIN CAPSULE BADGE (Matches user's uploaded reference) ─── */}
      <div
        style={{
          position: "relative",
          display: "inline-flex",
          alignItems: "stretch",
          borderRadius: 22,
          overflow: "hidden",
          border: "5px solid #ffffff",
          boxShadow:
            "0 14px 44px rgba(0, 0, 0, 0.75), 0 0 35px rgba(220, 20, 60, 0.5), inset 0 2px 2px rgba(255, 255, 255, 0.8)",
          transform: isSquareAvatar ? "scale(1.05)" : "scale(1.0)",
        }}
      >
        {/* Top Diagonal Gloss Reflection */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: "48%",
            background:
              "linear-gradient(180deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.05) 100%)",
            pointerEvents: "none",
            zIndex: 10,
          }}
        />

        {/* 45-degree Metallic Light Glint Ray */}
        <div
          style={{
            position: "absolute",
            top: -40,
            bottom: -40,
            left: isPill1 ? "36%" : "54%",
            width: 70,
            transform: "skewX(-28deg)",
            background:
              "linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.25) 30%, rgba(255, 255, 255, 0.9) 50%, rgba(255, 255, 255, 0.25) 70%, transparent 100%)",
            pointerEvents: "none",
            zIndex: 11,
          }}
        />

        {/* LEFT TAB: RED (Bold White Text) */}
        <div
          style={{
            background:
              "linear-gradient(180deg, #ff1a1a 0%, #e60000 45%, #a80000 100%)",
            color: "#ffffff",
            fontWeight: 900,
            fontSize: isPill1 ? 74 : 64,
            padding: isPill1 ? "22px 55px" : "24px 50px",
            letterSpacing: isPill1 ? "3.5px" : "2.5px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            textShadow:
              "0 3px 8px rgba(0, 0, 0, 0.7), 0 0 15px rgba(255, 255, 255, 0.2)",
            position: "relative",
            zIndex: 2,
          }}
        >
          {isPill1 ? "MP4" : "MP4 NEWS"}
        </div>

        {/* Vertical Divider Line */}
        <div
          style={{
            width: 2,
            background: "rgba(0, 0, 0, 0.15)",
            zIndex: 3,
          }}
        />

        {/* RIGHT TAB: WHITE (Bold Red/Dark Text) */}
        <div
          style={{
            background:
              "linear-gradient(180deg, #ffffff 0%, #f6f6f6 50%, #e6e6e6 100%)",
            color: "#cc0000",
            fontWeight: 900,
            fontSize: isPill1 ? 64 : 76,
            padding: isPill1 ? "22px 48px" : "24px 60px",
            letterSpacing: isPill1 ? "2px" : "3px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 14,
            textShadow: "0 2px 5px rgba(0, 0, 0, 0.15)",
            position: "relative",
            zIndex: 2,
          }}
        >
          {isPill1 ? (
            <>
              <span style={{ color: "#cc0000" }}>NEWS</span>
              <span
                style={{
                  color: "#111111",
                  fontFamily: "'Segoe UI', 'Noto Sans Devanagari', sans-serif",
                  fontSize: 58,
                }}
              >
                हिन्दी
              </span>
            </>
          ) : (
            <span
              style={{
                color: "#cc0000",
                fontFamily: "'Segoe UI', 'Noto Sans Devanagari', sans-serif",
              }}
            >
              हिन्दी
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
