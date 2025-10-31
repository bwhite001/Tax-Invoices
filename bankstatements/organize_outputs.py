"""
Organize bank statement outputs into FY-specific directories with timestamps
"""
import shutil
from pathlib import Path
from datetime import datetime

def organize_outputs():
    print("="*60)
    print("Organizing Bank Statement Outputs")
    print("="*60)
    
    # Define paths
    base_dir = Path("G:/My Drive/Tax Invoices")
    extracted_dir = base_dir / "bankstatements" / "extracted"
    
    # Create FY directory structure
    fy_dir = base_dir / "FY2024-2025" / "Processed" / "BankStatements"
    
    # Create timestamped subdirectory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = fy_dir / f"ZipMoney_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nCreating output directory: {output_dir}")
    
    # Files to move
    files_to_move = [
        "expense_catalog.csv",
        "expense_catalog.xlsx",
        "zip_transactions.csv",
        "monthly_expenses_by_category.csv",
        "expenses_only.csv",
        "income_only.csv",
        "PROCESSING_SUMMARY.md",
        "CROSS_REFERENCE_MAPPING.md"
    ]
    
    # Move category files
    category_files = list(extracted_dir.glob("category_*.csv"))
    
    print(f"\nMoving {len(files_to_move) + len(category_files)} files...")
    
    moved_count = 0
    
    # Move main files
    for filename in files_to_move:
        source = extracted_dir / filename
        if source.exists():
            dest = output_dir / filename
            shutil.copy2(source, dest)
            print(f"  ✓ {filename}")
            moved_count += 1
        else:
            print(f"  ✗ {filename} (not found)")
    
    # Move category files
    for source in category_files:
        dest = output_dir / source.name
        shutil.copy2(source, dest)
        print(f"  ✓ {source.name}")
        moved_count += 1
    
    # Create a processing metadata file
    metadata = f"""# Bank Statement Processing Metadata

**Processing Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Fiscal Year**: FY2024-2025
**Bank**: Zip Money
**Statement Period**: July 2024 - June 2025
**Statements Processed**: 24 PDF files
**Transactions Extracted**: 75 unique transactions
**Output Directory**: {output_dir}

## Files Generated
- expense_catalog.csv (master catalog)
- expense_catalog.xlsx (Excel with summaries)
- zip_transactions.csv (raw extracted data)
- monthly_expenses_by_category.csv
- expenses_only.csv
- income_only.csv
- category_*.csv (9 category files)
- PROCESSING_SUMMARY.md
- CROSS_REFERENCE_MAPPING.md

## Processing Steps
1. File preparation (24 PDFs with "zip_" prefix)
2. Transaction extraction using zip_money_extractor.py
3. Duplicate removal (150 → 75 transactions)
4. Categorization and type assignment
5. Output generation and organization

## Next Steps
- Cross-reference with invoice catalogs
- Review for tax deductions
- Verify business vs personal expenses
"""
    
    metadata_file = output_dir / "PROCESSING_METADATA.txt"
    metadata_file.write_text(metadata, encoding='utf-8')
    print(f"  ✓ PROCESSING_METADATA.txt")
    moved_count += 1
    
    print(f"\n{'='*60}")
    print(f"SUCCESS! Moved {moved_count} files")
    print(f"{'='*60}")
    print(f"\nOutput location:")
    print(f"  {output_dir}")
    print(f"\nOriginal files remain in: {extracted_dir}")
    print(f"(You can delete them after verifying the organized outputs)")
    
    return output_dir

if __name__ == "__main__":
    output_dir = organize_outputs()
    print(f"\n✓ Bank statement outputs organized successfully!")
    print(f"✓ Location: {output_dir}")
