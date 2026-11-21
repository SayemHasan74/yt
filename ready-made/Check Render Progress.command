#!/bin/zsh
ROOT="$(cd -- "$(dirname -- "$0")" && pwd)"
"$ROOT/gta6-clipper/.venv/bin/python" - "$ROOT" <<'PY'
from pathlib import Path
import json,sys,os
root=Path(sys.argv[1]);spec=json.loads((root/'settings/latest_render.json').read_text());r=Path(spec['run']);dest=Path(spec['destination'])
s=r/'render_status.json';d=json.loads(s.read_text()) if s.exists() else {'stage':'Starting'}
print('\nSTATUS:',d['stage']);print('Updated:',d.get('updated',''));print('Finished videos:',sum((dest/n).exists() for n in spec['filenames']), '/', len(spec['filenames']));print('Clean folder:',dest)
try:os.kill(int((r/'render.pid').read_text()),0);print('Local task: running')
except (ProcessLookupError,FileNotFoundError):print('Local task: exited — see status above')
if d.get('error'):print('Error:',d['error'])
f=r/'render.log'
if f.exists():print('\nLatest render log:\n'+'\n'.join(f.read_text(errors='replace').splitlines()[-5:]))
PY
read '?Press Return to close. Rendering continues separately.'
