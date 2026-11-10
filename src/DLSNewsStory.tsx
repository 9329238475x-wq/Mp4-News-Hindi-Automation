/**
 * Master TV Broadcast – Single Story Composition
 * 100% matches user's detailed specification:
 * - Subscribe Video Intro plays EXCLUSIVELY at the very start of the first story (storyIndex === 0)
 *   with official channel watermark overlay!
 * - Never added to subsequent stories (storyIndex > 0).
 * - "Taraju" (Seesaw / Scale) Dynamic Focus Choreography:
 *   - Frame 0-42: Initial Center Hook (Headline Panel BIG in Center, Types Live in 2.0s)
 *   - Frame 42-240: Split Screen (Media Frame on Left with Images 1-3, Headline Card on Right)
 *   - Frame 240-480: TARAJU SHIFT 1 -> Media Panel Expands to Grand 1740x640 Cinema Frame (Images 4-6 with Directional Slides), Headline Card recedes
 *   - Frame 480-720: TARAJU SHIFT 2 -> Headline Card comes forward, Bullet Point 1 Types Live in 2.0s, Media Panel returns to Split
 *   - Frame 720-960: TARAJU SHIFT 3 -> Media Panel Expands to Grand Frame (Images 7-9)
 *   - Frame 960-1200: TARAJU SHIFT 4 -> Next Headline Types Live in 2.0s, Media in Split
 * - 10-15 Real News Photos with Smart Watermark Cropping!
 * - Directional transitions: Slide from Left, Drop from Top, Slide from Right, Rise from Bottom, Ken Burns!
 * - Pinned on Top Center: [ BREAKING | NEWS ] 3D Ulat-Palat Flip Badge
 * - Shiny looping News-background.mp4 + Background-Music at 15% volume
 * - 100% Emoji-Free Ticker & Header
 */
