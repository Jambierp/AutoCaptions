#!/usr/bin/env python3
import sys
import os
import argparse
from pathlib import Path
import subprocess

import premiere_convert
from transcribe import transcribe_to_srt
from pannel import console, log  # assuming these provide console logging

def prompt_input_file():
    """Prompt the user for an input file and verify it exists."""
    while True:
        input_file = input("Enter the path to an Audio or Video file to be transcribed: ").strip()
        if not input_file:
            print("No file entered. Please try again.")
            continue
        if not os.path.isfile(input_file):
            print("File does not exist. Please try again.")
            continue
        return input_file

def prompt_output_file(input_filepath):
    """Determine the output file location with a default based on the input file."""
    path = Path(input_filepath)
    default_filename = path.stem + ".xml"
    default_path = path.parent / default_filename
    print(f"Enter the path to save the output Premiere Pro XML sequence file.")
    print(f"Press Enter to use the default: {default_path}")
    output_file = input("Output file path: ").strip()
    if not output_file:
        output_file = str(default_path)
    return output_file

def prompt_configuration():
    """Ask the user for configuration details with defaults."""
    print("\nConfiguration:")
    model = input("Enter Whisper model (small/medium/large) [default: small]: ").strip() or "small"
    
    split_gap_input = input("Enter split silence (s) [default: 0.5]: ").strip()
    try:
        split_gap = float(split_gap_input) if split_gap_input else 0.5
    except ValueError:
        print("Invalid value for split silence. Using default 0.5.")
        split_gap = 0.5

    split_length_input = input("Enter split length (chars) [default: 20]: ").strip()
    try:
        split_length = int(split_length_input) if split_length_input else 20
    except ValueError:
        print("Invalid value for split length. Using default 20.")
        split_length = 20

    return model, split_gap, split_length

def srt_to_xml(srt_filename, outfile):
    """Convert the SRT file to Premiere Pro XML and save it."""
    print(f"\nConverting {srt_filename} to Premiere Pro XML...")
    premiere_xml = premiere_convert.srt_to_xml(srt_filename)
    if not outfile.endswith(".xml"):
        outfile += ".xml"
    with open(outfile, "w") as f:
        f.write(premiere_xml)
    log.success(f"Saved Premiere Pro XML to {outfile!r}")
    return outfile

def main():
    parser = argparse.ArgumentParser(
        description="Transcribe Audio to Premiere Pro XML."
    )
    parser.add_argument("--input", type=str,
                        help="Path to the input Audio or Video file")
    parser.add_argument("--output", type=str,
                        help="Path to the output XML file")
    parser.add_argument("--model", type=str, choices=["small", "medium", "large"],
                        help="Whisper model to use", default="small")
    parser.add_argument("--split_gap", type=float,
                        help="Split silence gap in seconds", default=0.5)
    parser.add_argument("--split_length", type=int,
                        help="Split length in characters", default=20)

    # If no arguments are provided, use interactive prompts.
    if len(sys.argv) == 1:
        print("No command-line arguments provided; entering interactive mode.\n")
        input_filepath = prompt_input_file()
        output_filepath = prompt_output_file(input_filepath)
        model, split_gap, split_length = prompt_configuration()
    else:
        args = parser.parse_args()
        if not args.input:
            parser.error("The --input parameter is required in non-interactive mode.")
        input_filepath = args.input
        if args.output:
            output_filepath = args.output
        else:
            # Use default output file based on input file if not provided.
            path = Path(input_filepath)
            default_filename = path.stem + ".xml"
            default_path = path.parent / default_filename
            output_filepath = str(default_path)
        model = args.model
        split_gap = args.split_gap
        split_length = args.split_length

    log.progress("Loading modules...")
    log.progress("\nStarting transcription and conversion (check console for progress)...")

    # Transcribe audio using Whisper.
    srt_filepath = transcribe_to_srt(
        input_filepath,
        model_name=model,
        split_gap=split_gap,
        split_length=split_length
    )

    # Convert SRT to Premiere Pro XML.
    outfile = srt_to_xml(srt_filepath, output_filepath)
    print(f"\nDone! Premiere Pro XML file saved to: {outfile}")
    
    # Optionally, on Linux you can open the output folder:
    # subprocess.Popen(["xdg-open", os.path.dirname(outfile)])

if __name__ == "__main__":
    main()
