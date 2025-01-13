from openpyxl import Workbook
from dclgen_parser.parser import Table

class ExcelReporter:
    """Generates Excel reports from parsed table data"""

    def generate_excel_report(self, table: Table, output_file: str):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Table Information"

        # Add headers
        headers = ["Name", "Type", "Length", "Precision", "Scale", "Nullable"]
        sheet.append(headers)

        # Add attribute data
        for attr in table.attributes:
            sheet.append([
                attr.name,
                attr.type,
                attr.length or "N/A",
                attr.precision or "N/A",
                attr.scale or "N/A",
                "Yes" if attr.nullable else "No"
            ])

        # Save the workbook
        workbook.save(output_file)
