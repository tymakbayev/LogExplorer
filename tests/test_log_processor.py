import unittest
import os
import tempfile
from src.core.log_processor import LogProcessor

class TestLogProcessor(unittest.TestCase):
    def setUp(self):
        self.log_processor = LogProcessor()
        
        # Create a temporary log file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file_path = self.temp_file.name
        
        # Write test data
        test_data = (
            "2023-01-01 12:00:00 INFO: System started\n"
            "2023-01-01 12:01:00 DEBUG: Connection established\n"
            "2023-01-01 12:02:00 ERROR: Failed to process request\n"
            "2023-01-01 12:03:00 INFO: User logged in\n"
            "2023-01-01 12:04:00 WARNING: High memory usage\n"
        )
        self.temp_file.write(test_data.encode('utf-8'))
        self.temp_file.close()
        
    def tearDown(self):
        self.log_processor.close()
        os.unlink(self.temp_file_path)
        
    def test_open_file(self):
        result = self.log_processor.open_file(self.temp_file_path)
        self.assertTrue(result)
        self.assertEqual(self.log_processor.total_lines, 5)
        
    def test_get_line(self):
        self.log_processor.open_file(self.temp_file_path)
        line = self.log_processor.get_line(2)
        self.assertIn("ERROR: Failed to process request", line)
        
    def test_get_lines(self):
        self.log_processor.open_file(self.temp_file_path)
        lines = self.log_processor.get_lines(1, 3)
        self.assertEqual(len(lines), 2)
        self.assertIn("DEBUG: Connection established", lines[0])
        self.assertIn("ERROR: Failed to process request", lines[1])
        
    def test_search(self):
        self.log_processor.open_file(self.temp_file_path)
        results = self.log_processor.search("ERROR")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], 2)  # Line number
        
        # Case insensitive search
        results = self.log_processor.search("error", case_sensitive=False)
        self.assertEqual(len(results), 1)
        
        # Case sensitive search
        results = self.log_processor.search("error", case_sensitive=True)
        self.assertEqual(len(results), 0)
        
    def test_search_with_regex(self):
        self.log_processor.open_file(self.temp_file_path)
        # Search with regex pattern
        results = self.log_processor.search(r"\d{2}:\d{2}:\d{2}")
        self.assertEqual(len(results), 5)  # All lines have time stamps

if __name__ == "__main__":
    unittest.main()
