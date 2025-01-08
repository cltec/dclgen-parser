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
    """Parser for CHAR type attributes"""
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

class SimpleAttributeParser(AttributeParser):
    """Parser for simple types (INTEGER, TIMESTAMP, etc.)"""
    def can_parse(self, declaration: str) -> bool:
        return True  # Fallback parser for all other types

    def parse(self, declaration: str) -> Attribute:
        parts = declaration.strip().split()
        name = parts[0].strip()
        dtype = parts[1].strip()
        nullable = "NOT NULL" not in declaration
        
        return Attribute(name=name, type=dtype, nullable=nullable)

class DCLGENParser:
    """Main parser class for DCLGEN files"""
    def __init__(self):
        self.parsers: List[AttributeParser] = [
            CharAttributeParser(),
            SimpleAttributeParser()  # Fallback parser
        ]

    def _extract_schema_and_table_names(self, content: str) -> tuple[str, Optional[str]]:
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
        sql_block_match = re.search(r'DECLARE.*?TABLE\s*\((.*?)\)\s*END-EXEC', 
                                  content, re.DOTALL)
        if not sql_block_match:
            raise ValueError("Could not find SQL declaration block")

        attributes = []
        declarations = sql_block_match.group(1).strip().split(',')
        
        for decl in declarations:
            decl = decl.strip()
            if not decl:
                continue
                
            # Find appropriate parser
            parser = next(p for p in self.parsers if p.can_parse(decl))
            attribute = parser.parse(decl)
            attributes.append(attribute)

        return attributes

    def parse(self, content: str) -> Table:
        """Parse DCLGEN content and return Table object"""
        table_name, schema_name = self._extract_schema_and_table_names(content)
        attributes = self._extract_attributes(content)
        return Table(table_name=table_name, schema_name=schema_name, attributes=attributes)
