#!/usr/bin/env python3
"""
Map existing extracted clips to ad_clips directory based on text matching.
"""

import json
import shutil
from pathlib import Path
from fuzzywuzzy import fuzz

# Ad quotes we're looking for
AD_QUOTES = {
    "heirloom_forever": "There's something really meaningful that it's an heirloom and it'll be with you forever",
    "generation_to_generation": "The knowledge that you might pass it down from generation to generation",
    "buying_intentionally": "buying things very intentionally that you think will also have that type of journey in your life",
    "beautiful_object": "It is a beautiful object",
    "pride_in_what_you_made": "sense of pride in the beauty of the object",
    "more_meaningful": "why cast iron seems more meaningful",
    "my_efforts_made_it_epic": "my efforts made that pan epic",
    "seasoning_perfect": "the way I've kept the seasoning perfect",
    "it_unlocked_me": "It unlocked me being really comfortable",
    "make_food_confident": "make food at any time and feel confident",
    "never_tried_that": "I'd never tried that",
    "every_morning": "I make scrambled eggs every morning",
    "almost_every_day": "I make a fried egg almost every day now",
    "her_dad_makes_food": "her dad makes all this food, too, and not just moms",
    "give_to_mom": "give to my mom",
    "two_minutes_twenty_seconds": "2 minutes and 20 seconds",
    "comfortable_using_it": "comfortable using it and likes using it to fry eggs",
    "worth_it": "it felt like it was worth it",
    "investing_worth_it": "investing in it really makes it worth it",
    "brought_anywhere": "I brought it anywhere I could",
    "retaining_flavor": "retaining it all",
    "almost_foolproof": "almost foolproof",
    "tool_that_can_do_so_much": "a tool that can do so much",
    "see_to_believe": "see it to believe it",
    "hold_it_feel_it": "Once you hold it, once you feel it",
}

def find_best_match(clip_text, threshold=60):
    """Find the best matching ad quote for a clip."""
    best_match = None
    best_score = 0

    for ad_name, ad_key_phrase in AD_QUOTES.items():
        score = fuzz.partial_ratio(ad_key_phrase.lower(), clip_text.lower())
        if score > best_score:
            best_score = score
            best_match = ad_name

    if best_score >= threshold:
        return best_match, best_score
    return None, 0

def map_clips():
    """Map existing clips to ad_clips directory."""

    output_dir = Path("ad_clips")
    output_dir.mkdir(exist_ok=True)

    mapped = {}
    script_dirs = sorted(Path(".").glob("script_*"))

    print(f"Found {len(script_dirs)} script directories")
    print(f"Looking for {len(AD_QUOTES)} ad quotes\n")

    for script_dir in script_dirs:
        script_file = script_dir / "script.txt"
        if not script_file.exists():
            continue

        print(f"\nProcessing {script_dir.name}...")

        # Read script file
        with open(script_file, 'r') as f:
            content = f.read()

        # Split into clips
        clips = content.split("Clip ")

        for i, clip_content in enumerate(clips[1:], 1):  # Skip first empty split
            # Extract clip text
            lines = clip_content.strip().split('\n')
            clip_text = ' '.join(lines[1:])  # Skip clip number line

            # Find matching audio file
            wav_files = list(script_dir.glob(f"*_clip_{i:02d}*.wav"))
            if not wav_files:
                continue

            wav_file = wav_files[0]

            # Find best matching ad quote
            match_name, score = find_best_match(clip_text)

            if match_name and match_name not in mapped:
                print(f"  ✓ Clip {i}: {match_name} (score: {score}%)")

                # Copy to ad_clips
                dest_file = output_dir / f"{match_name}.wav"
                shutil.copy2(wav_file, dest_file)

                mapped[match_name] = {
                    "source": str(wav_file),
                    "score": score,
                    "clip_text": clip_text[:100] + "..."
                }

    # Save mapping
    with open(output_dir / "mapping.json", 'w') as f:
        json.dump(mapped, f, indent=2)

    print(f"\n{'='*60}")
    print(f"MAPPING COMPLETE")
    print(f"{'='*60}")
    print(f"Mapped {len(mapped)}/{len(AD_QUOTES)} clips")
    print(f"Output directory: ad_clips/")

    if len(mapped) < len(AD_QUOTES):
        print(f"\n⚠️  Missing {len(AD_QUOTES) - len(mapped)} clips:")
        for ad_name in AD_QUOTES:
            if ad_name not in mapped:
                print(f"  - {ad_name}")

    return mapped

if __name__ == "__main__":
    try:
        import fuzzywuzzy
    except ImportError:
        print("Error: fuzzywuzzy not installed")
        print("Run: pip3 install fuzzywuzzy --user")
        exit(1)

    map_clips()
