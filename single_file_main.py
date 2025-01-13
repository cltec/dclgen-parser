import sys
import argparse
import os
from prettytable import PrettyTable
from dclgen_parser.parser import DCLGENParser
from dclgen_parser.excel_reporter import ExcelReporter

def print_table_info(table):
    """Print general table information"""
    print("\nTable Information:")
    info_table = PrettyTable()
    info_table.field_names = ["Property", "Value"]
    info_table.align["Property"] = "l"
    info_table.align["Value"] = "l"
    
    info_table.add_row(["Table Name", table.table_name])
    info_table.add_row(["Schema Name", table.schema_name or "N/A"])
    info_table.add_row(["Total Attributes", len(table.attributes)])
    
    print(info_table)

def print_attributes(attributes):
    """Print detailed attribute information"""
    print("\nAttributes:")
    attr_table = PrettyTable()
    attr_table.field_names = ["Name", "Type", "Length", "Precision", "Scale", "Nullable"]
    attr_table.align = "l"  # Left align all columns
    
    for attr in attributes:
        attr_table.add_row([
            attr.name,
            attr.type,
            attr.length or "N/A",
            attr.precision or "N/A",
            attr.scale or "N/A",
            "Yes" if attr.nullable else "No"
        ])
    
    print(attr_table)

def main():
    parser = argparse.ArgumentParser(description='Parse a single DCLGEN file and display its contents')
    parser.add_argument('file', help='Path to the DCLGEN file to parse')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show the file content before parsing')
    
    args = parser.parse_args()
    
    try:
        # Read the file
        file_path = os.path.abspath(args.file)
        with open(file_path, 'r') as f:
            content = f.read()
            
        if args.verbose:
            print("\nFile Content:")
            print("=" * 80)
            print(content)
            print("=" * 80)
        
        # Parse the file
        dclgen_parser = DCLGENParser()
        table = dclgen_parser.parse(content)
        
        # Print results
        print("\nDCLGEN File Analysis Report")
        print("=" * 80)
        
        # Print table information
        print_table_info(table)
        
        # Print attribute details
        print_attributes(table.attributes)
    
        # Generate Excel report
        excel_reporter = ExcelReporter()
        excel_file_name = os.path.splitext(os.path.basename(file_path))[0] + ".xlsx"
        excel_reporter.generate_excel_report([table], excel_file_name)
        print(f"\nExcel report generated: {excel_file_name}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
