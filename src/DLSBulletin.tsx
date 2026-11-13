/**
 * Master TV News – Full Multi-Story Bulletin
 * Sequences all stories with mathematical frame-accurate timings:
 * - Passes globalStartFrame to ensure continuous ticker scrolling and digital clock
 */
import React from "react";
import { Sequence } from "remotion";
import { DLSNewsStory } from "./DLSNewsStory";
import { DLSBulletinProps, DLS_TIMING, getStoryDurationFrames } from "./types";

export const DLSBulletin: React.FC<DLSBulletinProps> = ({
  stories,
  channelName = "Uncut भारत",
  channelTagline = "100% निडर • निष्पक्ष • सच",
}) => {
  // Collect all headlines for the continuous bottom ticker
  const allHeadlines = stories.map((s) => s.screen_headline);

  // Dynamic start and frame-accurate duration for each story
  // Only the first story (index === 0) includes the 93 frames Subscribe Intro
  let currentStart = 0;
  const storyTimings = stories.map((story, index) => {
    const from = currentStart;
    const isFirstStory = index === 0;
    const durationInFrames = getStoryDurationFrames(story, isFirstStory);

    currentStart += durationInFrames;
    return { from, durationInFrames };
  });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "#02040a",
      }}
    >
      {stories.map((story, index) => {
        const { from, durationInFrames } = storyTimings[index];
        return (
          <Sequence
            key={story.story_number}
            from={from}
            durationInFrames={durationInFrames}
            name={`[#${String(story.story_number).padStart(2, "0")}] ${story.verified_location || ""}: ${story.screen_headline.substring(0, 35)}...`}
          >
            <DLSNewsStory
              story={story}
              storyIndex={index}
              totalStories={stories.length}
              channelName={channelName}
              channelTagline={channelTagline}
              allHeadlines={allHeadlines}
              globalStartFrame={from}
            />
          </Sequence>
        );
      })}
    </div>
  );
};
