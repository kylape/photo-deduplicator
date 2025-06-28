#!/usr/bin/env python3

import pytest
import exif

class TestExifHash:
    """Test the EXIF hash logic for DSLR vs iPhone photos"""
    
    def test_dslr_hash_includes_shutter_count(self):
        """DSLR photos should include shutter count in hash"""
        dslr = exif.ExifEntry('IMG_001.nef', '2023:01:01 12:00:00', '12345', 'SN123', 'Nikon')
        hash_str = dslr.uniq_str()
        
        assert '2023:01:01 12:00:00' in hash_str
        assert 'Nikon' in hash_str
        assert '12345' in hash_str
        assert 'SN123' in hash_str
        assert 'nef' in hash_str
    
    def test_iphone_hash_excludes_shutter_count(self):
        """iPhone photos should not include shutter count in hash"""
        iphone = exif.ExifEntry('IMG_002.heic', '2023:01:01 12:00:00', 'None', 'None', 'Apple')
        hash_str = iphone.uniq_str()
        
        assert '2023:01:01 12:00:00' in hash_str
        assert 'Apple' in hash_str
        assert 'heic' in hash_str
        assert 'None' not in hash_str
    
    def test_iphone_different_formats_not_duplicates(self):
        """iPhone photos in different formats should not be considered duplicates"""
        iphone_heic = exif.ExifEntry('IMG_003.heic', '2023:01:01 12:00:00', 'None', 'None', 'Apple')
        iphone_jpg = exif.ExifEntry('IMG_003.jpg', '2023:01:01 12:00:00', 'None', 'None', 'Apple')
        
        assert iphone_heic != iphone_jpg
        assert iphone_heic.uniq_str() != iphone_jpg.uniq_str()
    
    def test_dslr_different_formats_not_duplicates(self):
        """DSLR photos in different formats should not be considered duplicates"""
        dslr_nef = exif.ExifEntry('IMG_004.nef', '2023:01:01 14:00:00', '54321', 'SN456', 'Nikon')
        dslr_jpg = exif.ExifEntry('IMG_004.jpg', '2023:01:01 14:00:00', '54321', 'SN456', 'Nikon')
        
        assert dslr_nef != dslr_jpg
        assert dslr_nef.uniq_str() != dslr_jpg.uniq_str()
    
    def test_same_iphone_photos_are_duplicates(self):
        """Identical iPhone photos should be considered duplicates"""
        iphone1 = exif.ExifEntry('IMG_005.heic', '2023:01:01 15:00:00', 'None', 'None', 'Apple')
        iphone2 = exif.ExifEntry('IMG_006.heic', '2023:01:01 15:00:00', 'None', 'None', 'Apple')
        
        assert iphone1 == iphone2
        assert iphone1.uniq_str() == iphone2.uniq_str()
    
    def test_same_dslr_photos_are_duplicates(self):
        """Identical DSLR photos should be considered duplicates"""
        dslr1 = exif.ExifEntry('IMG_007.nef', '2023:01:01 16:00:00', '99999', 'SN789', 'Canon')
        dslr2 = exif.ExifEntry('IMG_008.nef', '2023:01:01 16:00:00', '99999', 'SN789', 'Canon')
        
        assert dslr1 == dslr2
        assert dslr1.uniq_str() == dslr2.uniq_str()
    
    def test_empty_shutter_count_uses_iphone_logic(self):
        """Photos with empty shutter count should use iPhone hash logic"""
        photo = exif.ExifEntry('IMG_009.jpg', '2023:01:01 17:00:00', '', '', 'Apple')
        hash_str = photo.uniq_str()
        
        assert '2023:01:01 17:00:00' in hash_str
        assert 'Apple' in hash_str
        assert 'jpg' in hash_str
        # Should not contain empty strings
        assert hash_str == '2023:01:01 17:00:00Applejpg'
    
    def test_none_shutter_count_uses_iphone_logic(self):
        """Photos with None shutter count should use iPhone hash logic"""
        photo = exif.ExifEntry('IMG_010.heif', '2023:01:01 18:00:00', None, None, 'Apple')
        hash_str = photo.uniq_str()
        
        assert '2023:01:01 18:00:00' in hash_str
        assert 'Apple' in hash_str
        assert 'heif' in hash_str
        assert hash_str == '2023:01:01 18:00:00Appleheif'

if __name__ == "__main__":
    pytest.main([__file__, "-v"])