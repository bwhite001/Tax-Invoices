# Bank Statement Processing System

**Version**: 2.0 (Updated October 2025)  
**Status**: Production-Ready  
**Current Focus**: Zip Money Statements

Automated system for extracting, cataloging, and organizing bank statement transactions for tax preparation and expense tracking.

---

## 🚀 Quick Start

**New to this system?** Start here: **[QUICKSTART.md](QUICKSTART.md)**

### 6-Step Workflow
```bash
python bankstatements/prepare_files.py          # 1. Prepare files
python bankstatements/zip_money_extractor.py    # 2. Extract transactions
python bankstatements/remove_duplicates.py      # 3. Remove duplicates
python bankstatements/run_cataloger.py          # 4. Catalog & categorize
python bankstatements/fix_categorization.py     # 5. Fix categories
python bankstatements/organize_outputs.py       # 6. Organize outputs
```

**Result**: Organized, categorized transactions in `FY2024-2025/Processed/BankStatements/`

---

## 📋 What This System Does

### Core Features
✅ **Extracts** transactions from PDF bank statements  
✅ **Removes** duplicate transactions automatically  
✅ **Categorizes** expenses into 9 categories  
✅ **Organizes** outputs by fiscal year and timestamp  
✅ **Generates** multiple report formats (CSV, Excel)  
✅ **Creates** cross-reference guides for invoice matching  

### Supported Banks
- **Zip Money/Pay** ✓ (Fully implemented with custom parser)
- **Suncorp Bank** (Legacy support via bank_statement_extractor.py)
- **Beyond Bank** (Legacy support via bank_statement_extractor.py)
- **Afterpay** (Legacy support via bank_statement_extractor.py)

---

## 📁 Current Workflow (Zip Money)

### Input
- PDF statements in: `Statements/FY2024-2025/`
- Any file naming (numbered or monthly)

### Processing
1. **File Preparation**: Adds "zip_" prefix for detection
2. **Extraction**: Parses PDF text, extracts transactions
3. **Deduplication**: Removes duplicate entries
4. **Cataloging**: Consolidates and categorizes
5. **Correction**: Fixes category assignments
6. **Organization**: Moves to FY-specific folders

### Output
- **Location**: `FY2024-2025/Processed/BankStatements/ZipMoney_TIMESTAMP/`
- **Files**: 17 files including CSV, Excel, summaries, and guides

---

## 📊 Output Files

### Main Catalogs
- `expense_catalog.csv` - Master catalog (all transactions)
- `expense_catalog.xlsx` - Excel with summary sheets
- `zip_transactions.csv` - Raw extracted data

### Analysis Files
- `monthly_expenses_by_category.csv` - Monthly breakdown
- `expenses_only.csv` - Purchase transactions
- `income_only.csv` - Refunds and credits

### Category Files (8 files)
- `category_Shopping.csv` - Amazon, Temu, etc.
- `category_Dining.csv` - Restaurants, fast food
- `category_Entertainment.csv` - Steam, Netflix, etc.
- `category_Banking.csv` - Fees and charges
- `category_Transfer.csv` - BPAY payments
- `category_Transport.csv` - Uber, fuel
- `category_Utilities.csv` - Bills
- `category_Income.csv` - Refunds
- `category_Other.csv` - Uncategorized

### Documentation
- `PROCESSING_SUMMARY.md` - Comprehensive report
- `CROSS_REFERENCE_MAPPING.md` - Invoice matching guide
- `PROCESSING_METADATA.txt` - Processing details

---

## 🛠️ Prerequisites

### Required
- **Python 3.8+** (Tested with 3.11.9)
- **Python Packages**:
  ```bash
  pip install -r requirements.txt
  ```
  Or individually:
  ```bash
  pip install pandas openpyxl pdfplumber PyPDF2
  ```

### Optional
- **Java** (Not required for current Zip Money workflow)
- Only needed if using legacy bank_statement_extractor.py with tabula-py

---

## 📚 Documentation

### Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - Step-by-step guide (START HERE)
- **[FUTURE_PROCESSING_GUIDE.md](FUTURE_PROCESSING_GUIDE.md)** - Detailed workflow and customization

### Reference
- **[TASK_COMPLETION_SUMMARY.md](TASK_COMPLETION_SUMMARY.md)** - Latest processing results
- **[USER_GUIDE.txt](USER_GUIDE.txt)** - Legacy documentation (for reference)

### Generated Reports
- **PROCESSING_SUMMARY.md** - Created after each run
- **CROSS_REFERENCE_MAPPING.md** - Invoice matching guide

---

## 🎯 Use Cases

### Tax Preparation
- Extract all transactions for fiscal year
- Categorize business vs personal expenses
- Cross-reference with invoice catalogs
- Calculate deductible amounts

### Expense Tracking
- Monthly spending analysis
- Category-based budgeting
- Merchant spending patterns
- Payment history tracking

### Invoice Reconciliation
- Match Amazon Order IDs with invoices
- Verify transaction amounts
- Track refunds and credits
- Identify missing receipts

---

## 🔧 Script Reference

### Current Workflow Scripts
| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| prepare_files.py | Add "zip_" prefix | Statements/FY/ | temp_processing/ |
| zip_money_extractor.py | Extract from PDFs | temp_processing/ | zip_transactions.csv |
| remove_duplicates.py | Clean duplicates | zip_transactions.csv | Updated CSV |
| run_cataloger.py | Categorize | zip_transactions.csv | Multiple CSVs |
| fix_categorization.py | Improve categories | expense_catalog.csv | Updated catalog |
| organize_outputs.py | Organize by FY | extracted/ | FY/Processed/ |

