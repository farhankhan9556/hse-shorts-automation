import os
import requests
from pathlib import Path

# ==============================
# PEXELS API
# ==============================

API_KEY = os.environ.get("PEXELS_API_KEY")

if not API_KEY:
    raise RuntimeError("PEXELS_API_KEY is missing from GitHub Secrets")

HEADERS = {
    "Authorization": API_KEY
}

# ==============================
# OUTPUT FOLDER
# ==============================

OUTPUT_DIR = Path("assets")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "hse_source.mp4"

# ==============================
# HSE SEARCH TOPICS
# ==============================

QUERIES = [
    "construction worker safety",
    "construction site safety",
    "worker wearing safety helmet",
    "industrial worker safety",
    "workplace safety"
]

# ==============================
# SEARCH PEXELS
# ==============================

video = None

for query in QUERIES:

    print(f"Searching Pexels for: {query}")

    response = requests.get(
        "https://api.pexels.com/v1/videos/search",
        headers=HEADERS,
        params={
            "query": query,
            "orientation": "portrait",
            "size": "medium",
            "per_page": 15
        },
        timeout=30
    )

    print(f"Pexels response: {response.status_code}")

    response.raise_for_status()

    data = response.json()

    videos = data.get("videos", [])

    if videos:
        video = videos[0]
        print(f"Found Pexels video ID: {video.get('id')}")
        break

# ==============================
# CHECK RESULT
# ==============================

if not video:
    raise RuntimeError("No HSE video was found on Pexels")

# ==============================
# FIND VIDEO FILE
# ==============================

video_files = video.get("video_files", [])

if not video_files:
    raise RuntimeError("Pexels returned no downloadable video files")

# Prefer portrait video files
portrait_files = [
    f for f in video_files
    if f.get("width", 0) > 0
    and f.get("height", 0) > 0
    and f.get("height", 0) >= f.get("width", 0)
]

if portrait_files:
    video_files = portrait_files

# Sort by resolution
video_files.sort(
    key=lambda f: f.get("width", 0) * f.get("height", 0),
    reverse=True
)

video_url = video_files[0].get("link")

if not video_url:
    raise RuntimeError("No downloadable video link found")

print(f"Downloading video from Pexels...")
print(f"Resolution: {video_files[0].get('width')}x{video_files[0].get('height')}")

# ==============================
# DOWNLOAD VIDEO
# ==============================

with requests.get(
    video_url,
    stream=True,
    timeout=120
) as response:

    response.raise_for_status()

    with open(OUTPUT_FILE, "wb") as file:

        for chunk in response.iter_content(
            chunk_size=1024 * 1024
        ):

            if chunk:
                file.write(chunk)

# ==============================
# FINISHED
# ==============================

file_size = OUTPUT_FILE.stat().st_size / (1024 * 1024)

print("--------------------------------")
print("HSE SOURCE VIDEO READY")
print(f"File: {OUTPUT_FILE}")
print(f"Size: {file_size:.2f} MB")
print("--------------------------------")
