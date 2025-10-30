# Bank Statement Extractor & Expense Cataloger

**Complete Python toolkit for extracting and cataloging expenses from Australian bank statements**

---

## 🎯 Overview

Two powerful Python scripts that automate the extraction and categorization of transactions from Australian bank statements. Perfect for tax preparation, expense tracking, and financial analysis.

### Supported Financial Institutions
- **Suncorp Bank** - CSV and PDF formats
- **Beyond Bank Australia** - PDF format
- **Zip Money/Pay** - CSV and PDF formats  
- **Afterpay** - CSV reconciliation reports and PDF statements

---

## 📦 What's Included

### Core Scripts
1. **bank_statement_extractor.py** (19.8 KB)
   - Extracts transactions from PDF and CSV statement files
   - Automatic bank detection from filename keywords
   - Handles multiple file formats and layouts
   - Error handling and progress reporting

2. **expense_cataloger.py** (14.3 KB)
   - Consolidates transactions from all banks
   - Automatic expense categorization (13 categories)
   - Generates summary statistics and reports
   - Multiple export formats (CSV, Excel)

### Documentation
- **README.md** - Complete project documentation
- **USER_GUIDE.txt** - Detailed step-by-step instructions
- **requirements.txt** - Python package dependencies

### Utilities
- **quick_start.bat** - Windows automated setup script
- Organized folder structure for input/output

---

## ⚙️ Key Features

### Extraction Capabilities
✓ Dual format support (CSV and PDF)  
✓ Multi-bank processing in single run  
✓ Preserves all transaction metadata  
✓ Date standardization across formats  
✓ Balance tracking where available  

### Cataloging & Analysis
✓ Automatic expense categorization  
✓ Income vs expense classification  
✓ Monthly spending breakdown  
✓ Category-wise summaries  
✓ Bank-wise transaction analysis  
✓ Excel export with summary sheets  
✓ Filtered views by category  

### Smart Categorization
Automatically assigns transactions to 13 categories:
- Groceries (Coles, Woolworths, ALDI, IGA)
- Dining & Restaurants (Uber Eats, Menulog, cafes)
- Transport & Fuel (BP, Shell, Caltex, Uber)
- Utilities (electricity, internet, phone)
- Entertainment (Netflix, Spotify, streaming)
- Shopping (Amazon, Bunnings, Kmart)
- Health & Medical (pharmacy, doctor, dental)
- Insurance
- Subscriptions & Memberships
- Banking Fees
- Income (salary, refunds)
- Transfers (BPAY, inter-account)
- Other (uncategorized)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Java Runtime Environment (for PDF processing)
- Windows operating system

### Installation

**Option 1: Automated (Windows)**
```bash
# Double-click quick_start.bat
# Follow the prompts
```

**Option 2: Manual**
```bash
# Install Python packages
pip install -r requirements.txt

# Or install individually
pip install pandas openpyxl pdfplumber PyPDF2 tabula-py
```

### Usage

**Step 1: Download Bank Statements**
- Log into your online banking
- Download statements (CSV preferred over PDF)
- Save to the `statements` folder
- Include bank name in filename (e.g., `suncorp_oct_2024.csv`)

**Step 2: Extract Transactions**
```bash
python bank_statement_extractor.py
```
- Processes all statement files
- Creates individual CSV files per bank

**Step 3: Catalog Expenses**
```bash
python expense_cataloger.py
```
- Consolidates all transactions
- Generates categorized expense catalog
- Creates summary reports

---

## 📊 Output Files

### From Extractor
- `suncorp_transactions.csv`
- `beyondbank_transactions.csv`
- `zip_transactions.csv`
- `afterpay_transactions.csv`

### From Cataloger
- `expense_catalog.csv` - Master consolidated file
- `expense_catalog.xlsx` - Excel with summary sheet
- `monthly_expenses_by_category.csv` - Monthly breakdown
- `expenses_only.csv` - Filtered expense view
- `income_only.csv` - Filtered income view
- `category_*.csv` - Individual category files (optional)

---

## 💡 Use Cases

### Personal Finance
- Track monthly spending by category
- Identify subscription and recurring costs
- Budget planning and expense analysis
- Financial goal tracking

### Tax Preparation
- Organize deductible expenses
- Work-from-home expense tracking (ATO compliant)
- Business expense reporting
- Financial year-end reconciliation

### Business
- Expense claim preparation
- Cash flow analysis
- Vendor payment tracking
- Financial reporting

---

## 📥 Downloading Statements

### Suncorp Bank
**Internet Banking → Transaction History → Download as CSV**
- Select account and date range (max 364 days)
- Choose CSV format for best results
- eStatements also available as PDF

### Beyond Bank Australia
**Internet Banking → Accounts → Create Transaction Listing**
- Select account and date range (max 1 year)
- Download as PDF
- Not a replacement for official statements

### Zip Money/Pay
**Dashboard → Settings → Disbursements → Export CSV**
- Create custom report with date range
- Or download monthly statements via app

