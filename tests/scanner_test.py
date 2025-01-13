import unittest
from unittest.mock import mock_open, patch, MagicMock
from pathlib import Path

from dclgen_parser.scanner import DCLGENScanner

class TestDCLGENScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = DCLGENScanner()
        self.sample_dclgen = """
      ******************************************************************
      * DCLGEN TABLE(EIP_ADT_TRAIL)                                    *
      ******************************************************************
           EXEC SQL DECLARE EIP_ADT_TRAIL TABLE
           ( S_DT_TM                        TIMESTAMP NOT NULL,
             C_USER_1                       CHAR(8) NOT NULL,
             C_USER_2                       CHAR(8) NOT NULL,
             C_SRVC_ID                      CHAR(3) NOT NULL
           ) END-EXEC.
        """
        
    def test_is_dclgen_file_valid_content(self):
        """Test that valid DCLGEN content is properly identified"""
        with patch('builtins.open', mock_open(read_data=self.sample_dclgen)):
            result = self.scanner.is_dclgen_file(Path('valid.dclgen'))
            self.assertTrue(result)
            
    def test_is_dclgen_file_invalid_content(self):
        """Test that non-DCLGEN content is properly rejected"""
        non_dclgen_content = "This is not a DCLGEN file"
        with patch('builtins.open', mock_open(read_data=non_dclgen_content)):
            result = self.scanner.is_dclgen_file(Path('invalid.txt'))
            self.assertFalse(result)
            
    def test_is_dclgen_file_unicode_error(self):
        """Test handling of Unicode decode errors"""
        with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')):
            result = self.scanner.is_dclgen_file(Path('binary.file'))
            self.assertFalse(result)
            
    def test_is_dclgen_file_io_error(self):
        """Test handling of IO errors"""
        with patch('builtins.open', side_effect=IOError('Test IO Error')):
            result = self.scanner.is_dclgen_file(Path('nonexistent.file'))
            self.assertFalse(result)

    def test_scan_directory_single_file(self):
        """Test scanning a directory with a single DCLGEN file"""
        mock_path = MagicMock(spec=Path)
        mock_path.is_file.return_value = True
        mock_path.relative_to.return_value = Path('test.dclgen')

        with patch('pathlib.Path.rglob') as mock_rglob:
            mock_rglob.return_value = [mock_path]
            
            # Mock the file reading operations
            with patch.object(self.scanner, 'is_dclgen_file', return_value=True):
                with patch('builtins.open', mock_open(read_data=self.sample_dclgen)):
                    result = self.scanner.scan_directory('/dummy/path')
                    
                    # Verify results
                    self.assertIn('EIP_ADT_TRAIL', result)
                    stats_list = result['EIP_ADT_TRAIL']
                    self.assertEqual(len(stats_list), 1)
                    self.assertEqual(stats_list[0].attribute_count, 4)
                    self.assertEqual(stats_list[0].filename, 'test.dclgen')

    def test_scan_directory_multiple_files(self):
        """Test scanning a directory with multiple DCLGEN files raises an error"""
        mock_path1 = MagicMock(spec=Path)
        mock_path1.is_file.return_value = True
        mock_path1.relative_to.return_value = Path('test1.dclgen')

        mock_path2 = MagicMock(spec=Path)
        mock_path2.is_file.return_value = True
        mock_path2.relative_to.return_value = Path('test2.dclgen')

        with patch('pathlib.Path.rglob') as mock_rglob:
            mock_rglob.return_value = [mock_path1, mock_path2]
            
            with patch.object(self.scanner, 'is_dclgen_file', return_value=True):
                with patch('builtins.open', mock_open(read_data=self.sample_dclgen)):
                    with self.assertRaises(ValueError) as context:
                        self.scanner.scan_directory('/dummy/path')
                    
                    self.assertIn("Table 'EIP_ADT_TRAIL' is defined more than once", str(context.exception))

    def test_scan_directory_with_errors(self):
        """Test scanning a directory with a file that raises an error"""
        mock_path = MagicMock(spec=Path)
        mock_path.is_file.return_value = True
        mock_path.relative_to.return_value = Path('error.dclgen')
        mock_path.__str__.return_value = 'error.dclgen'

        with patch('pathlib.Path.rglob') as mock_rglob:
            mock_rglob.return_value = [mock_path]
            
            with patch.object(self.scanner, 'is_dclgen_file', return_value=True):
                with patch('builtins.open', side_effect=Exception('Test error')):
                    with self.assertRaises(Exception) as context:
                        self.scanner.scan_directory('/dummy/path')
                    
                    self.assertIn("Test error", str(context.exception))

    def test_scan_directory_empty(self):
        """Test scanning an empty directory"""
        with patch('pathlib.Path.rglob') as mock_rglob:
            mock_rglob.return_value = []
            result = self.scanner.scan_directory('/dummy/path')
            self.assertEqual(len(result), 0)

    def test_scan_directory_no_dclgen_files(self):
        """Test scanning a directory with no DCLGEN files"""
        mock_path = MagicMock(spec=Path)
        mock_path.is_file.return_value = True
        
        with patch('pathlib.Path.rglob') as mock_rglob:
            mock_rglob.return_value = [mock_path]
            
            with patch.object(self.scanner, 'is_dclgen_file', return_value=False):
                result = self.scanner.scan_directory('/dummy/path')
                self.assertEqual(len(result), 0)

