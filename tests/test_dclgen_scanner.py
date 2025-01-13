import unittest
from pathlib import Path
from dclgen_parser.scanner import DCLGENScanner

class TestDCLGENScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = DCLGENScanner()

    def test_duplicate_table_error(self):
        # Simulate duplicate table scenario
        directory_path = "test_resources/duplicate_tables"
        Path(directory_path).mkdir(parents=True, exist_ok=True)

        # Create two files with the same table name
        file_content = """
        DCLGEN TABLE(SCHEMA.TABLE1)
        EXEC SQL DECLARE TABLE1 TABLE (
            ID INTEGER NOT NULL,
            NAME VARCHAR(255)
        ) END-EXEC.
        """
        (Path(directory_path) / "file1.dclgen").write_text(file_content)
        (Path(directory_path) / "file2.dclgen").write_text(file_content)

        with self.assertRaises(ValueError) as context:
            self.scanner.scan_directory(directory_path)

        self.assertIn("Table 'TABLE1' is defined more than once", str(context.exception))

if __name__ == '__main__':
    unittest.main()
