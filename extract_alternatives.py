#!/usr/bin/env python3
"""Quick script to extract alternative clips"""
import sys
sys.path.insert(0, '/Users/katiemuscarella/Projects/field/ads')
from extract_clips import AudioClipExtractor

# Initialize extractor
extractor = AudioClipExtractor("audio/matt 1.m4a", model_size="base")

# Load audio and transcribe
extractor.load_audio()
extractor.transcribe()

# Alternative clips
alternatives = [
    ("script_5_clip_04a.wav", "you start with scrambled eggs that's the gateway to cast iron because once you realize like these aren't sticking then you just start using everything"),
    ("script_5_clip_04b.wav", "yeah so you start with scrambled eggs that's the gateway to cast iron because once you realize like these aren't sticking then you just start using everything")
]

print("\nExtracting alternative clips for Clip 4...\n")

for filename, quote in alternatives:
    print(f"Extracting: {filename}")
    print(f"Quote: {quote[:60]}...")

    match = extractor.find_quote_timestamps(quote)

    if match:
        print(f"  ✓ Found match (score: {match['score']}%)")
        print(f"    Timestamp: {match['start_time']:.1f}s - {match['end_time']:.1f}s")

        output_path = f"script_5/{filename}"
        extractor.extract_clip(
            match['start_time'],
            match['end_time'],
            output_path,
            padding_ms=500
        )

        duration = (match['end_time'] - match['start_time'])
        print(f"    Saved: {filename} ({duration:.1f}s)\n")
    else:
        print(f"  ⚠️  Not found\n")

print("Done!")
