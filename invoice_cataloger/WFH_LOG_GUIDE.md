# Work From Home (WFH) Log Guide

## 📋 Overview

The WFH Log feature allows you to calculate your work-use percentage dynamically based on actual work-from-home days, rather than using a static percentage. This provides more accurate tax deduction calculations.

## 🎯 Purpose

### Why Use WFH Logs?

**Traditional Approach (Static):**
```python
work_use_percentage = 60  # Fixed 60% (3 days WFH / 5 days total)
```

**WFH Log Approach (Dynamic):**
```python
# Calculated from actual WFH days in your log
# July: 14 WFH / 23 total = 60.9%
# August: 15 WFH / 22 total = 68.2%
# Average: 62.5%
```

### Benefits:
✅ **More Accurate** - Based on actual work patterns
✅ **Audit-Ready** - Detailed records of WFH days
✅ **Flexible** - Accounts for varying work patterns
✅ **Automatic** - No manual percentage calculations

---

## 📝 Supported Formats

### CSV Format

**File Structure:**
```csv
Date,Location,WorkFromHome,Notes
2024-07-01,Home,Yes,Full day WFH
2024-07-02,Office,No,In office
2024-07-03,Home,Yes,Full day WFH
2024-07-04,Home,Yes,Full day WFH
2024-07-05,Office,No,In office
```

**Required Columns:**
- `Date` - Date in YYYY-MM-DD format
- `WorkFromHome` - Whether you worked from home

**Optional Columns:**
- `Location` - Where you worked (Home, Office, etc.)
- `Notes` - Additional notes

**Supported WFH Values:**
- `Yes` / `No`
- `True` / `False`
- `1` / `0`
- `Y` / `N`
- Case-insensitive

### JSON Format

**File Structure:**
```json
{
  "financial_year": "2024-2025",
  "entries": [
    {
      "date": "2024-07-01",
      "location": "Home",
      "wfh": true,
      "notes": "Full day WFH"
    },
    {
      "date": "2024-07-02",
      "location": "Office",
      "wfh": false,
      "notes": "In office"
    },
    {
      "date": "2024-07-03",
      "location": "Home",
      "wfh": true,
      "notes": "Full day WFH"
    }
  ]
}
```

**Required Fields:**
- `entries` - Array of work day entries
- `entries[].date` - Date in YYYY-MM-DD format
- `entries[].wfh` - Boolean or string (true/false, "Yes"/"No")

**Optional Fields:**
- `financial_year` - Financial year label
- `entries[].location` - Work location
- `entries[].notes` - Additional notes

---

## 🔢 Calculation Method

### Formula

```
WFH Percentage = (WFH Days / Total Work Days) × 100
```

### Example Calculation

**WFH Log:**
```csv
Date,Location,WorkFromHome,Notes
2024-07-01,Home,Yes,Full day WFH
2024-07-02,Office,No,In office
2024-07-03,Home,Yes,Full day WFH
2024-07-04,Home,Yes,Full day WFH
2024-07-05,Office,No,In office
```

**Calculation:**
- Total Work Days: 5
- WFH Days: 3 (July 1, 3, 4)
- Office Days: 2 (July 2, 5)
- **WFH Percentage: 60%** (3 / 5 × 100)

### Monthly Breakdown

The system also provides monthly statistics:

```
WFH Statistics Report
Financial Year: 2024-2025
Date Range: 2024-07-01 to 2024-08-31

OVERALL STATISTICS
------------------------------------------------------------
Total Work Days:        44
WFH Days:               27
Office Days:            17
WFH Percentage:       61.4%

MONTHLY BREAKDOWN
------------------------------------------------------------
July 2024             14 WFH /  23 total ( 60.9%)
August 2024           13 WFH /  21 total ( 61.9%)
```

---

## 🚀 Usage

### With Invoice Cataloger

```bash
# Use WFH log for dynamic work-use percentage
python invoice_cataloger.py --financial-year 2024-2025 --wfh-log wfh_log.csv
```

### With Standalone Tax Calculator

```bash
# Calculate tax with WFH log
python tax_calculator_cli.py \
  --catalog catalog.csv \
  --wfh-log wfh_log.csv \
  --output tax_report.csv

# Show WFH statistics
python tax_calculator_cli.py \
  --catalog catalog.csv \
  --wfh-log wfh_log.csv \
  --output tax_report.csv \
  --show-wfh-report
```

### Programmatic Usage

```python
from pathlib import Path
from tax.wfh import WFHParser, WFHCalculator

# Parse WFH log
parser = WFHParser()
log_data = parser.parse(Path("wfh_log.csv"))

# Calculate percentage
calculator = WFHCalculator()
percentage = calculator.calculate_wfh_percentage(log_data)
print(f"WFH Percentage: {percentage}%")

# Generate report
report = calculator.generate_wfh_report(log_data, "2024-2025")
print(report)
```

