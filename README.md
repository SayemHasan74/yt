# Shorts Studio — current local fork

Source backup of the current Shorts Studio app maintained on an Apple M4 MacBook Air.
This snapshot preserves the existing clipping workflow. The proposed checkpoint-only
AI rebuild has **not** been implemented.

## Included

- The dashboard and Python pipeline in `ready-made/gta6-clipper/`.
- Required fonts, sound assets, small face/object tracking models and their notices.
- The Mac launchers, environment setup, render helpers and local verification scripts.
- Saved visual preferences in `ready-made/workspace/brand.json`.
- A credential-free settings example at `ready-made/settings/clipper.env.example`.

## Saved rendering preferences

- Fixed stacked portrait composition, 1080 × 1920.
- Native-size, unstretched facecam in the top panel.
- Padded gameplay at 0.85 cover scale.
- One consistent purple backing across the header and padding, with subtle shimmer.
- A compact hook visible for the entire clip.
- Existing short editing and silence cutting, including multi-part story edits.

These settings do not mean every source has the same facecam coordinates. A new
source still needs valid camera detection or appropriate source coordinates.

## Current workflow

With Codex selected, the app launches a separate Codex CLI job to manage preparation,
story selection, rendering and quality checks. Whisper, Python and FFmpeg process
media locally. The source also retains the app's No AI mode and other existing
features. The lower-usage checkpoint runner discussed during planning is not part
of this version.

## Running / restoring

On the original configured Mac, double-click `ready-made/Open Clipper.command`.
Keep its Terminal window open; the dashboard normally opens at localhost:8765.

This repository is a **source backup, not a self-contained installation**. It excludes
the machine-specific Python environment, bundled runtime binaries, Whisper models,
credentials, source videos and finished clips. Existing launchers expect the local
runtime layout described in `ready-made/START HERE.txt` and may contain
machine-specific paths. A fresh clone needs those dependencies configured before
it can run. Windows packaging/migration has not been performed or verified.

Python package requirements are in `ready-made/gta6-clipper/requirements*.txt`.
The app also needs FFmpeg/FFprobe, its required Whisper models, and a configured
AI provider if using AI selection. Read `INSTALL.md` and `MODIFYING.md` in the app
folder for the existing dependency and source documentation.

The local settings example contains no account keys. On a newly configured machine,
copy it to `ready-made/settings/clipper.env` and configure credentials locally.
Never commit that private file.

## Deliberately excluded

- Downloaded source video/audio and exported Shorts.
- Job runs, transcripts, private logs, account state and analytics.
- API keys, browser cookies, private settings and authentication files.
- Python environments, package caches, node_modules, large Whisper/Qwen models,
  downloaded installers and machine-specific runtime binaries.
- Historical PC handoff copies, offline backups, and private audit/review reports.

The `.gitignore` uses an allowlist so these items do not enter a normal commit.

## License and maintenance

The app's original MIT notice is preserved in `ready-made/gta6-clipper/LICENSE`.
Font and model notices are retained with their assets. Upstream updating and author
feedback/promotional integrations were removed in this local fork; maintenance is
manual. See `CHANGELOG.md` and `MODIFYING.md` in the app folder for prior changes.
