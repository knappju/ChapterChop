import whisper
import numpy as np

# Load the Whisper model once, globally
model = whisper.load_model("medium")  # You can change to "small", "medium", etc. if needed

"""
Transcribe the audio before and after a gap and combine the results with a '...' in the middle.
Args:
    segment (dict): A segment dictionary containing:
        - "buffered_segment": np.ndarray
        - "sample_rate": int
        - "gap_start": float
        - "gap_end": float
        - "start": float (optional, required if you want precise gap offsets)
Returns:
    tuple: (transcript: str, confidence: float)
"""
def transcribe_segment(segment):
    audio = segment["buffered_segment"]
    sr = segment["sample_rate"]
    gap_start = segment["gap_start"]
    gap_end = segment["gap_end"]
    clip_start = segment.get("start", gap_start - 2.0)  # Default to buffer-before

    # Convert gap times relative to clip
    gap_start_offset = gap_start - clip_start
    gap_end_offset = gap_end - clip_start

    gap_start_sample = int(gap_start_offset * sr)
    gap_end_sample = int(gap_end_offset * sr)

    # Slice pre-gap and post-gap audio
    pre_gap_audio = audio[:gap_start_sample]
    post_gap_audio = audio[gap_end_sample:]

    # Run Whisper on pre-gap audio
    pre_result = model.transcribe(pre_gap_audio, language="en", fp16=False)
    pre_text = pre_result["text"].strip()
    pre_conf = _get_avg_confidence(pre_result.get("segments", []))

    # Run Whisper on post-gap audio
    post_result = model.transcribe(post_gap_audio, language="en", fp16=False)
    post_text = post_result["text"].strip()
    post_conf = _get_avg_confidence(post_result.get("segments", []))

    # Construct final transcript
    transcript = f"{pre_text} ... {post_text}".strip()

    # Weighted average confidence
    pre_len = len(pre_gap_audio)
    post_len = len(post_gap_audio)
    total_len = max(pre_len + post_len, 1)
    confidence = (pre_conf * pre_len + post_conf * post_len) / total_len

    return transcript, confidence


"""
Calculate average confidence from Whisper segments.
"""
def _get_avg_confidence(segments):
    if not segments:
        return 0.0
    logprobs = [seg["avg_logprob"] for seg in segments if "avg_logprob" in seg]
    if not logprobs:
        return 0.0
    probs = [np.exp(lp) for lp in logprobs]
    return float(np.mean(probs))