---

## 📅 Date Range Filtering

### Filter by Financial Year

```python
from tax.wfh import WFHParser

parser = WFHParser()
log_data = parser.parse(Path("wfh_log.csv"))

# Filter for FY 2024-2025 (July 1, 2024 - June 30, 2025)
filtered_data = parser.filter_by_financial_year(log_data, "2024-2025")
```

### Filter by Custom Date Range

```python
# Filter for specific date range
filtered_data = parser.filter_by_date_range(
    log_data,
    start_date="2024-07-01",
    end_date="2024-12-31"
)
```

---

## 📊 Example Files

### Example 1: Simple CSV

**File: `wfh_log_simple.csv`**
```csv
Date,WorkFromHome
2024-07-01,Yes
2024-07-02,No
2024-07-03,Yes
2024-07-04,Yes
2024-07-05,No
```

**Result**: 60% WFH (3/5 days)

### Example 2: Detailed CSV

**File: `wfh_log_detailed.csv`**
```csv
Date,Location,WorkFromHome,Notes
2024-07-01,Home,Yes,Full day WFH - project work
2024-07-02,Office,No,Team meeting day
2024-07-03,Home,Yes,Full day WFH
2024-07-04,Home,Yes,Full day WFH
2024-07-05,Office,No,Client presentation
2024-07-08,Home,Yes,Full day WFH
2024-07-09,Home,Yes,Full day WFH
2024-07-10,Office,No,In office
```

**Result**: 62.5% WFH (5/8 days)

### Example 3: JSON Format

**File: `wfh_log.json`**
```json
{
  "financial_year": "2024-2025",
  "entries": [
    {"date": "2024-07-01", "location": "Home", "wfh": true, "notes": "Full day WFH"},
    {"date": "2024-07-02", "location": "Office", "wfh": false, "notes": "In office"},
    {"date": "2024-07-03", "location": "Home", "wfh": true, "notes": "Full day WFH"},
    {"date": "2024-07-04", "location": "Home", "wfh": true, "notes": "Full day WFH"},
    {"date": "2024-07-05", "location": "Office", "wfh": false, "notes": "In office"}
  ]
}
```

**Result**: 60% WFH (3/5 days)

---

## ✅ Validation Rules

### Date Format
- **Required**: YYYY-MM-DD format
- **Example**: 2024-07-01
- **Invalid**: 01/07/2024, 2024-7-1, July 1 2024

### WFH Field
- **CSV**: Yes/No, True/False, 1/0, Y/N (case-insensitive)
- **JSON**: true/false (boolean) or "Yes"/"No" (string)

### Duplicate Dates
- **Not Allowed**: Each date should appear only once
- **Error**: "Duplicate dates found: 2024-07-01"

### Missing Fields
- **CSV**: Date and WorkFromHome columns required
- **JSON**: date and wfh fields required in each entry

---

## 🔍 Troubleshooting

### Error: "Invalid date format"

**Problem**: Date not in YYYY-MM-DD format

**Solution**:
```csv
# ❌ Wrong
Date,WorkFromHome
01/07/2024,Yes
2024-7-1,Yes

# ✅ Correct
Date,WorkFromHome
2024-07-01,Yes
2024-07-01,Yes
```

### Error: "Missing required fields"

**Problem**: CSV missing Date or WorkFromHome column

**Solution**:
```csv
# ❌ Wrong (missing WorkFromHome column)
Date,Location
2024-07-01,Home

# ✅ Correct
Date,WorkFromHome
2024-07-01,Yes
```

### Error: "Duplicate dates found"

**Problem**: Same date appears multiple times

**Solution**:
```csv
# ❌ Wrong
Date,WorkFromHome
2024-07-01,Yes
2024-07-01,No  # Duplicate!

# ✅ Correct
Date,WorkFromHome
2024-07-01,Yes
2024-07-02,No
```

### Warning: "No WFH data for FY2024-2025"

**Problem**: Log doesn't contain dates for specified financial year

**Solution**:
- Check your log covers the correct date range
- Australian FY 2024-2025 is July 1, 2024 - June 30, 2025
- Add entries for the correct period

### Error: "WFH log file not found"

**Problem**: File path is incorrect

**Solution**:
```bash
# ❌ Wrong
python invoice_cataloger.py --wfh-log wfh.csv  # File doesn't exist

# ✅ Correct
python invoice_cataloger.py --wfh-log examples/wfh_log.csv
python invoice_cataloger.py --wfh-log "C:/Users/Me/Documents/wfh_log.csv"
```

---

## 💡 Best Practices

### 1. Keep Regular Records
- Update your WFH log daily or weekly
- Don't wait until tax time to create it
- Use calendar reminders to maintain consistency

### 2. Be Accurate
- Record actual WFH days, not estimates
- Include all work days (don't skip days)
- Be honest
