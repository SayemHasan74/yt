# Local changes

## 1.0.14-local.1

- Fixed saved Codex selection on fresh workspaces and prevented a stale hidden Claude selector from determining the run provider.

- Removed upstream update code, polling and remote release notes.
- Removed author feedback submission and issue links.
- Replaced author logo, theme names and example watermark.
- Removed affiliate links, discount promotions and promotional banners.
- Preserved the MIT license and third-party notices.
- Clipping, AI provider selection, downloads and optional user-configured publishing remain available.

## Default layout adjustment

- Set stacked layout to 30% facecam / 70% gameplay.
- Preserve facecam aspect ratio, cap enlargement at 2x, and use purple padding.
- Keep a cropped gameplay view with subject scale reduced by 15% relative to the legacy stack.
- Keep the hook at the seam for the full clip, including callback parts.
- Disable automatic facecam punch-ins on stacked renders.
- Include renderer code in part-cache identity so old layout parts are not reused.
- Verified geometry, hook duration, and a short synthetic encode; existing Shorts were not re-rendered.

### More gameplay space

- Reduced header from 576px to 432px, reclaiming 25% of its height; gameplay region is now 77.5%.
- Replaced purple source-edge padding in gameplay with soft video-derived fill through the bottom edge.
- Kept sharp gameplay at 0.85 scale and facecam aspect ratio unchanged.
- Synthetic geometry/encode and bottom-edge checks passed.

### Rejected preview replaced — code only

- Stopped the revised-three render and deleted its outputs; cached sources retained.
- Replaced flat header with violet/magenta gradient and soft glow border.
- Replaced gameplay filler with uniform cover framing edge to edge.
- Removed the hook fade and enforced white text on purple for stacked renders.
- Retained fixed panels and proportional facecam. No new production render started.

### Saved wider purple-glass preference

- Saved padded 0.85 gameplay, native facecam, translucent-style purple padding and slow purple shimmer as workspace defaults.
- Added a local-only three-video task and clean MP4-only delivery folder.
- No cloud AI, new downloads or new transcription are used for this render task.
