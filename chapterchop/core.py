"""
Core logic of ChapterChop.
"""
import os
import subprocess

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