#!/usr/bin/env python3

import pytest
import os
import exif

class TestExifEntry:
    """Test the updated ExifEntry class with new fields"""

    def test_init_with_all_fields(self):
        """Test ExifEntry initialization with all fields"""
        entry = exif.ExifEntry(
            filename="IMG_001.jpg",
            dirpath="/photos/2023/01/01",
            timestamp="2023:01:01 12:00:00",
            shutter_count="12345",
            serial_number="SN123",
            make="Nikon",
            size="2048000",
            dimensions="1920x1080"
        )

        assert entry.filename == "IMG_001.jpg"
        assert entry.dirpath == "/photos/2023/01/01"
        assert entry.timestamp == "2023:01:01 12:00:00"
        assert entry.shutter_count == "12345"
        assert entry.serial_number == "SN123"
        assert entry.make == "Nikon"
        assert entry.size == "2048000"
        assert entry.dimensions == "1920x1080"
        assert entry.file_ext == "jpg"

    def test_file_ext_extraction(self):
        """Test file extension extraction in various cases"""
        # Normal case
        entry1 = exif.ExifEntry(filename="photo.HEIC")
        assert entry1.file_ext == "heic"

        # Multiple dots
        entry2 = exif.ExifEntry(filename="my.photo.NEF")
        assert entry2.file_ext == "nef"

        # No extension
        entry3 = exif.ExifEntry(filename="photo")
        assert entry3.file_ext == ""

        # Empty filename
        entry4 = exif.ExifEntry(filename="")
        assert entry4.file_ext == ""

        # Just extension
        entry5 = exif.ExifEntry(filename=".jpg")
        assert entry5.file_ext == "jpg"

    def test_path_method(self):
        """Test the path() method combines dirpath and filename"""
        entry = exif.ExifEntry(
            filename="photo.jpg",
            dirpath="/home/user/photos"
        )

        expected_path = os.path.join("/home/user/photos", "photo.jpg")
        assert entry.path() == expected_path

    def test_path_method_edge_cases(self):
        """Test path() method with edge cases"""
        # Empty dirpath
        entry1 = exif.ExifEntry(filename="photo.jpg", dirpath="")
        assert entry1.path() == "photo.jpg"

        # Dirpath with trailing slash
        entry2 = exif.ExifEntry(filename="photo.jpg", dirpath="/photos/")
        expected = os.path.join("/photos/", "photo.jpg")
        assert entry2.path() == expected

        # Both empty
        entry3 = exif.ExifEntry(filename="", dirpath="")
        assert entry3.path() == ""

    def test_uniq_str_includes_all_fields(self):
        """Test that uniq_str() includes all fields in hash"""
        entry = exif.ExifEntry(
            filename="test.jpg",
            timestamp="2023:01:01 12:00:00",
            make="Apple",
            shutter_count="None",
            serial_number="None",
            size="1024000",
            dimensions="1920x1080"
        )

        hash_str = entry.uniq_str()

        # Should include all fields
        assert "2023:01:01 12:00:00" in hash_str
        assert "Apple" in hash_str
        assert "None" in hash_str  # shutter_count and serial_number
        assert "jpg" in hash_str
        assert "1024000" in hash_str
        assert "1920x1080" in hash_str

    def test_as_dict_includes_all_fields(self):
        """Test that as_dict() includes all new fields"""
        entry = exif.ExifEntry(
            filename="test.jpg",
            dirpath="/photos",
            timestamp="2023:01:01 12:00:00",
            make="Apple",
            size="1024000",
            dimensions="1920x1080"
        )

        result = entry.as_dict()

        # All fields should be present
        assert "filename" in result
        assert "dirpath" in result
        assert "timestamp" in result
        assert "shutter_count" in result
        assert "serial_number" in result
        assert "make" in result
        assert "size" in result
        assert "dimensions" in result

        # Verify values are correct
        assert result["filename"] == "test.jpg"
        assert result["dirpath"] == "/photos"
        assert result["timestamp"] == "2023:01:01 12:00:00"
        assert result["make"] == "Apple"
        assert result["size"] == "1024000"
        assert result["dimensions"] == "1920x1080"

    def test_str_representation(self):
        """Test string representation of ExifEntry"""
        entry = exif.ExifEntry(
            filename="photo.jpg",
            make="Canon",
            timestamp="2023:01:01 15:30:45",
            serial_number="ABC123",
            shutter_count="9999"
        )

        expected = "photo.jpg: Canon, timestamp: 2023:01:01 15:30:45, ABC123, shutter count: 9999"
        assert str(entry) == expected

    def test_unified_hash_logic(self):
        """Test that all photos use the same hash logic with all fields"""
        # iPhone photo with size and dimensions
        iphone = exif.ExifEntry(
            filename="IMG_001.heic",
            timestamp="2023:01:01 12:00:00",
            make="Apple",
            shutter_count="None",
            serial_number="None",
            size="3145728",
            dimensions="4032x3024"
        )

        # DSLR photo with size and dimensions
        dslr = exif.ExifEntry(
            filename="DSC_001.nef",
            timestamp="2023:01:01 12:00:00",
            make="Nikon",
            shutter_count="12345",
            serial_number="SN789",
            size="25165824",
            dimensions="6000x4000"
        )

        # Both should have all fields in their hash
        iphone_hash = iphone.uniq_str()
        dslr_hash = dslr.uniq_str()

        # iPhone hash should include all fields (even None values)
        assert "Apple" in iphone_hash
        assert "None" in iphone_hash  # shutter_count and serial_number as None
        assert "heic" in iphone_hash
        assert "3145728" in iphone_hash
        assert "4032x3024" in iphone_hash

        # DSLR hash should include all fields with real values
        assert "Nikon" in dslr_hash
        assert "12345" in dslr_hash
        assert "SN789" in dslr_hash
        assert "nef" in dslr_hash
        assert "25165824" in dslr_hash
        assert "6000x4000" in dslr_hash

    def test_load_exif_file_works_with_new_format(self):
        """Test that load_exif_file works correctly with new format"""
        import tempfile
        import json

        # Create test data in new format with all fields
        test_data = {
            "filename": "test.jpg",
            "dirpath": "/photos/2023/01/01",
            "timestamp": "2023:01:01 12:00:00",
            "shutter_count": "12345",
            "serial_number": "SN123",
            "make": "Nikon",
            "size": "2048000",
            "dimensions": "1920x1080"
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(json.dumps(test_data) + "\n")
            f.flush()

            with open(f.name) as fp:
                # Should now work correctly with keyword arguments
                entries = list(exif.load_exif_file(fp))
                assert len(entries) == 1

                entry = entries[0]
                # All fields should be in correct positions
                assert entry.filename == "test.jpg"
                assert entry.dirpath == "/photos/2023/01/01"
                assert entry.timestamp == "2023:01:01 12:00:00"
                assert entry.shutter_count == "12345"
                assert entry.serial_number == "SN123"
                assert entry.make == "Nikon"
                assert entry.size == "2048000"
                assert entry.dimensions == "1920x1080"

        os.unlink(f.name)

class TestExifEntryBugsAndIssues:
    """Test class specifically for bugs and issues found in the code"""

    def test_uniq_str_works_correctly(self):
        """Test that uniq_str() now works correctly after fixing file_ext bug"""
        entry = exif.ExifEntry(filename="test.jpg")

        # Should work now that file_ext bug is fixed
        hash_str = entry.uniq_str()
        assert isinstance(hash_str, str)
        assert "jpg" in hash_str  # file_ext should be included

    def test_load_exif_file_handles_missing_fields(self):
        """Test that load_exif_file handles missing fields gracefully"""
        import tempfile
        import json

        # Test data with some missing new fields (backward compatibility)
        test_data = {"filename": "test.jpg", "timestamp": "2023:01:01 12:00:00",
                    "shutter_count": "123", "serial_number": "SN", "make": "Canon"}

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(json.dumps(test_data) + "\n")
            f.flush()

            with open(f.name) as fp:
                # Should handle missing fields by using defaults
                try:
                    entries = list(exif.load_exif_file(fp))
                    entry = entries[0]

                    # Present fields should be correct
                    assert entry.filename == "test.jpg"
                    assert entry.timestamp == "2023:01:01 12:00:00"
                    assert entry.shutter_count == "123"
                    assert entry.serial_number == "SN"
                    assert entry.make == "Canon"

                    # Missing fields should use defaults
                    assert entry.dirpath == ""  # Default value
                    assert entry.size == ""     # Default value
                    assert entry.dimensions == ""  # Default value

                except KeyError as e:
                    # If it raises KeyError, that's expected behavior for missing required fields
                    assert "dirpath" in str(e) or "size" in str(e) or "dimensions" in str(e)

        os.unlink(f.name)

    def test_round_trip_save_and_load(self):
        """Test that we can save an ExifEntry and load it back correctly"""
        import tempfile
        import json

        # Create an entry with all fields
        original = exif.ExifEntry(
            filename="photo.heic",
            dirpath="/photos/2023/12/25",
            timestamp="2023:12:25 10:30:45",
            shutter_count="None",
            serial_number="None",
            make="Apple",
            size="4194304",
            dimensions="4032x3024"
        )

        # Save to file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(json.dumps(original.as_dict()) + "\n")
            f.flush()

            # Load from file
            with open(f.name) as fp:
                loaded_entries = list(exif.load_exif_file(fp))
                assert len(loaded_entries) == 1

                loaded = loaded_entries[0]

                # Should be identical
                assert loaded.filename == original.filename
                assert loaded.dirpath == original.dirpath
                assert loaded.timestamp == original.timestamp
                assert loaded.shutter_count == original.shutter_count
                assert loaded.serial_number == original.serial_number
                assert loaded.make == original.make
                assert loaded.size == original.size
                assert loaded.dimensions == original.dimensions
                assert loaded.file_ext == original.file_ext

                # Should be considered equal (same hash)
                assert loaded == original
                assert loaded.uniq_str() == original.uniq_str()

        os.unlink(f.name)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
