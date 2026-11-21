"""Read existing CLI logs and export an audit; never invoke an AI or media worker."""
import collections, csv, datetime, hashlib, json, pathlib, re
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = pathlib.Path('/Users/ghost/.codex/sessions/2026/11/21/rollout-2026-11-21T00-41-26-01a1fa43-7091-7920-9f3f-81b9234f2fd9.jsonl')
FAILED = pathlib.Path('/Users/ghost/.codex/sessions/2026/11/20/rollout-2026-11-20T21-38-53-01a1f99c-5124-7a61-bd44-54e2517ec03b.jsonl')
OUT = ROOT / 'reports/codex-usage-audit-2026-11-21'
CATEGORIES = {
 'BOOT': ('Read instructions, rules, and source code', 'Local preflight + a small versioned AI contract; no repeated source-code browsing.'),
 'DOWNLOAD': ('Start/retry downloads and inspect source metadata', 'Local downloader with bounded retries and a source cache.'),
 'DOWNLOAD_REPAIR': ('Repair failed/slow download workflow', 'Prebuilt fallback; ask for help only after deterministic recovery fails.'),
 'POLL': ('Check logs, processes, sizes, or progress', 'Local event/status watcher; no model response for an unchanged state.'),
 'WAIT': ('Sleep or resume a pending tool execution', 'OS/process waiting outside the AI session.'),
 'TRANSCRIBE': ('Start/refine local speech transcription', 'Local Whisper worker; selected-region refinement can be queued from JSON.'),
 'CANDIDATES': ('Generate or widen the candidate shortlist', 'Local scorer with an explicit per-source cap and cached shortlist.'),
 'CONTEXT': ('Read nearby transcript context', 'Keep AI judgment, but include a bounded context package in the selection request.'),
 'SELECT': ('Choose stories, replace picks, write hooks/titles and boundaries', 'Keep AI; return a batch of structured editorial decisions in one request.'),
 'PREVIEW': ('Generate visual contact sheets / source peeks', 'Generate bounded preview assets locally before any visual review.'),
 'VISUAL': ('Inspect images for story and framing judgment', 'Optional batched AI review of ambiguous picks; local geometry checks otherwise.'),
 'VALIDATE': ('Run pick eligibility / timing checks', 'Validate structured picks locally before starting a render.'),
 'RENDER': ('Start, stop, restart or recut local render jobs', 'Local queue consumes approved picks and a locked visual preset.'),
 'REPAIR': ('Diagnose, patch and test runtime code/platform failures', 'Resolve during maintenance/preflight; do not let a normal clipping job edit app code.'),
 'TIMING': ('Audit final spoken payoff and kept source spans', 'Local word/span assertions; AI only for unresolved story semantics.'),
 'CAPTIONS': ('Correct caption wording / filter unrelated speech', 'AI or human judgment when ambiguous; apply approved corrections locally.'),
 'QC': ('Run/read automatic picture, audio and duration checks', 'Local QC and a concise exception packet; no model for each successful check.'),
 'BOOKKEEP': ('Record used moments and prevent duplicate selection', 'Local transactional cache/manifest update.'),
 'DELIVER': ('Build final manifests, covers, summaries and file checks', 'Local packaging and delivery; AI only if new editorial copy is requested.'),
 'APP': ('Start or verify the local review web app', 'Local service manager and HTTP health check.'),
}

