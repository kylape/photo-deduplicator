#!/usr/bin/env python3

import argparse
import os
import sys
import json
import subprocess
import shlex

EXIF_FILE_NAME = ".exif_data"
EXIF_IGNORE_NAME = ".exif_ignore"

class ExifEntry:

    def __init__(self, filename="", timestamp="", shutter_count="", serial_number="", make=""):
        self.filename = filename
        self.timestamp = timestamp
        self.serial_number = serial_number
        self.shutter_count = shutter_count
        self.make = make

    def __str__(self):
        return "%s: %s, timestamp: %s, %s, shutter count: %s" % (self.filename, self.make, self.timestamp, self.serial_number, self.shutter_count)
     
    def as_dict(self):
        return {
            "filename": self.filename,
            "timestamp": self.timestamp,
            "shutter_count": self.shutter_count,
            "serial_number": self.serial_number,
            "make": self.make,
        }
    

def load_exif_file(fp):
    for line in fp.readlines():
        try:
            j = json.loads(line)
            yield ExifEntry(j["filename"], j["timestamp"], j["shutter_count"], j["serial_number"], j["make"])
        except Exception as e:
            pass


def is_img(f):
    if "." not in f:
        return False

    ext = f.rsplit(".", 1)[1].lower()
    return ext in ("nef", "jpg")


ignore_cache = set()

def is_ignored(dirpath):
    if os.path.exists(os.path.join(dirpath, EXIF_IGNORE_NAME)):
        # ignore dirs with the ignore file
        ignore_cache.add(dirpath)
        return True
    
    for ignored_dir in ignore_cache:
        if dirpath.startswith(ignored_dir):
            # ignore all child dirs
            return True

    return False

def scan(dirname):
    entries = []
    for dirpath, _, filenames in os.walk(dirname):

        if is_ignored(dirpath):
            continue

        print("Scanning dir %s" % dirpath)
        exif_file_exists = EXIF_FILE_NAME in filenames
        exif_file_path = os.path.join(dirpath, EXIF_FILE_NAME)

        # check if the dir is writeable before running a potentially expensive exiftool command
        if not os.access(dirpath, os.W_OK):
            continue

        # TODO: Ensure exif file does not need to be regnerated based on something
        if exif_file_exists:
            with open(exif_file_path) as fp:
                dir_entries = list(load_exif_file(fp))

        img_files = {f.lower() for f in filenames if is_img(f)}

        if len(img_files) == 0:
            continue

        if not exif_file_exists or img_files != {e.filename.lower() for e in dir_entries}:
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
        if e["FileTypeExtension"].lower() in ("jpg", "nef") and e.get("Make") in ("NIKON CORPORATION", "Apple"):
            yield ExifEntry(e["FileName"], e["DateTimeOriginal"], str(e.get("ShutterCount")), str(e.get("SerialNumber")), e.get("Make"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="Root folder to scan")
    args = parser.parse_args()
    if not os.path.exists(args.dir):
        print("Error: Path does not exist: %s" % args.dir)
        sys.exit(1)
    scan(args.dir)

if __name__ == "__main__":
    main()
