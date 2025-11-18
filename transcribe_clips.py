import speech_recognition as sr
import os
import json
from pathlib import Path

# Initialize recognizer
recognizer = sr.Recognizer()

def transcribe_audio_file(audio_path):
    """Transcribe a single WAV file"""
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            return text
    except Exception as e:
        return f"Error: {str(e)}"

# Process all script folders
results = {}

for script_num in range(1, 11):
    script_dir = f"script_{script_num}"
    if not os.path.exists(script_dir):
        continue

    results[script_dir] = {}

    # Find all clip files (not complete files)
    clip_files = sorted([f for f in os.listdir(script_dir) if f.endswith('.wav') and 'complete' not in f])

    for clip_file in clip_files:
        clip_path = os.path.join(script_dir, clip_file)
        print(f"Transcribing {clip_path}...")
        transcription = transcribe_audio_file(clip_path)
        results[script_dir][clip_file] = transcription
        print(f"  Result: {transcription[:100]}...")

# Save results
with open('transcriptions.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nTranscriptions saved to transcriptions.json")