### Legacy Scripts (For Reference)
| Script | Status | Notes |
|--------|--------|-------|
| bank_statement_extractor.py | Legacy | Multi-bank support (requires Java) |
| expense_cataloger.py | Legacy | Used by run_cataloger.py |

---

## 📈 Processing Statistics (FY2024-2025)

### Latest Run
- **Statements Processed**: 24 PDFs
- **Transactions Extracted**: 75 unique
- **Date Range**: July 2024 - June 2025
- **Categories**: 9 categories assigned
- **Processing Time**: ~5 minutes

### Financial Summary
- **Total Purchases**: $4,281.40
- **Total Payments**: $4,896.49
- **Net Balance**: -$615.09

---

## 🔄 For Next Fiscal Year

When starting FY2025-2026:

1. **Create directories**:
   ```
   Statements/FY2025-2026/
   FY2025-2026/Processed/BankStatements/
   ```

2. **Update 2 scripts**:
   - `prepare_files.py` - Change source_dir path
   - `organize_outputs.py` - Change fy_dir path

3. **Run same workflow** - All 6 steps

See [FUTURE_PROCESSING_GUIDE.md](FUTURE_PROCESSING_GUIDE.md) for details.

---

## 🆘 Troubleshooting

### Common Issues

**"No files found"**
- Check PDFs are in `Statements/FY2024-2025/`
- Verify folder path in scripts
- Ensure PDFs are not password-protected

**"No transactions extracted"**
- Check PDF format (text-based, not scanned)
- Verify "zip_" prefix was added
- Review PDF content manually

**"Wrong categories"**
- Run `fix_categorization.py`
- Manually edit `expense_catalog.csv`
- Update categorization rules in script

**"Duplicate transactions"**
- Run `remove_duplicates.py` again
- Check if same statement processed twice

See [QUICKSTART.md](QUICKSTART.md) for more troubleshooting tips.

---

## 🔒 Security & Privacy

- ✅ All processing done locally
- ✅ No data sent to external services
- ✅ Original files preserved
- ✅ Sensitive data remains on local drive

**Recommendation**: Keep financial data on encrypted drives and backup regularly.

---

## 📝 Version History

### Version 2.0 (October 2025) - Current
- Custom Zip Money PDF parser
- Automated 6-step workflow
- FY-specific organization
- Timestamped outputs
- Cross-reference mapping
- Comprehensive documentation

### Version 1.0 (October 2024) - Legacy
- Multi-bank support (Suncorp, Beyond Bank, Zip, Afterpay)
- Generic extraction and cataloging
- Manual file organization
- `category_*.csv` - Individual files per category (optional)

## Expense Categories

The cataloger automatically assigns transactions to these categories:
- Groceries
- Dining & Restaurants
- Transport & Fuel
- Utilities (electricity, internet, phone)
- Entertainment & Subscriptions
- Shopping
- Health & Medical
- Insurance
- Banking Fees
- Income
- Transfers
- Other

## Customization

### Adding Custom Categories

Edit the `CATEGORIES` dictionary in `expense_cataloger.py`:

```python
CATEGORIES = {
    'Your Category': ['keyword1', 'keyword2', 'keyword3'],
    # ... more categories
}
```

### Adjusting Date Formats

If your bank uses a non-standard date format, add it to the `_standardize_dates` method:

```python
formats = [
    '%d/%m/%Y',      # 31/10/2024
    '%Y-%m-%d',      # 2024-10-31
    # Add your format here
]
```

## Troubleshooting

### Common Issues

**"No CSV files found"**
- Ensure files are in the correct folder
- Check that filenames contain bank keywords (suncorp, beyond, zip, afterpay)

**"Error extracting PDF"**
- Verify Java is installed and in PATH
- Check that PDF is not password-protected
- Some scanned PDFs may not extract properly

**"Cannot parse date"**
- Check date format in your statements
- Add the format to `_standardize_dates` method

**Missing transactions**
- Some banks may have different statement formats
- Check the source file and adjust regex patterns if needed

### Getting Help

For Australian bank-specific issues:
- **Suncorp**: 13 11 55
- **Beyond Bank**: 13 25 85
- **Zip**: help.zip.co
- **Afterpay**: help.afterpay.com

## Tax and Accounting

These scripts are designed to help organize financial data for:
- Tax deduction tracking
- Work-from-home expense claims
- Business expense reporting
- Personal budgeting

**Important**: Always consult with a registered tax agent or accountant for 
tax-related matters. This tool is for data organization only.

## File Structure

```
project/
│
├── bank_statement_extractor.py   # Extract statements from PDFs/CSVs
├── expense_cataloger.py           # Consolidate and categorize expenses
├── requirements.txt               # Python dependencies
├── README.md                      # This file
│
├── statements/                    # Input folder (your bank statements)
│   ├── suncorp_2024_10.csv
│   ├── beyondbank_statement.pdf
│   ├── zip_export.csv
│   └── afterpay_settlement.csv
│
└── extracted/                     # Output folder (generated files)
    ├── suncorp_transactions.csv
    ├── beyondbank_transactions.csv
    ├── zip_transactions.csv
    ├── afterpay_transactions.csv
    ├── expense_catalog.csv
    ├── expense_catalog.xlsx
    └── monthly_expenses_by_category.csv
```

## Security & Privacy

**Important Security Notes:**
- Bank statements contain sensitive financial information
- Keep all statement files secure and private
- Do not share or upload statements to untrusted services
- Delete or archive statements after processing
- This tool processes files locally - no data is sent online

## License

This tool is provided as-is for personal use. Use at your own risk.

## Version

Version 1.0 - October 2024
Compatible with Python 3.8+

## Author

Created for Australian bank statement processing and expense tracking.
