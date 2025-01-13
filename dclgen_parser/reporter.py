from typing import Dict, List
import csv

from dclgen_parser.parser import Table

class ReportGenerator:
    """Generates CSV reports from DCLGEN scanning results"""
    
    def generate_report(self, tables_stats: Dict[str, Table], output_file: str):
        """Generate a CSV report of the DCLGEN scanning results"""
        # Ensure output file has .csv extension
        if not output_file.lower().endswith('.csv'):
            output_file = output_file + '.csv'
            
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([ 'Table Name', 'Number of Attributes', 'File Path', 'Schema', 'Normalized File Name'])
            
            # Write data rows
            for table_name in sorted(tables_stats.keys()):
                table = tables_stats[table_name]
                normalized_filename = table.table_name.upper()
                writer.writerow([
                    table_name,
                    len(table.attributes),
                    "N/A",  # File path is not available in this context
                    table.schema_name or "N/A",
                    normalized_filename
                ])
                    writer.writerow([
                        table_name,
                        stats.attribute_count,
                        stats.filename,
                        stats.schema,
                        normalized_filename
                    ])
