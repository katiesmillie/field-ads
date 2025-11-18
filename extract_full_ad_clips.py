#!/usr/bin/env python3
"""
Extract full ad quote clips using Fireflies JSON timestamps.
Ensures each clip contains the complete text shown in the player.
"""

import json
from pathlib import Path
from pydub import AudioSegment

# Map of ad quote name to (audio_file, start_time, end_time, padding_ms)
# Times are in seconds from the Fireflies JSON
CLIP_EXTRACTIONS = {
    "generation_to_generation": {
        "file": "audio/matt 1.m4a",
        "start": 465.45,  # "I think because I wanted..."
        "end": 484.86,    # "...they couldn't cook before."
        "padding": 500
    },
    "investing_worth_it": {
        "file": "audio/matt 1.m4a",
        "start": 478.70,  # "You might bring it to a friend's house..."
        "end": 489.58,    # "...makes it worth it."
        "padding": 500
    },
    "heirloom_forever": {
        "file": "audio/matt 1.m4a",
        "start": 490.38,  # "Not just because it's non toxic..."
        "end": 514.62,    # "...journey in your life."
        "padding": 500
    },
    "buying_intentionally": {
        "file": "audio/matt 1.m4a",
        "start": 506.50,  # "There's something really meaningful..."
        "end": 514.62,    # "...journey in your life."
        "padding": 500
    },
    "beautiful_object": {
        "file": "audio/matt 1.m4a",
        "start": 299.58,  # "The way you have that set up..."
        "end": 326.57,    # "...by the seasoning or the imperfections."
        "padding": 500
    },
    "two_minutes_twenty_seconds": {
        "file": "audio/matt 1.m4a",
        "start": 90.32,   # "And so when I show people..."
        "end": 103.92,    # "...your stainless steel."
        "padding": 500
    },
    "see_to_believe": {
        "file": "audio/matt 1.m4a",
        "start": 232.00,  # Context before
        "end": 242.00,    # "...you don't take my word for it."
        "padding": 500
    },
    "almost_every_day": {
        "file": "audio/matt 1.m4a",
        "start": 623.84,  # "Even with Teflon..."
        "end": 642.50,    # "...perfect shape of a fried egg and you're done."
        "padding": 500
    },
    "give_to_mom": {
        "file": "audio/matt 1.m4a",
        "start": 988.36,  # Context before
        "end": 1016.49,   # "...making her life easier."
        "padding": 500
    },
    "my_efforts_made_it_epic": {
        "file": "audio/matt 1.m4a",
        "start": 1884.00,  # Context before "My..."
        "end": 1893.74,    # "...that pan epic."
        "padding": 500
    },
    "seasoning_perfect": {
        "file": "audio/matt 1.m4a",
        "start": 1906.00,  # Context before
        "end": 1918.22,    # "...the seasoning perfect."
        "padding": 500
    },
    "more_meaningful": {
        "file": "audio/matt 1.m4a",
        "start": 306.46,   # "And I think when you're holding..."
        "end": 337.37,     # "...use it for everything."
        "padding": 500
    },
    "pride_in_what_you_made": {
        "file": "audio/matt 1.m4a",
        "start": 306.46,   # "And I think when you're holding..."
        "end": 326.57,     # "...by the seasoning or the imperfections."
        "padding": 500
    },
}

def extract_clip(clip_name, config, output_dir="ad_clips"):
    """Extract a single clip using the provided config."""

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    audio_file = config["file"]
    start_sec = config["start"]
    end_sec = config["end"]
    padding_ms = config["padding"]

    print(f"\nExtracting: {clip_name}")
    print(f"  Source: {audio_file}")
    print(f"  Time: {start_sec:.2f}s - {end_sec:.2f}s (duration: {end_sec - start_sec:.2f}s)")

    # Load audio
    audio = AudioSegment.from_file(audio_file)

    # Convert to milliseconds and add padding
    start_ms = max(0, int(start_sec * 1000) - padding_ms)
    end_ms = min(len(audio), int(end_sec * 1000) + padding_ms)

    # Extract clip
    clip = audio[start_ms:end_ms]

    # Save
    output_file = output_path / f"{clip_name}.wav"
    clip.export(output_file, format="wav")

    print(f"  ✓ Saved: {output_file} ({len(clip)/1000:.2f}s)")

    return str(output_file)

def main():
    print("="*60)
    print("EXTRACTING FULL AD CLIPS WITH COMPLETE TEXT")
    print("="*60)
    print(f"\nExtracting {len(CLIP_EXTRACTIONS)} clips...")

    extracted = []

    for clip_name, config in CLIP_EXTRACTIONS.items():
        try:
            output_file = extract_clip(clip_name, config)
            extracted.append(clip_name)
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print(f"\n{'='*60}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"Successfully extracted {len(extracted)}/{len(CLIP_EXTRACTIONS)} clips:")
    for name in extracted:
        print(f"  ✓ {name}")

    if len(extracted) < len(CLIP_EXTRACTIONS):
        print(f"\nFailed clips:")
        for name in CLIP_EXTRACTIONS:
            if name not in extracted:
                print(f"  ✗ {name}")

if __name__ == "__main__":
    main()
