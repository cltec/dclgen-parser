import unittest

from dclgen_parser.parser import DCLGENParser

class TestDCLGENParser(unittest.TestCase):
    def setUp(self):
        self.parser = DCLGENParser()
        self.sample_dclgen = """
           EXEC SQL DECLARE EIP_ADT_TRAIL TABLE                                 
           ( S_DT_TM                        TIMESTAMP NOT NULL,                 
             C_USER_1                       CHAR(8) NOT NULL,                   
             C_USER_2                       CHAR(8) NOT NULL,                   
             C_SRVC_ID                      CHAR(3) NOT NULL,                   
             P_EVNT_TP                      CHAR(3) NOT NULL,                   
             X_EVNT_DSCR                    VARCHAR(1000) NOT NULL,             
             C_PRG_REF                      CHAR(20) NOT NULL,                  
             C_BIC_CD                       CHAR(11) NOT NULL,                  
             C_SYS_ALT_REF                  INTEGER NOT NULL                    
           ) END-EXEC.
        """
        
        self.schema_in_declare = """
           EXEC SQL DECLARE SCHEMA1.TABLE1 TABLE                                 
           ( FIELD1                        INTEGER NOT NULL                    
           ) END-EXEC.
        """
        
        self.schema_in_dclgen = """
      ******************************************************************        
      * DCLGEN TABLE(SCHEMA2.TABLE2)                                    *        
      ******************************************************************        
           EXEC SQL DECLARE TABLE2 TABLE                                 
           ( FIELD1                        INTEGER NOT NULL                    
           ) END-EXEC.
        """
        
        self.both_schemas = """
      ******************************************************************        
      * DCLGEN TABLE(SCHEMA3.TABLE3)                                    *        
      ******************************************************************        
           EXEC SQL DECLARE SCHEMA4.TABLE3 TABLE                                 
           ( FIELD1                        INTEGER NOT NULL                    
           ) END-EXEC.
        """

    def test_table_name_extraction(self):
        table = self.parser.parse(self.sample_dclgen)
        self.assertEqual(table.table_name, "EIP_ADT_TRAIL")

    def test_attributes_count(self):
        table = self.parser.parse(self.sample_dclgen)
        self.assertEqual(len(table.attributes), 9)

    def test_timestamp_attribute(self):
        table = self.parser.parse(self.sample_dclgen)
        timestamp_attr = next(attr for attr in table.attributes if attr.name == "S_DT_TM")
        self.assertEqual(timestamp_attr.type, "TIMESTAMP")
        self.assertFalse(timestamp_attr.nullable)

    def test_char_attribute(self):
        table = self.parser.parse(self.sample_dclgen)
        char_attr = next(attr for attr in table.attributes if attr.name == "C_USER_1")
        self.assertEqual(char_attr.type, "CHAR")
        self.assertEqual(char_attr.length, 8)
        self.assertFalse(char_attr.nullable)

    def test_varchar_attribute(self):
        table = self.parser.parse(self.sample_dclgen)
        varchar_attr = next(attr for attr in table.attributes if attr.name == "X_EVNT_DSCR")
        self.assertEqual(varchar_attr.type, "VARCHAR")
        self.assertEqual(varchar_attr.length, 1000)
        self.assertFalse(varchar_attr.nullable)

    def test_integer_attribute(self):
        table = self.parser.parse(self.sample_dclgen)
        integer_attr = next(attr for attr in table.attributes if attr.name == "C_SYS_ALT_REF")
        self.assertEqual(integer_attr.type, "INTEGER")
        self.assertFalse(integer_attr.nullable)
        self.assertIsNone(integer_attr.length)  # INTEGER type should not have length

    def test_no_schema(self):
        """Test case when no schema is present"""
        table = self.parser.parse(self.sample_dclgen)
        self.assertIsNone(table.schema_name)
        self.assertEqual(table.table_name, "EIP_ADT_TRAIL")

    def test_schema_in_declare_statement(self):
        """Test extraction of schema from DECLARE statement"""
        table = self.parser.parse(self.schema_in_declare)
        self.assertEqual(table.schema_name, "SCHEMA1")
        self.assertEqual(table.table_name, "TABLE1")

    def test_schema_in_dclgen_statement(self):
        """Test extraction of schema from DCLGEN TABLE statement"""
        table = self.parser.parse(self.schema_in_dclgen)
        self.assertEqual(table.schema_name, "SCHEMA2")
        self.assertEqual(table.table_name, "TABLE2")

    def test_schema_precedence(self):
        """Test that DECLARE statement schema takes precedence over DCLGEN TABLE schema"""
        table = self.parser.parse(self.both_schemas)
        self.assertEqual(table.schema_name, "SCHEMA4")
        self.assertEqual(table.table_name, "TABLE3")
