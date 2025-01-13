import os
import argparse
from datetime import datetime

from dclgen_parser.excel_reporter import ExcelReporter

from dclgen_parser.scanner import DCLGENScanner

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Scan directory for DCLGEN files and generate CSV report')
    parser.add_argument('directory', help='Directory to scan for DCLGEN files')
    parser.add_argument('--output', '-o', 
                       default='dclgen_report.csv',
                       help='Output file for the CSV report (default: dclgen_report.csv)')
    
    args = parser.parse_args()
    
    # Verify directory exists
    directory_path = os.path.abspath(args.directory)
    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' does not exist")
        return 1
        
    # Create scanner and process files
    scanner = DCLGENScanner()
    tables_stats = scanner.scan_directory(args.directory)
    
    # Generate Excel report
    excel_reporter = ExcelReporter()
    excel_file_name = f"report_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    excel_reporter.generate_excel_report(list(tables_stats.values()), excel_file_name)
    
    print(f"Excel report generated: {excel_file_name}")
    return 0

if __name__ == '__main__':
    exit(main())
