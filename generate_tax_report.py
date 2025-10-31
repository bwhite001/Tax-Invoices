#!/usr/bin/env python3
"""
Tax Report Generator CLI

Simple command-line interface for generating tax reports.
Uses the modular tax_report_generator package.

Usage:
    python generate_tax_report.py
    python generate_tax_report.py --financial-year 2024-2025
    python generate_tax_report.py --financial-year 2025-2026 --base-dir "G:/My Drive/Tax Invoices"
"""

import sys
import argparse
from pathlib import Path

# Import the tax report generator
from tax_report_generator.main import TaxReportGenerator


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive tax reports with WFH calculations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate report for FY2024-2025 (default)
  python generate_tax_report.py

  # Generate report for specific financial year
  python generate_tax_report.py --financial-year 2025-2026

  # Specify custom base directory
  python generate_tax_report.py --base-dir "C:/Tax Documents"

The script will:
  1. Process WFH log to calculate actual work-from-home percentage
  2. Load and recalculate invoice deductions based on WFH percentage
  3. Process bank statement data
  4. Generate consolidated Excel report with multiple sheets
        """
    )
    
    parser.add_argument(
        "--financial-year",
        "-fy",
        default="2024-2025",
        help="Financial year in format YYYY-YYYY (default: 2024-2025)"
    )
    
    parser.add_argument(
        "--base-dir",
        "-d",
        type=Path,
        default=None,
        help="Base directory containing tax files (default: current directory)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        # Create generator instance
        generator = TaxReportGenerator(
            financial_year=args.financial_year,
            base_dir=args.base_dir
        )
        
        # Run the generation process
        report_path = generator.run()
        
        if report_path:
            print(f"\n✅ SUCCESS! Report generated successfully.")
            print(f"📁 Location: {report_path}")
            return 0
        else:
            print("\n❌ FAILED! Could not generate report.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
