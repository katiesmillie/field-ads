#!/usr/bin/env python3
"""
Extract ad quote audio clips from interview recordings.
Searches for 26 specific quotes across all audio files and extracts them.
"""

import whisper
import json
from pathlib import Path
from pydub import AudioSegment
from fuzzywuzzy import fuzz
import argparse

# All 26 ad quote candidates with their expected text
AD_QUOTES = {
    "heirloom_forever": "Not just because it's non toxic, not because it's non stick. But even if you bought all those, you know, in another type of pan with a coating, I don't think you'd be bringing it on adventures, bringing it to your friend's house. There's something really meaningful that it's an heirloom and it'll be with you forever. And I think that kind of starts to make you think about not consuming as much and buying things very intentionally that you think will also have that type of journey in your life.",

    "generation_to_generation": "I think because I wanted to figure out how to cook with cast iron because it felt like it was worth it. The knowledge that you might pass it down from generation to generation. You might bring it to a friend's house to do something with it and cook a meal that they couldn't cook before.",

    "buying_intentionally": "There's something really meaningful that it's an heirloom and it'll be with you forever. And I think that kind of starts to make you think about not consuming as much and buying things very intentionally that you think will also have that type of journey in your life.",

    "beautiful_object": "Once you hold it, once you feel it, like, if those. The way you have that set up in that room, it's like, literally, you could just hang it on the wall if that's all you want to do with it. It is a beautiful object. And I think when you're holding the less expensive ones, you can really tell the difference, and you can tell that it is heavier, it's harder to use, and maybe there's a sense of pride in the beauty of the object and then what you made that object into by the seasoning or the imperfections.",

    "pride_in_what_you_made": "It is a beautiful object. And I think when you're holding the less expensive ones, you can really tell the difference, and you can tell that it is heavier, it's harder to use, and maybe there's a sense of pride in the beauty of the object and then what you made that object into by the seasoning or the imperfections.",

    "more_meaningful": "And maybe there's a sense of pride in the beauty of the object and then what you made that object into by the seasoning or the imperfections. And I think that's why cast iron seems more meaningful and why once you start using it, you want to buy more or use it for everything.",

    "my_efforts_made_it_epic": "And it's funny how you can get attached to it like no other piece of cookware when someone else uses it because I made it. My. It's like my efforts made that pan epic.",

    "seasoning_perfect": "Sometimes I yell, I'll clean it, because I have a thing. Like, I love doing it. I. Yeah, I really like knowing that I cleaned it properly and reset it and it's ready to go for the next person. And that doesn't mean it's hard to do or special. It's just the way I've kept the seasoning perfect.",

    "it_unlocked_me": "So it made me want to cook more. And because it made me want to cook more, I started getting a lot more into it and a lot more comfortable. It unlocked me being really comfortable. And we do go car camping, and we do use the grill in the backyard.",

    "make_food_confident": "And now it's really meaningful to have my daughter, who is three, only know the version of someone who, like, literally can just, like, make food at any time and feel confident and make cool meals that we all like eating and not being intimidated by the tool that you're using, because I can use it for everything, and the cleanup is fast, and I just use it every morning and every night.",

    "never_tried_that": "I make scrambled eggs every morning. I've gotten really good at them. You want them fluffy? I can do anything. I can flip fried eggs in the air. I'd never tried that. I'd never had it so nonstick that I could just, like, flip them in the air.",

    "every_morning": "So it made me want to cook more. And because it made me want to cook more, I started getting a lot more into it and a lot more comfortable. I make scrambled eggs every morning. I've gotten really good at them.",

    "almost_every_day": "Even with Teflon, I wasn't enjoying or making fried eggs. I make a fried egg almost every day now. And with the smaller field skillets, you can literally crack an egg or two in some of them, and it keeps a perfect shape of a fried egg and you're done.",

    "her_dad_makes_food": "All of this just started happening, especially when I got a kid, because I wanted to have her know that her dad makes all this food, too, and not just moms. And I was cooking some stuff, but I just. It unlocked me being really comfortable.",

    "give_to_mom": "I gave my mom a number four skillet as a gift and she also isn't comfortable in the kitchen and I think by me doing was exciting to use what I think helped me in the kitchen to give to my mom and get her in that rhythm of maybe even just frying an egg every morning or making her life easier.",

    "two_minutes_twenty_seconds": "And so when I show people how easy it is, I've even timed it before the cleanup from making eggs. I swear, 2 minutes and 20 seconds, re oiled and ready, back on the stove to cook again. It's way different than even the nuance of cleaning your stainless steel.",

    "comfortable_using_it": "But it's literally cast iron, which is not precious. And so I think my excitement and my new knowledge, I pass it on to my mom and she's now comfortable using it and likes using it to fry eggs.",

    "worth_it": "I think because I wanted to figure out how to cook with cast iron because it felt like it was worth it.",

    "investing_worth_it": "You might bring it to a friend's house to do something with it and cook a meal that they couldn't cook before. I think it shows you that investing in it really makes it worth it. Not just because it's non toxic, not because it's non stick.",

    "brought_anywhere": "I just kind of made it, so. So I brought it anywhere I could. And when we go car camping, I would bring my Coleman stove.",

    "retaining_flavor": "So I think those gateways led me to cast iron chicken in the oven. It led me to sauteing mushrooms and vegetables. And I. The flavor you get out of it and cooking burgers and not having all the flavor go into the barbecue grill and retaining it all.",

    "almost_foolproof": "I think the more you cook with it, I've noticed that the seasoning gets darker and it's building more and more layers, and it's getting even more nonstick, which makes it almost foolproof that you can cook with it easily.",

    "tool_that_can_do_so_much": "You just get to seek out this whole new world of cooking that you never knew existed. So that is a lot of. Yeah. Just weird to get a tool that can do so much and to almost get to seek out this whole new world of cooking that you never knew existed.",

    "see_to_believe": "And until they really touch it and feel it and feel the weight or the smoothness of the bottom, they don't really understand in the handle and the way it feels in your hand, they don't really understand the difference in cooking on a surface that's maybe more rough. You got to see it to believe it, and you don't take my word for it.",

    "hold_it_feel_it": "Once you interact with this skillet, you're like. This is like. Like seeing. Once you hold it, once you feel it, like, if those. The way you have that set up in that room, it's like, literally, you could just hang it on the wall if that's all you want to do with it.",
}

