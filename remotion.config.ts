/**
 * Safe, Low-Resource Remotion Configuration
 * Designed to prevent PC overheating, crashes, or sudden shutdowns:
 * - Concurrency capped at 1 (Single-threaded rendering = cool CPU & low RAM)
 * - Lightweight JPEG frame buffer with 80% quality
 * - ANGLE / Software OpenGL rendering to protect GPU drivers
 */
import { Config } from "@remotion/cli/config";
const { startLocalAssetServer } = require("./src/utils/localAssetServer.js");

// Start high-performance zero-copy local streaming server for assets & story outputs
startLocalAssetServer();

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(80);
Config.setOverwriteOutput(true);
Config.setConcurrency(1); // Safe single-core mode: prevents 100% CPU spikes & overheating!
Config.setChromiumOpenGlRenderer("angle");
Config.setDefaultPremountInSeconds(1);
