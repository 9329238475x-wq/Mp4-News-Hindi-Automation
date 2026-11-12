/**
 * Master TV News Broadcast – Type Definitions & Design Tokens
 * Exactly matches 'news-preview.png' and 'news-video.mp4'
 */

/* ── Single Story Timing Specification ── */
export interface StoryTimingSpecs {
  fps: number;
  pre_padding_frames: number;   // 15 frames (0.5s visual reveal)
  audio_start_frame: number;    // Frame 15 (exact audio trigger)
  audio_duration_frames: number;
  post_padding_frames: number;  // 36 frames (1.2s breathing pause)
  transition_frames: number;    // 15 frames (0.5s crossfade)
  total_story_frames: number;
  total_story_seconds: number;
}

/* ── Story Chunk (Sentence-level visual mapping & dynamic memes) ── */
export interface VisualSlot {
  path: string;
  is_scraped?: boolean;
  credit_source?: string | null;
  keyword?: string;
}

export interface StoryChunk {
  chunk_index: number;
  sentence: string;
  visual_intent: "REAL_PHOTO" | "MEME_REACTION";
  image_keywords_en: string[];
  meme_keyword_en?: string | null;
  local_visual_path?: string;
  local_visual_paths?: string[];
  visual_images?: VisualSlot[];
  is_scraped_news?: boolean;
  credit_source?: string | null;
}

/* ── Single Story ── */
export interface DLSStory {
  story_number: number;
  category: string;
  is_suicide_story?: boolean;
  screen_headline: string;
  /** 3-4 Dynamic Sequential Screen Headlines (Change across story phases) */
  screen_headlines?: string[];
  voiceover_script: string;
  bullet_points: string[];
  chunks?: StoryChunk[];
  visual_keywords: string[];
  visual_keywords_en?: string[];
  primary_source_index: number;
  real_image_url: string | null;
  real_image_attribution: string;
  source?: string;
  original_title: string;
  all_real_images?: string[];
  /** Locally downloaded visual asset path (relative to public/) */
  local_visual_asset?: string;
  /** Locally downloaded news source image (relative to public/) */
  local_news_image?: string;
  /** Locally generated TTS audio path (relative to public/) */
  local_audio_asset?: string;
  /** Audio duration in seconds */
  audio_duration?: number;
  /** Frame-accurate audio RMS waveform (0.0 to 1.0 with -45dBFS silence gate) */
  audio_waveform?: number[];
  /** Verified dateline location (e.g., 'जीरकपुर (पंजाब)') */
  verified_location?: string;
  /** Verified transparent source tag (e.g., '📷 स्रोत: अमर उजाला | घटनास्थल') */
  image_attribution_tag?: string;
  /** Exact timing specs */
  timing_specs?: StoryTimingSpecs;
}

/* ── Single Story Remotion Props ── */
export interface DLSStoryProps extends Record<string, unknown> {
  story: DLSStory;
  storyIndex: number;
  totalStories: number;
  channelName: string;
  channelTagline?: string;
  /** All headlines for ticker rotation */
  allHeadlines: string[];
  /** Global frame offset for continuous ticker and clock in segmented renders */
  globalStartFrame?: number;
  /** Exact allocated frames for story content (excluding subscribe intro) */
  mainDurationFrames?: number;
}

/* ── Full Bulletin Remotion Props ── */
export interface DLSBulletinProps extends Record<string, unknown> {
  stories: DLSStory[];
  channelName: string;
  channelTagline: string;
}

/* ── Master TV Design Tokens (Matches news-preview.png) ── */
export const TV_COLORS = {
  headerRedGradient: "linear-gradient(135deg, #d30000 0%, #8b0000 100%)",
  headerTaglineYellow: "#ffd700",
  liveRed: "#ff1744",
  statusPillBg: "rgba(10, 20, 38, 0.75)",
  statusPillBorder: "rgba(255, 255, 255, 0.15)",
  
  // Neon Cyber Frame
  neonCyan: "#00f0ff",
  neonCyanGlow: "rgba(0, 240, 255, 0.45)",
  neonCyanBorder: "rgba(0, 240, 255, 0.65)",
  exclusiveBadgeGradient: "linear-gradient(90deg, #ff9100 0%, #ff3d00 100%)",
  
  // Right Newsroom Card
  breakingBadgeGradient: "linear-gradient(90deg, #ff1744 0%, #b70038 100%)",
  glassCardBg: "rgba(7, 12, 24, 0.82)",
  glassCardBorder: "rgba(0, 240, 255, 0.22)",
  headlineWhite: "#ffffff",
  categoryCyan: "#00f0ff",
  categoryBlue: "#38bdf8",
  
  // Bullet Points
  bulletPillBg: "rgba(255, 255, 255, 0.05)",
  bulletPillBorder: "rgba(255, 255, 255, 0.12)",
  bulletArrowGold: "#fbbf24",
  bulletTextWhite: "#f3f4f6",
  
  // Audio Equalizer
  equalizerCyan: "#00f0ff",
  equalizerYellow: "#facc15",
  equalizerRed: "#ef4444",
  
  // Bottom Ticker
  tickerRedBox: "linear-gradient(135deg, #180003 0%, #3b0007 50%, #180003 100%)",
  tickerTrackBg: "linear-gradient(180deg, #d3000b 0%, #aa0007 50%, #820004 100%)",
  tickerBorderTop: "rgba(255, 77, 79, 0.45)",
  tickerStarGold: "#fde047",
  tickerTextWhite: "#ffffff",
  tickerTextRed: "#d3000b",
  tickerTextHighlight: "#fde047",

  // Studio Background
  bgDark1: "#040711",
  bgDark2: "#070c1d",
  bgDark3: "#0b142d",
} as const;

// Backward compatibility alias
export const DLS_COLORS = TV_COLORS;

export const DLS_TIMING = {
  fps: 30,
  prePaddingSeconds: 0,
  postPaddingSeconds: 0,
  transitionSeconds: 0,
  defaultAudioSeconds: 20,
  introFrames: 93, // 3.10 seconds of Subscribe-video.mp4 (exclusively on first story)

  get prePaddingFrames() { return 0; },
  get postPaddingFrames() { return 0; },
  get transitionFrames() { return 0; },
} as const;

export const getStoryDurationFrames = (
  story: DLSStory,
  isFirstStory: boolean = false
): number => {
  // 1ms प्रिसिजन: ऑडियो खत्म होते ही वीडियो उसी फ्रेम पर समाप्त (Zero extra silence/dead air)
  const durSeconds = story.audio_duration || DLS_TIMING.defaultAudioSeconds;
  const baseFrames = Math.ceil(durSeconds * DLS_TIMING.fps);
  return isFirstStory ? baseFrames + DLS_TIMING.introFrames : baseFrames;
};

export const defaultDLSBulletin: DLSBulletinProps = {
  channelName: "Mp4 News हिन्दी",
  channelTagline: "सच्चाई सबसे पहले",
  stories: [],
};
