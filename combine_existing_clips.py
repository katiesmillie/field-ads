#!/usr/bin/env python3
"""Combine existing extracted clips into single audio files"""
from pydub import AudioSegment
from pathlib import Path
import re

# Scripts to process
scripts = ["script_3", "script_7", "script_8", "script_9"]

print("Combining existing clips from complete scripts...\n")

for script_name in scripts:
    print(f"=" * 60)
    print(f"Processing {script_name.upper()}")
    print(f"=" * 60)

    script_dir = Path(script_name)

    # Find all clip files (excluding alternatives and any existing complete files)
    clip_files = sorted([
        f for f in script_dir.glob("*_clip_*.wav")
        if not 'complete' in f.name and not f.name.endswith('a.wav')
    ])

    if not clip_files:
        print(f"⚠️  No clips found in {script_name}/\n")
        continue

    print(f"Found {len(clip_files)} clips:")
    for f in clip_files:
        print(f"  - {f.name}")
    print()

    # Load and combine all clips
    combined = None
    total_duration = 0

    for clip_file in clip_files:
        try:
            clip = AudioSegment.from_wav(str(clip_file))
            duration = len(clip) / 1000

            if combined is None:
                combined = clip
            else:
                combined += clip

            total_duration += duration
            print(f"  ✓ Added {clip_file.name} ({duration:.1f}s)")
        except Exception as e:
            print(f"  ✗ Error loading {clip_file.name}: {e}")

    # Export combined audio
    if combined:
        output_file = script_dir / f"{script_name}_complete_clean.wav"
        print(f"\nTotal duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
        print(f"Exporting: {output_file}")

        combined.export(str(output_file), format="wav")
        print(f"✅ Done!\n")
    else:
        print(f"❌ No clips were loaded for {script_name}\n")

print("=" * 60)
print("All scripts processed!")
