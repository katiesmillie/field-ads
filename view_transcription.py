#!/usr/bin/env python3
"""
View the Whisper transcription of an audio file
"""

import whisper
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description='View audio transcription')
    parser.add_argument('audio_file', help='Path to the audio file')
    parser.add_argument('--model', default='base', help='Whisper model size')
    parser.add_argument('--output', help='Output file for full transcription (JSON)')
    parser.add_argument('--search', help='Search for a phrase in the transcription')

    args = parser.parse_args()

    print(f"Loading Whisper model: {args.model}")
    model = whisper.load_model(args.model)

    print(f"Transcribing audio: {args.audio_file}")
    result = model.transcribe(args.audio_file, word_timestamps=True, verbose=False)

    print("\n" + "="*80)
    print("FULL TRANSCRIPTION")
    print("="*80 + "\n")

    for i, segment in enumerate(result['segments']):
        timestamp = f"[{segment['start']:.1f}s - {segment['end']:.1f}s]"
        print(f"{timestamp} {segment['text']}")

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n✓ Full transcription saved to: {args.output}")

    if args.search:
        print(f"\n" + "="*80)
        print(f"SEARCH RESULTS FOR: {args.search}")
        print("="*80 + "\n")

        search_lower = args.search.lower()
        found = False

        for segment in result['segments']:
            if search_lower in segment['text'].lower():
                found = True
                timestamp = f"[{segment['start']:.1f}s - {segment['end']:.1f}s]"
                print(f"{timestamp} {segment['text']}")

        if not found:
            print("No matches found.")

if __name__ == '__main__':
    main()
