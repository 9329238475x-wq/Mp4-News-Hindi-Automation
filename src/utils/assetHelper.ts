const LOCAL_SERVER_PORT = 3333;

/**
 * Universal Asset Resolver for Sicreat-Automation
 * Routes all media requests to the local high-speed streaming server (port 3333):
 * - assets/News-background.mp4 -> http://127.0.0.1:3333/assets/News-background.mp4
 * - out/story_01/audio_story_1.mp3 -> http://127.0.0.1:3333/out/story_01/audio_story_1.mp3
 * - out/story_01/news_img_1_01.jpg -> http://127.0.0.1:3333/out/story_01/news_img_1_01.jpg
 */
export const assetPath = (path: string | null | undefined): string => {
  if (!path) return "";
  if (
    path.startsWith("http://") ||
    path.startsWith("https://") ||
    path.startsWith("data:")
  ) {
    return path;
  }
  const clean = path.replace(/^[\\/]+/, "").replace(/\\/g, "/");
  return `http://127.0.0.1:${LOCAL_SERVER_PORT}/${clean}`;
};
