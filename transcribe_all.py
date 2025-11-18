#!/usr/bin/env python3
import speech_recognition as sr
import json
import os

recognizer = sr.Recognizer()

clips = [
    {'script': 1, 'num': 1, 'file': 'script_1/script_1_clip_01a.wav'},
    {'script': 1, 'num': 2, 'file': 'script_1/script_1_clip_02a.wav'},
    {'script': 1, 'num': 3, 'file': 'script_1/script_1_clip_03a.wav'},
    {'script': 1, 'num': 4, 'file': 'script_1/script_1_clip_04.wav'},
    {'script': 1, 'num': 5, 'file': 'script_1/script_1_clip_05.wav'},
    {'script': 2, 'num': 2, 'file': 'script_2/script_2_clip_02.wav'},
    {'script': 2, 'num': 3, 'file': 'script_2/script_2_clip_03.wav'},
    {'script': 2, 'num': 4, 'file': 'script_2/script_2_clip_04.wav'},
    {'script': 2, 'num': 5, 'file': 'script_2/script_2_clip_05a.wav'},
    {'script': 3, 'num': 1, 'file': 'script_3/script_3_clip_01.wav'},
    {'script': 3, 'num': 2, 'file': 'script_3/script_3_clip_02.wav'},
    {'script': 3, 'num': 3, 'file': 'script_3/script_3_clip_03.wav'},
    {'script': 3, 'num': 4, 'file': 'script_3/script_3_clip_04.wav'},
    {'script': 3, 'num': 5, 'file': 'script_3/script_3_clip_05.wav'},
    {'script': 3, 'num': 6, 'file': 'script_3/script_3_clip_06.wav'},
    {'script': 4, 'num': 2, 'file': 'script_4/script_4_clip_02.wav'},
    {'script': 4, 'num': 3, 'file': 'script_4/script_4_clip_03.wav'},
    {'script': 4, 'num': 4, 'file': 'script_4/script_4_clip_04.wav'},
    {'script': 4, 'num': 5, 'file': 'script_4/script_4_clip_05.wav'},
    {'script': 4, 'num': 6, 'file': 'script_4/script_4_clip_06.wav'},
    {'script': 5, 'num': 1, 'file': 'script_5/script_5_clip_01.wav'},
    {'script': 5, 'num': 2, 'file': 'script_5/script_5_clip_02.wav'},
    {'script': 5, 'num': 3, 'file': 'script_5/script_5_clip_03.wav'},
    {'script': 5, 'num': 4, 'file': 'script_5/script_5_clip_04.wav'},
    {'script': 5, 'num': 5, 'file': 'script_5/script_5_clip_05.wav'},
    {'script': 6, 'num': 1, 'file': 'script_6/script_6_clip_01.wav'},
    {'script': 6, 'num': 2, 'file': 'script_6/script_6_clip_02.wav'},
    {'script': 6, 'num': 3, 'file': 'script_6/script_6_clip_03.wav'},
    {'script': 6, 'num': 4, 'file': 'script_6/script_6_clip_04.wav'},
    {'script': 6, 'num': 5, 'file': 'script_6/script_6_clip_05.wav'},
    {'script': 6, 'num': 6, 'file': 'script_6/script_6_clip_06.wav'},
    {'script': 7, 'num': 1, 'file': 'script_7/script_7_clip_01.wav'},
    {'script': 7, 'num': 2, 'file': 'script_7/script_7_clip_02.wav'},
    {'script': 7, 'num': 3, 'file': 'script_7/script_7_clip_03.wav'},
    {'script': 7, 'num': 4, 'file': 'script_7/script_7_clip_04.wav'},
    {'script': 7, 'num': 5, 'file': 'script_7/script_7_clip_05.wav'},
    {'script': 7, 'num': 6, 'file': 'script_7/script_7_clip_06.wav'},
    {'script': 8, 'num': 1, 'file': 'script_8/script_8_clip_01.wav'},
    {'script': 8, 'num': 2, 'file': 'script_8/script_8_clip_02.wav'},
    {'script': 8, 'num': 3, 'file': 'script_8/script_8_clip_03.wav'},
    {'script': 8, 'num': 4, 'file': 'script_8/script_8_clip_04.wav'},
    {'script': 8, 'num': 5, 'file': 'script_8/script_8_clip_05.wav'},
    {'script': 9, 'num': 1, 'file': 'script_9/script_9_clip_01.wav'},
    {'script': 9, 'num': 2, 'file': 'script_9/script_9_clip_02.wav'},
    {'script': 9, 'num': 3, 'file': 'script_9/script_9_clip_03.wav'},
    {'script': 9, 'num': 4, 'file': 'script_9/script_9_clip_04.wav'},
    {'script': 9, 'num': 5, 'file': 'script_9/script_9_clip_05.wav'},
    {'script': 10, 'num': 1, 'file': 'script_10/script_10_clip_01.wav'},
    {'script': 10, 'num': 2, 'file': 'script_10/script_10_clip_02.wav'},
    {'script': 10, 'num': 3, 'file': 'script_10/script_10_clip_03.wav'},
    {'script': 10, 'num': 4, 'file': 'script_10/script_10_clip_04.wav'},
    {'script': 10, 'num': 5, 'file': 'script_10/script_10_clip_05a.wav'}
]

results = {}

for i, clip in enumerate(clips):
    print(f"[{i+1}/{len(clips)}] Transcribing Script {clip['script']}, Clip {clip['num']}...")

    try:
        with sr.AudioFile(clip['file']) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)

            if clip['script'] not in results:
                results[clip['script']] = []

            results[clip['script']].append({
                'num': clip['num'],
                'file': clip['file'],
                'text': text
            })

            print(f"   ✓ {text[:80]}...")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        if clip['script'] not in results:
            results[clip['script']] = []
        results[clip['script']].append({
            'num': clip['num'],
            'file': clip['file'],
            'text': f"[Transcription error: {str(e)}]"
        })

# Save to JSON
with open('transcriptions.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Done! Transcriptions saved to transcriptions.json")
