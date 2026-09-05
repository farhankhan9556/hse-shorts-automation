import os
import random
import subprocess
import requests
import wave
import math
from pathlib import Path
from datetime import date

API_KEY = os.environ.get("PEXELS_API_KEY")

if not API_KEY:
    raise RuntimeError("PEXELS_API_KEY is missing")

OUT = Path("assets")
OUT.mkdir(parents=True, exist_ok=True)

TODAY = date.today()

topics = [
    {
        "search": "construction worker hard hat safety",
        "title": "WEAR YOUR HARD HAT",
        "script": "Before entering a construction site, always wear your safety helmet. A hard hat can protect you from serious head injuries.",
        "hashtags": "#HSE #Safety #HardHat #ConstructionSafety #WorkplaceSafety"
    },
    {
        "search": "construction ladder safety worker",
        "title": "LADDER SAFETY",
        "script": "Before climbing a ladder, check that it is stable and secure. Maintain three points of contact and never rush the job.",
        "hashtags": "#HSE #LadderSafety #SafetyFirst #ConstructionSafety #WorkplaceSafety"
    },
    {
        "search": "construction worker PPE safety",
        "title": "USE THE RIGHT PPE",
        "script": "Safety starts with the right PPE. Wear your helmet, safety shoes, gloves and eye protection before starting the job.",
        "hashtags": "#HSE #PPE #SafetyFirst #ConstructionSafety #WorkplaceSafety"
    },
    {
        "search": "construction site hazard inspection",
        "title": "STOP AND CHECK",
        "script": "Never start a task without checking the hazards. Stop, assess the risk and make sure the controls are in place.",
        "hashtags": "#HSE #RiskAssessment #Safety #ConstructionSafety #WorkplaceSafety"
    },
    {
        "search": "construction worker working at height",
        "title": "WORKING AT HEIGHT",
        "script": "Before working at height, check your access equipment and fall protection. Never work at height without proper controls.",
        "hashtags": "#HSE #WorkingAtHeight #FallProtection #SafetyFirst #ConstructionSafety"
    },
    {
        "search": "construction worker safety gloves",
        "title": "PROTECT YOUR HANDS",
        "script": "Your hands are exposed to many hazards. Choose the correct gloves and inspect them before starting the task.",
        "hashtags": "#HSE #HandSafety #PPE #SafetyFirst #ConstructionSafety"
    },
    {
        "search": "construction worker safety goggles",
        "title": "PROTECT YOUR EYES",
        "script": "Flying particles and chemicals can cause permanent eye injuries. Always wear the correct eye protection for the task.",
        "hashtags": "#HSE #EyeSafety #PPE #SafetyFirst #WorkplaceSafety"
    },
    {
        "search": "construction worker housekeeping safety",
        "title": "GOOD HOUSEKEEPING",
        "script": "Keep walkways clear and remove waste as you work. Good housekeeping reduces trips, falls and other workplace hazards.",
        "hashtags": "#HSE #Housekeeping #SafetyFirst #ConstructionSafety #WorkplaceSafety"
    },
    {
        "search": "construction worker lifting safety",
        "title": "LIFT SAFELY",
        "script": "Before lifting, check the weight and your route. Use the correct lifting method and get help when the load is too heavy.",
        "hashtags": "#HSE #ManualHandling #LiftingSafety #SafetyFirst #WorkplaceSafety"
    },
    {
        "search": "construction worker electrical safety",
        "title": "ELECTRICAL SAFETY",
        "script": "Never work on electrical equipment without proper authorization. Isolate the energy and verify that it is safe before work begins.",
        "hashtags": "#HSE #ElectricalSafety #LOTO #SafetyFirst #ConstructionSafety"
    },
    {
        "search": "construction crane lifting safety",
        "title": "SAFE LIFTING",
        "script": "Before a lifting operation, check the lifting plan, equipment and exclusion zone. Never stand under a suspended load.",
        "hashtags": "#HSE #LiftingSafety #CraneSafety #ConstructionSafety #SafetyFirst"
    },
    {
        "search": "construction confined space safety",
        "title": "CONFINED SPACE",
        "script": "Never enter a confined space without proper authorization and controls. Test the atmosphere and follow the entry procedure.",
        "hashtags": "#HSE #ConfinedSpace #SafetyFirst #ConstructionSafety #WorkplaceSafety"
    }
]

