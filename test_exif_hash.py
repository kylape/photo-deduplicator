#!/usr/bin/env python3

import pytest
import exif

class TestExifHash:
    """Test the EXIF hash logic for DSLR vs iPhone photos"""

    def test_dslr_hash_includes_all_fields(self):
        """DSLR photos should include all fields in hash"""
        dslr = exif.ExifEntry(filename='IMG_001.nef', timestamp='2023:01:01 12:00:00',
                            shutter_count='12345', serial_number='SN123', make='Nikon')
        hash_str = dslr.uniq_str()

        assert '2023:01:01 12:00:00' in hash_str
        assert 'Nikon' in hash_str
        assert '12345' in hash_str
        assert 'SN123' in hash_str
        assert 'nef' in hash_str

    def test_iphone_hash_includes_all_fields(self):
        """iPhone photos should include all fields in hash (including None values)"""
        iphone = exif.ExifEntry(filename='IMG_002.heic', timestamp='2023:01:01 12:00:00',
                              shutter_count='None', serial_number='None', make='Apple')
        hash_str = iphone.uniq_str()

        assert '2023:01:01 12:00:00' in hash_str
        assert 'Apple' in hash_str
        assert 'heic' in hash_str
        assert 'None' in hash_str  # Now includes None values

    def test_different_formats_not_duplicates(self):
        """Photos in different formats should not be considered duplicates"""
        heic = exif.ExifEntry(filename='IMG_003.heic', timestamp='2023:01:01 12:00:00',
                            shutter_count='None', serial_number='None', make='Apple')
        jpg = exif.ExifEntry(filename='IMG_003.jpg', timestamp='2023:01:01 12:00:00',
                           shutter_count='None', serial_number='None', make='Apple')

        assert heic != jpg
        assert heic.uniq_str() != jpg.uniq_str()

    def test_same_photos_with_different_filenames_are_duplicates(self):
        """Photos with same metadata but different filenames should be duplicates"""
        photo1 = exif.ExifEntry(filename='IMG_005.heic', timestamp='2023:01:01 15:00:00',
                              shutter_count='None', serial_number='None', make='Apple')
        photo2 = exif.ExifEntry(filename='different_name.heic', timestamp='2023:01:01 15:00:00',
                              shutter_count='None', serial_number='None', make='Apple')

        assert photo1 == photo2  # Same metadata, different filename
        assert photo1.uniq_str() == photo2.uniq_str()

    def test_size_and_dimensions_affect_hash(self):
        """Photos with different size or dimensions should not be duplicates"""
        photo1 = exif.ExifEntry(filename='IMG_007.jpg', timestamp='2023:01:01 16:00:00',
                              make='Apple', size='1000000', dimensions='1920x1080')
        photo2 = exif.ExifEntry(filename='IMG_007.jpg', timestamp='2023:01:01 16:00:00',
                              make='Apple', size='2000000', dimensions='1920x1080')  # Different size
        photo3 = exif.ExifEntry(filename='IMG_007.jpg', timestamp='2023:01:01 16:00:00',
                              make='Apple', size='1000000', dimensions='4032x3024')  # Different dimensions

        assert photo1 != photo2  # Different size
        assert photo1 != photo3  # Different dimensions
        assert photo2 != photo3  # Both different

if __name__ == "__main__":
    pytest.main([__file__, "-v"])