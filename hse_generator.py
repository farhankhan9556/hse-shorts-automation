
import os
import requests
from pathlib import Path

API_KEY = os.environ.get("PEXELS_API_KEY")

if not API_KEY:
    raise Exception("PEXELS_API_KEY is missing")

OUTPUT = Path("assets")
OUTPUT.mkdir(exist_ok=True)

queries = [
    "construction worker safety",
    "construction site worker",
    "worker wearing safety helmet",
    "industrial safety",
    "workplace safety"
]

headers = {
    "Authorization": API_KEY
}

video = None

for query in queries:
    print(f"Searching Pexels: {query}")

    response = requests.get(
        "https://api.pexels.com/v1/videos/search",
        headers=headers,
        params={
            "query": query,
            "orientation": "portrait",
            "size": "medium",
            "per_page": 10
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if data.get("videos"):
        video = data["videos"][0]
        print(f"Found video: {video['id']}")
        break

if not video:
    raise Exception("No suitable HSE video found")

files = video.get("video_files", [])

# Prefer HD portrait/vertical footage
files.sort(
    key=lambda x: (
        x.get("width", 0) * x.get("height", 0)
    ),
    reverse=True
)

video_url = files[0]["link"]

output_file = OUTPUT / "hse_source.mp4"

print("Downloading video...")

with requests.get(video_url, stream=True, timeout=120) as r:
    r.raise_for_status()

    with open(output_file, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)

print(f"Video downloaded successfully: {output_file}")