# Choose 3 different topics each day
start_index = TODAY.toordinal() % len(topics)

selected_topics = [
    topics[start_index % len(topics)],
    topics[(start_index + 1) % len(topics)],
    topics[(start_index + 2) % len(topics)]
]

headers = {
    "Authorization": API_KEY
}


def create_music(path):
    sample_rate = 44100
    duration = 15
    samples = sample_rate * duration

    with wave.open(str(path), "w") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        for i in range(samples):
            t = i / sample_rate

            notes = [220.00, 277.18, 329.63, 440.00]

            chord = 0

            for note in notes:
                chord += math.sin(2 * math.pi * note * t)

            value = int((chord / len(notes)) * 900)

            if t < 1:
                value = int(value * t)

            if t > 13.5:
                value = int(value * (15 - t) / 1.5)

            value = max(-32767, min(32767, value))

            wav.writeframes(
                value.to_bytes(2, "little", signed=True) +
                value.to_bytes(2, "little", signed=True)
            )


def timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)

    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def ass_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds - int(seconds)) * 100)

    return f"{h}:{m:02}:{s:02}.{cs:02}"


def download_video(topic, number):

    print(f"\nSearching Pexels for Short {number}: {topic['search']}")

    response = requests.get(
        "https://api.pexels.com/v1/videos/search",
        headers=headers,
        params={
            "query": topic["search"],
            "orientation": "portrait",
            "size": "medium",
            "per_page": 20
        },
        timeout=30
    )

    response.raise_for_status()

    videos = response.json().get("videos", [])

    if not videos:
        raise RuntimeError(
            f"No Pexels video found for: {topic['search']}"
        )

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

    source = OUT / f"source_{number}.mp4"

    print(f"Downloading video {number}...")

    with requests.get(
        video_url,
        stream=True,
        timeout=120
    ) as r:

        r.raise_for_status()

        with open(source, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):

                if chunk:
                    f.write(chunk)

    return source, video


