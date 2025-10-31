"""
Run expense cataloger on extracted Zip Money transactions
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from expense_cataloger import ExpenseCataloger

def main():
    print("="*60)
    print("Expense Cataloger - Zip Money Transactions")
    print("="*60)
    
    # Set folders
    input_folder = "G:/My Drive/Tax Invoices/bankstatements/extracted"
    
    print(f"\nInput folder: {input_folder}")
    print("Output: Same folder with cataloged files")
    
    # Create cataloger
    cataloger = ExpenseCataloger(input_folder)
    
    # Load statements
    print("\n" + "="*60)
    if not cataloger.load_all_statements():
        print("No statements loaded. Exiting.")
        return
    
    # Consolidate and categorize
    print("\n" + "="*60)
    consolidated_df = cataloger.consolidate_transactions()
    
    if consolidated_df.empty:
        print("No transactions to process. Exiting.")
        return
    
    # Generate summary
    cataloger.generate_summary(consolidated_df)
    
    # Save main catalog
    cataloger.save_catalog(consolidated_df)
    
    # Create monthly report
    try:
        cataloger.create_monthly_report(consolidated_df)
    except Exception as e:
        print(f"Could not create monthly report: {e}")
    
    # Create filtered exports
    print("\n" + "="*60)
    print("Creating filtered exports...")
    cataloger.filter_and_export(consolidated_df)
    
    print("\n" + "="*60)
    print("CATALOGING COMPLETE!")
    print("="*60)
    print("\nGenerated files:")
    print("  - expense_catalog.csv (master catalog)")
    print("  - expense_catalog.xlsx (Excel with summaries)")
    print("  - monthly_expenses_by_category.csv")
    print("  - expenses_only.csv")
    print("  - income_only.csv")
    print("  - category_*.csv (individual category files)")

if __name__ == "__main__":
    main()
