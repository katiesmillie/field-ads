import json
import os

for script_num in range(1, 11):
    script_dir = f"script_{script_num}"
    metadata_file = os.path.join(script_dir, "metadata.json")

    if not os.path.exists(metadata_file):
        continue

    with open(metadata_file, 'r') as f:
        data = json.load(f)

    print(f"\n=== SCRIPT {script_num} ===")
    for clip in data['clips']:
        clip_num = clip['clip_number']
        if 'matched_text' in clip and clip['matched_text']:
            print(f"Clip {clip_num}: {clip['matched_text']}")
        else:
            print(f"Clip {clip_num}: [NO MATCHED TEXT - status: {clip.get('status')}]")
