# invoice_cataloger - Parameters Reference

Complete parameter documentation for the invoice_cataloger module.

---

## 📋 Table of Contents

- [Configuration File](#configuration-file)
- [LM Studio Parameters](#lm-studio-parameters)
- [Financial Year Parameters](#financial-year-parameters)
- [Work From Home Parameters](#work-from-home-parameters)
- [Path Parameters](#path-parameters)
- [OCR Parameters](#ocr-parameters)
- [Processing Parameters](#processing-parameters)
- [Command Line Arguments](#command-line-arguments)
- [Environment Variables](#environment-variables)
- [Examples](#examples)

---

## 📁 Configuration File

**Location**: `invoice_cataloger/config.py`

All parameters are defined in the `Config` class and can be modified by editing this file.

---

## 🤖 LM Studio Parameters

### lm_studio_endpoint

```python
lm_studio_endpoint: str = "http://localhost:1234/v1/chat/completions"
```

- **Type**: String (URL)
- **Default**: `"http://localhost:1234/v1/chat/completions"`
- **Description**: LM Studio API endpoint for AI processing
- **Required**: Yes
- **Examples**:
  - Local: `"http://localhost:1234/v1/chat/completions"`
  - Remote: `"http://192.168.1.100:1234/v1/chat/completions"`
  - Custom port: `"http://localhost:5000/v1/chat/completions"`

**When to change**:
- Running LM Studio on a different machine
- Using a custom port
- Load balancing across multiple LM Studio instances

### lm_studio_model

```python
lm_studio_model: str = "mistral-7b-instruct"
```

- **Type**: String
- **Default**: `"mistral-7b-instruct"`
- **Description**: Model name to use for inference
- **Required**: No (uses default model if not specified)
- **Options**:
  - `"mistral-7b-instruct"` - Recommended, best balance
  - `"llama-2-7b"` - Alternative, good accuracy
  - `"neural-chat-7b"` - Alternative, fast
  - Any model loaded in LM Studio

**When to change**:
- Testing different models
- Optimizing for speed vs accuracy
- Using specialized models

### lm_studio_timeout

```python
lm_studio_timeout: int = 120
```

- **Type**: Integer (seconds)
- **Default**: `120`
- **Description**: Maximum time to wait for API response
- **Range**: 30-300 seconds
- **Required**: No

**When to change**:
- Slow computer/model
- Processing complex invoices
- Network latency issues

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
- Batch processing multiple years
- Historical data processing

**Validation**:
```python
# Valid formats
"2024-2025"  ✓
"2023-2024"  ✓

# Invalid formats
"2024-25"    ✗ (must be full year)
"24-25"      ✗ (must be full year)
"2024/2025"  ✗ (must use hyphen)
```

---

## 🏠 Work From Home Parameters

### work_from_home_days

```python
work_from_home_days: int = 3
```

- **Type**: Integer
- **Default**: `3`
- **Description**: Number of days per week working from home
- **Range**: 0-7
- **Required**: Yes
- **Examples**:
  - Full-time WFH: `5`
  - Part-time WFH: `3`
  - Hybrid: `2`
  - Office-based: `0`

**When to change**:
- Your WFH arrangement changes
- Different work patterns
- Calculating different scenarios

### total_work_days

```python
total_work_days: int = 5
```

- **Type**: Integer
- **Default**: `5`
- **Description**: Total working days per week
- **Range**: 1-7
- **Required**: Yes
- **Examples**:
  - Standard: `5` (Mon-Fri)
  - 4-day week: `4`
  - 6-day week: `6`

**When to change**:
- Part-time work
- Compressed work week
- Non-standard schedule

### work_use_percentage

```python
work_use_percentage: int = 60
```

- **Type**: Integer (percentage)
- **Default**: `60` (calculated as work_from_home_days / total_work_days * 100)
- **Description**: Percentage of work use for shared expenses
- **Range**: 0-100
- **Required**: Yes
- **Calculation**: `(work_from_home_days / total_work_days) * 100`
- **Examples**:
  - 3/5 days: `60%`
  - 5/5 days: `100%`
  - 2/5 days: `40%`

**When to change**:
- Automatically calculated from above parameters
- Manual override for specific scenarios
- ATO-approved alternative calculations

**ATO Compliance**:
- Must be reasonable and substantiated
- Based on actual work patterns
- Applied to: Electricity, Internet, Phone, Office Supplies
- NOT applied to: Professional Development, Memberships

---

## 📂 Path Parameters

### base_path

```python
base_path: Path = Path("G:/My Drive/Tax Invoices")
```

- **Type**: Path object
- **Default**: `Path("G:/My Drive/Tax Invoices")`
- **Description**: Base directory for all tax files
- **Required**: Yes
- **Examples**:
  - Google Drive: `Path("G:/My Drive/Tax Invoices")`
  - OneDrive: `Path("C:/Users/Name/OneDrive/Tax Invoices")`
  - Local: `Path("C:/Tax Documents")`
  - Network: `Path("//server/share/Tax Invoices")`

**When to change**:
- Different storage location
- Multiple users
- Network storage

### invoice_folder

```python
invoice_folder: Path = base_path / f"FY{financial_year}"
```

- **Type**: Path object
- **Default**: Calculated from base_path and financial_year
- **Description**: Folder containing invoice files to process
- **Required**: Yes (auto-calculated)
- **Example**: `G:/My Drive/Tax Invoices/FY2024-2025`

**When to change**:
- Custom folder structure
- Different naming convention
- Usually auto-calculated, rarely needs manual change

### output_folder

```python
output_folder: Path = invoice_folder / "Processed"
```

- **Type**: Path object
- **Default**: `{invoice_folder}/Processed`
- **Description**: Output folder for processed files
- **Required**: Yes (auto-created if doesn't exist)
- **Example**: `G:/My Drive/Tax Invoices/FY2024-2025/Processed`

**When to change**:
- Custom output location
- Separate processing folders
- Usually auto-calculated

### log_folder

```python
log_folder: Path = output_folder / "Logs"
```

- **Type**: Path object
- **Default**: `{output_folder}/Logs`
- **Description**: Folder for processing logs
- **Required**: Yes (auto-created if doesn't exist)
- **Example**: `G:/My Drive/Tax Invoices/FY2024-2025/Processed/Logs`

**When to change**:
- Custom log location
- Centralized logging
- Usually auto-calculated

---

## 🔍 OCR Parameters

### use_easyocr

```python
use_easyocr: bool = True
```

- **Type**: Boolean
- **Default**: `True`
- **Description**: Enable EasyOCR for text extraction
- **Required**: No
- **Dependencies**: `pip install easyocr`

**When to change**:
- EasyOCR not installed
- Performance optimization
- Prefer Tesseract only

**Pros**:
- No additional software installation
- Deep learning-based
- Good accuracy

**Cons**:
- Slower than Tesseract
- Larger memory footprint
- First run downloads models (~100MB)

### use_tesseract

```python
use_tesseract: bool = True
```

- **Type**: Boolean
- **Default**: `True`
- **Description**: Enable Tesseract OCR for text extraction
- **Required**: No
- **Dependencies**: Tesseract software + `pip install pytesseract`

**When to change**:
- Tesseract not installed
- Using EasyOCR only
- Performance optimization

**Pros**:
- Fast processing
- Mature and stable
- Lower memory usage

**Cons**:
- Requires separate installation
- Less accurate than EasyOCR
- Platform-specific setup

### tesseract_path

```python
tesseract_path: str = "C:/Program Files/Tesseract-OCR/tesseract.exe"
```

- **Type**: String (file path)
- **Default**: `"C:/Program Files/Tesseract-OCR/tesseract.exe"` (Windows)
- **Description**: Path to Tesseract executable
- **Required**: Only if use_tesseract is True
- **Platform-specific**:
  - **Windows**: `"C:/Program Files/Tesseract-OCR/tesseract.exe"`
  - **macOS**: `"/usr/local/bin/tesseract"` or `"/opt/homebrew/bin/tesseract"`
  - **Linux**: `"/usr/bin/tesseract"`

**When to change**:
- Custom Tesseract installation
- Different platform
- Portable installation

**Finding Tesseract**:
```bash
# Windows
where tesseract

# macOS/Linux
which tesseract
```

---

## ⚙️ Processing Parameters

### max_retries

```python
max_retries: int = 3
```

- **Type**: Integer
- **Default**: `3`
- **Description**: Maximum retry attempts for failed files
- **Range**: 0-10
- **Required**: No

**When to change**:
- Unreliable network/LM Studio
- Increase for better coverage
- Decrease for faster processing

**Behavior**:
- 0: No retries, fail immediately
- 1-3: Reasonable for most cases
- 4+: For problematic files

### use_cache

```python
use_cache: bool = True
```

- **Type**: Boolean
- **Default**: `True`
- **Description**: Enable caching to avoid reprocessing
- **Required**: No

**When to change**:
- Force reprocessing all files
- Testing changes
- Cache corruption

**Benefits**:
- Faster subsequent runs
- Avoids duplicate processing
- Preserves previous results

**Cache Location**: `{output_folder}/cache.json`

### cache_file

```python
cache_file: str = "cache.json"
```

- **Type**: String (filename)
- **Default**: `"cache.json"`
- **Description**: Cache file name
- **Required**: No
- **Location**: Stored in output_folder

**When to change**:
- Multiple cache files
- Custom naming
- Rarely needs changing

### failed_files_file

```python
failed_files_file: str = "failed_files.json"
```

- **Type**: String (filename)
- **Default**: `"failed_files.json"`
- **Description**: Failed files tracking file
- **Required**: No
- **Location**: Stored in output_folder

**When to change**:
- Custom naming
- Multiple tracking files
- Rarely needs changing

---

## 💻 Command Line Arguments

Override config file parameters via command line:

### --financial-year

```bash
python invoice_cataloger.py --financial-year 2023-2024
```

- **Type**: String (YYYY-YYYY)
- **Default**: From config.py
- **Description**: Specify financial year
- **Example**: `--financial-year 2024-2025`

### --retry-failed

```bash
python invoice_cataloger.py --retry-failed
```

- **Type**: Flag (no value)
- **Default**: False
- **Description**: Process only previously failed files
- **Use case**: Retry after fixing issues

### --check-only

```bash
python invoice_cataloger.py --check-only
```

- **Type**: Flag (no value)
- **Default**: False
- **Description**: Check prerequisites without processing
- **Use case**: Verify setup

### --verbose

```bash
python invoice_cataloger.py --verbose
```

- **Type**: Flag (no value)
- **Default**: False
- **Description**: Enable debug logging
- **Use case**: Troubleshooting

### --reprocess

```bash
python invoice_cataloger.py --reprocess
```

- **Type**: Flag (no value)
- **Default**: False
- **Description**: Reprocess all files (ignore cache)
- **Use case**: Force complete reprocessing

---

## 🌍 Environment Variables

Alternative to config file (optional):

### LM_STUDIO_ENDPOINT

```bash
export LM_STUDIO_ENDPOINT="http://192.168.1.100:1234/v1/chat/completions"
```

- **Type**: String (URL)
- **Description**: Override LM Studio endpoint
- **Priority**: Environment variable > config file

### FINANCIAL_YEAR

```bash
export FINANCIAL_YEAR="2024-2025"
```

- **Type**: String (YYYY-YYYY)
- **Description**: Override financial year
- **Priority**: Command line > environment variable > config file

### TESSERACT_PATH

```bash
export TESSERACT_PATH="/usr/local/bin/tesseract"
```

- **Type**: String (file path)
- **Description**: Override Tesseract path
- **Priority**: Environment variable > config file

---

## 📝 Examples

### Example 1: Standard Configuration

```python
# config.py
financial_year = "2024-2025"
work_from_home_days = 3
total_work_days = 5
work_use_percentage = 60
lm_studio_endpoint = "http://localhost:1234/v1/chat/completions"
```

**Use case**: Standard 3-day WFH arrangement

### Example 2: Full-Time Remote

```python
# config.py
financial_year = "2024-2025"
work_from_home_days = 5
total_work_days = 5
work_use_percentage = 100
```

**Use case**: 100% remote work

### Example 3: Custom Paths

```python
# config.py
base_path = Path("C:/Tax Documents")
financial_year = "2024-2025"
```

**Use case**: Local storage instead of Google Drive

### Example 4: Remote LM Studio

```python
# config.py
lm_studio_endpoint = "http://192.168.1.100:1234/v1/chat/completions"
lm_studio_timeout = 180  # Longer timeout for network
```

**Use case**: LM Studio on different machine

### Example 5: OCR Only (No Tesseract)

```python
# config.py
use_easyocr = True
use_tesseract = False
```

**Use case**: EasyOCR only, no Tesseract installation

### Example 6: Command Line Override

```bash
# Process different year without changing config
python invoice_cataloger.py --financial-year 2023-2024

# Retry failed files
python invoice_cataloger.py --financial-year 2024-2025 --retry-failed

# Force reprocess with verbose logging
python invoice_cataloger.py --reprocess --verbose
```

**Use case**: Temporary parameter changes

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
"2025-2024"  ✗ Second year must be first + 1
```

### Work Percentage Validation

```python
# Valid
work_from_home_days = 3, total_work_days = 5  ✓ (60%)
work_from_home_days = 5, total_work_days = 5  ✓ (100%)

# Invalid
work_from_home_days = 6, total_work_days = 5  ✗ WFH > total
work_from_home_days = -1, total_work_days = 5 ✗ Negative value
```

### Path Validation

```python
# Valid
Path("G:/My Drive/Tax Invoices")  ✓
Path("C:/Tax Documents")           ✓

# Warning
Path("/nonexistent/path")          ⚠️ Created if doesn't exist
```

---

## 📚 Related Documentation

- **[README.md](README.md)** - Module overview
- **[API_SETUP_GUIDE.md](API_SETUP_GUIDE.md)** - LM Studio setup
- **[../QUICKSTART.md](../QUICKSTART.md)** - Quick start guide
- **[../MODULE_INDEX.md](../MODULE_INDEX.md)** - All modules

---

*Last Updated: December 2024*  
*Version: 1.0*
