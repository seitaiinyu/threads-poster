#!/usr/bin/env python3
"""本人のYouTube動画を文字起こしして Obsidian の該当フォルダへ保存する。
使い方: python3 yt_transcribe.py <yt_list.txt> [最大本数]
- 腰痛/坐骨/膝 の日本語タイトルだけ対象。Obsidianに同名ファイルがあればスキップ
- 出力形式は既存ノートと同じ: タイトル / URL / Transcript: (mm:ss) 本文
"""
import os, sys, re, subprocess, glob
from faster_whisper import WhisperModel

VAULT = "/Users/takeuchiyuuki/Documents/Obsidian Vault"
YTDLP = os.path.expanduser("~/bin/yt-dlp")
FFMPEG = os.path.expanduser("~/bin/ffmpeg")
WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yt_work")
os.makedirs(WORK, exist_ok=True)

FOLDERS = [
    (re.compile(r"坐骨|座骨"), "Youtube 坐骨神経痛"),
    (re.compile(r"腰痛|ぎっくり|ヘルニア|狭窄|腰"), "Youtube 腰痛"),
    (re.compile(r"膝"), "Youtube 膝の痛み"),
]


def folder_for(title):
    if re.search(r"[A-Za-z]{4,}", title) and not re.search(r"[ぁ-んァ-ン]", title):
        return None  # 英語タイトルは除外
    for pat, name in FOLDERS:
        if pat.search(title):
            return name
    return None


def safe_name(title):
    t = re.sub(r'[\\/:*?"<>|]', "_", title).strip()
    return t[:120]


def already(folder, title):
    key = re.sub(r"\s+", "", title)[:25]
    for f in glob.glob(os.path.join(VAULT, folder, "*.md")):
        if re.sub(r"\s+", "", os.path.basename(f)).startswith(key[:15]):
            return True
    return False


def main():
    src = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    model = None
    done = 0
    for line in open(src, encoding="utf-8"):
        parts = line.rstrip("\n").split("|", 3)
        if len(parts) < 4:
            continue
        vid, dur, _, title = parts
        folder = folder_for(title)
        if not folder:
            continue
        if already(folder, title):
            continue
        try:
            if dur not in ("NA", "") and float(dur) > 1500:
                continue  # 25分超は後回し
        except ValueError:
            pass
        if done >= limit:
            break
        url = f"https://www.youtube.com/watch?v={vid}"
        wav = os.path.join(WORK, f"{vid}.wav")
        print(f"[{done+1}/{limit}] {title[:50]}", flush=True)
        if not os.path.exists(wav):
            r = subprocess.run([YTDLP, "-q", "--no-warnings", "-x", "--audio-format", "wav",
                                "--postprocessor-args", "ffmpeg:-ac 1 -ar 16000",
                                "--ffmpeg-location", os.path.dirname(FFMPEG),
                                "-o", os.path.join(WORK, f"{vid}.%(ext)s"), url],
                               capture_output=True, text=True)
            if not os.path.exists(wav):
                print("  DL失敗:", r.stderr[-200:].strip(), flush=True)
                continue
        if model is None:
            model = WhisperModel("small", device="cpu", compute_type="int8")
        segs, _ = model.transcribe(wav, language="ja", vad_filter=True, beam_size=5)
        lines = []
        for s in segs:
            lines.append(f"({int(s.start//60):02d}:{int(s.start%60):02d}) {s.text.strip()}")
        body = f"# {title}\n\n{url}\n\nTranscript:\n" + "\n".join(lines) + "\n"
        out = os.path.join(VAULT, folder, safe_name(title) + ".md")
        open(out, "w", encoding="utf-8").write(body)
        os.remove(wav)
        done += 1
        print(f"  保存: {folder}/{safe_name(title)[:40]}.md ({len(lines)}行)", flush=True)
    print(f"完了: {done}本", flush=True)


if __name__ == "__main__":
    main()
