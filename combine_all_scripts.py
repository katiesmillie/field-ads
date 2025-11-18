#!/usr/bin/env python3
"""Combine all clips from complete scripts into single audio files"""
import os
os.chdir('/Users/katiemuscarella/Projects/field/ads')

from extract_clips import AudioClipExtractor
from pydub import AudioSegment
from pathlib import Path

# Define scripts to combine (from EXTRACTION_SUMMARY.md - complete scripts only)
scripts_config = {
    "script_3": {
        "source": "audio/matt 1.m4a",  # 5 of 6 clips from matt 1
        "quotes": [
            "Cast iron is kind of a gateway drug to the more intentional... a life worth living.",
            "I think because I wanted to figure out how to cook with cast iron because it felt like it was worth it. The knowledge that you might pass it down from generation to generation.",
            "You might bring it to a friend's house to do something with it and cook a meal that they couldn't cook before. I think it shows you that investing in it really makes it worth it.",
            "Not just because it's non toxic, not because it's non stick. But even if you bought all those, you know, in another type of pan with a coating, I don't think you'd be bringing it on adventures, bringing it to your friend's house.",
            "There's something really meaningful that it's an heirloom and it'll be with you forever. And I think that kind of starts to make you think about not consuming as much and buying things very intentionally that you think will also have that type of journey in your life."
        ]
    },
    "script_7": {
        "source": "audio/matt 3.m4a",
        "quotes": [
            "I really love the idea of using one thing over and over again. I know how to cook on it. I know its imperfections.",
            "It probably cooks better than a brand new one because I know it so well. There's something about that that I really like.",
            "There's something about the heirloom quality of it that I think is in such stark contrast to our world right now, which is you consume a thing, you throw it away, you get another thing.",
            "It's the antithesis of that. And that's really meaningful to me.",
            "I think if cast iron can be a gateway to thinking about other things you buy, does it have those qualities?",
            "It kind of makes you think about, like, one level deeper when you buy something."
        ]
    },
    "script_8": {
        "source": "audio/matt 1.m4a",
        "quotes": [
            "I think the start of cooking with cast iron was always scrambled eggs. It seems like that seems to be the test of what non-stick means to someone.",
            "I think once you figure out that it's just as easy to cook scrambled eggs on, it's kind of the gateway to a lot of other things that you can use it for.",
            "I think those gateways led me to cast iron chicken in the oven. It led me to sauteing mushrooms and vegetables.",
            "And you start to be a little bit more adventurous and creative with what you can do with cast iron.",
            "It's kind of this progression where it unlocks you to be more creative in the kitchen."
        ]
    },
    "script_9": {
        "source": "audio/matt 1.m4a",
        "quotes": [
            "I've even timed it before. To clean up from making eggs, I swear, two minutes and twenty seconds, re-oiled and ready, back on the stove to cook again.",
            "It's way different than even the nuance of cleaning your stainless steel, where you have to scrub off like stuff on the bottom of it.",
            "Cleaning it and oiling it, it's just part of the process. It doesn't feel like a chore. It doesn't feel difficult.",
            "And the seasoning only gets darker and better over time.",
            "It's almost foolproof."
        ]
    }
}

print("Combining all complete scripts...\n")

# Process each script
for script_name, config in scripts_config.items():
    print(f"=" * 60)
    print(f"Processing {script_name.upper()}")
    print(f"Source: {config['source']}")
    print("=" * 60)

    # Load audio and transcribe
    print(f"Loading audio and transcribing {config['source']}...")
    extractor = AudioClipExtractor(config['source'], model_size="base")
    extractor.load_audio()
    extractor.transcribe()

    print(f"\nFinding {len(config['quotes'])} clips without padding...\n")

    combined = None
    clips_found = 0

    for i, quote in enumerate(config['quotes'], 1):
        print(f"Clip {i}: {quote[:60]}...")
        match = extractor.find_quote_timestamps(quote)

        if match:
            print(f"  ✓ Found at {match['start_time']:.1f}s - {match['end_time']:.1f}s")

            # Extract without padding
            start_ms = int(match['start_time'] * 1000)
            end_ms = int(match['end_time'] * 1000)

            clip = extractor.audio[start_ms:end_ms]

            if combined is None:
                combined = clip
            else:
                combined += clip

            duration = len(clip) / 1000
            print(f"  Added ({duration:.1f}s)")
            clips_found += 1
        else:
            print(f"  ⚠️  Not found")

        print()

    # Export combined audio
    if combined and clips_found > 0:
        total_duration = len(combined) / 1000
        print(f"Total: {clips_found}/{len(config['quotes'])} clips, {total_duration:.1f}s ({total_duration/60:.1f} min)")

        output_file = f"{script_name}/{script_name}_complete_clean.wav"
        print(f"Exporting: {output_file}")
        combined.export(output_file, format="wav")
        print(f"✅ Done!\n")
    else:
        print(f"❌ No clips extracted for {script_name}\n")

print("=" * 60)
print("All scripts processed!")
