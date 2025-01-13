from pathlib import Path
from typing import Dict, List, NamedTuple
from dclgen_parser.parser import DCLGENParser  # Import the parser we created earlier

class TableStats(NamedTuple):
    """Statistics for a single table"""
    filename: str
    attribute_count: int
    schema:str


class DCLGENScanner:
    """Scans directories for DCLGEN files and processes them"""
    
    def __init__(self):
        self.parser = DCLGENParser()
        
    def is_dclgen_file(self, file_path: Path) -> bool:
        """
        Check if a file is likely a DCLGEN file by looking for typical DCLGEN content
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                return 'DCLGEN TABLE' in content and 'EXEC SQL DECLARE' in content
        except (UnicodeDecodeError, IOError):
            return False
            
    def scan_directory(self, directory_path: str) -> Dict[str, List[TableStats]]:
        """
        Scan a directory for DCLGEN files and process them
        Returns a dictionary mapping table names to their statistics
        """
        tables_stats: Dict[str, List[TableStats]] = {}
        
        # Convert to Path object for easier manipulation
        base_path = Path(directory_path)
        
        # Walk through all files in the directory and subdirectories
        for file_path in base_path.rglob('*'):
            if not file_path.is_file():
                continue
                
            if not self.is_dclgen_file(file_path):
                continue
                
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    table = self.parser.parse(content)
                    
                    # Create stats for this table
                    stats = TableStats(
                        filename=str(file_path.relative_to(base_path)),
                        attribute_count=len(table.attributes),
                        schema=table.schema_name if table.schema_name else ""
                    )
                    
                    # Ensure each table is only defined once
                    if table.table_name in tables_stats:
                        raise ValueError(f"Table '{table.table_name}' is defined more than once")
                    
                    tables_stats[table.table_name] = [stats]
                    
            except Exception as e:
                raise e
                    
        return tables_stats
    
