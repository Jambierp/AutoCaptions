#!/usr/bin/env python3
import sys
import os
from pathlib import Path
import subprocess

import premiere_convert
from transcribe import transcribe_to_srt
from log import console, log  # assuming these provide console logging

def prompt_input_file():
    """Prompt user for an input file and verify it exists."""
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
    """Ask the user for configuration details, with defaults if left blank."""
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
    # Ensure the output filename ends with .xml
    if not outfile.endswith(".xml"):
        outfile += ".xml"
    with open(outfile, "w") as f:
        f.write(premiere_xml)
    log.success(f"Saved Premiere Pro XML to {outfile!r}")
    return outfile

def main():
    log.progress("Loading modules...")

    # Prompt user for necessary file paths and configuration.
    input_filepath = prompt_input_file()
    output_filepath = prompt_output_file(input_filepath)
    model, split_gap, split_length = prompt_configuration()

    log.progress("\nStarting transcription and conversion (check console for progress)...")
    
    # Run transcription
    srt_filepath = transcribe_to_srt(
        input_filepath, 
        model_name=model,
        split_gap=split_gap,
        split_length=split_length
    )

    # Convert SRT to Premiere Pro XML
    outfile = srt_to_xml(srt_filepath, output_filepath)

    print(f"\nDone! Premiere Pro XML file saved to: {outfile}")
    # Optionally, on Linux you could open the file manager using xdg-open if desired:
    # subprocess.Popen(["xdg-open", os.path.dirname(outfile)])

if __name__ == "__main__":
    main()
