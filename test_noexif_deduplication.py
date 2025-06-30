#!/usr/bin/env python3

import pytest
import tempfile
import os
import hashlib
import shutil
import exif

class TestNoExifFile:
    """Test the NoExifFile class functionality"""

    def test_init_with_all_fields(self):
        """Test NoExifFile initialization"""
        noexif = exif.NoExifFile(
            filename="video.mp4",
            dirpath="/videos/2023",
            file_hash="abc123def456",
            size="10485760"
        )

        assert noexif.filename == "video.mp4"
        assert noexif.dirpath == "/videos/2023"
        assert noexif.file_hash == "abc123def456"
        assert noexif.size == "10485760"

    def test_path_method(self):
        """Test the path() method"""
        noexif = exif.NoExifFile(
            filename="test.mov",
            dirpath="/home/user/videos"
        )

        expected_path = os.path.join("/home/user/videos", "test.mov")
        assert noexif.path() == expected_path

    def test_relative_path_method(self):
        """Test the relative_path() method"""
        noexif = exif.NoExifFile(
            filename="video.mp4",
            dirpath="/home/user/photos/vacation/videos"
        )

        base_dir = "/home/user/photos"
        expected_relative = "vacation/videos/video.mp4"
        assert noexif.relative_path(base_dir) == expected_relative

    def test_string_representation(self):
        """Test string representation of NoExifFile"""
        noexif = exif.NoExifFile(
            filename="test.mp4",
            file_hash="abcdef123456789",
            size="1048576"
        )

        result = str(noexif)
        assert "test.mp4" in result
        assert "abcdef123456" in result  # First 12 chars of hash
        assert "1048576" in result

    def test_equality_based_on_hash(self):
        """Test that NoExifFile equality is based on file hash"""
        noexif1 = exif.NoExifFile(
            filename="file1.mp4",
            dirpath="/dir1",
            file_hash="samehash123",
            size="1000"
        )

        noexif2 = exif.NoExifFile(
            filename="file2.mp4",  # Different filename
            dirpath="/dir2",       # Different directory
            file_hash="samehash123",  # Same hash
            size="2000"            # Different size
        )

        noexif3 = exif.NoExifFile(
            filename="file1.mp4",
            dirpath="/dir1",
            file_hash="differenthash",  # Different hash
            size="1000"
        )

        assert noexif1 == noexif2  # Same hash
        assert noexif1 != noexif3  # Different hash

        # Test that hash() function returns consistent integers
        assert isinstance(hash(noexif1), int)
        assert isinstance(hash(noexif2), int)
        assert isinstance(hash(noexif3), int)
        assert hash(noexif1) == hash(noexif2)  # Same file hash = same Python hash
        assert hash(noexif1) != hash(noexif3)  # Different file hash = different Python hash


class TestHashFunctions:
    """Test hash calculation and persistence functions"""

    def test_calculate_file_hash(self):
        """Test file hash calculation"""
        # Create a temporary file with known content
        with tempfile.NamedTemporaryFile(delete=False) as f:
            test_content = b"Hello, World! This is test content."
            f.write(test_content)
            f.flush()

            # Calculate hash using our function
            calculated_hash = exif.calculate_file_hash(f.name)

            # Calculate expected hash
            expected_hash = hashlib.sha256(test_content).hexdigest()

            assert calculated_hash == expected_hash

        os.unlink(f.name)

    def test_calculate_hash_nonexistent_file(self):
        """Test hash calculation for non-existent file"""
        result = exif.calculate_file_hash("/nonexistent/file.txt")
        assert result is None

    def test_load_empty_hash_file(self):
        """Test loading from non-existent hash file"""
        hashes = exif.load_hash_file("/nonexistent/hash_file.txt")
        assert hashes == set()

    def test_save_and_load_hash_file(self):
        """Test saving and loading hash file"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            hash_file_path = f.name

        # Save some hashes
        test_hashes = ["abc123", "def456", "ghi789"]
        for h in test_hashes:
            exif.save_hash_to_file(hash_file_path, h)

        # Load hashes back
        loaded_hashes = exif.load_hash_file(hash_file_path)

        assert loaded_hashes == set(test_hashes)

        os.unlink(hash_file_path)

    def test_hash_file_persistence(self):
        """Test that hash file persists across multiple operations"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            hash_file_path = f.name

        # Save initial hash
        exif.save_hash_to_file(hash_file_path, "hash1")

        # Load and verify
        hashes = exif.load_hash_file(hash_file_path)
        assert "hash1" in hashes

        # Save another hash
        exif.save_hash_to_file(hash_file_path, "hash2")

        # Load and verify both are present
        hashes = exif.load_hash_file(hash_file_path)
        assert "hash1" in hashes
        assert "hash2" in hashes
        assert len(hashes) == 2

        os.unlink(hash_file_path)


