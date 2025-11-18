#!/usr/bin/env python3
"""Combine all clips from a complete script into one continuous audio file"""
from pydub import AudioSegment
from pathlib import Path

# Choose Script 6 (6 clips, all from matt 1.m4a, 100% complete)
script_num = 6
script_dir = Path(f"script_{script_num}")

print(f"Combining all clips from Script {script_num}...\n")

# Load all clips in order
clips = []
clip_files = sorted(script_dir.glob("script_*_clip_*.wav"))

for clip_file in clip_files:
    if 'complete' not in clip_file.name:  # Skip any previously combined files
        print(f"Loading: {clip_file.name}")
        clip = AudioSegment.from_wav(str(clip_file))
        clips.append(clip)
        print(f"  Duration: {len(clip)/1000:.1f}s")

print(f"\nTotal clips: {len(clips)}")

# Combine all clips
print("\nCombining clips...")
combined = clips[0]
for clip in clips[1:]:
    combined += clip

total_duration = len(combined) / 1000
print(f"Combined duration: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")

# Export combined audio
output_file = script_dir / f"script_{script_num}_complete.wav"
print(f"\nExporting to: {output_file}")
combined.export(str(output_file), format="wav")

print(f"✅ Done! Created {output_file}")
