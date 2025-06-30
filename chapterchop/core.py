"""
Core logic of ChapterChop.
"""
import os
import subprocess
from . import audio


"""
Load audio and print detected silence gaps to the console.
Args:
    audio_path (str): Path to the input audio file.
    min_gap_seconds (float): Minimum silence duration to qualify as a gap.
"""
def test_gap_detection(audio_path, min_gap_seconds=2.0):

    #make sure it knows where ffmpeg is.
    if not audio.test_ffmpeg():
        sys.exit("FFmpeg test failed! Please install or bundle ffmpeg properly.")

    print(f"\nLoading audio file: {audio_path}")
    
    y, sr = audio.load_audio(audio_path)
    duration = len(y) / sr
    print(f"Loaded audio: sample rate = {sr}, duration = {duration:.2f} seconds")

    print(f"\nDetecting gaps longer than {min_gap_seconds} seconds...")
    gaps = audio.detect_silence_gaps(y, sr, min_gap_seconds=min_gap_seconds)

    if not gaps:
        print("No silence gaps detected.")
    else:
        print(f"Found {len(gaps)} silence gap(s):")
        for i, (start, end) in enumerate(gaps, 1):
            print(f"  Gap {i}: {start:.2f}s → {end:.2f}s  (duration: {end - start:.2f}s)")

