# Bank Statement Processing - Quick Start Guide

**Last Updated**: October 31, 2025  
**Version**: 2.0 (Current Workflow)

---

## 🚀 Quick Start - Process New Statements in 6 Steps

### Prerequisites
- Python 3.8+ installed
- Required packages: `pip install pandas openpyxl pdfplumber PyPDF2`

### Step-by-Step Workflow

```bash
# Step 1: Prepare Files (adds "zip_" prefix)
python bankstatements/prepare_files.py

# Step 2: Extract Transactions from PDFs
python bankstatements/zip_money_extractor.py

# Step 3: Remove Duplicates
python bankstatements/remove_duplicates.py

# Step 4: Catalog & Categorize
python bankstatements/run_cataloger.py

# Step 5: Fix Categorization (optional but recommended)
python bankstatements/fix_categorization.py

# Step 6: Organize Outputs by FY and Timestamp
python bankstatements/organize_outputs.py
```

**That's it!** Your processed statements will be in:
```
FY2024-2025/Processed/BankStatements/ZipMoney_YYYYMMDD_HHMMSS/
```

---

## 📁 Before You Start

### 1. Place Your Statements
Put PDF statements in:
```
G:/My Drive/Tax Invoices/Statements/FY2024-2025/
```

### 2. File Naming
- Any naming works (numbered or monthly)
- Script will add "zip_" prefix automatically
- Original files are preserved

---

## 📊 What You Get

### Output Files (17 files)
1. **expense_catalog.csv** - Master catalog
2. **expense_catalog.xlsx** - Excel with summaries
3. **zip_transactions.csv** - Raw data
4. **monthly_expenses_by_category.csv** - Monthly breakdown
5. **expenses_only.csv** - Purchases only
6. **income_only.csv** - Refunds only
7-14. **category_*.csv** - 8 category files
15. **PROCESSING_SUMMARY.md** - Detailed report
16. **CROSS_REFERENCE_MAPPING.md** - Invoice matching guide
17. **PROCESSING_METADATA.txt** - Processing details

