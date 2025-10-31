"""
WFH Parser - Parse Work From Home logs from CSV or JSON files

Supports:
- CSV format: Date, Location, WorkFromHome, Notes
- JSON format: {financial_year, entries: [{date, location, wfh, notes}]}
"""
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import from parent modules
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils import get_logger


class WFHParser:
    """
    Parse WFH logs from CSV or JSON files
    
    Supports filtering by date range and financial year.
    """
    
    def __init__(self):
        self.logger = get_logger()
    
    def parse(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse WFH log file (auto-detect format)
        
        Args:
            file_path: Path to WFH log file
        
        Returns:
            List of WFH entries
        """
        if not file_path.exists():
            self.logger.error(f"WFH log file not found: {file_path}")
            return []
        
        # Detect format by extension
        ext = file_path.suffix.lower()
        
        if ext == '.csv':
            return self.parse_csv(file_path)
        elif ext == '.json':
            return self.parse_json(file_path)
        else:
            self.logger.error(f"Unsupported WFH log format: {ext}")
            return []
    
    def parse_csv(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse CSV format WFH log
        
        Expected columns: Date, Location, WorkFromHome, Notes
        
        Args:
            file_path: Path to CSV file
        
        Returns:
            List of WFH entries
        """
        entries = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        # Validate required fields
                        if 'Date' not in row or 'WorkFromHome' not in row:
                            self.logger.warning(f"Row {row_num}: Missing required fields (Date, WorkFromHome)")
                            continue
                        
                        # Parse date
                        date_str = row['Date'].strip()
                        if not date_str:
                            self.logger.warning(f"Row {row_num}: Empty date field")
                            continue
                        
                        # Validate date format
                        try:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        except ValueError:
                            self.logger.warning(f"Row {row_num}: Invalid date format '{date_str}' (expected YYYY-MM-DD)")
                            continue
                        
                        # Parse WFH field (support Yes/No, True/False, 1/0)
                        wfh_str = row['WorkFromHome'].strip().lower()
                        wfh = wfh_str in ['yes', 'true', '1', 'y']
                        
                        # Create entry
                        entry = {
                            'date': date_str,
                            'date_obj': date_obj,
                            'location': row.get('Location', '').strip(),
                            'wfh': wfh,
                            'notes': row.get('Notes', '').strip()
                        }
                        
                        entries.append(entry)
                    
                    except Exception as e:
                        self.logger.warning(f"Row {row_num}: Error parsing row - {e}")
                        continue
            
            self.logger.info(f"Parsed {len(entries)} entries from CSV: {file_path.name}")
            return entries
        
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {e}")
            return []
    
    def parse_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse JSON format WFH log
        
        Expected format:
        {
            "financial_year": "2024-2025",
            "entries": [
                {"date": "2024-07-01", "location": "Home", "wfh": true, "notes": "..."}
            ]
        }
        
        Args:
            file_path: Path to JSON file
        
        Returns:
            List of WFH entries
        """
        entries = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate structure
            if not isinstance(data, dict):
                self.logger.error("Invalid JSON structure: Expected object at root")
                return []
            
            if 'entries' not in data:
                self.logger.error("Invalid JSON structure: Missing 'entries' field")
                return []
            
            if not isinstance(data['entries'], list):
                self.logger.error("Invalid JSON structure: 'entries' must be an array")
                return []
            
            # Parse entries
            for idx, entry_data in enumerate(data['entries'], start=1):
                try:
                    # Validate required fields
                    if 'date' not in entry_data or 'wfh' not in entry_data:
                        self.logger.warning(f"Entry {idx}: Missing required fields (date, wfh)")
                        continue
                    
                    # Parse date
                    date_str = entry_data['date'].strip()
                    if not date_str:
                        self.logger.warning(f"Entry {idx}: Empty date field")
                        continue
                    
                    # Validate date format
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    except ValueError:
                        self.logger.warning(f"Entry {idx}: Invalid date format '{date_str}' (expected YYYY-MM-DD)")
                        continue
                    
                    # Parse WFH field (support boolean or string)
                    wfh_value = entry_data['wfh']
                    if isinstance(wfh_value, bool):
                        wfh = wfh_value
                    elif isinstance(wfh_value, str):
                        wfh = wfh_value.strip().lower() in ['yes', 'true', '1', 'y']
                    else:
                        wfh = bool(wfh_value)
                    
                    # Create entry
                    entry = {
                        'date': date_str,
                        'date_obj': date_obj,
                        'location': entry_data.get('location', '').strip(),
                        'wfh': wfh,
                        'notes': entry_data.get('notes', '').strip()
                    }
                    
                    entries.append(entry)
                
                except Exception as e:
                    self.logger.warning(f"Entry {idx}: Error parsing entry - {e}")
                    continue
            
            self.logger.info(f"Parsed {len(entries)} entries from JSON: {file_path.name}")
            
            # Log financial year if present
            if 'financial_year' in data:
                self.logger.info(f"Financial year: {data['financial_year']}")
            
            return entries
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON file: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error reading JSON file: {e}")
            return []
    
    def validate_log(self, log_data: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
        """
        Validate WFH log data
        
        Args:
            log_data: List of WFH entries
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not log_data:
            errors.append("No entries found in log")
            return False, errors
        
        # Check for required fields
        for idx, entry in enumerate(log_data, start=1):
            if 'date' not in entry:
                errors.append(f"Entry {idx}: Missing 'date' field")
            if 'wfh' not in entry:
                errors.append(f"Entry {idx}: Missing 'wfh' field")
            if 'date_obj' not in entry:
                errors.append(f"Entry {idx}: Missing 'date_obj' field")
        
        # Check for duplicate dates
        dates = [entry['date'] for entry in log_data if 'date' in entry]
        duplicates = [date for date in dates if dates.count(date) > 1]
        if duplicates:
            unique_duplicates = list(set(duplicates))
            errors.append(f"Duplicate dates found: {', '.join(unique_duplicates)}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def filter_by_date_range(self, log_data: List[Dict[str, Any]], 
                            start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Filter log entries by date range
        
        Args:
            log_data: List of WFH entries
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            Filtered list of entries
        """
        try:
            start_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_obj = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError as e:
            self.logger.error(f"Invalid date format: {e}")
            return log_data
        
        filtered = [
            entry for entry in log_data
            if 'date_obj' in entry and start_obj <= entry['date_obj'] <= end_obj
        ]
        
        self.logger.info(f"Filtered to {len(filtered)} entries between {start_date} and {end_date}")
        return filtered
    
    def filter_by_financial_year(self, log_data: List[Dict[str, Any]], 
                                 financial_year: str) -> List[Dict[str, Any]]:
        """
        Filter log entries by Australian financial year (July 1 - June 30)
        
        Args:
            log_data: List of WFH entries
            financial_year: Financial year in format YYYY-YYYY (e.g., "2024-2025")
        
        Returns:
            Filtered list of entries
        """
        try:
            # Parse financial year
            years = financial_year.split('-')
            if len(years) != 2:
                self.logger.error(f"Invalid financial year format: {financial_year}")
                return log_data
            
            start_year = int(years[0])
            end_year = int(years[1])
            
            if end_year != start_year + 1:
                self.logger.error(f"Invalid financial year: {financial_year}")
                return log_data
            
            # Australian financial year: July 1 to June 30
            start_date = f"{start_year}-07-01"
            end_date = f"{end_year}-06-30"
            
            self.logger.info(f"Filtering for FY{financial_year}: {start_date} to {end_date}")
            
            return self.filter_by_date_range(log_data, start_date, end_date)
        
        except Exception as e:
            self.logger.error(f"Error filtering by financial year: {e}")
            return log_data
