#!/bin/zsh
# Terminal-only downloader for public/authorized YouTube, Instagram, and Facebook videos.

set -u

SCRIPT_DIR="${0:A:h}"
PYTHON="$SCRIPT_DIR/gta6-clipper/.venv/bin/python"
DEFAULT_OUTPUT="$HOME/Downloads"

if [[ ! -x "$PYTHON" ]]; then
  print -u2 "The local downloader is missing. Expected: $PYTHON"
  exit 1
fi

print ""
print "Video Downloader"
print "Public or authorized YouTube / Instagram / Facebook links only."
print "Downloads go to: $DEFAULT_OUTPUT"
print ""

while true; do
  read -r "url?Paste a video link (or press Return to quit): "
  url="${url## ##}"
  url="${url%% ##}"

  if [[ -z "$url" ]]; then
    break
  fi

  if [[ ! "$url" =~ '^https?://' ]]; then
    print -u2 "That does not look like a web link. Paste the full https:// link."
    continue
  fi

  print ""
  read -r "output_dir?Save folder [Return = $DEFAULT_OUTPUT]: "
  output_dir="${output_dir## ##}"
  output_dir="${output_dir%% ##}"
  [[ -z "$output_dir" ]] && output_dir="$DEFAULT_OUTPUT"
  output_dir="${output_dir/#\~/$HOME}"

  if [[ ! -d "$output_dir" ]]; then
    print "Creating: $output_dir"
    mkdir -p "$output_dir" || { print -u2 "Could not create that folder."; continue; }
  fi

  print ""
  print "Starting download — progress appears below."
  print ""

  "$PYTHON" -m yt_dlp \
    --no-playlist \
    --newline \
    --progress \
    --format 'bv*+ba/b' \
    --merge-output-format mp4 \
    --remux-video mp4 \
    --output "$output_dir/%(title).180B [%(id)s].%(ext)s" \
    "$url"
  status=$?

  print ""
  if [[ $status -eq 0 ]]; then
    print "Done. Saved in: $output_dir"
  else
    print -u2 "Download failed (code $status)."
    print -u2 "The post may be private, login-only, unavailable, DRM-protected, or the site may have changed."
  fi
  print ""
done

print "Downloader closed."
read -r '?Press Return to close this Terminal window. '
