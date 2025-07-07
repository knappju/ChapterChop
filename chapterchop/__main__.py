"""
Entrypoint for running ChapterChop from the command line.
"""

import sys
from .core import *
import argparse


def validate_args(args):
    errors = []

    # Validate each input file
    for path in args.InputFile:
        if not os.path.isfile(path):
            errors.append(f"Input file does not exist or is not a file: {path}")
        elif not path.lower().endswith('.mp3'):
            errors.append(f"Input file does not have .mp3 extension: {path}")

    # Check if OutputDirectory is writable or creatable
    if not os.path.exists(args.OutputDirectory):
        try:
            os.makedirs(args.OutputDirectory, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create output directory: {args.OutputDirectory} ({e})")
    elif not os.access(args.OutputDirectory, os.W_OK):
        errors.append(f"Output directory is not writable: {args.OutputDirectory}")

    # SilenceThreshold must be between 0.0 and 1.0
    if not (0.0 <= args.SilenceThreshold <= 1.0):
        errors.append(f"SilenceThreshold must be between 0.0 and 1.0 (got {args.SilenceThreshold})")

    # SilenceGap must be a positive number
    if args.SilenceGap <= 0:
        errors.append(f"SilenceGap must be a positive number (got {args.SilenceGap})")

    # Model must be one of the allowed values
    valid_models = {'tiny', 'base', 'small', 'medium', 'large'}
    if args.Model not in valid_models:
        errors.append(f"Model must be one of: {', '.join(valid_models)} (got '{args.Model}')")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)

def main():

    parser = argparse.ArgumentParser()

    #define optional arguments with default values
    parser.add_argument('--InputFile', type=str, nargs='+', default=['input'], help='Path to Input.mp3 Files')
    parser.add_argument('--OutputDirectory', type=str, default='output', help='Path to Output Directory')
    parser.add_argument('--SilenceThreshold', type=float, default=0.05, help='Audio Volume Level Considered Silence.')
    parser.add_argument('--SilenceGap', type=float, default=3.0, help='The Silence Length in Seconds')
    parser.add_argument('--Model', type=str, default='base', help='Which AI Model Size to Use')

    args = parser.parse_args()
    validate_args(args)

    result = process_audio_file(audio_path=args.InputFile[0], output_folder=args.OutputDirectory, silence_threshold=args.SilenceThreshold, min_gap_sec=args.SilenceGap) #currently only taking in the first input file argument.

if __name__ == "__main__":
    main()