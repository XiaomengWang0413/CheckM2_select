#!/usr/bin/env python3
"""
Filter genomes by completeness and contamination, then copy matching files to a destination folder.
"""

import argparse
import csv
import os
import shutil
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Filter genomes from CheckM report (Completeness>=50, Contamination<=10) and copy files to a new folder."
    )
    parser.add_argument("-i", "--input", required=True, help="CheckM TSV report (e.g., quality_report.tsv)")
    parser.add_argument("-s", "--source", required=True, help="Source folder containing genome files")
    parser.add_argument("-d", "--dest", required=True, help="Destination folder for selected genomes")
    parser.add_argument("--ext", nargs="+", default=[".fa", ".fna", ".fasta", ""],
                        help="Possible file extensions (including empty string for no extension). Default: .fa .fna .fasta ''")
    parser.add_argument("--copy-mode", choices=["copy", "link", "symlink"], default="copy",
                        help="How to transfer files: copy (default), hard link, or symbolic link")
    parser.add_argument("--overwrite", action="store_true", default=True,
                        help="Overwrite existing files in destination (default: True)")
    parser.add_argument("--no-overwrite", dest="overwrite", action="store_false",
                        help="Skip copying if file already exists in destination")
    parser.add_argument("--dry-run", action="store_true", help="Only print what would be done, without actual copying")
    return parser.parse_args()

def find_genome_file(basename, source_folder, extensions):
    """Return the full path of the first existing file with given basename + extension."""
    for ext in extensions:
        candidate = os.path.join(source_folder, basename + ext)
        if os.path.isfile(candidate):
            return candidate
    return None

def transfer_file(src, dst, mode, overwrite, dry_run):
    """Copy, link, or symlink file from src to dst."""
    if dry_run:
        print(f"[DRY RUN] Would {mode} {src} -> {dst}")
        return True
    try:
        if mode == "copy":
            shutil.copy2(src, dst)
        elif mode == "link":
            os.link(src, dst)
        elif mode == "symlink":
            os.symlink(src, dst)
        return True
    except Exception as e:
        print(f"Error transferring {src} -> {dst}: {e}", file=sys.stderr)
        return False

def main():
    args = parse_arguments()

    # Create destination folder if needed
    if not args.dry_run:
        os.makedirs(args.dest, exist_ok=True)

    # Read TSV and filter genomes
    selected_names = []
    try:
        with open(args.input, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                try:
                    comp = float(row['Completeness'])
                    cont = float(row['Contamination'])
                    if comp >= 50 and cont <= 10:
                        selected_names.append(row['Name'])
                except (ValueError, KeyError):
                    continue  # skip lines with invalid data
    except Exception as e:
        print(f"Error reading {args.input}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(selected_names)} genomes meeting criteria.")
    if not selected_names:
        print("No genomes to copy.")
        return

    # Process each genome name
    copied = 0
    missing = []
    for name in selected_names:
        src_file = find_genome_file(name, args.source, args.ext)
        if src_file is None:
            missing.append(name)
            print(f"Warning: Genome file for '{name}' not found in {args.source}", file=sys.stderr)
            continue

        dest_file = os.path.join(args.dest, os.path.basename(src_file))
        if not args.overwrite and os.path.exists(dest_file):
            print(f"Skipping {dest_file} (already exists, overwrite disabled)")
            continue

        if transfer_file(src_file, dest_file, args.copy_mode, args.overwrite, args.dry_run):
            copied += 1

    print(f"Successfully processed {copied} genome files.")
    if missing:
        print(f"Missing files for {len(missing)} genomes: {', '.join(missing[:10])}{'...' if len(missing)>10 else ''}")

if __name__ == "__main__":
    main()
