"""
Main Module - Tax Report Generator

Orchestrates the entire tax report generation process.
Follows Command Pattern for clean separation of concerns.
"""

from pathlib import Path
from typing import Dict, Any
import sys

# Import our modules
from .config import Config
from .wfh_processor import WFHProcessor
from .invoice_processor import InvoiceProcessor
from .bank_processor import BankProcessor
from .report_generator import ReportGenerator


class TaxReportGenerator:
    """
    Main orchestrator for tax report generation
    
    Responsibilities:
    - Coordinate all processing steps
    - Handle errors gracefully
    - Provide progress feedback
    """

    def __init__(self, financial_year: str = "2024-2025", base_dir: Path = None):
        """
        Initialize tax report generator
        
        Args:
            financial_year: Financial year (e.g., "2024-2025")
            base_dir: Base directory path
        """
        self.config = Config(financial_year, base_dir)
        self.wfh_processor = WFHProcessor(self.config.tax_params.exclude_locations)
        self.invoice_processor = InvoiceProcessor(self.config.tax_params.wfh_categories)
        self.bank_processor = BankProcessor()
        self.report_generator = ReportGenerator(self.config.report_config)

        # Results storage
        self.results = {}

    def validate_inputs(self) -> Dict[str, bool]:
        """
        Validate all input files exist
        
        Returns:
            Dictionary with validation results
        """
        print("🔍 Validating input files...")
        validation = self.config.validate_paths()

        if not validation['all_valid']:
            print("❌ Missing required files:")
            for file_type, exists in validation['required'].items():
                if not exists:
                    print(f"   - {file_type}: {self.config.file_paths.__dict__[file_type]}")

            print("\nOptional files:")
            for file_type, exists in validation['optional'].items():
                status = "✓ Found" if exists else "⚠ Missing"
                print(f"   - {file_type}: {status}")

        return validation

    def process_wfh_data(self) -> Dict[str, Any]:
        """
        Process WFH log data
        
        Returns:
            WFH statistics
        """
        print("\n🏠 Processing WFH log...")

        try:
            # Load WFH data
            wfh_data = self.wfh_processor.load_wfh_log(self.config.file_paths.wfh_log)

            # Calculate statistics
            wfh_stats = self.wfh_processor.calculate_statistics()

            print(f"✓ Processed {wfh_stats['total_days']} work days")
            print(f"  WFH Percentage: {wfh_stats['wfh_percentage']:.1f}%")

            self.results['wfh'] = {
                'data': wfh_data,
                'stats': wfh_stats
            }

            return wfh_stats

        except Exception as e:
            print(f"❌ Error processing WFH data: {e}")
            raise

    def process_invoice_data(self, wfh_percentage: float) -> Dict[str, Any]:
        """
        Process invoice catalog with WFH percentage
        
        Args:
            wfh_percentage: Calculated WFH percentage
            
        Returns:
            Invoice statistics
        """
        print("\n📄 Processing invoice catalog...")

        try:
            # Load invoice data
            invoice_df = self.invoice_processor.load_invoice_catalog(self.config.file_paths.invoice_catalog)

            # Recalculate deductions
            updated_df = self.invoice_processor.recalculate_deductions(wfh_percentage)

            # Get summary statistics
            invoice_stats = self.invoice_processor.get_summary_statistics()

            print(f"✓ Processed {invoice_stats['invoice_count']} invoices")
            print(f"  Original deductions: ${invoice_stats['original_deduction']:,.2f}")
            print(f"  Recalculated deductions: ${invoice_stats['recalculated_deduction']:,.2f}")
            print(f"  Adjustment: ${invoice_stats['adjustment']:,.2f}")

            self.results['invoice'] = {
                'data': updated_df,
                'stats': invoice_stats,
                'category_summary': self.invoice_processor.get_category_summary(),
                'monthly_summary': self.invoice_processor.get_monthly_summary()
            }

            return invoice_stats

        except Exception as e:
            print(f"❌ Error processing invoice data: {e}")
            raise

    def process_bank_data(self) -> Dict[str, Any]:
        """
        Process bank statement data
        
        Returns:
            Bank statistics
        """
        print("\n🏦 Processing bank statements...")

        try:
            # Load bank data
            bank_df = self.bank_processor.load_bank_statements(self.config.file_paths.bank_statements)

            if bank_df.empty:
                print("⚠ No bank statement data found")
                bank_stats = self.bank_processor.get_summary_statistics()
            else:
                # Categorize for tax
                categorized_df = self.bank_processor.categorize_for_tax()
                bank_stats = self.bank_processor.get_summary_statistics()

                print(f"✓ Processed {bank_stats['total_transactions']} transactions")
                print(f"  Potentially deductible: {bank_stats['tax_relevant_count']}")

            self.results['bank'] = {
                'data': bank_df,
                'stats': bank_stats
            }

            return bank_stats

        except Exception as e:
            print(f"❌ Error processing bank data: {e}")
            raise

    def generate_report(self) -> Path:
        """
        Generate consolidated Excel report
        
        Returns:
            Path to generated report
        """
        print("\n📊 Generating consolidated report...")

        try:
            # Create workbook
            self.report_generator.create_workbook()

            # Add sheets
            self.report_generator.add_summary_sheet(
                self.results['wfh']['stats'],
                self.results['invoice']['stats'],
                self.results['bank']['stats']
            )

            self.report_generator.add_invoice_sheet(self.results['invoice']['data'])
            self.report_generator.add_category_breakdown_sheet(self.results['invoice']['category_summary'])
            self.report_generator.add_wfh_analysis_sheet(
                self.results['wfh']['data'],
                self.results['wfh']['stats']['monthly_breakdown']
            )
            self.report_generator.add_bank_sheet(self.results['bank']['data'])
            self.report_generator.add_monthly_sheet(self.results['invoice']['monthly_summary'])

            # Save report
            output_path = self.config.get_output_path()
            self.report_generator.save_workbook(output_path)

            print(f"✓ Report generated: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Error generating report: {e}")
            raise

    def run(self) -> Path:
        """
        Run complete tax report generation process
        
        Returns:
            Path to generated report
        """
        print("="*70)
        print(f"TAX REPORT GENERATOR - {self.config.financial_year.upper()}")
        print("="*70)

        try:
            # Step 1: Validate inputs
            validation = self.validate_inputs()
            if not validation['all_valid']:
                raise FileNotFoundError("Required input files are missing")

            # Step 2: Process WFH data
            wfh_stats = self.process_wfh_data()
            wfh_percentage = wfh_stats['wfh_percentage']

            # Step 3: Process invoice data
            invoice_stats = self.process_invoice_data(wfh_percentage)

            # Step 4: Process bank data
            bank_stats = self.process_bank_data()

            # Step 5: Generate report
            report_path = self.generate_report()

            # Final summary
            print("\n" + "="*70)
            print("PROCESSING COMPLETE")
            print("="*70)
            print(f"Financial Year: {self.config.financial_year}")
            print(f"WFH Percentage: {wfh_percentage:.1f}%")
            print(f"Total Deductions: ${invoice_stats['recalculated_deduction']:,.2f}")
            print(f"Report Location: {report_path}")
            print("\nReport contains:")
            print("  • Summary - Overview statistics")
            print("  • Invoice Catalog - All processed invoices")
            print("  • Category Breakdown - Deductions by category")
            print("  • WFH Analysis - Daily and monthly WFH patterns")
            print("  • Bank Statements - Transaction data")
            print("  • Monthly Summary - Month-by-month breakdown")
            print("="*70)

            return report_path

        except Exception as e:
            print(f"\n❌ PROCESSING FAILED: {e}")
            import traceback
            traceback.print_exc()
            return None

    def __repr__(self) -> str:
        """String representation"""
        return f"TaxReportGenerator(fy={self.config.financial_year})"


def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate tax reports with WFH calculations")
    parser.add_argument(
        "--financial-year",
        default="2024-2025",
        help="Financial year (e.g., 2024-2025)"
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=None,
        help="Base directory path"
    )

    args = parser.parse_args()

    # Create and run generator
    generator = TaxReportGenerator(args.financial_year, args.base_dir)
    report_path = generator.run()

    if report_path:
        print(f"\n✅ Success! Report saved to: {report_path}")
        return 0
    else:
        print("\n❌ Failed to generate report")
        return 1


if __name__ == "__main__":
    sys.exit(main())
