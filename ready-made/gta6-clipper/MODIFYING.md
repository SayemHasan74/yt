# Shorts Studio local fork

This copy is maintained locally. The original application's MIT license permits modification and requires its copyright and permission notice to remain. Keep `LICENSE`, `fonts/OFL*.txt`, and `models/NOTICES.txt` with the code/assets.

## Source map

| File | Responsibility |
| --- | --- |
| `app.html` | Browser interface, translations, review and settings |
| `app.py` | Local HTTP API, job management and AI command integration |
| `watch.py`, `hunt.py`, `live.py`, `chat.py` | Downloading, discovery, live capture and chat signals |
| `transcribe.py` | Local Whisper transcription |
| `nopick.py`, `moments.py`, `vision.py`, `callbacks.py` | Candidate scoring and event signals |
| `clip.py`, `reframe.py`, `batch.py`, `formats.py`, `parts.py` | Editing, framing and rendering |
| `qc.py`, `peek.py` | Technical checks and frame previews |
| `themes.json`, `brand.example.json`, `sounds/`, `fonts/` | Rendering appearance and assets |
| `translate.py`, `voice.py`, `meme.py` | Optional translation, commentary and sounds |
| `ytstats.py`, `yt_panel.js`, `learn.py` | Optional YouTube statistics and channel learning |
| `SKILL.md`, `SKILL-REFERENCE.md` | Instructions given to the selected AI agent |

The launcher, `environment.sh`, settings, runtime, data, logs and workspace sit one directory above this source folder.

## Removed connections

- Upstream application updater and its remote manifests/download code (`update.py` removed).
- Startup/periodic update polling and remote release-note fetching.
- Feedback email endpoint, issue submission link, contact form and author-facing buttons.
- Author logo, named visual theme, default example watermark and affiliate links.
- Discount campaigns, partner copy, auto-post promotions and update announcements.

The old update and feedback API paths return HTTP 410 and cannot install code or send feedback. The local build version is read only from `version.json`. `CHANGELOG.md` records local changes.

The previous source is retained only in an offline ZIP under `../backups/`. It is not imported or executed. Replacing source from that archive would undo these changes. The old installer ZIP and obsolete patch were removed to avoid duplicate upstream copies.

## Remaining network use and permissions

Video downloading and chat require the selected platform's servers. User-selected Codex/other cloud AI tools send their prompts and inspected content to their provider. Local No AI mode avoids those agent calls; local Whisper transcription still runs.

Optional publishing uses your own Blotato account directly, with no referral link. Optional YouTube analytics use Google's APIs and your own keys/OAuth client. Translation downloads use the Argos model index when a language pack is missing. Model and Python dependency providers remain independent third parties.

The existing downloader can repair itself by upgrading yt-dlp after an extraction error; that is a dependency update, not an upstream app update. Review that behavior in `watch.py` if you want fully manual dependency updates too.

Removing author connections does not sandbox the program. It runs with your user account's permissions; the existing Codex tool-running mode also uses broad permissions. No claim of a complete security audit is made for the third-party runtime, dependencies or binary models.

## Editing and checks

Close the launcher, edit the relevant file, and reopen it. Keep source changes under version control or make local backups. Do not restore the upstream updater or replace this fork from the original distribution as an automatic repair.

Source/interface checks for this change do not download or render videos, invoke an AI, publish content, or schedule work. The review inventory and validation results are stored under `../settings/`.

## Current default stacked layout

`reframe.py` uses a fixed 432px (22.5%) header and 1488px (77.5%) lower video panel. `fit_facecam` preserves proportions on a generated violet/magenta gradient with a soft glow border. `gameplay_view` uses uniform cover scaling of actual source video, reaching all four lower-panel edges; no blur/transparent filler is composited. This supersedes the earlier 0.85-scale padded viewport: preserving that exact zoom reduction while filling the taller panel is not possible without cropping or distortion. Side content, including chat, can still be cropped by portrait framing. The hook is white on purple, persistent and unfaded. Existing original exports remain untouched; rejected revised outputs were deleted and the local render was stopped. Do not restart it until the revised layout is approved.

## Latest approved saved preferences
Workspace brand.json now selects padded gameplay at 0.85 cover scale, native-size facecam, and purple_glass. Padding and header blend blurred source footage with a violet/magenta gradient and slow subtle shimmer. This supersedes the earlier edge-to-edge/no-padding preference. The foreground webcam is copied without resizing. The local publish-three task writes all working files under workspace/runs and copies only validated final MP4s into the clean delivery folder recorded in settings/latest_render.json.
