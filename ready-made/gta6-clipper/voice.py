# Your voice on the clip: places your recorded line at AT seconds and ducks the game/streamer audio under it.
# Usage: python voice.py clip.mp4 line.wav AT out.mp4
# The line is what makes the clip yours (commentary = transformation). Video is copied untouched.
import subprocess, sys

def probe(p, what):  # duration of the file, or "audio" if it has an audio stream
    a = ["-select_streams", "a", "-show_entries", "stream=index"] if what == "audio" else ["-show_entries", "format=duration"]
    r = subprocess.run(["ffprobe", "-v", "error", *a, "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip()
    return bool(r) if what == "audio" else float(r or 0)

def main(clip, line, at, out):
    at = max(0.0, float(at)); dur = probe(clip, "dur")
    if not probe(line, "audio"): sys.exit("your recording has no sound in it: record again or pick another file")
    if dur and at > dur - 1: sys.exit(f"the voice starts at {at:.1f} s but the Short is only {dur:.1f} s long: pick an earlier moment")
    ms = int(at * 1000); fit = f",atrim=end={dur - at:.2f}" if dur else ""  # a line longer than the rest of the Short is cut at the end, not silently dropped
    graph = (f"[1:a]loudnorm=I=-16:TP=-1.5,aresample=48000,aformat=channel_layouts=stereo{fit},adelay={ms}|{ms},apad,asplit=2[v][sc];"
             + ("[0:a]" if probe(clip, "audio") else "anullsrc=r=48000:cl=stereo,") + "aresample=48000,aformat=channel_layouts=stereo[g];"
             # sidechain: the game drops about 15 dB only while you talk, returns over 0.4 s
             "[g][sc]sidechaincompress=threshold=0.015:ratio=20:attack=15:release=400:makeup=1[duck];"
             "[duck][v]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]")
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", clip, "-i", line, "-filter_complex", graph,
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.3f}" if dur else "86400", out], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode: sys.exit("could not add the voice: " + (r.stderr.strip().splitlines() or ["ffmpeg failed"])[-1][:200])
    print("ok", out)

if __name__ == "__main__":
    main(*sys.argv[1:5])
