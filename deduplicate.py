#!/usr/bin/env python3

import argparse
import os
import sys
import json
import exif
import shutil
from collections import defaultdict


def load_exif_files(dirname):
    for dirpath, _, filenames in os.walk(dirname):
        if exif.EXIF_FILE_NAME in filenames:
            with open(os.path.join(dirpath, exif.EXIF_FILE_NAME)) as fp:
                  for e in exif.load_exif_file(fp):
                      yield e, os.path.join(dirpath, e.filename)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scan_root", help="Root folder to scan")
    parser.add_argument("target_root", help="Root folder to place all images")
    args = parser.parse_args()

    if not os.path.exists(args.scan_root):
        print("Error: Path does not exist: %s" % args.dir)
        sys.exit(1)

    photo_dict = defaultdict(list)

    for e, path in load_exif_files(args.scan_root):
        photo_dict[e].append(path)

    for k, v in photo_dict.items():
        to_copy = v[0]
        
        for img in v:
            if img.lower().endswith(".nef"):
                to_copy = img
                break

        year, month, day = k.timestamp.split()[0].split(":")
        hour, minute, second = k.timestamp.split()[1].split(":")
        target_dir = os.path.join(args.target_root, year, month, day)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        ext = img.lower().split(".")[-1]

        shutter_count_valid = k.shutter_count is not None \
                and k.shutter_count != "" \
                and k.shutter_count != "None"

        identifier = k.shutter_count if shutter_count_valid else k.make
        file_name = "%s.%s" % ("-".join([hour, minute, second, identifier]), ext)

        dest_file = os.path.join(target_dir, file_name)

        if not os.path.exists(dest_file):
            shutil.copy(to_copy, dest_file)
            print("%s -> %s" % (to_copy, dest_file))
        else:
            print("%s is already copied" % to_copy)

if __name__ == "__main__":
    main()
