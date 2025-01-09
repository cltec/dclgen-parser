from dataclasses import dataclass
from typing import List, Optional
import re
from abc import ABC, abstractmethod

@dataclass
class Attribute:
    """Represents a database table attribute/column"""
    name: str
    type: str
    length: Optional[int] = None
    precision: Optional[int] = None  # For DECIMAL type
    scale: Optional[int] = None      # For DECIMAL type
    nullable: bool = True

@dataclass
class Table:
    """Represents a database table"""
    table_name: str
    schema_name: Optional[str]
    attributes: List[Attribute]

class AttributeParser(ABC):
    """Abstract base class for attribute parsing strategies"""
    @abstractmethod
    def can_parse(self, declaration: str) -> bool:
        pass

    @abstractmethod
    def parse(self, declaration: str) -> Attribute:
        pass

class CharAttributeParser(AttributeParser):
    """Parser for CHAR and VARCHAR type attributes"""
    def can_parse(self, declaration: str) -> bool:
        return "CHAR(" in declaration or "VARCHAR(" in declaration

    def parse(self, declaration: str) -> Attribute:
        parts = declaration.strip().split()
        name = parts[0].strip()
        type_part = " ".join(parts[1:])
        
        # Extract length
        length_match = re.search(r'(?:VAR)?CHAR\((\d+)\)', type_part)
        length = int(length_match.group(1)) if length_match else None
        
        # Determine if it's VARCHAR or CHAR
        dtype = "VARCHAR" if "VARCHAR" in type_part else "CHAR"
        
        # Check nullable
        nullable = "NOT NULL" not in type_part
        
        return Attribute(name=name, type=dtype, length=length, nullable=nullable)

class DecimalAttributeParser(AttributeParser):
    """Parser for DECIMAL type attributes"""
    def can_parse(self, declaration: str) -> bool:
        type_part = declaration.upper().split()[1] if len(declaration.split()) > 1 else ""
        return type_part.startswith("DEC") or type_part.startswith("DECIMAL")

    def parse(self, declaration: str) -> Attribute:
        parts = declaration.strip().split()
        name = parts[0].strip()
        type_part = " ".join(parts[1:]).upper()

        # Extract precision and scale
        # Handle both DECIMAL(p,s) and DEC(p,s) formats
        decimal_match = re.search(r'(?:DECIMAL|DEC)\s*\((\d+)(?:\s*,\s*(\d+))?\)', type_part, re.IGNORECASE)
        if not decimal_match:
            raise ValueError(f"Invalid DECIMAL format in declaration: {declaration}")
            
        precision = int(decimal_match.group(1))
        scale = int(decimal_match.group(2)) if decimal_match.group(2) else 0

        nullable = "NOT NULL" not in type_part
        
        return Attribute(
            name=name,
            type="DECIMAL",
            precision=precision,
            scale=scale,
            nullable=nullable
        )

class FloatAttributeParser(AttributeParser):
    """Parser for FLOAT type attributes"""
    def can_parse(self, declaration: str) -> bool:
        return any(type_name in declaration.upper() for type_name in ["FLOAT", "REAL", "DOUBLE"])

    def parse(self, declaration: str) -> Attribute:
        parts = declaration.strip().split()
        name = parts[0].strip()
        type_part = " ".join(parts[1:]).upper()
        
        # Determine specific float type
        if "REAL" in type_part:
            dtype = "REAL"
        elif "DOUBLE" in type_part:
            dtype = "DOUBLE"
        else:
            dtype = "FLOAT"
            
        # Check for precision in FLOAT
        precision = None
        if dtype == "FLOAT":
            precision_match = re.search(r'FLOAT\((\d+)\)', type_part)
            if precision_match:
                precision = int(precision_match.group(1))
        
        nullable = "NOT NULL" not in type_part
        
        return Attribute(name=name, type=dtype, precision=precision, nullable=nullable)

class DateTimeAttributeParser(AttributeParser):
    """Parser for DATE, TIME, and TIMESTAMP type attributes"""
    def can_parse(self, declaration: str) -> bool:
        return any(type_name in declaration.upper() for type_name in ["DATE", "TIME", "TIMESTAMP"])

    def parse(self, declaration: str) -> Attribute:
        parts = declaration.strip().split()
        name = parts[0].strip()
        type_part = " ".join(parts[1:]).upper()
        
        # Determine specific type
        if "TIMESTAMP" in type_part:
            dtype = "TIMESTAMP"
        elif "TIME" in type_part:
            dtype = "TIME"
        else:
            dtype = "DATE"
            
        nullable = "NOT NULL" not in type_part
        
        return Attribute(name=name, type=dtype, nullable=nullable)

