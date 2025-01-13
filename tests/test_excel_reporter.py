import unittest
from dclgen_parser.parser import Attribute, Table
from dclgen_parser.excel_reporter import ExcelReporter
import os
from openpyxl import load_workbook

class TestExcelReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = ExcelReporter()
        self.test_table = Table(
            table_name="test_table",
            schema_name="test_schema",
            attributes=[
                Attribute(name="id", type="INTEGER", nullable=False),
                Attribute(name="name", type="VARCHAR", length=255, nullable=True),
                Attribute(name="price", type="DECIMAL", precision=10, scale=2, nullable=False)
            ]
        )
        self.output_file = "test_report.xlsx"

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_generate_excel_report(self):
        self.reporter.generate_excel_report(self.test_table, self.output_file)
        self.assertTrue(os.path.exists(self.output_file))

        # Load the workbook and verify its contents
        workbook = load_workbook(self.output_file)
        sheet = workbook.active

        # Check headers
        expected_headers = ["Name", "Type", "Length", "Precision", "Scale", "Nullable"]
        actual_headers = [cell.value for cell in sheet[1]]
        self.assertEqual(expected_headers, actual_headers)

        # Check attribute data
        expected_data = [
            ["id", "INTEGER", "N/A", "N/A", "N/A", "No"],
            ["name", "VARCHAR", 255, "N/A", "N/A", "Yes"],
            ["price", "DECIMAL", "N/A", 10, 2, "No"]
        ]

        for row_idx, expected_row in enumerate(expected_data, start=2):
            actual_row = [sheet.cell(row=row_idx, column=col_idx).value for col_idx in range(1, 7)]
            self.assertEqual(expected_row, actual_row)

if __name__ == '__main__':
    unittest.main()
