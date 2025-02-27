import os
import re
import mmap
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

class LogProcessor:
    def __init__(self):
        self.current_file = None
        self.file_map = None
        self.file_size = 0
        self.line_offsets = []
        self.total_lines = 0

    def open_file(self, file_path: str) -> bool:
        """Open a log file and prepare it for processing."""
        try:
            if self.file_map:
                self.file_map.close()
            
            self.current_file = open(file_path, 'rb')
            self.file_size = os.path.getsize(file_path)
            
            if self.file_size > 0:
                self.file_map = mmap.mmap(self.current_file.fileno(), 0, access=mmap.ACCESS_READ)
                self._index_lines()
                return True
            else:
                self.current_file.close()
                self.current_file = None
                return False
        except Exception as e:
            if self.current_file:
                self.current_file.close()
                self.current_file = None
            print(f"Error opening file: {e}")
            return False

    def _index_lines(self) -> None:
        """Create an index of line positions for fast access."""
        self.line_offsets = [0]
        self.file_map.seek(0)
        
        pos = self.file_map.find(b'\n')
        while pos != -1:
            self.line_offsets.append(pos + 1)  # Position after newline
            pos = self.file_map.find(b'\n', pos + 1)
        
        self.total_lines = len(self.line_offsets)

    def get_line(self, line_number: int) -> str:
        """Get a specific line by line number."""
        if not self.file_map or line_number < 0 or line_number >= self.total_lines:
            return ""
        
        start = self.line_offsets[line_number]
        end = self.file_size if line_number == self.total_lines - 1 else self.line_offsets[line_number + 1] - 1
        
        self.file_map.seek(start)
        line_bytes = self.file_map.read(end - start)
        return line_bytes.decode('utf-8', errors='replace')

    def get_lines(self, start_line: int, end_line: int) -> List[str]:
        """Get a range of lines."""
        if not self.file_map:
            return []
        
        start_line = max(0, start_line)
        end_line = min(self.total_lines, end_line)
        
        return [self.get_line(i) for i in range(start_line, end_line)]

    def search(self, pattern: str, case_sensitive: bool = False) -> List[Tuple[int, str]]:
        """Search for a pattern in the log file."""
        if not self.file_map or not pattern:
            return []
        
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            compiled_pattern = re.compile(pattern.encode('utf-8'), flags)
        except re.error:
            # If regex fails, search as plain text
            escaped = re.escape(pattern).encode('utf-8')
            compiled_pattern = re.compile(escaped, flags)
        
        results = []
        
        # Use multiple threads for searching large files
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            chunk_size = max(1, self.total_lines // os.cpu_count())
            futures = []
            
            for i in range(0, self.total_lines, chunk_size):
                end = min(i + chunk_size, self.total_lines)
                futures.append(executor.submit(self._search_chunk, i, end, compiled_pattern))
            
            for future in futures:
                results.extend(future.result())
        
        return results

    def _search_chunk(self, start_line: int, end_line: int, pattern) -> List[Tuple[int, str]]:
        """Search a chunk of the file for the pattern."""
        results = []
        for i in range(start_line, end_line):
            line = self.get_line(i)
            if pattern.search(line.encode('utf-8')):
                results.append((i, line))
        return results

    def filter_by_time(self, start_time: str, end_time: str, time_format: str) -> List[Tuple[int, str]]:
        """Filter logs by time range."""
        # This is a placeholder for time-based filtering
        # In a real implementation, you would parse the time from each log line
        # and compare it with the start_time and end_time
        return []

    def close(self) -> None:
        """Close the current file."""
        if self.file_map:
            self.file_map.close()
            self.file_map = None
        if self.current_file:
            self.current_file.close()
            self.current_file = None
        self.line_offsets = []
        self.total_lines = 0
