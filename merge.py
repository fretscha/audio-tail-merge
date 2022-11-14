import logging
from logging.config import fileConfig

import ffmpeg


fileConfig("logging_config.ini")

logger = logging.getLogger()

audio_files = [
    "./data/preamble.wav",
    "./data/PinkPanther30.wav",
    "./data/taunt.wav",
    "./data/gettysburg10.wav",
]
audio_streams = {}
for audio in audio_files:
    probe = ffmpeg.probe(audio)
    if probe["streams"][0]["codec_type"] == "audio":
        # expect first stream to be audio
        audio_streams[audio] = float(ffmpeg.probe(audio)["format"]["duration"])
    else:
        logger.debug(f"dropped {audio} because stream 0 is not a audio stram")


max_duration = max(audio_streams.values())

streams = []
for af in audio_streams.keys():
    duration_diff = max_duration - audio_streams[af]
    stream = ffmpeg.input(af).filter(
        "adelay", f"{duration_diff * 1000}|{duration_diff * 1000}"
    )
    streams.append(stream)

merged = ffmpeg.filter(streams, "amix", inputs=len(streams))
merged.output("./data/output.mp3").run(overwrite_output=True)
