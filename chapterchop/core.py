"""
Core logic of ChapterChop.
"""
from . import audio
from . import transcription
import json
import os

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

    total = len(segments)
    filtered_segments = []

    for i, seg in enumerate(segments, 1):
        print(f"Transcribing segment {i} of {total}...")

        transcript, confidence = transcription.transcribe_segment(seg)
        seg["transcript"] = transcript
        seg["confidence"] = round(confidence, 3)
        
        if "chapter" in transcript.lower():
            filtered_segments.append(seg)
    
    output_json_path = os.path.join("./examples", "Segments.json")
    save_segments_to_json(segments, output_json_path)

    output_json_path = os.path.join("./examples", "FilteredSegments.json")
    save_segments_to_json(filtered_segments, output_json_path)

    total_segments = len(filtered_segments)

    for i, segment in enumerate(filtered_segments):
        if i == 0:
            start_time = 0
            end_time = segment["gap_start"] + 1.0
            output_path = f"examples/{i+9}.mp3"
            audio.trim_audio_ffmpeg(audio_path, output_path, seconds_to_timestamp(start_time), seconds_to_timestamp(end_time))
            start_time = segment["gap_end"] - 1.0
            end_time = filtered_segments[i + 1]["gap_start"] + 1.0
        elif i == total_segments - 1:
            start_time = segment["gap_end"] - 1.0
            end_time = audio.get_audio_duration(audio_path)
        else:
            start_time = segment["gap_end"] - 1.0
            end_time = filtered_segments[i + 1]["gap_start"] + 1.0

        output_path = f"examples/{i+10}.mp3"
        audio.trim_audio_ffmpeg(audio_path, output_path, seconds_to_timestamp(start_time), seconds_to_timestamp(end_time))
        
def seconds_to_timestamp(seconds):
    """Convert float seconds to HH:MM:SS.mmm format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:06.3f}"

def save_segments_to_json(segments, output_path):
    # Prepare clean, serializable segment data
    serializable_segments = []
    for seg in segments:
        serializable_segments.append({
            "index": seg.get("index"),
            "gap_start": round(seg.get("gap_start", 0), 3),
            "gap_end": round(seg.get("gap_end", 0), 3),
            "transcript": seg.get("transcript", ""),
            "confidence": seg.get("confidence", None)
        })

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serializable_segments, f, indent=4, ensure_ascii=False)

    print(f"Segments saved to JSON: {output_path}")