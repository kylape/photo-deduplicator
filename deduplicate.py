#!/usr/bin/env python3

import argparse
import os
import sys
import json
import exif
import shutil
from collections import defaultdict


def load_exif_files(dirname):
    """Load both EXIF and NoExif files from directory structure"""
    for dirpath, _, filenames in os.walk(dirname):
        if exif.EXIF_FILE_NAME in filenames:
            with open(os.path.join(dirpath, exif.EXIF_FILE_NAME)) as fp:
                for e in exif.load_exif_file(fp):
                    yield e, os.path.join(dirpath, e.filename)


def collect_all_files(dirname):
    """Collect all files (both EXIF and NoExif) by scanning directory"""
    from collect_exif_data import scan_dir, is_img, is_ignored

    for dirpath, dirnames, filenames in os.walk(dirname):
        if is_ignored(dirpath):
            continue

        if "thumb" in dirpath.lower() or "preview" in dirpath.lower():
            continue

        # Check if directory has supported image/video files
        img_files = [f for f in filenames if is_img(f)]
        if not img_files:
            continue

        exif_file_exists = exif.EXIF_FILE_NAME in filenames
        exif_file_path = os.path.join(dirpath, exif.EXIF_FILE_NAME)

        if exif_file_exists:
            print(f"Reading existing exif file in {dirpath}")
            with open(exif_file_path) as fp:
                for entry in exif.load_exif_file(fp):
                    yield entry
        else:
            print(f"Scanning dir {dirpath}")

            try:
                for entry in scan_dir(dirpath, filenames):
                    yield entry
            except Exception as e:
                print(f"Error scanning {dirpath}: {e}")
                continue


def handle_noexif_file(noexif_file, target_root, scan_root, existing_hashes, hash_file_path, force_move=False):
    """Handle files without EXIF data using hash-based deduplication"""
    noexif_dir = os.path.join(target_root, "noexif")

    # If hash already exists, skip the file
    if noexif_file.file_hash in existing_hashes:
        print(f"{noexif_file.path()} already exists (hash match)")
        return False

    # Create target directory structure preserving relative path
    relative_path = noexif_file.relative_path(scan_root)
    target_file_path = os.path.join(noexif_dir, relative_path)
    target_dir = os.path.dirname(target_file_path)

    # Create directory if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Copy or move the file
    source_path = noexif_file.path()
    if not os.path.exists(target_file_path):
        try:
            if force_move:
                shutil.move(source_path, target_file_path)
            else:
                shutil.copyfile(source_path, target_file_path)

            # Save hash to file and add to in-memory set
            exif.save_hash_to_file(hash_file_path, noexif_file.file_hash)
            existing_hashes.add(noexif_file.file_hash)

            print(f"{source_path} -> {target_file_path}")
            return True
        except (IOError, OSError) as e:
            print(f"Error copying {source_path}: {e}")
            return False
    else:
        print(f"{target_file_path} already exists")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scan_root", help="Root folder to scan")
    parser.add_argument("target_root", help="Root folder to place all images")
    parser.add_argument("--force", "-f", action="store_true", help="Move instead of copy")
    args = parser.parse_args()

    if not os.path.exists(args.scan_root):
        print("Error: Path does not exist: %s" % args.dir)
        sys.exit(1)

    exif_photo_dict = defaultdict(list)
    noexif_files = []

    # Collect all files from fresh scan
    for entry in collect_all_files(args.scan_root):
        if isinstance(entry, exif.ExifEntry):
            exif_photo_dict[entry].append(entry)
        elif isinstance(entry, exif.NoExifFile):
            noexif_files.append(entry)

    # Handle EXIF files with timestamp-based organization
    for k, v in exif_photo_dict.items():
        to_copy = v[0]

        date_part, time_part = k.timestamp.split()
        year, month, day = date_part.split(":") if ":" in date_part else date_part.split("/")
        hour, minute, second = time_part.split(":")
        target_dir = os.path.join(args.target_root, year, month, day)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        shutter_count_valid = k.shutter_count is not None \
                and k.shutter_count != "" \
                and k.shutter_count != "None"

        identifier = k.shutter_count if shutter_count_valid else (k.make or "Unknown")
        file_name = "%s.%s" % ("-".join([hour, minute, second, identifier]), k.file_ext)

        dest_file = os.path.join(target_dir, file_name)

        if not os.path.exists(dest_file):
            print("%s -> %s" % (to_copy.path(), dest_file))
            if args.force:
                os.rename(to_copy.path(), dest_file)
            else:
                shutil.copyfile(to_copy.path(), dest_file)
        else:
            print("%s is already copied" % to_copy.path())

    # Handle NoExif files with hash-based deduplication
    if noexif_files:
        # Set up noexif directory and load existing hashes once
        noexif_dir = os.path.join(args.target_root, "noexif")
        hash_file_path = os.path.join(noexif_dir, exif.NOEXIF_HASH_FILE)

        # Ensure noexif directory exists
        if not os.path.exists(noexif_dir):
            os.makedirs(noexif_dir)

        # Load existing hashes once
        existing_hashes = exif.load_hash_file(hash_file_path)
        print(f"Loaded {len(existing_hashes)} existing hashes from {hash_file_path}")

        # Process all noexif files
        copied_count = 0
        for noexif_file in noexif_files:
            if handle_noexif_file(noexif_file, args.target_root, args.scan_root,
                                existing_hashes, hash_file_path, args.force):
                copied_count += 1

        print(f"Processed {len(noexif_files)} NoExif files, copied {copied_count} new files")

if __name__ == "__main__":
    main()
