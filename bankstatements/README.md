# Bank Statement Extractor & Expense Cataloger

Python scripts for extracting and cataloging expenses from Australian bank statements.

## Supported Banks
- **Suncorp Bank** (CSV and PDF)
- **Beyond Bank Australia** (PDF)
- **Zip Money/Pay** (CSV and PDF)
- **Afterpay** (CSV reconciliation reports and PDF)

## Prerequisites

### Python
- Python 3.8 or higher
- pip (Python package installer)

### Java (for PDF processing)
- Java Runtime Environment (JRE) 8 or higher
- Required for tabula-py PDF table extraction

## Installation

1. **Install Python packages:**
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pandas openpyxl pdfplumber PyPDF2 tabula-py
```

2. **Verify Java installation:**
```bash
java -version
```

If Java is not installed, download from: https://www.java.com/download/

## Usage

### Step 1: Extract Bank Statements

1. Create a folder for your bank statements (e.g., `statements`)
2. Download statements from your banks:
   - **Suncorp**: Log into Internet Banking > Transaction History > Download as CSV
   - **Beyond Bank**: Internet Banking > Accounts > Create Transaction Listing (PDF)
   - **Zip**: Zip Dashboard > Settings > Disbursements > Export CSV
   - **Afterpay**: Business Hub > Reconciliation > Export Report (CSV)

3. Place all downloaded files in the `statements` folder
4. Run the extractor:
```bash
python bank_statement_extractor.py
```

5. Follow the prompts to specify input/output folders
6. The script will extract transactions from all statement files

### Step 2: Catalog Expenses

1. Run the cataloger:
```bash
python expense_cataloger.py
```

2. The script will:
   - Load all extracted CSV files
   - Consolidate transactions from all banks
   - Automatically categorize expenses
   - Generate summary statistics
   - Create master catalog file

## Output Files

The scripts generate the following files in the output folder:

### From Extractor:
- `suncorp_transactions.csv` - Extracted Suncorp transactions
- `beyondbank_transactions.csv` - Extracted Beyond Bank transactions
- `zip_transactions.csv` - Extracted Zip transactions
- `afterpay_transactions.csv` - Extracted Afterpay transactions

### From Cataloger:
- `expense_catalog.csv` - Master catalog of all transactions
- `expense_catalog.xlsx` - Excel version with summary sheet
- `monthly_expenses_by_category.csv` - Monthly breakdown by category
- `expenses_only.csv` - Filtered view of expenses
- `income_only.csv` - Filtered view of income
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
