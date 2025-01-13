from typing import Dict, List
import csv

from dclgen_parser.parser import Table

class ReportGenerator:
    """Generates CSV reports from DCLGEN scanning results"""
    
    def generate_report(self, tables_stats: Dict[str, List[TableStats]], output_file: str):
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
                stats_list = tables_stats[table_name]
                for stats in stats_list:
                    normalized_filename = stats.filename.rsplit('.', 1)[0].upper()
                    writer.writerow([
                        table_name,
                        stats.attribute_count,
                        stats.filename,
                        stats.schema,
                        normalized_filename
                    ])
