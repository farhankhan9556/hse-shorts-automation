import os
import random
import subprocess
import requests
from pathlib import Path

# =========================
# SETTINGS
# =========================

API_KEY = os.environ.get("PEXELS_API_KEY")

if not API_KEY:
    raise RuntimeError("PEXELS_API_KEY is missing")

OUT = Path("assets")
OUT.mkdir(parents=True, exist_ok=True)

SOURCE = OUT / "source.mp4"
VOICE = OUT / "voice.mp3"
FINAL = OUT / "hse_short.mp4"

# =========================
# HSE TOPICS
# =========================

topics = [
    {
        "search": "construction worker safety helmet",
        "title": "WEAR YOUR HARD HAT",
        "script": "Before entering a construction site, always wear your safety helmet. A hard hat can protect you from serious head injuries."
    },
    {
        "search": "construction worker ladder safety",
        "title": "LADDER SAFETY",
        "script": "Before climbing a ladder, check that it is stable and secure. Never rush. Three points of contact can prevent a serious fall."
    },
    {
        "search": "construction worker PPE",
        "title": "USE THE RIGHT PPE",
        "script": "Safety starts with the right PPE. Wear your helmet, safety shoes, gloves, and eye protection before starting the job."
    },
    {
        "search": "construction site worker safety",
        "title": "STOP AND CHECK",
        "script": "Never start a task without checking the hazards. Stop, assess the risk, and make sure the controls are in place."
    },
    {
        "search": "industrial worker safety",
        "title": "SAFETY FIRST",
        "script": "A safe job starts before the work begins. Identify the hazards, follow the procedure, and never take unnecessary risks."
    }
]

topic = random.choice(topics)

print("================================")
print("TODAY'S HSE TOPIC")
print(topic["title"])
print("================================")

# =========================
# SEARCH PEXELS
# =========================

headers = {
    "Authorization": API_KEY
}

response = requests.get(
    "https://api.pexels.com/v1/videos/search",
    headers=headers,
    params={
        "query": topic["search"],
        "orientation": "portrait",
        "size": "medium",
        "per_page": 15
    },
    timeout=30
)

response.raise_for_status()

videos = response.json().get("videos", [])

if not videos:
    raise RuntimeError("No Pexels video found")

# Randomize the result so every day is less repetitive
video = random.choice(videos)

files = video.get("video_files", [])

portrait = [
    f for f in files
    if f.get("width", 0) > 0
    and f.get("height", 0) > 0
    and f["height"] >= f["width"]
]

if portrait:
    files = portrait

files.sort(
    key=lambda f: f.get("width", 0) * f.get("height", 0),
    reverse=True
)

video_url = files[0]["link"]

print("Downloading Pexels footage...")

with requests.get(
    video_url,
    stream=True,
    timeout=120
) as r:

    r.raise_for_status()

    with open(SOURCE, "wb") as f:
        for chunk in r.iter_content(1024 * 1024):
            if chunk:
                f.write(chunk)

print("Source video downloaded")

# =========================
# CREATE NATURAL VOICE
# =========================

print("Creating voice...")

subprocess.run(
    [
        "edge-tts",
        "--voice",
        "en-US-GuyNeural",
        "--text",
        topic["script"],
        "--write-media",
        str(VOICE)
    ],
    check=True
)

print("Voice created")

# =========================
# CREATE SUBTITLE FILE
# =========================

subtitle = OUT / "captions.srt"

words = topic["script"].split()

# Split into short caption groups
groups = []

for i in range(0, len(words), 6):
    groups.append(" ".join(words[i:i + 6]))

duration = 14.0
part = duration / len(groups)

with open(subtitle, "w", encoding="utf-8") as f:

    for i, text in enumerate(groups):

        start = i * part
        end = min((i + 1) * part, duration)

        def timestamp(seconds):
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds - int(seconds)) * 1000)
            return f"{h:02}:{m:02}:{s:02},{ms:03}"

        f.write(f"{i + 1}\n")
        f.write(f"{timestamp(start)} --> {timestamp(end)}\n")
        f.write(f"{text.upper()}\n\n")

print("Captions created")

# =========================
# CREATE 1080x1920 SHORT
# =========================

print("Rendering final HSE Short...")

filter_complex = (
    "[0:v]"
    "scale=1080:1920:force_original_aspect_ratio=increase,"
    "crop=1080:1920,"
    "setsar=1,"
    "subtitles=assets/captions.srt:"
    "force_style='FontName=DejaVu Sans,"
    "FontSize=20,"
    "Bold=1,"
    "PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,"
    "Outline=4,"
    "Shadow=2,"
    "Alignment=2,"
    "MarginV=180'"
    "[v]"
)

subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-i",
        str(SOURCE),
        "-i",
        str(VOICE),
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        "-map",
        "1:a",
        "-t",
        "15",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-shortest",
        str(FINAL)
    ],
    check=True
)

print("================================")
print("HSE SHORT CREATED SUCCESSFULLY")
print(f"File: {FINAL}")
print("================================")
