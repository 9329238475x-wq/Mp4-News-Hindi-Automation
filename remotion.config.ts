/**
 * High-Performance, Multi-Platform Remotion Configuration
 * - Local Windows: Single-threaded safe rendering to protect PC hardware from overheating
 * - Linux Cloud (Kaggle CPU): Turbo multi-core rendering with JPEG frame buffer & veryfast x264 preset
 */
import { Config } from "@remotion/cli/config";
const { startLocalAssetServer } = require("./src/utils/localAssetServer.js");

// Start high-performance zero-copy local streaming server for assets & story outputs
startLocalAssetServer();

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(85);
Config.setOverwriteOutput(true);
Config.setX264Preset("veryfast");
Config.setDefaultPremountInSeconds(1);

if (process.platform === "linux") {
  // Linux headless Docker: disable OpenGL context overhead for 2D DOM compositions
  Config.setChromiumOpenGlRenderer(null);
} else {
  // Windows: Safe low-resource single-core mode to keep CPU cool
  Config.setChromiumOpenGlRenderer("angle");
  Config.setConcurrency(1);
}
