/**
 * Master TV News – Remotion Composition Registration
 * Matches 'news-preview.png' and 'news-video.mp4'
 */
import React from "react";
import { Composition } from "remotion";
import { DLSBulletin } from "./DLSBulletin";
import { DLSNewsStory } from "./DLSNewsStory";
import { ChannelLogo } from "./components/ChannelLogo";
import { SubscribeIntro } from "./components/SubscribeIntro";
import { DLSStory, defaultDLSBulletin, DLS_TIMING, getStoryDurationFrames } from "./types";
import sampleStories from "../niches/01-daily-top10/generated_sample_top10.json";

const loadedStories: DLSStory[] =
  Array.isArray(sampleStories) && sampleStories.length > 0
    ? (sampleStories as DLSStory[])
    : defaultDLSBulletin.stories;

const fullBulletinProps = {
  channelName: "Mp4 News हिन्दी",
  channelTagline: "सच्चाई सबसे पहले",
  stories: loadedStories,
};

export const DLSComposition: React.FC = () => {
  const totalFrames = loadedStories.reduce(
    (acc, s, idx) => acc + getStoryDurationFrames(s, idx === 0),
    0
  );
  const firstStory = loadedStories[0];
  const firstStoryDuration = getStoryDurationFrames(firstStory, true);
  const allHeadlines = loadedStories.map((s) => s.screen_headline);

  return (
    <>
      {/* 1. Fast Single-Story Preview (Story #1 with Subscribe Intro) */}
      <Composition
        id="DLSNewsSingleStory"
        component={DLSNewsStory}
        durationInFrames={firstStoryDuration}
        fps={DLS_TIMING.fps}
        width={1920}
        height={1080}
        defaultProps={{
          story: firstStory,
          storyIndex: 0,
          totalStories: loadedStories.length,
          channelName: fullBulletinProps.channelName,
          channelTagline: fullBulletinProps.channelTagline,
          allHeadlines,
          globalStartFrame: 0,
        }}
      />

      {/* 2. Full Multi-Story Bulletin (All 10 Stories) */}
      <Composition
        id="DLSNewsBulletin"
        component={DLSBulletin}
        durationInFrames={totalFrames}
        fps={DLS_TIMING.fps}
        width={1920}
        height={1080}
        defaultProps={fullBulletinProps}
      />

      {/* 3. Individual Story Compositions for Segmented Rendering & Lossless Concat */}
      {loadedStories.map((story, index) => {
        const isFirstStory = index === 0;
        const duration = getStoryDurationFrames(story, isFirstStory);
        const globalStart = loadedStories
          .slice(0, index)
          .reduce((acc, s, idx) => acc + getStoryDurationFrames(s, idx === 0), 0);
        const compId = `DLSNewsStory-${String(story.story_number || index + 1).padStart(2, "0")}`;

        return (
          <Composition
            key={story.story_number || index}
            id={compId}
            component={DLSNewsStory}
            durationInFrames={duration}
            fps={DLS_TIMING.fps}
            width={1920}
            height={1080}
            defaultProps={{
              story,
              storyIndex: index,
              totalStories: loadedStories.length,
              channelName: fullBulletinProps.channelName,
              channelTagline: fullBulletinProps.channelTagline,
              allHeadlines,
              globalStartFrame: globalStart,
            }}
          />
        );
      })}

      {/* 4. Channel Logo Compositions (Transparent & Studio PNG Renderings) */}
      <Composition
        id="Mp4NewsHindi-Logo-Style1"
        component={ChannelLogo}
        durationInFrames={1}
        fps={30}
        width={1180}
        height={340}
        defaultProps={{
          styleVariant: "mp4-newshindi" as const,
          showHandle: false,
          isSquareAvatar: false,
          darkBg: false,
        }}
      />

      <Composition
        id="Mp4NewsHindi-Logo-Style2"
        component={ChannelLogo}
        durationInFrames={1}
        fps={30}
        width={1180}
        height={340}
        defaultProps={{
          styleVariant: "mp4news-hindi" as const,
          showHandle: false,
          isSquareAvatar: false,
          darkBg: false,
        }}
      />

      <Composition
        id="Mp4NewsHindi-YouTube-Avatar-Dark"
        component={ChannelLogo}
        durationInFrames={1}
        fps={30}
        width={800}
        height={800}
        defaultProps={{
          styleVariant: "mp4-newshindi" as const,
          showHandle: false,
          isSquareAvatar: true,
          darkBg: true,
        }}
      />

      <Composition
        id="Mp4NewsHindi-YouTube-Avatar-Transparent"
        component={ChannelLogo}
        durationInFrames={1}
        fps={30}
        width={800}
        height={800}
        defaultProps={{
          styleVariant: "mp4-newshindi" as const,
          showHandle: false,
          isSquareAvatar: true,
          darkBg: false,
        }}
      />

      {/* 5. Subscribe Video Intro (Standalone Preview) */}
      <Composition
        id="Mp4NewsHindi-SubscribeIntro"
        component={SubscribeIntro}
        durationInFrames={DLS_TIMING.introFrames}
        fps={DLS_TIMING.fps}
        width={1920}
        height={1080}
        defaultProps={{
          channelName: fullBulletinProps.channelName,
          channelTagline: fullBulletinProps.channelTagline,
        }}
      />
    </>
  );
};
