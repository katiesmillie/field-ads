#!/usr/bin/env python3
"""Extract more alternative clips using known timestamps"""
from pydub import AudioSegment
from pathlib import Path

# Load the audio file
print("Loading audio file...")
audio = AudioSegment.from_file("audio/matt 1.m4a", format="m4a")
print(f"Audio loaded: {len(audio)/1000:.1f} seconds\n")

# Define clips with their timestamps (in seconds)
clips = [
    {
        "filename": "script_1/script_1_clip_03a.wav",
        "start": 537.9,
        "end": 603.0,
        "description": "scrambled eggs gateway / confidence theme"
    },
    {
        "filename": "script_2/script_2_clip_05a.wav",
        "start": 642.5,
        "end": 660.1,
        "description": "getting creative / adventurous cooking"
    }
]

padding_ms = 500

print("Extracting more alternative clips...\n")

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

print("Done! 2 more alternative clips extracted.")
