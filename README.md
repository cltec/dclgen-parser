# DCLGEN Parser

A Python library for parsing COBOL DCLGEN files that contain DB2 table declarations. The library extracts table metadata, column definitions, and data types, handling COBOL's fixed format structure and providing a clean interface to the parsed data.

## Features

- Parse DB2 table declarations from DCLGEN files
- Handle COBOL fixed format source code
- Support for multiple DB2 data types:
  - Character types (CHAR, VARCHAR)
  - Numeric types (INTEGER, SMALLINT, BIGINT)
  - Decimal types (DECIMAL, DEC)
  - Floating point types (FLOAT, REAL, DOUBLE)
  - Date/Time types (DATE, TIME, TIMESTAMP)
  - LOB types (BLOB, CLOB, DBCLOB)
- Extract schema and table names
- Handle COBOL source code comments
- Generate CSV reports with table statistics

## Usage

### Basic Usage

```python
from dclgen_parser.parser import DCLGENParser

# Initialize parser
parser = DCLGENParser()

# Parse a DCLGEN file
with open('path/to/dclgen/file.dclgen', 'r') as f:
    content = f.read()
    table = parser.parse(content)

# Access parsed data
print(f"Table name: {table.table_name}")
print(f"Schema: {table.schema_name}")
for attr in table.attributes:
    print(f"Column: {attr.name}, Type: {attr.type}")
```

### Scanning Multiple Files

```python
from dclgen_parser.scanner import DCLGENScanner
from dclgen_parser.reporter import ReportGenerator

# Initialize scanner
scanner = DCLGENScanner()

# Scan directory for DCLGEN files
stats = scanner.scan_directory('path/to/dclgen/files')

# Generate report
reporter = ReportGenerator()
reporter.generate_report(stats, 'output_report.csv')
```

## Command Line Interface

The package includes a command-line tool for quick analysis of DCLGEN files:

```bash
poetry run python main.py path/to/dclgen/file.dclgen
```

Optional flags:
- `-v, --verbose`: Show the raw file content before parsing

## Project Structure

```
dclgen-parser/
├── dclgen_parser/
│   ├── __init__.py
│   ├── parser.py      # Core parsing logic
│   ├── scanner.py     # Directory scanning functionality
│   └── reporter.py    # Report generation
├── tests/
│   ├── __init__.py
│   ├── parser_test.py
│   ├── scanner_test.py
│   └── reporter_test.py
├── main.py            # CLI interface
├── pyproject.toml
└── README.md
```

## Testing

Run the test suite:

```bash
poetry run pytest
```

## Known Limitations

- Only handles DB2 table declarations in DCLGEN format
- No support for table constraints (PRIMARY KEY, FOREIGN KEY)
- Single file processing in CLI mode

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a new Pull Request

