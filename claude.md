# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This is a photo/video deduplication system with two complementary approaches:

**EXIF-based deduplication** for photos with timestamps, and **hash-based deduplication** for files without EXIF timestamps (videos, some photos).

Originally designed for Nikon cameras, now supports iPhone photos, videos, and mixed camera collections.

## Testing

Run all unit tests with:
```bash
python -m pytest test_exif_entry.py test_exif_hash.py test_noexif_deduplication.py -v
```

Run specific test suites:
```bash
# EXIF-based deduplication tests
python -m pytest test_exif_hash.py -v

# ExifEntry class tests
python -m pytest test_exif_entry.py -v

# Hash-based deduplication tests (for files without EXIF timestamps)
python -m pytest test_noexif_deduplication.py -v
```

To install test dependencies:
```bash
pip install -r requirements.txt
```

## Backlog:

* ~~Right now deduplication only supports NEF, but JPG should also be supported.~~ ✅ DONE
* ~~iCloud photos should be downloaded and deduplicated, expanding the supported formats~~ ✅ DONE (HEIC/HEIF support added)
* ~~Consider adding file content hashing for more robust iPhone photo deduplication~~ ✅ DONE (Hash-based deduplication for files without EXIF timestamps)
* Refactor ExifData to do native comparisons using hash (is this a good idea?)
* Be smarter about updating exif data in photo dirs.
* Combine individual scripts into one.

## Features:

### EXIF-based Deduplication
- Photos with DateTimeOriginal are organized by date: `year/month/day/HH-MM-SS-identifier.ext`
- Uses unified hash including timestamp, make, shutter count, serial number, file extension, size, and dimensions
- Supports NEF, JPG, HEIC, HEIF formats

### Hash-based Deduplication (NoExif files)
- Files without EXIF timestamps (videos, some photos) are stored in `noexif/` folder
- Uses SHA256 content hash for deduplication
- Preserves original directory structure under `noexif/`
- Maintains hash registry in `noexif/file_hashes.txt`
- Supports MOV, MP4 video formats
- **Optimized for performance**: loads existing hashes once per session, not per file
- **Automatic directory creation**: ensures `noexif/` directory exists before processing

## Implementation Notes

### Design Decisions Made
- **Unified hash algorithm**: All photos (DSLR/iPhone) use same hash fields instead of conditional logic for simpler maintenance
- **SHA256 content hashing**: For files without EXIF timestamps, uses file content hash for reliable deduplication
- **Directory structure preservation**: NoExif files maintain original relative paths under `noexif/`
- **One hash file per session**: Loads `file_hashes.txt` once for efficiency, not per file
- **Dual file type support**: `collect_exif_data.py` yields both `ExifEntry` and `NoExifFile` objects

### Backward Compatibility
- **BREAKING**: New ExifEntry constructor requires regenerating all `.exif_data` files
- **Field additions**: Added `dirpath`, `size`, `dimensions` to ExifEntry
- **Format support**: Added HEIC/HEIF (iPhone), MOV/MP4 (videos) to original NEF/JPG

### Performance Optimizations
- **Hash file loading**: O(1) duplicate checking via in-memory set
- **Directory filtering**: Skips thumbnail/preview directories automatically
- **Efficient __hash__()**: Converts hex SHA256 directly to int without double-hashing

### Testing Strategy
- **30+ unit tests** across 3 test files covering all functionality
- **Edge case coverage**: Empty files, missing fields, non-hex test strings
- **Integration testing**: Round-trip save/load, directory creation, hash persistence

## Workflow

### Typical Usage
1. **Scan source directory**: `python collect_exif_data.py /source/photos`
   - Extracts EXIF data, creates `.exif_data` files
   - Calculates SHA256 hashes for files without timestamps
2. **Deduplicate to target**: `python deduplicate.py /source/photos /target/organized`
   - EXIF photos → date-based folders: `2023/12/25/14-30-45-12345.jpg`
   - NoExif files → `noexif/` with preserved structure
   - Creates `noexif/file_hashes.txt` registry

### File Organization Results
```
/target/organized/
├── 2023/01/15/10-30-45-12345.nef          # DSLR photo
├── 2023/01/15/10-30-45-Apple.heic         # iPhone photo
├── noexif/
│   ├── file_hashes.txt                     # Hash registry
│   ├── vacation/videos/sunset.mov          # Preserved structure
│   └── downloads/random_video.mp4
```

### Key Constraints
- **EXIF timestamp required** for date-based organization
- **Content hashing** for files without timestamps (videos, some photos)
- **Regenerate .exif_data** when upgrading (new fields added)
- **Hash collisions**: Extremely unlikely with SHA256, but theoretically possible
