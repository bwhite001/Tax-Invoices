"""
Configuration Module

Centralized configuration management following DRY principles.
Single Responsibility: Manage all configuration parameters.
"""

from pathlib import Path
from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass
class FilePaths:
    """File path configuration - Single Responsibility Principle"""
    wfh_log: Path
    invoice_catalog: Path
    deduction_summary: Path
    bank_statements: Path
    output_dir: Path

    @classmethod
    def for_financial_year(cls, fy: str, base_dir: Path = None) -> 'FilePaths':
        """
        Create file paths for any financial year (DRY - reusable)
        
        Args:
            fy: Financial year (e.g., "2024-2025")
            base_dir: Base directory path
        """
        if base_dir is None:
            base_dir = Path.cwd()
        
        fy_dir = base_dir / f"FY{fy}"
        
        return cls(
            wfh_log=base_dir / "wfh" / f"wfh_{fy.replace('-', '_')}.csv",
            invoice_catalog=fy_dir / "Processed" / "Invoice_Catalog_20251031_193538.csv",
            deduction_summary=fy_dir / "Processed" / "Deduction_Summary_20251031_193538.csv",
            bank_statements=fy_dir / "Processed" / "BankStatements" / "ZipMoney_20251031_201436" / "expense_catalog.csv",
            output_dir=fy_dir / "Processed"
        )


@dataclass
class TaxParameters:
    """Tax calculation parameters - Single Responsibility Principle"""
    financial_year: str
    fy_start_date: str
    fy_end_date: str
    wfh_categories: List[str]
    exclude_locations: List[str]
    default_wfh_percentage: float

    @classmethod
    def for_australian_fy(cls, start_year: int) -> 'TaxParameters':
        """
        Create Australian tax parameters for any FY (DRY - reusable)
        
        Args:
            start_year: Starting year of FY (e.g., 2024 for FY2024-2025)
        """
        end_year = start_year + 1
        
        return cls(
            financial_year=f"{start_year}-{end_year}",
            fy_start_date=f"{start_year}-07-01",
            fy_end_date=f"{end_year}-06-30",
            wfh_categories=[
                'Electricity',
                'Internet',
                'Phone & Mobile',
                'Office Supplies',
                'Software & Subscriptions',
                'Computer Equipment',
                'Communication Tools'
            ],
            exclude_locations=['Leave'],
            default_wfh_percentage=60.0
        )


@dataclass
class ReportConfig:
    """Report generation configuration - Single Responsibility Principle"""
    timestamp_format: str
    currency_format: str
    percentage_format: str
    date_format: str
    excel_header_color: str
    excel_header_font_color: str

    @classmethod
    def default(cls) -> 'ReportConfig':
        """Default report configuration"""
        return cls(
            timestamp_format="%Y%m%d_%H%M%S",
            currency_format="$#,##0.00",
            percentage_format="0.00%",
            date_format="%Y-%m-%d",
            excel_header_color="366092",
            excel_header_font_color="FFFFFF"
        )


class Config:
    """
    Main configuration class - Facade Pattern
    
    Provides unified interface to all configuration components.
    """

    def __init__(self, financial_year: str = "2024-2025", base_dir: Path = None):
        """
        Initialize configuration
        
        Args:
            financial_year: Financial year (e.g., "2024-2025")
            base_dir: Base directory path
        """
        self.base_dir = base_dir or Path.cwd()
        self.financial_year = financial_year
        
        # Extract start year from financial year string
        start_year = int(financial_year.split('-')[0])
        
        # Initialize components
        self.file_paths = FilePaths.for_financial_year(financial_year, self.base_dir)
        self.tax_params = TaxParameters.for_australian_fy(start_year)
        self.report_config = ReportConfig.default()

    def validate_paths(self) -> dict:
        """
        Validate that all required files exist
        
        Returns:
            Dictionary with validation results
        """
        validation = {
            'all_valid': True,
            'required': {},
            'optional': {},
            'missing_required': [],
            'missing_optional': []
        }

        # Check required files
        required_files = {
            'wfh_log': self.file_paths.wfh_log,
            'invoice_catalog': self.file_paths.invoice_catalog
        }

        for name, path in required_files.items():
            exists = path.exists()
            validation['required'][name] = exists
            if not exists:
                validation['all_valid'] = False
                validation['missing_required'].append(str(path))

        # Check optional files
        optional_files = {
            'deduction_summary': self.file_paths.deduction_summary,
            'bank_statements': self.file_paths.bank_statements
        }

        for name, path in optional_files.items():
            exists = path.exists()
            validation['optional'][name] = exists
            if not exists:
                validation['missing_optional'].append(str(path))

        return validation

    def get_output_filename(self, prefix: str = "Tax_Report") -> str:
        """
        Generate timestamped output filename
        
        Args:
            prefix: Filename prefix
            
        Returns:
            Formatted filename with timestamp
        """
        timestamp = datetime.now().strftime(self.report_config.timestamp_format)
        return f"{prefix}_{self.financial_year}_{timestamp}.xlsx"

    def get_output_path(self, prefix: str = "Tax_Report") -> Path:
        """
        Get full output file path
        
        Args:
            prefix: Filename prefix
            
        Returns:
            Full path to output file
        """
        filename = self.get_output_filename(prefix)
        return self.file_paths.output_dir / filename

    def __repr__(self) -> str:
        """String representation"""
        return f"Config(financial_year='{self.financial_year}', base_dir='{self.base_dir}')"
