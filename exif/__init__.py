#!/usr/bin/env python3

import argparse
import os
import sys
import json
import hashlib
from collections import defaultdict

EXIF_FILE_NAME = ".exif_data"
EXIF_IGNORE_NAME = ".exif_ignore"
NOEXIF_HASH_FILE = "file_hashes.txt"

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
        return "".join([
            self.timestamp or "",
            self.make or "",
            self.shutter_count or "",
            self.serial_number or "",
            self.file_ext or "",
            self.size or "",
            self.dimensions or ""
        ])

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


class NoExifFile:
    """Represents a file without EXIF timestamp data, identified by content hash"""

    def __init__(self, filename="", dirpath="", file_hash="", size=""):
        self.filename = filename
        self.dirpath = dirpath
        self.file_hash = file_hash
        self.size = size

    def path(self):
        return os.path.join(self.dirpath, self.filename)

    def relative_path(self, base_dir):
        """Get path relative to base directory"""
        full_path = self.path()
        return os.path.relpath(full_path, base_dir)

    def __str__(self):
        return f"{self.filename}: hash={self.file_hash[:12]}..., size={self.size}"

    def __eq__(self, other):
        return isinstance(other, NoExifFile) and self.file_hash == other.file_hash

    def __hash__(self):
        # file_hash is already a hash (SHA256), convert hex string to int
        # This avoids hashing an already-good hash with Python's hash()
        if not self.file_hash:
            return 0
        try:
            return int(self.file_hash, 16)
        except ValueError:
            # Fall back for non-hex test strings
            return hash(self.file_hash)


def calculate_file_hash(file_path, chunk_size=8192):
    """Calculate SHA256 hash of file content"""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except (IOError, OSError) as e:
        print(f"Error calculating hash for {file_path}: {e}")
        return None


def load_hash_file(hash_file_path):
    """Load existing hashes from the hash file"""
    hashes = set()
    if os.path.exists(hash_file_path):
        try:
            with open(hash_file_path, 'r') as f:
                for line in f:
                    hash_val = line.strip()
                    if hash_val:
                        hashes.add(hash_val)
        except (IOError, OSError) as e:
            print(f"Error reading hash file {hash_file_path}: {e}")
    return hashes


def save_hash_to_file(hash_file_path, file_hash):
    """Append a new hash to the hash file"""
    try:
        with open(hash_file_path, 'a') as f:
            f.write(file_hash + '\n')
    except (IOError, OSError) as e:
        print(f"Error writing to hash file {hash_file_path}: {e}")


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
