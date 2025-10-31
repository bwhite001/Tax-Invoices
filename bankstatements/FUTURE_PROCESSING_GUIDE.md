# Future Bank Statement Processing Guide

This guide explains how to process new bank statements in the future using the established workflow.

---

## 📁 Directory Structure

```
G:/My Drive/Tax Invoices/
├── Statements/
│   └── FY2024-2025/              # Source statements
│       └── temp_processing/       # Temporary processing folder
├── FY2024-2025/
│   └── Processed/
│       └── BankStatements/        # Organized outputs
│           └── ZipMoney_YYYYMMDD_HHMMSS/  # Timestamped results
└── bankstatements/
    ├── Scripts (extraction & cataloging tools)
    └── extracted/                 # Temporary output folder
```

---

## 🔄 Processing Workflow for New Statements

### Step 1: Prepare New Statements
Place new PDF statements in: `Statements/FY[YEAR]/`

### Step 2: Run File Preparation
```bash
python bankstatements/prepare_files.py
```
- Copies PDFs to temp_processing folder
- Adds "zip_" prefix for auto-detection
- Preserves original files

### Step 3: Extract Transactions
```bash
python bankstatements/zip_money_extractor.py
```
- Extracts transactions from all PDFs
- Outputs to: `bankstatements/extracted/zip_transactions.csv`

### Step 4: Remove Duplicates
```bash
python bankstatements/remove_duplicates.py
```
- Cleans duplicate transactions
- Updates zip_transactions.csv

### Step 5: Catalog & Categorize
```bash
python bankstatements/run_cataloger.py
```
- Consolidates transactions
- Auto-categorizes expenses
- Generates multiple output formats

### Step 6: Fix Categorization (if needed)
```bash
python bankstatements/fix_categorization.py
```
- Corrects Income/Expense types
- Improves category assignments

### Step 7: Organize Outputs
```bash
python bankstatements/organize_outputs.py
```
- Moves files to FY-specific directory
- Creates timestamped folder
- Generates processing metadata

---

## 📊 Output Files Explained

### Main Catalog Files
- **expense_catalog.csv** - Master catalog with all transactions
- **expense_catalog.xlsx** - Excel version with summary sheets
- **zip_transactions.csv** - Raw extracted transaction data

### Analysis Files
- **monthly_expenses_by_category.csv** - Monthly spending breakdown
- **expenses_only.csv** - Purchase transactions only
- **income_only.csv** - Refunds and credits

### Category Files
- **category_Shopping.csv** - Shopping transactions
- **category_Dining.csv** - Food and dining
- **category_Entertainment.csv** - Entertainment purchases
- **category_Banking.csv** - Fees and charges
- **category_Transfer.csv** - BPAY payments
- **category_Transport.csv** - Uber and transport
- **category_Utilities.csv** - Utility bills
- **category_Income.csv** - Refunds
- **category_Other.csv** - Uncategorized

### Documentation
- **PROCESSING_SUMMARY.md** - Comprehensive processing report
- **CROSS_REFERENCE_MAPPING.md** - Invoice matching guide
- **PROCESSING_METADATA.txt** - Processing details and timestamp

---

## 🔧 Customization

### Adding New Categories
Edit `bankstatements/fix_categorization.py`:
```python
def categorize_transaction(row):
    desc = str(row['description']).lower()
    
    # Add your custom category
    if 'your_keyword' in desc:
        return 'YourCategory'
    
    # ... rest of categorization logic
```

### Adjusting Date Formats
Edit `bankstatements/zip_money_extractor.py`:
```python
date_patterns = [
    r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})',  # Current: "1 Aug 2024"
    # Add new patterns here
]
```

### Modifying Output Structure
Edit `bankstatements/organize_outputs.py`:
```python
# Change FY directory
fy_dir = base_dir / "FY2025-2026" / "Processed" / "BankStatements"

# Change timestamp format
timestamp = datetime.now().strftime("%Y%m%d")  # Date only
```

---

## 🎯 Best Practices

### Monthly Processing
1. Download statements at month-end
2. Process immediately while fresh
3. Cross-reference with invoices
4. Archive processed statements

### File Naming
- Keep "zip_" prefix for auto-detection
- Use consistent naming: "Month YYYY.pdf"
- Avoid special characters

### Data Validation
- Check transaction counts match statements
- Verify date ranges are complete
- Spot-check amounts and descriptions
- Review categorization accuracy

### Backup Strategy
- Original PDFs remain in Statements folder
- Processed outputs in FY-specific directories
- Keep temp_processing folder until verified
- Archive old fiscal years annually

---

## 🔍 Troubleshooting

### "No transactions extracted"
- Check PDF format (must be text-based, not scanned)
- Verify "zip_" prefix in filename
- Ensure PDFs are in temp_processing folder

### "Wrong categories assigned"
- Run fix_categorization.py
- Manually edit expense_catalog.csv if needed
- Update categorization rules for future

### "Duplicate transactions"
- Run remove_duplicates.py again
- Check if same statement processed twice
- Verify date ranges don't overlap

### "Missing transactions"
- Compare with statement summary
- Check date format parsing
- Review extraction regex patterns

---

## 📅 Fiscal Year Transition

When starting a new fiscal year:

1. Create new FY directory:
   ```
   Statements/FY2025-2026/
   FY2025-2026/Processed/BankStatements/
   ```

2. Update organize_outputs.py:
   ```python
   fy_dir = base_dir / "FY2025-2026" / "Processed" / "BankStatements"
   ```

3. Update prepare_files.py:
   ```python
   source_dir = Path("G:/My Drive/Tax Invoices/Statements/FY2025-2026")
   ```

4. Process new statements using same workflow

---

## 📊 Cross-Reference with Invoices

### Amazon Orders
1. Open CROSS_REFERENCE_MAPPING.md
2. Find Amazon Order IDs
3. Search invoice catalog for matching IDs
4. Verify amounts and dates match

### Other Merchants
1. Use transaction date ±3 days
2. Match by amount
3. Check merchant name variations
4. Document matches in spreadsheet

---

## 🛠️ Script Reference

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| prepare_files.py | Copy & rename PDFs | Statements/FY/ | temp_processing/ |
| zip_money_extractor.py | Extract transactions | temp_processing/ | zip_transactions.csv |
| remove_duplicates.py | Clean duplicates | zip_transactions.csv | Updated CSV |
| run_cataloger.py | Categorize expenses | zip_transactions.csv | Multiple CSVs |
| fix_categorization.py | Improve categories | expense_catalog.csv | Updated catalog |
| organize_outputs.py | Organize outputs | extracted/ | FY/Processed/ |

---

## 📝 Notes

- All scripts use absolute paths for reliability
- Original files are never modified
- Processing is idempotent (can run multiple times)
- Outputs are timestamped to prevent overwrites
- Scripts work with Python 3.8+

---

## 🆘 Support

For issues or questions:
1. Check TODO.md for processing checklist
2. Review USER_GUIDE.txt for detailed instructions
3. Consult PROCESSING_SUMMARY.md for last run details
4. Check script comments for technical details

---

**Last Updated**: October 31, 2025  
**Version**: 1.0  
**Compatible with**: Zip Money statements (FY2024-2025 format)
