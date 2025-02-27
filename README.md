# LogExplorer

LogExplorer is a high-performance GUI application for viewing, searching, and analyzing log files. It provides a fast and intuitive interface for working with large log files, with search capabilities comparable to grep but with a user-friendly interface.

## Features

- **Fast Log File Loading**: Efficiently handles large log files using memory mapping
- **High-Performance Search**: Search through logs with grep-like speed using multi-threading
- **Intuitive UI**: Easy-to-use interface with search results and log content views
- **Navigation**: Quickly navigate through large log files with pagination
- **Case-Sensitive Search**: Option to perform case-sensitive or case-insensitive searches
- **Keyboard Shortcuts**: Convenient keyboard shortcuts for common operations

## Installation

### Prerequisites

- Python 3.6 or higher
- PyQt5

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/logexplorer.git
   cd logexplorer
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Starting the Application

Run the application with:

```
python -m src.main
```

### Opening Log Files

1. Click the "Browse" button or use Ctrl+O to open a file dialog
2. Select your log file
3. The file will be loaded and displayed in the main view

### Searching Logs

1. Enter your search pattern in the search box
2. Toggle "Case Sensitive" if needed
3. Press Enter or click the "Search" button
4. Results will appear in the results list
5. Click on any result to jump to that line in the log

### Navigating Through Logs

- Use the "Previous Page" and "Next Page" buttons to navigate through large files
- The current page and total pages are displayed between the navigation buttons

### Keyboard Shortcuts

- **Ctrl+O**: Open file
- **Ctrl+F**: Focus search box
- **Enter** (in search box): Perform search

## Performance

LogExplorer is designed for high performance:

- Uses memory mapping for efficient file access
- Implements multi-threaded search for large files
- Indexes line positions for fast navigation
- Loads and displays logs in chunks to maintain responsiveness

## Development

### Project Structure

```
logexplorer/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── log_processor.py
│   └── ui/
│       ├── __init__.py
│       └── main_window.py
├── tests/
│   ├── __init__.py
│   ├── test_log_processor.py
│   └── test_ui.py
└── requirements.txt
```

### Running Tests

Run the test suite with:

```
python -m unittest discover tests
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
