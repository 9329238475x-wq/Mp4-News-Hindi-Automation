import http from "node:http";
import fs from "node:fs";
import path from "node:path";

const PORT = 3333;
const ROOT_DIR = path.resolve(__dirname, "..", "..");

const MIME_TYPES: Record<string, string> = {
  ".mp4": "video/mp4",
  ".webm": "video/webm",
  ".mp3": "audio/mpeg",
  ".wav": "audio/wav",
  ".ogg": "audio/ogg",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".png": "image/png",
  ".webp": "image/webp",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".json": "application/json",
  ".ttf": "font/ttf",
  ".otf": "font/otf",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
};

let serverInstance: http.Server | null = null;

function findFile(reqPath: string): string | null {
  const clean = reqPath.replace(/^[\\/]+/, "");
  const candidateBases = [
    path.resolve(ROOT_DIR, clean),
    path.resolve(ROOT_DIR, "out", clean),
    path.resolve(ROOT_DIR, "assets", clean),
  ];

  for (const baseP of candidateBases) {
    if (fs.existsSync(baseP) && fs.statSync(baseP).isFile()) {
      return baseP;
    }
  }

  const candidateSubdirs = [
    "news real image",
    "news_real_image",
    "news image",
    "news_image",
    "voice over",
    "voice_over",
    "meems image",
    "meems_image",
  ];

  for (const baseP of candidateBases) {
    const parsed = path.parse(baseP);
    for (const sub of candidateSubdirs) {
      const subP = path.join(parsed.dir, sub, parsed.base);
      if (fs.existsSync(subP) && fs.statSync(subP).isFile()) {
        return subP;
      }
    }
  }

  return null;
}

export const startLocalAssetServer = (): Promise<number> => {
  return new Promise((resolve) => {
    if (serverInstance) {
      return resolve(PORT);
    }

    const server = http.createServer((req, res) => {
      // Handle CORS Preflight
      res.setHeader("Access-Control-Allow-Origin", "*");
      res.setHeader("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS");
      res.setHeader("Access-Control-Allow-Headers", "*");

      if (req.method === "OPTIONS") {
        res.writeHead(204);
        return res.end();
      }

      const parsedUrl = new URL(req.url || "/", `http://127.0.0.1:${PORT}`);
      let reqPath = decodeURIComponent(parsedUrl.pathname).replace(/^\/+/, "");

      const fullPath = findFile(reqPath);
      if (!fullPath) {
        const ext = path.extname(reqPath).toLowerCase();
        if ([".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"].includes(ext)) {
          const TRANSPARENT_1X1_PNG = Buffer.from(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
            "base64"
          );
          res.writeHead(200, {
            "Content-Type": "image/png",
            "Content-Length": TRANSPARENT_1X1_PNG.length,
            "Cache-Control": "no-cache",
          });
          return res.end(TRANSPARENT_1X1_PNG);
        }
        res.writeHead(404, { "Content-Type": "text/plain" });
        return res.end(`File Not Found: ${reqPath}`);
      }

      const stat = fs.statSync(fullPath);
      const totalSize = stat.size;
      const ext = path.extname(fullPath).toLowerCase();
      const contentType = MIME_TYPES[ext] || "application/octet-stream";

      // ─── Range Request Handling (Essential for Chromium Video & Audio Seeking) ───
      const range = req.headers.range;
      if (range) {
        const parts = range.replace(/bytes=/, "").split("-");
        const start = parseInt(parts[0], 10);
        const end = parts[1] ? parseInt(parts[1], 10) : totalSize - 1;

        if (start >= totalSize || end >= totalSize) {
          res.writeHead(416, {
            "Content-Range": `bytes */${totalSize}`,
          });
          return res.end();
        }

        const chunksize = end - start + 1;
        const fileStream = fs.createReadStream(fullPath, { start, end });

        res.writeHead(206, {
          "Content-Range": `bytes ${start}-${end}/${totalSize}`,
          "Accept-Ranges": "bytes",
          "Content-Length": chunksize,
          "Content-Type": contentType,
        });

        fileStream.pipe(res);
      } else {
        res.writeHead(200, {
          "Content-Length": totalSize,
          "Content-Type": contentType,
          "Accept-Ranges": "bytes",
        });

        fs.createReadStream(fullPath).pipe(res);
      }
    });

    server.on("error", (err: any) => {
      if (err.code === "EADDRINUSE") {
        // Port already in use (e.g. from previous run), reuse it!
        resolve(PORT);
      } else {
        console.error("Local Asset Server error:", err);
        resolve(PORT);
      }
    });

    server.listen(PORT, "127.0.0.1", () => {
      serverInstance = server;
      resolve(PORT);
    });
  });
};
