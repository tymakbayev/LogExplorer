import unittest
from unittest.mock import MagicMock, patch
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from src.ui.main_window import MainWindow

# Create QApplication instance for UI tests
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

class TestMainWindow(unittest.TestCase):
    def setUp(self):
        self.window = MainWindow()
        # Mock the log processor to avoid file operations
        self.window.log_processor = MagicMock()
        self.window.log_processor.total_lines = 100
        self.window.log_processor.get_lines.return_value = [f"Line {i}\n" for i in range(10)]
        self.window.log_processor.search.return_value = [(5, "Line 5 with search term")]
        
    def test_ui_elements_exist(self):
        # Check that all main UI elements exist
        self.assertIsNotNone(self.window.file_path_input)
        self.assertIsNotNone(self.window.search_input)
        self.assertIsNotNone(self.window.case_sensitive_checkbox)
        self.assertIsNotNone(self.window.results_list)
        self.assertIsNotNone(self.window.log_display)
        self.assertIsNotNone(self.window.prev_button)
        self.assertIsNotNone(self.window.next_button)
        
    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
    def test_browse_file(self, mock_file_dialog):
        # Mock file dialog to return a test file path
        mock_file_dialog.return_value = ("/path/to/test.log", "")
        
        # Call browse_file method
        self.window.browse_file()
        
        # Check that file path was set and open_file was called
        self.assertEqual(self.window.file_path_input.text(), "/path/to/test.log")
        self.window.log_processor.open_file.assert_called_once_with("/path/to/test.log")
        
    def test_search_logs(self):
        # Set up test data
        self.window.current_file = "/path/to/test.log"
        self.window.search_input.setText("search term")
        
        # Call search_logs method directly (not through signal to avoid threading)
        with patch('src.ui.main_window.SearchThread'):
            self.window.search_logs()
            
        # Verify search was initiated
        self.assertTrue(self.window.progress_bar.isVisible())
        
    def test_navigation(self):
        # Set up test data
        self.window.current_file = "/path/to/test.log"
        self.window.current_display_start = 10
        
        # Test next page
        self.window.show_next_page()
        self.assertEqual(self.window.current_display_start, 1010)  # 10 + 1000 (lines_per_page)
        
        # Test previous page
        self.window.show_previous_page()
        self.assertEqual(self.window.current_display_start, 10)

if __name__ == "__main__":
    unittest.main()