def create_short(topic, number):

    print(f"\n========== SHORT {number} ==========")
    print(topic["title"])

    source, video = download_video(topic, number)

    voice = OUT / f"voice_{number}.mp3"
    music = OUT / f"music_{number}.wav"
    ass = OUT / f"captions_{number}.ass"
    final = OUT / f"hse_short_{number}.mp4"

    title_file = OUT / f"youtube_title_{number}.txt"
    description_file = OUT / f"youtube_description_{number}.txt"
    hashtags_file = OUT / f"youtube_hashtags_{number}.txt"

    # Voice
    print("Creating voice...")

    subprocess.run(
        [
            "edge-tts",
            "--voice",
            "en-US-GuyNeural",
            "--text",
            topic["script"],
            "--write-media",
            str(voice)
        ],
        check=True
    )

    # Music
    print("Creating background music...")

    create_music(music)

    # Captions
    words = topic["script"].split()

    groups = [
        " ".join(words[i:i + 5])
        for i in range(0, len(words), 5)
    ]

    total_time = 14.5
    part = total_time / len(groups)

    with open(ass, "w", encoding="utf-8") as f:

        f.write(
            "[Script Info]\n"
            "ScriptType: v4.00+\n"
            "PlayResX: 1080\n"
            "PlayResY: 1920\n\n"
        )

        f.write("[V4+ Styles]\n")

        f.write(
            "Format: Name, Fontname, Fontsize, PrimaryColour, "
            "SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
            "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
            "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, "
            "MarginV, Encoding\n"
        )

        f.write(
            "Style: Caption,DejaVu Sans,48,"
            "&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,"
            "-1,0,0,0,100,100,0,0,1,3,1,2,80,80,300,1\n"
        )

        f.write(
            "Style: Hook,DejaVu Sans,68,"
            "&H0000FFFF,&H0000FFFF,&H00000000,&H80000000,"
            "-1,0,0,0,100,100,0,0,1,4,2,8,60,60,120,1\n"
        )

        f.write("\n[Events]\n")

        f.write(
            "Format: Layer, Start, End, Style, Name, "
            "MarginL, MarginR, MarginV, Effect, Text\n"
        )

        # Hook
        f.write(
            f"Dialogue: 0,0:00:00.00,0:00:03.00,Hook,,"
            f"0,0,0,,{{\\fad(300,300)}}{topic['title']}\n"
        )

        # Captions
        for i, text in enumerate(groups):

            start = i * part
            end = min((i + 1) * part, total_time)

            f.write(
                f"Dialogue: 0,{ass_time(start)},{ass_time(end)},"
                f"Caption,,0,0,0,,"
                f"{{\\fad(180,180)"
                f"\\t(0,180,\\fscx105\\fscy105)"
                f"\\t(180,360,\\fscx100\\fscy100)}}"
                f"{text.upper()}\n"
            )

    # Metadata
    photographer = video.get(
        "user", {}
    ).get(
        "name",
        "Pexels contributor"
    )

    pexels_page = video.get(
        "url",
        "https://www.pexels.com/"
    )

    youtube_title = (
        f"{topic['title']} | HSE Safety Short"
    )

    youtube_description = f"""⚠️ HSE SAFETY SHORT

{topic["script"]}

Stay alert. Follow the procedure. Go home safe.

📌 Safety Reminder:
Always follow your company's approved procedures,
risk assessments and safety requirements.

🎥 Footage:
Video by {photographer} from Pexels
{pexels_page}

Photos and videos provided by Pexels:
https://www.pexels.com/

{topic["hashtags"]}

#Shorts #HSE #Safety
"""

    title_file.write_text(
        youtube_title,
        encoding="utf-8"
    )

    description_file.write_text(
        youtube_description,
        encoding="utf-8"
    )

    hashtags_file.write_text(
        topic["hashtags"],
        encoding="utf-8"
    )

    # Final video
    print("Rendering final Short...")

    filter_complex = (
        "[0:v]"
        "scale=1080:1920:"
        "force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "setsar=1,"
        f"subtitles=assets/captions_{number}.ass"
        "[v];"

        "[1:a]volume=1.0[voice];"

        "[2:a]volume=0.12[music];"

        "[voice][music]"
        "amix=inputs=2:"
        "duration=first:"
        "dropout_transition=2"
        "[a]"
    )

    subprocess.run(
        [
            "ffmpeg",
            "-y",

            "-i",
            str(source),

            "-i",
            str(voice),

            "-i",
            str(music),

            "-filter_complex",
            filter_complex,

            "-map",
            "[v]",

            "-map",
            "[a]",

            "-t",
            "15",

            "-r",
            "30",

            "-c:v",
            "libx264",

            "-preset",
            "veryfast",

            "-crf",
            "23",

            "-pix_fmt",
            "yuv420p",

            "-c:a",
            "aac",

            "-b:a",
            "160k",

            "-movflags",
            "+faststart",

            str(final)
        ],
        check=True
    )

    print(f"✅ Short {number} completed:")
    print(final)

    return final


# Create 3 Shorts
for number, topic in enumerate(selected_topics, start=1):

    create_short(topic, number)


print("\n===================================")
print("🎉 3 HSE SHORTS CREATED SUCCESSFULLY")
print("===================================")

for number in range(1, 4):

    final = OUT / f"hse_short_{number}.mp4"

    if final.exists():

        size_mb = final.stat().st_size / (1024 * 1024)

        print(
            f"Short {number}: "
            f"{size_mb:.2f} MB"
        )
