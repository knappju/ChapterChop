"""
Entrypoint for running ChapterChop from the command line.
"""

import sys
from .core import *

def main():

    audio_file = r"examples\3.mp3"
    result = process_audio_file(audio_file)

if __name__ == "__main__":
    main()