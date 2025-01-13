import unittest
import csv
import os
from tempfile import NamedTemporaryFile

from dclgen_parser.reporter import ReportGenerator
from dclgen_parser.parser import Table, Attribute

class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        self.report_generator = ReportGenerator()
        self.sample_stats = {
            'TABLE1': Table(
                table_name='TABLE1',
                schema_name='Schema1',
                attributes=[
                    Attribute(name='ID', type='INTEGER', nullable=False),
                    Attribute(name='NAME', type='VARCHAR', length=255, nullable=True)
                ]
            ),
            'TABLE2': Table(
                table_name='TABLE2',
                schema_name='Schema1',
                attributes=[
                    Attribute(name='PRICE', type='DECIMAL', precision=10, scale=2, nullable=False)
                ]
            )
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
                self.assertEqual(len(rows), 3)  # Header + 2 data rows
                
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
                self.assertEqual(rows[0][4], 'TABLE1')
                self.assertEqual(rows[1][4], 'TABLE1')
                self.assertEqual(rows[2][4], 'TABLE2')

        finally:
            # Clean up temporary file
            os.unlink(temp_filename)