# One reviewed entry per outer agent tool call. First tag is the primary purpose;
# additional tags preserve mixed actions instead of pretending each call does one job.
ANNOTATIONS = '''
1|BOOT|Read the clipper skill and complete workflow instructions.
2|DOWNLOAD,BOOT|List installed files; launch watch.py for the requested YouTube half-hour.
3|BOOT,POLL|Inspect watch.py and clip_rules.json; poll the first watcher process.
4|DOWNLOAD_REPAIR,BOOT|Try upgrading yt-dlp; inspect candidate/render constraints.
5|DOWNLOAD|Retry watch.py for the same source window.
6|REPAIR,POLL|Read the failed watcher result; inspect transcription configuration and source files.
7|DOWNLOAD|Run a verbose standalone audio-section download to diagnose the failure.
8|POLL|Read the download error log.
9|DOWNLOAD|Retry the audio download without the failing match-filter option.
10|BOOT,POLL|Read peek.py and batch.py; poll download and read its tail.
11|DOWNLOAD,BOOT|Inspect download/lite-mode configuration; query channel and duration metadata.
12|POLL|Check download progress and collect metadata-command output.
13|POLL|Inspect yt-dlp/FFmpeg processes.
14|DOWNLOAD_REPAIR|Terminate slow downloader processes; write and start an eight-part parallel audio downloader.
15|BOOT,POLL|Read transcription/watch code; inspect parallel-download progress.
16|DOWNLOAD_REPAIR|Revise the fallback downloader metadata extraction and restart it.
17|POLL,APP|Read part-download progress and inspect review-app startup options.
18|POLL|Poll fallback downloader and inspect audio-part size/log.
19|POLL|Poll fallback downloader and inspect audio-part size/log again.
20|POLL|Poll fallback downloader and inspect growing cache size.
21|BOOT,POLL|Read candidate and QC code while polling downloader.
22|POLL|Resume downloader session; inspect part size and completion messages.
23|WAIT|Wait for a yielded orchestration cell.
24|POLL|Resume downloader session and inspect progress again.
25|WAIT|Wait for another yielded orchestration cell.
26|WAIT|Sleep 45 seconds before the next progress check.
27|POLL|Check cached audio sizes and downloader completion.
28|TRANSCRIBE,DOWNLOAD|Launch watch.py on cached audio to transcribe; probe audio duration.
29|POLL|Read transcription progress; inspect available RAM and disk space.
30|WAIT|Sleep 45 seconds during transcription.
31|POLL|Check transcription log and worker CPU/process status.
32|WAIT|Sleep another 45 seconds during transcription.
33|POLL|Check transcript files/log and collect transcription-process output.
34|CANDIDATES|Generate the Smart shortlist and read source metadata.
35|CONTEXT|Read six bounded transcript regions around potential stories.
36|SELECT,CONTEXT,PREVIEW|Read more context; write five provisional picks/hooks; launch source peeks.
37|POLL,BOOT|Check available model files and peek progress.
38|POLL|Read source-peek log.
39|BOOT,POLL|Inspect clip download/snap behavior and peek progress.
40|WAIT|Sleep 30 seconds while source peeks run.
41|POLL|Check generated peek images and process output.
42|VISUAL|Inspect four source contact sheets: family, giveaway, race and rating.
43|CANDIDATES|Regenerate 30 candidates with per-source cap raised to 30.
44|CONTEXT,SELECT,PREVIEW|Read three other transcript regions; prepare replacement dog/helicopter/driving peeks.
45|POLL|Check replacement-peek progress and generated files.
46|WAIT|Sleep 30 seconds during replacement peeks.
47|POLL|Check replacement-peek log and collect process output.
48|VISUAL|Inspect dog, helicopter and driving source contact sheets.
49|TRANSCRIBE|Write/start selected-region Whisper-small refinement and merge corrected word timings.
50|BOOT,POLL|Inspect renderer silence-cut/squeeze code; check refinement progress.
51|POLL|Check refinement log and review files.
52|POLL|Check Whisper-small cache size and Python process activity.
53|WAIT|Sleep 45 seconds during model/refinement work.
54|POLL|Check refinement progress and process output.
55|POLL|Locate Whisper download cache and incomplete model files.
56|POLL|Read downloaded Whisper model byte counts.
57|POLL|Check refinement log and produced review transcripts.
58|CONTEXT,CAPTIONS|Read refined dog/family/race transcript wording.
59|CONTEXT,CAPTIONS,POLL|Read wider dog context and refined driving/rating text; collect refinement completion.
60|SELECT,PREVIEW|Revise dog story setup/bounds and generate a new source peek.
61|SELECT,VALIDATE,RENDER|Write first four story picks, hooks, titles and boundaries; validate and launch batch rendering.
62|RENDER|Stop the initial rendering process tree to adjust timing.
63|BOOT,POLL|Inspect local pick checks and render log.
64|BOOT|Inspect transcript/talk-duration validation and partial output files.
65|BOOT|Read callback/compilation format guidance and implementation.
66|BOOT|Inspect minimum-length, silence-cut and sentence-snap behavior.
67|CONTEXT|Read extra family setup and post-rating transcript context.
68|SELECT,VALIDATE,PREVIEW|Set family callback parts and driving start; rerun dog peek and pick validation.
69|RENDER,PREVIEW|Launch final peeks and restart first-four rendering with two workers.
70|POLL|Read dog, batch-render and final-peek progress logs.
71|WAIT|Sleep 45 seconds during rendering.
72|POLL|Read render/peek progress and list current outputs.
73|REPAIR,VISUAL|Diagnose invalid-pixel-size render failures; inspect font code and dog contact sheet.
74|BOOT,REPAIR|Inspect QC/result handling and clip initialization.
75|REPAIR|Reproduce the font failure with one direct render and inspect work files.
76|REPAIR|Read the direct-render font error traceback.
77|REPAIR|Inspect renderer self-tests and font-loading paths.
78|REPAIR|Inspect clip.py CLI entry point and final code lines.
79|REPAIR|Probe Apple Color Emoji supported pixel sizes.
80|REPAIR|Back up and patch Apple emoji font size; run renderer checks.
81|RENDER,REPAIR|Read repair-test status; restart the first-four batch after the font fix.
82|TRANSCRIBE,SELECT,PREVIEW|Refine the fifth story with Whisper; write provisional kind-of pick and request its source peek.
83|POLL|Read batch/fifth-transcription progress and output listing.
84|POLL|Inspect render cache sizes, fifth transcript file and process CPU activity.
85|WAIT|Sleep 35 seconds during rendering/refinement.
86|CONTEXT,POLL|Read fifth-story refined transcript and progress logs.
87|SELECT,VISUAL,VALIDATE|Inspect fifth contact sheet; write final fifth pick/hook/title and combined picks; validate it.
88|BOOT,POLL|Inspect stack-layout implementation and batch progress.
89|RENDER,SELECT|Adjust fifth start; create a custom render script overriding TOP_H to 1280; render fifth clip and cover.
90|POLL|Inspect fifth-render log, worker processes and intermediate cache size.
91|POLL|Inspect specific render process identities and elapsed times.
92|WAIT|Sleep 45 seconds during rendering.
93|POLL|Read batch/fifth-render progress and current outputs.
94|QC,VISUAL|Inspect first finished cover and launch its automatic QC.
95|POLL,QC|Read render progress and first-clip QC result.
96|WAIT|Sleep 45 seconds during rendering.
97|POLL|Read render logs and output listing.
98|TIMING,VISUAL|Probe race clip duration/kept spans and inspect its cover.
99|VISUAL,CAPTIONS|Extract/read a gameplay-subtitle frame to check driving dialogue wording.
100|POLL|Read remaining render progress and output files.
101|TIMING,CAPTIONS|Inspect fifth-story word timings and driving render metadata.
102|TIMING,POLL|Compare fifth chosen range, downloaded/intermediate durations and batch log.
103|REPAIR|Inspect reframe/render/tail code to diagnose missing endings.
104|TIMING|Compare every render's requested endpoint with the last retained source frame, including callback parts.
105|REPAIR,POLL|Inspect tail trimming and remaining render progress.
106|TIMING,POLL|Read rating's final kept spans and batch result.
107|REPAIR|Patch tail trimming so later quieter dialogue survives; run a targeted check.
108|CAPTIONS,RENDER,SELECT|Correct banged/banked and remove radio captions; revise driving start; write/start payoff recut script.
109|QC,VISUAL|Inspect combined output contact sheet and automatic QC results.
110|WAIT|Sleep 45 seconds during payoff recuts.
111|POLL|Read recut logs for race and driving clips.
112|REPAIR,POLL|Inspect stale self-test expectations and fifth recut progress.
113|REPAIR|Update tail-trim self-tests for the new dialogue-preservation rule and run checks.
114|RENDER,REPAIR|Make recut script accept explicit clip numbers; restart race/driving recuts; check repair status.
115|WAIT|Sleep 45 seconds during recuts.
116|POLL|Inspect fifth, race and driving recut logs.
117|QC,VISUAL,PREVIEW|Run fifth-clip QC; generate and inspect a final multi-frame contact sheet.
118|POLL,QC|Read fifth QC and recut progress.
119|BOOKKEEP,POLL|Record used source/story intervals; inspect remaining recut/QC logs.
120|WAIT|Sleep 35 seconds during final recuts.
121|POLL|Inspect remaining race/driving recut progress.
122|QC,TIMING|Run driving QC and verify the final heard transcript words for clips three through five.
123|POLL,QC|Read driving QC, remaining recut logs and render process activity.
124|WAIT|Sleep 45 seconds while final race recut finishes.
125|POLL|Read race recut progress and job log.
126|POLL|Check race output size and remaining FFmpeg activity.
127|DELIVER,QC,PREVIEW|Run final race QC; write/start final media audit, contact sheets, cover and sidecar preparation.
128|POLL,APP,QC|Collect final-review output, read race QC and inspect app startup path.
129|DELIVER,VISUAL,QC|Inspect final overview; assert five usable outputs; write results manifest and QC/story-review notes.
130|APP|Start the local review app in a detached process and record its PID.
131|APP|Read review-app startup log and verify its localhost HTTP response.
'''