### Categories
- Shopping (Amazon, Temu, etc.)
- Dining (Pizza, McDonald's, etc.)
- Entertainment (Steam, Netflix, etc.)
- Banking (Fees, charges)
- Transfer (BPAY payments)
- Transport (Uber, fuel)
- Utilities (Bills)
- Income (Refunds)
- Other (Uncategorized)

---

## 🔧 Detailed Process Breakdown

### Process 1: File Preparation
**Script**: `prepare_files.py`

**What it does**:
- Scans `Statements/FY2024-2025/` for PDF files
- Copies files to `temp_processing/` folder
- Adds "zip_" prefix for auto-detection
- Preserves original files

**Input**: PDF files in Statements folder  
**Output**: Prefixed PDFs in temp_processing folder

**Manual Alternative**:
```bash
# If you prefer manual copying:
# 1. Create: Statements/FY2024-2025/temp_processing/
# 2. Copy PDFs and rename with "zip_" prefix
# Example: "August 2024.pdf" → "zip_August 2024.pdf"
```

---

### Process 2: Transaction Extraction
**Script**: `zip_money_extractor.py`

**What it does**:
- Reads all PDFs with "zip_" prefix
- Extracts transaction data using pdfplumber
- Parses dates, descriptions, and amounts
- Outputs to CSV format

**Input**: PDFs in temp_processing folder  
**Output**: `bankstatements/extracted/zip_transactions.csv`

**What gets extracted**:
- Date (standardized to YYYY-MM-DD)
- Description (merchant name, order IDs)
- Amount (positive for purchases, negative for payments)
- Source file name

**Example Output**:
```csv
date,description,amount,source_file
2024-08-08,Amazon AU Order # 213803...,58.25,zip_August 2024.pdf
2024-08-03,BPAY Payment (,-250.0,zip_August 2024.pdf
```

---

### Process 3: Duplicate Removal
**Script**: `remove_duplicates.py`

**What it does**:
- Loads zip_transactions.csv
- Identifies exact duplicate transactions
- Removes duplicates (keeps first occurrence)
- Updates the CSV file

**Why needed**: 
- Monthly and numbered statements may overlap
- Same transaction appears in multiple PDFs
- Ensures accurate totals

**Example**:
```
Before: 150 transactions (with duplicates)
After: 75 unique transactions
```

---

### Process 4: Cataloging & Categorization
**Script**: `run_cataloger.py`

**What it does**:
- Loads cleaned transaction data
- Auto-categorizes based on keywords
- Generates multiple output formats
- Creates summary statistics

**Categorization Logic**:
```python
# Examples:
"Amazon" → Shopping
"Pizza Hut" → Dining
"Steam" → Entertainment
"BPAY Payment" → Transfer
"Monthly Account Fee" → Banking
```

**Outputs**:
- Master catalog (CSV + Excel)
- Monthly breakdown
- Filtered views (expenses, income)
- Category-specific files

---

### Process 5: Category Correction
**Script**: `fix_categorization.py`

**What it does**:
- Fixes Income/Expense type reversal
- Improves category assignments
- Corrects BPAY payment categorization
- Updates expense_catalog.csv

**Key Fixes**:
- Negative amounts → "Payment" type
- Positive amounts → "Purchase" type
- BPAY → "Transfer" category
- Refunds → "Income" category
- Account fees → "Banking" category

**Before/After Example**:
```
Before: BPAY Payment → Transport (wrong)
After:  BPAY Payment → Transfer (correct)
```

---

### Process 6: Output Organization
**Script**: `organize_outputs.py`

**What it does**:
- Creates FY-specific directory structure
- Generates timestamped folder
- Copies all output files
- Creates processing metadata

**Directory Structure**:
```
FY2024-2025/
└── Processed/
    └── BankStatements/
        └── ZipMoney_20251031_201436/
            ├── expense_catalog.csv
            ├── expense_catalog.xlsx
            ├── zip_transactions.csv
            ├── monthly_expenses_by_category.csv
            ├── expenses_only.csv
            ├── income_only.csv
            ├── category_*.csv (8 files)
            ├── PROCESSING_SUMMARY.md
            ├── CROSS_REFERENCE_MAPPING.md
            └── PROCESSING_METADATA.txt
```

**Benefits**:
- Organized by fiscal year
- Timestamped (no overwrites)
- Easy to find past processing runs
- Consistent with invoice catalog structure

---

## 🎯 Common Use Cases

### Monthly Processing
```bash
# 1. Download new month's statement
# 2. Place in Statements/FY2024-2025/
# 3. Run all 6 steps
# 4. Review outputs in Processed folder
```

### Reprocessing with Changes
```bash
# If you need to reprocess:
# 1. Delete contents of bankstatements/extracted/
# 2. Run steps 2-6 again
# 3. New timestamped folder will be created
```

### Processing Multiple Months
```bash
# Place all PDFs in Statements folder
# Run all 6 steps once
# Script processes all files together
```

---

## 🔍 Verification Checklist

After processing, verify:

- [ ] Check transaction count matches statements
- [ ] Verify date range is complete
- [ ] Review category assignments
- [ ] Spot-check amounts
- [ ] Open Excel file to view summaries
- [ ] Check CROSS_REFERENCE_MAPPING.md for Amazon orders

---

## 🆘 Troubleshooting

### "No files found"
- Check PDFs are in correct folder
- Verify folder path in script
- Ensure PDFs are not password-protected

### "No transactions extracted"
- Check PDF format (must be text-based, not scanned)
- Verify "zip_" prefix was added
- Review PDF content manually

### "Wrong categories"
- Run fix_categorization.py
- Manually edit expense_catalog.csv if needed
- Update categorization rules in script

### "Duplicate transactions"
- Run remove_duplicates.py again
- Check if same statement processed twice
- Verify date ranges don't overlap

---

## 📝 Tips & Best Practices

### File Management
- Keep original PDFs in Statements folder
- Don't delete temp_processing until verified
- Archive old FY folders annually

### Processing Timing
- Process monthly for better tracking
- Run immediately after downloading statements
- Cross-reference with invoices while fresh

### Customization
- Edit fix_categorization.py to add categories
- Modify keywords for better matching
- Adjust date formats if needed

### Data Validation
- Compare totals with statement summaries
- Verify payment counts
- Check for missing months

---

## 📚 Additional Documentation

- **FUTURE_PROCESSING_GUIDE.md** - Detailed workflow and customization
- **PROCESSING_SUMMARY.md** - Last processing results
- **CROSS_REFERENCE_MAPPING.md** - Invoice matching guide
- **TASK_COMPLETION_SUMMARY.md** - Complete task details

---

## 🔄 For Next Fiscal Year

When starting FY2025-2026:

1. Create new folders:
   ```
   Statements/FY2025-2026/
   FY2025-2026/Processed/BankStatements/
   ```

2. Update scripts (2 files):
   - `prepare_files.py`: Change FY path
   - `organize_outputs.py`: Change FY path

3. Run same 6-step workflow

---

## ⚡ One-Line Summary

**Download statements → Run 6 scripts → Get organized, categorized data ready for tax prep**

---

**Questions?** Check FUTURE_PROCESSING_GUIDE.md for detailed explanations.

**Need Help?** Review script comments or consult USER_GUIDE.txt.
