#!/usr/bin/env python3
"""Extract alternative clips using known timestamps"""
from pydub import AudioSegment
from pathlib import Path

# Load the audio file
print("Loading audio file...")
audio = AudioSegment.from_file("audio/matt 1.m4a", format="m4a")
print(f"Audio loaded: {len(audio)/1000:.1f} seconds\n")

# Define clips with their timestamps (in seconds)
clips = [
    {
        "filename": "script_1/script_1_clip_01a.wav",
        "start": 168.9,
        "end": 200.4,
        "description": "cheaper skillets theme"
    },
    {
        "filename": "script_1/script_1_clip_02a.wav",
        "start": 303.2,
        "end": 323.9,
        "description": "beautiful object / inspired theme"
    },
    {
        "filename": "script_10/script_10_clip_05a.wav",
        "start": 92.1,
        "end": 101.7,
        "description": "two minutes cleanup"
    }
]

padding_ms = 500

print("Extracting alternative clips...\n")

for clip_info in clips:
    print(f"Extracting: {clip_info['filename']}")
    print(f"  Description: {clip_info['description']}")
    print(f"  Timestamp: {clip_info['start']:.1f}s - {clip_info['end']:.1f}s")

    # Convert to milliseconds and add padding
    start_ms = max(0, int(clip_info['start'] * 1000) - padding_ms)
    end_ms = min(len(audio), int(clip_info['end'] * 1000) + padding_ms)

    # Extract the clip
    clip = audio[start_ms:end_ms]

    # Ensure directory exists
    output_path = Path(clip_info['filename'])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Export as WAV
    clip.export(str(output_path), format="wav")

    duration = (end_ms - start_ms) / 1000
    print(f"  Saved: {clip_info['filename']} ({duration:.1f}s)\n")

print("Done! 3 alternative clips extracted.")