def local(t):
    return datetime.datetime.fromisoformat(t.replace('Z', '+00:00')).astimezone(ZoneInfo('Asia/Dhaka')).isoformat(timespec='milliseconds')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = [json.loads(line) for line in SOURCE.open()]
    annotations = {}
    for line in ANNOTATIONS.strip().splitlines():
        num, tags, purpose = line.split('|', 2)
        annotations[int(num)] = (tags.split(','), purpose)
    calls, usages, outputs = [], [], {}
    pending = []
    # Every record is parsed, including tool outputs; private reasoning text is
    # deliberately neither exported nor reproduced in this task-purpose audit.
    for line_num, d in enumerate(data, 1):
        a = d.get('payload', {})
        if d['type'] == 'response_item' and a.get('type') in ('custom_tool_call', 'function_call'):
            num = len(calls) + 1
            tags, purpose = annotations[num]
            command = a.get('input', a.get('arguments', ''))
            calls.append(dict(call=num, source_line=line_num, timestamp_dhaka=local(d['timestamp']),
                              tool=a['name'], primary=tags[0], tags=';'.join(tags), purpose=purpose,
                              call_id=a['call_id'], command=command))
            pending.append(num)
        if d['type'] == 'response_item' and a.get('type') in ('custom_tool_call_output', 'function_call_output'):
            outputs[a['call_id']] = a.get('output')
        if d['type'] == 'token_usage_record':
            usages.append(dict(response=len(usages)+1, source_line=line_num, timestamp_dhaka=local(d['timestamp']),
                               response_id=a['response_id'], calls=list(pending), **a['usage']))
            pending = []
    assert len(calls) == len(annotations) == 131
    assert len(usages) == len({r['response_id'] for r in usages}) == 132
    assert sum(len(u['calls']) for u in usages) == 131
    assert sum(not u['calls'] for u in usages) == 1
    image_count, text_chars, primitive_sites = 0, 0, collections.Counter()
    for c in calls:
        o = outputs[c['call_id']]
        blocks = o if isinstance(o, list) else [dict(type='input_text', text=str(o))]
        c['output_images'] = sum(b.get('type') == 'input_image' for b in blocks)
        c['output_text_characters'] = sum(len(b.get('text', '')) for b in blocks if b.get('type') == 'input_text')
        c['output_blocks'] = len(blocks)
        image_count += c['output_images']; text_chars += c['output_text_characters']
        primitive_sites.update(re.findall(r'\btools\.([a-z_]+)\s*\(', c['command']))
        u = next(u for u in usages if c['call'] in u['calls'])
        for key in ('input_tokens', 'cached_input_tokens', 'output_tokens', 'total_tokens'):
            c[key] = u[key]
    counts = collections.Counter(c['primary'] for c in calls)
    tag_counts = collections.Counter(t for c in calls for t in c['tags'].split(';'))
    tokens = collections.Counter()
    for u in usages:
        tokens.update({k: v for k, v in u.items() if k.endswith('_tokens')})
    final_usage = next(d['payload']['info']['total_token_usage'] for d in reversed(data)
                       if d['type'] == 'event_msg' and d['payload'].get('type') == 'token_count'
                       and d['payload'].get('info'))
    assert dict(tokens) == final_usage
    assert sum(counts.values()) == 131
    assert sum(tokens[k] for k in ('input_tokens', 'output_tokens')) == tokens['total_tokens']
    def write_csv(name, rows, fields):
        with (OUT / name).open('w', newline='') as f:
            w = csv.DictWriter(f, fields, extrasaction='ignore'); w.writeheader(); w.writerows(rows)
    write_csv('tool-call-ledger.csv', calls, ['call', 'timestamp_dhaka', 'primary', 'tags', 'purpose', 'tool', 'source_line', 'call_id', 'input_tokens', 'cached_input_tokens', 'output_tokens', 'total_tokens', 'output_images', 'output_text_characters'])
    response_rows = []
    for u in usages:
        response_rows.append(dict(u, calls=';'.join(map(str,u['calls'])), primary=calls[u['calls'][0]-1]['primary'] if u['calls'] else 'FINAL',
                                  purpose=calls[u['calls'][0]-1]['purpose'] if u['calls'] else 'Final delivery message listing the five Shorts, QC results and review URL.',
                                  uncached_input_tokens=u['input_tokens']-u['cached_input_tokens']))
    write_csv('model-response-usage.csv', response_rows, ['response','timestamp_dhaka','primary','calls','purpose','response_id','source_line','input_tokens','cached_input_tokens','uncached_input_tokens','output_tokens','reasoning_output_tokens','total_tokens'])
    metrics = dict(source_log=str(SOURCE), source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                   source_lines=len(data), source_bytes=SOURCE.stat().st_size,
                   failed_session_log=str(FAILED), started_dhaka=local(data[0]['timestamp']), ended_dhaka=local(data[-1]['timestamp']),
                   duration_seconds=(datetime.datetime.fromisoformat(data[-1]['timestamp'].replace('Z','+00:00'))-datetime.datetime.fromisoformat(data[0]['timestamp'].replace('Z','+00:00'))).total_seconds(),
                   cli_sessions_successful=1, cli_sessions_failed_before_work=1, model_responses=len(usages), outer_tool_calls=len(calls),
                   outer_tools=dict(collections.Counter(c['tool'] for c in calls)), primary_counts=dict(counts), overlapping_tag_counts=dict(tag_counts),
                   tokens=dict(tokens), output_images=image_count, tool_output_text_characters=text_chars,
                   nested_tool_syntax_sites=dict(primitive_sites), final_responses_without_tools=1)
    (OUT / 'audit-metrics.json').write_text(json.dumps(metrics, indent=2)+'\n')
    lines = ['# Complete tool-call inventory', '', 'Each row maps to the original session log. Tags may overlap. Commands and private model reasoning are not reproduced.', '']
    for c in calls:
        lines += [f"- **{c['call']:03d} — {c['primary']}** ({c['timestamp_dhaka']}, source line {c['source_line']}): {c['purpose']} Additional tags: {c['tags']}. "
                  f"Response usage: {c['input_tokens']:,} input ({c['cached_input_tokens']:,} cached), {c['output_tokens']:,} output tokens."]
    (OUT / 'complete-call-inventory.md').write_text('\n'.join(lines)+'\n')
    table = ['| Task type | Primary calls | Calls involving this type | Treatment in a lower-usage pipeline |','|---|---:|---:|---|']
    for tag, (label, recommendation) in CATEGORIES.items():
        table.append(f'| {tag}: {label} | {counts[tag]} | {tag_counts[tag]} | {recommendation} |')
    (OUT / 'category-table.md').write_text('\n'.join(table)+'\n')
    print(json.dumps(metrics, indent=2))


if __name__ == '__main__': main()
