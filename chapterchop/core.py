"""
Core logic of ChapterChop.
"""
import os
import subprocess
from . import audio
import json

"""
Orchestrates the full gap detection and clip saving process.

Args:
    audio_path (str): Path to the input audio file (.mp3, .wav, .m4b).
    silence_threshold (float): Volume threshold to consider as silence.
    min_gap_sec (float): Minimum duration of silence to be considered a gap.
    buffer_before (float): Seconds before each gap to include in the clip.
    buffer_after (float): Seconds after each gap to include in the clip.
Returns:
    dict: A dictionary containing the output directory and metadata list.
"""
def process_audio_file(audio_path, silence_threshold=0.05, min_gap_sec=3.0, buffer_before=2.0, buffer_after=2.0):

    print(f"Loading audio: {audio_path}")
    y, sr = audio.load_audio(audio_path)

    print("Detecting silence...")
    gaps = audio.detect_silence_gaps(
        y, sr,
        min_gap_seconds=min_gap_sec,
        silence_threshold=silence_threshold
    )
    print(f"Found {len(gaps)} gap(s)")
    
    segments = []

    for i, (gap_start, gap_end) in enumerate(gaps, 1):
        # create a local copy of the desired gap areas.
        segment, seg_sr = audio.extract_buffered_segment(
            y, sr,
            gap_start=gap_start,
            gap_end=gap_end,
            buffer_before=2.0,
            buffer_after=2.0
        )
        # Add to the list
        segments.append({
            "index": i,
            "gap_start": gap_start,
            "gap_end": gap_end,
            "buffered_segment": segment,
            "sample_rate": seg_sr
        })

    print(f"Extracted {len(segments)} total segments.")
        

