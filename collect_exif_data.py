#!/usr/bin/env python3

import exif
import argparse
import os
import sys
import json
import subprocess
import shlex


def is_img(f):
    if "." not in f:
        return False

    ext = f.rsplit(".", 1)[1].lower()
    return ext in ("nef", "jpg")


ignore_cache = set()

def is_ignored(dirpath):
    if os.path.exists(os.path.join(dirpath, exif.EXIF_IGNORE_NAME)):
        # ignore dirs with the ignore file
        ignore_cache.add(dirpath)
        return True
    
    for ignored_dir in ignore_cache:
        if dirpath.startswith(ignored_dir):
            # ignore all child dirs
            return True

    return False

def scan(dirname, strict):
    entries = []

    for dirpath, _, filenames in os.walk(dirname):

        if is_ignored(dirpath):
            continue

        print("Scanning dir %s" % dirpath)
        exif_file_exists = exif.EXIF_FILE_NAME in filenames
        exif_file_path = os.path.join(dirpath, exif.EXIF_FILE_NAME)

        # check if the dir is writeable before running a potentially expensive exiftool command
        if not os.access(dirpath, os.W_OK):
            continue

        # TODO: Ensure exif file does not need to be regnerated based on something
        if exif_file_exists:
            with open(exif_file_path) as fp:
                dir_entries = list(exif.load_exif_file(fp))

        img_files = {f.lower() for f in filenames if is_img(f)}

        if len(img_files) == 0:
            continue

        needs_regen = strict and img_files != {e.filename.lower() for e in dir_entries}
        if not exif_file_exists or needs_regen:
            generated_dir_entries = True
            dir_entries = [exif_entry for exif_entry in scan_dir(dirpath, filenames)]
        else:
            generated_dir_entries = False

        if generated_dir_entries:
            with open(exif_file_path, "w") as fp:
                for entry in sorted(dir_entries, key=lambda e: e.filename):
                    fp.write(json.dumps(entry.as_dict()) + "\n")

        entries.extend(dir_entries)
    for entry in entries:
        print(entry)
    print("Exif count: %d" % len(entries))


def scan_dir(dirpath, filenames):
    proc = subprocess.run(shlex.split('exiftool -j "%s"' % dirpath), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    raw_json = proc.stdout

    if len(raw_json) == 0:
        return

    exiftool_data = json.loads(raw_json)

    if proc.returncode != 0:
        print("Error running exiftool")
        for e in exiftool_data:
            if "Error" in e:
                print("%s: %s" % (os.path.join(dirpath, e["FileName"]), e["Error"]))
        sys.exit(1)

    for e in exiftool_data:
        if "Make" not in e or "DateTimeOriginal" not in e:
            continue
        if e["FileTypeExtension"].lower() in ("jpg", "nef") and e.get("Make").lower() in ("nikon corporation", "apple", "canon", "nikon"):
            yield exif.ExifEntry(e["FileName"], e["DateTimeOriginal"], str(e.get("ShutterCount")), str(e.get("SerialNumber")), e.get("Make"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="Root folder to scan")
    parser.add_argument("-s", "--strict", action="store_true", help="Be strict about regenerating .exif_data")
    args = parser.parse_args()
    if not os.path.exists(args.dir):
        print("Error: Path does not exist: %s" % args.dir)
        sys.exit(1)
    scan(args.dir, args.strict)

if __name__ == "__main__":
    main()
