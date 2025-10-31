#!/usr/bin/env python3
"""
Standalone Tax Calculator CLI

Calculate tax deductions from an existing invoice catalog.
Supports dynamic work-use percentage from WFH logs.

Usage:
    python tax_calculator_cli.py --catalog catalog.csv --output tax_report.csv
    python tax_calculator_cli.py --catalog catalog.csv --wfh-log wfh_log.csv --output tax_report.csv
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

# Import modules
from tax import TaxCalculator, ATOStrategy
from catalog import CatalogLoader
from utils import setup_logger, get_logger


def main():
    """Main entry point for standalone tax calculator"""
    parser = argparse.ArgumentParser(
        description="Calculate tax deductions from invoice catalog",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with catalog
  python tax_calculator_cli.py --catalog catalog.csv --output tax_report.csv
  
  # With WFH log for dynamic work-use percentage
  python tax_calculator_cli.py --catalog catalog.csv --wfh-log wfh_log.csv --output tax_report.csv
  
  # With static work-use percentage
  python tax_calculator_cli.py --catalog catalog.csv --work-use-percentage 65 --output tax_report.csv
  
  # With financial year filtering
  python tax_calculator_cli.py --catalog catalog.csv --wfh-log wfh_log.csv --financial-year 2024-2025 --output tax_report.csv
  
  # Export to Excel
  python tax_calculator_cli.py --catalog catalog.csv --output tax_report.xlsx --format excel
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--catalog',
        type=str,
        required=True,
        help='Path to catalog file (CSV, Excel, or JSON)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--wfh-log',
        type=str,
        help='Path to WFH log file (CSV or JSON) for dynamic work-use percentage'
    )
    
    parser.add_argument(
        '--strategy',
        type=str,
        default='ato',
        choices=['ato', 'custom'],
        help='Tax calculation strategy (default: ato)'
    )
    
    parser.add_argument(
        '--work-use-percentage',
        type=float,
        help='Static work-use percentage (0-100). Overridden by --wfh-log if provided'
    )
    
    parser.add_argument(
        '--financial-year',
        type=str,
        help='Financial year for WFH log filtering (format: YYYY-YYYY, e.g., 2024-2025)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output path for tax report (default: tax_report.csv in current directory)'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        default='csv',
        choices=['csv', 'excel', 'json'],
        help='Output format (default: csv)'
    )
    
    parser.add_argument(
        '--show-wfh-report',
        action='store_true',
        help='Display WFH statistics report'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose (DEBUG) logging'
    )
    
    args = parser.parse_args()
    
    # Setup logger
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_logger(Path.cwd() / 'logs', log_level)
    logger = get_logger()
    
    logger.section("STANDALONE TAX CALCULATOR")
    logger.info("Calculate tax deductions from invoice catalog")
    
    try:
        # Validate catalog file
        catalog_path = Path(args.catalog)
        if not catalog_path.exists():
            logger.error(f"Catalog file not found: {catalog_path}")
            sys.exit(1)
        
        logger.info(f"Loading catalog: {catalog_path}")
        
        # Load catalog
        loader = CatalogLoader()
        
        # Detect format and load
        ext = catalog_path.suffix.lower()
        if ext == '.csv':
            catalog = loader.load_from_csv(catalog_path)
        elif ext in ['.xlsx', '.xls']:
            catalog = loader.load_from_excel(catalog_path)
        elif ext == '.json':
            catalog = loader.load_from_json(catalog_path)
        else:
            logger.error(f"Unsupported catalog format: {ext}")
            logger.error("Supported formats: .csv, .xlsx, .xls, .json")
            sys.exit(1)
        
        if not catalog:
            logger.error("No entries found in catalog")
            sys.exit(1)
        
        logger.success(f"Loaded {len(catalog)} entries from catalog")
        
        # Create tax strategy
        if args.strategy == 'ato':
            strategy = ATOStrategy()
            logger.info("Using ATO tax strategy")
        else:
            logger.error("Custom strategy not yet implemented")
            sys.exit(1)
        
        # Validate WFH log if provided
        wfh_log_path = None
        if args.wfh_log:
            wfh_log_path = Path(args.wfh_log)
            if not wfh_log_path.exists():
                logger.error(f"WFH log file not found: {wfh_log_path}")
                sys.exit(1)
            logger.info(f"Using WFH log: {wfh_log_path}")
        
        # Validate work-use percentage
        work_use_percentage = args.work_use_percentage
        if work_use_percentage is not None:
            if work_use_percentage < 0 or work_use_percentage > 100:
                logger.error(f"Invalid work-use percentage: {work_use_percentage}% (must be 0-100)")
                sys.exit(1)
            logger.info(f"Using static work-use percentage: {work_use_percentage}%")
        
        # Create tax calculator
        logger.section("CALCULATING TAX DEDUCTIONS")
        
        calculator = TaxCalculator(
            strategy,
            work_use_percentage=work_use_percentage,
            wfh_log_path=wfh_log_path,
            financial_year=args.financial_year
        )
        
        # Calculate deductions
        tax_entries = calculator.calculate_deductions(catalog)
        
        if not tax_entries:
            logger.warning("No tax entries generated")
            sys.exit(0)
        
        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            # Default output based on format
            if args.format == 'csv':
                output_path = Path('tax_report.csv')
            elif args.format == 'excel':
                output_path = Path('tax_report.xlsx')
            else:
                output_path = Path('tax_report.json')
        
        # Export tax report
        logger.section("EXPORTING TAX REPORT")
        
        exported_path = calculator.export_tax_report(
            tax_entries,
            output_path,
            format=args.format
        )
        
        logger.success(f"Tax report exported: {exported_path}")
        
        # Show WFH report if requested
        if args.show_wfh_report:
            wfh_report = calculator.get_wfh_report()
            if wfh_report:
                logger.section("WFH STATISTICS")
                print(wfh_report)
            else:
                logger.info("No WFH statistics available (no WFH log provided)")
        
        # Summary
        logger.section("SUMMARY")
        total_amount = sum(entry.get('TotalAmount', 0) for entry in tax_entries)
        total_deductible = sum(entry.get('DeductibleAmount', 0) for entry in tax_entries)
        
        logger.info(f"Total invoices processed: {len(tax_entries)}")
        logger.info(f"Total invoice amount: ${total_amount:,.2f}")
        logger.info(f"Total deductible amount: ${total_deductible:,.2f}")
        logger.success("Tax calculation complete!")
        
    except KeyboardInterrupt:
        logger.warning("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
