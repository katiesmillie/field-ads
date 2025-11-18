#!/usr/bin/env python3
"""
Audio Clip Extractor for Field Company Ad Scripts
Transcribes audio using Whisper and extracts specific quotes as separate clips.
"""

import os
import json
import whisper
from pydub import AudioSegment
from fuzzywuzzy import fuzz
import argparse
from pathlib import Path


class AudioClipExtractor:
    def __init__(self, audio_file, model_size="base"):
        """
        Initialize the extractor.

        Args:
            audio_file: Path to the audio file
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.audio_file = audio_file
        self.model_size = model_size
        self.model = None
        self.transcription = None
        self.audio = None

    def load_audio(self):
        """Load the audio file using pydub."""
        print(f"Loading audio file: {self.audio_file}")

        # Determine file format from extension
        file_ext = os.path.splitext(self.audio_file)[1].lower()
        if file_ext == '.m4a':
            self.audio = AudioSegment.from_file(self.audio_file, format="m4a")
        elif file_ext == '.mp3':
            self.audio = AudioSegment.from_mp3(self.audio_file)
        elif file_ext == '.wav':
            self.audio = AudioSegment.from_wav(self.audio_file)
        else:
            # Try to auto-detect
            self.audio = AudioSegment.from_file(self.audio_file)

        print(f"Audio loaded: {len(self.audio)/1000:.1f} seconds")

    def transcribe(self):
        """Transcribe the audio using Whisper with word-level timestamps."""
        print(f"Loading Whisper model: {self.model_size}")
        self.model = whisper.load_model(self.model_size)

        print("Transcribing audio (this may take a while)...")
        result = self.model.transcribe(
            self.audio_file,
            word_timestamps=True,
            verbose=False
        )

        self.transcription = result
        print("Transcription complete!")
        return result

    def find_quote_timestamps(self, quote_text, threshold=85):
        """
        Find the start and end timestamps for a quote in the transcription.

        Args:
            quote_text: The quote to search for
            threshold: Minimum similarity score (0-100) to consider a match

        Returns:
            Dictionary with start_time, end_time, matched_text, and score
        """
        if not self.transcription:
            raise ValueError("No transcription available. Run transcribe() first.")

        # Normalize the quote
        quote_normalized = quote_text.lower().strip()
        quote_words = quote_normalized.split()

        best_match = None
        best_score = 0

        # Extract all words with timestamps from segments
        all_words = []
        for segment in self.transcription['segments']:
            if 'words' in segment:
                all_words.extend(segment['words'])

        # Sliding window approach to find the best match
        window_size = len(quote_words)

        for i in range(len(all_words) - window_size + 1):
            window_words = all_words[i:i + window_size]
            window_text = ' '.join([w['word'].strip() for w in window_words])

            # Calculate similarity score
            score = fuzz.ratio(quote_normalized, window_text.lower())

            if score > best_score and score >= threshold:
                best_score = score
                best_match = {
                    'start_time': window_words[0]['start'],
                    'end_time': window_words[-1]['end'],
                    'matched_text': window_text,
                    'score': score
                }

        # If no good match found with strict window, try partial matching
        if not best_match:
            print(f"  No exact match found. Trying partial matching...")
            for segment in self.transcription['segments']:
                segment_text = segment['text'].lower().strip()
                score = fuzz.partial_ratio(quote_normalized, segment_text)

                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = {
                        'start_time': segment['start'],
                        'end_time': segment['end'],
                        'matched_text': segment['text'],
                        'score': score
                    }

        # Reject matches that are too short (likely false positives)
        if best_match and len(best_match['matched_text'].split()) < 3:
            print(f"  ⚠️  Match too short, rejecting: '{best_match['matched_text']}'")
            return None

        return best_match

    def extract_clip(self, start_time, end_time, output_file, padding_ms=500):
        """
        Extract a clip from the audio file.

        Args:
            start_time: Start time in seconds
            end_time: End time in seconds
            output_file: Path to save the extracted clip
            padding_ms: Padding in milliseconds before and after
        """
        if not self.audio:
            self.load_audio()

        # Convert to milliseconds and add padding
        start_ms = max(0, int(start_time * 1000) - padding_ms)
        end_ms = min(len(self.audio), int(end_time * 1000) + padding_ms)

        # Extract the clip
        clip = self.audio[start_ms:end_ms]

        # Export as WAV
        clip.export(output_file, format="wav")

        return {
            'start_ms': start_ms,
            'end_ms': end_ms,
            'duration_ms': end_ms - start_ms
        }

    def process_script(self, script_name, quotes, output_dir, padding_ms=500):
        """
        Process an entire script by extracting all quotes.

        Args:
            script_name: Name of the script (e.g., "script_5")
            quotes: List of quote strings to extract
            output_dir: Directory to save clips
            padding_ms: Padding in milliseconds

        Returns:
            Dictionary with metadata about all extracted clips
        """
        # Create output directory
        script_dir = Path(output_dir) / script_name
        script_dir.mkdir(parents=True, exist_ok=True)

        # Ensure audio is loaded
        if not self.audio:
            self.load_audio()

        # Ensure we have a transcription
        if not self.transcription:
            self.transcribe()

        metadata = {
            'script_name': script_name,
            'source_file': self.audio_file,
            'clips': []
        }

        print(f"\nProcessing {script_name}...")
        print(f"Extracting {len(quotes)} clips...\n")

        for idx, quote in enumerate(quotes, 1):
            print(f"Clip {idx}/{len(quotes)}: {quote[:50]}...")

            # Find the quote in the transcription
            match = self.find_quote_timestamps(quote)

            if not match:
                print(f"  ⚠️  WARNING: Could not find quote in transcription")
                metadata['clips'].append({
                    'clip_number': idx,
                    'quote': quote,
                    'status': 'not_found'
                })
                continue

            print(f"  ✓ Found match (score: {match['score']}%)")
            print(f"    Matched: {match['matched_text'][:60]}...")

            # Extract the clip
            clip_filename = f"{script_name}_clip_{idx:02d}.wav"
            clip_path = script_dir / clip_filename

            clip_info = self.extract_clip(
                match['start_time'],
                match['end_time'],
                str(clip_path),
                padding_ms
            )

            print(f"    Saved: {clip_filename}")
            print(f"    Duration: {clip_info['duration_ms']/1000:.1f}s\n")

            # Add to metadata
            metadata['clips'].append({
                'clip_number': idx,
                'filename': clip_filename,
                'quote': quote,
                'matched_text': match['matched_text'],
                'match_score': match['score'],
                'start_time_seconds': match['start_time'],
                'end_time_seconds': match['end_time'],
                'start_ms': clip_info['start_ms'],
                'end_ms': clip_info['end_ms'],
                'duration_ms': clip_info['duration_ms'],
                'padding_ms': padding_ms,
                'status': 'success'
            })

        # Save metadata
        metadata_path = script_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Metadata saved: {metadata_path}")

        # Save script text file
        script_text_path = script_dir / 'script.txt'
        with open(script_text_path, 'w') as f:
            f.write(f"{script_name.upper()}\n")
            f.write("=" * 60 + "\n\n")
            for idx, quote in enumerate(quotes, 1):
                f.write(f"Clip {idx}:\n")
                f.write(f"{quote}\n\n")

        print(f"✓ Script text saved: {script_text_path}")

        # Print summary
        successful = sum(1 for c in metadata['clips'] if c['status'] == 'success')
        print(f"\n{'='*60}")
        print(f"SUMMARY: {successful}/{len(quotes)} clips extracted successfully")
        print(f"Output directory: {script_dir}")
        print(f"{'='*60}\n")

        return metadata


def main():
    parser = argparse.ArgumentParser(
        description='Extract audio clips from interview recordings'
    )
    parser.add_argument(
        'audio_file',
        help='Path to the audio file'
    )
    parser.add_argument(
        '--script',
        default='script_5',
        help='Script name (default: script_5)'
    )
    parser.add_argument(
        '--output-dir',
        default='.',
        help='Output directory (default: current directory)'
    )
    parser.add_argument(
        '--padding',
        type=int,
        default=500,
        help='Padding in milliseconds (default: 500)'
    )
    parser.add_argument(
        '--model',
        default='base',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        help='Whisper model size (default: base)'
    )

    args = parser.parse_args()

    # All script quotes
    script_1_quotes = [
        "I had had other skillets like Lodge, cheaper, and I never felt connected to it enough to try to figure it out as much as I did with Field, because it felt so beautiful and smooth.",
        "And so I think something about that inspired me.",
        "I started making scrambled eggs in it. And it was easy and they were nonstick, and it started to give me more and more confidence.",
        "I make a fried egg almost every day now. And with the smaller field skillets, you can literally crack an egg or two in some of them, and it keeps a perfect shape of a fried egg and you're done.",
        "Cast iron has changed my life. I'm a better dad."
    ]

    script_2_quotes = [
        "I have so much pride in figuring this thing out. That wasn't actually that hard. I just thought it was going to be.",
        "I think the start of cooking with cast iron was always scrambled eggs. It seems like that seems to be the test of what non stick means to someone.",
        "And I think once you figure out that you can get a nonstick surface from cast iron, then you're not, you know, worried.",
        "So I think those gateways led me to cast iron chicken in the oven. It led me to sauteing mushrooms and vegetables.",
        "I literally never used three pans at once, or even two. And just the connection to it made me start getting more creative.",
        "It really does make you have some behavioral change."
    ]

    script_3_quotes = [
        "Cast iron is kind of a gateway drug to the more intentional... a life worth living.",
        "I think because I wanted to figure out how to cook with cast iron because it felt like it was worth it. The knowledge that you might pass it down from generation to generation.",
        "You might bring it to a friend's house to do something with it and cook a meal that they couldn't cook before. I think it shows you that investing in it really makes it worth it.",
        "Not just because it's non toxic, not because it's non stick. But even if you bought all those, you know, in another type of pan with a coating, I don't think you'd be bringing it on adventures, bringing it to your friend's house.",
        "There's something really meaningful that it's an heirloom and it'll be with you forever. And I think that kind of starts to make you think about not consuming as much and buying things very intentionally that you think will also have that type of journey in your life.",
        "It unlocked me being really comfortable. And we do go car camping, and we do use the grill in the backyard."
    ]

    script_4_quotes = [
        "I think the assumption is like, it's like extra work.",
        "I've even timed it before the cleanup from making eggs. I swear, 2 minutes and 20 seconds, re oiled and ready, back on the stove to cook again.",
        "It's way different than even the nuance of cleaning your stainless steel.",
        "I realized that you didn't need to be so precious. Every time I cooked the seasoning and all those changes happen naturally.",
        "I think by cooking with it, I've noticed that the seasoning gets darker and it's building more and more layers, and it's getting even more nonstick.",
        "Which makes it almost foolproof that you can cook with it easily every time."
    ]

    script_5_quotes = [
        "And now it's really meaningful to have my daughter, who is three, only know the version of someone who, like, literally can just, like, make food at any time and feel confident.",
        "And make cool meals that we all like eating and not being intimidated by the tool that you're using, because I can use it for everything, and the cleanup is fast, and I just use it every morning and every night.",
        "I make a fried egg almost every day now. And with the smaller field skillets, you can literally crack an egg or two in some of them, and it keeps a perfect shape of a fried egg and you're done.",
        "I think the start of cooking with cast iron was always scrambled eggs.",
        "Cast iron has changed my life. I'm a better dad."
    ]

    script_6_quotes = [
        "Usually when people bring up cast iron, they tell me that they found a skillet that's cheaper, and they wonder what the difference in the price would be.",
        "And until they really touch it and feel it and feel the weight or the smoothness of the bottom, they don't really understand in the handle and the way it feels in your hand, they don't really understand the difference in cooking on a surface that's maybe more rough.",
        "Once you hold it, once you feel it, like, if those. The way you have that set up in that room, it's like, literally, you could just hang it on the wall if that's all you want to do with it. It is a beautiful object.",
        "And I think when you're holding the less expensive ones, you can really tell the difference, and you can tell that it is heavier, it's harder to use.",
        "And maybe there's a sense of pride in the beauty of the object and then what you made that object into by the seasoning or the imperfections.",
        "And I think that's why cast iron seems more meaningful and why once you start using it, you want to buy more or use it for everything."
    ]

    script_7_quotes = [
        "A year ago my wife was the one who cooked and I would make a few meals. But when I cook, it's meat sauce and spaghetti, which is once a week.",
        "We've always been against toxic pans and I never would buy the ceramic ones or any of the other brands that were saying they were non toxic because it still feel... We were already using non toxic pans and I would never buy the ceramic coated ones, even though it seemed like the easiest way to get non stick stick.",
        "But I eventually got some really nice stainless steel pans and I really perfected the preheat, the oil or whatever and cooking. So I was already getting more comfortable with cooking because of stainless steel.",
        "But stainless steel doesn't make you feel like you're. You're not bringing it with you camping. You're not. It's probably not going to last your whole life because you're going to make it gnarly. It just wasn't the same type of experience.",
        "By knowing that everything I cooked on a cast iron was going to be a part of its journey or I could reset it at any time.",
        "So I already started getting into cooking because of stainless steel and I was getting more comfortable with non stick that way. And after Teflon was banned from this house, I never tried any other surface because I knew they were all going to be scratched."
    ]

    script_8_quotes = [
        "I gifted my mom a number four field skillet for her birthday which is not true. I just gifted it to her.",
        "I gave my mom a number four skillet as a gift and she also isn't comfortable in the kitchen and I think by me doing was exciting to use what I think helped me in the kitchen to give to my mom and get her in that rhythm of maybe even just frying an egg every morning or making her life easier.",
        "And I think she went through the same type of experience where you might think it's way harder than it is and I think by telling her you can't do it wrong and as long as you follow the preheat step in the oil step. Like, cooking with cast iron is very easy.",
        "And I do remember her first impression of after she cooked, wondering if she did it wrong. Like, the same fears that I had.",
        "And so I think my excitement and my new knowledge, I pass it on to my mom and she's now comfortable using it and likes using it to fry eggs."
    ]

    script_9_quotes = [
        "I think that's why cast iron seems more meaningful and why once you start using it, you want to buy more or use it for everything.",
        "I feel like the adventure cooking. I'm asking you a question almost while I say it, but the adventurous cooking is more of being comfortable with cooking. The adventure, I guess, is trying to sear the steak that I've never done.",
        "I think the adventurous cooking also when you get into cast iron is trusting that you can go from pancakes and then just throw some eggs on it.",
        "And, you know, the same way you'd cook at a diner or a really epic restaurant where they're using a griddle, you realize you can just throw anything on it and it doesn't matter how clean clean it is or if you clean it in between.",
        "And that is another really awesome benefit of using the griddles and cast iron in general is you can make a ton of stuff and you don't have to be precious about it."
    ]

    script_10_quotes = [
        "Sometimes I yell, I'll clean it, because I have a thing. Like, I love doing it.",
        "I really like knowing that I cleaned it properly and reset it and it's ready to go for the next person. And that doesn't mean it's hard to do or special. It's just the way I've kept the seasoning perfect.",
        "You take a pride in cast iron, where you've worked so hard on the seasoning, and you're really proud of it, and it's even and perfect.",
        "It's like my efforts made that pan epic.",
        "I can clean that thing and be done with it after using it in less than two minutes. No different than scrubbing any other pan."
    ]

    # Map of all scripts
    scripts = {
        'script_1': script_1_quotes,
        'script_2': script_2_quotes,
        'script_3': script_3_quotes,
        'script_4': script_4_quotes,
        'script_5': script_5_quotes,
        'script_6': script_6_quotes,
        'script_7': script_7_quotes,
        'script_8': script_8_quotes,
        'script_9': script_9_quotes,
        'script_10': script_10_quotes,
    }

    if args.script not in scripts:
        print(f"Error: Script '{args.script}' not defined.")
        print(f"Available scripts: {', '.join(scripts.keys())}")
        return 1

    # Create extractor
    extractor = AudioClipExtractor(args.audio_file, model_size=args.model)

    # Process the script
    extractor.process_script(
        args.script,
        scripts[args.script],
        args.output_dir,
        padding_ms=args.padding
    )

    return 0


if __name__ == '__main__':
    exit(main())
