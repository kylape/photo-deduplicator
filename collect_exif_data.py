#!/usr/bin/env python3

from exif import Image
import argparse
import os
import sys
import json

EXIF_FILE_NAME = ".exif_data"

class ExifEntry:

    def __init__(self, filename="", timestamp="", f_number="", model=""):
        self.filename = filename
        self.timestamp = timestamp
        self.f_number = f_number
        self.model = model

    def __str__(self):
        return "%s: timestamp: %s, %s f/%s" % (self.filename, self.timestamp, self.model, self.f_number)
     
    def as_dict(self):
        return {
            "filename": self.filename,
            "timestamp": self.timestamp,
            "f_number": self.f_number,
            "model": self.model,
        }
    

def load_exif_file(fp):
    for line in fp.readlines():
        j = json.loads(line)
        yield ExifEntry(j["filename"], j["timestamp"], j["f_number"], j["model"])


def extract_exif(path):
    with open(path, "rb") as fp:
        img = Image(fp)

        if not img.has_exif:
            return ExifEntry()

        return ExifEntry(
            timestamp=img.datetime_original,
            f_number=img.f_number,
            model=img.model,
        )


def scan(dirname):
    entries = []
    for dirpath, _, filenames in os.walk(dirname):
        exif_file_exists = EXIF_FILE_NAME in filenames
        exif_file_path = os.path.join(dirpath, EXIF_FILE_NAME)

        # TODO: Ensure exif file does not need to be regnerated based on something
        if exif_file_exists:
            with open(exif_file_path) as fp:
                dir_entries = list(load_exif_file(fp))

        jpg_cnt = len([f for f in filenames if f.lower().endswith(".jpg")])

        if not exif_file_exists or jpg_cnt != len(dir_entries):
            dir_entries = [exif_entry for exif_entry in scan_dir(dirpath, filenames)]

        if not exif_file_exists:
            with open(exif_file_path, "w") as fp:
                for entry in sorted(dir_entries, key=lambda e: e.filename):
                    fp.write(json.dumps(entry.as_dict()) + "\n")

        entries.extend(dir_entries)
    for entry in entries:
        print(entry)
    print("Exif count: %d" % len(entries))


def scan_dir(dirpath, filenames):
    for filename in filenames:
        fullpath = os.path.join(dirpath, filename.lower())
        if fullpath.endswith(".jpg"):
            exif_entry = extract_exif(fullpath)
            exif_entry.filename = filename
            yield exif_entry


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
