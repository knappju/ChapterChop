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

    print("Saving clips around gaps...")
    metadata = []
    temp_dir, saved_paths = audio.save_clips_to_tempdir(
        gaps, y, sr,
        before_sec=buffer_before,
        after_sec=buffer_after,
        metadata_list=metadata
    )

    print(f"Saved {len(saved_paths)} clips to: {temp_dir}")
    
    return {
        "clips_dir": temp_dir,
        "metadata": metadata
    }


def save_metadata(metadata, output_path="gaps_metadata.json"):
    """
    Save the metadata JSON to a file.

    Args:
        metadata (list): List of metadata dicts.
        output_path (str): Path to the output JSON file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    print(f"Metadata saved to: {output_path}")