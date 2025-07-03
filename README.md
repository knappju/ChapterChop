# ChapterChop 📖🔊

⚠️🚧 **Disclaimer: Project Under Active Development** 🚧⚠️ 

ChapterChop is a Python-based tool for detecting silent gaps in audiobook files and extracting their surrounding audio for transcription. It's designed to help segment audiobooks into logical chapters or sections based on silence patterns, making it easier to organize, analyze, or navigate long-form audio content.

---

## Features

- 🎧 Supports `.mp3`, `.wav`, `.m4b` formats (via `ffmpeg`)
- ✂️ Automatically detects silent gaps above a configurable threshold
- 📄 Extracts buffered audio clips around each gap
- 🧠 Transcribes surrounding segments using OpenAI Whisper
- 📊 Outputs structured `.json` metadata with timestamps and confidence scores
- 🔍 Filters segments containing the word **"chapter"** to identify potential chapter breaks
- ⚙️ Cross-platform compatible (Windows/Linux/macOS with Python 3.13)

---

## Installation

1. **Clone the repository**:

```bash
git clone https://github.com/yourusername/ChapterChop.git
cd ChapterChop
```

## Usage
```
python -m chapterchop
```
