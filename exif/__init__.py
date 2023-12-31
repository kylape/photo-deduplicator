#!/usr/bin/env python3

import argparse
import os
import sys
import json
from collections import defaultdict

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
     
    """
    ExifEntries are considered equal *even if the filenames are different*.
    """
    def __eq__(self, x):
        return self.uniq_str() == x.uniq_str()

    def __hash__(self):
        return hash(self.uniq_str())

    def uniq_str(self):
        return "".join([self.timestamp, self.make, self.shutter_count, self.serial_number])

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
        j = json.loads(line)
        yield ExifEntry(j["filename"], j["timestamp"], j["shutter_count"], j["serial_number"], j["make"])
