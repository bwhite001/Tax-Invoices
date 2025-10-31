# Module Index & Complete Documentation

Complete reference for all modules in the Australian Tax Invoice Processing System.

---

## 📋 Table of Contents

- [Module Overview](#module-overview)
- [Module 1: invoice_cataloger](#module-1-invoice_cataloger)
- [Module 2: tax_report_generator](#module-2-tax_report_generator)
- [Module 3: bankstatements](#module-3-bankstatements)
- [Module 4: google_scripts](#module-4-google_scripts)
- [Module 5: wfh](#module-5-wfh)
- [Module Interaction](#module-interaction)
- [Common Parameters](#common-parameters)

---

## 🎯 Module Overview

| Module | Purpose | Language | Dependencies | Input | Output |
|--------|---------|----------|--------------|-------|--------|
| **invoice_cataloger** | AI invoice processing | Python | LM Studio, OCR | PDF, images, docs | Excel, CSV |
| **tax_report_generator** | Tax report generation | Python | pandas, openpyxl | Invoice catalog, WFH log | Excel report |
| **bankstatements** | Bank processing | Python | pandas, pdfplumber | PDF statements | Excel, CSV |
| **google_scripts** | Gmail extraction | JavaScript | Google Account | Gmail emails | Google Drive files |
| **wfh** | Location tracking | JavaScript | Google Account | IP address | Google Sheets log |

---

## Module 1: invoice_cataloger

### Purpose
AI-powered invoice data extraction, categorization, and ATO-compliant deduction calculation.

### Location
`invoice_cataloger/`

### Main Script
`invoice_cataloger.py`

### Configuration File
`invoice_cataloger/config.py`

### Parameters

#### LM Studio Configuration
```python
lm_studio_endpoint: str = "http://localhost:1234/v1/chat/completions"
```
- **Type**: String (URL)
- **Default**: `"http://localhost:1234/v1/chat/completions"`
- **Description**: LM Studio API endpoint
- **Example**: `"http://192.168.1.100:1234/v1/chat/completions"` (remote server)
- **Required**: Yes

```python
lm_studio_model: str = "mistral-7b-instruct"
```
- **Type**: String
- **Default**: `"mistral-7b-instruct"`
- **Description**: Model name to use
- **Options**: Any model loaded in LM Studio
- **Required**: No (uses default model if not specified)

```python
lm_studio_timeout: int = 120
```
- **Type**: Integer (seconds)
- **Default**: `120`
- **Description**: API request timeout
- **Range**: 30-300 seconds
- **Required**: No

#### Financial Year Configuration
```python
financial_year: str = "2024-2025"
```
- **Type**: String (YYYY-YYYY format)
- **Default**: `"2024-2025"`
- **Description**: Australian financial year (July 1 - June 30)
- **Example**: `"2023-2024"`, `"2025-2026"`
- **Required**: Yes

#### Work From Home Configuration
```python
work_from_home_days: int = 3
```
- **Type**: Integer
- **Default**: `3`
- **Description**: Number of days per week working from home
- **Range**: 0-7
- **Required**: Yes

```python
total_work_days: int = 5
```
- **Type**: Integer
- **Default**: `5`
- **Description**: Total working days per week
- **Range**: 1-7
- **Required**: Yes

```python
work_use_percentage: int = 60
```
- **Type**: Integer (percentage)
- **Default**: `60` (calculated as work_from_home_days / total_work_days * 100)
- **Description**: Percentage of work use for shared expenses
- **Range**: 0-100
- **Required**: Yes

#### Path Configuration
```python
base_path: Path = Path("G:/My Drive/Tax Invoices")
```
- **Type**: Path object
- **Default**: `Path("G:/My Drive/Tax Invoices")`
- **Description**: Base directory for all tax files
- **Required**: Yes

```python
invoice_folder: Path = base_path / f"FY{financial_year}"
```
- **Type**: Path object
- **Default**: Calculated from base_path and financial_year
- **Description**: Folder containing invoice files
- **Required**: Yes (auto-calculated)

```python
output_folder: Path = invoice_folder / "Processed"
```
- **Type**: Path object
- **Default**: Calculated from invoice_folder
- **Description**: Output folder for processed files
- **Required**: Yes (auto-created)

```python
log_folder: Path = output_folder / "Logs"
```
- **Type**: Path object
- **Default**: Calculated from output_folder
- **Description**: Folder for processing logs
- **Required**: Yes (auto-created)

#### OCR Configuration
```python
use_easyocr: bool = True
```
- **Type**: Boolean
- **Default**: `True`
- **Description**: Enable EasyOCR for text extraction
- **Required**: No

```python
use_tesseract: bool = True
```
- **Type**: Boolean
- **Default**: `True`
- **Description**: Enable Tesseract OCR
- **Required**: No

```python
tesseract_path: str = "C:/Program Files/Tesseract-OCR/tesseract.exe"
```
- **Type**: String (file path)
- **Default**: `"C:/Program Files/Tesseract-OCR/tesseract.exe"` (Windows)
- **Description**: Path to Tesseract executable
- **Required**: Only if use_tesseract is True
- **Platform-specific**:
  - Windows: `"C:/Program Files/Tesseract-OCR/tesseract.exe"`
  - macOS: `"/usr/local/bin/tesseract"`
  - Linux: `"/usr/bin/tesseract"`

#### Processing Configuration
```python
max_retries: int = 3
```
- **Type**: Integer
- **Default**: `3`
- **Description**: Maximum retry attempts for failed files
- **Range**: 0-10
- **Required**: No

```python
use_cache: bool = True
```
- **Type**: Boolean
- **Default**: `True`
- **Description**: Enable caching to avoid reprocessing
- **Required**: No

```python
cache_file: str = "cache.json"
```
- **Type**: String (filename)
- **Default**: `"cache.json"`
- **Description**: Cache file name
- **Required**: No

### Command Line Arguments

```bash
python invoice_cataloger.py [OPTIONS]
```

**Options:**
- `--financial-year YYYY-YYYY` - Specify financial year (default: 2024-2025)
- `--retry-failed` - Process only previously failed files
- `--check-only` - Check prerequisites without processing
- `--verbose` - Enable debug logging
- `--reprocess` - Reprocess all files (ignore cache)

**Examples:**
```bash
# Process current year
python invoice_cataloger.py --financial-year 2024-2025

# Retry failed files
python invoice_cataloger.py --financial-year 2024-2025 --retry-failed

# Check setup
python invoice_cataloger.py --check-only

# Verbose mode
python invoice_cataloger.py --financial-year 2024-2025 --verbose
```

### Input Files
- **Location**: `FY{year}/` folder
- **Formats**: PDF, PNG, JPG, JPEG, GIF, DOC, DOCX, XLS, XLSX, EML, MSG
- **Structure**: Flat or nested folders (recursive search)

### Output Files
- **Location**: `FY{year}/Processed/`
- **Files**:
  - `Invoice_Catalog_{timestamp}.xlsx` - Main Excel catalog
  - `Invoice_Catalog_{timestamp}.csv` - Detailed CSV
  - `Deduction_Summary_{timestamp}.csv` - Category summary
  - `cache.json` - Processing cache
  - `failed_files.json` - Failed files list
  - `Logs/processing_{date}.log` - Processing log

### Dependencies
```
pandas>=1.5.0
openpyxl>=3.0.0
requests>=2.28.0
python-dotenv>=0.20.0
PyMuPDF>=1.21.0
pdfplumber>=0.7.0
pypdf>=3.0.0
python-docx>=0.8.11
extract-msg>=0.41.0
easyocr>=1.6.0 (optional)
pytesseract>=0.3.10 (optional)
pdf2image>=1.16.0 (optional)
```

---

## Module 2: tax_report_generator

### Purpose
Generate consolidated tax reports with WFH calculations and bank statement integration.

### Location
`tax_report_generator/`

### Main Script
`generate_tax_report.py` (wrapper)  
`tax_report_generator/main.py` (core)

### Configuration File
`tax_report_generator/config.py`

### Parameters

#### Financial Year Configuration
```python
financial_year: str = "2024-2025"
```
- **Type**: String (YYYY-YYYY format)
- **Default**: `"2024-2025"`
- **Description**: Australian financial year
- **Required**: Yes

#### Path Configuration
```python
base_dir: Path = Path.cwd()
```
- **Type**: Path object
- **Default**: Current working directory
- **Description**: Base directory (auto-detected)
- **Required**: Yes (auto-detected)

```python
wfh_log: Path = base_dir / "wfh" / f"wfh_{financial_year.replace('-', '_')}.csv"
```
- **Type**: Path object
- **Default**: `wfh/wfh_2024_2025.csv`
- **Description**: WFH log file path
- **Required**: Yes

```python
invoice_catalog: Path = base_dir / f"FY{financial_year}" / "Processed" / "Invoice_Catalog_*.csv"
```
- **Type**: Path pattern
- **Default**: Latest Invoice_Catalog CSV in Processed folder
- **Description**: Invoice catalog file (uses most recent)
- **Required**: Yes

```python
bank_statements_dir: Path = base_dir / f"FY{financial_year}" / "Processed" / "BankStatements"
```
- **Type**: Path object
- **Default**: `FY{year}/Processed/BankStatements/`
- **Description**: Bank statements directory
- **Required**: No (optional)

#### Tax Parameters
```python
wfh_categories: List[str] = [
    'Electricity',
    'Internet',
    'Phone',
    'Office Supplies',
    'Mobile/Communication'
]
```
- **Type**: List of strings
- **Default**: 5 categories
- **Description**: Expense categories affected by WFH percentage
- **Required**: Yes

```python
exclude_locations: List[str] = ['Leave', 'Sick', 'Holiday']
```
- **Type**: List of strings
- **Default**: `['Leave', 'Sick', 'Holiday']`
- **Description**: Locations to exclude from WFH calculation
- **Required**: No

```python
fixed_rate_per_hour: float = 0.70
```
- **Type**: Float (dollars)
- **Default**: `0.70`
- **Description**: ATO fixed rate per hour (2024-25)
- **Required**: No (for reference only)

### Command Line Arguments

```bash
python generate_tax_report.py [OPTIONS]
```

**Options:**
- `--financial-year YYYY-YYYY` - Specify financial year
- `--base-dir PATH` - Specify base directory
- `--verbose` - Enable debug logging

**Examples:**
```bash
# Generate report for current year
python generate_tax_report.py

# Specify financial year
python generate_tax_report.py --financial-year 2023-2024

# Custom base directory
python generate_tax_report.py --base-dir "C:/Tax Documents"

# Verbose mode
python generate_tax_report.py --verbose
```

### Input Files
- **WFH Log**: `wfh/wfh_{year}.csv`
  - Format: CSV with Date, Location columns
  - Example: `2024-07-01,Home`
- **Invoice Catalog**: `FY{year}/Processed/Invoice_Catalog_*.csv`
  - Latest catalog from invoice_cataloger
- **Bank Statements**: `FY{year}/Processed/BankStatements/` (optional)
  - From bankstatements module

### Output Files
- **Location**: Current directory
- **File**: `Tax_Report_{year}_{timestamp}.xlsx`
- **Sheets**:
  - Summary - Overview with totals
  - Invoice Catalog - All invoices with recalculated deductions
  - Category Breakdown - Expenses by category
  - WFH Analysis - Daily and monthly WFH data
  - Bank Statements - Bank transactions (if available)
  - Monthly Summary - Month-by-month breakdown

### Dependencies
```
pandas>=1.5.0
openpyxl>=3.0.0
```

---

## Module 3: bankstatements

### Purpose
Extract and categorize bank statement transactions.

### Location
`bankstatements/`

### Main Scripts
1. `prepare_files.py` - Add zip_ prefix
2. `zip_money_extractor.py` - Extract transactions
3. `remove_duplicates.py` - Remove duplicates
4. `run_cataloger.py` - Categorize expenses
5. `fix_categorization.py` - Fix categories
6. `organize_outputs.py` - Organize by FY

### Configuration

#### In prepare_files.py
```python
source_dir: str = "Statements/FY2024-2025"
```
- **Type**: String (directory path)
- **Default**: `"Statements/FY2024-2025"`
- **Description**: Source directory for bank statements
- **Required**: Yes (update for each FY)

```python
temp_dir: str = "temp_processing"
```
- **Type**: String (directory path)
- **Default**: `"temp_processing"`
- **Description**: Temporary processing directory
- **Required**: Yes

#### In organize_outputs.py
```python
fy_dir: str = "FY2024-2025"
```
- **Type**: String (directory path)
- **Default**: `"FY2024-2025"`
- **Description**: Financial year directory
- **Required**: Yes (update for each FY)

```python
output_base: str = "Processed/BankStatements"
```
- **Type**: String (directory path)
- **Default**: `"Processed/BankStatements"`
- **Description**: Output base directory
- **Required**: Yes

#### In expense_cataloger.py
```python
CATEGORIES: Dict[str, List[str]] = {
    'Shopping': ['amazon', 'temu', 'ebay', ...],
    'Dining': ['restaurant', 'cafe', 'mcdonald', ...],
    'Entertainment': ['steam', 'netflix', 'spotify', ...],
    # ... more categories
}
```
- **Type**: Dictionary of category names to keyword lists
- **Default**: 9 predefined categories
- **Description**: Categorization rules
- **Required**: Yes (customizable)

### Workflow

```bash
# Step 1: Prepare files
python bankstatements/prepare_files.py

# Step 2: Extract transactions
python bankstatements/zip_money_extractor.py

# Step 3: Remove duplicates
python bankstatements/remove_duplicates.py

# Step 4: Categorize
python bankstatements/run_cataloger.py

# Step 5: Fix categories (optional)
python bankstatements/fix_categorization.py

# Step 6: Organize outputs
python bankstatements/organize_outputs.py
```

### Input Files
- **Location**: `Statements/FY{year}/`
- **Format**: PDF bank statements
- **Naming**: Any (numbered or monthly)
- **Bank**: Zip Money (custom parser)

### Output Files
- **Location**: `FY{year}/Processed/BankStatements/ZipMoney_{timestamp}/`
- **Files** (17 total):
  - `expense_catalog.xlsx` - Main catalog
  - `expense_catalog.csv` - Detailed CSV
  - `monthly_expenses_by_category.csv` - Monthly breakdown
  - `category_*.csv` - 9 category files
  - `PROCESSING_SUMMARY.md` - Processing report
  - `CROSS_REFERENCE_MAPPING.md` - Invoice matching guide

### Dependencies
```
pandas>=1.5.0
openpyxl>=3.0.0
pdfplumber>=0.7.0
PyPDF2>=3.0.0
tabula-py>=2.5.0 (optional, requires Java)
```

---

## Module 4: google_scripts

### Purpose
Automatically extract invoice attachments from Gmail.

### Location
`google_scripts/`

### Main Script
`invoice_extract.gs` (Google Apps Script)

### Configuration

```javascript
const CONFIG = {
  searchKeywords: ['invoice', 'receipt', 'tax invoice', 'bill', 'payment', 'statement'],
  parentFolderName: 'Tax Invoices',
  processedLabelName: 'Invoices-Extracted',
  maxEmailsPerRun: 50,
  allowedFileTypes: ['pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'eml'],
  spreadsheetName: 'Extracted Invoices Log',
  fyLabelPrefix: 'Tax FY'
};
```

#### Parameters

```javascript
searchKeywords: string[]
```
- **Type**: Array of strings
- **Default**: `['invoice', 'receipt', 'tax invoice', 'bill', 'payment', 'statement']`
- **Description**: Keywords to search in email subject/body
- **Required**: Yes

```javascript
parentFolderName: string
```
- **Type**: String
- **Default**: `'Tax Invoices'`
- **Description**: Main folder name in Google Drive
- **Required**: Yes

```javascript
processedLabelName: string
```
- **Type**: String
- **Default**: `'Invoices-Extracted'`
- **Description**: Gmail label for processed emails
- **Required**: Yes

```javascript
maxEmailsPerRun: number
```
- **Type**: Integer
- **Default**: `50`
- **Description**: Maximum emails to process per run
- **Range**: 1-500
- **Required**: Yes

```javascript
allowedFileTypes: string[]
```
- **Type**: Array of strings
- **Default**: `['pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'eml']`
- **Description**: File extensions to extract
- **Required**: Yes

### Functions

- `extractInvoiceAttachments()` - Main extraction function
- `testExtraction()` - Test with 5 emails
- `createAutomationTrigger()` - Set up daily automation
- `deleteAllTriggers()` - Remove all triggers

### Input
- Gmail emails with attachments
- Emails matching search keywords
- From most recent tax period

### Output
- **Google Drive**: `Tax Invoices/FY{year}/` folders
- **Files**: Renamed as `YYYY-MM-DD_sender@email.com_filename.ext`
- **Log**: "Extracted Invoices Log" spreadsheet

### Dependencies
- Google Account
- Gmail access
- Google Drive access
- Google Sheets access
- Google Apps Script permissions

---

## Module 5: wfh

### Purpose
Track work location based on IP address for WFH compliance.

### Location
`wfh/`

### Main Scripts
- `code.gs` - Google Apps Script
- `IPLocationTracker.html` - Web app interface

### Configuration

```javascript
const CONFIG = {
  locations: {
    home: {
      name: 'Home',
      ipAddresses: ['YOUR_HOME_IP_HERE'],
      ispKeywords: ['SuperLoop', 'Telstra', 'Optus']
    },
    office: {
      name: 'Office',
      ipAddresses: ['YOUR_OFFICE_IP_HERE'],
      ispKeywords: ['CompanyName', 'Office']
    }
  },
  businessHours: {
    startHour: 9,
    endHour: 17,
    daysOfWeek: [1, 2, 3, 4, 5]
  },
  checkInterval: 3,
  sheetName: 'Location Log',
  timezone: 'Australia/Sydney',
  geoApiService: 'ip-api'
};
```

#### Parameters

```javascript
locations.home.ipAddresses: string[]
```
- **Type**: Array of strings (IP addresses)
- **Default**: `['YOUR_HOME_IP_HERE']` (must configure)
- **Description**: Home IP addresses (exact or partial)
- **Example**: `['203.123.45.67']` or `['203.123.45']` (range)
- **Required**: Yes

```javascript
locations.home.ispKeywords: string[]
```
- **Type**: Array of strings
- **Default**: `['SuperLoop', 'Telstra', 'Optus']`
- **Description**: ISP keywords for fallback matching
- **Required**: No

```javascript
locations.office.ipAddresses: string[]
```
- **Type**: Array of strings (IP addresses)
- **Default**: `['YOUR_OFFICE_IP_HERE']` (must configure)
- **Description**: Office IP addresses
- **Required**: Yes

```javascript
businessHours.startHour: number
```
- **Type**: Integer (0-23)
- **Default**: `9`
- **Description**: Business hours start (24-hour format)
- **Required**: Yes

```javascript
businessHours.endHour: number
```
- **Type**: Integer (0-23)
- **Default**: `17`
- **Description**: Business hours end (24-hour format)
- **Required**: Yes

```javascript
businessHours.daysOfWeek: number[]
```
- **Type**: Array of integers (0-6, 0=Sunday)
- **Default**: `[1, 2, 3, 4, 5]` (Mon-Fri)
- **Description**: Working days
- **Required**: Yes

```javascript
checkInterval: number
```
- **Type**: Integer (hours)
- **Default**: `3`
- **Description**: Hours between automated checks
- **Range**: 1-8
- **Required**: Yes

```javascript
timezone: string
```
- **Type**: String
- **Default**: `'Australia/Sydney'`
- **Description**: Timezone for logging
- **Options**: Any valid timezone (Australia/Sydney, Australia/Brisbane, etc.)
- **Required**: Yes

### Functions

- `setupSpreadsheet()` - Create location log sheet
- `testGetMyIP()` - Test IP detection
- `handleAutomaticLocationCheck()` - Manual location check
- `createAutomaticTriggers()` - Set up automation
- `getLocationStatistics()` - View statistics

### Input
- Your IP address (automatic detection)
- Configured IP addresses and ISP keywords

### Output
- **Google Sheets**: "Location Log"
- **Columns**: Timestamp, Date, Time, Day, Location, IP, ISP, City, Region
- **Color Coding**: Green (Home), Blue (Office), Yellow (Unknown)
- **CSV Export**: For use in tax_report_generator

### Dependencies
- Google Account
- Google Sheets access
- Google Apps Script permissions
- IP geolocation API (free, no key required)

---

## 🔄 Module Interaction

### Data Flow

```
Gmail Emails
    ↓
google_scripts (extracts attachments)
    ↓
Google Drive → Local Files
    ↓
invoice_cataloger (processes invoices)
    ↓
Invoice_Catalog.csv
    ↓         ↘
    ↓          Bank Statements → bankstatements
    ↓                                ↓
    ↓                         expense_catalog.csv
    ↓                                ↓
    ↓         ↙──────────────────────┘
    ↓         ↓
    ↓    WFH Log ← wfh (tracks location)
    ↓         ↓
    └─────────┴──→ tax_report_generator
                        ↓
                Tax_Report.xlsx
```

### Integration Points

1. **google_scripts → invoice_cataloger**
   - Output: Files in Google Drive
   - Input: Files in FY folders

2. **invoice_cataloger → tax_report_generator**
   - Output: Invoice_Catalog.csv
   - Input: Invoice catalog for recalculation

3. **bankstatements → tax_report_generator**
   - Output: expense_catalog.csv
   - Input: Bank transactions for integration

4. **wfh → tax_report_generator**
   - Output: wfh_{year}.csv
   - Input: WFH log for percentage calculation

5. **tax_report_generator → Accountant**
   - Output: Consolidated Excel report
   - Use: Tax return preparation

---

## 🔧 Common Parameters

### Financial Year Format
- **Format**: `"YYYY-YYYY"`
- **Example**: `"2024-2025"`
- **Period**: July 1 to June 30 (Australian FY)

### File Paths
- **Base**: `G:/My Drive/Tax Invoices`
- **FY Folders**: `FY2024-2025/`
- **Processed**: `FY2024-2025/Processed/`
- **Logs**: `FY2024-2025/Processed/Logs/`

### Date Formats
- **CSV**: `YYYY-MM-DD` (e.g., `2024-07-01`)
- **Display**: `DD/MM/YYYY` (e.g., `01/07/2024`)
- **Timestamps**: `YYYYMMDD_HHMMSS` (e.g., `20241215_143022`)

### Categories
Standard expense categories across modules:
- Electricity
- Internet
- Phone
- Software & Subscriptions
- Computer Equipment
- Professional Development
- Professional Membership
- Office Supplies
- Mobile/Communication
- Shopping
- Dining
- Entertainment
- Transport
- Utilities
- Banking
- Income
- Transfer
- Other

---

## 📚 Additional Resources

### Module-Specific Documentation
- [invoice_cataloger/README.md](invoice_cataloger/README.md)
- [tax_report_generator/README.md](tax_report_generator/README.md)
- [bankstatements/README.md](bankstatements/README.md)
- [google_scripts/Invoice-Email-Extractor-Guide.md](google_scripts/Invoice-Email-Extractor-Guide.md)
- [wfh/IP-Location-Tracker-Guide.md](wfh/IP-Location-Tracker-Guide.md)

### Configuration Guides
- [invoice_cataloger/API_SETUP_GUIDE.md](invoice_cataloger/API_SETUP_GUIDE.md)
- [invoice_cataloger/VENDOR_OVERRIDES_GUIDE.md](invoice_cataloger/VENDOR_OVERRIDES_GUIDE.md)
- [invoice_cataloger/WFH_LOG_GUIDE.md](invoice_cataloger/WFH_LOG_GUIDE.md)
- [invoice_cataloger/TAX_STRATEGY_GUIDE.md](invoice_cataloger/TAX_STRATEGY_GUIDE.md)

---

*Last Updated: December 2024*  
*Version: 1.0*
