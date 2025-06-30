"""
Entrypoint for running ChapterChop from the command line.
"""

import sys
from .core import *

def main():

    audio_file = r"examples\3.mp3"
    test_gap_detection(audio_file, min_gap_seconds=2.0)

if __name__ == "__main__":
    main()