#!/bin/zsh
# Double-click this file to open the terminal-only video downloader.
SCRIPT_DIR="${0:A:h}"
LOCAL_DOWNLOADER="$SCRIPT_DIR/download-video.sh"
PROJECT_DOWNLOADER='/Users/ghost/My Computer/Local Disk E/YT Shorts/fresh-saved-repo/ready-made/download-video.sh'

# The launcher can be copied to Desktop; the real downloader stays in the project.
if [[ -x "$LOCAL_DOWNLOADER" ]]; then
  exec "$LOCAL_DOWNLOADER"
elif [[ -x "$PROJECT_DOWNLOADER" ]]; then
  exec "$PROJECT_DOWNLOADER"
else
  print -u2 'Could not find download-video.sh in the project.'
  print -u2 'Open the launcher from the ready-made folder, or restore the project folder.'
  read -r '?Press Return to close. '
fi
