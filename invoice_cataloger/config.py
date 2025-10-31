"""
Configuration Management for Invoice Cataloger
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Main configuration class for Invoice Cataloger"""
    
    # API Provider Configuration
    api_provider: str = field(default_factory=lambda: os.getenv("API_PROVIDER", "lmstudio"))
    
    # LM Studio Configuration
    lm_studio_endpoint: str = field(default_factory=lambda: os.getenv("LM_STUDIO_ENDPOINT", "http://192.168.0.100:1234/v1/chat/completions"))
    lm_studio_models_endpoint: str = field(default_factory=lambda: os.getenv("LM_STUDIO_MODELS_ENDPOINT", "http://192.168.0.100:1234/v1/models"))
    lm_studio_model: str = field(default_factory=lambda: os.getenv("LM_STUDIO_MODEL", "local-model"))
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"))
    openai_api_base: str = field(default_factory=lambda: os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"))
    
    # OpenRouter Configuration
    openrouter_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY"))
    openrouter_model: str = field(default_factory=lambda: os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"))
    openrouter_api_base: str = field(default_factory=lambda: os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1"))
    openrouter_app_name: str = field(default_factory=lambda: os.getenv("OPENROUTER_APP_NAME", "Invoice-Cataloger"))
    
    # Custom Prompt Configuration
    use_custom_prompt: bool = field(default_factory=lambda: os.getenv("USE_CUSTOM_PROMPT", "false").lower() == "true")
    custom_extraction_prompt: Optional[str] = field(default_factory=lambda: os.getenv("CUSTOM_EXTRACTION_PROMPT"))
    
    # Paths (dynamic based on financial year)
    base_path: Path = Path("G:/My Drive/Tax Invoices")
    financial_year: str = field(default_factory=lambda: os.getenv("FINANCIAL_YEAR", "2024-2025"))
    
    # File Types to Process
    file_extensions: List[str] = field(default_factory=lambda: [
        '.pdf', '.png', '.jpg', '.jpeg', '.gif',
        '.doc', '.docx', '.xls', '.xlsx',
        '.eml', '.msg'
    ])
    
    # ATO Configuration - Software Developer, 3 days WFH
    work_from_home_days: int = field(default_factory=lambda: int(os.getenv("WORK_FROM_HOME_DAYS", "3")))
    total_work_days: int = field(default_factory=lambda: int(os.getenv("TOTAL_WORK_DAYS", "5")))
    work_use_percentage: int = field(default_factory=lambda: int(os.getenv("WORK_FROM_HOME_DAYS", "3")) * 100 // int(os.getenv("TOTAL_WORK_DAYS", "5")))
    fixed_rate_hourly: float = field(default_factory=lambda: float(os.getenv("FIXED_RATE_HOURLY", "0.70")))
    occupation: str = field(default_factory=lambda: os.getenv("OCCUPATION", "Web / Software Developer"))
    
    # LLM Parameters
    temperature: float = field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.1")))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "3000")))
    timeout_seconds: int = field(default_factory=lambda: int(os.getenv("LLM_TIMEOUT_SECONDS", "120")))
    retry_attempts: int = field(default_factory=lambda: int(os.getenv("LLM_RETRY_ATTEMPTS", "3")))
    retry_delay_seconds: int = field(default_factory=lambda: int(os.getenv("LLM_RETRY_DELAY_SECONDS", "2")))
    
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
    
    @property
    def vendor_overrides_path(self) -> Path:
        """Get vendor overrides configuration path"""
        # Look for vendor_overrides.json in the invoice_cataloger directory
        script_dir = Path(__file__).parent
        return script_dir / "vendor_overrides.json"
    
    def load_vendor_overrides(self) -> dict:
        """Load vendor override configuration"""
        try:
            if self.vendor_overrides_path.exists():
                with open(self.vendor_overrides_path, 'r') as f:
                    data = json.load(f)
                    # Filter only enabled overrides
                    enabled_overrides = [
                        override for override in data.get('overrides', [])
                        if override.get('enabled', True)
                    ]
                    return {
                        'overrides': enabled_overrides,
                        'available_categories': data.get('available_categories', [])
                    }
            return {'overrides': [], 'available_categories': []}
        except Exception as e:
            print(f"Warning: Could not load vendor overrides: {e}")
            return {'overrides': [], 'available_categories': []}
    
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
    
    def validate_api_config(self) -> tuple[bool, str]:
        """Validate API configuration based on selected provider"""
        provider = self.api_provider.lower()
        
        if provider == "openai":
            if not self.openai_api_key:
                return False, "OpenAI API key is required. Set OPENAI_API_KEY in .env file"
            if not self.openai_model:
                return False, "OpenAI model is required. Set OPENAI_MODEL in .env file"
            return True, f"OpenAI configured with model: {self.openai_model}"
        
        elif provider == "openrouter":
            if not self.openrouter_api_key:
                return False, "OpenRouter API key is required. Set OPENROUTER_API_KEY in .env file"
            if not self.openrouter_model:
                return False, "OpenRouter model is required. Set OPENROUTER_MODEL in .env file"
            return True, f"OpenRouter configured with model: {self.openrouter_model}"
        
        elif provider == "lmstudio":
            if not self.lm_studio_endpoint:
                return False, "LM Studio endpoint is required. Set LM_STUDIO_ENDPOINT in .env file"
            return True, f"LM Studio configured at: {self.lm_studio_endpoint}"
        
        else:
            return False, f"Invalid API provider: {provider}. Must be 'lmstudio', 'openai', or 'openrouter'"
    
    def to_dict(self) -> dict:
        """Convert config to dictionary"""
        return {
            'api_provider': self.api_provider,
            'lm_studio_endpoint': self.lm_studio_endpoint,
            'openai_model': self.openai_model if self.api_provider == 'openai' else 'N/A',
            'openrouter_model': self.openrouter_model if self.api_provider == 'openrouter' else 'N/A',
            'financial_year': self.financial_year,
            'work_use_percentage': self.work_use_percentage,
            'occupation': self.occupation,
            'invoice_folder': str(self.invoice_folder),
            'output_folder': str(self.output_folder),
            'use_custom_prompt': self.use_custom_prompt,
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