class TestHashBasedDeduplication:
    """Test hash-based deduplication logic"""

    def test_duplicate_detection_by_hash(self):
        """Test that files with same content hash are considered duplicates"""
        # Create two files with identical content
        test_content = b"Identical content for testing"

        with tempfile.NamedTemporaryFile(delete=False) as f1:
            f1.write(test_content)
            f1.flush()
            hash1 = exif.calculate_file_hash(f1.name)

            with tempfile.NamedTemporaryFile(delete=False) as f2:
                f2.write(test_content)  # Same content
                f2.flush()
                hash2 = exif.calculate_file_hash(f2.name)

                # Hashes should be identical
                assert hash1 == hash2

                # NoExifFile objects should be equal
                noexif1 = exif.NoExifFile("file1.mp4", "/dir1", hash1, "100")
                noexif2 = exif.NoExifFile("file2.mp4", "/dir2", hash2, "100")

                assert noexif1 == noexif2

        os.unlink(f1.name)
        os.unlink(f2.name)

    def test_different_content_different_hash(self):
        """Test that files with different content have different hashes"""
        content1 = b"Content for file 1"
        content2 = b"Different content for file 2"

        with tempfile.NamedTemporaryFile(delete=False) as f1:
            f1.write(content1)
            f1.flush()
            hash1 = exif.calculate_file_hash(f1.name)

            with tempfile.NamedTemporaryFile(delete=False) as f2:
                f2.write(content2)
                f2.flush()
                hash2 = exif.calculate_file_hash(f2.name)

                # Hashes should be different
                assert hash1 != hash2

                # NoExifFile objects should not be equal
                noexif1 = exif.NoExifFile("file1.mp4", "/dir1", hash1, "100")
                noexif2 = exif.NoExifFile("file2.mp4", "/dir2", hash2, "100")

                assert noexif1 != noexif2

        os.unlink(f1.name)
        os.unlink(f2.name)

    def test_hash_set_efficiency(self):
        """Test that the hash set is used for efficient duplicate checking"""
        # Create a hash set with some existing hashes
        existing_hashes = {"hash1", "hash2", "hash3"}

        # Test file with existing hash
        noexif_existing = exif.NoExifFile("file1.mp4", "/dir1", "hash1", "100")
        assert noexif_existing.file_hash in existing_hashes

        # Test file with new hash
        noexif_new = exif.NoExifFile("file2.mp4", "/dir1", "newhash", "100")
        assert noexif_new.file_hash not in existing_hashes

        # Test adding new hash to set
        existing_hashes.add(noexif_new.file_hash)
        assert noexif_new.file_hash in existing_hashes
        assert len(existing_hashes) == 4

    def test_noexif_directory_creation(self):
        """Test that noexif directory is created correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_root = temp_dir
            noexif_dir = os.path.join(target_root, "noexif")

            # Directory should not exist initially
            assert not os.path.exists(noexif_dir)

            # Create the directory (simulating the main function behavior)
            if not os.path.exists(noexif_dir):
                os.makedirs(noexif_dir)

            # Directory should now exist
            assert os.path.exists(noexif_dir)
            assert os.path.isdir(noexif_dir)

            # Hash file path should be constructible
            hash_file_path = os.path.join(noexif_dir, exif.NOEXIF_HASH_FILE)
            assert hash_file_path.endswith("file_hashes.txt")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])