class BlobAttributeParser(AttributeParser):
    """Parser for BLOB, CLOB, and DBCLOB type attributes"""
    def can_parse(self, declaration: str) -> bool:
        return any(type_name in declaration.upper() for type_name in ["BLOB", "CLOB", "DBCLOB"])

    def parse(self, declaration: str) -> Attribute:
        parts = declaration.strip().split()
        name = parts[0].strip()
        type_part = " ".join(parts[1:]).upper()
        
        # Determine specific type
        if "DBCLOB" in type_part:
            dtype = "DBCLOB"
        elif "CLOB" in type_part:
            dtype = "CLOB"
        else:
            dtype = "BLOB"
            
        # Extract length if specified
        length_match = re.search(rf'{dtype}\((\d+)(?:K|M|G)?\)', type_part)
        length = int(length_match.group(1)) if length_match else None
        
        nullable = "NOT NULL" not in type_part
        
        return Attribute(name=name, type=dtype, length=length, nullable=nullable)

class SimpleAttributeParser(AttributeParser):
    """Parser for simple types (INTEGER, SMALLINT, BIGINT)"""
    def can_parse(self, declaration: str) -> bool:
        return True  # Fallback parser for all other types

    def parse(self, declaration: str) -> Attribute:
        parts = declaration.strip().split()
        name = parts[0].strip()
        dtype = parts[1].strip().upper()
        nullable = "NOT NULL" not in declaration
        
        return Attribute(name=name, type=dtype, nullable=nullable)

class DCLGENParser:
    """Main parser class for DCLGEN files"""
    def __init__(self):
        self.parsers: List[AttributeParser] = [
            CharAttributeParser(),
            DecimalAttributeParser(),
            FloatAttributeParser(),
            DateTimeAttributeParser(),
            BlobAttributeParser(),
            SimpleAttributeParser()  # Fallback parser
        ]

    def _extract_schema_and_table_names(self, content: str) -> Tuple[str, Optional[str]]:
        """Extract schema and table name from DCLGEN content"""
        # First try to get schema from DCLGEN TABLE declaration
        dclgen_schema = None
        dclgen_match = re.search(r'DCLGEN\s+TABLE\(([\w.]+)\)', content)
        if dclgen_match:
            dclgen_parts = dclgen_match.group(1).split('.')
            if len(dclgen_parts) == 2:
                dclgen_schema = dclgen_parts[0]

        # Extract table name from DECLARE statement - handling schema-qualified names
        table_match = re.search(r'DECLARE\s+([\w.]+)\s+TABLE', content)
        if not table_match:
            raise ValueError("Could not find table declaration in DCLGEN")
            
        full_table_name = table_match.group(1)
        # Split schema and table name
        parts = full_table_name.split('.')
        if len(parts) == 2:
            schema_name, table_name = parts
        else:
            schema_name = dclgen_schema  # Use schema from DCLGEN TABLE if available
            table_name = full_table_name
            
        return table_name, schema_name

    def _extract_attributes(self, content: str) -> List[Attribute]:
        """Extract attributes from DCLGEN content"""
        # Find the SQL declaration block
        sql_block_match = re.search(r'DECLARE.*?TABLE\s*\((.*?)\)\s*END-EXEC\.', 
                                  content, re.DOTALL | re.IGNORECASE)
        if not sql_block_match:
            raise ValueError("Could not find SQL declaration block")

        attributes = []
        # Get the full declaration block
        sql_block = sql_block_match.group(1).strip()
        
        # Split declarations while preserving commas inside parentheses
        declarations = []
        current_decl = []
        paren_count = 0
        
        # Split into lines first to handle potential formatting
        for char in sql_block:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            
            if char == ',' and paren_count == 0:
                # End of declaration
                if current_decl:
                    declarations.append(''.join(current_decl).strip())
                current_decl = []
            else:
                current_decl.append(char)
        
        # Add the last declaration if exists
        if current_decl:
            declarations.append(''.join(current_decl).strip())
        
        # Process each declaration
        for decl in declarations:
            if not decl.strip():
                continue
                
            # Find appropriate parser
            parser = next(p for p in self.parsers if p.can_parse(decl))
            attribute = parser.parse(decl)
            attributes.append(attribute)

        return attributes

    def _clean_cobol_format(self, content: str) -> str:
        """Clean COBOL fixed-format content by removing sequence numbers, line identifiers and comments"""
        cleaned_lines = []
        for line in content.splitlines():
            # Skip empty lines
            if not line.strip():
                cleaned_lines.append(line)
                continue
            
            # If line is shorter than 7 characters, preserve it as is
            if len(line) < 7:
                cleaned_lines.append(line)
                continue
            
            # Check if it's a comment line (asterisk in column 7)
            if len(line) > 6 and line[6] == '*':
                continue
                
            # Remove sequence numbers (1-6) and keep only the content starting from column 7
            # For longer lines, also remove the identification area (73-80)
            content_line = line[6:72] if len(line) > 72 else line[6:]
            cleaned_lines.append(content_line)
            
        return '\n'.join(cleaned_lines)

    def parse(self, content: str) -> Table:
        """Parse DCLGEN content and return Table object"""
        # Clean up COBOL fixed-format content first
        cleaned_content = self._clean_cobol_format(content)
        table_name, schema_name = self._extract_schema_and_table_names(cleaned_content)
        attributes = self._extract_attributes(cleaned_content)
        return Table(table_name=table_name, schema_name=schema_name, attributes=attributes)
