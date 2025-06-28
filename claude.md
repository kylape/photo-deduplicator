# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This is a loose collection of scripts to manage a large set of photos.
Most of the photos are from a Nikon camera.
Deduplicated photos are stored in a date-based hierarchy: year, month, day.
Photo uniqueness is based on EXIF data extracted from each photo.

## Testing

Run unit tests with:
```bash
python -m pytest test_exif_hash.py -v
```

To install test dependencies:
```bash
pip install -r requirements.txt
```

## Backlog:

* ~~Right now deduplication only supports NEF, but JPG should also be supported.~~ ✅ DONE
* ~~iCloud photos should be downloaded and deduplicated, expanding the supported formats~~ ✅ DONE (HEIC/HEIF support added)
* Consider adding file content hashing for more robust iPhone photo deduplication
* Refactor ExifData to do native comparisons using hash (is this a good idea?)
* Be smarter about updating exif data in photo dirs.
* Combine individual scripts into one.
