from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
import subprocess, json, re

root = Path(__file__).resolve().parents[1] / "website-design"
out = root / "assets/intro-video"
tmp = Path("/private/tmp/seventies-video")
tmp.mkdir(exist_ok=True)
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
font = "/System/Library/Fonts/Supplemental/Arial.ttf"
bold = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
scenes = [
    (
        "Seventies Sound",
        "A first look at 1970s music",
        "Welcome to Seventies Sound. This is a short introduction to music from the nineteen seventies.",
    ),
    (
        "Choose a style",
        "Pop / Glam rock / Disco",
        "Start with pop, glam rock or disco. Each section introduces an artist and gives you a song to try.",
    ),
    (
        "Explore the music",
        "Read / Listen / Compare",
        "Read the short introduction, open the extra facts, then follow a listening link to explore the music.",
    ),
    (
        "What should we add?",
        "Visit the Request page",
        "You can suggest another artist or topic on the Request page. This is a starting point, so there is more music to discover.",
    ),
]
voice_id = "Xb7hH8MSUJpSbSDYk0k2"
voice_name = "Alice - Clear, Engaging Educator"


def elevenlabs_key():
    env_file = root.parent / ".env"
    for line in env_file.read_text().splitlines():
        name, _, value = line.partition("=")
        key = value.strip().strip("'\"")
        if name.strip() == "ELEVENLABS_API_KEY" and key:
            return key
    raise RuntimeError("ELEVENLABS_API_KEY is missing from .env")


def make_narration(text, output):
    payload = json.dumps(
        {
            "text": text,
            "model_id": "eleven_flash_v2_5",
            "voice_settings": {
                "stability": 0.45,
                "similarity_boost": 0.8,
                "style": 0.15,
                "use_speaker_boost": True,
            },
        }
    )
    result = subprocess.run(
        [
            "curl",
            "-fsS",
            "--request",
            "POST",
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            "--header",
            f"xi-api-key: {elevenlabs_key()}",
            "--header",
            "Content-Type: application/json",
            "--data",
            payload,
            "--output",
            str(output),
        ],
        capture_output=True,
    )
    if result.returncode:
        raise RuntimeError("ElevenLabs narration request failed. Check the API key and account status.")


clips = []
durations = []
scene_colours = ["#934326", "#345B50", "#A05A2C", "#6B3F67"]
for i, (title, subtitle, speech) in enumerate(scenes):
    im = Image.new("RGB", (1280, 720), "#F7F1E5")
    d = ImageDraw.Draw(im)
    accent = scene_colours[i]
    d.rectangle((0, 0, 34, 720), fill=accent)
    d.rectangle((75, 122, 360, 130), fill=accent)
    d.text(
        (75, 75), "SEVENTIES SOUND", font=ImageFont.truetype(bold, 25), fill=accent
    )
    d.text((75, 185), title, font=ImageFont.truetype(bold, 57), fill="#29231E")
    d.text((75, 285), subtitle, font=ImageFont.truetype(font, 35), fill="#29231E")
    d.text((75, 625), f"INTRODUCTION  {i + 1} / {len(scenes)}", font=ImageFont.truetype(bold, 18), fill=accent)
    d.arc((760, 270, 1210, 720), 190, 355, fill=accent, width=8)
    d.ellipse((840, 350, 1120, 630), fill="#29231E")
    d.ellipse((865, 375, 1095, 605), outline="#F7F1E5", width=3)
    d.ellipse((895, 405, 1065, 575), outline="#F7F1E5", width=2)
    d.ellipse((930, 440, 1030, 540), fill=accent)
    d.ellipse((973, 483, 987, 497), fill="#F7F1E5")
    im.save(tmp / f"{i}.png")
    if i == 0:
        im.save(out / "poster.jpg", quality=88)
    narration = tmp / f"{i}.mp3"
    make_narration(speech, narration)
    info = subprocess.run([ffmpeg, "-i", str(narration)], capture_output=True, text=True)
    match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", info.stderr)
    if not match:
        raise RuntimeError("No narration audio was produced")
    h, m, s = map(float, match.groups())
    length = h * 3600 + m * 60 + s + 0.5
    durations.append(length)
    clip = tmp / f"{i}.mp4"
    clips.append(clip)
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-loop",
            "1",
            "-i",
            str(tmp / f"{i}.png"),
            "-i",
            str(narration),
            "-t",
            str(length),
            "-vf",
            "scale=1280:720,format=yuv420p",
            "-r",
            "24",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "25",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-af",
            "apad",
            str(clip),
        ],
        check=True,
        capture_output=True,
    )
(tmp / "clips.txt").write_text("".join(f"file '{p}'\n" for p in clips))
subprocess.run(
    [
        ffmpeg,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(tmp / "clips.txt"),
        "-c",
        "copy",
        "-movflags",
        "+faststart",
        str(out / "introduction.mp4"),
    ],
    check=True,
    capture_output=True,
)


def stamp(value):
    ms = round(value * 1000)
    return f"{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}"


vtt = "WEBVTT\n\n"
start = 0
for scene, duration in zip(scenes, durations):
    # Short captions use one sentence at a time; timings split within each scene.
    sentences = [x.strip() + "." for x in scene[2].split(".") if x.strip()]
    total = sum(len(x) for x in sentences)
    end = start + duration
    for sentence in sentences:
        nxt = start + (duration * len(sentence) / total)
        vtt += f"{stamp(start)} --> {stamp(nxt)}\n{sentence}\n\n"
        start = nxt
    start = end
(out / "captions.vtt").write_text(vtt)
(out / "video-text.txt").write_text("\n\n".join(x[2] for x in scenes))
(out / "production.json").write_text(
    json.dumps(
        {
            "duration_seconds": sum(durations),
            "size": list(im.size),
            "format": "H.264 MP4 + AAC",
            "narration": f"ElevenLabs {voice_name}; AI-generated British narration",
            "voice_id": voice_id,
            "voice_model": "eleven_flash_v2_5",
            "original_script": [x[2] for x in scenes],
            "captions": "English WebVTT; scene-based sentence timing",
        },
        indent=2,
    )
)
print(
    "Video ready:",
    round(sum(durations), 1),
    "seconds;",
    (out / "introduction.mp4").stat().st_size,
    "bytes",
)
