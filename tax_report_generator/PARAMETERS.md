# tax_report_generator - Parameters Reference

Complete parameter documentation for the tax_report_generator module.

---

## 📋 Table of Contents

- [Configuration File](#configuration-file)
- [Financial Year Parameters](#financial-year-parameters)
- [Path Parameters](#path-parameters)
- [Tax Parameters](#tax-parameters)
- [WFH Calculation Parameters](#wfh-calculation-parameters)
- [Command Line Arguments](#command-line-arguments)
- [Examples](#examples)

---

## 📁 Configuration File

**Location**: `tax_report_generator/config.py`

All parameters are defined in the `Config` class and `TaxParameters` class.

---

## 📅 Financial Year Parameters

### financial_year

```python
financial_year: str = "2024-2025"
```

- **Type**: String (YYYY-YYYY format)
- **Default**: `"2024-2025"`
- **Description**: Australian financial year (July 1 - June 30)
- **Required**: Yes
- **Format**: Must be `"YYYY-YYYY"` where second year = first year + 1
- **Examples**:
  - Current: `"2024-2025"`
  - Previous: `"2023-2024"`
  - Next: `"2025-2026"`

**When to change**:
- Processing different financial year
- Generating historical reports
- Year-end processing

---

## 📂 Path Parameters

### base_dir

```python
base_dir: Path = Path.cwd()
```

- **Type**: Path object
- **Default**: Current working directory (auto-detected)
- **Description**: Base directory for all files
- **Required**: Yes (auto-detected)
- **Examples**:
  - Auto: `Path.cwd()` (recommended)
  - Manual: `Path("G:/My Drive/Tax Invoices")`
  - Custom: `Path("C:/Tax Documents")`

**When to change**:
- Custom directory structure
- Running from different location
- Usually auto-detected, rarely needs manual change

### wfh_log

```python
wfh_log: Path = base_dir / "wfh" / f"wfh_{financial_year.replace('-', '_')}.csv"
```

- **Type**: Path object
- **Default**: `wfh/wfh_2024_2025.csv`
- **Description**: WFH log file path
- **Required**: Yes
- **Format**: CSV with Date, Location columns
- **Example**: `G:/My Drive/Tax Invoices/wfh/wfh_2024_2025.csv`

**When to change**:
- Custom WFH log location
- Different file naming
- Multiple WFH logs

**File Format**:
```csv
Date,Location
2024-07-01,Home
2024-07-02,Office
2024-07-03,Home
```

### invoice_catalog

```python
invoice_catalog: Path = base_dir / f"FY{financial_year}" / "Processed" / "Invoice_Catalog_*.csv"
```

- **Type**: Path pattern
- **Default**: Latest Invoice_Catalog CSV in Processed folder
- **Description**: Invoice catalog file from invoice_cataloger
- **Required**: Yes
- **Pattern**: Uses glob pattern to find latest file
- **Example**: `FY2024-2025/Processed/Invoice_Catalog_20241215_143022.csv`

**When to change**:
- Custom catalog location
- Specific catalog file
- Different naming convention

**Behavior**:
- Automatically finds most recent catalog
- Uses timestamp in filename
- Falls back to any matching file

### deduction_summary

```python
deduction_summary: Path = base_dir / f"FY{financial_year}" / "Processed" / "Deduction_Summary_*.csv"
```

- **Type**: Path pattern
- **Default**: Latest Deduction_Summary CSV
- **Description**: Deduction summary file (optional)
- **Required**: No
- **Example**: `FY2024-2025/Processed/Deduction_Summary_20241215_143022.csv`

**When to change**:
- Custom summary location
- Specific summary file
- Usually auto-detected

### bank_statements_dir

```python
bank_statements_dir: Path = base_dir / f"FY{financial_year}" / "Processed" / "BankStatements"
```

- **Type**: Path object
- **Default**: `FY{year}/Processed/BankStatements/`
- **Description**: Bank statements directory (optional)
- **Required**: No
- **Example**: `FY2024-2025/Processed/BankStatements/ZipMoney_20241215/`

**When to change**:
- Custom bank statements location
- Different directory structure
- Multiple bank statement sources

**Behavior**:
- Searches for expense_catalog.csv in subdirectories
- Integrates if found
- Skips if not available

---

## 💰 Tax Parameters

### wfh_categories

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

**When to change**:
- Add custom categories
- Remove categories
- ATO guideline changes

**Categories Explained**:
- **Electricity**: Power bills for home office
- **Internet**: Home internet connection
- **Phone**: Mobile phone bills
- **Office Supplies**: Stationery, printer ink, etc.
- **Mobile/Communication**: VoIP, video conferencing

**NOT Affected by WFH %**:
- Professional Development (100% deductible)
- Professional Membership (100% deductible)
- Computer Equipment (depreciation rules apply)
- Software & Subscriptions (depreciation rules apply)

### exclude_locations

```python
exclude_locations: List[str] = ['Leave', 'Sick', 'Holiday']
```

- **Type**: List of strings
- **Default**: `['Leave', 'Sick', 'Holiday']`
- **Description**: Locations to exclude from WFH calculation
- **Required**: No

**When to change**:
- Add custom exclusions
- Different leave types
- Company-specific locations

**Examples**:
```python
# Standard
exclude_locations = ['Leave', 'Sick', 'Holiday']

# Extended
exclude_locations = ['Leave', 'Sick', 'Holiday', 'Training', 'Conference']

# Minimal
exclude_locations = ['Leave']
```

**Behavior**:
- Excluded days not counted in total work days
- Excluded days not counted as WFH or office
- Improves accuracy of WFH percentage

### fixed_rate_per_hour

```python
fixed_rate_per_hour: float = 0.70
```

- **Type**: Float (dollars)
- **Default**: `0.70`
- **Description**: ATO fixed rate per hour (2024-25)
- **Required**: No (for reference only)
- **ATO Rate**: $0.70 per hour for 2024-25 financial year

**When to change**:
- ATO rate changes
- Different financial year
- Reference purposes only

**Note**: This parameter is for reference. The system uses Actual Cost Method, not Fixed Rate Method.

---

## 🏠 WFH Calculation Parameters

### WFH Percentage Calculation

The system calculates WFH percentage from the WFH log:

```python
wfh_percentage = (wfh_days / total_work_days) * 100
```

**Where**:
- `wfh_days` = Days with Location = "Home"
- `total_work_days` = All work days (excluding excluded locations)

**Example**:
```
Total days in log: 250
Excluded days (Leave, Sick): 15
Work days: 235
WFH days (Home): 154
Office days (Office): 81

WFH % = (154 / 235) * 100 = 65.5%
```

### Deduction Recalculation

For WFH categories, deductions are recalculated:

```python
new_deduction = invoice_total * (wfh_percentage / 100)
```

**Example**:
```
Invoice: Electricity bill
Total: $150.00
Original deduction (60%): $90.00
Calculated WFH %: 65.5%
New deduction: $150.00 * 0.655 = $98.25
Adjustment: +$8.25
```

---

## 💻 Command Line Arguments

Override config file parameters via command line:

### --financial-year

```bash
python generate_tax_report.py --financial-year 2023-2024
```

- **Type**: String (YYYY-YYYY)
- **Default**: From config.py
- **Description**: Specify financial year
- **Example**: `--financial-year 2024-2025`

### --base-dir

```bash
python generate_tax_report.py --base-dir "C:/Tax Documents"
```

- **Type**: String (directory path)
- **Default**: Current working directory
- **Description**: Specify base directory
- **Example**: `--base-dir "G:/My Drive/Tax Invoices"`

### --verbose

```bash
python generate_tax_report.py --verbose
```

- **Type**: Flag (no value)
- **Default**: False
- **Description**: Enable debug logging
- **Use case**: Troubleshooting, detailed output

---

## 📝 Examples

### Example 1: Standard Configuration

```python
# config.py
financial_year = "2024-2025"
wfh_categories = [
    'Electricity',
    'Internet',
    'Phone',
    'Office Supplies',
    'Mobile/Communication'
]
exclude_locations = ['Leave', 'Sick', 'Holiday']
```

**Use case**: Standard setup with default categories

### Example 2: Custom WFH Categories

```python
# config.py
wfh_categories = [
    'Electricity',
    'Internet',
    'Phone',
    'Office Supplies',
    'Mobile/Communication',
    'Heating/Cooling',  # Added
    'Water'             # Added
]
```

**Use case**: Additional home office expenses

### Example 3: Minimal Exclusions

```python
# config.py
exclude_locations = ['Leave']  # Only exclude leave
```

**Use case**: Count sick days as work days

### Example 4: Custom Paths

```python
# config.py
base_dir = Path("C:/Tax Documents")
wfh_log = base_dir / "logs" / f"wfh_{financial_year}.csv"
```

**Use case**: Custom directory structure

### Example 5: Command Line Override

```bash
# Process different year
python generate_tax_report.py --financial-year 2023-2024

# Custom base directory
python generate_tax_report.py --base-dir "C:/Tax Documents"

# Verbose output
python generate_tax_report.py --verbose

# Combined
python generate_tax_report.py --financial-year 2024-2025 --base-dir "C:/Tax" --verbose
```

**Use case**: Temporary parameter changes

### Example 6: Programmatic Usage

```python
from tax_report_generator.main import TaxReportGenerator
from tax_report_generator.config import Config

# Create custom config
config = Config(financial_year="2024-2025")
config.tax_params.wfh_categories.append('Custom Category')
config.tax_params.exclude_locations = ['Leave', 'Sick', 'Holiday', 'Training']

# Create generator with custom config
generator = TaxReportGenerator(
    financial_year=config.financial_year,
    base_dir=config.base_dir
)

# Run generation
report_path = generator.run()
```

**Use case**: Programmatic control, custom configurations

---

## 🔧 Parameter Validation

The system validates parameters on startup:

### Financial Year Validation

```python
# Valid
"2024-2025"  ✓
"2023-2024"  ✓

# Invalid
"2024-25"    ✗ Must be full year
"24-25"      ✗ Must be full year
"2024/2025"  ✗ Must use hyphen
```

### Path Validation

```python
# Valid
Path("G:/My Drive/Tax Invoices")  ✓
Path.cwd()                         ✓

# Warning
Path("/nonexistent/path")          ⚠️ Warning if doesn't exist
```

### WFH Log Validation

```python
# Valid CSV format
Date,Location
2024-07-01,Home     ✓
2024-07-02,Office   ✓

# Invalid
Date,Location
01/07/2024,Home     ✗ Wrong date format
2024-07-01,home     ⚠️ Case-sensitive (should be "Home")
```

### Category Validation

```python
# Valid
wfh_categories = ['Electricity', 'Internet']  ✓

# Warning
wfh_categories = []  ⚠️ Empty list, no recalculation
```

---

## 📊 Output Configuration

### Report Filename

```python
report_filename = f"Tax_Report_{financial_year}_{timestamp}.xlsx"
```

- **Format**: `Tax_Report_YYYY-YYYY_YYYYMMDD_HHMMSS.xlsx`
- **Example**: `Tax_Report_2024-2025_20241215_143530.xlsx`
- **Location**: Current directory

### Report Sheets

The generated Excel file contains:

1. **Summary** - Overview with totals
2. **Invoice Catalog** - All invoices with recalculated deductions
3. **Category Breakdown** - Expenses by category
4. **WFH Analysis** - Daily and monthly WFH data
5. **Bank Statements** - Bank transactions (if available)
6. **Monthly Summary** - Month-by-month breakdown

**Configuration**: Sheet names and structure are fixed

---

## 🔄 Data Flow

```
WFH Log (CSV)
    ↓
Calculate WFH %
    ↓
Invoice Catalog (CSV)
    ↓
Recalculate Deductions
    ↓
Bank Statements (CSV) [optional]
    ↓
Generate Report (XLSX)
```

---

## 📚 Related Documentation

- **[README.md](README.md)** - Module overview
- **[../QUICKSTART.md](../QUICKSTART.md)** - Quick start guide
- **[../MODULE_INDEX.md](../MODULE_INDEX.md)** - All modules
- **[../invoice_cataloger/WFH_LOG_GUIDE.md](../invoice_cataloger/WFH_LOG_GUIDE.md)** - WFH log format

---

## 💡 Tips & Best Practices

### WFH Categories

**Do include**:
- Expenses shared between work and personal use
- Utilities (electricity, internet, phone)
- Office supplies used at home

**Don't include**:
- 100% work expenses (professional development, memberships)
- Capital items (computer equipment - use depreciation)
- Personal expenses

### Exclude Locations

**Do exclude**:
- Annual leave
- Sick leave
- Public holidays
- Unpaid leave

**Don't exclude**:
- Training days (if working)
- Conference days (if working)
- Travel days (if working)

### File Organization

**Best practices**:
- Keep WFH log updated throughout the year
- Run report generation monthly for tracking
- Store generated reports with date stamps
- Backup all source files

---

## ⚠️ Common Issues

### Issue: "WFH log not found"

**Solution**:
```python
# Check file exists
wfh_log = Path("wfh/wfh_2024_2025.csv")
print(wfh_log.exists())  # Should be True

# Check file format
# Must have Date,Location columns
```

### Issue: "Invoice catalog not found"

**Solution**:
```python
# Check pattern matches
import glob
pattern = "FY2024-2025/Processed/Invoice_Catalog_*.csv"
files = glob.glob(pattern)
print(files)  # Should list catalog files
```

### Issue: "Wrong WFH percentage"

**Solution**:
```python
# Check excluded locations
exclude_locations = ['Leave', 'Sick', 'Holiday']

# Check WFH log entries
# Ensure "Home" and "Office" are capitalized correctly
```

### Issue: "Deductions not recalculated"

**Solution**:
```python
# Check category names match
wfh_categories = [
    'Electricity',  # Must match exactly
    'Internet',     # Case-sensitive
    'Phone'
]
```

---

*Last Updated: December 2024*  
*Version: 1.0*
