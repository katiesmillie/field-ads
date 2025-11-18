# Field Company Ad Clip Extractor

Extracts specific quotes from Matt's interview recordings to create ad scripts.

## Setup

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Install ffmpeg (if not already installed):**
   ```bash
   brew install ffmpeg
   ```

3. **Audio files are already in `audio/` folder:**
   - `audio/matt 1.m4a` (23MB - main interview)
   - `audio/matt 2.m4a` (3MB)
   - `audio/matt 3.m4a` (2.5MB)

## Quick Start - Extract All Scripts

**To extract all 10 scripts from all audio files at once:**

```bash
./extract_all_scripts.sh
```

This will:
- Process all 10 scripts (script_1 through script_10)
- Search for clips in all 3 audio files
- Extract clips with 500ms padding
- Create folders for each script with clips, metadata, and script text
- Takes about 30-45 minutes total

**Output:**
```
script_1/
├── script_1_clip_01.wav
├── script_1_clip_02.wav
├── ...
├── metadata.json
└── script.txt

script_2/
├── script_2_clip_01.wav
├── ...
└── metadata.json

... (script_3 through script_10)
```

## Manual Extraction - Single Script

### Extract one specific script:

```bash
python3 extract_clips.py "audio/matt 1.m4a" --script script_5
```

Available scripts: `script_1`, `script_2`, `script_3`, `script_4`, `script_5`, `script_6`, `script_7`, `script_8`, `script_9`, `script_10`

### Output for each script:

```
script_5/
├── script_5_clip_01.wav
├── script_5_clip_02.wav
├── script_5_clip_03.wav
├── ...
├── metadata.json      (timestamps and match info)
└── script.txt         (full script text for reference)
```

## Options

- `--model` - Whisper model size (tiny, base, small, medium, large)
  - `tiny` - Fastest, less accurate
  - `base` - Good balance (default)
  - `small` - Better accuracy, slower
  - `medium` - Even better, much slower
  - `large` - Best accuracy, very slow

- `--padding` - Padding in milliseconds (default: 500)
- `--output-dir` - Where to save clips (default: current directory)

## Examples

```bash
# Use larger model for better accuracy
python extract_clips.py audio/4484-Atwood-Rd.m4a --script script_5 --model small

# Custom padding
python extract_clips.py audio/4484-Atwood-Rd.m4a --script script_5 --padding 1000

# Save to specific directory
python extract_clips.py audio/4484-Atwood-Rd.m4a --script script_5 --output-dir ~/Desktop
```

## Troubleshooting

**If clips aren't found:**
- The script uses fuzzy matching (70% similarity threshold)
- Try a larger Whisper model: `--model small` or `--model medium`
- Check the console output to see what text was matched
- Review `metadata.json` to see match scores

**If transcription is slow:**
- Use a smaller model: `--model tiny`
- The first run downloads the model (1-2GB)
- Subsequent runs are faster

## Adding More Scripts

Edit `extract_clips.py` and add to the `scripts` dictionary:

```python
scripts = {
    'script_5': script_5_quotes,
    'script_1': [
        "Quote 1...",
        "Quote 2...",
        # etc.
    ],
}
```
