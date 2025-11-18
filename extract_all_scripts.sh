#!/bin/bash
# Extract all 10 scripts from all 3 audio files

echo "=================================="
echo "Field Company - Extract All Scripts"
echo "=================================="
echo ""

# Audio files
audio_files=("audio/matt 1.m4a" "audio/matt 2.m4a" "audio/matt 3.m4a")

# Scripts to process
scripts=("script_1" "script_2" "script_3" "script_4" "script_5" "script_6" "script_7" "script_8" "script_9" "script_10")

total_scripts=${#scripts[@]}
total_audio=${#audio_files[@]}
total_combinations=$((total_scripts * total_audio))
current=0

echo "Processing $total_scripts scripts across $total_audio audio files..."
echo "Total operations: $total_combinations"
echo ""

# Process each script
for script in "${scripts[@]}"; do
    echo "========================================"
    echo "Processing $script"
    echo "========================================"
    echo ""

    # Try each audio file
    for audio in "${audio_files[@]}"; do
        current=$((current + 1))
        echo "[$current/$total_combinations] Trying: $script from $audio"

        # Run extraction (will skip if no matches found)
        python3 extract_clips.py "$audio" --script "$script" 2>&1 | grep -E "(✓|⚠️|SUMMARY)" || true

        echo ""
    done

    echo ""
done

echo "=================================="
echo "Extraction Complete!"
echo "=================================="
echo ""
echo "Results:"
ls -d script_* 2>/dev/null | while read dir; do
    clips=$(ls "$dir"/*.wav 2>/dev/null | wc -l | tr -d ' ')
    echo "  $dir: $clips clips"
done
