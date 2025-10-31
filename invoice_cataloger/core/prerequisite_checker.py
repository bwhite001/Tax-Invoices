"""
Prerequisite Checker - Validates system requirements and configuration

Separated from main cataloger for single responsibility.
"""
from pathlib import Path
from typing import Tuple

from config import Config
from utils import get_logger
from extractors import PDFExtractor
from processors import LLMProcessor


class PrerequisiteChecker:
    """Check if all prerequisites are met before processing"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger()
    
    def check_all(self) -> bool:
        """
        Check all prerequisites
        
        Returns:
            True if all checks pass, False otherwise
        """
        self.logger.section("CHECKING PREREQUISITES")
        self.logger.info(f"Processing Financial Year: FY{self.config.financial_year}")
        self.logger.info(f"API Provider: {self.config.api_provider.upper()}")
        
        # Run all checks
        checks = [
            self._check_financial_year(),
            self._check_invoice_folder(),
            self._check_output_folders(),
            self._check_api_config(),
            self._check_api_connection(),
            self._check_extraction_dependencies()
        ]
        
        return all(checks)
    
    def _check_financial_year(self) -> bool:
        """Validate financial year format"""
        if not self.config.validate_financial_year():
            self.logger.error(f"Invalid financial year format: {self.config.financial_year}")
            self.logger.error("Use format: YYYY-YYYY (e.g., '2024-2025')")
            return False
        return True
    
    def _check_invoice_folder(self) -> bool:
        """Check if invoice folder exists"""
        if not self.config.invoice_folder.exists():
            self.logger.error(f"Invoice folder not found: {self.config.invoice_folder}")
            self.logger.error("Please create the folder and add invoice files.")
            return False
        
        self.logger.success(f"Invoice folder exists: {self.config.invoice_folder}")
        return True
    
    def _check_output_folders(self) -> bool:
        """Create output folders if they don't exist"""
        try:
            self.config.ensure_directories()
            self.logger.success(f"Output folder ready: {self.config.output_folder}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create output folders: {e}")
            return False
    
    def _check_api_config(self) -> bool:
        """Validate API configuration"""
        api_valid, api_message = self.config.validate_api_config()
        if not api_valid:
            self.logger.error(api_message)
            self.logger.error("Please check your .env file configuration")
            return False
        
        self.logger.success(api_message)
        return True
    
    def _check_api_connection(self) -> bool:
        """Test API connection based on provider"""
        self.logger.info(f"Testing {self.config.api_provider.upper()} connection...")
        
        provider = self.config.api_provider
        
        if provider == "lmstudio":
            return self._test_lmstudio_connection()
        elif provider == "openai":
            return self._test_openai_connection()
        elif provider == "openrouter":
            return self._test_openrouter_connection()
        else:
            self.logger.error(f"Unknown API provider: {provider}")
            return False
    
    def _test_lmstudio_connection(self) -> bool:
        """Test LM Studio connection"""
        success, message = LLMProcessor.test_connection(
            "lmstudio",
            endpoint=self.config.lm_studio_endpoint,
            models_endpoint=self.config.lm_studio_models_endpoint
        )
        
        if not success:
            self.logger.error(message)
            self.logger.error("Please ensure:")
            self.logger.error("  1. LM Studio is running")
            self.logger.error("  2. A model is loaded (e.g., Mistral 7B)")
            self.logger.error("  3. Developer Server is started")
            return False
        
        self.logger.success(message)
        return True
    
    def _test_openai_connection(self) -> bool:
        """Test OpenAI connection"""
        success, message = LLMProcessor.test_connection(
            "openai",
            api_key=self.config.openai_api_key,
            model=self.config.openai_model,
            api_base=self.config.openai_api_base
        )
        
        if not success:
            self.logger.error(message)
            self.logger.error("Please ensure:")
            self.logger.error("  1. OPENAI_API_KEY is set in .env file")
            self.logger.error("  2. API key is valid and has credits")
            self.logger.error("  3. Model name is correct")
            return False
        
        self.logger.success(message)
        return True
    
    def _test_openrouter_connection(self) -> bool:
        """Test OpenRouter connection"""
        success, message = LLMProcessor.test_connection(
            "openrouter",
            api_key=self.config.openrouter_api_key,
            model=self.config.openrouter_model,
            api_base=self.config.openrouter_api_base,
            app_name=self.config.openrouter_app_name
        )
        
        if not success:
            self.logger.error(message)
            self.logger.error("Please ensure:")
            self.logger.error("  1. OPENROUTER_API_KEY is set in .env file")
            self.logger.error("  2. API key is valid and has credits")
            self.logger.error("  3. Model name is correct")
            return False
        
        self.logger.success(message)
        return True
    
    def _check_extraction_dependencies(self) -> bool:
        """Check extraction dependencies and show available methods"""
        # Show custom prompt status
        if self.config.use_custom_prompt:
            self.logger.info("Using custom extraction prompt")
        else:
            self.logger.info("Using default optimized extraction prompt")
        
        # Check PDF dependencies
        pdf_ok, pdf_missing = PDFExtractor.check_dependencies()
        if not pdf_ok:
            self.logger.warning("Missing PDF dependencies:")
            for dep in pdf_missing:
                self.logger.warning(f"  - {dep}")
        
        # Show available extraction methods
        self.logger.info("\nAvailable extraction methods:")
        pdf_methods = PDFExtractor.get_available_methods()
        for method, available in pdf_methods.items():
            status = "✓" if available else "✗"
            self.logger.info(f"  {status} {method}")
        
        return True  # Non-critical, so always return True
