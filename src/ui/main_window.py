import os
import time
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLineEdit, QFileDialog, QLabel, 
                             QTextEdit, QCheckBox, QProgressBar, QSplitter,
                             QListWidget, QListWidgetItem, QComboBox, QMessageBox,
                             QShortcut, QMenu, QAction)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QKeySequence, QTextCursor, QFont, QColor

from src.core.log_processor import LogProcessor

class SearchThread(QThread):
    search_complete = pyqtSignal(list)
    progress_update = pyqtSignal(int)
    
    def __init__(self, log_processor, search_text, case_sensitive):
        super().__init__()
        self.log_processor = log_processor
        self.search_text = search_text
        self.case_sensitive = case_sensitive
        
    def run(self):
        results = self.log_processor.search(self.search_text, self.case_sensitive)
        self.search_complete.emit(results)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.log_processor = LogProcessor()
        self.current_file = None
        self.search_results = []
        self.current_display_start = 0
        self.lines_per_page = 1000
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("LogExplorer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # File selection area
        file_layout = QHBoxLayout()
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Log file path...")
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path_input)
        file_layout.addWidget(browse_button)
        main_layout.addLayout(file_layout)
        
        # Search area
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search pattern...")
        self.search_input.returnPressed.connect(self.search_logs)
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_logs)
        self.case_sensitive_checkbox = QCheckBox("Case Sensitive")
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        search_layout.addWidget(self.case_sensitive_checkbox)
        main_layout.addLayout(search_layout)
        
        # Splitter for results and content
        splitter = QSplitter(Qt.Vertical)
        
        # Results area
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        results_label = QLabel("Search Results:")
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.show_selected_result)
        results_layout.addWidget(results_label)
        results_layout.addWidget(self.results_list)
        results_widget.setLayout(results_layout)
        
        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_label = QLabel("Log Content:")
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Courier New", 10))
        content_layout.addWidget(content_label)
        content_layout.addWidget(self.log_display)
        content_widget.setLayout(content_layout)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous Page")
        self.prev_button.clicked.connect(self.show_previous_page)
        self.next_button = QPushButton("Next Page")
        self.next_button.clicked.connect(self.show_next_page)
        self.page_info_label = QLabel("Page: 0/0")
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.page_info_label)
        nav_layout.addWidget(self.next_button)
        content_layout.addLayout(nav_layout)
        
        # Add widgets to splitter
        splitter.addWidget(results_widget)
        splitter.addWidget(content_widget)
        splitter.setSizes([200, 600])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(lambda: self.search_input.setFocus())
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.browse_file)
        
        # Context menu for results
        self.results_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_list.customContextMenuRequested.connect(self.show_context_menu)
        
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Log File", "", "All Files (*);;Text Files (*.txt);;Log Files (*.log)")
        if file_path:
            self.file_path_input.setText(file_path)
            self.open_file(file_path)
    
    def open_file(self, file_path):
        self.status_bar.showMessage(f"Opening file: {file_path}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Use a timer to allow the UI to update before processing
        QTimer.singleShot(100, lambda: self._process_file_open(file_path))
    
    def _process_file_open(self, file_path):
        start_time = time.time()
        success = self.log_processor.open_file(file_path)
        
        if success:
            self.current_file = file_path
            self.current_display_start = 0
            self.update_log_display()
            self.results_list.clear()
            self.search_results = []
            
            elapsed = time.time() - start_time
            self.status_bar.showMessage(f"File loaded: {os.path.basename(file_path)} ({self.log_processor.total_lines} lines) in {elapsed:.2f} seconds")
        else:
            self.status_bar.showMessage(f"Failed to open file: {file_path}")
            QMessageBox.critical(self, "Error", f"Failed to open file: {file_path}")
        
        self.progress_bar.setVisible(False)
    
    def search_logs(self):
        search_text = self.search_input.text()
        if not search_text or not self.current_file:
            return
        
        self.status_bar.showMessage(f"Searching for: {search_text}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start search in a separate thread
        self.search_thread = SearchThread(
            self.log_processor, 
            search_text, 
            self.case_sensitive_checkbox.isChecked()
        )
        self.search_thread.search_complete.connect(self.handle_search_results)
        self.search_thread.progress_update.connect(self.progress_bar.setValue)
        self.search_thread.start()
    
    def handle_search_results(self, results):
        self.search_results = results
        self.results_list.clear()
        
        for line_num, line_text in results:
            # Truncate long lines for display
            display_text = line_text[:100] + "..." if len(line_text) > 100 else line_text
            item = QListWidgetItem(f"Line {line_num + 1}: {display_text}")
            item.setData(Qt.UserRole, line_num)
            self.results_list.addItem(item)
        
        self.status_bar.showMessage(f"Found {len(results)} matches")
        self.progress_bar.setVisible(False)
    
    def show_selected_result(self, item):
        line_num = item.data(Qt.UserRole)
        self.highlight_line(line_num)
    
    def highlight_line(self, line_num):
        # Calculate which page contains this line
        page = line_num // self.lines_per_page
        self.current_display_start = page * self.lines_per_page
        
        # Update display
        self.update_log_display()
        
        # Highlight the specific line
        cursor = self.log_display.textCursor()
        cursor.setPosition(0)
        
        # Find the position of the target line in the displayed text
        line_offset = line_num - self.current_display_start
        for _ in range(line_offset):
            cursor.movePosition(QTextCursor.NextBlock)
        
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        self.log_display.setTextCursor(cursor)
        self.log_display.ensureCursorVisible()
    
    def update_log_display(self):
        if not self.current_file:
            return
        
        end_line = min(self.current_display_start + self.lines_per_page, self.log_processor.total_lines)
        lines = self.log_processor.get_lines(self.current_display_start, end_line)
        
        self.log_display.clear()
        self.log_display.setPlainText(''.join(lines))
        
        # Update page info
        total_pages = (self.log_processor.total_lines + self.lines_per_page - 1) // self.lines_per_page
        current_page = self.current_display_start // self.lines_per_page + 1
        self.page_info_label.setText(f"Page: {current_page}/{total_pages}")
        
        # Enable/disable navigation buttons
        self.prev_button.setEnabled(self.current_display_start > 0)
        self.next_button.setEnabled(end_line < self.log_processor.total_lines)
    
    def show_previous_page(self):
        if self.current_display_start > 0:
            self.current_display_start = max(0, self.current_display_start - self.lines_per_page)
            self.update_log_display()
    
    def show_next_page(self):
        if self.current_display_start + self.lines_per_page < self.log_processor.total_lines:
            self.current_display_start += self.lines_per_page
            self.update_log_display()
    
    def show_context_menu(self, position):
        item = self.results_list.itemAt(position)
        if not item:
            return
        
        context_menu = QMenu()
        copy_action = QAction("Copy Line", self)
        copy_action.triggered.connect(lambda: self.copy_result_line(item))
        context_menu.addAction(copy_action)
        
        context_menu.exec_(self.results_list.mapToGlobal(position))
    
    def copy_result_line(self, item):
        line_num = item.data(Qt.UserRole)
        line_text = self.log_processor.get_line(line_num)
        QApplication.clipboard().setText(line_text)
        self.status_bar.showMessage("Line copied to clipboard", 2000)
    
    def closeEvent(self, event):
        self.log_processor.close()
        event.accept()
