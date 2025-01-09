import os
import argparse

from dclgen_parser.reporter import ReportGenerator

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
    
    # Generate report
    report_generator = ReportGenerator()
    report_generator.generate_report(tables_stats, args.output)
    
    print(f"CSV report generated: {args.output}")
    return 0

if __name__ == '__main__':
    exit(main())
