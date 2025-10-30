"""
Cache Management for Invoice Cataloger
Handles duplicate detection and processed file tracking
"""
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime


class CacheManager:
    """Manages cache for processed invoices"""
    
    def __init__(self, cache_path: Path):
        self.cache_path = Path(cache_path)
        self.cache: List[Dict[str, Any]] = []
        self.load()
    
    def load(self):
        """Load cache from file"""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cache: {e}")
                self.cache = []
        else:
            self.cache = []
    
    def save(self):
        """Save cache to file"""
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def find_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Find cached entry by file hash"""
        for entry in self.cache:
            if entry.get('FileHash') == file_hash:
                return entry
        return None
    
    def add_entry(self, file_name: str, file_hash: str, extracted_data: Dict[str, Any],
                  category: str, deduction: Dict[str, Any]):
        """Add new entry to cache"""
        entry = {
            'FileName': file_name,
            'FileHash': file_hash,
            'ProcessedDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ExtractedData': extracted_data,
            'Category': category,
            'Deduction': deduction
        }
        self.cache.append(entry)
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'unique_vendors': len(set(
                entry.get('ExtractedData', {}).get('vendor_name', 'Unknown')
                for entry in self.cache
            ))
        }
    
    @staticmethod
    def calculate_file_hash(file_path: Path) -> Optional[str]:
        """Calculate MD5 hash of file"""
        try:
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            return md5_hash.hexdigest()
        except Exception as e:
            print(f"Error calculating hash: {e}")
            return None


class FailedFilesManager:
    """Manages tracking of failed file processing attempts"""
    
    def __init__(self, failed_files_path: Path):
        self.failed_files_path = Path(failed_files_path)
        self.failed_files: List[Dict[str, Any]] = []
        self.load()
    
    def load(self):
        """Load failed files list from file"""
        if self.failed_files_path.exists():
            try:
                with open(self.failed_files_path, 'r', encoding='utf-8') as f:
                    self.failed_files = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load failed files: {e}")
                self.failed_files = []
        else:
            self.failed_files = []
    
    def save(self):
        """Save failed files list to file"""
        try:
            self.failed_files_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.failed_files_path, 'w', encoding='utf-8') as f:
                json.dump(self.failed_files, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving failed files: {e}")
    
    def find_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Find failed file entry by path"""
        for entry in self.failed_files:
            if entry.get('FilePath') == file_path:
                return entry
        return None
    
    def add_failure(self, file_path: str, file_name: str, error_reason: str, attempt_count: int = 1):
        """Add or update failed file entry"""
        existing = self.find_by_path(file_path)
        
        if existing:
            existing['AttemptCount'] = attempt_count
            existing['LastAttempt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            existing['ErrorReason'] = error_reason
        else:
            entry = {
                'FilePath': file_path,
                'FileName': file_name,
                'ErrorReason': error_reason,
                'AttemptCount': attempt_count,
                'FirstAttempt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'LastAttempt': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.failed_files.append(entry)
    
    def remove_failure(self, file_path: str):
        """Remove file from failed list (successful retry)"""
        self.failed_files = [
            entry for entry in self.failed_files
            if entry.get('FilePath') != file_path
        ]
    
    def get_retry_candidates(self, max_attempts: int) -> List[Dict[str, Any]]:
        """Get files that can be retried (haven't exceeded max attempts)"""
        return [
            entry for entry in self.failed_files
            if entry.get('AttemptCount', 0) < max_attempts
        ]
    
    def get_stats(self) -> Dict[str, int]:
        """Get failed files statistics"""
        return {
            'total_failed': len(self.failed_files),
            'retry_candidates': len(self.get_retry_candidates(3)),
            'max_attempts_exceeded': len([
                entry for entry in self.failed_files
                if entry.get('AttemptCount', 0) >= 3
            ])
        }