### Afterpay
**Business Hub → Reconciliation → Export Report**
- Choose Detail or Summary by Store
- Select date range and download CSV
- Consumer statements available via app

---

## 🔧 Customization

### Adding Categories
Edit the `CATEGORIES` dictionary in `expense_cataloger.py`:

```python
CATEGORIES = {
    'Your Category': ['keyword1', 'keyword2'],
    # Add more categories...
}
```

### Adjusting Date Formats
Add to the `formats` list in `_standardize_dates()`:

```python
formats = [
    '%d/%m/%Y',    # Australian standard
    '%Y-%m-%d',    # ISO format
    # Add your format...
]
```

### Custom Filtering
Modify the `filter_and_export()` method to create custom filtered views.

---

## ⚠️ Important Notes

### Security
- All processing is done **locally** - no data sent online
- Keep statement files secure and private
- Delete or securely archive after processing

### Tax & Accounting
- This tool **organizes data only**
- Always consult a registered tax agent for tax matters
- Keep original statements for official records
- Verify categorization accuracy for deductions

### Technical
- CSV format is more reliable than PDF extraction
- Password-protected PDFs must be decrypted first
- Some scanned PDFs may not extract properly
- Requires Java for PDF table extraction

---

## 🛠️ Troubleshooting

### "No CSV files found"
- Check files are in correct folder
- Verify filename contains bank keyword
- Ensure proper file extension (.csv or .pdf)

### "Error extracting PDF"
- Verify Java installation: `java -version`
- Check PDF is not password-protected
- Try using CSV format instead

### "Cannot parse date"
- Add date format to `_standardize_dates()` method
- Check date format in original statement

### Missing Transactions
- Verify date range in downloaded statement
- Check for multi-page PDFs
- Compare transaction count with bank statement

---

## 📞 Support

### Bank Support
- **Suncorp**: 13 11 55
- **Beyond Bank**: 13 25 85
- **Zip**: help.zip.co
- **Afterpay**: help.afterpay.com

### Technical Resources
- Python: docs.python.org
- Pandas: pandas.pydata.org
- PDFPlumber: github.com/jsvine/pdfplumber

---

## 📋 File Structure

```
bank_statement_tools/
│
├── bank_statement_extractor.py   # Main extraction script
├── expense_cataloger.py           # Cataloging script
├── requirements.txt               # Dependencies
├── README.md                      # Documentation
├── USER_GUIDE.txt                 # Detailed instructions
├── quick_start.bat                # Setup automation
│
├── statements/                    # Input folder
│   ├── suncorp_2024_10.csv
│   ├── beyondbank_statement.pdf
│   ├── zip_export.csv
│   └── afterpay_settlement.csv
│
└── extracted/                     # Output folder
    ├── suncorp_transactions.csv
    ├── expense_catalog.csv
    ├── expense_catalog.xlsx
    └── [other output files...]
```

---

## 📈 Example Output

### Console Summary
```
=== EXPENSE SUMMARY ===

Total Income:   $5,234.00
Total Expenses: $3,891.50
Net:            $1,342.50

--- Expenses by Category ---
Category          Total      Count   Average
Groceries         $856.20    12      $71.35
Dining            $432.50    18      $24.03
Transport         $380.00    8       $47.50
Utilities         $295.00    4       $73.75
...
```

### CSV Output
All transactions in standardized format with categorization, ready for analysis in Excel or import to accounting software.

---

## ✅ Benefits

- **Save Time**: Automate hours of manual data entry
- **Accuracy**: Eliminate transcription errors
- **Organization**: All expenses in one standardized format
- **Analysis**: Quick insights into spending patterns
- **Tax Ready**: Organized data for deduction claims
- **Multi-Bank**: Handle multiple financial institutions
- **Flexible**: Customize categories and outputs
- **Secure**: Process locally, no cloud upload

---

## 📝 Version Information

**Version**: 1.0  
**Date**: October 2024  
**Platform**: Windows (Python 3.8+)  
**License**: Personal use  

---

## 🎓 Best Practices

1. **Download Regularly**: Monthly or quarterly to keep current
2. **Use CSV When Possible**: More reliable than PDF extraction
3. **Consistent Naming**: Include bank and date in filenames
4. **Verify First**: Check a sample extraction before processing all
5. **Keep Originals**: Archive original statements after processing
6. **Review Categories**: Spot-check auto-categorization accuracy
7. **Backup Data**: Keep copies of processed files

---

## 🔐 Privacy & Security

Your financial data is sensitive. This tool:
- ✓ Processes everything **locally on your computer**
- ✓ Does **not** send data to any online service
- ✓ Does **not** store credentials or login information
- ✓ Creates standard CSV files you control
- ✓ Can be used offline once dependencies are installed

**Always keep your bank statements secure and delete when no longer needed.**

---

*Created for Australian bank statement processing and personal finance management. This tool is provided as-is for personal use.*