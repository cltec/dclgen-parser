import unittest
from dclgen_parser.parser import Attribute, Table
from dclgen_parser.excel_reporter import ExcelReporter
import os

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

if __name__ == '__main__':
    unittest.main()
