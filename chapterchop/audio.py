import os
import subprocess
import soundfile as sf
import numpy as np
import tempfile
import logging
import librosa

logger = logging.getLogger(__name__)

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
def load_audio(path, target_sr=44100):
    
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
        logger.info(f"Running ffmpeg to convert: {path}")
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
Save audio clips around each gap to a temporary directory and optionally build a metadata list.
Args:
    gaps (list of tuples): List of (gap_start, gap_end) in seconds.
    y (np.ndarray): Full audio time series.
    sr (int): Sample rate of the audio.
    before_sec (float): Seconds before the gap to include.
    after_sec (float): Seconds after the gap to include.
    metadata_list (list, optional): A list to store JSON-friendly metadata about each gap clip.
Returns:
    str: Path to the temporary directory containing saved WAV clips.
    list of str: List of saved .wav file paths.
"""
def save_clips_to_tempdir( gaps, y, sr, before_sec=2.0, after_sec=2.0, metadata_list=None ):
    temp_dir = tempfile.mkdtemp(prefix="chapterchop_gaps_")
    saved_paths = []
    duration = len(y) / sr

    for idx, (gap_start, gap_end) in enumerate(gaps, 1):
        clip_start = max(0, gap_start - before_sec)
        clip_end = min(duration, gap_end + after_sec)

        start_sample = int(clip_start * sr)
        end_sample = int(clip_end * sr)
        clip_audio = y[start_sample:end_sample]

        filename = f"Gap_{idx}.wav"
        file_path = os.path.join(temp_dir, filename)
        sf.write(file_path, clip_audio, sr)
        saved_paths.append(file_path)

        # Add metadata entry if a list is provided
        if metadata_list is not None:
            metadata_list.append({
                "file": filename,
                "start": round(clip_start, 3),
                "gap_start": round(gap_start, 3),
                "gap_end": round(gap_end, 3),
                "end": round(clip_end, 3)
            })

    return temp_dir, saved_paths

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