import json
import os
from difflib import SequenceMatcher

# Read matt 3 transcript
with open('matt 3.txt', 'r') as f:
    transcript = f.read().lower()

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

results = {}

for script_num in range(1, 11):
    script_dir = f"script_{script_num}"
    metadata_file = os.path.join(script_dir, "metadata.json")

    if not os.path.exists(metadata_file):
        continue

    with open(metadata_file, 'r') as f:
        data = json.load(f)

    results[f"script_{script_num}"] = []

    for clip in data['clips']:
        clip_num = clip['clip_number']
        quote = clip.get('quote', '')

        # Check if quote appears in transcript
        if quote.lower() in transcript:
            results[f"script_{script_num}"].append({
                'clip': clip_num,
                'found': True,
                'quote': quote[:100] + "..." if len(quote) > 100 else quote
            })
        else:
            # Check for partial matches
            words = quote.split()
            if len(words) > 5:
                first_part = ' '.join(words[:5]).lower()
                if first_part in transcript:
                    results[f"script_{script_num}"].append({
                        'clip': clip_num,
                        'found': 'PARTIAL',
                        'quote': quote[:100] + "..." if len(quote) > 100 else quote
                    })
                else:
                    results[f"script_{script_num}"].append({
                        'clip': clip_num,
                        'found': False,
                        'quote': quote[:100] + "..." if len(quote) > 100 else quote
                    })

# Print results
for script, clips in results.items():
    print(f"\n=== {script.upper()} ===")
    for clip_info in clips:
        status = "✓ FOUND" if clip_info['found'] == True else ("~ PARTIAL" if clip_info['found'] == 'PARTIAL' else "✗ NOT FOUND")
        print(f"Clip {clip_info['clip']}: {status}")
        print(f"   {clip_info['quote']}")
