import os
import subprocess
import soundfile as sf
import numpy as np
import tempfile
import librosa

"""
    Load any audio file using ffmpeg (mp3, wav, m4b, etc.).
    Converts to mono WAV and loads it with soundfile.
    
    Args:
        path (str): Path to the input audio file.
        target_sr (int): Sample rate to resample to (default: 16000).
    
    Returns:
        tuple: (y, sr) where y is the audio time series (np.ndarray) and sr is the sample rate.
    
    Raises:
        RuntimeError: If ffmpeg fails or the audio can't be read.
"""
def load_audio(path, target_sr=16000):
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"Audio file does not exist: {path}")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    ffmpeg_path = get_ffmpeg_path()

    ffmpeg_cmd = [
        ffmpeg_path,
        "-i", path,
        "-ar", str(target_sr),
        "-ac", "1",
        "-f", "wav",
        "-y",
        tmp_path
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        y, sr = sf.read(tmp_path)
        if y.ndim > 1:
            y = y[:, 0]  # ensure mono
        return y.astype(np.float32), sr

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg conversion failed: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

"""
Detect periods of silence longer than a given duration.
Args:
    y (np.ndarray): Audio time series (mono).
    sr (int): Sample rate of the audio.
    min_gap_seconds (float): Minimum duration of silence to count as a gap.
    silence_threshold (float): RMS threshold below which audio is considered silent.
Returns:
    list of tuples: [(start_time, end_time), ...] for each silent gap.
"""
def detect_silence_gaps(y, sr, min_gap_seconds=2.0, silence_threshold=0.3):

    frame_len = int(0.1 * sr)  # 100ms frames
    hop_len = frame_len // 2

    rms = librosa.feature.rms(y=y, frame_length=frame_len, hop_length=hop_len)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_len)
    silent = rms < silence_threshold

    gaps = []
    start = None

    for i, is_silent in enumerate(silent):
        t = times[i]
        if is_silent:
            if start is None:
                start = t
        elif start is not None:
            end = t
            if (end - start) >= min_gap_seconds:
                gaps.append((start, end))
            start = None

    # Handle trailing silence
    if start is not None:
        end = times[-1]
        if (end - start) >= min_gap_seconds:
            gaps.append((start, end))

    return gaps

"""
Extract a segment of audio from y that includes time before and after a given gap.
Parameters
----------
y : np.ndarray
    Full audio time series.
sr : int
    Sample rate of the audio.
gap_start : float
    Start time of the detected gap (in seconds).
gap_end : float
    End time of the detected gap (in seconds).
buffer_before : float, optional
    Duration before the gap to include (in seconds). Default is 2.0.
buffer_after : float, optional
    Duration after the gap to include (in seconds). Default is 2.0.
Returns
-------
segment : np.ndarray
    The audio segment with the buffer applied.
sr : int
    The sample rate of the audio (same as input).
"""
def extract_buffered_segment(y, sr, gap_start, gap_end, buffer_before=2.0, buffer_after=2.0):

    total_duration = len(y) / sr
    clip_start = max(0, gap_start - buffer_before)
    clip_end = min(total_duration, gap_end + buffer_after)

    start_sample = int(clip_start * sr)
    end_sample = int(clip_end * sr)

    segment = y[start_sample:end_sample]
    return segment, sr

def get_audio_duration(path):
    """Get audio duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json", path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    duration = float(json.loads(result.stdout)["format"]["duration"])
    return duration

def trim_audio_ffmpeg(input_path, output_path, start_time, end_time):
    ffmpeg_path = get_ffmpeg_path()
    
    cmd = [
        ffmpeg_path,
        "-i", input_path,
        "-ss", start_time,
        "-to", end_time,
        "-c", "copy",
        output_path
    ]
    subprocess.run(cmd, check=True)

def get_ffmpeg_path():
    base_dir = os.path.dirname(__file__)
    # Adjust path to where you bundle ffmpeg inside your repo
    ffmpeg_path = os.path.join(base_dir, ".." ,"third_party", "ffmpeg", "win64", "ffmpeg.exe")
    print(f"{ffmpeg_path}")
    return ffmpeg_path

def test_ffmpeg():
    ffmpeg_path = get_ffmpeg_path()
    try:
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            text=True,
            check=True
        )
        # You can log or print if you want here
        return True
    except Exception:
        # Maybe try system PATH fallback here if you want
        return False