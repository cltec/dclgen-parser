from openpyxl import Workbook
from typing import List
from dclgen_parser.parser import Table

class ExcelReporter:
    """Generates Excel reports from parsed table data"""

    def generate_excel_report(self, tables: List[Table], output_file: str):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Table Information"

        # Add headers
        headers = ["Table", "Name", "Type", "Length", "Precision", "Scale", "Nullable"]
        sheet.append(headers)

        for table in tables:
            # Add attribute data
            for attr in table.attributes:
                sheet.append([
                    table.table_name,
                    attr.name,
                    attr.type,
                    attr.length or "N/A",
                    attr.precision or "N/A",
                    attr.scale or "N/A",
                    "Yes" if attr.nullable else "No"
                ])

        # Save the workbook
        workbook.save(output_file)