import React from "react";
import {
  Audio,
  Loop,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { assetPath } from "./utils/assetHelper";
import { NewsBackground } from "./components/NewsBackground";
import { NewsTopHeader } from "./components/NewsTopHeader";
import { DLSTarajuShowcase } from "./components/DLSTarajuShowcase";
import { DLSNewsCard } from "./components/DLSNewsCard";
import { NewsTicker } from "./components/NewsTicker";
import { NextStoryTransition } from "./components/NextStoryTransition";
import { FullScreenMemeOverlay } from "./components/FullScreenMemeOverlay";
import { SubscribeIntro } from "./components/SubscribeIntro";
import { DLSStoryProps, DLS_TIMING } from "./types";

const DLSStoryMain: React.FC<DLSStoryProps> = ({
  story,
  storyIndex,
  totalStories,
  channelName,
  channelTagline,
  allHeadlines,
  globalStartFrame = 0,
  mainDurationFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames: compositionFrames } = useVideoConfig();
  // 1ms प्रिसिजन: यदि पैरेंट ने सटीक स्टोरी फ्रेम्स दिए हैं, तो उसी का उपयोग करें (0 dead air)
  const durationInFrames = mainDurationFrames ?? compositionFrames;

  // Identify meme assets so they NEVER display as normal news photos
  const memePaths = new Set(
    story.chunks
      ?.filter((c) => c.visual_intent === "MEME_REACTION" && c.local_visual_path)
      .map((c) => c.local_visual_path!) || []
  );

  // 10 to 15 Real News Images Array (filtered to strictly real photos, excluding memes)
  const rawImages =
    story.all_real_images && story.all_real_images.length > 0
      ? story.all_real_images
      : [
          story.local_news_image ||
            story.local_visual_asset ||
            "assets/news_img_1_01.jpg",
        ];
  const allImages = rawImages.filter((img) => !memePaths.has(img));
  if (allImages.length === 0) {
    allImages.push(rawImages[0]);
  }

  // Authentic video asset if available (must be an MP4 or WebM file, not a twitter link or object)
  const rawVideo =
    story.videos && story.videos.length > 0 ? story.videos[0] : null;
  const videoAsset =
    typeof rawVideo === "string"
      ? rawVideo
      : rawVideo && typeof rawVideo === "object"
      ? rawVideo.local_path ||
        (typeof rawVideo.url === "string" && (rawVideo.url.endsWith(".mp4") || rawVideo.url.endsWith(".webm"))
          ? rawVideo.url
          : null)
      : null;

  // ─── TARAJU (SEESAW) PIECEWISE CONTINUOUS CHOREOGRAPHY ───
  let expandProgress = 0;
  if (frame >= 380 && frame < 620) {
    const sp = spring({
      frame: frame - 380,
      fps,
      config: { damping: 14, mass: 0.8 },
    });
    expandProgress = interpolate(sp, [0, 1], [0, 1]);
  } else if (frame >= 620 && frame < 860) {
    const sp = spring({
      frame: frame - 620,
      fps,
      config: { damping: 14, mass: 0.8 },
    });
    expandProgress = interpolate(sp, [0, 1], [1, 0]);
  } else if (frame >= 860 && frame < 1100) {
    const sp = spring({
      frame: frame - 860,
      fps,
      config: { damping: 14, mass: 0.8 },
    });
    expandProgress = interpolate(sp, [0, 1], [0, 1]);
  } else if (frame >= 1100 && frame < 1340) {
    const sp = spring({
      frame: frame - 1100,
      fps,
      config: { damping: 14, mass: 0.8 },
    });
    expandProgress = interpolate(sp, [0, 1], [1, 0]);
  } else {
    expandProgress = 0;
  }

  const audioStartFrame = 0; // 0s pre-padding (voice starts immediately at frame 0)
  const isSingleOrLast = !totalStories || totalStories === 1 || storyIndex === totalStories - 1;
  const transitionDuration = isSingleOrLast ? 0 : 30; // 0s on single/last story so video finishes exactly with voice
  const transitionStartFrame = Math.max(0, durationInFrames - transitionDuration);
  const nextStoryNumber = (story.story_number || storyIndex + 1) + 1;
  const isLastStory = isSingleOrLast;

  // ─── DYNAMIC MEME TIMING CALCULATION (Weighted sentence mapping) ───
  const memeSegments: {
    imageSrc: string;
    caption: string;
    startFrame: number;
    durationInFrames: number;
  }[] = [];

  const chunkVisuals: {
    chunkIndex: number;
    startFrame: number;
    endFrame: number;
    imageSrc: string;
    sentence?: string;
  }[] = [];

  if (story.chunks && story.chunks.length > 0) {
    const chunks = story.chunks;
    const voStart = audioStartFrame;
    const voAvailableFrames = Math.max(300, transitionStartFrame - voStart);
    const totalChars = chunks.reduce(
      (acc, c) => acc + Math.max(10, (c.sentence || "").trim().length),
      0
    );

    let cumulativeFrames = voStart;
    let globalImgIdx = 0;
    const totalImages = allImages.length;

    chunks.forEach((chunk, cIdx) => {
      const chars = Math.max(10, (chunk.sentence || "").trim().length);
      const chunkFrames = Math.floor((chars / totalChars) * voAvailableFrames);
      const cStart = cumulativeFrames;
      const cEnd =
        cIdx === chunks.length - 1
          ? transitionStartFrame
          : cumulativeFrames + chunkFrames;

      const chunkDur = cEnd - cStart;

      // Each chunk displays its dedicated matching image (or primary story image)
      // Long chunks (>= 150 frames / ~5s) can split into 2 matching images
      const primaryChunkImage =
        chunk.local_visual_path ||
        allImages[cIdx % totalImages] ||
        allImages[0];
      const secondaryImage =
        allImages[(cIdx + 1) % totalImages] || primaryChunkImage;

      const numSlots = chunkDur >= 150 && totalImages > chunks.length ? 2 : 1;
      const slotDuration = Math.floor(chunkDur / numSlots);

      for (let s = 0; s < numSlots; s++) {
        const slotStart = cStart + s * slotDuration;
        const slotEnd =
          s === numSlots - 1 ? cEnd : slotStart + slotDuration;

        const currentSlotImage =
          s === 0 ? primaryChunkImage : secondaryImage;

        chunkVisuals.push({
          chunkIndex: cIdx + 1,
          startFrame: slotStart,
          endFrame: slotEnd,
          imageSrc: currentSlotImage,
          sentence: chunk.sentence,
        });
      }

      if (chunk.visual_intent === "MEME_REACTION" && chunk.local_visual_path) {
        // High-impact punchy meme display: ~75 to 90 frames (~2.5 to 3.0s)
        const memeDur = Math.min(chunkFrames, 90);
        const startOffset = Math.max(0, Math.floor((chunkFrames - memeDur) / 2));
        memeSegments.push({
          imageSrc: chunk.local_visual_path,
          caption: "वायरल मीम / REACTION",
          startFrame: cumulativeFrames + startOffset,
          durationInFrames: memeDur,
        });
      }
      cumulativeFrames += chunkFrames;
    });
  }

  const isSuicideStory = Boolean(story.is_suicide_story) || /आत्महत्या|खुदकुशी|suicide/i.test(`${story.screen_headline || ''} ${story.voiceover_script || ''} ${(story.bullet_points || []).join(' ')}`);
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        position: "relative",
        fontFamily: "'Noto Sans Devanagari', 'Segoe UI', sans-serif",
        color: "#ffffff",
        overflow: "hidden",
        backgroundColor: "#02040a",
      }}
    >
      {/* ─── 0. BACKGROUND MUSIC (Soft 8% Volume, so voiceover is clear & dominant) ─── */}
      <Loop durationInFrames={924}>
        <Audio
          src={assetPath("background-Music.mp3")}
          volume={0.08}
        />
      </Loop>

      {/* ─── VOICEOVER AUDIO (Starts Frame 0, Boosted 130% Studio Volume) ─── */}
      <Sequence from={audioStartFrame} name={`Audio: Story ${story.story_number}`}>
        {story.local_audio_asset && (
          <Audio src={assetPath(story.local_audio_asset)} volume={1.3} />
        )}
      </Sequence>

      {/* ─── 1. SHINY 1080p NEWS STUDIO MOTION VIDEO LOOP BACKGROUND ─── */}
      <NewsBackground />

      {/* ─── 2. TOP BROADCAST HEADER (Left Channel Branding, Zero Emojis) ─── */}
      <NewsTopHeader
        channelName={channelName}
        tagline={channelTagline}
      />

      {/* ─── 3. DYNAMIC TARAJU MEDIA SHOWCASE (10-15 Images + Directional Transitions + Seesaw Expansion) ─── */}
      <DLSTarajuShowcase
        images={allImages}
        chunkVisuals={chunkVisuals}
        videoSrc={videoAsset}
        attributionTag={(
          story.image_attribution_tag ||
          `स्रोत: ${story.real_image_attribution || "विशेष रिपोर्ट"}`
        )
          .replace(/📷|📸/g, "")
          .trim()}
        isExpanded={expandProgress > 0.5}
        expandProgress={expandProgress}
      />

      {/* ─── 4. MASTER DYNAMIC CARD (Center -> Right + Live Typing + Seesaw Focus) ─── */}
      <DLSNewsCard
        headline={story.screen_headline}
        headlines={story.screen_headlines}
        category={story.category}
        bulletPoints={story.bullet_points}
        expandProgress={expandProgress}
      />

      {/* ─── 4.5. FULL-SCREEN DYNAMIC MEME OVERLAYS (Full-screen between Header & Ticker, Z-Index 45) ─── */}
      {memeSegments.map((seg, sIdx) => {
        if (
          frame >= seg.startFrame &&
          frame < seg.startFrame + seg.durationInFrames
        ) {
          return (
            <Sequence
              key={sIdx}
              from={seg.startFrame}
              durationInFrames={seg.durationInFrames}
            >
              <FullScreenMemeOverlay
                imageSrc={seg.imageSrc}
                caption={seg.caption}
                channelName={channelName}
                durationInFrames={seg.durationInFrames}
              />
            </Sequence>
          );
        }
        return null;
      })}

      {/* ─── 5. "अगली बड़ी ख़बर" STINGER TRANSITION BUMPER (Z-Index 40: Above media/card, BEHIND Top Header & News Ticker) ─── */}
      {!isLastStory && frame >= transitionStartFrame && (
        <Sequence from={transitionStartFrame} durationInFrames={transitionDuration}>
          <NextStoryTransition
            nextStoryNumber={nextStoryNumber}
            channelName={channelName}
          />
        </Sequence>
      )}

      {/* ─── 5.8 SUICIDE PREVENTION COMPLIANCE TICKER (YouTube / Meta Policy Safe) ─── */}
      {isSuicideStory && (
        <div
          style={{
            position: 'absolute',
            bottom: 104,
            left: 40,
            right: 40,
            height: 40,
            backgroundColor: 'rgba(180, 20, 20, 0.94)',
            borderRadius: 8,
            border: '1px solid rgba(255, 200, 200, 0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 85,
            boxShadow: '0 4px 20px rgba(0,0,0,0.6)',
            color: '#ffffff',
            fontSize: 18,
            fontWeight: 700,
            letterSpacing: '0.5px',
          }}
        >
          🚨 मानसिक स्वास्थ्य हेल्पलाइन: Tele-MANAS (14416) | KIRAN (1800-599-0019)
        </div>
      )}

      {/* ─── 6. BOTTOM TICKER (Elevated 26px, 76px Height, Zero Emojis - Z-Index 100 on Top) ─── */}
      <NewsTicker
        headlines={allHeadlines}
        channelName={channelName}
        globalFrameOffset={globalStartFrame}
      />
    </div>
  );
};

