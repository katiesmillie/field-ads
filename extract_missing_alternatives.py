#!/usr/bin/env python3
"""Extract alternative clips for missing quotes"""
import os
os.chdir('/Users/katiemuscarella/Projects/field/ads')

from extract_clips import AudioClipExtractor

# Initialize extractor
extractor = AudioClipExtractor("audio/matt 1.m4a", model_size="base")

# Load audio and transcribe
print("Loading audio and transcribing...")
extractor.load_audio()
extractor.transcribe()

# Alternative clips with their quotes
alternatives = [
    # Script 1, Clip 1a - cheaper skillets theme
    ("script_1/script_1_clip_01a.wav",
     "usually when people bring up cast iron they tell me that they found skillet that's cheaper and they wonder what the difference in the price of the and until they really touch it and feel it and feel the weight or the smoothness of the bottom they don't really understand and the handle on the way it feels in your hand they don't really understand the difference in cooking on a surface that's maybe more rough and so you might try to accommodate that by using more oil or butter to make it non-stick and it is harder to use and I think when you find this like really nice weight this handle and the smooth bottom"),

    # Script 1, Clip 2a - beautiful object / inspired theme
    ("script_1/script_1_clip_02a.wav",
     "it is a beautiful object and I think when you're holding the less expensive ones you can really tell the difference and you can tell that it is heavier it's harder to use and maybe there's a sense of pride and the beauty of the object and then what you made that object into by the seasoning or the imperfections"),

    # Script 10, Clip 5a - two minutes cleanup
    ("script_10/script_10_clip_05a.wav",
     "I've even timed it before to clean up from making eggs I swear two minutes and twenty seconds re-oiled and ready back on the stove to cook again it's way different than even the nuance of cleaning your stainless steel")
]

print("\nExtracting alternative clips for missing quotes...\n")

for filename, quote in alternatives:
    print(f"Extracting: {filename}")
    print(f"Quote: {quote[:60]}...")

    match = extractor.find_quote_timestamps(quote)

    if match:
        print(f"  ✓ Found match (score: {match['score']}%)")
        print(f"    Timestamp: {match['start_time']:.1f}s - {match['end_time']:.1f}s")

        output_path = filename
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
