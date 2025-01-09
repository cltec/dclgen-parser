import unittest
import csv
import os
from tempfile import NamedTemporaryFile

from dclgen_parser.reporter import ReportGenerator
from dclgen_parser.scanner import TableStats

class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        self.report_generator = ReportGenerator()
        self.sample_stats = {
            'TABLE1': [
                TableStats(filename='file1.dclgen', attribute_count=5, schema="Schema1"),
                TableStats(filename='file2.dclgen', attribute_count=5, schema="Schema1")
            ],
            'TABLE2': [
                TableStats(filename='file3.dclgen', attribute_count=3, schema="Schema1")
            ]
        }

    def test_generate_report(self):
        # Use a temporary file for testing
        with NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            temp_filename = temp_file.name
            
        try:
            # Generate report
            self.report_generator.generate_report(self.sample_stats, temp_filename)
            
            # Verify file contents
            with open(temp_filename, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)
                
                # Check header
                self.assertEqual(rows[0], [ 'Table Name', 'Number of Attributes', 'File Path', 'Schema', 'Normalized File Name'])
                
                # Check data rows
                self.assertEqual(len(rows), 4)  # Header + 3 data rows
                
                # Verify content is sorted by table name
                self.assertEqual(rows[1][0], 'TABLE1')
                self.assertEqual(rows[2][0], 'TABLE1')
                self.assertEqual(rows[3][0], 'TABLE2')
                
                # Verify attribute counts
                self.assertEqual(rows[1][1], '5')
                self.assertEqual(rows[2][1], '5')
                self.assertEqual(rows[3][1], '3')
                
        finally:
            # Clean up temporary file
            os.unlink(temp_filename)

    def test_generate_report_includes_normalized_file_name(self):
        with NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            temp_filename = temp_file.name

        try:
            # Generate report
            self.report_generator.generate_report(self.sample_stats, temp_filename)

            # Verify file contents
            with open(temp_filename, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)

                # Check for 'normalized file name' in header
                self.assertIn('Normalized File Name', header)

        finally:
            # Clean up temporary file
            os.unlink(temp_filename)
    def test_generate_report_normalizes_file_name(self):
        with NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            temp_filename = temp_file.name

        try:
            # Generate report
            self.report_generator.generate_report(self.sample_stats, temp_filename)

            # Verify file contents
            with open(temp_filename, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header
                rows = list(reader)

                # Check normalized file names
                self.assertEqual(rows[0][4], 'FILE1')
                self.assertEqual(rows[1][4], 'FILE2')
                self.assertEqual(rows[2][4], 'FILE3')

        finally:
            # Clean up temporary file
            os.unlink(temp_filename)

