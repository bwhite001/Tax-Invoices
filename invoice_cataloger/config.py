"""
Configuration Management for Invoice Cataloger
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List
import json


@dataclass
class Config:
    """Main configuration class for Invoice Cataloger"""
    
    # LM Studio Configuration
    lm_studio_endpoint: str = "http://192.168.0.100:1234/v1/chat/completions"
    lm_studio_models_endpoint: str = "http://192.168.0.100:1234/v1/models"
    lm_studio_model: str = "local-model"
    
    # Paths (dynamic based on financial year)
    base_path: Path = Path("G:/My Drive/Tax Invoices")
    financial_year: str = "2024-2025"
    
    # File Types to Process
    file_extensions: List[str] = field(default_factory=lambda: [
        '.pdf', '.png', '.jpg', '.jpeg', '.gif',
        '.doc', '.docx', '.xls', '.xlsx',
        '.eml', '.msg'
    ])
    
    # ATO Configuration - Software Developer, 3 days WFH
    work_from_home_days: int = 3
    total_work_days: int = 5
    work_use_percentage: int = 60  # 3/5 = 60%
    fixed_rate_hourly: float = 0.70  # 2024-25 ATO rate
    occupation: str = "Web / Software Developer"
    
    # LM Studio Parameters
    temperature: float = 0.1  # Low temperature for consistent extraction
    max_tokens: int = 3000
    timeout_seconds: int = 120
    retry_attempts: int = 3
    retry_delay_seconds: int = 2
    
    # OCR Configuration
    use_easyocr: bool = True
    use_tesseract: bool = True
    tesseract_path: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    ocr_languages: List[str] = field(default_factory=lambda: ['en'])
    
    # Processing Options
    parallel_processing: bool = False
    max_workers: int = 4
    delete_processed_files: bool = False  # Keep originals
    move_processed_files: bool = True  # Move to Processed folder
    max_retry_attempts: int = 3  # Maximum retry attempts for failed files
    
    # Logging
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    
    @property
    def invoice_folder(self) -> Path:
        """Get invoice folder path for current financial year"""
        return self.base_path / f"FY{self.financial_year}"
    
    @property
    def output_folder(self) -> Path:
        """Get output folder path"""
        return self.invoice_folder / "Processed"
    
    @property
    def log_folder(self) -> Path:
        """Get log folder path"""
        return self.output_folder / "Logs"
    
    @property
    def cache_path(self) -> Path:
        """Get cache file path"""
        return self.output_folder / "cache.json"
    
    @property
    def failed_files_path(self) -> Path:
        """Get failed files tracking path"""
        return self.output_folder / "failed_files.json"
    
    def validate_financial_year(self) -> bool:
        """Validate financial year format (YYYY-YYYY)"""
        if not self.financial_year or '-' not in self.financial_year:
            return False
        
        try:
            years = self.financial_year.split('-')
            if len(years) != 2:
                return False
            
            start_year = int(years[0])
            end_year = int(years[1])
            
            return end_year == start_year + 1
        except (ValueError, IndexError):
            return False
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.log_folder.mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> dict:
        """Convert config to dictionary"""
        return {
            'lm_studio_endpoint': self.lm_studio_endpoint,
            'financial_year': self.financial_year,
            'work_use_percentage': self.work_use_percentage,
            'occupation': self.occupation,
            'invoice_folder': str(self.invoice_folder),
            'output_folder': str(self.output_folder),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Config':
        """Create config from dictionary"""
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
    
    def save_to_file(self, filepath: Path):
        """Save configuration to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: Path) -> 'Config':
        """Load configuration from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


# Global config instance
config = Config()
