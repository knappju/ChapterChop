"""
Entrypoint for running ChapterChop from the command line.
"""

import sys
from .core import *

def main():
    if not test_ffmpeg():
        sys.exit("FFmpeg test failed! Please install or bundle ffmpeg properly.")

    # Proceed with rest of your app
    print("FFmpeg test passed. Running audio processing...")
    # call your core processing functions here...

if __name__ == "__main__":
    main()