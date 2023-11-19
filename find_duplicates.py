#!/usr/bin/env python3

import argparse
import os
import sys
import json
import exif
from collections import defaultdict


def load_exif_files(dirname):
    for dirpath, _, filenames in os.walk(dirname):
        if exif.EXIF_FILE_NAME in filenames:
            with open(os.path.join(dirpath, exif.EXIF_FILE_NAME)) as fp:
                  for e in exif.load_exif_file(fp):
                      yield e, os.path.join(dirpath, e.filename)


def raw_dupe(exif, paths):
    if len(paths) != 2:
        return False
    
    img_exts = {"nef", "jpg"}

    return paths[0][:-3] == paths[1][:-3] and {paths[0][-3:].lower(), paths[1][-3:].lower()} == img_exts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="Root folder to scan")
    parser.add_argument("-i", "--ignore-raw-dupes", action="store_true", help="Ignore raw NEF files that look like duplicates next to their corresponding JPEG")
    args = parser.parse_args()

    if not os.path.exists(args.dir):
        print("Error: Path does not exist: %s" % args.dir)
        sys.exit(1)

    photo_dict = defaultdict(list)
    folder_dict = defaultdict(set)

    for e, path in load_exif_files(args.dir):
        photo_dict[e].append(path)
        folder_dict[os.path.dirname(path)].add(e)

    for k, v in photo_dict.items():
        if args.ignore_raw_dupes and raw_dupe(k, v):
            continue

        if len(v) > 1:
            print()
            print("Duplcates:")
            for i in v:
                print(i)

    for i, t in enumerate(folder_dict.items()):
        path, images = t
        path_keys = list(folder_dict.keys())
        for k in range(i+1, len(path_keys)):
            path1, set1 = path, images
            path2, set2 = path_keys[k], folder_dict[path_keys[k]]

            if set1 == set2:
                print("These two folders are the same:")
                print(path1)
                print(path2)
                continue

            if (set1 - set2) == set():
                print("All the files in 1 are also in 2")
                print(path1)
                print(path2)
                continue

            if (set2 - set1) == set():
                print("All the files in 1 are also in 2")
                print(path2)
                print(path1)
                continue


if __name__ == "__main__":
    main()
