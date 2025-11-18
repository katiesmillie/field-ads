#!/usr/bin/env python3
"""Re-extract and combine script clips without padding for clean playback"""
import os
os.chdir('/Users/katiemuscarella/Projects/field/ads')

from extract_clips import AudioClipExtractor
from pydub import AudioSegment
from pathlib import Path

# Script 6 clips from the script file
script_6_quotes = [
    "Usually when people bring up cast iron, they tell me that they found a skillet that's cheaper, and they wonder what the difference in the price would be.",
    "And until they really touch it and feel it and feel the weight or the smoothness of the bottom, they don't really understand in the handle and the way it feels in your hand, they don't really understand the difference in cooking on a surface that's maybe more rough.",
    "Once you hold it, once you feel it, like, if those. The way you have that set up in that room, it's like, literally, you could just hang it on the wall if that's all you want to do with it. It is a beautiful object.",
    "And I think when you're holding the less expensive ones, you can really tell the difference, and you can tell that it is heavier, it's harder to use.",
    "And maybe there's a sense of pride in the beauty of the object and then what you made that object into by the seasoning or the imperfections.",
    "And I think that's why cast iron seems more meaningful and why once you start using it, you want to buy more or use it for everything."
]

print("Loading audio and transcribing matt 1.m4a...")
extractor = AudioClipExtractor("audio/matt 1.m4a", model_size="base")
extractor.load_audio()
extractor.transcribe()

print("\nFinding clips without padding...\n")

combined = None

for i, quote in enumerate(script_6_quotes, 1):
    print(f"Clip {i}: {quote[:60]}...")
    match = extractor.find_quote_timestamps(quote)

    if match:
        print(f"  Found at {match['start_time']:.1f}s - {match['end_time']:.1f}s")

        # Extract without padding
        start_ms = int(match['start_time'] * 1000)
        end_ms = int(match['end_time'] * 1000)

        clip = extractor.audio[start_ms:end_ms]

        if combined is None:
            combined = clip
        else:
            combined += clip

        print(f"  Added to combined audio ({len(clip)/1000:.1f}s)")
    else:
        print(f"  ⚠️  Not found")

    print()

if combined:
    total_duration = len(combined) / 1000
    print(f"Total combined duration: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")

    output_file = "script_6/script_6_complete_clean.wav"
    print(f"Exporting to: {output_file}")
    combined.export(output_file, format="wav")

    print(f"✅ Done! Created clean version without overlaps")
else:
    print("❌ No clips were extracted")