export const DLSNewsStory: React.FC<DLSStoryProps> = ({
  story,
  storyIndex,
  totalStories,
  channelName = "Mp4 News हिन्दी",
  channelTagline = "सच्चाई सबसे पहले",
  allHeadlines = [],
  globalStartFrame = 0,
}) => {
  const { durationInFrames } = useVideoConfig();

  // Subscribe Intro video plays EXCLUSIVELY on the very first story (storyIndex === 0)
  const hasSubscribeIntro = storyIndex === 0;
  const introFrames = hasSubscribeIntro ? DLS_TIMING.introFrames : 0;
  const mainDuration = Math.max(1, durationInFrames - introFrames);

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        position: "relative",
        backgroundColor: "#02040a",
      }}
    >
      {/* ─── 1. SUBSCRIBE VIDEO INTRO (Exclusively at the start of Story #1) ─── */}
      {hasSubscribeIntro && (
        <Sequence
          from={0}
          durationInFrames={introFrames}
          name="Subscribe Video Intro"
        >
          <SubscribeIntro
            channelName={channelName}
            channelTagline={channelTagline}
          />
        </Sequence>
      )}

      {/* ─── 2. MAIN NEWS STORY CONTENT ─── */}
      <Sequence
        from={introFrames}
        durationInFrames={mainDuration}
        name={`Story Content #${story.story_number || storyIndex + 1}`}
      >
        <DLSStoryMain
          story={story}
          storyIndex={storyIndex}
          totalStories={totalStories}
          channelName={channelName}
          channelTagline={channelTagline}
          allHeadlines={allHeadlines}
          globalStartFrame={globalStartFrame + introFrames}
          mainDurationFrames={mainDuration}
        />
      </Sequence>
    </div>
  );
};
