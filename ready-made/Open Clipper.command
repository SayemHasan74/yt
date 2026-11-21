#!/bin/zsh
READY_MADE="$(cd -- "$(dirname -- "$0")" && pwd)"
export READY_MADE
source "$READY_MADE/environment.sh"
cd "$READY_MADE/workspace" || exit 1
mkdir -p "$READY_MADE/tmp" "$READY_MADE/logs"
echo 'Shorts Studio — keep this window open while using the app.'
echo 'The browser opens automatically. Press Control+C here to stop.'
echo "Your runs and Shorts: $READY_MADE/workspace/runs"
"$READY_MADE/gta6-clipper/.venv/bin/python" -u "$READY_MADE/gta6-clipper/app.py" "$READY_MADE/workspace" 2>&1 | tee -a "$READY_MADE/logs/app.log"
result=${pipestatus[1]}
if [[ $result -ne 0 && $result -ne 130 ]]; then
  echo "Clipper stopped with code $result. See ready-made/logs/app.log."
  read '?Press Return to close.'
fi
