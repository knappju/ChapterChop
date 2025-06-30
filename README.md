# ChapterChop

In Progress...

ChapterChop detects silent gaps in audiobook MP3s to identify chapter breaks. It extracts audio clips around these gaps and transcribes the surrounding audio using OpenAI’s Whisper model.

## Features

- Detects silence longer than 2 seconds  
- Saves audio clips around gaps  
- Transcribes audio before and after gaps with confidence scores  
- Outputs a JSON report with timestamps and transcripts  