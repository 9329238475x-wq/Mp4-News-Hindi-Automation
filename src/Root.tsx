import React from "react";
import { DLSComposition } from "./Composition";
import { assetPath } from "./utils/assetHelper";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <style>
        {`
          @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600;700;800;900&display=swap');

          @font-face {
            font-family: 'Noto Sans Devanagari';
            src: url('${assetPath("assets/NotoSansDevanagari-Regular.ttf")}') format('truetype');
            font-weight: 400 500;
            font-style: normal;
          }

          @font-face {
            font-family: 'Noto Sans Devanagari';
            src: url('${assetPath("assets/NotoSansDevanagari-Bold.ttf")}') format('truetype');
            font-weight: 600 700 800 900;
            font-style: normal;
          }

          *, *::before, *::after {
            font-family: 'Noto Sans Devanagari', 'Nirmala UI', 'Mangal', 'Segoe UI', sans-serif;
          }
        `}
      </style>
      <DLSComposition />
    </>
  );
};
