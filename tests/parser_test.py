import unittest

from dclgen_parser.parser import DCLGENParser

class TestDCLGENParser(unittest.TestCase):
    def setUp(self):
        self.parser = DCLGENParser()
        self.sample_dclgen = """
           EXEC SQL DECLARE MYSCHEMA.COMPLETE_TABLE TABLE                                 
           ( TIMESTAMP_COL                  TIMESTAMP NOT NULL,                 
             CHAR_COL                       CHAR(8) NOT NULL,                   
             VARCHAR_COL                    VARCHAR(1000) NOT NULL,             
             INTEGER_COL                    INTEGER NOT NULL,
             DECIMAL_COL                    DECIMAL(10,2) NOT NULL,
             SMALL_DEC                      DEC(5) NOT NULL,
             FLOAT_COL                      FLOAT(53) NOT NULL,
             REAL_COL                       REAL NOT NULL,
             DOUBLE_COL                     DOUBLE NOT NULL,
             DATE_COL                       DATE NOT NULL,
             TIME_COL                       TIME NOT NULL,
             BLOB_COL                       BLOB(1M) NOT NULL,
             CLOB_COL                       CLOB(2G) NOT NULL,
             DBCLOB_COL                     DBCLOB(100) NOT NULL,
             BIGINT_COL                     BIGINT NOT NULL,
             SMALLINT_COL                   SMALLINT
           ) END-EXEC.
        """

    def test_table_metadata(self):
        """Test basic table metadata extraction"""
        table = self.parser.parse(self.sample_dclgen)
        self.assertEqual(table.table_name, "COMPLETE_TABLE")
        self.assertEqual(table.schema_name, "MYSCHEMA")
        self.assertEqual(len(table.attributes), 16)

    def test_char_attributes(self):
        """Test parsing of CHAR and VARCHAR types"""
        table = self.parser.parse(self.sample_dclgen)
        
        # Test CHAR
        char_attr = next(attr for attr in table.attributes if attr.name == "CHAR_COL")
        self.assertEqual(char_attr.type, "CHAR")
        self.assertEqual(char_attr.length, 8)
        self.assertFalse(char_attr.nullable)
        
        # Test VARCHAR
        varchar_attr = next(attr for attr in table.attributes if attr.name == "VARCHAR_COL")
        self.assertEqual(varchar_attr.type, "VARCHAR")
        self.assertEqual(varchar_attr.length, 1000)
        self.assertFalse(varchar_attr.nullable)

    def test_decimal_attribute_full(self):
        """Test parsing of DECIMAL type with precision and scale"""
        table = self.parser.parse(self.sample_dclgen)
        decimal_attr = next(attr for attr in table.attributes if attr.name == "DECIMAL_COL")
        self.assertEqual(decimal_attr.type, "DECIMAL")
        self.assertEqual(decimal_attr.precision, 10)
        self.assertEqual(decimal_attr.scale, 2)
        self.assertFalse(decimal_attr.nullable)

    def test_decimal_attribute_no_scale(self):
        """Test parsing of DECIMAL type with only precision"""
        table = self.parser.parse(self.sample_dclgen)
        decimal_attr = next(attr for attr in table.attributes if attr.name == "SMALL_DEC")
        self.assertEqual(decimal_attr.type, "DECIMAL")
        self.assertEqual(decimal_attr.precision, 5)
        self.assertEqual(decimal_attr.scale, 0)
        self.assertFalse(decimal_attr.nullable)

    def test_float_attributes(self):
        """Test parsing of different floating point types"""
        table = self.parser.parse(self.sample_dclgen)
        
        # Test FLOAT with precision
        float_attr = next(attr for attr in table.attributes if attr.name == "FLOAT_COL")
        self.assertEqual(float_attr.type, "FLOAT")
        self.assertEqual(float_attr.precision, 53)
        self.assertFalse(float_attr.nullable)
        
        # Test REAL
        real_attr = next(attr for attr in table.attributes if attr.name == "REAL_COL")
        self.assertEqual(real_attr.type, "REAL")
        self.assertIsNone(real_attr.precision)
        self.assertFalse(real_attr.nullable)
        
        # Test DOUBLE
        double_attr = next(attr for attr in table.attributes if attr.name == "DOUBLE_COL")
        self.assertEqual(double_attr.type, "DOUBLE")
        self.assertIsNone(double_attr.precision)
        self.assertFalse(double_attr.nullable)

    def test_datetime_attributes(self):
        """Test parsing of date and time types"""
        table = self.parser.parse(self.sample_dclgen)
        
        # Test DATE
        date_attr = next(attr for attr in table.attributes if attr.name == "DATE_COL")
        self.assertEqual(date_attr.type, "DATE")
        self.assertFalse(date_attr.nullable)
        
        # Test TIME
        time_attr = next(attr for attr in table.attributes if attr.name == "TIME_COL")
        self.assertEqual(time_attr.type, "TIME")
        self.assertFalse(time_attr.nullable)
        
        # Test TIMESTAMP
        timestamp_attr = next(attr for attr in table.attributes if attr.name == "TIMESTAMP_COL")
        self.assertEqual(timestamp_attr.type, "TIMESTAMP")
        self.assertFalse(timestamp_attr.nullable)

    def test_lob_attributes(self):
        """Test parsing of LOB types"""
        table = self.parser.parse(self.sample_dclgen)
        
        # Test BLOB
        blob_attr = next(attr for attr in table.attributes if attr.name == "BLOB_COL")
        self.assertEqual(blob_attr.type, "BLOB")
        self.assertEqual(blob_attr.length, 1)  # 1M
        self.assertFalse(blob_attr.nullable)
        
        # Test CLOB
        clob_attr = next(attr for attr in table.attributes if attr.name == "CLOB_COL")
        self.assertEqual(clob_attr.type, "CLOB")
        self.assertEqual(clob_attr.length, 2)  # 2G
        self.assertFalse(clob_attr.nullable)
        
        # Test DBCLOB
        dbclob_attr = next(attr for attr in table.attributes if attr.name == "DBCLOB_COL")
        self.assertEqual(dbclob_attr.type, "DBCLOB")
        self.assertEqual(dbclob_attr.length, 100)
        self.assertFalse(dbclob_attr.nullable)

    def test_integer_attributes(self):
        """Test parsing of integer types"""
        table = self.parser.parse(self.sample_dclgen)
        
        # Test INTEGER
        int_attr = next(attr for attr in table.attributes if attr.name == "INTEGER_COL")
        self.assertEqual(int_attr.type, "INTEGER")
        self.assertFalse(int_attr.nullable)
        
        # Test BIGINT
        bigint_attr = next(attr for attr in table.attributes if attr.name == "BIGINT_COL")
        self.assertEqual(bigint_attr.type, "BIGINT")
        self.assertFalse(bigint_attr.nullable)
        
        # Test SMALLINT and nullable
        smallint_attr = next(attr for attr in table.attributes if attr.name == "SMALLINT_COL")
        self.assertEqual(smallint_attr.type, "SMALLINT")
        self.assertTrue(smallint_attr.nullable)

    def test_invalid_dclgen(self):
        """Test parsing invalid DCLGEN content"""
        invalid_content = """
        This is not a valid DCLGEN file
        """
        with self.assertRaises(ValueError) as context:
            self.parser.parse(invalid_content)
        self.assertTrue("Could not find table declaration" in str(context.exception))

    def test_empty_table(self):
        """Test parsing a table with no attributes"""
        empty_table = """
           EXEC SQL DECLARE EMPTY_TABLE TABLE                                 
           (
           ) END-EXEC.
        """
        table = self.parser.parse(empty_table)
        self.assertEqual(len(table.attributes), 0)

    def test_malformed_declaration(self):
        """Test handling of malformed attribute declarations"""
        malformed_dclgen = """
           EXEC SQL DECLARE MALFORMED_TABLE TABLE                                 
           ( BAD_COL                        UNKNOWN_TYPE NOT NULL,
             GOOD_COL                       INTEGER NOT NULL
           ) END-EXEC.
        """
        table = self.parser.parse(malformed_dclgen)
        bad_col = next(attr for attr in table.attributes if attr.name == "BAD_COL")
        self.assertEqual(bad_col.type, "UNKNOWN_TYPE")  # SimpleAttributeParser handles unknown types

    def test_multiline_timestamp_declaration_with_comments(self):
        """Test parsing of TIMESTAMP WITH TIME ZONE that spans multiple lines"""
        multiline_dclgen = """
           EXEC SQL DECLARE TEST_TABLE TABLE                                 
           ( REGULAR_COL                    INTEGER NOT NULL,
CR0146       MULTILINE_TS                   TIMESTAMP
CR0146                                         WITH TIME ZONE NOT NULL,
CR0146       D_BSN_DT_INI                   DATE NOT NULL              
           ) END-EXEC.
        """
        table = self.parser.parse(multiline_dclgen)
        
        # Verify we got both columns
        self.assertEqual(len(table.attributes), 3)
        
        # Check the timestamp column
        ts_attr = next(attr for attr in table.attributes if attr.name == "MULTILINE_TS")
        self.assertEqual(ts_attr.type, "TIMESTAMP")
        self.assertFalse(ts_attr.nullable)

    def test_cobol_comments_in_declaration(self):
        """Test handling of COBOL comment lines (*) in attribute declarations"""
        dclgen_with_comments = """
           EXEC SQL DECLARE TEST_TABLE TABLE                                 
           ( FIRST_COL                     CHAR(16) NOT NULL,
CR0146*      OLD_COLUMN                     CHAR(16) NOT NULL,
CR0146       ACTUAL_COLUMN                  CHAR(35) NOT NULL,
             LAST_COL                      INTEGER NOT NULL
           ) END-EXEC.
        """
        table = self.parser.parse(dclgen_with_comments)
        
        # Should only have 3 columns (commented one should be ignored)
        self.assertEqual(len(table.attributes), 3)
        
        # Verify the correct columns are present
        attr_names = {attr.name for attr in table.attributes}
        self.assertSetEqual(attr_names, {"FIRST_COL", "ACTUAL_COLUMN", "LAST_COL"})
        
        # Verify no attributes with name "*" exist
        self.assertFalse(any(attr.name == "*" for attr in table.attributes))
