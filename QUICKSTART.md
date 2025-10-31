# Quick Start Guide

Get started with the Australian Tax Invoice Processing System in 15 minutes.

---

## 🎯 Choose Your Starting Point

Select the module you want to use:

1. **[Invoice Processing](#1-invoice-processing)** - Extract data from invoices using AI
2. **[Tax Report Generation](#2-tax-report-generation)** - Generate consolidated tax reports
3. **[Bank Statement Processing](#3-bank-statement-processing)** - Process bank statements
4. **[Gmail Invoice Extraction](#4-gmail-invoice-extraction)** - Auto-extract from Gmail
5. **[Work-From-Home Tracking](#5-work-from-home-tracking)** - Track WFH location

---

## 1. Invoice Processing

**Module**: `invoice_cataloger/`  
**Purpose**: AI-powered invoice data extraction and categorization  
**Time**: 10 minutes

### Prerequisites
- ✅ Python 3.8+ installed
- ✅ LM Studio running with model loaded
- ✅ Invoice files (PDF, images, documents)

### Quick Setup

```bash
# 1. Install dependencies
cd "g:/My Drive/Tax Invoices/invoice_cataloger"
pip install -r requirements.txt

# 2. Verify LM Studio is running
# Open LM Studio → Load model → Start Developer Server

# 3. Check prerequisites
python invoice_cataloger.py --check-only

# 4. Process invoices
python invoice_cataloger.py --financial-year 2024-2025
```

### Expected Output
```
✓ Invoice folder exists
✓ LM Studio connected
✓ Processing 150 files...
✓ Saved to: FY2024-2025/Processed/Invoice_Catalog_20241215_143022.xlsx
```

### Next Steps
- Review the Excel file in `FY2024-2025/Processed/`
- Check logs in `FY2024-2025/Processed/Logs/`
- See [invoice_cataloger/README.md](invoice_cataloger/README.md) for details

---

## 2. Tax Report Generation

**Module**: `tax_report_generator/`  
**Purpose**: Generate consolidated tax reports with WFH calculations  
**Time**: 5 minutes

### Prerequisites
- ✅ Python 3.8+ installed
- ✅ WFH log file: `wfh/wfh_2024_2025.csv`
- ✅ Invoice catalog: `FY2024-2025/Processed/Invoice_Catalog_*.csv`

### Quick Setup

```bash
# 1. Install dependencies
cd "g:/My Drive/Tax Invoices"
pip install -r tax_report_generator/requirements.txt

# 2. Generate report
python generate_tax_report.py

# Or specify financial year
python generate_tax_report.py --financial-year 2024-2025
```

### Expected Output
```
✓ WFH log loaded: 245 days
✓ WFH percentage: 65.5%
✓ Invoice catalog loaded: 150 invoices
✓ Recalculated deductions
✓ Report saved: Tax_Report_2024-2025_20241215_143530.xlsx
```

### Next Steps
- Open the generated Excel file
- Review the Summary sheet
- Check WFH Analysis sheet
- See [tax_report_generator/README.md](tax_report_generator/README.md) for details

---

## 3. Bank Statement Processing

**Module**: `bankstatements/`  
**Purpose**: Extract and categorize bank transactions  
**Time**: 10 minutes

### Prerequisites
- ✅ Python 3.8+ installed
- ✅ Bank statement PDFs in `Statements/FY2024-2025/`

### Quick Setup (6-Step Workflow)

```bash
cd "g:/My Drive/Tax Invoices"

# Step 1: Prepare files (add zip_ prefix)
python bankstatements/prepare_files.py

# Step 2: Extract transactions from PDFs
python bankstatements/zip_money_extractor.py

# Step 3: Remove duplicates
python bankstatements/remove_duplicates.py

# Step 4: Categorize expenses
python bankstatements/run_cataloger.py

# Step 5: Fix categorization (optional)
python bankstatements/fix_categorization.py

# Step 6: Organize outputs by FY
python bankstatements/organize_outputs.py
```

### Expected Output
```
✓ Processed 24 statements
✓ Extracted 75 transactions
✓ Categorized into 9 categories
✓ Saved to: FY2024-2025/Processed/BankStatements/ZipMoney_20241215/
```

### Next Steps
- Review `expense_catalog.xlsx`
- Check category breakdowns
- See [bankstatements/README.md](bankstatements/README.md) for details

---

## 4. Gmail Invoice Extraction

**Module**: `google_scripts/`  
**Purpose**: Automatically extract invoice attachments from Gmail  
**Time**: 15 minutes

### Prerequisites
- ✅ Google Account with Gmail
- ✅ Invoice emails with attachments
- ✅ Google Apps Script access

### Quick Setup

1. **Open Google Apps Script**
   - Go to [script.google.com](https://script.google.com)
   - Click "New project"
   - Name it "Invoice Email Extractor"

2. **Add the Script**
   - Copy contents of `google_scripts/invoice_extract.gs`
   - Paste into script editor
   - Save (Ctrl+S)

3. **Configure Settings**
   ```javascript
   const CONFIG = {
     searchKeywords: ['invoice', 'receipt', 'tax invoice'],
     parentFolderName: 'Tax Invoices',
     maxEmailsPerRun: 50
   };
   ```

4. **Grant Permissions**
   - Click Run (▶️)
   - Review permissions
   - Allow access

5. **Test Extraction**
   - Select `testExtraction` function
   - Click Run
   - Check Google Drive for files

6. **Set Up Automation** (Optional)
   - Select `createAutomationTrigger`
   - Click Run
   - Script runs daily at 2 AM

### Expected Output
- Files in Google Drive: `Tax Invoices/FY2024-2025/`
- Log sheet: "Extracted Invoices Log"
- Summary email after each run

### Next Steps
- Check Google Drive folder structure
- Review extraction log
- See [google_scripts/Invoice-Email-Extractor-Guide.md](google_scripts/Invoice-Email-Extractor-Guide.md)

---

## 5. Work-From-Home Tracking

**Module**: `wfh/`  
**Purpose**: Automatically track work location based on IP address  
**Time**: 15 minutes

### Prerequisites
- ✅ Google Account
- ✅ Your home and office IP addresses
- ✅ Google Apps Script access

### Quick Setup

1. **Find Your IP Address**
   - Visit [whatismyipaddress.com](https://whatismyipaddress.com)
   - Note your IPv4 address

2. **Create Apps Script Project**
   - Go to [script.google.com](https://script.google.com)
   - Click "New project"
   - Name it "IP Location Tracker"

3. **Add Script Files**
   - Add `code.gs` from `wfh/code.gs`
   - Add HTML file: `IPLocationTracker.html`
   - Save both files

4. **Configure IP Addresses**
   ```javascript
   const CONFIG = {
     locations: {
       home: {
         name: 'Home',
         ipAddresses: ['YOUR_HOME_IP_HERE'],
         ispKeywords: ['SuperLoop', 'Telstra']
       },
       office: {
         name: 'Office',
         ipAddresses: ['YOUR_OFFICE_IP_HERE'],
         ispKeywords: ['CompanyName']
       }
     }
   };
   ```

5. **Set Up Spreadsheet**
   - Select `setupSpreadsheet` function
   - Click Run
   - Grant permissions

6. **Deploy Web App**
   - Click Deploy → New deployment
   - Choose Web app
   - Execute as: Me
   - Who has access: Only myself
   - Deploy and copy URL

7. **Test Detection**
   - Open web app URL
   - Click "Check My Location Now"
   - Verify location is correct

8. **Set Up Automation**
   - Select `createAutomaticTriggers`
   - Click Run
   - Checks at 9 AM, 12 PM, 3 PM on weekdays

### Expected Output
- Google Sheet: "Location Log"
- Color-coded entries (Green=Home, Blue=Office)
- Email notifications with check links

### Next Steps
- Bookmark web app URL
- Review location log
- See [wfh/IP-Location-Tracker-Guide.md](wfh/IP-Location-Tracker-Guide.md)

---

## 🔄 Complete Workflow (All Modules)

For comprehensive tax preparation, use modules in this order:

### Step 1: Extract Invoices from Gmail
```bash
# Run google_scripts module
# Extracts attachments to Google Drive
```

### Step 2: Process Invoices with AI
```bash
cd invoice_cataloger
python invoice_cataloger.py --financial-year 2024-2025
```

### Step 3: Process Bank Statements
```bash
# Run 6-step bankstatements workflow
python bankstatements/prepare_files.py
python bankstatements/zip_money_extractor.py
# ... (continue with remaining steps)
```

### Step 4: Track Work-From-Home Days
```bash
# Use wfh module throughout the year
# Generates wfh/wfh_2024_2025.csv
```

### Step 5: Generate Consolidated Tax Report
```bash
python generate_tax_report.py --financial-year 2024-2025
```

### Result
- ✅ All invoices cataloged and categorized
- ✅ Bank statements processed and matched
- ✅ WFH percentage calculated from actual data
- ✅ Deductions recalculated with accurate WFH %
- ✅ Comprehensive Excel report ready for accountant

---

## 🐛 Quick Troubleshooting

### "Cannot connect to LM Studio"
```bash
# 1. Open LM Studio
# 2. Load a model (Mistral 7B recommended)
# 3. Go to Developer tab
# 4. Click "Start Server"
# 5. Verify at http://localhost:1234/v1/models
```

### "Module not found" errors
```bash
# Install dependencies for specific module
pip install -r invoice_cataloger/requirements.txt
pip install -r tax_report_generator/requirements.txt
pip install -r bankstatements/requirements.txt
```

### "File not found" errors
```bash
# Check file paths in error message
# Verify financial year matches folder name
# Ensure files are in correct directory
```

### "Permission denied" (Google Scripts)
```bash
# 1. Run script manually first
# 2. Click "Review permissions"
# 3. Choose your account
# 4. Click "Advanced" → "Go to [script name]"
# 5. Click "Allow"
```

### "No text extracted from PDF"
```bash
# Install OCR libraries
pip install easyocr pytesseract pdf2image

# Or check if PDF is password-protected
```

---

## 📚 Additional Resources

### Documentation
- **[PREREQUISITES.md](PREREQUISITES.md)** - Complete requirements list
- **[MODULE_INDEX.md](MODULE_INDEX.md)** - All modules with parameters
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Detailed setup instructions

### Module-Specific Guides
- **[invoice_cataloger/README.md](invoice_cataloger/README.md)** - Invoice processing details
- **[tax_report_generator/README.md](tax_report_generator/README.md)** - Report generation
- **[bankstatements/README.md](bankstatements/README.md)** - Bank processing workflow
- **[google_scripts/Invoice-Email-Extractor-Guide.md](google_scripts/Invoice-Email-Extractor-Guide.md)** - Gmail automation
- **[wfh/IP-Location-Tracker-Guide.md](wfh/IP-Location-Tracker-Guide.md)** - Location tracking

### Configuration Guides
- **[invoice_cataloger/API_SETUP_GUIDE.md](invoice_cataloger/API_SETUP_GUIDE.md)** - LM Studio setup
- **[invoice_cataloger/VENDOR_OVERRIDES_GUIDE.md](invoice_cataloger/VENDOR_OVERRIDES_GUIDE.md)** - Custom vendor rules
- **[invoice_cataloger/WFH_LOG_GUIDE.md](invoice_cataloger/WFH_LOG_GUIDE.md)** - WFH log format
- **[invoice_cataloger/TAX_STRATEGY_GUIDE.md](invoice_cataloger/TAX_STRATEGY_GUIDE.md)** - Tax calculations

---

## 💡 Tips for Success

### First-Time Users
1. **Start with one module** - Don't try to set up everything at once
2. **Test with small datasets** - Process 5-10 files first
3. **Read error messages** - They usually tell you exactly what's wrong
4. **Check logs** - Most modules create detailed log files
5. **Verify prerequisites** - Use the verification steps in PREREQUISITES.md

### For Best Results
- **Keep files organized** by financial year
- **Run modules regularly** (monthly is ideal)
- **Backup your data** before processing
- **Review outputs** for accuracy
- **Update configurations** as needed

### Common Mistakes to Avoid
- ❌ Not starting LM Studio before invoice processing
- ❌ Wrong financial year in folder names
- ❌ Skipping dependency installation
- ❌ Not granting Google Script permissions
- ❌ Processing same files multiple times

---

## 🎯 Success Checklist

After completing quick start, you should have:

### Invoice Processing
- [ ] LM Studio running with model loaded
- [ ] Invoices processed and cataloged
- [ ] Excel file with categorized expenses
- [ ] Deduction calculations complete

### Tax Reporting
- [ ] WFH log file created/updated
- [ ] Invoice catalog loaded
- [ ] Consolidated report generated
- [ ] All sheets populated with data

### Bank Processing
- [ ] Statements extracted
- [ ] Transactions categorized
- [ ] Outputs organized by FY
- [ ] Cross-reference guide created

### Gmail Automation
- [ ] Script deployed and authorized
- [ ] Test extraction successful
- [ ] Files appearing in Google Drive
- [ ] Automation trigger set (optional)

### WFH Tracking
- [ ] IP addresses configured
- [ ] Web app deployed
- [ ] Location detection working
- [ ] Log sheet created

---

## 🚀 Next Steps

Once you've completed the quick start:

1. **Explore Advanced Features**
   - Custom categorization rules
   - Vendor overrides
   - Tax strategy customization
   - Batch processing

2. **Set Up Automation**
   - Daily Gmail extraction
   - Automated WFH tracking
   - Scheduled report generation

3. **Integrate Modules**
   - Use outputs from one module as inputs to another
   - Create end-to-end workflows
   - Generate comprehensive reports

4. **Customize for Your Needs**
   - Adjust work-from-home percentages
   - Add custom expense categories
   - Modify report formats
   - Configure email notifications

---

## 📞 Getting Help

If you get stuck:

1. **Check module README** - Most questions answered there
2. **Review error messages** - They're usually specific
3. **Verify prerequisites** - Missing dependencies cause most issues
4. **Check logs** - Detailed information in log files
5. **Test components** - Use test functions to isolate issues

**Common Help Resources:**
- Module README files
- Configuration guides
- Troubleshooting sections
- Example files in `examples/` folders

---

**Ready to dive deeper?** See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for comprehensive setup instructions.

**Need module details?** Check [MODULE_INDEX.md](MODULE_INDEX.md) for complete parameter documentation.

---

*Last Updated: December 2024*  
*Version: 1.0*
