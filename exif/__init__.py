#!/usr/bin/env python3

import argparse
import os
import sys
import json
from collections import defaultdict

EXIF_FILE_NAME = ".exif_data"
EXIF_IGNORE_NAME = ".exif_ignore"

class ExifEntry:

    def __init__(self, filename="", dirpath="", timestamp="", shutter_count="", serial_number="", make="", size="", dimensions=""):
        self.filename = filename
        self.dirpath = dirpath
        self.timestamp = timestamp
        self.serial_number = serial_number
        self.shutter_count = shutter_count
        self.make = make
        self.size = size
        self.dimensions = dimensions
        self.file_ext = self.filename.lower().split('.')[-1] if '.' in self.filename else ''

    def __str__(self):
        return "%s: %s, timestamp: %s, %s, shutter count: %s" % (self.filename, self.make, self.timestamp, self.serial_number, self.shutter_count)

    """
    ExifEntries are considered equal *even if the filenames are different*.
    """
    def __eq__(self, x):
        return self.uniq_str() == x.uniq_str()

    def __hash__(self):
        return hash(self.uniq_str())

    def uniq_str(self):
        return "".join([self.timestamp, self.make, self.shutter_count, self.serial_number, self.file_ext, self.size, self.dimensions])

    def path(self):
        return os.path.join(self.dirpath, self.filename)

    def as_dict(self):
        return {
            "filename": self.filename,
            "dirpath": self.dirpath,
            "timestamp": self.timestamp,
            "shutter_count": self.shutter_count,
            "serial_number": self.serial_number,
            "make": self.make,
            "size": self.size,
            "dimensions": self.dimensions,
        }


def load_exif_file(fp):
    for line in fp.readlines():
        j = json.loads(line)
        yield ExifEntry(
            filename=j["filename"],
            dirpath=j["dirpath"],
            timestamp=j["timestamp"],
            serial_number=j["serial_number"],
            shutter_count=j["shutter_count"],
            make=j["make"],
            size=j["size"],
            dimensions=j["dimensions"],
        )
