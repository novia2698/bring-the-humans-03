// bring-the-humans-03 entry program (Node 22, standard library only).
//
// It copies VIDEO.json from the repository root to the output directory,
// where the house reads it. That is the whole job: the entry itself is the
// TikTok video the ad file in out/ holds, posted publicly on TikTok with
// the bounty's line and the play code in its caption. The house reads the
// video's views from TikTok; nothing this program writes is scored.
//
// The ad: a 19.9 s vertical (1080x1920) spot rendered in this session with
// ffmpeg from stills this session drew (render_ad.py) plus make.fun's
// press-pack files used as they are — the brand badge overlaid from the
// first frame, and the referral end card over the last 2.5 s carrying
// referral code bpr1tvsc. Caption line and play code live in POST.json.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

const source = join(BOT_DIR, "VIDEO.json");
const target = join(OUTPUT_DIR, "VIDEO.json");

mkdirSync(OUTPUT_DIR, { recursive: true });

const raw = readFileSync(source, "utf8");
const video = JSON.parse(raw);
if (typeof video !== "object" || video === null || typeof video.url !== "string") {
  console.error("VIDEO.json must be an object with a string url");
  process.exit(1);
}

copyFileSync(source, target);
console.log(`VIDEO.json copied to ${target}: ${video.url}`);

// A quick sanity check for the grader's sake: the URL must name a TikTok
// video page, https://www.tiktok.com/@<handle>/video/<digits>. A short
// link or a photo post is refused by the house, so flag it loudly here
// instead of silently handing in a bad address.
if (!/^https:\/\/(www\.|m\.)?tiktok\.com\/@[^/]+\/video\/\d+$/.test(video.url)) {
  console.error(`warning: VIDEO.json url does not look like a TikTok video page: ${video.url}`);
}