def find_quote_in_segments(quote_text, segments, threshold=70):
    """Find the best matching segment for a quote using fuzzy matching."""
    best_match = None
    best_score = 0
    best_start = None
    best_end = None

    # Try different window sizes to find the quote
    for window_size in range(1, min(len(segments) + 1, 20)):
        for i in range(len(segments) - window_size + 1):
            window_segments = segments[i:i + window_size]
            window_text = " ".join([s["text"] for s in window_segments])

            score = fuzz.ratio(quote_text.lower(), window_text.lower())

            if score > best_score:
                best_score = score
                best_match = window_text
                best_start = window_segments[0]["start"]
                best_end = window_segments[-1]["end"]

    if best_score >= threshold:
        return {
            "matched_text": best_match,
            "score": best_score,
            "start": best_start,
            "end": best_end
        }

    return None

def extract_ad_quotes(audio_files, output_dir="ad_clips", model_size="base", padding_ms=500):
    """Extract all ad quote clips from audio files."""

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    print(f"Loading Whisper model '{model_size}'...")
    model = whisper.load_model(model_size)

    results = {}

    for audio_file in audio_files:
        print(f"\n{'='*60}")
        print(f"Processing: {audio_file}")
        print(f"{'='*60}\n")

        # Transcribe
        print("Transcribing audio...")
        result = model.transcribe(str(audio_file), word_timestamps=True)
        segments = result["segments"]

        # Try to find each quote
        for clip_name, quote_text in AD_QUOTES.items():
            # Skip if already found
            if clip_name in results:
                continue

            print(f"\nSearching for: {clip_name}...")
            match = find_quote_in_segments(quote_text, segments)

            if match:
                print(f"✓ Found! (score: {match['score']}%)")

                # Extract audio
                audio = AudioSegment.from_file(audio_file)
                start_ms = max(0, match['start'] * 1000 - padding_ms)
                end_ms = min(len(audio), match['end'] * 1000 + padding_ms)

                clip = audio[start_ms:end_ms]
                output_file = output_path / f"{clip_name}.wav"
                clip.export(output_file, format="wav")

                results[clip_name] = {
                    "source_file": str(audio_file),
                    "output_file": str(output_file),
                    "match_score": match['score'],
                    "matched_text": match['matched_text'],
                    "start_time": match['start'],
                    "end_time": match['end']
                }

                print(f"  Saved to: {output_file}")
            else:
                print(f"✗ Not found in this file")

    # Save metadata
    metadata_file = output_path / "extraction_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"Extracted {len(results)}/{len(AD_QUOTES)} clips")
    print(f"Output directory: {output_dir}")
    print(f"Metadata saved to: {metadata_file}")

    if len(results) < len(AD_QUOTES):
        print(f"\n⚠️  Missing {len(AD_QUOTES) - len(results)} clips:")
        for clip_name in AD_QUOTES:
            if clip_name not in results:
                print(f"  - {clip_name}")
        print("\nTry using a larger model with --model small or --model medium")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract ad quote clips from audio")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper model size (default: base)")
    parser.add_argument("--padding", type=int, default=500,
                       help="Padding in milliseconds (default: 500)")
    parser.add_argument("--output-dir", default="ad_clips",
                       help="Output directory (default: ad_clips)")

    args = parser.parse_args()

    # Find all audio files
    audio_files = list(Path("audio").glob("*.m4a"))

    if not audio_files:
        print("Error: No audio files found in audio/ directory")
        exit(1)

    print(f"Found {len(audio_files)} audio files to search")
    print(f"Looking for {len(AD_QUOTES)} ad quote clips\n")

    extract_ad_quotes(
        audio_files,
        output_dir=args.output_dir,
        model_size=args.model,
        padding_ms=args.padding
    )
